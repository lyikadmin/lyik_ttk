import apluggy as pluggy
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    OperationPluginSpec,
    OperationResponseModel,
    OperationStatus,
    PluginException,
    GenericFormRecordModel,
    invoke,
    TransformerResponseModel,
    DBDocumentModel,
    DocMeta,
    DocQueryGenericModel,
    DocumentModel,
    TRANSFORMER_RESPONSE_STATUS,
    TemplateDocumentModel,
    get_operation_html_message,
)
from lyikpluginmanager.annotation import RequiredVars, RequiredEnv
from io import BytesIO
from PIL import Image
from pypdf import PdfWriter, PdfReader
import mimetypes
import mimetypes
from ..models.forms.new_schengentouristvisa import (
    Schengentouristvisa,
)
from .docket_utilities.docket_utilities import DocketUtilities
from ..models.pdf.pdf_model import EditableForm
from typing import Annotated, Dict, List
from typing_extensions import Doc
import logging
import os

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())


class DocketOperation(OperationPluginSpec):

    @impl
    async def process_operation(
        self,
        context: ContextModel,
        record_id: Annotated[int, Doc(" Record ID of the form record.")],
        status: Annotated[str, Doc("The status of the form.")],
        form_record: Annotated[GenericFormRecordModel, Doc("This is the form record.")],
        params: Dict | None,
    ) -> Annotated[
        OperationResponseModel,
        RequiredVars(["DB_CONN_URL", "DOWNLOAD_DOC_API_ENDPOINT", "PDF_GARBLE_KEY"]),
        RequiredEnv(["API_DOMAIN"]),
        Doc("Reurns the operation response with operation status and message."),
    ]:
        try:
            parsed_form_model = Schengentouristvisa(**form_record.model_dump())

            docket_util = DocketUtilities()

            final_files: List[DocumentModel] = []

            mapped_data: EditableForm = docket_util.map_schengen_to_editable_form(
                schengen_visa_data=parsed_form_model
            )

            data_dict: Dict = mapped_data.model_dump(mode="json")

            transformed_data: TransformerResponseModel = (
                await invoke.template_generate_pdf(
                    org_id=context.org_id,
                    config=context.config,
                    form_id=context.form_id,
                    additional_args={"record_id": record_id},
                    template_id="01_SwitzerlandVisaForm",
                    form_name="ttkform",
                    record=data_dict,
                )
            )

            if not transformed_data or not isinstance(
                transformed_data, TransformerResponseModel
            ):
                raise PluginException(
                    message="PDF generation failed for the current operation. Please try again or contact support.",
                    detailed_message=f"PDF generation failed. Error:{str(e),}",
                )

            if transformed_data.status != TRANSFORMER_RESPONSE_STATUS.SUCCESS:
                return OperationResponseModel(
                    status=OperationStatus.FAILED,
                    message="Failed to create Docket. Please try again or contact support.",
                )

            pdfs: List[TemplateDocumentModel] = transformed_data.response

            for pdf in pdfs:
                final_files.append(
                    DocumentModel(
                        doc_name=pdf.doc_name,
                        doc_content=pdf.doc_content,
                        doc_type=pdf.doc_type,
                        doc_size=len(pdf.doc_content),
                    )
                )

            files_in_rec_with_filename = {
                "appointment_schedule_document": self.safe_getattr(
                    parsed_form_model,
                    "appointment.appointment_scheduled.upload_appointment",
                ),
                "passport_front": self.safe_getattr(
                    parsed_form_model, "passport.passport_details.ovd_front"
                ),
                "passport_back": self.safe_getattr(
                    parsed_form_model, "passport.passport_details.ovd_back"
                ),
                "passport_size_photo": self.safe_getattr(
                    parsed_form_model, "photograph.passport_photo.photo"
                ),
                "address_proof": self.safe_getattr(
                    parsed_form_model,
                    "residential_address.residential_address_card_v1.address_proof_upload",
                ),
                "itinerary": self.safe_getattr(
                    parsed_form_model,
                    "itinerary_accomodation.itinerary_card.upload_itinerary",
                ),
                "accommodation_proof": self.safe_getattr(
                    parsed_form_model, "accomodation.booked_appointment.booking_upload"
                ),
                "flight_tickets": self.safe_getattr(
                    parsed_form_model, "ticketing.flight_tickets.flight_tickets"
                ),
                "travel_insurance": self.safe_getattr(
                    parsed_form_model,
                    "travel_insurance.flight_reservation_details.flight_reservation_tickets",
                ),
                "aadhaar_card_front": self.safe_getattr(
                    parsed_form_model,
                    "additional_details.national_id.aadhaar_upload_front",
                ),
                "aadhaar_card_back": self.safe_getattr(
                    parsed_form_model,
                    "additional_details.national_id.aadhaar_upload_back",
                ),
                "salary_slip": self.safe_getattr(
                    parsed_form_model, "salary_slip.upload.salary_slip"
                ),
                "bank_statement": self.safe_getattr(
                    parsed_form_model, "bank_statement.upload.bank_statements"
                ),
            }

            fetched_documents_by_key: Dict[str, DBDocumentModel] = {}

            for key, file_data in files_in_rec_with_filename.items():
                if isinstance(file_data, dict) and file_data.get("doc_id"):
                    try:
                        doc = DBDocumentModel(**file_data)

                        fetched_docs: List[DBDocumentModel] = (
                            await invoke.fetchDocument(
                                config=context.config,
                                org_id=context.org_id,
                                file_id=doc.doc_id,
                                coll_name=context.form_id,
                                metadata_params=None,
                            )
                        )

                        fetched_documents_by_key[key] = fetched_docs[0]

                    except Exception as e:
                        raise PluginException(
                            message=f"Internal error occurred. Please contact support.",
                            detailed_message=f"Error while fetching document: {str(e)}",
                        )

            # ✅ Process and get final files
            processed_files: List[DocumentModel] = self.process_documents_for_output(
                fetched_documents_by_key
            )

            final_files.extend(processed_files)

            if len(final_files) != 0:
                await self.store_all_files(
                    context=context,
                    files=final_files,
                    rec_id=record_id,
                    tag={
                        "docket": "docket",
                    },
                )
                logger.info("Files saved to DB.")

            # Create the link for downloading the payload file
            link_data = DocQueryGenericModel(
                org_id=context.org_id, form_id=context.form_id, record_id=record_id
            )
            link_data = link_data.model_copy(update={"docket": "docket"})

            # Obfuscate the data string
            obfus_str = self.obfuscate_string(
                data_str=link_data.model_dump_json(),
                static_key=context.config.PDF_GARBLE_KEY,
            )

            # Build the download URL for the payload
            api_domain = os.getenv("API_DOMAIN")
            download_doc_endpoint = context.config.DOWNLOAD_DOC_API_ENDPOINT
            download_url = api_domain + download_doc_endpoint + f"{obfus_str}.zip"

            # Return the successful operation response with the download URL
            html_msg = get_operation_html_message(
                title_text="Docket generated successfully.",
                message_text="Click the download button to download the Docket.",
                action_text="Download",
                url=download_url,
            )
            return OperationResponseModel(
                status=OperationStatus.SUCCESS,
                message=html_msg,
            )
        except PluginException as pe:
            logger.error(pe.detailed_message)
            return OperationResponseModel(
                status=OperationStatus.FAILED,
                message=pe.message,
            )
        except Exception as e:
            logger.error(f"Exception during Docket creation. Error: {str(e)}")
            return OperationResponseModel(
                status=OperationStatus.FAILED,
                message="Failed to generate the Docket.",
            )

    def safe_getattr(self, obj, attr_path: str):
        """Safely gets nested attributes from an object using dot notation."""
        try:
            for attr in attr_path.split("."):
                obj = getattr(obj, attr)
                if obj is None:
                    return None
            return obj
        except AttributeError:
            return None

    async def store_all_files(
        self,
        context: ContextModel,
        files: List[DocumentModel],
        rec_id: int,
        tag: Dict[str, str],
    ):
        for file in files:
            meta_data = DocMeta(
                org_id=context.org_id,
                form_id=context.form_id,
                record_id=rec_id,
                doc_type=file.doc_type,
            )
            meta_data = meta_data.model_copy(update=tag)

            try:
                await invoke.deleteDocument(
                    config=context.config,
                    org_id=context.org_id,
                    coll_name=context.form_id,
                    file_id=None,
                    metadata_params=DocQueryGenericModel(
                        **meta_data.model_dump(exclude_unset=True)
                    ),
                )
            except Exception as e:
                continue
        for file in files:
            meta_data = DocMeta(
                org_id=context.org_id,
                form_id=context.form_id,
                record_id=rec_id,
                doc_type=file.doc_type,
            )
            meta_data = meta_data.model_copy(update=tag)
            try:
                await invoke.addDocument(
                    config=context.config,
                    org_id=context.org_id,
                    coll_name=context.form_id,
                    document=file,
                    metadata=meta_data,
                )
            except Exception as e:
                raise PluginException(
                    message="Internal error occurred. Please contact support.",
                    detailed_message=f"Failed to save the document. Error:{str(e)}",
                )

    def get_extension_from_mime(self, mime_type: str) -> str:
        ext = mimetypes.guess_extension(mime_type)
        return ext

    def process_documents_for_output(
        self, fetched_documents_by_key: Dict[str, DBDocumentModel]
    ) -> List[DocumentModel]:
        """
        Given a mapping of logical keys to DBDocumentModel (each with one file),
        returns a dict of final file names and their content in bytes.
        """
        try:
            output_docs: List[DocumentModel] = []
            group_mapping = {
                "passport": ["passport_front", "passport_back"],
                "aadhaar_card": ["aadhaar_card_front", "aadhaar_card_back"],
                "bank_statement": ["bank_statement"],
                "salary_slip": ["salary_slip"],
                "flight_tickets": ["flight_tickets"],
                "appointment": ["appointment_schedule_document"],
                "photo": ["passport_size_photo"],
                "address_proof": ["address_proof"],
                "itinerary": ["itinerary"],
                "accommodation_proof": ["accommodation_proof"],
                "travel_insurance": ["travel_insurance"],
            }

            for group_name, key_list in group_mapping.items():
                group_docs: List[DBDocumentModel] = [
                    fetched_documents_by_key[key]
                    for key in key_list
                    if key in fetched_documents_by_key
                ]

                if not group_docs:
                    continue

                mime_types = {
                    doc.metadata.doc_type
                    for doc in group_docs
                    if doc.metadata and doc.metadata.doc_type
                }
                if not mime_types:
                    raise Exception(f"Missing MIME type in group '{group_name}'")

                if len(group_docs) == 1:
                    doc = group_docs[0]
                    mime_type = doc.metadata.doc_type
                    ext = self.get_extension_from_mime(mime_type)
                    doc_name = f"{group_name}{ext}"
                    output_docs.append(
                        DocumentModel(
                            doc_id=None,
                            doc_name=doc_name,
                            doc_type=mime_type,
                            doc_size=len(doc.doc_content),
                            doc_content=doc.doc_content,
                        )
                    )
                else:
                    mime_type = next(iter(mime_types))
                    if mime_type.startswith("image/"):
                        images = [
                            Image.open(BytesIO(doc.doc_content)).convert("RGB")
                            for doc in group_docs
                        ]
                        buffer = BytesIO()
                        images[0].save(
                            buffer,
                            format="PDF",
                            save_all=True,
                            append_images=images[1:],
                        )
                        pdf_bytes = buffer.getvalue()
                        output_docs.append(
                            DocumentModel(
                                doc_id=None,
                                doc_name=f"{group_name}.pdf",
                                doc_type="application/pdf",
                                doc_size=len(pdf_bytes),
                                doc_content=pdf_bytes,
                            )
                        )
                    elif mime_type == "application/pdf":
                        writer = PdfWriter()
                        for doc in group_docs:
                            reader = PdfReader(BytesIO(doc.doc_content))
                            for page in reader.pages:
                                writer.add_page(page)
                        buffer = BytesIO()
                        writer.write(buffer)
                        merged_bytes = buffer.getvalue()
                        output_docs.append(
                            DocumentModel(
                                doc_id=None,
                                doc_name=f"{group_name}.pdf",
                                doc_type="application/pdf",
                                doc_size=len(merged_bytes),
                                doc_content=merged_bytes,
                            )
                        )
                    else:
                        for i, doc in enumerate(group_docs):
                            ext = self.get_extension_from_mime(doc.metadata.doc_type)
                            doc_name = f"{group_name}_{i+1}{ext}"
                            output_docs.append(
                                DocumentModel(
                                    doc_id=None,
                                    doc_name=doc_name,
                                    doc_type=doc.metadata.doc_type,
                                    doc_size=len(doc.doc_content),
                                    doc_content=doc.doc_content,
                                )
                            )

            return output_docs
        except Exception as e:
            raise PluginException(
                message="Internal error occurred. Please try again.",
                detailed_message=f"Error occurred while processing the docs. Error: {str(e)}",
            )

    def obfuscate_string(self, data_str: str, static_key: str) -> str:
        """
        Obfuscates a string using AES encryption with a static key.

        :param data_str: The string that will be encrypted.
        :param static_key: The key used for encryption.
        :return: The obfuscated string in Base64 format.
        """
        try:
            # Ensure the key is exactly 16 bytes long
            key = static_key.encode().ljust(16, b"\0")

            # Data to encrypt
            data = data_str.encode()

            # Create cipher and encrypt the data with padding
            cipher = AES.new(key, AES.MODE_ECB)
            encrypted_data = cipher.encrypt(pad(data, AES.block_size))

            # Encode the encrypted data with Base64
            obfuscated_string = base64.urlsafe_b64encode(encrypted_data).decode()
            return obfuscated_string

        except Exception as e:
            raise PluginException(
                message="Internal error occurred. Please contact support.",
                detailed_message=f"Failed to obfuscate the string. Error: {str(e)}",
            )
