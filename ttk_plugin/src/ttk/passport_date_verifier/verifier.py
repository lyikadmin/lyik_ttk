import apluggy as pluggy
import os
from pydantic import BaseModel, ConfigDict, Field, field_validator
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
    SingleFieldModel,
)
from typing import Annotated
from typing_extensions import Doc
from lyikpluginmanager.core.utils import generate_hash_id_from_dict
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

class PassportPayload(BaseModel):
    expiry_date: str | None = Field(description="Passport expiry date")
    desired_validity: int | None = Field(description="dynamic validation duration")
    model_config = ConfigDict(extra="allow")

    @field_validator('desired_validity')
    def validate_month(cls, v):
        if not (1 <= v <= 24):
            raise ValueError('desired_validity must be between 1 and 24')
        return v
    

class PassportDateVerificationPlugin(VerifyHandlerSpec):
    """
    Passport date verification plugin, with the dynamic duration validity.
    """

    @impl
    async def verify_handler(
        self,
        context: ContextModel | None,
        payload: Annotated[
            PassportPayload,
            Doc("Payload for passport date validity processing."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response after validating the passport date."),
    ]:

        payload_dict = payload.model_dump()

        ret = check_if_verified(payload=payload_dict)
        if ret:
            return ret

        try:
            expiry_str = payload_dict.get("expiry_date")
            desired_validity = payload_dict.get("desired_validity")

            if not expiry_str:
                raise ValueError("passport_expiry_date not found in payload.")
            
            if not desired_validity:
                raise ValueError("desired validity not found in the payload.")

            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            today = datetime.today().date()

            validity_duration = today + relativedelta(months=desired_validity)

            # Validation Logic
            if expiry_date > validity_duration:
                status = VERIFY_RESPONSE_STATUS.SUCCESS
                message = "Passport date verified successfully."
                hash_id = generate_hash_id_from_dict(payload_dict)
            else:
                status = VERIFY_RESPONSE_STATUS.FAILURE
                message = "Passport date verification failed."
                hash_id = None

            return VerifyHandlerResponseModel(
                id=hash_id,
                status=status,
                message=message,
                actor="system",
                response=payload_dict,
            )

        except Exception as e:
            message = f"Failed verification process. {e}"
            status = VERIFY_RESPONSE_STATUS.FAILURE
            logger.error(message)
            return VerifyHandlerResponseModel(
                id=None, status=status, message=message, actor="system"
            )



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
                ver_Status.status = VERIFY_RESPONSE_STATUS.FAILURE
                ver_Status.message = "Values have changed. Please Re-verify"
                return ver_Status

    return None
