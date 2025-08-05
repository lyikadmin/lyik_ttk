from lyikpluginmanager import VerifyHandlerResponseModel, VERIFY_RESPONSE_STATUS
from .message import get_error_message
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from pydantic import EmailStr, TypeAdapter
import re

email_adapter = TypeAdapter(EmailStr)


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
            return ver_Status

    return None


def validate_phone(value: str, country_code: int) -> str:
    try:
        phone = phonenumbers.parse(
            number=value,
            region=phonenumbers.region_code_for_country_code(country_code),
        )
    except NumberParseException as e:
        raise ValueError(
            get_error_message(error_message_code="LYIK_ERR_0007", parameters=[value])
        ) from e
    if not phonenumbers.is_valid_number(phone):
        raise ValueError(
            get_error_message(error_message_code="LYIK_ERR_0007", parameters=[value])
        )

    return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)


def validate_email(value: str) -> str:
    """
    Validates that the given string is a valid email address using Pydantic's EmailStr.

    Args:
        value (str): The email address to validate.

    Returns:
        str: The validated email address (unchanged) if valid.

    Raises:
        ValueError: If the email is invalid.
    """
    try:
        email = email_adapter.validate_python(value)
        return str(email)  # Ensures plain string return
    except Exception as e:
        raise ValueError(
            get_error_message(error_message_code="LYIK_ERR_0006", parameters=[value])
        ) from e


def validate_pincode(value: str) -> str:
    """
    Validates that the given string is a 6-digit numeric pincode.

    Args:
        value (str): The pincode to validate.

    Returns:
        str: The validated pincode (unchanged) if valid.

    Raises:
        ValueError: If the pincode is not a 6-digit number.
    """
    if len(value) == 6 and value.isdigit():
        return value
    raise ValueError(
        get_error_message(error_message_code="LYIK_ERR_0004", parameters=[value])
    )


def validate_aadhaar_number(value: str) -> str:
    """
    Validates that the given string is a 12-digit Aadhaar number.

    Args:
        value (str): The Aadhaar number to validate.

    Returns:
        str: The validated Aadhaar number (unchanged) if valid.

    Raises:
        ValueError: If the input is not a 12-digit number.
    """
    if len(value) == 12 and value.isdigit():
        return value
    raise ValueError(
        get_error_message(error_message_code="LYIK_ERR_0005", parameters=[value])
    )


def validate_passport_number(value: str) -> str:
    """
    Validates that the given string is a valid Indian passport number using regex.

    Format: 1 uppercase letter followed by 7 digits (e.g., A1234567)

    Args:
        value (str): The passport number to validate.

    Returns:
        str: The validated passport number if valid.

    Raises:
        ValueError: If the passport number format is invalid.
    """
    if re.fullmatch(r"^[A-Z][0-9]{7}$", value):
        return value
    raise ValueError(
        get_error_message(error_message_code="LYIK_ERR_0001", parameters=[value])
    )
