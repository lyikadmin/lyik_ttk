import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    PluginException,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
)
from typing import Annotated, List
from typing_extensions import Doc

from lyik.ttk.models.generated.universal_model_with_submission_requires_docket_status import (
    RootSubmitInfo,
    DOCKETSTATUS,
)
import logging
from lyik.ttk.utils.verifier_util import check_if_verified, validate_pincode
from lyik.ttk.utils.message import get_error_message
from lyik.ttk.utils import get_form_indicator, FormConfig

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

ACTOR = "system"


def _get_nested_value(data: dict, path: str):
    """
    Safely get a nested value from a dict given a dotted path like
    'confirm.viewed_data'. Returns None if any key is missing.
    """
    current = data
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def _all_requirements_satisfied(requirements: List[str], payload_dict: dict) -> bool:
    """
    Returns True only if all requirements specified by dotted paths
    are present and truthy in payload_dict.
    """
    for req in requirements:
        value = _get_nested_value(payload_dict, req)
        if not value:
            logger.info(
                "Submission requirement not satisfied: %s (value: %r)", req, value
            )
            return False
    return True


class SumbitApplicationVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootSubmitInfo,
            Doc("Address payload."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response after validating the Application Submission."),
    ]:
        """
        This verifier verifies the Application Submission.
        Checks that the confirmation checkboxes are ticked before submitting.
        """
        frm_config = FormConfig(form_indicator=get_form_indicator(context.record))
        submit_requirement: List[str] | None = (
            frm_config.get_submit_requirement_list()
        )
        try:
            # Currently can save for any status selected.
            # if payload.docket.docket_status not in {
            #     DOCKETSTATUS.ADDITIONAL_REVIEW,
            #     DOCKETSTATUS.ENABLE_DOWNLOAD,
            # }:
            #     return VerifyHandlerResponseModel(
            #         actor=ACTOR,
            #         message=get_error_message(
            #             error_message_code="LYIK_ERR_UNDER_REVIEW_SUBMISSION"
            #         ),
            #         status=VERIFY_RESPONSE_STATUS.FAILURE,
            #     )

            # Only enforce dynamic requirements when ENABLE_DOWNLOAD and we have a list
            if (
                payload.docket.docket_status.value == DOCKETSTATUS.ENABLE_DOWNLOAD.value
                and submit_requirement
            ):
                """
                submit_requirement will be a list which may be empty,
                or will have a list such as
                [
                    "confirm.viewed_data",
                    "confirm.appointment_booked",
                    "confirm.addons_addressed",
                    "confirm.docs_uploaded",
                    "confirm.understand_lock",
                ]

                These paths are evaluated against payload_dict and
                all must be truthy for a successful submission.
                """
                payload_dict = payload.model_dump()

                if not _all_requirements_satisfied(
                    submit_requirement, payload_dict
                ):
                    return VerifyHandlerResponseModel(
                        actor=ACTOR,
                        message=get_error_message(
                            error_message_code="LYIK_ERR_DID_NOT_FULLY_CONFIRM_SUBMISSION"
                        ),
                        status=VERIFY_RESPONSE_STATUS.FAILURE,
                    )

            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=f"Verified by the {ACTOR}",
                status=VERIFY_RESPONSE_STATUS.SUCCESS,
            )

        except Exception as e:
            logger.error(f"Unhandled exception occurred. Error: {str(e)}")
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=get_error_message(
                    error_message_code="LYIK_ERR_DID_NOT_FULLY_CONFIRM_SUBMISSION"
                ),
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )
