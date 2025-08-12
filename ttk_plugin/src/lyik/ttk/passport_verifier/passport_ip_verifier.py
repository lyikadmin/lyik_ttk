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
from lyik.ttk.models.forms.schengentouristvisa import (
    Schengentouristvisa,
    RootPassport,
    CIVILMARITALSTATUS,
)
from lyik.ttk.utils.verifier_util import (
    check_if_verified,
)
from datetime import date
from dateutil.relativedelta import relativedelta
import logging
from lyik.ttk.utils.message import get_error_message
from lyik.ttk.utils.utils import format_date_to_string

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

ACTOR = "system"


class PassportIPVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootPassport,
            Doc("Passport IP payload."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response after validating the Passport IP."),
    ]:
        """
        This verifier validates if the appointment details, specifically the date is valid.
        """
        payload_dict = payload.model_dump(mode="json")
        ret = check_if_verified(payload=payload_dict)
        if ret:
            return ret

        full_form_record = Schengentouristvisa.model_validate(context.record)

        india_return_date = None
        if (
            full_form_record
            and full_form_record.visa_request_information
            and full_form_record.visa_request_information.visa_request
            and full_form_record.visa_request_information.visa_request.arrival_date
        ):
            india_return_date = (
                full_form_record.visa_request_information.visa_request.arrival_date
            )

        if not india_return_date:
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=get_error_message(
                    error_message_code="LYIK_ERR_PASSPORT_ENTER_DATE_OF_RETURN"
                ),
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )

        passport_expiry_date = None
        if payload.passport_details:
            passport_expiry_date = payload.passport_details.date_of_expiry

        if not passport_expiry_date:
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=get_error_message(
                    error_message_code="Please Enter the passport expiry date"
                ),
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )

        # Passports cannot expire in the 6 months from the date of return to india
        expiry_valid_from_date = india_return_date + relativedelta(months=6)

        if passport_expiry_date < expiry_valid_from_date:
            expiry_valid_from_date = format_date_to_string(india_return_date)

            expiry_error_message = get_error_message(
                error_message_code="LYIK_ERR_PASSPORT_6_MONTH_EXPIRED",
                parameters=[expiry_valid_from_date],
            )
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=expiry_error_message,
                error_paths={
                    "passport.passport_details.date_of_expiry": expiry_error_message
                },
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )

        marital_status = payload.other_details.civil_status
        if marital_status == CIVILMARITALSTATUS.OTHER:
            if not payload.other_details.other_civil_status:
                return VerifyHandlerResponseModel(
                    actor=ACTOR,
                    message=get_error_message(
                        error_message_code="LYIK_ERR_OTHER_CIVIL_STATUS"
                    ),
                    status=VERIFY_RESPONSE_STATUS.FAILURE,
                )

        return VerifyHandlerResponseModel(
            actor=ACTOR,
            message="Verified Successfully",
            status=VERIFY_RESPONSE_STATUS.SUCCESS,
        )
    