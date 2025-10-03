import logging
from typing import Annotated, Dict
from typing import Any, Union
import jwt
import httpx

import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    PreActionProcessorSpec,
    ContextModel,
    GenericFormRecordModel,
)
from lyik.ttk.models.forms.schengentouristvisa import (
    Schengentouristvisa,
)
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

impl = pluggy.HookimplMarker(getProjectName())


class InvokeAppointmentAPI(PreActionProcessorSpec):
    @impl
    async def pre_action_processor(
        self,
        context: ContextModel,
        action: Annotated[str, "save or submit"],
        current_state: Annotated[str | None, "previous record state"],
        new_state: Annotated[str | None, "new record state"],
        payload: Annotated[GenericFormRecordModel, "entire form record model"],
    ) -> Annotated[GenericFormRecordModel, "possibly modified record"]:
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
                form = Schengentouristvisa(**payload.model_dump())
            except Exception as e:
                logger.error(
                    "Failed to parse form payload for country normalization: %s", e
                )
                return payload

            scratch_pad = form.scratch_pad

            if (
                getattr(scratch_pad, "appointment_city_dropdown_values", None)
                and getattr(scratch_pad, "appointment_city_dates", None)
                and getattr(scratch_pad, "business_days", None)
            ):
                logger.info(
                    "Scratch pad already contains appointment data. Skipping API call."
                )
                return payload

            try:
                country_code: str = (
                    form.visa_request_information.visa_request.from_country.value
                )
                visa_type: str = (
                    form.visa_request_information.visa_request.visa_type.value
                )
            except Exception as e:
                logger.error(
                    "Unable to fetch the country of departure or visa type from the form. Skipping preaction."
                )
                return payload

            url = "https://ttkcrmv2-uat.ttkservices.com/api/v2/getAppointmentDetail"

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

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=body, headers=headers)

            response.raise_for_status()
            data = response.json()

            if data.get("status") != "success":
                logger.error(f"Appointment API returned failure: {data}")
                return payload

            return_data = data.get("returnData", [])

            if not return_data:
                logger.warning("Appointment API returned no appointment data.")
                return payload

            city_dropdown_values = {item["city"]: item["city"] for item in return_data}
            city_dates = {item["city"]: item["appointmentDate"] for item in return_data}
            business_days = return_data[0].get("businessDays")

            if city_dropdown_values:
                form.scratch_pad.appointment_city_dropdown_values = str(
                    city_dropdown_values
                )
            if city_dates:
                form.scratch_pad.appointment_city_dates = str(city_dates)
            if business_days is not None:
                form.scratch_pad.business_days = business_days

            logger.info("Successfully updated scratch pad with TTK appointment data.")

        except Exception as ex:
            logger.error(f"Something went wrong. Skipping preaction: {ex}")
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
