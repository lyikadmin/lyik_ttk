import base64

def decode_base64_to_str(encoded_str: str) -> str:
    """
    Decodes a URL-safe base64-encoded string to a UTF-8 string.
    """
    return base64.urlsafe_b64decode(encoded_str + '=' * (-len(encoded_str) % 4)).decode("utf-8")