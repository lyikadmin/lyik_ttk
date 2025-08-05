from lyikpluginmanager import CustomMessage
from typing import List


def get_error_message(
    error_message_code: str, parameters: List[str] | None = None
) -> str:
    try:
        error_message = str(
            CustomMessage(message_code=error_message_code, parameters=parameters)
        )
        return error_message
    except Exception as e:
        return f"Unknown error err_code:'{error_message_code}'"
