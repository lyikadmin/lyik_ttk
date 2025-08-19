from typing import List, Optional, ClassVar
from datetime import date
import jwt
import country_converter as coco
from pydantic import BaseModel

import logging
logger = logging.getLogger(__name__)


def get_personas_from_encoded_token(token: str) -> List[str] | None:
    try:
        # Decode the JWT token
        decoded_token = jwt.decode(token, options={"verify_signature": False})

        # Extract the personas from user_metadata
        personas = (
            decoded_token.get("user_metadata", {})
            .get("permissions", {})
            .get("persona", [])
        )

        return personas
    except Exception as e:
        return None

def format_date_to_string(d: Optional[date]) -> Optional[str]:
    try:
        return d.strftime("%d-%b-%Y")  # e.g. 02-Aug-1990
    except Exception as e:
        logger.warning(f"Date formatting failed for '{d}': {e}")
        return d


# --- Country converter to get full name from ISO3 code ---
class ISO3ToCountryModel(BaseModel):
    iso3_input: str
    _cc: coco.CountryConverter = coco.CountryConverter()

    # Some Countries full name should be used, for example 'Czechia' should be 'Czech Republic' instead.
    USE_COUNTRY_FULL_NAME: ClassVar[List[str]] = ["CZE"]

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