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
from ..models.forms.schengentouristvisa import (
    RootPreviousVisas,
    PURPOSEOFVISAORTRAVEL,
    OPTION,
)
from ..utils.message import get_error_message
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
        try:
            if payload is None:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="The payload is missing. Ensure the payload is properly available.",
                )

            collected_fingerprint_flag = (
                payload.fingerprint_collected == OPTION.YES.value
            )
            have_past_visa_flag = payload.have_past_visa == OPTION.YES.value

            if not have_past_visa_flag:
                return VerifyHandlerResponseModel(
                    status=VERIFY_RESPONSE_STATUS.SUCCESS,
                    actor="system",
                    message="Verified successfully by the system.",
                )
            else:

                # Check all required fields are filled
                missing_fields = []
                for (
                    field_name,
                    value,
                ) in payload.previous_visas_details.model_dump().items():
                    if (not value) and (field_name == "others_specify"):
                        if (
                            payload.previous_visas_details.purpose_of_visa
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
                        message=get_error_message(
                            error_message_code="LYIK_ERR_MISSING_FIELDS_PREV_VISA"
                        ),
                    )

                # Check end date of visa is in the past
                end_date = payload.previous_visas_details.end_date
                if end_date is None or end_date >= date.today():
                    return VerifyHandlerResponseModel(
                        status=VERIFY_RESPONSE_STATUS.FAILURE,
                        actor="system",
                        message=get_error_message(
                            error_message_code="LYIK_ERR_INVALID_VISA_ED_PREV_VISA"
                        ),
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
                message=get_error_message(error_message_code="LYIK_ERR_SAVE_FAILURE"),
            )
