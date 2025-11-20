import logging
from typing import Annotated

import apluggy as pluggy
from lyikpluginmanager import (
    ContextModel,
    GenericFormRecordModel,
)
from lyik.ttk.models.generated.universal_model import (
    UniversalModel,
    RootVisaRequestInformationVisaRequest,
)
from .._base_preaction import BaseUnifiedPreActionProcessor
from pydantic import BaseModel
import country_converter as coco

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Utility model for conversion
class CountryModel(BaseModel):
    country_input: str
    _cc: coco.CountryConverter = coco.CountryConverter()

    def alpha3(self) -> str:
        try:
            result = self._cc.convert(
                names=self.country_input,
                to="ISO3",
                not_found=None
            )
            if result and isinstance(result, str) and len(result) == 3:
                return result.upper()
        except Exception as e:
            logger.warning(f"Country conversion failed for '{self.country_input}': {e}")
        return self.country_input  # Fallback to original


class NormalizeCountryCodes(BaseUnifiedPreActionProcessor):
    async def unified_pre_action_processor_impl(
        self,
        context: ContextModel,
        action: Annotated[str, "save or submit"],
        current_state: Annotated[str | None, "previous record state"],
        new_state: Annotated[str | None, "new record state"],
        payload: Annotated[GenericFormRecordModel, "entire form record model"],
    ) -> Annotated[GenericFormRecordModel, "possibly modified record"]:
        """
        Convert 'from_country' and 'to_country' fields in the visa request to ISO3 format.
        """
        try:
            form = UniversalModel(**payload.model_dump())
        except Exception as e:
            logger.error("Failed to parse form payload for country normalization: %s", e)
            return payload

        visa_request: RootVisaRequestInformationVisaRequest | None = (
            form.visa_request_information.visa_request
            if form.visa_request_information else None
        )

        if not visa_request:
            return payload

        modified = False

        for attr in ["from_country", "to_country"]:
            val = getattr(visa_request, attr, None)
            if val:
                iso3 = CountryModel(country_input=val).alpha3()
                if iso3 != val:
                    setattr(visa_request, attr, iso3)
                    modified = True

        if not modified:
            return payload

        updated_data = form.model_dump(mode="json")
        return GenericFormRecordModel.model_validate(updated_data)



