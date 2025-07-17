from typing import List
import jwt


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
