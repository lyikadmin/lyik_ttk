from pydantic import BaseModel
import country_converter as coco
import logging
from datetime import date, datetime


logger = logging.getLogger(__name__)


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
        return self.iso3_input
