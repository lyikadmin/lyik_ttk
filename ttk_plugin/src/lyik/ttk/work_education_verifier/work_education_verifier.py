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
from lyikpluginmanager.annotation import RequiredVars
from typing_extensions import Doc
from ..models.forms.schengentouristvisa import RootWorkAddress
import logging
from ..utils.verifier_util import check_if_verified, validate_phone
from ..utils.message import get_error_message

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

ACTOR = "system"


class WorkEducationVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootWorkAddress,
            Doc("Work/Education details payload."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        RequiredVars(["DEFAULT_COUNTRY_CODE"]),
        Doc("Response after validating the Work/Education details."),
    ]:
        """
        This verifier verifies the work/education details.
        """

        if not context or not context.config:
            raise PluginException(
                message=get_error_message(
                    error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                ),
                detailed_message="The context is missing or config is missing in context.",
            )

        default_country_code = context.config.DEFAULT_COUNTRY_CODE

        if not default_country_code:
            raise PluginException(
                message=get_error_message(
                    error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                ),
                detailed_message="The DEFAULT_COUNTRY_CODE is missing in config.",
            )

        payload_dict = payload.model_dump(mode="json")

        ret = check_if_verified(payload=payload_dict)
        if ret:
            return ret
        try:
            current_occupation = payload.current_occupation_status

            if current_occupation.value == "STUDENT":
                education_details = payload.education_details

                if education_details:
                    contact_number_of_education = (
                        education_details.establishment_contact
                    )

                    if contact_number_of_education:
                        try:
                            valid_education_number = validate_phone(
                                value=contact_number_of_education,
                                country_code=default_country_code,
                            )
                            if valid_education_number:
                                payload.education_details.establishment_contact = (
                                    valid_education_number
                                )
                                logger.info(
                                    "Education establishment phone number is valid."
                                )
                        except Exception as e:
                            return VerifyHandlerResponseModel(
                                actor=ACTOR,
                                message=str(e),
                                status=VERIFY_RESPONSE_STATUS.FAILURE,
                            )
            else:
                work_details = payload.work_details

                if work_details:
                    contact_number_of_work = work_details.work_phone

                    if contact_number_of_work:
                        try:
                            valid_work_number = validate_phone(
                                value=contact_number_of_work,
                                country_code=default_country_code,
                            )
                            if valid_work_number:
                                payload.work_details.work_phone = valid_work_number
                                logger.info("Work phone number is valid.")
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
                message=get_error_message(error_message_code="LYIK_ERR_SAVE_FAILURE"),
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )
