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
from typing import Annotated, Optional
from typing_extensions import Doc
import logging
from datetime import datetime
from lyik.ttk.utils.verifier_util import check_if_verified, validate_phone, validate_email
from lyik.ttk.utils.message import get_error_message
from lyik.ttk.utils.utils import format_date_to_string
from datetime import date
from lyik.ttk.models.generated.universal_model_with_appointment import RootAppointment, ADDONSERVICEAPPOINTMENT
from lyik.ttk.models.generated.universal_model import UniversalModel
# from lyik.ttk.models.forms.schengentouristvisa import (
#     Schengentouristvisa,
#     RootAppointment,
#     ADDONSERVICEAPPOINTMENT,
# )

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

ACTOR = "system"


class AppointmentDetailsVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootAppointment,
            Doc("Appointment Details payload."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        RequiredVars(["DEFAULT_COUNTRY_CODE"]),
        Doc("Response after validating Appointment Details."),
    ]:
        """
        This verifier validates if the appointment details, specifically the date is valid.
        """
        payload_dict = payload.model_dump(mode="json")
        ret = check_if_verified(payload=payload_dict)
        if ret:
            return ret

        if payload.add_on_service_option == ADDONSERVICEAPPOINTMENT.YES:
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=f"Verified by the {ACTOR}",
                status=VERIFY_RESPONSE_STATUS.SUCCESS,
            )

        if not context or not context.config:
            raise PluginException(
                message=get_error_message(
                    error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                ),
                detailed_message="The context is missing or config is missing in context.",
            )

        appointment_date = (
            payload
            and payload.appointment_scheduled
            and payload.appointment_scheduled.scheduled_date
        )

        full_form_record = UniversalModel.model_validate(context.record)

        departure_date = (
            full_form_record.visa_request_information
            and full_form_record.visa_request_information.visa_request
            and full_form_record.visa_request_information.visa_request.departure_date
        )

        if not appointment_date:
            error = get_error_message(
                error_message_code="LYIK_ERR_MISSING_SCH_DATE_APT"
            )
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=error,
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )

        if not departure_date:
            error = get_error_message(error_message_code="LYIK_ERR_MISSING_DD_VRS_APT")
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=error,
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )

        if (
            isinstance(appointment_date, date)
            and isinstance(departure_date, date)
            and appointment_date >= departure_date
        ):
            error = get_error_message(
                error_message_code="LYIK_ERR_INVALID_APT_DATE",
                parameters=[
                    format_date_to_string(appointment_date),
                    format_date_to_string(departure_date),
                ],
            )
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=error,
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )
        return VerifyHandlerResponseModel(
            actor=ACTOR,
            message=f"Verified by {ACTOR}",
            status=VERIFY_RESPONSE_STATUS.SUCCESS,
        )
