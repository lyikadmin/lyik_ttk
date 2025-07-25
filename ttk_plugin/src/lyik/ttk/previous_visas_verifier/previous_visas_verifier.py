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
from ..models.forms.new_schengentouristvisa import (
    RootPreviousVisas,
    PURPOSEOFVISAORTRAVEL,
)
import logging
from datetime import date

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())


class PreviousVisasVerifier(VerifyHandlerSpec):
    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[RootPreviousVisas, Doc("Payload for Previous Visas")],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response after validating Previous Visas details."),
    ]:
        """
        This plugin verifies if the user has selected that they had been issued a schengen visa in the past,
        all the details are mandatory to fill in the form.
        Args:
            payload (RootPreviousVisas): The payload for the Previous Visas.
        Returns:
            VerifyHandlerResponseModel: VerifyHandlerResponseModel with the verification status.
        """

        logger.info("Started Previous visas verification process.")
        try:
            if payload is None:
                raise PluginException(
                    message="Internal configuration error. Please contact support.",
                    detailed_message="The payload is missing. Ensure the payload is properly available.",
                )

            previous_visas_details = payload.previous_visas_details

            if not previous_visas_details:
                raise PluginException(
                    message="Internal configuration error. Please contact support.",
                    detailed_message="The payload is missing Previous Visas Details.",
                )

            if previous_visas_details.have_past_visa.value == "NO":
                logger.info(
                    "User has not been issued previous Schengen visa. Verified successfully."
                )
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.SUCCESS,
                    actor="system",
                    message="Verified successfully by the system.",
                )
            else:
                # Check all required fields are filled
                missing_fields = []
                for field_name, value in previous_visas_details.model_dump().items():
                    if (not value) and (field_name == "others_specify"):
                        if (
                            previous_visas_details.purpose_of_visa
                            == PURPOSEOFVISAORTRAVEL.OTHER
                        ):
                            missing_fields.append(field_name)

                    elif (not value) and (field_name != "others_specify"):
                        missing_fields.append(field_name)

                if missing_fields:
                    logger.error(
                        f"Missing or invalid fields in previous visa details: {missing_fields}"
                    )
                    return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.FAILURE,
                        actor="system",
                        message="Please ensure all the details are filled if you have been issued a Schengen visa in the past.",
                    )

                # Check end date of visa is in the past
                end_date = previous_visas_details.end_date
                if end_date is None or end_date >= date.today():
                    logger.error("The end date of visa is not a past date.")
                    return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.FAILURE,
                        actor="system",
                        message="End Date of Visa must be a past. Try again or contact support.",
                    )

                logger.info(
                    "User has previous visa and all fields are valid. Verified successfully."
                )
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
            logger.error(f"Something went wrong in Previous visas verification: {e}")
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                actor="system",
                message="Something went wrong while verification. Please contact support.",
            )
