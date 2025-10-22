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
from lyik.ttk.models.forms.schengentouristvisa import RootVisaRequestInformation
import logging
from datetime import date, timedelta
from lyik.ttk.utils.verifier_util import (
    check_if_verified,
    validate_phone,
    validate_email,
)
from lyik.ttk.models.forms.schengentouristvisa import (
    Schengentouristvisa,
)
from lyik.ttk.utils.message import get_error_message

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

ACTOR = "system"
DEFAULT_BUSINESS_DAYS = 10


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
                message=get_error_message(
                    error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                ),
                detailed_message="The context is missing or config is missing in context.",
            )

        full_form_record = Schengentouristvisa.model_validate(context.record)

        try:
            business_days = int(full_form_record.scratch_pad.business_days)
            if not business_days:
                business_days = DEFAULT_BUSINESS_DAYS
        except Exception as e:
            business_days = DEFAULT_BUSINESS_DAYS

        today = date.today()
        earliest_departure_date = business_days_from(
            start=today, business_days=business_days
        )

        if earliest_departure_date > payload.visa_request.departure_date:
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=get_error_message(
                    "LYIK_ERR_EARLY_ARRIVAL_DEPARTURE_DATES",
                    [earliest_departure_date.strftime("%d-%b-%Y")],
                ),
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )

        default_country_code = context.config.DEFAULT_COUNTRY_CODE

        if not default_country_code:
            raise PluginException(
                message=get_error_message(
                    error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                ),
                detailed_message="The DEFAULT_COUNTRY_CODE is missing in config.",
            )
        message = ""

        if not (
            payload.visa_request.departure_date and payload.visa_request.arrival_date
        ):
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=get_error_message("LYIK_ERR_EMPTY_ARRIVAL_DEPARTURE_DATES"),
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )

        if payload.visa_request.departure_date > payload.visa_request.arrival_date:
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=get_error_message("LYIK_ERR_ARRIVAL_BEFORE_DEPARTURE_DATE"),
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )
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
                message=get_error_message(error_message_code="LYIK_ERR_SAVE_FAILURE"),
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )


def business_days_from(start: date, business_days: int) -> date:
    """
    Return the date that is `business_days` business days after `start`
    (Mon–Fri only; weekends skipped). `start` itself is not counted.
    """
    d = start
    added = 0
    while added < business_days:
        d += timedelta(days=1)
        if d.weekday() < 5:  # 0=Mon ... 4=Fri
            added += 1
    return d
