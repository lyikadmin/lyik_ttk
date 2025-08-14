import logging
from typing import Annotated, Optional

import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    PreActionProcessorSpec,
    ContextModel,
    GenericFormRecordModel,
)
from lyik.ttk.models.forms.schengentouristvisa import (
    RootLetsGetStarted,
    Schengentouristvisa,
    RootVisaRequestInformationVisaRequest,
    RootScratchPad,
)
from pydantic import BaseModel
import country_converter as coco
from datetime import date

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

impl = pluggy.HookimplMarker(getProjectName())


# --- Utility to format a date object to 'DD/MM/YYYY' string ---
def format_date_to_string(d: Optional[date]) -> Optional[str]:
    if d:
        try:
            return d.strftime("%d-%b-%Y")  # e.g. 02-Aug-1990
        except Exception as e:
            logger.warning(f"Date formatting failed for '{d}': {e}")
    return None


# --- Country converter to get full name from ISO3 code ---
class ISO3ToCountryModel(BaseModel):
    iso3_input: str
    _cc: coco.CountryConverter = coco.CountryConverter()

    # Some Countries full name should be used, for example 'Czechia' should be 'Czech Republic' instead.
    USE_COUNTRY_FULL_NAME = ["CZE"]

    def country_name(self) -> str:
        """
        Converts ISO3 code (e.g., 'IND') to full country name (e.g., 'India').
        Falls back to original input on failure.
        """
        iso = (self.iso3_input or "").strip().upper()
        to_field = "name_official" if iso in self.USE_COUNTRY_FULL_NAME else "name_short"
        try:
            result = self._cc.convert(
                names=iso, to=to_field, not_found=None
            )
            if result and isinstance(result, str):
                return result
        except Exception as e:
            logger.warning(
                f"ISO3 to country name conversion failed for '{self.iso3_input}': {e}"
            )
        return self.iso3_input  # Fallback to original


class NormalizeFields(PreActionProcessorSpec):
    @impl
    async def pre_action_processor(
        self,
        context: ContextModel,
        action: Annotated[str, "save or submit"],
        current_state: Annotated[str | None, "previous record state"],
        new_state: Annotated[str | None, "new record state"],
        payload: Annotated[GenericFormRecordModel, "entire form record model"],
    ) -> Annotated[GenericFormRecordModel, "modified record with normalize fields"]:
        """
        This plugin normalizes/enriches certain field values.
        - Converts ISO3 country codes to full country names in separate fields
        - Formats date fields to 'DD/MM/YYYY' string representations
        """
        try:
            form = Schengentouristvisa(**payload.model_dump())
        except Exception as e:
            logger.error("Failed to parse form payload: %s", e)
            return payload

        visa_request: RootVisaRequestInformationVisaRequest | None = (
            form.visa_request_information.visa_request
            if form.visa_request_information
            else None
        )

        traveller_details = (
            "Primary Traveller"
            if (
                form.visa_request_information.visa_request
                and form.visa_request_information.visa_request.traveller_type
                == "Primary"
            )
            else (
                form.visa_request_information.visa_request.traveller_type
                if form.visa_request_information.visa_request
                and form.visa_request_information.visa_request.traveller_type
                else None
            )
        )

        # get the passport details
        try:
            first_name = form.passport.passport_details.first_name or ""
            surname = form.passport.passport_details.surname or ""

            traveller_full_name = " ".join(filter(None, [first_name, surname]))
        except Exception as e:
             traveller_full_name = " "

        sub_title: str | None = context.form_name

        # If available, use the from country full name as form subtitle.
        if (
            form.visa_request_information
            and form.visa_request_information.visa_request
            and form.visa_request_information.visa_request.to_country_full_name
        ):
            sub_title = form.visa_request_information.visa_request.to_country_full_name

        if not visa_request:
            return payload

        modified = False

        if form.visa_request_information and form.visa_request_information.visa_request:
            form.visa_request_information.visa_request.form_title = traveller_full_name

        def convert_to_country_name(country_code: str) -> str:
            code = country_code.strip().upper()
            if len(code) == 3 and code.isalpha():
                return ISO3ToCountryModel(iso3_input=code).country_name() or country_code
            return country_code

        # From country full name converstion.
        from_country = visa_request.from_country
        if from_country:
            new_name = convert_to_country_name(from_country)
            if new_name != from_country:
                visa_request.from_country_full_name = new_name
                modified = True

        # To country full name converstion.
        to_country = visa_request.to_country
        if to_country:
            new_name = convert_to_country_name(to_country)
            if new_name != to_country:
                visa_request.to_country_full_name = new_name
                modified = True

        # Arrival date formatting conversion.
        arrival_val = visa_request.arrival_date
        if arrival_val:
            formatted = format_date_to_string(arrival_val)
            if formatted and formatted != visa_request.arrival_date_formatted:
                visa_request.arrival_date_formatted = formatted
                modified = True

        # Arrival date formatting conversion.
        departure_val = visa_request.departure_date
        if departure_val:
            formatted = format_date_to_string(departure_val)
            if formatted and formatted != visa_request.departure_date_formatted:
                visa_request.departure_date_formatted = formatted
                modified = True


        # --- ADD Traveler Details header ---
        try:
            if form.lets_get_started:
                lets = form.lets_get_started
            else:
                lets = RootLetsGetStarted()
            # lets = updated_data.get("lets_get_started", {})
            if traveller_details:
                lets.traveler_details_header = (
                    f"<h2 style='text-align: center'>{traveller_details}</h2>"
                )
                # if sub_title:
                #     lets["traveler_details_header"] = f"<h1 style='text-align: center'>{traveller_details} | {context.form_name}</h1>"
                # else:
                #     lets["traveler_details_header"] = f"<h1 style='text-align: center'>{traveller_details}</h1>"
            form.lets_get_started = lets
            modified = True
        except Exception as e:
            logger.error(f"Failed to set traveler_details_header: {e}")
            form.lets_get_started = RootLetsGetStarted()
            form.lets_get_started.traveler_details_header = ""
            modified = True

        # --- UPDATE THE FORM TITLE ---
        try:
            if form.scratch_pad:
                scratch = form.scratch_pad
            else:
                scratch = RootScratchPad()
            scratch.form_title = traveller_full_name or ""
            form.scratch_pad = scratch
            modified = True
        except Exception as e:
            logger.error(f"Failed to set form_title: {e}")
            # guarantee you still return a dict
            form.scratch_pad = RootScratchPad()
            form.scratch_pad.form_title = ""
            modified = True

        # --- UPDATE THE FORM SUBTITLE ---
        try:
            if form.scratch_pad:
                scratch = form.scratch_pad
            else:
                scratch = RootScratchPad()
            scratch.form_sub_title = sub_title or ""
            form.scratch_pad = scratch
            modified = True
        except Exception as e:
            logger.error(f"Failed to set form_sub_title: {e}")
            form.scratch_pad = RootScratchPad()
            form.scratch_pad.form_sub_title = ""
            modified = True

        # Return original payload if no change was made
        if not modified:
            return payload

        return GenericFormRecordModel.model_validate(form.model_dump())
