import logging
from typing import Annotated

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

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

impl = pluggy.HookimplMarker(getProjectName())


class ISO3ToCountryModel(BaseModel):
    iso3_input: str
    _cc: coco.CountryConverter = coco.CountryConverter()

    def country_name(self) -> str:
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


class ExpandCountryCodesToNames(PreActionProcessorSpec):
    @impl
    async def pre_action_processor(
        self,
        context: ContextModel,
        action: Annotated[str, "save or submit"],
        current_state: Annotated[str | None, "previous record state"],
        new_state: Annotated[str | None, "new record state"],
        payload: Annotated[GenericFormRecordModel, "entire form record model"],
    ) -> Annotated[GenericFormRecordModel, "modified record with expanded country"]:
        """
        If from_country and to_country contain ISO3 codes, convert them to country names
        and store in separate fields: from_country_full_name and to_country_full_name.
        """
        try:
            form = Schengentouristvisa(**payload.model_dump())
        except Exception as e:
            logger.error("Failed to parse form payload for country expansion: %s", e)
            return payload

        visa_request: RootVisaRequestInformationVisaRequest | None = (
            form.visa_request_information.visa_request
            if form.visa_request_information
            else None
        )

        if not visa_request:
            return payload

        modified = False

        field_map = {
            "from_country": "from_country_full_name",
            "to_country": "to_country_full_name",
        }

        for source_field, target_field in field_map.items():
            val = getattr(visa_request, source_field, None)

            # Check if it's a valid ISO3-like string (3 uppercase letters)
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

        if not modified:
            return payload

        updated_data = form.model_dump(mode="json")
        return GenericFormRecordModel.model_validate(updated_data)
