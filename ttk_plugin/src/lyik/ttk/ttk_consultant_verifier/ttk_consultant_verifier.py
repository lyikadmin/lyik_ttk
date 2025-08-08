import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    PluginException,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
)
from typing import Annotated
from typing_extensions import Doc
from ..models.forms.schengentouristvisa import RootConsultantInfo
import logging
from datetime import datetime
from ..utils.verifier_util import check_if_verified, validate_email
from ..utils.message import get_error_message

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

ACTOR = "system"


class TTKConsultantVerifier(VerifyHandlerSpec):
    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootConsultantInfo,
            Doc("TTK Consultant details payload."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response after validating the TTK Consultant details."),
    ]:
        """
        This verifier verifies the TTK Consultant details.
        """
        payload_dict = payload.model_dump(mode="json")

        # Check if payload is already verified
        ret = check_if_verified(payload=payload_dict)
        if ret:
            return ret

        try:
            dummy_accommodation = payload.dummy_accommodation
            confirmed_accommodation = payload.confirmed_accommodation

            # Verify details if dummy accommodation details are uploaded.
            if dummy_accommodation:
                dummy_email_address = dummy_accommodation.accommodation_email

                if dummy_email_address:
                    try:
                        valid_dummy_accomodation_email = validate_email(
                            value=dummy_email_address
                        )
                        if valid_dummy_accomodation_email:
                            logger.info("Email ID validated successfully.")
                    except Exception as e:
                        logger.error(
                            f"Failed to validate the entered email id in Confirmed Accommodation. Error: {str(e)}"
                        )
                        return VerifyHandlerResponseModel(
                            actor=ACTOR,
                            message=str(e),
                            status=VERIFY_RESPONSE_STATUS.FAILURE,
                        )

            # Verify details if confirmed accommodation details are uploaded.
            if confirmed_accommodation:
                confirmed_email_address = confirmed_accommodation.accommodation_email

                if confirmed_email_address:
                    try:
                        valid_confirmed_accomodation_email = validate_email(
                            value=confirmed_email_address
                        )
                        if valid_confirmed_accomodation_email:
                            logger.info("Email ID validated successfully.")
                    except Exception as e:
                        logger.error(
                            f"Failed to validate the entered email id in Confirmed Accommodation. Error: {str(e)}"
                        )
                        return VerifyHandlerResponseModel(
                            actor=ACTOR,
                            message=str(e),
                            status=VERIFY_RESPONSE_STATUS.FAILURE,
                        )

            logger.info("TTK Consultant data verified successfully.")
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=f"Verified by the {ACTOR}",
                status=VERIFY_RESPONSE_STATUS.SUCCESS,
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
