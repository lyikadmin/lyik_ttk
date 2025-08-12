from typing import List, Optional
from datetime import date
import jwt

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
