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
from lyik.ttk.models.forms.schengentouristvisa import RootSubmitInfo, DOCKETSTATUS
import logging
from lyik.ttk.utils.verifier_util import check_if_verified, validate_pincode
from lyik.ttk.utils.message import get_error_message

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

ACTOR = "system"


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
        This verifier verifies the Address details.
        """
        try:
            if payload.docket.docket_status == DOCKETSTATUS.ENABLE_DOWNLOAD:
                cfm = payload.confirm
                if not (
                    cfm.viewed_data
                    and cfm.appointment_booked
                    and cfm.addons_addressed
                    and cfm.docs_uploaded
                    and cfm.understand_lock
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
