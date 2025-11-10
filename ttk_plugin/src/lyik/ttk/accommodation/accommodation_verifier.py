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
from lyik.ttk.models.forms.schengentouristvisa import RootAccomodation
from lyik.ttk.utils.message import get_error_message
import logging
from datetime import datetime
from lyik.ttk.utils.verifier_util import check_if_verified, validate_email

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

ACTOR = "system"


class AccommodationVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootAccomodation,
            Doc("Accommodation details payload."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response after validating the Accommodation details."),
    ]:
        """
        This verifier verifies the accommodation details.
        Validates the email mainly
        """
        payload_dict = payload.model_dump(mode="json")

        ret = check_if_verified(payload=payload_dict)
        if ret:
            return ret

        try:
            accommodation_choice = payload.accommodation_choice

            if accommodation_choice.accommodation_option.value == "BOOKED":
                booked_accommodation = payload.booked_appointment

                if booked_accommodation:
                    email_of_accommodation = booked_accommodation.accommodation_email

                    if email_of_accommodation:
                        try:
                            valid_accomodation_email = validate_email(
                                value=email_of_accommodation
                            )
                            if valid_accomodation_email:
                                logger.info("Accommodation Email is valid.")
                        except Exception as e:
                            return VerifyHandlerResponseModel(
                                actor=ACTOR,
                                message=str(e),
                                status=VERIFY_RESPONSE_STATUS.FAILURE,
                            )
            else:
                invitation_details = payload.invitation_details

                if invitation_details:
                    inviter_email = invitation_details.email_id

                    if inviter_email:
                        try:
                            valid_inviter_email = validate_email(value=inviter_email)
                            if valid_inviter_email:
                                logger.info("Inviter Email is valid.")
                        except Exception as e:
                            return VerifyHandlerResponseModel(
                                actor=ACTOR,
                                message=str(e),
                                status=VERIFY_RESPONSE_STATUS.FAILURE,
                            )

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
