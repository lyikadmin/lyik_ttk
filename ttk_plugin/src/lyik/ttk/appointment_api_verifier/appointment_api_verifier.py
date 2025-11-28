import apluggy as pluggy
from lyikpluginmanager import (
    invoke,
    getProjectName,
    ContextModel,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
    PluginException,
)

from lyik.ttk.models.generated.universal_model_with_appointment import (
    UniversalModelWithAppointment,
    RootAppointmentEarliestAppointmentDate,
)
from datetime import datetime
from lyik.ttk.utils.verifier_util import check_if_verified
from typing import Annotated, Optional, Dict, Any, Union
from typing_extensions import Doc
from lyik.ttk.utils.message import get_error_message
import logging
import os
import httpx
import jwt
import json


logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())


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


class AppointmentAPIVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootAppointmentEarliestAppointmentDate,
            Doc("Earliest Apointment Date card payload"),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response after verifying the Earliest Apointment Date."),
    ]:
        """
        CTA To re-fetch the appointment details list
        """
        RUN_API = True
        try:
            if not context:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="The context is missing.",
                )
            if not context.token:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="The token is missing in context.",
                )

            token = context.token

            # Step 1: Decode outer token
            outer_payload = self._decode_jwt(token=token)

            # Step 2: Search for 'token'
            ttk_token = self.find_token_field(outer_payload)

            if not ttk_token:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="The ttk_token could not be found.",
                )

            try:
                form = UniversalModelWithAppointment(**context.record)
            except Exception as e:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="Failed to parse the form record.",
                )

            # Initialize appointment details if not present (The Case where a record was just created)
            # if not form.appointment:
            #     form.appointment = RootAppointment()

            # appointment = form.appointment

            # if (
            #     appointment.earliest_appointment_date
            #     and appointment.earliest_appointment_date.appointment_city_dropdown_values
            #     and appointment.earliest_appointment_date.appointment_city_dates
            #     and appointment.earliest_appointment_date.business_days
            # ):
            #     logger.info(
            #         "Appointment section already contains appointment data. Skipping API call."
            #     )
            #     return VerifyHandlerResponseModel(
            #         status=VERIFY_RESPONSE_STATUS.SUCCESS,
            #         actor="system",
            #         message="",
            #     )

            try:
                country_code: str = (
                    form.visa_request_information.visa_request.to_country.value
                )
                visa_type: str = (
                    form.visa_request_information.visa_request.visa_type.value
                )
            except Exception as e:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_VISA_TYPE_COA_MISSING"
                    ),
                    detailed_message="The visa_type of the to_country is missing in the record.",
                )

            api_prefix = os.getenv("TTK_API_BASE_URL")
            api_route = os.getenv("TTK_APPOINTMENT_API_ROUTE")
            if not api_prefix or not api_route:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="Api details missing. Skipping Appointment API Preaction process.",
                )

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
                    raise PluginException(
                        message=get_error_message(
                            error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                        ),
                        detailed_message=f"Appointment API returned failure: {data}",
                    )

                return_data = data.get("returnData", [])

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

            parsed_payload = RootAppointmentEarliestAppointmentDate(**payload)

            if city_dropdown_values:
                parsed_payload.appointment_city_dropdown_values = json.dumps(
                    city_dropdown_values
                )
            if city_dates:
                parsed_payload.appointment_city_dates = json.dumps(city_dates)
            if business_days is not None:
                parsed_payload.business_days = business_days

            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                message="",  # verified_successfully
                actor="system",
                response=parsed_payload.model_dump(),
            )

        except PluginException as pe:
            logger.error(pe.detailed_message)
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                actor="system",
                message=pe.message,
            )
        except Exception as ex:
            logger.error(f"Something went wrong: {ex}")
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                actor="system",
                message=get_error_message(error_message_code="LYIK_ERR_SAVE_FAILURE"),
            )

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
