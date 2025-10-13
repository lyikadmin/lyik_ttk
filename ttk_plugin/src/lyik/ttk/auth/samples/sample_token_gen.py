# pip install PyJWT requests

import jwt
import base64
import json
import requests

TTK_TOKEN_SECRET = "BmThdDKu4lPOFiiqwHG1GQVm7iGeVIqALcqwJDM6VySzVdOwZ1UMoylzwhIDgXl6"
API_URL = "http://localhost:8080/v1/auth/get-token"


def base64url_encode(s: str) -> str:
    return base64.urlsafe_b64encode(s.encode()).decode().rstrip("=")


def extract_lyik_token(obj):
    """Try common field names and nested 'data' to pull a JWT-like token."""
    if not isinstance(obj, dict):
        return None
    candidate_keys = [
        "lyikToken",
        "LYIKToken",
        "token",
        "accessToken",
        "access_token",
        "jwt",
        "jwtToken",
        "id_token",
        "idToken",
    ]
    for k in candidate_keys:
        if k in obj and isinstance(obj[k], str) and obj[k].count(".") >= 2:
            return obj[k]
    if "data" in obj and isinstance(obj["data"], dict):
        return extract_lyik_token(obj["data"])
    return None


def run_for_payload(role_name: str, payload: dict):
    print("\n" + "=" * 90)
    print(f"🚀 Role: {role_name}")

    # 1) Build TTK token
    token = jwt.encode(payload, TTK_TOKEN_SECRET, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    # print(f"\n🔐 TTK Token ({role_name}):")
    # print(token)

    # 2) Decode & print payload
    decoded = jwt.decode(token, TTK_TOKEN_SECRET, algorithms=["HS256"])
    # print("\n📜 Decoded TTK Payload:")
    # print(json.dumps(decoded, indent=2))

    # 3) Call API with TTK token to fetch LYIK token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        # Your curl sent an empty body; mirroring that here:
        resp = requests.post(API_URL, headers=headers, data="")
        status = resp.status_code
        text = resp.text
        try:
            data = resp.json()
        except ValueError:
            data = None
    except requests.RequestException as e:
        print("\n❌ API call failed:")
        print(str(e))
        return

    if not (200 <= status < 300):
        print("\n❌ API returned an error:")
        print(f"Status: {status}")
        print(f"Body: {text}")
        return

    if data is None:
        print("\n⚠️ API did not return JSON. Raw response:")
        print(text)
        return

    # 4) Extract & print LYIK token
    lyik_token = extract_lyik_token(data)
    if not lyik_token:
        print("\nℹ️ Full API JSON (no obvious token field found):")
        print(json.dumps(data, indent=2))
        return

    print(f"\n🔑 LYIK Token ({role_name}):")
    print(lyik_token)

    # 5) Base64URL-encode the full LYIK token string
    lyik_token_b64url = base64url_encode(lyik_token)
    print(f"\n📦 Base64URL Encoded LYIK Token ({role_name}):")
    print(lyik_token_b64url)


# ---- All four payloads ----
payloads = [
    (
        "client",
        {
            "userId": "U001",
            "accessType": "client",
            "fullName": "Example Client",
            "loginTime": "2025-04-25 15:10:30",
            "expiryTimestamp": "1781934720",
            "Order ID": "RVIS-03072025-003",
        },
    ),
    (
        "maker",
        {
            "userId": "U002",
            "accessType": "maker",
            "fullName": "Example Maker",
            "loginTime": "2025-04-25 15:10:30",
            "expiryTimestamp": "1781934720",
            "Order ID": "RVIS-03072025-003",
        },
    ),
    (
        "corporate_client",
        {
            "userId": "U003",
            "accessType": "corporate_client",
            "fullName": "Example Corporate Client",
            "loginTime": "2025-04-25 15:10:30",
            "expiryTimestamp": "1781934720",
            "Order ID": "RVIS-03072025-003",
        },
    ),
    (
        "sme",
        {
            "userId": "U004",
            "accessType": "sme",
            "fullName": "Example SME",
            "loginTime": "2025-04-25 15:10:30",
            "expiryTimestamp": "1781934720",
            "Order ID": "RVIS-03072025-003",
        },
    ),
    (
        "spoc",
        {
            "userId": "U005",
            "accessType": "spoc",
            "fullName": "Example SPOC",
            "loginTime": "2025-04-25 15:10:30",
            "expiryTimestamp": "1781934720",
            "Order ID": "RVIS-03072025-003",
        },
    ),
    (
        "admin",
        {
            "userId": "U006",
            "accessType": "admin",
            "fullName": "Debasish Client",
            "loginTime": "2025-04-25 15:10:30",
            "expiryTimestamp": "1781934720",
        },
    ),
]

if __name__ == "__main__":
    for role, pl in payloads:
        run_for_payload(role, pl)
