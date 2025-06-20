import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
    PluginException,
)
from typing import Annotated
from typing_extensions import Doc
from ..models.forms.new_schengentouristvisa import RootAdditionalDetails
import logging
from datetime import date
import re

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())


class AdditionalTravelDetailsVerifier(VerifyHandlerSpec):
    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootAdditionalDetails, Doc("Payload for Additional Travel Details.")
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response after validating Previous Visas details."),
    ]:
        """
        This plugin verifies the additional travel details of the user.
        Args:
            payload (RootAdditionalDetails): This is the additional travel details payload.
        Returns:
            VerifyHandlerResponseModel: VerifyHandlerResponseModel with the verification status.

        """

        logger.info("Started Additional travel details verification process.")
        try:
            if payload is None:
                raise PluginException(
                    message="Internal configuration error. Please contact support.",
                    detailed_message="The payload is missing. Ensure the payload is properly available.",
                )

            application_details = payload.app_details
            family_eu = payload.family_eu

            if application_details:
                if application_details.application_on_behalf.value == "NO":
                    logger.info(
                        "User is not submitting the Schengen visa on behalf of the other person. Verified successfully."
                    )
                    return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.SUCCESS,
                        actor="system",
                        message="Verified successfully by the system.",
                    )
                else:
                    # Check all required fields are filled
                    missing_fields = []
                    for field_name, value in application_details.model_dump().items():
                        if not value:
                            missing_fields.append(field_name)

                    if missing_fields:
                        logger.error(
                            f"Missing or invalid fields in application details: {missing_fields}"
                        )
                        return VerifyHandlerResponseModel(
                            status=VERIFY_RESPONSE_STATUS.FAILURE,
                            actor="system",
                            message="Please ensure all the details are filled if you are submitting the visa on behalf of the other person.",
                        )

                    # Check if the entered email is valid or not.
                    is_valid_mail = self.is_valid_email(
                        email=application_details.email_address
                    )

                    if not is_valid_mail:
                        raise PluginException(
                            message="Please enter a valid email addres and try again.",
                            detailed_message="The user has entered an invalid email address.",
                        )

            if family_eu:
                if family_eu.is_family_member.value == "NO":
                    logger.info(
                        "User does not have a Family Member of EU, EEA, Swiss, or UK National. Verified successfully."
                    )
                    return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.SUCCESS,
                        actor="system",
                        message="Verified successfully by the system.",
                    )
                else:
                    # Check all required fields are filled
                    missing_fields = []
                    for field_name, value in family_eu.model_dump().items():
                        if not value:
                            missing_fields.append(field_name)

                    if missing_fields:
                        logger.error(
                            f"Missing or invalid fields in Family Member of EU, EEA, Swiss, or UK National: {missing_fields}"
                        )
                        return VerifyHandlerResponseModel(
                            status=VERIFY_RESPONSE_STATUS.FAILURE,
                            actor="system",
                            message="Please ensure all the details are filled if you have Family Member of EU, EEA, Swiss, or UK National.",
                        )

            logger.info("Additional Travel Details verified successfully.")
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.SUCCESS,
                actor="system",
                message="Verified successfully by the system.",
            )

        except PluginException as pe:
            logger.error(pe.detailed_message)
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                actor="system",
                message=pe.message,
            )
        except Exception as e:
            logger.error(
                f"Something went wrong in Additional Travel Details verification: {e}"
            )
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                actor="system",
                message="Something went wrong while verification. Please contact support.",
            )

    def is_valid_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(pattern, email) is not None
