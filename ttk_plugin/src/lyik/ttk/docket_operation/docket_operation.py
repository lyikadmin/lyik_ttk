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
)
from lyikpluginmanager.annotation import RequiredVars, RequiredEnv
from io import BytesIO
from PIL import Image
from pypdf import PdfWriter, PdfReader
import mimetypes
import mimetypes
from lyik.ttk.models.forms.schengentouristvisa import (
    Schengentouristvisa,
)
from lyik.ttk.ttk_storage_util.ttk_storage import TTKStorage
from lyik.ttk.utils.operation_html_message import get_docket_operation_html_message
from lyik.ttk.utils.message import get_error_message
from lyik.ttk.docket_operation.docket_utilities.map_form_rec_to_schengen_pdf import (
    DocketUtilities,
)
from lyik.ttk.models.pdf.pdf_model import PDFModel
from typing import Annotated, Dict, List
from typing_extensions import Doc
import logging
import os
import io
import zipfile
from datetime import datetime


logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

PRIMARY_TRAVELLER = "Primary"
CO_TRAVELLER = "Co-traveller"
COLLECTION_NAME = "primary_travellers"
CODES = [
    "BEL",
    "HRV",
    "DNK",
    "EST",
    "FIN",
    "FRA",
    "DEU",
    "GRC",
    "ISL",
    "LVA",
    "LTU",
    "NLD",
    "NOR",
    "ROU",
    "SVK",
    "ESP",
    "SWE",
]
ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png"}
GENERATED_DOC_ID = "GENERATED_DOC"


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
            if not context or not context.config:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="The context or config is missing.",
                )
            config = context.config

            conn_url = config.DB_CONN_URL
            if not conn_url:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="DB_CONN_URL is missing in the config.",
                )

            org_id = context.org_id
            if not org_id:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="org_id is missing in the context.",
                )

            parsed_form_model = Schengentouristvisa(**form_record.model_dump())

            traveller_type = (
                parsed_form_model.visa_request_information.visa_request.traveller_type
            )
            if not traveller_type:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="traveller_type is missing in payload, hence the exception.",
                )

            order_id = parsed_form_model.visa_request_information.visa_request.order_id
            if not order_id:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="order_id is missing in the payload.",
                )

            if traveller_type == CO_TRAVELLER:
                try:
                    ttk_storage = TTKStorage(db_conn_url=conn_url)
                    fetched_data: GenericFormRecordModel = (
                        await ttk_storage.query_primary_info(
                            collection_name=COLLECTION_NAME,
                            org_id=org_id,
                            order_id=order_id,
                        )
                    )

                    if not fetched_data:
                        raise PluginException(
                            message=get_error_message(
                                error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                            ),
                            detailed_message="Failed to fetch the Primary traveller details.",
                        )

                    primary_traveller_data = Schengentouristvisa(
                        **fetched_data.model_dump(mode="json")
                    )

                    shared_traveller_info = parsed_form_model.shared_travell_info
                    shared = (
                        shared_traveller_info.shared
                        if shared_traveller_info.shared
                        else None
                    )

                    if shared:
                        if (
                            shared.itinerary_same != None
                            and shared.itinerary_same.value == "ITINERARY"
                        ):
                            primary_traveller_itinerary = (
                                primary_traveller_data.itinerary_accomodation
                            )
                            if (
                                not primary_traveller_itinerary
                                or not primary_traveller_itinerary.itinerary_card
                            ):
                                raise PluginException(
                                    message=get_error_message(
                                        error_message_code="LYIK_ERR_MISSING_ITINERARY_DOCKET"
                                    ),
                                    detailed_message="Primary traveller itinerary data is missing in the form record.",
                                )
                            parsed_form_model.itinerary_accomodation = (
                                primary_traveller_itinerary
                            )

                        if (
                            shared.accommodation_same != None
                            and shared.accommodation_same.value == "ACCOMMODATION"
                        ):
                            primary_traveller_accommodation = (
                                primary_traveller_data.accomodation
                            )
                            if not primary_traveller_accommodation:
                                raise PluginException(
                                    message=get_error_message(
                                        error_message_code="LYIK_ERR_MISSING_ACCOMMODATION_DOCKET"
                                    ),
                                    detailed_message="Primary traveller Accommodation data is missing in the form record.",
                                )
                            parsed_form_model.accomodation = (
                                primary_traveller_accommodation
                            )

                        if (
                            shared.flight_ticket_same != None
                            and shared.flight_ticket_same.value == "FLIGHT_TICKET"
                        ):
                            primary_traveller_flight_ticket = (
                                primary_traveller_data.ticketing
                            )
                            if (
                                not primary_traveller_flight_ticket
                                or not primary_traveller_flight_ticket.flight_tickets
                            ):
                                raise PluginException(
                                    message=get_error_message(
                                        error_message_code="LYIK_ERR_MISSING_FLIGHT_TICKET_DOCKET"
                                    ),
                                    detailed_message="Primary traveller Flight Tickets data is missing in the form record.",
                                )
                            parsed_form_model.ticketing = (
                                primary_traveller_flight_ticket
                            )

                except Exception as e:
                    raise PluginException(
                        get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message=f"Exception raised during fetch primary traveller details. Error: {str(e)}",
                    )

            generated_pdf_doc = None

            if (
                not parsed_form_model.consultant_info.application_form_embassy
                or not parsed_form_model.consultant_info.application_form_embassy.application_form
            ):

                docket_util = DocketUtilities()

                mapped_data: PDFModel = docket_util.map_schengen_to_pdf_model(
                    schengen_visa_data=parsed_form_model
                )

                data_dict: Dict = mapped_data.model_dump(mode="json")

                template_id = ""

                if parsed_form_model.visa_request_information.visa_request.to_country:
                    template_id = (
                        parsed_form_model.visa_request_information.visa_request.to_country
                    )
                else:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_MISSING_TO_COUNTRY_DOCKET"
                        ),
                        detailed_message="to_country field is not filled in visa_request_information.",
                    )

                final_template_id = "REF_PDF" if template_id in CODES else template_id

                transformed_data: TransformerResponseModel = (
                    await invoke.template_generate_pdf(
                        org_id=context.org_id,
                        config=context.config,
                        form_id=context.form_id,
                        additional_args={"record_id": record_id},
                        template_id=final_template_id,
                        form_name="schengenpdf",
                        record=data_dict,
                    )
                )

                if not transformed_data or not isinstance(
                    transformed_data, TransformerResponseModel
                ):
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_SOMETHING_WENT_WRONG"
                        ),
                        detailed_message=f"PDF generation failed. Error:{str(e),}",
                    )

                if transformed_data.status != TRANSFORMER_RESPONSE_STATUS.SUCCESS:
                    return OperationResponseModel(
                        status=OperationStatus.FAILED,
                        message=get_error_message(
                            error_message_code="LYIK_ERR_DOCKET_GEN_FAILURE"
                        ),
                    )

                pdfs: List[TemplateDocumentModel] = transformed_data.response
                pdf = pdfs[0]

                generated_pdf_doc = DBDocumentModel(
                    doc_id=GENERATED_DOC_ID,
                    doc_name=self.generate_application_pdf_name(
                        parsed_form_model.passport.passport_details.first_name,
                        parsed_form_model.visa_request_information.visa_request.to_country_full_name,
                    ),
                    doc_content=pdf.doc_content,
                    doc_size=len(pdf.doc_content),
                    metadata=DocMeta(
                        org_id=context.org_id,
                        form_id=context.form_id,
                        record_id=record_id,
                        doc_type=pdf.doc_type,
                    ),
                )

            files_in_rec_with_filename = self.get_files_from_record(
                parsed_form_model=parsed_form_model,
                pdf_doc_model=generated_pdf_doc,
            )

            fetched_documents_by_key: Dict[str, DBDocumentModel] = {}

            for key, file_data in files_in_rec_with_filename.items():
                if isinstance(file_data, dict):
                    try:
                        doc = DBDocumentModel(**file_data)
                        if doc.doc_id != GENERATED_DOC_ID:
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
                        else:
                            fetched_documents_by_key[key] = doc

                    except Exception as e:
                        raise PluginException(
                            message=get_error_message(
                                error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                            ),
                            detailed_message=f"Error while fetching document: {str(e)}",
                        )

            # ✅ Process and get final files
            processed_files: List[DocumentModel] = self.process_documents_for_output(
                fetched_documents_by_key
            )

            if len(processed_files) != 0:
                await self.store_all_files(
                    context=context,
                    files=processed_files,
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

            first_name = parsed_form_model.passport.passport_details.first_name or ""
            surname = parsed_form_model.passport.passport_details.surname or ""

            # Clean full name
            full_name = " ".join(f"{first_name} {surname}".split())
            # Spaces between words, title case
            file_name = f"{full_name} {datetime.now().strftime('%d %b %Y')}".title()

            # Build the download URL for the payload
            api_domain = os.getenv("API_DOMAIN")
            download_doc_endpoint = context.config.DOWNLOAD_DOC_API_ENDPOINT
            download_url = f"{api_domain}{download_doc_endpoint}{obfus_str}.zip?file_name={file_name}"

            # Return the successful operation response with the download URL
            html_msg = get_docket_operation_html_message(
                title_text="Your application is now ready to be submitted at your Visa Appointment!",
                instruction_points=[
                    "Download your Docket Zip File.",
                    "This ZIP file contains all necessary documents (excluding the originals you need to carry) along with an <strong>‘Instruction Sheet’</strong>.",
                    "Kindly print the documents, arrange them in the order specified in the Instruction Sheet, and bring them to your Visa Appointment.",
                ],
                url=download_url,
                action_text="Download Docket",
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
                message=get_error_message(
                    error_message_code="LYIK_ERR_UNEXPECTED_ERROR_DOCKET"
                ),
            )

    def get_files_from_record(
        self,
        parsed_form_model: Schengentouristvisa,
        pdf_doc_model: DBDocumentModel | None,
    ) -> Dict[str, any]:
        files_in_rec_with_filename = {}

        appointment = parsed_form_model.appointment
        passport = parsed_form_model.passport
        previous_visa = parsed_form_model.previous_visas
        additional_details = parsed_form_model.additional_details
        consultant_info = parsed_form_model.consultant_info
        itinerary = parsed_form_model.itinerary_accomodation
        address = parsed_form_model.residential_address
        flight = parsed_form_model.ticketing
        accommodation = parsed_form_model.accomodation
        travel_insurance = parsed_form_model.travel_insurance
        salary_slips = parsed_form_model.salary_slip
        bank_statement = parsed_form_model.bank_statement
        itr = parsed_form_model.itr_acknowledgement

        if consultant_info and consultant_info.instruction_letter:
            files_in_rec_with_filename["Instruction_sheet"] = (
                consultant_info.instruction_letter.upload_instruction
            )
        if appointment and appointment.appointment_scheduled:
            files_in_rec_with_filename["Visa_Appointment"] = (
                appointment.appointment_scheduled.upload_appointment
            )
        if passport and passport.passport_details:
            files_in_rec_with_filename["Passport_front"] = (
                passport.passport_details.ovd_front
            )
        if passport and passport.passport_details:
            files_in_rec_with_filename["Passport_back"] = (
                passport.passport_details.ovd_back
            )
        if previous_visa and previous_visa.previous_visas_details:
            files_in_rec_with_filename["Previous_Visa"] = (
                previous_visa.previous_visas_details.previous_visa_copy
            )
        if additional_details and additional_details.travel_info:
            files_in_rec_with_filename["Non-Schengen Visa"] = (
                additional_details.travel_info.visa_copy
            )
        if consultant_info and consultant_info.cover_letter:
            files_in_rec_with_filename["Cover_Letter"] = (
                consultant_info.cover_letter.cover_letter
            )
        if pdf_doc_model:
            files_in_rec_with_filename[pdf_doc_model.doc_name] = (
                pdf_doc_model.model_dump()
            )
        elif (
            consultant_info
            and consultant_info.application_form_embassy
            and consultant_info.application_form_embassy.application_form
        ):
            files_in_rec_with_filename[
                self.generate_application_pdf_name(
                    parsed_form_model.passport.passport_details.first_name,
                    parsed_form_model.visa_request_information.visa_request.to_country_full_name,
                )
            ] = consultant_info.application_form_embassy.application_form
        else:
            raise PluginException(
                message=get_error_message(
                    error_message_code="LYIK_ERR_MISSING_EMBASSY_FORM_DOCKET"
                ),
                detailed_message="Application Form from Embassy is not uploaded.",
            )

        if itinerary and itinerary.itinerary_card:
            files_in_rec_with_filename["Itinerary"] = (
                itinerary.itinerary_card.upload_itinerary
            )
        if address and address.residential_address_card_v1:
            files_in_rec_with_filename["Address_Proof"] = (
                address.residential_address_card_v1.address_proof_upload
            )
        if address and address.resident_in_other_country:
            files_in_rec_with_filename["Foreign_Address_Proof"] = (
                address.resident_in_other_country.address_proof
            )
        if flight and flight.flight_tickets:
            files_in_rec_with_filename["Flight_Tickets"] = (
                flight.flight_tickets.flight_tickets
            )
        if accommodation and accommodation.booked_appointment:
            files_in_rec_with_filename["Accommodation"] = (
                accommodation.booked_appointment.booking_upload
            )
        if travel_insurance and travel_insurance.flight_reservation_details:
            files_in_rec_with_filename["Travel_Insurance"] = (
                travel_insurance.flight_reservation_details.flight_reservation_tickets
            )
        if salary_slips and salary_slips.upload:
            files_in_rec_with_filename["Salary_Slips"] = salary_slips.upload.salary_slip
        if bank_statement and bank_statement.upload:
            files_in_rec_with_filename["Bank_Statements"] = (
                bank_statement.upload.bank_statements
            )
        if itr and itr.upload:
            files_in_rec_with_filename["ITR_Document"] = itr.upload.itr_acknowledgement
        if accommodation and accommodation.invitation_details:
            files_in_rec_with_filename["Inviter_Passport"] = (
                accommodation.invitation_details.passport_bio_page
            )
            files_in_rec_with_filename["Inviter_Visa"] = (
                accommodation.invitation_details.visa_copy_permit
            )
            files_in_rec_with_filename["Inviter_Accommodation"] = (
                accommodation.invitation_details.accommodation_proof
            )
        if additional_details and additional_details.national_id:
            files_in_rec_with_filename["Aadhaar_front"] = (
                additional_details.national_id.aadhaar_upload_front
            )
            files_in_rec_with_filename["Aadhaar_back"] = (
                additional_details.national_id.aadhaar_upload_back
            )
        if consultant_info and consultant_info.additional_documents:
            for idx, add_docs in enumerate(
                consultant_info.additional_documents, start=1
            ):
                if (
                    add_docs.additionaldocumentgroup
                    and add_docs.additionaldocumentgroup.additional_documents_card
                    and add_docs.additionaldocumentgroup.additional_documents_card.file_upload
                    and add_docs.additionaldocumentgroup.additional_documents_card.file_upload.get(
                        "doc_id"
                    )
                ):
                    key_name = (
                        add_docs.additionaldocumentgroup.additional_documents_card.document_name
                        if add_docs.additionaldocumentgroup.additional_documents_card.document_name
                        else f"Additional_Doc{idx:02d}"
                    )
                    files_in_rec_with_filename[key_name] = (
                        add_docs.additionaldocumentgroup.additional_documents_card.file_upload
                    )

        return files_in_rec_with_filename

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
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message=f"Failed to save the document. Error:{str(e)}",
                )

    def get_extension_from_mime(self, mime_type: str) -> str:
        ext = mimetypes.guess_extension(mime_type)
        return ext

    def process_documents_for_output(
        self, fetched_documents_by_key: Dict[str, DBDocumentModel]
    ) -> List[DocumentModel]:
        """
        Converts each fetched document to a DocumentModel, prefixing the file name with a sequence number
        starting from 02, and appending the correct extension.
        """
        try:
            output_docs: List[DocumentModel] = []

            keys_to_process = ["Salary_Slips", "Bank_Statements", "ITR_Document"]

            for key in keys_to_process:
                doc = fetched_documents_by_key.get(key)
                if doc:
                    self.maybe_unzip_and_replace(key, doc, fetched_documents_by_key)

            for index, (key, doc) in enumerate(
                fetched_documents_by_key.items(), start=1
            ):
                if not doc or not doc.doc_content:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message=f"The document object or the document content is missing for the key: {key}, hence the exception.",
                    )

                mime_type = doc.metadata.doc_type if doc.metadata else None
                if not mime_type:
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message=f"Missing MIME type for document key: {key}",
                    )

                seq_prefix = f"{index:02d}"

                # Convert image to PDF
                if mime_type.startswith("image/"):
                    image = Image.open(BytesIO(doc.doc_content)).convert("RGB")
                    buffer = BytesIO()
                    image.save(buffer, format="PDF")
                    pdf_bytes = buffer.getvalue()
                    doc_name = f"{seq_prefix}_{key}.pdf"
                    output_docs.append(
                        DocumentModel(
                            doc_id=None,
                            doc_name=doc_name,
                            doc_type="application/pdf",
                            doc_size=len(pdf_bytes),
                            doc_content=pdf_bytes,
                        )
                    )
                else:
                    # Keep PDFs or other supported files as-is
                    ext = self.get_extension_from_mime(mime_type)
                    doc_name = f"{seq_prefix}_{key}{ext}"
                    output_docs.append(
                        DocumentModel(
                            doc_id=None,
                            doc_name=doc_name,
                            doc_type=mime_type,
                            doc_size=len(doc.doc_content),
                            doc_content=doc.doc_content,
                        )
                    )
            return output_docs

        except Exception as e:
            raise PluginException(
                message=get_error_message(
                    error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                ),
                detailed_message=f"Error while processing the documents: {str(e)}",
            )

    def _is_zip_bytes(self, b: bytes) -> bool:
        try:
            return zipfile.is_zipfile(io.BytesIO(b))
        except Exception:
            return False

    def _is_zip_mime(self, m: str | None) -> bool:
        if not m:
            return False
        m = m.lower()
        return (
            m == "application/zip"
            or "zip" in m  # catches x-zip-compressed, x-zip, multipart/x-zip, etc.
            or m == "application/octet-stream"
        )

    def maybe_unzip_and_replace(
        self, key: str, doc: DBDocumentModel, fetched_dict: dict[str, DBDocumentModel]
    ):
        mime = (doc.metadata.doc_type or "").lower() if doc.metadata else ""
        if doc.doc_content and (
            self._is_zip_mime(mime) or self._is_zip_bytes(doc.doc_content)
        ):
            extracted_docs = self.create_extracted_documents_from_zip(doc, key)

            # Preserve order
            new_dict = {}
            for existing_key in list(fetched_dict.keys()):
                if existing_key == key:
                    new_dict.update(extracted_docs)
                else:
                    new_dict[existing_key] = fetched_dict[existing_key]
            fetched_dict.clear()
            fetched_dict.update(new_dict)
        else:
            pass

    def create_extracted_documents_from_zip(
        self, original_doc: DBDocumentModel, base_key: str
    ) -> dict[str, DBDocumentModel]:
        """
        Extracts files from a zip if they are PDF or image, and builds
        DBDocumentModels for them. Keys are formed using `key_prefix`.

        Raises:
            ValueError: If extracted file is not a supported type.
        """
        new_entries: Dict[str, DBDocumentModel] = {}

        with zipfile.ZipFile(io.BytesIO(original_doc.doc_content)) as zip_file:
            valid_files = [
                f
                for f in zip_file.infolist()
                if not f.is_dir()
                and not f.filename.startswith("__MACOSX")
                and not os.path.basename(f.filename).startswith("._")
            ]

            for index, file_info in enumerate(valid_files):
                file_bytes = zip_file.read(file_info)
                mime_type, _ = mimetypes.guess_type(file_info.filename)

                if mime_type not in ALLOWED_MIME_TYPES:
                    raise ValueError(
                        f"Unsupported file type inside zip: {file_info.filename} ({mime_type})"
                    )

                # Override MIME type while preserving other metadata
                new_metadata = original_doc.metadata.model_copy(deep=True)
                new_metadata.doc_type = mime_type

                # Set key
                if len(valid_files) == 1:
                    key_name = base_key
                else:
                    key_name = f"{base_key}_{index + 1}"

                new_entries[key_name] = DBDocumentModel(
                    doc_id=None,
                    doc_name=os.path.basename(file_info.filename),
                    doc_size=len(file_bytes),
                    doc_content=file_bytes,
                    metadata=new_metadata,
                )

        return new_entries

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
                message=get_error_message(
                    error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                ),
                detailed_message=f"Failed to obfuscate the string. Error: {str(e)}",
            )

    def generate_application_pdf_name(self, first_name: str, country_name: str) -> str:
        """
        Generates the application PDF file name in the format:
        <FirstName_with_Underscores>_<CountryName_with_Underscores>_Application.pdf

        - First name: strip spaces, title case, replace spaces with underscores
        - Country name: strip spaces, title case, replace spaces with underscores
        """
        first_name_clean = first_name.strip().title().replace(" ", "_")
        country_clean = country_name.strip().title().replace(" ", "_")
        return f"{first_name_clean}_{country_clean}_Application"
