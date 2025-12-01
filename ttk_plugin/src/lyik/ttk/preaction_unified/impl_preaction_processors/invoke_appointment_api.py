import logging
from typing import Any, Union, Optional, Annotated, Dict
from typing_extensions import Doc
import jwt
import httpx
import os
import json
from datetime import datetime
from lyikpluginmanager import (
    PluginException,
)

from lyikpluginmanager.annotation import RequiredEnv
import apluggy as pluggy
from lyikpluginmanager import (
    ContextModel,
    GenericFormRecordModel,
)

from lyik.ttk.models.generated.universal_model_with_appointment import (
    UniversalModelWithAppointment,
    RootAppointment,
    RootAppointmentEarliestAppointmentDate,
)
from lyik.ttk.utils.form_indicator import FormIndicator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from .._base_preaction import BaseUnifiedPreActionProcessor


# --- Utility to format a date object to 'YYYY-MM-DD' string ---
def format_date_to_string(date_str: str) -> Optional[str]:
    if date_str:
        try:
            parsed = datetime.strptime(date_str, "%Y-%m-%d").date()
            # return parsed.strftime("%d-%b-%Y")  # e.g. 02-Aug-1990
            # return parsed.strftime("%Y-%m-%d") # e.g. 1990-08-02
            return parsed.strftime("%d/%m/%Y")  # e.g. 02/08/1990
        except Exception as e:
            logger.warning(f"Date formatting failed for '{date_str}': {e}")
    return None


class InvokeAppointmentAPI(BaseUnifiedPreActionProcessor):
    async def unified_pre_action_processor_impl(
        self,
        context: ContextModel,
        action: Annotated[str, "save or submit"],
        current_state: Annotated[str | None, "previous record state"],
        new_state: Annotated[str | None, "new record state"],
        form_indicator: Annotated[
            FormIndicator,
            Doc("The form indicator for the form"),
        ],
        payload: Annotated[GenericFormRecordModel, "entire form record model"],
    ) -> Annotated[
        GenericFormRecordModel,
        RequiredEnv(["TTK_API_BASE_URL", "TTK_APPOINTMENT_API_ROUTE"]),
        Doc("possibly modified record"),
    ]:
        RUN_API = True
        try:
            if not context:
                logger.error("Context is missing. Skipping preaction.")
                return payload
            if not context.token:
                logger.error("Token is missing in context. Skipping preaction.")
                return payload

            token = context.token

            # Step 1: Decode outer token
            outer_payload = self._decode_jwt(token=token)

            # Step 2: Search for 'token'
            ttk_token = self.find_token_field(outer_payload)

            if not ttk_token:
                logger.error("TTK token is missing. Skipping preaction.")
                return payload

            try:
                form = UniversalModelWithAppointment(**payload.model_dump())
            except Exception as e:
                logger.error(
                    "Failed to parse form payload for country normalization: %s", e
                )
                return payload

            # Initialize appointment details if not present (The Case where a record was just created)
            if not form.appointment:
                form.appointment = RootAppointment()
                if not form.appointment.earliest_appointment_date:
                    form.appointment.earliest_appointment_date = RootAppointmentEarliestAppointmentDate()

            appointment = form.appointment

            if (
                appointment.earliest_appointment_date
                and appointment.earliest_appointment_date.appointment_city_dropdown_values
                and appointment.earliest_appointment_date.appointment_city_dates
                and appointment.earliest_appointment_date.business_days
            ):
                logger.info(
                    "Appointment section already contains appointment data. Skipping API call."
                )
                return payload

            try:
                country_code: str = (
                    form.visa_request_information.visa_request.to_country
                )
                visa_type: str = (
                    form.visa_request_information.visa_request.visa_type
                )
            except Exception as e:
                logger.error(
                    "Unable to fetch the country of departure or visa type from the form. Skipping preaction."
                )
                return payload

            api_prefix = os.getenv("TTK_API_BASE_URL")
            api_route = os.getenv("TTK_APPOINTMENT_API_ROUTE")
            if not api_prefix or not api_route:
                logger.error(
                    "Api details missing. Skipping Appointment API Preaction process."
                )
                return payload

            url = api_prefix + api_route

            # Body for API request
            body = {
                "countryCode": country_code,
                "visaType": visa_type,
                "submissionType": "Normal",
            }

            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {ttk_token}",
            }

            if RUN_API:
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, json=body, headers=headers)
                response.raise_for_status()
                data = response.json()

                logger.debug(f"The raw data returned for appointment API: {data}")

                if data.get("status") != "success":
                    logger.error(f"Appointment API returned failure: {data}")
                    return payload

                return_data = data.get("returnData", [])

                if not return_data:
                    if not current_state:  # Case when the record is new
                        logger.warning("Appointment API returned no appointment data.")
                        return payload
                    else:
                        raise PluginException(
                            message=f"Appointment Information cannot be fetched for country '{country_code}'. Please try again later."
                        )

                city_dropdown_values = {
                    item["city"]: item["city"] for item in return_data
                }
                city_dates = {
                    item["city"]: format_date_to_string(
                        date_str=item["appointmentDate"]
                    )
                    for item in return_data
                }
                # Get the first valid business Days.
                for item in return_data:
                    val = item.get("businessDays")
                    # treat None or empty-string (after stripping) as empty; 0 is allowed
                    if val is not None and (
                        not isinstance(val, str) or val.strip() != ""
                    ):
                        business_days = str(val)
                        break
                else:
                    business_days = ""
            else:
                # Hardcoded Values for testing:
                city_dropdown_values = {
                    "Ahmedabad": "Ahmedabad",
                    "Bengaluru": "Bengaluru",
                    "Chandigarh": "Chandigarh",
                    "Chennai": "Chennai",
                    "Cochin": "Cochin",
                    "Hyderabad": "Hyderabad",
                    "Jaipur": "Jaipur",
                    "Jalandhar": "Jalandhar",
                    "Kolkata": "Kolkata",
                    "Lucknow": "Lucknow",
                    "Mumbai": "Mumbai",
                    "Delhi": "Delhi",
                    "Pune": "Pune",
                }

                city_dates = {
                    "Ahmedabad": "08/10/2025",
                    "Bengaluru": "09/10/2025",
                    "Chandigarh": "10/10/2025",
                    "Chennai": "11/10/2025",
                    "Cochin": "12/10/2025",
                    "Hyderabad": "13/10/2025",
                    "Jaipur": "08/10/2025",
                    "Jalandhar": "08/10/2025",
                    "Kolkata": "08/10/2025",
                    "Lucknow": "08/10/2025",
                    "Mumbai": "08/10/2025",
                    "Delhi": "08/10/2025",
                    "Pune": "08/10/2025",
                }

                business_days = "10"


            if city_dropdown_values:
                form.appointment.earliest_appointment_date.appointment_city_dropdown_values = json.dumps(
                    city_dropdown_values
                )
            if city_dates:
                form.appointment.earliest_appointment_date.appointment_city_dates = (
                    json.dumps(city_dates)
                )
            if business_days is not None:
                form.appointment.earliest_appointment_date.business_days = business_days

        except PluginException as pe:
            raise
        except Exception as ex:
            logger.error(f"Something went wrong. Skipping appointment preaction: {ex}")
            return payload

        updated_data = form.model_dump(mode="json")
        return GenericFormRecordModel.model_validate(updated_data)

    def _decode_jwt(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token, algorithms=["HS256"], options={"verify_signature": False}
            )
            return payload
        except Exception as e:
            logger.error(f"Something went wrong while decoding payload: {e}")

    def find_token_field(self, data: Dict[str, Any]) -> Union[str, None]:
        if isinstance(data, dict):
            provider_info = data.get("provider_info")
            if isinstance(provider_info, dict):
                token = provider_info.get("token")
                if isinstance(token, str):
                    return token

        return None
