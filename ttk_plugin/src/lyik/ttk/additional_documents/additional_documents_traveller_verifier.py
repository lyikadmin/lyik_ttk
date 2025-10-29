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
import io
import re
import base64
import zipfile
from typing import Any, Dict, List


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
        This verifier is responsible for:
        1. Building/normalizing the traveller upload cards:
           - For each consultant document requirement, ensure there is a corresponding
             traveller card (to allow the end user to upload their filled-out file).
           - Existing traveller uploads are preserved where possible.
           - Duplicate consultant documents are de-duplicated and numbered
             ("Doc", "Doc (2)", "Doc (3)", ...) so we don't create conflicting cards.

        2. Generating downloadable templates:
           - For each consultant document template, generate a filled .docx file.
           - All generated .docx files are bundled into a single in-memory ZIP.
           - A base64 download link for that ZIP is injected back into the payload
             as `template_download_display`.

        The method returns a VerifyHandlerResponseModel containing the updated payload
        (cards + download link), or an appropriate failure response.
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

            # We'll accumulate traveller cards here, but dedup by name.
            # key: effective_document_name (possibly "Doc", "Doc (2)", etc.)
            # value: FieldGrp... wrapper we build below
            new_traveller_group_map: Dict[
                str,
                FieldGrpRootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroup,
            ] = {}

            # Instead of a list of templates, we now keep a map:
            # key: effective_document_name (this will become the final filename base)
            # value: consultant_card.file_upload (the template file to transform)
            templates_map: Dict[str, Any] = {}

            # Track how many times we've seen each *raw* document_name (without numbering)
            # so we can generate "Name", "Name (2)", "Name (3)", ...
            doc_name_counts: Dict[str, int] = {}  # base_name -> count

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

                # Count how many times we've seen this base name so far
                count = doc_name_counts.get(document_name, 0) + 1
                doc_name_counts[document_name] = count

                # Build the "effective" name that should be unique across duplicates.
                # First copy keeps the raw name. Subsequent copies get " (2)", " (3)", ...
                if count == 1:
                    effective_document_name = document_name
                else:
                    effective_document_name = f"{document_name} ({count})"

                # Track template file for ZIP bundling.
                # Using effective_document_name here means each duplicate
                # produces a separate entry and thus a separate generated doc.
                if template_file is not None:
                    templates_map[effective_document_name] = template_file

                # See if we already had a traveller card for this doc name in the *incoming* payload.
                # We now look up by effective_document_name; if it's new (like "... (2)"),
                # it probably won't exist yet, which is fine.
                maybe_existing = existing_traveller_by_doc_name.get(
                    effective_document_name
                )
                if maybe_existing:
                    # Preserve the user's uploaded file, if any
                    preserved_upload = maybe_existing.file_upload
                else:
                    preserved_upload = None

                # Check if we've ALREADY created a traveller card wrapper for this effective name
                already_built_wrapper = new_traveller_group_map.get(
                    effective_document_name
                )

                if already_built_wrapper:
                    # We don't append a duplicate. But we *can* opportunistically
                    # attach an upload if the first version didn't have one and this one does.
                    built_card = (
                        already_built_wrapper.additionaldocumentgrouptraveller.additional_documents_card_traveller
                    )

                    if built_card.file_upload is None and preserved_upload is not None:
                        built_card.file_upload = preserved_upload

                else:
                    # Build traveller card wrapper in the expected schema
                    new_wrapper = FieldGrpRootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroup(
                        additionaldocumentgrouptraveller=(
                            RootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroupAdditionaldocumentgrouptraveller(
                                additional_documents_card_traveller=(
                                    RootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroupAdditionaldocumentgrouptravellerAdditionalDocumentsCardTraveller(
                                        document_name=effective_document_name,
                                        document_description=document_description,
                                        document_name_display=effective_document_name,
                                        document_description_display=document_description,
                                        file_upload=preserved_upload,
                                    )
                                )
                            )
                        )
                    )

                    # Store this wrapper keyed by effective_document_name so duplicates
                    # (e.g. "Letter", "Letter (2)") are treated as distinct rows
                    # and true exact name repeats don't create duplicates.
                    new_traveller_group_map[effective_document_name] = new_wrapper

            # Convert the deduped map into the final list for the payload.
            # dict preserves insertion order, so first occurrence
            # of each effective_document_name defines ordering.
            new_traveller_group: List[
                FieldGrpRootAdditionalDocumentsPaneAdditionalDocumentsTravellerGroup
            ] = list(new_traveller_group_map.values())

            # Generate the ZIP download link using templates_map
            templates_link_response = await self.generate_template_zip(
                templates_map=templates_map,
                record=full_form_record,
                context=context,
            )

            if isinstance(templates_link_response, VerifyHandlerResponseModel):
                return templates_link_response

            # Mutate payload to reflect final state
            payload.template_download_display = templates_link_response
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
        templates_map: Dict[str, Any],  # { effective_document_name: template_file }
        record,
        context: ContextModel,
    ) -> str:

        generated_doc_list: List[TemplateDocumentModel] = []

        # Iterate over the mapping of desired filename -> template file
        for desired_doc_name, template in templates_map.items():
            transformer_res: TransformerResponseModel = (
                await invoke.template_generate_docx(
                    org_id=context.org_id,
                    config=context.config,
                    record=record,
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

                # We now force the generated document to take on the (possibly numbered)
                # effective_document_name as the filename in the ZIP.
                # We also sanitize it and ensure it ends with .docx.
                safe_base_name = (
                    re.sub(
                        r"[^\w\-\.\(\) ]+",
                        "_",
                        desired_doc_name or "",
                    ).strip()
                    or "document"
                )
                if not safe_base_name.lower().endswith(".docx"):
                    final_name = f"{safe_base_name}.docx"
                else:
                    final_name = safe_base_name

                # override upstream name so downstream ZIP code uses it
                d.doc_name = final_name

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
                # NOTE: This still matters because after sanitization, two different
                # desired_doc_name values could collide to the same cleaned filename.
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
