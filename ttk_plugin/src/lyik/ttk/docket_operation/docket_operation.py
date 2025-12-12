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
    DocxTemplateModel,
)
from lyikpluginmanager.annotation import RequiredVars, RequiredEnv
from io import BytesIO
from PIL import Image
import mimetypes
import mimetypes

from lyik.ttk.models.generated.universal_model_with_all_shared_sections import (
    UniversalModelWithAllSharedSections,
    SAMEITINERARYASPRIMARY,
    SAMEACCOMMODATIONASPRIMARY,
    SAMEFLIGHTTICKETASPRIMARY,
)
from lyik.ttk.models.forms.schengentouristvisa import Schengentouristvisa
from lyik.ttk.ttk_storage_util.ttk_storage import TTKStorage
from lyik.ttk.utils.operation_html_message import get_docket_operation_html_message
from lyik.ttk.utils.message import get_error_message

from lyik.ttk.docket_operation.docket_utilities.schengen_pdf_mapping import (
    map_schengen_pdf,
)
from lyik.ttk.models.pdf.schengen_pdf_model import SchengenPDFModel
from lyik.ttk.docket_operation.docket_utilities.pdf_mapping_util import PDFMappingUtil

from typing import Annotated, Dict, List, Any
from functools import lru_cache
from typing_extensions import Doc
import logging
import os
import io
import zipfile, filetype, tarfile
import rarfile
import py7zr
from datetime import datetime
from lyik.ttk.utils.form_indicator import FormIndicator, get_form_indicator
from lyik.ttk.utils.csv_utils import load_csv_rows


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
FOLDERS = [
    "pdf",
    "docx",
]
ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png"}
GENERATED_DOC_ID = "GENERATED_DOC"
ZIP_MIMES = {"application/zip", "application/x-zip-compressed"}
RAR_MIMES = {"application/x-rar", "application/vnd.rar"}
SEVENZ_MIMES = {"application/x-7z-compressed"}
TAR_MIMES = {"application/x-tar", "application/x-gtar"}
GZ_MIMES = {"application/gzip", "application/x-gzip"}
BZ2_MIMES = {"application/x-bzip2"}


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
        RequiredEnv(["API_DOMAIN", "CRED_FILES_MOUNT_PATH", "LYIK_ROOT_PATH"]),
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

            form_indicator: FormIndicator = get_form_indicator(
                form_rec=form_record.model_dump(mode="json")
            )

            parsed_form_model = UniversalModelWithAllSharedSections(
                **form_record.model_dump()
            )

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

                    primary_traveller_data = UniversalModelWithAllSharedSections(
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
                            and shared.itinerary_same
                            == SAMEITINERARYASPRIMARY.ITINERARY.value
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
                            and shared.accommodation_same
                            == SAMEACCOMMODATIONASPRIMARY.ACCOMMODATION.value
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
                            and shared.flight_ticket_same
                            == SAMEFLIGHTTICKETASPRIMARY.FLIGHT_TICKET.value
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

            if parsed_form_model.visa_request_information.visa_request.to_country:
                to_country = (
                    parsed_form_model.visa_request_information.visa_request.to_country
                )
            else:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_MISSING_TO_COUNTRY_DOCKET"
                    ),
                    detailed_message="to_country field is not filled in visa_request_information.",
                )

            generated_application_doc_model = None

            # if (
            #     not parsed_form_model.consultant_info.application_form_embassy
            #     or not parsed_form_model.consultant_info.application_form_embassy.application_form
            # ):

            generated_appl_doc: TemplateDocumentModel = (
                await self._get_generated_application_doc(
                    context=context,
                    form_record=form_record,
                    form_indicator=form_indicator,
                    record_id=record_id,
                    to_country=to_country,
                )
            )

            generated_application_doc_model = DBDocumentModel(
                doc_id=GENERATED_DOC_ID,
                doc_name=self.generate_application_name(
                    parsed_form_model.passport.passport_details.first_name,
                    parsed_form_model.visa_request_information.visa_request.to_country_full_name,
                ),
                doc_content=generated_appl_doc.doc_content,
                doc_size=len(generated_appl_doc.doc_content),
                metadata=DocMeta(
                    org_id=context.org_id,
                    form_id=context.form_id,
                    record_id=record_id,
                    doc_type=generated_appl_doc.doc_type,
                ),
            )

            files_in_rec_with_filename = self.get_files_from_record(
                parsed_form_model=parsed_form_model,
                application_doc_model=generated_application_doc_model,
                form_indicator=form_indicator,
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

    async def _get_generated_application_doc(
        self,
        context: ContextModel,
        record_id: str,
        form_indicator: FormIndicator,
        form_record: GenericFormRecordModel,
        to_country: str,
    ) -> TemplateDocumentModel:
        """
        This function is responsible for the following:

        In case of offline journey:
        1. Call the appropriate mapping utility for pdf mapping based on the country.
        2. Get the mapped data and call the pdf transformer and pass the appropriate pdf template for generating application document.

        In case of online journey:
        1. Call the docx transformer, pass the appropriate docx based on the country to generate application doc.

        In both the cases, return the application doc.
        """

        transformed_data = None

        if form_indicator == FormIndicator.SCHENGEN:
            schengen_mapped_data: SchengenPDFModel = map_schengen_pdf(
                schengen_visa_data=Schengentouristvisa(**form_record.model_dump())
            )

            data_dict: Dict = schengen_mapped_data.model_dump(mode="json")

            template_id = to_country

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
                    keep_pdf_editable=False,
                )
            )
        else:
            type_of_dir = self._detect_template_folder(country_code=to_country)

            if type_of_dir:
                if type_of_dir == "pdf":
                    util = PDFMappingUtil(form_record.model_dump())
                    mapped_data: Dict = util.get_mapped_data(form_indicator)

                    # if form_indicator == FormIndicator.SGP_SINGAPORE:
                    #     mapped_data: Dict = map_singapore_to_pdf(
                    #         form_data=form_record.model_dump()
                    #     )
                    # if form_indicator == FormIndicator.MEX_MEXICO:
                    #     mapped_data: Dict = map_mexico_pdf(
                    #         form_data=form_record.model_dump()
                    #     )
                    # if form_indicator == FormIndicator.JPN_JAPAN:
                    #     mapped_data: Dict = map_japan_pdf(
                    #         form_data=form_record.model_dump()
                    #     )

                    transformed_data: TransformerResponseModel = (
                        await invoke.template_generate_pdf(
                            org_id=context.org_id,
                            config=context.config,
                            form_id=context.form_id,
                            additional_args={"record_id": record_id},
                            template_id=to_country,
                            form_name="countryapplicationtemplates",
                            record=mapped_data,
                            keep_pdf_editable=False,
                        )
                    )
                else:
                    transformed_data: TransformerResponseModel = (
                        await invoke.template_generate_docx(
                            org_id=context.org_id,
                            config=context.config,
                            record=form_record,
                            form_id=context.form_id,
                            additional_args={},
                            fetch_from_db_or_path=False,
                            form_name="countryapplicationtemplates",
                            template=DocxTemplateModel(template=to_country),
                        )
                    )
            else:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message=f"Failed to locate the template file.",
                )

        if not transformed_data or not isinstance(
            transformed_data, TransformerResponseModel
        ):
            raise PluginException(
                message=get_error_message(
                    error_message_code="LYIK_ERR_SOMETHING_WENT_WRONG"
                ),
                detailed_message=f"PDF generation failed.",
            )

        if transformed_data.status != TRANSFORMER_RESPONSE_STATUS.SUCCESS:
            return OperationResponseModel(
                status=OperationStatus.FAILED,
                message=get_error_message(
                    error_message_code="LYIK_ERR_DOCKET_GEN_FAILURE"
                ),
            )

        docs: List[TemplateDocumentModel] = transformed_data.response
        return docs[0]

    def _detect_template_folder(self, country_code: str) -> str | None:
        """
        Returns: 'pdf', 'docx', or None if not found.
        """

        base_dir = os.getenv("LYIK_ROOT_PATH", "/lyik")
        for folder in FOLDERS:
            path = os.path.join(
                base_dir,
                "templates",
                "countryapplicationtemplates",
                folder,
                country_code,
            )
            if os.path.isdir(path):
                return folder

        return None

    @staticmethod
    def load_csv(file_path: str) -> List[Dict[str, str]]:
        """
        Docket-sequence specific loader.

        - Uses the generic `load_csv_rows`
        - Sorts rows by the 'order' column (default 0 if missing/invalid)
        """
        rows = load_csv_rows(file_path)

        def _order_key(row: Dict[str, str]) -> int:
            raw = row.get("order", 0)
            try:
                return int(raw)
            except (TypeError, ValueError):
                return 0

        # Return a new sorted list so we don't mutate the cached `rows`
        return sorted(rows, key=_order_key)

    def _resolve_path(self, obj, path: str):
        """Safely resolve dotted path like a.b.c supporting Pydantic models and dicts."""
        try:
            for part in path.split("."):
                if obj is None:
                    return None

                # Handle list index: something.0.name
                if isinstance(obj, list) and part.isdigit():
                    idx = int(part)
                    if idx < 0 or idx >= len(obj):
                        return None
                    obj = obj[idx]
                    continue

                # Handle dict keys
                if isinstance(obj, dict):
                    obj = obj.get(part)
                    continue

                # Handle Pydantic model attributes (incl. model_extra)
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                    continue

                # Nothing matched → path broken
                return None

            return obj
        except Exception:
            return None

    def _find_upload_dict(self, obj):
        """Recursively find the dict that contains a real uploaded file (doc_id)."""
        if obj is None:
            return None

        if isinstance(obj, dict) and obj.get("doc_id"):
            return obj

        if isinstance(obj, dict):
            for v in obj.values():
                found = self._find_upload_dict(v)
                if found:
                    return found

        if isinstance(obj, list):
            for item in obj:
                found = self._find_upload_dict(item)
                if found:
                    return found

        if hasattr(obj, "__dict__"):
            for v in obj.__dict__.values():
                found = self._find_upload_dict(v)
                if found:
                    return found

        return None

    def _find_document_name(self, obj):
        """Recursively locate the first non-empty 'document_name' in dicts, lists, or model attributes."""

        if obj is None:
            return None

        # Handle dict (must check key BEFORE recursing into values)
        if isinstance(obj, dict):
            if obj.get("document_name"):
                return obj["document_name"]

            for v in obj.values():
                found = self._find_document_name(v)
                if found:
                    return found

            return None

        # Handle list
        if isinstance(obj, list):
            for item in obj:
                found = self._find_document_name(item)
                if found:
                    return found
            return None

        # Handle object with attributes (Pydantic / dataclass / normal class)
        if hasattr(obj, "__dict__"):
            attrs = obj.__dict__

            # Check attribute directly
            if attrs.get("document_name"):
                return attrs["document_name"]

            # Then recurse into attributes
            for v in attrs.values():
                found = self._find_document_name(v)
                if found:
                    return found
            return None

        # Anything else (primitive, None, etc.) has no structure → skip
        return None

    def get_files_from_record(
        self,
        parsed_form_model: UniversalModelWithAllSharedSections,
        application_doc_model: DBDocumentModel | None,
        form_indicator: FormIndicator,
    ) -> Dict[str, Any]:

        files = {}
        next_index = 1
        visa_type = parsed_form_model.visa_request_information.visa_request.visa_type

        mount_path = os.getenv("CRED_FILES_MOUNT_PATH")

        if not mount_path:
            raise ValueError(
                f"Missing mount_path: '{mount_path}'. Cannot import CSV file."
            )

        docket_seq_files_path = os.path.join(mount_path, "docket_sequence")

        if not os.path.exists(docket_seq_files_path):
            raise FileNotFoundError(
                f"Docket Sequence directory not found: {docket_seq_files_path}"
            )

        # Build the expected filename
        expected_file_name = f"{form_indicator.value}.csv"
        seq_file_path = os.path.join(
            mount_path, docket_seq_files_path, expected_file_name
        )

        if not os.path.exists(seq_file_path) or not os.path.isfile(seq_file_path):
            raise FileNotFoundError(
                f"Docket Sequence CSV file not found: {seq_file_path}"
            )

        for row in self.load_csv(seq_file_path):
            file_name = row["Name of the Document"]
            path = row["Upload Field Attribute"]
            row_visa_type = row["Type of Visa"]
            repeatable = (
                row["Is this Field Repeatable?"].lower() == "yes"
                if row["Is this Field Repeatable?"]
                else False
            )
            naming_template = row["Default Placeholder Name"]

            # Visa type check
            if (
                row_visa_type
                and str(row_visa_type).strip().lower() != str(visa_type).strip().lower()
            ):
                continue

            # SPECIAL case for PDF
            if path == "**FILLED_APPLICATION_DOC**":
                if application_doc_model:
                    files[application_doc_model.doc_name] = (
                        application_doc_model.model_dump()
                    )
                continue

            # Regular path evaluation
            value = self._resolve_path(parsed_form_model, path)
            if not value:
                continue

            # Handle repeatable dynamic entries
            if repeatable and isinstance(value, list):
                for item in value:
                    if not item:
                        continue

                    # 1) Find the file object
                    upload_dict = self._find_upload_dict(item)
                    if not upload_dict:
                        continue

                    # 2) Find document name (recursive)
                    doc_name = self._find_document_name(item)

                    # 3) Fallback to placeholder
                    final_name = doc_name or naming_template.format(index=next_index)

                    # 4) Add file
                    files[final_name] = upload_dict
                    next_index += 1

                continue

            files[file_name] = value

        return files

    # def get_files_from_record(
    #     self,
    #     parsed_form_model: Schengentouristvisa,
    #     pdf_doc_model: DBDocumentModel | None,
    # ) -> Dict[str, any]:
    #     files_in_rec_with_filename = {}
    #     next_index = 1

    #     visa_type = parsed_form_model.visa_request_information.visa_request.visa_type

    #     appointment = parsed_form_model.appointment
    #     passport = parsed_form_model.passport
    #     previous_visa = parsed_form_model.previous_visas
    #     additional_details = parsed_form_model.additional_details
    #     cover_letter_info = parsed_form_model.cover_letter_info
    #     invitation = parsed_form_model.invitation
    #     consultant_info = parsed_form_model.consultant_info
    #     itinerary = parsed_form_model.itinerary_accomodation
    #     address = parsed_form_model.residential_address
    #     flight = parsed_form_model.ticketing
    #     accommodation = parsed_form_model.accomodation
    #     travel_insurance = parsed_form_model.travel_insurance
    #     salary_slips = parsed_form_model.salary_slip
    #     bank_statement = parsed_form_model.bank_statement
    #     company_bank_statement = parsed_form_model.company_bank_statement
    #     company_incorporation_document = parsed_form_model.company_docs
    #     itr = parsed_form_model.itr_acknowledgement
    #     additional_documents = parsed_form_model.additional_documents_pane

    #     if consultant_info and consultant_info.instruction_letter:
    #         files_in_rec_with_filename["Instruction_sheet"] = (
    #             consultant_info.instruction_letter.upload_instruction
    #         )
    #     if appointment and appointment.appointment_scheduled:
    #         files_in_rec_with_filename["Visa_Appointment"] = (
    #             appointment.appointment_scheduled.upload_appointment
    #         )
    #     if passport and passport.passport_details:
    #         files_in_rec_with_filename["Passport_front"] = (
    #             passport.passport_details.ovd_front
    #         )
    #     if passport and passport.passport_details:
    #         files_in_rec_with_filename["Passport_back"] = (
    #             passport.passport_details.ovd_back
    #         )
    #     if previous_visa and previous_visa.previous_visas_details:
    #         files_in_rec_with_filename["Previous_Visa"] = (
    #             previous_visa.previous_visas_details.previous_visa_copy
    #         )
    #     if additional_details and additional_details.travel_info:
    #         files_in_rec_with_filename["Non-Schengen Visa"] = (
    #             additional_details.travel_info.visa_copy
    #         )
    #     if pdf_doc_model:
    #         files_in_rec_with_filename[pdf_doc_model.doc_name] = (
    #             pdf_doc_model.model_dump()
    #         )
    #     if visa_type == VISATYPE.Business:
    #         if cover_letter_info and cover_letter_info.covering_letter_card:
    #             files_in_rec_with_filename["Cover_Letter"] = (
    #                 cover_letter_info.covering_letter_card.cover_upload
    #             )
    #         if invitation and invitation.invitation_letter_upload:
    #             files_in_rec_with_filename["Invitation_Letter"] = (
    #                 invitation.invitation_letter_upload.invite_upload
    #             )
    #     if itinerary and itinerary.itinerary_card:
    #         files_in_rec_with_filename["Itinerary"] = (
    #             itinerary.itinerary_card.upload_itinerary
    #         )
    #     if address and address.residential_address_card_v1:
    #         files_in_rec_with_filename["Address_Proof"] = (
    #             address.residential_address_card_v1.address_proof_upload
    #         )
    #     if address and address.resident_in_other_country:
    #         files_in_rec_with_filename["Foreign_Address_Proof"] = (
    #             address.resident_in_other_country.address_proof
    #         )
    #     if flight and flight.flight_tickets:
    #         files_in_rec_with_filename["Flight_Tickets"] = (
    #             flight.flight_tickets.flight_tickets
    #         )
    #     if accommodation and accommodation.booked_appointment:
    #         files_in_rec_with_filename["Accommodation"] = (
    #             accommodation.booked_appointment.booking_upload
    #         )
    #     if travel_insurance and travel_insurance.flight_reservation_details:
    #         files_in_rec_with_filename["Travel_Insurance"] = (
    #             travel_insurance.flight_reservation_details.flight_reservation_tickets
    #         )
    #     if salary_slips and salary_slips.upload:
    #         files_in_rec_with_filename["Salary_Slips"] = salary_slips.upload.salary_slip
    #     if bank_statement and bank_statement.upload:
    #         files_in_rec_with_filename["Bank_Statements"] = (
    #             bank_statement.upload.bank_statements
    #         )
    #     if visa_type == VISATYPE.Business:
    #         if company_bank_statement and company_bank_statement.statements_card:
    #             files_in_rec_with_filename["Company_Bank_Statement"] = (
    #                 company_bank_statement.statements_card.statement_file
    #             )
    #         if (
    #             company_incorporation_document
    #             and company_incorporation_document.incorporation_docs
    #         ):
    #             files_in_rec_with_filename["Company_Incorporation_Certificate"] = (
    #                 company_incorporation_document.incorporation_docs.statement_file
    #             )
    #     if itr and itr.upload:
    #         files_in_rec_with_filename["ITR_Document"] = itr.upload.itr_acknowledgement
    #     if accommodation and accommodation.invitation_details:
    #         files_in_rec_with_filename["Inviter_Passport"] = (
    #             accommodation.invitation_details.passport_bio_page
    #         )
    #         files_in_rec_with_filename["Inviter_Visa"] = (
    #             accommodation.invitation_details.visa_copy_permit
    #         )
    #         files_in_rec_with_filename["Inviter_Accommodation"] = (
    #             accommodation.invitation_details.accommodation_proof
    #         )
    #     if additional_details and additional_details.national_id:
    #         files_in_rec_with_filename["Aadhaar_front"] = (
    #             additional_details.national_id.aadhaar_upload_front
    #         )
    #         files_in_rec_with_filename["Aadhaar_back"] = (
    #             additional_details.national_id.aadhaar_upload_back
    #         )
    #     if consultant_info and consultant_info.additional_documents:
    #         for ci_add_docs in consultant_info.additional_documents:
    #             ci_doc_group = ci_add_docs.additionaldocumentgroup
    #             if (
    #                 ci_doc_group
    #                 and ci_doc_group.additional_documents_card
    #                 and ci_doc_group.additional_documents_card.file_upload
    #                 and ci_doc_group.additional_documents_card.file_upload.get("doc_id")
    #             ):
    #                 card = ci_doc_group.additional_documents_card
    #                 key_name = card.document_name or f"Additional_Doc{next_index:02d}"
    #                 files_in_rec_with_filename[key_name] = card.file_upload
    #                 next_index += 1
    #     if additional_documents and additional_documents.additional_documents_traveller_group:
    #         for add_docs in additional_documents.additional_documents_traveller_group:
    #             doc_group = add_docs.additionaldocumentgrouptraveller
    #             if (
    #                 doc_group
    #                 and doc_group.additional_documents_card_traveller
    #                 and doc_group.additional_documents_card_traveller.file_upload
    #                 and doc_group.additional_documents_card_traveller.file_upload.get(
    #                     "doc_id"
    #                 )
    #             ):
    #                 doc_card = doc_group.additional_documents_card_traveller
    #                 key_name = (
    #                     doc_card.document_name_display or f"Additional_Doc{next_index:02d}"
    #                 )
    #                 files_in_rec_with_filename[key_name] = doc_card.file_upload
    #                 next_index += 1

    #     return files_in_rec_with_filename

    def add_documents_to_dict(
        documents_list, files_dict, start_index=1, prefix="Additional_Doc"
    ):
        """
        Adds documents from a list to files_dict, numbering them continuously.
        Returns the next available index after processing.
        """
        if not documents_list:
            return start_index

        for idx, add_docs in enumerate(documents_list, start=start_index):
            # Try to get the card safely (works for both sections)
            card = (
                getattr(add_docs, "additionaldocumentgroup", None)
                and getattr(
                    add_docs.additionaldocumentgroup, "additional_documents_card", None
                )
            ) or getattr(add_docs, "additional_documents_card", None)

            if not card:
                continue

            file_upload = getattr(card, "file_upload", None)
            if not (file_upload and file_upload.get("doc_id")):
                continue

            # Document name or fallback with continuous numbering
            key_name = card.document_name or f"{prefix}{idx:02d}"
            files_dict[key_name] = file_upload

        # Next available index
        return idx + 1

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

    def maybe_unzip_and_replace(
        self, key: str, doc: DBDocumentModel, fetched_dict: dict[str, DBDocumentModel]
    ):
        if not doc.doc_content:
            return

        # Detect MIME from bytes
        kind = filetype.guess(doc.doc_content)
        mime = kind.mime if kind else None

        archive_type = None
        if mime in ZIP_MIMES:
            archive_type = "zip"
        elif mime in RAR_MIMES:
            archive_type = "rar"
        elif mime in SEVENZ_MIMES:
            archive_type = "7z"
        elif mime in TAR_MIMES | GZ_MIMES | BZ2_MIMES:
            archive_type = "tar"

        # Fallback: zipfile check
        if not archive_type:
            try:
                if zipfile.is_zipfile(io.BytesIO(doc.doc_content)):
                    archive_type = "zip"
            except Exception:
                archive_type = None

        if archive_type:
            extracted_docs = self.create_extracted_documents_from_zip(
                doc, key, archive_type
            )

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
        self, original_doc: DBDocumentModel, base_key: str, archive_type: str
    ) -> dict[str, DBDocumentModel]:
        """
        Extracts files from a supported archive (zip, rar, 7z, tar/gz/bz2),
        and builds DBDocumentModels for them. Keys are formed using `base_key`.

        Raises:
            ValueError: If extracted file is not a supported type.
        """
        new_entries: Dict[str, DBDocumentModel] = {}

        if archive_type == "zip":
            archive = zipfile.ZipFile(io.BytesIO(original_doc.doc_content))
            file_list = [
                f
                for f in archive.infolist()
                if not f.is_dir()
                and not f.filename.startswith("__MACOSX")
                and not os.path.basename(f.filename).startswith("._")
            ]
            extractor = lambda f: archive.read(f)
            get_filename = lambda f: f.filename

        elif archive_type == "rar" and rarfile:
            archive = rarfile.RarFile(io.BytesIO(original_doc.doc_content))
            file_list = archive.infolist()
            extractor = lambda f: archive.read(f)
            get_filename = lambda f: f.filename

        elif archive_type == "7z" and py7zr:
            archive = py7zr.SevenZipFile(io.BytesIO(original_doc.doc_content))
            file_list = archive.getnames()
            extractor = lambda f: archive.read([f])[f]
            get_filename = lambda f: f

        elif archive_type == "tar":
            archive = tarfile.open(fileobj=io.BytesIO(original_doc.doc_content))
            file_list = [f for f in archive.getmembers() if f.isfile()]
            extractor = lambda f: archive.extractfile(f).read()
            get_filename = lambda f: f.name

        else:
            raise ValueError(
                f"Cannot extract the files. Unsupported archive type: {archive_type}"
            )

        for index, file_info in enumerate(file_list):
            filename = get_filename(file_info)
            file_bytes = extractor(file_info)
            mime_type, _ = mimetypes.guess_type(filename)

            if mime_type not in ALLOWED_MIME_TYPES:
                raise ValueError(
                    f"Unsupported file type inside zip: {file_info.filename} ({mime_type})"
                )

            # Override MIME type while preserving other metadata
            new_metadata = original_doc.metadata.model_copy(deep=True)
            new_metadata.doc_type = mime_type

            # Set key
            if len(file_list) == 1:
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

    def generate_application_name(self, first_name: str, country_name: str) -> str:
        """
        Generates the application file name in the format:
        <FirstName_with_Underscores>_<CountryName_with_Underscores>_Application.<ext>

        - First name: strip spaces, title case, replace spaces with underscores
        - Country name: strip spaces, title case, replace spaces with underscores
        """
        first_name_clean = first_name.strip().title().replace(" ", "_")
        country_clean = country_name.strip().title().replace(" ", "_")
        return f"{first_name_clean}_{country_clean}_Application"
