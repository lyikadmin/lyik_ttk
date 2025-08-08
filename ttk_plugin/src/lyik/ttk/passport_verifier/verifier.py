import apluggy as pluggy
import os
from pydantic import BaseModel, ConfigDict, Field, model_validator
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
    DocMeta,
    PluginException,
)
from typing import Annotated, List, Union, Tuple, Dict, Any
from typing_extensions import Doc
from lyikpluginmanager import invoke, DBDocumentModel, DocumentModel
from lyikpluginmanager.models.ovd import OVDGenericResponse, OVDPassport, OVDType
from lyikpluginmanager.core.utils import generate_hash_id_from_dict
from lyikpluginmanager.annotation import RequiresValidation
from ..models.forms.schengentouristvisa import RootPassportPassportDetails
from ..utils.verifier_util import validate_pincode, validate_passport_number
from ..utils.message import get_error_message
import logging
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import tempfile
import base64
import mimetypes
import textwrap


logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())


class PassportVerificationPlugin(VerifyHandlerSpec):
    """
    Passport date verification plugin, with the dynamic duration validity.
    """

    @impl
    async def verify_handler(
        self,
        context: ContextModel | None,
        payload: Annotated[
            RootPassportPassportDetails,
            Doc("Payload for passport ocr and validation."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        RequiresValidation(False),
        Doc("Response after validating the passport."),
    ]:
        """
        This Verifier fetches the data of passport and verifies.
        Returns the verifies data for autofilling.
        Saves the images in the Database.
        """
        payload_dict = payload.model_dump(mode="json")

        ret = check_if_verified(payload=payload_dict)
        if ret:
            return ret

        try:
            # Check if the front and back image of the Passport is available
            if not payload.ovd_front and not payload.ovd_back:
                logger.error("Front or Back image of the passport is not uploaded.")
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                    message=get_error_message(
                        error_message_code="LYIK_ERR_MISSING_IMAGES_PASSPORT"
                    ),
                )

            if isinstance(payload.ovd_front, str) and isinstance(payload.ovd_back, str):
                logger.info("OCR and verification flow initiated for the Passport.")

                # Get the OCR data from the OCR service
                ovd_response: OVDPassport = await get_ocr_data(
                    context=context, payload=payload
                )

                logger.info("Successfully fetched the OCR data for the Passport.")

                # Check if the document_type exists
                if not ovd_response.document_type:
                    logger.error(f"Document type is not present in the ovd response.")
                    return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                    )

                # Check if the document_type is Passport or not
                if ovd_response.document_type != OVDType.PASSPORT:
                    logger.error(
                        f"The OVDType is expected to be Passport. Instead received type: {ovd_response.document_type.value}"
                    )
                    return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                        message=get_error_message(
                            error_message_code="LYIK_ERR_INVALID_PASSPORT"
                        ),
                    )

                # Map the data from the ovd response to the passport model
                map_fields_to_payload(
                    payload=payload,
                    response=ovd_response,
                )
                logger.info("Mapped fields to the payload from OVD response.")

                # Save the images in the DB
                image_1, image_2 = await add_ovd_images_to_doc_store(
                    context=context,
                    image_1=payload.ovd_front,
                    image_2=payload.ovd_back,
                )

                logger.debug("Images saved to DB")

                if image_1:
                    payload.ovd_front = image_1
                if image_2:
                    payload.ovd_back = image_2

                # Check if passport number is valid or not.
                passport_number = payload.passport_number
                if passport_number:
                    try:
                        valid_passport_number = validate_passport_number(
                            value=passport_number
                        )
                        if valid_passport_number:
                            logger.info("Passport Number is valid.")
                    except Exception as e:
                        raise PluginException(
                            message=str(e),
                            detailed_message="The Passport Number format is invalid.",
                        )

                # Check if the PIN Code is valid or not.
                pincode = payload.pin_code
                if pincode:
                    try:
                        valid_pincode = validate_pincode(value=payload.pin_code)
                        if valid_pincode:
                            logger.info("PIN Code is valid.")
                    except Exception as e:
                        raise PluginException(
                            message=str(e),
                            detailed_message="The PIN Code format is invalid.",
                        )

                # Check the expiry status of the Passport
                expiry_validation = check_expiry_validation(payload=payload)
                if expiry_validation:
                    logger.warning("Passport has expired.")
                    return expiry_validation

                logger.info("Passport is verified successfully.")
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                    message="",  # verified_successfully
                    actor="system",
                    response=payload.model_dump(),
                )
            elif isinstance(payload.ovd_front, Dict) and isinstance(
                payload.ovd_back, Dict
            ):
                logger.info("Existing passport, initiating verification.")
                # Check if passport number is valid or not.
                passport_number = payload.passport_number
                if passport_number:
                    try:
                        valid_passport_number = validate_passport_number(
                            value=passport_number
                        )
                        if valid_passport_number:
                            logger.info("Passport Number is valid.")
                    except Exception as e:
                        raise PluginException(
                            message=str(e),
                            detailed_message="The Passport Number format is invalid.",
                        )
                # Check if the PIN Code is valid or not.
                pincode = payload.pin_code
                if pincode:
                    try:
                        valid_pincode = validate_pincode(value=payload.pin_code)
                        if valid_pincode:
                            logger.info("PIN Code is valid.")
                    except Exception as e:
                        raise PluginException(
                            message=str(e),
                            detailed_message="The PIN Code format is invalid.",
                        )
                expiry_validation = check_expiry_validation(payload=payload)
                if expiry_validation:
                    logger.warning("Passport has expired.")
                    return expiry_validation

                logger.info("Passport is verified successfully.")
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                    message="",  # verified_successfully
                    actor="system",
                    response=payload.model_dump(),
                )
            else:
                logger.error("Passport front and back images are missing.")
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                    message=get_error_message(
                        error_message_code="LYIK_ERR_MISSING_IMAGES_PASSPORT"
                    ),
                    actor="system",
                    response=payload.model_dump(),
                )

        except PluginException as pe:
            logger.error(pe.detailed_message)
            return VerifyHandlerResponseModel(
                id=None,
                status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                message=pe.message,
                actor="system",
            )

        except Exception as e:
            logger.error(f"Failed verification process. {e}")
            return VerifyHandlerResponseModel(
                id=None,
                status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                message=get_error_message(error_message_code="LYIK_ERR_SAVE_FAILURE"),
                actor="system",
            )


def map_fields_to_payload(response: OVDPassport, payload: RootPassportPassportDetails):
    # Mappings of fields from the response to the payload
    payload.first_name = response.name or ""
    payload.surname = response.surname or ""
    payload.date_of_birth = response.date_of_birth or ""
    payload.passport_number = response.uid or ""
    payload.date_of_issue = response.date_of_issue or ""
    payload.date_of_expiry = response.date_of_expiry or ""
    payload.gender = response.gender or ""
    payload.place_of_issue = response.place_of_issue or ""
    payload.place_of_birth = response.place_of_birth or ""
    payload.nationality = response.nationality or ""
    payload.issued_by = response.place_of_issue or ""
    payload.father_name = response.name_of_father or ""
    payload.mother_name = response.name_of_mother or ""
    payload.spouse_name = response.name_of_spouse or ""
    if response.full_address:
        lines = _split_string(response.full_address, 50)
        if len(lines) > 0:
            payload.address_line_1 = lines[0]
        if len(lines) > 1:
            payload.address_line_2 = lines[1]
    payload.city = response.city or ""
    payload.state = response.state or ""
    payload.country = response.country or ""
    payload.pin_code = response.postal_code or ""


def _split_string(text: str, max_length):
    """Splits a string at word boundaries, respecting a maximum line length.

    Args:
        text: The string to split.
        max_length: The maximum length of each resulting string.

    Returns:
        A list of strings, each no longer than max_length.
    """
    return textwrap.wrap(text, width=max_length)


def check_expiry_validation(
    payload: RootPassportPassportDetails,
) -> VerifyHandlerResponseModel:
    """
    After validating the date of expiry it will return the Verifier Response
    """
    if payload.date_of_expiry is None:
        logger.error("Date of expiry is not provided.")
        return VerifyHandlerResponseModel(
            status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
            message=get_error_message(
                error_message_code="LYIK_ERR_MISSING_DOE_PASSPORT"
            ),
            actor="system",
        )
    doe = payload.date_of_expiry
    desired_validity = payload.desired_validity
    logger.info(f"doe is: {doe} or type {type(doe)}")
    logger.info(f"date.today() is: {date.today()} or type {type(date.today())}")
    if doe < date.today():
        logger.error("The passport has already expired.")
        return VerifyHandlerResponseModel(
            status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
            message=get_error_message(error_message_code="LYIK_ERR_EXIPRED_PASSPORT"),
            actor="system",
        )

    if desired_validity is None:
        desired_validity = "6"

    validity_duration = datetime.today().date() + relativedelta(
        months=int(desired_validity)
    )

    if doe < validity_duration:
        logger.error("Failed to verify the Passport. Please contact admin.")
        return VerifyHandlerResponseModel(
            status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
            message=get_error_message(
                error_message_code="LYIK_ERR_SOMETHING_WENT_WRONG"
            ),
            actor="system",
        )


async def add_ovd_images_to_doc_store(
    context: ContextModel,
    image_1: Union[DBDocumentModel, DocumentModel, str, None],
    image_2: Union[DBDocumentModel, DocumentModel, str, None],
) -> Tuple[Union[DBDocumentModel, None], Union[DBDocumentModel, None]]:
    """
    Asynchronously saves given (front and back) images to the database.

    Args:
        context (ContextModel): Contains configuration and metadata for the operation.
        image_1 : File details for the image (either DocumentModel object, file path or None).
        image_2 : File details for the image (either DocumentModel object, file path or None).

    Returns:
        Tuple[DBDocumentMode | None, DBDocumentModel | None]: A tuple containing database models for the added images.
        Either of them element may be None if no back image is provided.

    Raises:
        ValueError: If the document processing fails during extraction or addition.
    """

    # Initialize responses for front and back images
    front_response = image_1
    back_response = image_2

    # Process the front image if provided
    if isinstance(image_1, str) or isinstance(image_1, DocumentModel):
        # Extract file details using the helper function
        document_model: DocumentModel = extract_file_details(decoded_image=image_1)

        # Add the front document to the database asynchronously
        front_response: DBDocumentModel = await invoke.addDocument(
            config=context.config,
            org_id=context.org_id,
            document=document_model,
            coll_name=context.form_id,
            metadata=DocMeta(
                org_id=context.org_id,
                form_id=context.form_id,
                record_id=None,
                doc_type=document_model.doc_type,
            ),
        )

    # Process the back image if provided
    if isinstance(image_2, str) or isinstance(image_2, DocumentModel):
        # Extract file details using the helper function
        document_model: DocumentModel = extract_file_details(decoded_image=image_2)

        # Add the back document to the database asynchronously
        back_response: DBDocumentModel = await invoke.addDocument(
            config=context.config,
            org_id=context.org_id,
            document=document_model,
            coll_name=context.form_id,
            metadata=DocMeta(
                org_id=context.org_id,
                form_id=context.form_id,
                record_id=None,
                doc_type=document_model.doc_type,
            ),
        )

    # Return the responses for both front and back images
    return front_response, back_response


def extract_file_details(
    decoded_image: Union[DocumentModel, str, None],
) -> DocumentModel:
    """
    Extract file details such as name, type (MIME type), size, and content.

    Args:
        decoded_image (FileResponse | str | None): Can be a file path (str),
        a FileResponse object with Base64-encoded content, or None.

    Returns:
        DBDocumentModel: A model containing extracted file details such as name,
        type, size, and content.

    Raises:
        FileNotFoundError: If the file path does not exist.
        ValueError: If invalid Base64 content is provided.
    """
    try:
        # Initialize variables to hold file details
        doc_name, doc_type, doc_size, doc_content = None, None, None, None

        # Handle case where the input is a file path (string)
        if isinstance(decoded_image, str):
            file_path = decoded_image
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File '{file_path}' not found.")
            doc_name = os.path.basename(file_path)
            doc_size = os.path.getsize(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            with open(file_path, "rb") as file:
                doc_content = file.read()

        # Handle case where the input is a FileResponse object
        elif isinstance(decoded_image, DocumentModel):
            doc_content = decoded_image.doc_content
            doc_name = decoded_image.doc_name
            doc_size = decoded_image.doc_size  # Calculate size in bytes
            mime_type = decoded_image.doc_type

        # Assign extracted MIME type
        doc_type = mime_type or "unknown"
        # doc_name = (
        #     construct_file_name(prefix="front", mime_type=doc_type)
        #     if front_image
        #     else construct_file_name(prefix="back", mime_type=doc_type)
        # )
        # Construct and return the document model with the extracted details
        return DocumentModel(
            doc_name=doc_name,
            doc_type=doc_type,
            doc_size=doc_size,
            doc_content=doc_content,
        )

    except base64.binascii.Error:
        raise ValueError("Invalid Base64-encoded content provided.")


def check_if_verified(payload: dict) -> VerifyHandlerResponseModel | None:
    """
    NOTE: Optional method to handle the flow is payload if already verified. (Re-verification)
    Example method to handle re-verification.
    Check if ver_Status already exists. If it does, check if values have changed.
    If it has, return failure status as values are inconsistent.
    """

    if payload.get("_ver_status"):
        ver_Status = VerifyHandlerResponseModel.model_validate(
            payload.get("_ver_status")
        )
        if ver_Status.status == VERIFY_RESPONSE_STATUS.SUCCESS:
            current_id = ver_Status.id
            generated_id = generate_hash_id_from_dict(payload)
            if str(current_id) == str(generated_id):
                return ver_Status
            else:
                ver_Status.status = VERIFY_RESPONSE_STATUS.DATA_ONLY
                ver_Status.message = get_error_message(
                    error_message_code="LYIK_WARN_VALUES_MODIFIED"
                )
                return ver_Status

    return None


async def get_ocr_data(
    context: ContextModel, payload: RootPassportPassportDetails
) -> OVDPassport:
    temp_file_paths = set()
    if isinstance(payload.ovd_front, str):
        ovd_front_to_send = payload.ovd_front
    elif isinstance(payload.ovd_front, Dict):
        parsed_front_doc = DBDocumentModel.model_validate(payload.ovd_front)
        front_doc = parsed_front_doc.model_copy()
        # Fetching the Document from DB to get the content
        doc_content = await get_document_from_db(context=context, doc=front_doc)
        front_doc.doc_content = doc_content
        # Creating a temp file as file path is needed for ocr
        temp_file_path = await create_temp_file(doc=front_doc)
        ovd_front_to_send = temp_file_path
        temp_file_paths.add(temp_file_path)
    else:
        ovd_front_to_send = None
    if isinstance(payload.ovd_back, str):
        ovd_back_to_send = payload.ovd_back
    elif isinstance(payload.ovd_back, Dict):
        parsed_back_doc = DBDocumentModel.model_validate(payload.ovd_back)
        back_doc = parsed_back_doc.model_copy()
        # Fetching the Document from DB to get the content
        doc_content = await get_document_from_db(context=context, doc=back_doc)
        back_doc.doc_content = doc_content
        # Creating a temp file as file path is needed for ocr
        temp_file_path = await create_temp_file(doc=back_doc)
        ovd_back_to_send = temp_file_path
        temp_file_paths.add(temp_file_path)
    else:
        ovd_back_to_send = None
    try:
        if ovd_front_to_send or ovd_back_to_send:
            ovd_response = await invoke.fetch_ovd_details(
                config=context.config,
                ovd_front=ovd_front_to_send,
                ovd_back=ovd_back_to_send,
            )
            return ovd_response
    except Exception as e:
        logger.exception(e)
        return VerifyHandlerResponseModel(
            status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
            message=get_error_message(error_message_code="LYIK_ERR_INVALID_OCR_FILES"),
            actor="system",
        )


async def get_document_from_db(context: ContextModel, doc: DBDocumentModel):
    documents: List[DBDocumentModel] = await invoke.fetchDocument(
        config=context.config,
        org_id=context.org_id,
        file_id=doc.doc_id,
        coll_name=context.form_id,
        metadata_params=None,
    )
    doc: DBDocumentModel = documents[0]
    return doc.doc_content


async def create_temp_file(doc: DBDocumentModel) -> str:
    """
    Creates a named temporary file from the uploaded file content and returns its path.
    Includes the appropriate file extension in the temp file name.
    """
    # Extract the file extension from the filename
    _, file_extension = os.path.splitext(doc.doc_name)
    if not file_extension:
        file_extension = ""  # Default to no extension if none is found

    # Create the temporary file with the correct suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        content = doc.doc_content
        temp_file.write(content)
        temp_file_path = temp_file.name
        return temp_file_path
