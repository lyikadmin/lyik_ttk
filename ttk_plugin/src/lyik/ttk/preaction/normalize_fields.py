import logging
from typing import Annotated, Optional

import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    PreActionProcessorSpec,
    ContextModel,
    GenericFormRecordModel,
)
from ..models.forms.new_schengentouristvisa import (
    Schengentouristvisa,
    RootVisaRequestInformationVisaRequest,
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

    def country_name(self) -> str:
        """
        Converts ISO3 code (e.g., 'IND') to full country name (e.g., 'India').
        Falls back to original input on failure.
        """
        try:
            result = self._cc.convert(
                names=self.iso3_input, to="name_short", not_found=None
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

        traveller_details = "Primary traveller" if (form.visa_request_information.visa_request and 
                                                    form.visa_request_information.visa_request.traveller_type == "Primary") else (form.visa_request_information.visa_request.traveller_type 
                                                                                                                                  if form.visa_request_information.visa_request and 
                                                                                                                                  form.visa_request_information.visa_request.traveller_type 
                                                                                                                                  else None)


        # get the passport details
        details = getattr(getattr(form, 'passport', None), 'passport_details', None)
        # join first and/or last name (if present), else None
        traveller_full_name = ' '.join(filter(None, (
            getattr(details, 'first_name', None),
            getattr(details, 'surname',    None),
        ))) or None

        sub_title :str|None = context.form_name

        if not visa_request:
            return payload

        modified = False

        if (form.visa_request_information and
        form.visa_request_information.visa_request):
            form.visa_request_information.visa_request.form_title = traveller_full_name

        # --- ISO3 → Full Country Name Mapping ---
        field_map = {
            "from_country": "from_country_full_name",
            "to_country": "to_country_full_name",
        }

        for source_field, target_field in field_map.items():
            val = getattr(visa_request, source_field, None)

            # Only convert if value looks like an ISO3 code
            if (
                val
                and isinstance(val, str)
                and val.isalpha()
                and len(val) == 3
                and val.isupper()
            ):
                country_name = ISO3ToCountryModel(iso3_input=val).country_name()
                if country_name and country_name != val:
                    setattr(visa_request, target_field, country_name)
                    modified = True
                    logger.info(
                        f"Expanded {source_field}: '{val}' -> '{country_name}' into '{target_field}'"
                    )

        # --- Date formatting ---
        date_fields = {
            "arrival_date": "arrival_date_formatted",
            "departure_date": "departure_date_formatted",
        }

        for src, target in date_fields.items():
            val = getattr(visa_request, src, None)
            formatted = format_date_to_string(val)
            if formatted:
                setattr(visa_request, target, formatted)
                modified = True
                logger.info(
                    f"Formatted {src}: '{val}' -> '{formatted}' into '{target}'"
                )

        updated_data = form.model_dump()

        # --- ADD Traveler Details header ---
        try:
            lets = updated_data.get("lets_get_started", {})
            if traveller_details:
                lets["traveler_details_header"] = f"<h2 style='text-align: center'>{traveller_details}</h2>"
                # if sub_title:
                #     lets["traveler_details_header"] = f"<h1 style='text-align: center'>{traveller_details} | {context.form_name}</h1>"
                # else:
                #     lets["traveler_details_header"] = f"<h1 style='text-align: center'>{traveller_details}</h1>"
            else:
                lets.setdefault("traveler_details_header", "")
            updated_data["lets_get_started"] = lets
            modified = True
        except Exception as e:
            logger.error(f"Failed to set traveler_details_header: {e}")
            updated_data.setdefault("lets_get_started", {})["traveler_details_header"] = ""
            modified = True

        # --- UPDATE THE FORM TITLE ---
        try:
            scratch = updated_data.get("scratch_pad") or {}
            scratch["form_title"] = traveller_full_name or ""
            updated_data["scratch_pad"] = scratch
            modified = True
        except Exception as e:
            logger.error(f"Failed to set form_title: {e}")
            # guarantee you still return a dict
            updated_data.setdefault("scratch_pad", {})["form_title"] = ""
            modified = True

        # --- UPDATE THE FORM SUBTITLE ---
        try:
            scratch = updated_data.get("scratch_pad") or {}
            scratch["form_sub_title"] = sub_title or ""
            updated_data["scratch_pad"] = scratch
            modified = True
        except Exception as e:
            logger.error(f"Failed to set form_sub_title: {e}")
            updated_data.setdefault("scratch_pad", {})["form_sub_title"] = ""
            modified = True

        # Return original payload if no change was made
        if not modified:
            return payload

        return GenericFormRecordModel.model_validate(updated_data)
