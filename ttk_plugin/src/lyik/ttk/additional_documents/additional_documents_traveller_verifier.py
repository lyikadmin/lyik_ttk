import apluggy as pluggy
from Crypto.Cipher import AES
import io
import zipfile
import base64
from Crypto.Util.Padding import pad
from lyikpluginmanager import (
    invoke,
    getProjectName,
    ContextModel,
    PluginException,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
    TransformerResponseModel,
    TRANSFORMER_RESPONSE_STATUS,
    TemplateDocumentModel,
    DocxTemplateModel,
    DocumentModel,
    DocMeta,
    DocQueryGenericModel,
)
from datetime import datetime
from typing import Annotated, List, Any, Dict
from typing_extensions import Doc
from lyik.ttk.models.forms.schengentouristvisa import (
    RootAdditionalDocumentsPane,
    FieldGrpRootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroup,
    RootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroupAdditionaldocumentgrouptraveller,
    RootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroupAdditionaldocumentgrouptravellerAdditionalDocumentsCardTraveller,
)
from lyikpluginmanager.annotation import RequiredVars
import logging
from lyik.ttk.utils.verifier_util import check_if_verified, validate_pincode
from lyik.ttk.utils.message import get_error_message
from lyik.ttk.utils.flatten_record import JSONFlattener

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

ACTOR = "system"


# VERIFIER_GENERATE_FILLED_GENERIC_TEMPLATES
class AdditionalDocumentsTravellerVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootAdditionalDocumentsPane,
            Doc("Address payload."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response with the cards and generated template link"),
        RequiredVars(["PDF_GARBLE_KEY", "DOWNLOAD_DOC_API_ENDPOINT"]),
    ]:
        """
        This verifier generates link to download the zip of templates, and also creates the appropriate cards required to upload the modified files, if it doesn't exist already.
        """
        payload = RootAdditionalDocumentsPane.model_validate(payload)
        # payload_dict = payload.model_dump(mode="json")

        if not context or not context.config:
            raise PluginException(
                message=get_error_message(
                    error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                ),
                detailed_message="The context is missing or config is missing in context.",
            )

        full_form_record = context.record

        try:
            # Keep a reference to what was originally on the payload
            old_traveller_group = payload.additional_documents_traveller_group or []

            # Fast lookup:
            # key: document_name_display (or equivalent id),
            # value: existing traveller card (so we can preserve file_upload)
            existing_traveller_by_doc_name: Dict[
                str,
                RootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroupAdditionaldocumentgrouptravellerAdditionalDocumentsCardTraveller,
            ] = {}

            for traveller_card_wrapper in old_traveller_group:
                traveller_card = (
                    traveller_card_wrapper.additionaldocumentgrouptraveller.additional_documents_card_traveller
                )
                existing_traveller_by_doc_name[traveller_card.document_name_display] = (
                    traveller_card
                )

            # We'll accumulate:
            new_traveller_group: List[
                FieldGrpRootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroup
            ] = []

            templates_list: List[Any] = []

            # Walk all consultant cards in order
            for (
                consultant_card_wrapper
            ) in payload.additional_documents_consultant_group:
                consultant_card = (
                    consultant_card_wrapper.additionaldocumentgroupconsultant.additional_documents_card_consultant
                )

                document_name = consultant_card.document_name
                document_description = consultant_card.document_description
                template_file = consultant_card.file_upload

                # Track template file for ZIP bundling
                if template_file is not None:
                    templates_list.append(template_file)

                # See if we already had a traveller card for this doc name
                maybe_existing = existing_traveller_by_doc_name.get(document_name)

                if maybe_existing:
                    # Preserve the user's uploaded file, if any
                    preserved_upload = maybe_existing.file_upload
                else:
                    preserved_upload = None

                # Build traveller card wrapper in the expected schema
                new_traveller_group.append(
                    FieldGrpRootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroup(
                        additionaldocumentgrouptraveller=(
                            RootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroupAdditionaldocumentgrouptraveller(
                                additional_documents_card_traveller=(
                                    RootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroupAdditionaldocumentgrouptravellerAdditionalDocumentsCardTraveller(
                                        document_name=document_name,
                                        document_description=document_description,
                                        document_name_display=document_name,
                                        document_description_display=document_description,
                                        file_upload=preserved_upload,
                                    )
                                )
                            )
                        )
                    )
                )

            # For now this is a stub.
            templates_link = await self.generate_template_zip(
                templates_list=templates_list, record=full_form_record, context=context
            )

            # Mutate payload to reflect final state
            payload.template_download_display = templates_link
            payload.additional_documents_traveller_group = new_traveller_group

            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=f"Verified by the {ACTOR}",
                status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                response=payload.model_dump(),
            )

        except PluginException as pe:
            logger.error(pe.detailed_message)
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=pe.message,
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )

        except Exception as e:
            logger.error(f"Unhandled exception occurred. Error: {str(e)}")
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=get_error_message(error_message_code="LYIK_ERR_SAVE_FAILURE"),
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )

    async def generate_template_zip(
        self,
        templates_list,
        record,
        context: ContextModel,
    ) -> str:
        json_flattener = JSONFlattener()
        flat_data = json_flattener.flatten(data=record)

        generated_doc_list: List[TemplateDocumentModel] = []

        for template in templates_list:
            transformer_res: TransformerResponseModel = (
                await invoke.template_generate_docx(
                    org_id=context.org_id,
                    config=context.config,
                    record=flat_data,
                    form_id=context.form_id,
                    additional_args={},
                    fetch_from_db_or_path=True,
                    form_name="",
                    template=DocxTemplateModel(template=template),
                )
            )

            if not transformer_res or not isinstance(
                transformer_res, TransformerResponseModel
            ):
                logger.error("Failed to transform the docx file.")
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                    actor="system",
                    message=get_error_message(
                        error_message_code="LYIK_ERR_SOMETHING_WENT_WRONG"
                    ),
                )

            if transformer_res.status == TRANSFORMER_RESPONSE_STATUS.FAILURE:
                logger.error("Failed to generate the Docx file.")
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                    actor="system",
                    message=get_error_message(
                        error_message_code="LYIK_ERR_DOCX_GEN_FAILURE"
                    ),
                )

            docs: List[TemplateDocumentModel] = transformer_res.response

            # collect all docs (not just first one)
            for d in docs:
                if not d or not getattr(d, "doc_content", None):
                    continue
                generated_doc_list.append(d)

        if not generated_doc_list:
            logger.error("No documents were generated from templates.")
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                actor="system",
                message=get_error_message(
                    error_message_code="LYIK_ERR_DOCX_GEN_FAILURE"
                ),
            )

        # Build zip in memory
        zip_buffer = io.BytesIO()
        name_counts: dict[str, int] = {}

        with zipfile.ZipFile(
            zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zip_file:
            for doc in generated_doc_list:
                base_name = doc.doc_name or "document.docx"

                # uniquify filenames inside zip
                if base_name in name_counts:
                    name_counts[base_name] += 1
                    if "." in base_name:
                        root, ext = base_name.rsplit(".", 1)
                        file_name = f"{root} ({name_counts[base_name]}).{ext}"
                    else:
                        file_name = f"{base_name} ({name_counts[base_name]})"
                else:
                    name_counts[base_name] = 1
                    file_name = base_name

                # actually write file bytes
                zip_file.writestr(file_name, doc.doc_content)

        # grab raw zip bytes
        zip_bytes = zip_buffer.getvalue()

        # base64 encode for inline download link
        encoded_zip = base64.b64encode(zip_bytes).decode("utf-8")

        html_msg = f"""
        <div>
            <p>Click below to download all generated documents as a ZIP:</p>
            <a
                href="data:application/zip;base64,{encoded_zip}"
                download="generated_documents.zip"
            >
                Download all documents
            </a>
        </div>
        """

        return html_msg

        # output_docs: List[DocumentModel] = []
        # for gen_doc in generated_doc_list:
        #     output_docs.append(
        #         DocumentModel(
        #             doc_id=None,
        #             doc_name=gen_doc.doc_name,
        #             doc_type=gen_doc.doc_type,
        #             doc_size=len(gen_doc.doc_content),
        #             doc_content=gen_doc.doc_content,
        #         )
        #     )

        # if len(output_docs) != 0:
        #     await self.store_all_files(
        #         context=context,
        #         files=output_docs,
        #         rec_id=record_id,
        #         tag={
        #             "custom_docx_templates": "custom_docx_templates",
        #         },
        #     )
        #     logger.info("Files saved to DB.")

        # # Create the link for downloading the payload file
        # link_data = DocQueryGenericModel(
        #     org_id=context.org_id, form_id=context.form_id, record_id=record_id
        # )
        # link_data = link_data.model_copy(update={"docket": "docket"})

        # # Obfuscate the data string
        # obfus_str = self.obfuscate_string(
        #     data_str=link_data.model_dump_json(),
        #     static_key=context.config.PDF_GARBLE_KEY,
        # )

        # file_name = f"Generated Templates {datetime.now().strftime('%d %b %Y')}".title()

        # api_domain = os.getenv("API_DOMAIN")
        # download_doc_endpoint = context.config.DOWNLOAD_DOC_API_ENDPOINT
        # download_url = f"{api_domain}{download_doc_endpoint}{obfus_str}.zip?file_name={file_name}"

        # html_msg = get_docket_operation_html_message(
        #     title_text="Templates generated",
        #     instruction_points=[
        #         "Download Your Generated Documents",
        #     ],
        #     url=download_url,
        #     action_text="Download Documents",
        # )

        return html_msg


#     async def store_all_files(
#         self,
#         context: ContextModel,
#         files: List[DocumentModel],
#         rec_id: int,
#         tag: Dict[str, str],
#     ):
#         """
#         Just saves the files into the DB with the specified tag.
#         Can be used by doc query later to fetch the files if needed.
#         """
#         for file in files:
#             meta_data = DocMeta(
#                 org_id=context.org_id,
#                 form_id=context.form_id,
#                 record_id=rec_id,
#                 doc_type=file.doc_type,
#             )
#             meta_data = meta_data.model_copy(update=tag)

#             try:
#                 await invoke.deleteDocument(
#                     config=context.config,
#                     org_id=context.org_id,
#                     coll_name=context.form_id,
#                     file_id=None,
#                     metadata_params=DocQueryGenericModel(
#                         **meta_data.model_dump(exclude_unset=True)
#                     ),
#                 )
#             except Exception as e:
#                 continue
#         for file in files:
#             meta_data = DocMeta(
#                 org_id=context.org_id,
#                 form_id=context.form_id,
#                 record_id=rec_id,
#                 doc_type=file.doc_type,
#             )
#             meta_data = meta_data.model_copy(update=tag)
#             try:
#                 await invoke.addDocument(
#                     config=context.config,
#                     org_id=context.org_id,
#                     coll_name=context.form_id,
#                     document=file,
#                     metadata=meta_data,
#                 )
#             except Exception as e:
#                 raise PluginException(
#                     message=get_error_message(
#                         error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
#                     ),
#                     detailed_message=f"Failed to save the document. Error:{str(e)}",
#                 )

#     def obfuscate_string(self, data_str: str, static_key: str) -> str:
#         """
#         Obfuscates a string using AES encryption with a static key.

#         :param data_str: The string that will be encrypted.
#         :param static_key: The key used for encryption.
#         :return: The obfuscated string in Base64 format.
#         """
#         try:
#             # Ensure the key is exactly 16 bytes long
#             key = static_key.encode().ljust(16, b"\0")

#             # Data to encrypt
#             data = data_str.encode()

#             # Create cipher and encrypt the data with padding
#             cipher = AES.new(key, AES.MODE_ECB)
#             encrypted_data = cipher.encrypt(pad(data, AES.block_size))

#             # Encode the encrypted data with Base64
#             obfuscated_string = base64.urlsafe_b64encode(encrypted_data).decode()
#             return obfuscated_string

#         except Exception as e:
#             raise PluginException(
#                 message=get_error_message(
#                     error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
#                 ),
#                 detailed_message=f"Failed to obfuscate the string. Error: {str(e)}",
#             )


# def get_docket_operation_html_message(
#     title_text: str,
#     instruction_points: list[str] | None = None,
#     url: str | None = None,
#     action_text: str | None = None,
# ) -> str:
#     action_text = "Download Docket" if url and not action_text else action_text

#     full_css = """
#     <style>
#         .operation-container {
#             text-align: center;
#             font-family: Arial, sans-serif;
#             padding: 24px;
#         }

#         .submit-button {
#             background-color: #3BB9EB;
#             color: white;
#             border: none;
#             padding: 8px 50px;
#             font-size: 17px;
#             border-radius: 9999px;
#             cursor: pointer;
#             transition: background-color 0.3s ease, transform 0.2s ease;
#             width: fit-content;
#             margin-top: 16px;
#             display: inline-block;
#             text-decoration: none;
#             font-weight: 600;
#         }

#         .submit-button:hover {
#             background-color: #1280aa;
#             transform: scale(1.02);
#         }

#         .operation-title {
#             font-size: 22px;
#             color: #333333;
#             font-weight: 600;
#             margin-top: 24px;
#             margin-bottom: 24px;
#         }

#         .instruction-list {
#             list-style-type: disc;
#             padding-left: 20px;
#             display: inline-block;
#             text-align: left;
#             font-size: 16px;
#             color: #222222;
#             font-weight: 500;
#             line-height: 1.8;
#             margin: 0 auto;
#         }

#         .instruction-list li {
#             margin-bottom: 12px;
#         }
#     </style>
#     """

#     url_button = (
#         f"""<a href="{url}" class="submit-button">{action_text}</a>""" if url else ""
#     )

#     instruction_html = ""
#     if instruction_points:
#         instruction_items = "".join(f"<li>{point}</li>" for point in instruction_points)
#         instruction_html = f"<ul class='instruction-list'>{instruction_items}</ul>"

#     html = f"""
#     {full_css}
#     <div class="operation-container">
#         {url_button}
#         <p class="operation-title">{title_text}</p>
#         {instruction_html}
#     </div>
#     """

#     return html
