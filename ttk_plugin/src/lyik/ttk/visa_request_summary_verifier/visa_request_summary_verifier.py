import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    PluginException,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
)
from lyikpluginmanager.annotation import RequiredVars
from typing import Annotated
from typing_extensions import Doc
from ..models.forms.new_schengentouristvisa import RootVisaRequestInformation
import logging
from datetime import datetime
from ..utils.verifier_util import check_if_verified, validate_phone, validate_email
from ..utils.message import get_error_message

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

ACTOR = "system"


class VisaRequestVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootVisaRequestInformation,
            Doc("Visa Request Summary payload."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        RequiredVars(["DEFAULT_COUNTRY_CODE"]),
        Doc("Response after validating the Visa Request Summary."),
    ]:
        """
        This verifier validates the data of the Visa Request Summary section.
        """
        if not context or not context.config:
            raise PluginException(
                message=get_error_message(error_message_code="TTK_ERR_0005"),
                detailed_message="The context is missing or config is missing in context.",
            )

        default_country_code = context.config.DEFAULT_COUNTRY_CODE

        if not default_country_code:
            raise PluginException(
                message=get_error_message(error_message_code="TTK_ERR_0005"),
                detailed_message="The DEFAULT_COUNTRY_CODE is missing in config.",
            )

        payload_dict = payload.model_dump(mode="json")

        ret = check_if_verified(payload=payload_dict)
        if ret:
            return ret

        try:
            visa_request = payload.visa_request

            if visa_request:
                phone_number = visa_request.phone_number
                email_id = visa_request.email_id

                if phone_number:
                    try:
                        valid_number = validate_phone(
                            value=phone_number, country_code=default_country_code
                        )
                        if valid_number:
                            payload.visa_request.phone_number = valid_number
                            logger.info("Visa phone number is valid.")
                    except Exception as e:
                        return VerifyHandlerResponseModel(
                            actor=ACTOR,
                            message=str(e),
                            status=VERIFY_RESPONSE_STATUS.FAILURE,
                        )

                if email_id:
                    try:
                        valid_email = validate_email(value=email_id)
                        if valid_email:
                            logger.info("Visa Email ID is valid.")
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
                response=payload.model_dump(),
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
                message=get_error_message(error_message_code="TTK_ERR_0006"),
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )
