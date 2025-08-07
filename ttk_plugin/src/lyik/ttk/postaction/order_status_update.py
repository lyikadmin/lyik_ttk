from __future__ import annotations

import logging
from typing import Annotated, Dict, Any, Union

import apluggy as pluggy
from lyikpluginmanager import (
    ContextModel,
    GenericFormRecordModel,
    PostActionProcessorSpec,
    getProjectName,
    PluginException,
)
import jwt
from lyikpluginmanager.annotation import RequiredEnv
from typing_extensions import Doc
import os
import httpx
import json
from datetime import date, datetime, time

from ..models.forms.new_schengentouristvisa import Schengentouristvisa
from ..models.forms.new_schengentouristvisa import DOCKETSTATUS
from pydantic import BaseModel

logger = logging.getLogger(__name__)
impl = pluggy.HookimplMarker(getProjectName())


class TravelerDetailsModel(BaseModel):
    dateOfArrival: str | None = ""
    dateOfDeparture: str | None = ""
    lengthOfStay: int | None = ""
    validityOfVisa: int | None = ""
    visaMode: str | None = ""


class OrderStatusUpdate(PostActionProcessorSpec):
    @impl
    async def post_action_processor(
        self,
        context: ContextModel,
        action: Annotated[str, "Save / Submit"],
        previous_state: Annotated[str | None, "Previous record state"],
        current_state: Annotated[str | None, "New record state"],
        payload: Annotated[GenericFormRecordModel, "Entire form record model"],
    ) -> Annotated[
        GenericFormRecordModel,
        RequiredEnv(["TTK_API_BASE_URL", "TTK_ORDER_UPDATE_ROUTE"]),
        Doc("Form record"),
    ]:
        "This plugin will update the order / progree status in the TTK Appication."
        try:

            if not context or not context.token:
                logger.error(
                    "ContextModel or token is missing in the context. Passing through OrderStatusUpdate Preaction."
                )
                return payload
            token = context.token

            api_prefix = os.getenv("TTK_API_BASE_URL")
            api_route = os.getenv("TTK_ORDER_UPDATE_ROUTE")  # api/v2/orderUpdate
            if not api_prefix:
                logger.error(
                    "Api prefix is missing. Skipping OrderStatusUpdate Preaction process."
                )
                return payload

            order_status_update_api = api_prefix + api_route

            # Step 1: Decode outer token
            outer_payload = self._decode_jwt(token=token)

            # Step 2: Search for 'token'
            inner_token = self.find_token_field(outer_payload)
            if not inner_token:
                # logger.error("Inner token not found in the decoded payload.")
                # return payload
                inner_token = "example_token"

            parsed_form_rec = Schengentouristvisa(**payload.model_dump())

            makerConfirmation = False
            appointmentDetails = {}
            additionalReviewRequired: bool = False
            formStatus:str | None = None
            travelerDetails: TravelerDetailsModel = TravelerDetailsModel()
            formTitle:str|None = ''

            if (
                parsed_form_rec.lets_get_started
                and parsed_form_rec.lets_get_started.form_status
            ):
                formStatus = parsed_form_rec.lets_get_started.form_status

            if (parsed_form_rec.visa_request_information and
                parsed_form_rec.visa_request_information.visa_request and
                parsed_form_rec.visa_request_information.visa_request.form_title):
                formTitle = parsed_form_rec.visa_request_information.visa_request.form_title
            if (
                parsed_form_rec.submit_info
                and parsed_form_rec.submit_info.confirm
                and getattr(
                    parsed_form_rec.submit_info.confirm.viewed_data, "value", "NO"
                )
                == "YES"
            ):
                makerConfirmation = True
            if (
                parsed_form_rec.submit_info
                and parsed_form_rec.submit_info.docket
                and parsed_form_rec.submit_info.docket == DOCKETSTATUS.ADDITIONAL_REVIEW
            ):
                additionalReviewRequired = True
            if (
                parsed_form_rec.visa_request_information
                and parsed_form_rec.visa_request_information.visa_request
            ):
                visa_request = parsed_form_rec.visa_request_information.visa_request
                travelerDetails = TravelerDetailsModel(
                    dateOfArrival=(
                        visa_request.arrival_date.strftime("%d-%m-%Y")
                        if visa_request.arrival_date
                        else None
                    ),
                    dateOfDeparture=(
                        visa_request.departure_date.strftime("%d-%m-%Y")
                        if visa_request.departure_date
                        else None
                    ),
                    lengthOfStay=(
                        visa_request.length_of_stay
                        if isinstance(visa_request.length_of_stay, int)
                        else None
                    ),
                    validityOfVisa=(
                        visa_request.validity
                        if isinstance(visa_request.validity, int)
                        else None
                    ),
                    visaMode=(
                        visa_request.visa_mode.value
                        if visa_request.visa_mode is not None
                        else None
                    ),
                )
            if (
                parsed_form_rec.appointment
                and parsed_form_rec.appointment.appointment_scheduled
            ):
                schedule = parsed_form_rec.appointment.appointment_scheduled
                appointmentDetails["location"] = schedule.scheduled_location or ""

                # Combine into yyyy-mm-dd HH:MM format
                raw_date = schedule.scheduled_date
                hour = schedule.scheduled_hour.value if schedule.scheduled_hour else 0
                minute = (
                    schedule.scheduled_minute.value if schedule.scheduled_minute else 0
                )

                appointment_datetime = ""

                if raw_date:
                    # Combine date and time safely
                    dt_obj = datetime.combine(raw_date, time(hour=hour, minute=minute))

                    # Format as string "YYYY-MM-DD HH:MM"
                    appointment_datetime = dt_obj.strftime("%Y-%m-%d %H:%M")

                appointmentDetails["appointmentDate"] = appointment_datetime

            body = {
                "orderId": parsed_form_rec.visa_request_information.visa_request.order_id,
                "completedSection": parsed_form_rec.lets_get_started.infopanes_completed,
                "totalSection": parsed_form_rec.lets_get_started.infopanes_total,
                "travellerId": parsed_form_rec.visa_request_information.visa_request.traveller_id,
                "makerConfirmation": makerConfirmation,
                "appointmentDetails": appointmentDetails,
                "additionalReviewRequired": additionalReviewRequired,
                "travellerName":formTitle,
                "formStatus": formStatus,
                "travelerDetails": travelerDetails.model_dump(),
            }
            logger.debug("Order Status Update Body:")
            logger.debug(json.dumps(body, indent=2))

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    order_status_update_api,
                    content=json.dumps(body),
                    headers={
                        "Authorization": f"Bearer {inner_token}",
                        "Content-Type": "application/json",
                    },
                )

                try:
                    response_json = response.json()
                except Exception as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    return payload

                if response_json.get("status") != "success":
                    logger.error(
                        f"Order status update API returned error status. Full response: {response_json}"
                    )
                else:
                    logger.info("Order status update API call successful.")

            return payload
        except PluginException as pe:
            logger.error(pe.detailed_message)
            return payload
        except Exception as e:
            logger.error(
                f"Unhandles exception raised during OrderStatusUpdate preaction process. Error: {str(e)}"
            )
            return payload

    def _decode_jwt(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token, algorithms=["HS256"], options={"verify_signature": False}
            )
            return payload
        except Exception as e:
            raise PluginException(
                message="Internal error occurred. Please contact support.",
                detailed_message=f"Something went wrong while decoding payload: {e}",
            )

    def find_token_field(self, data: Dict[str, Any]) -> Union[str, None]:
        if isinstance(data, dict):
            provider_info = data.get("provider_info")
            if isinstance(provider_info, dict):
                token = provider_info.get("token")
                if isinstance(token, str):
                    return token

        return None

    def format_date(
        self,
        raw_date: Union[date, datetime, str, None],
    ) -> str:
        """
        Formats a date, datetime, or string into a standard yyyy-mm-dd format.
        Returns the input if it's already a string.
        """
        if isinstance(raw_date, str):
            return raw_date
        if isinstance(raw_date, datetime):
            return raw_date.strftime("%Y-%m-%d")
        if isinstance(raw_date, date):
            return raw_date.strftime("%Y-%m-%d")
        return ""
