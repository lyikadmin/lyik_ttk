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
        "lyikToken", "LYIKToken", "token", "accessToken", "access_token",
        "jwt", "jwtToken", "id_token", "idToken"
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

    print(f"\n🔐 TTK Token ({role_name}):")
    print(token)

    # 2) Decode & print payload
    decoded = jwt.decode(token, TTK_TOKEN_SECRET, algorithms=["HS256"])
    print("\n📜 Decoded TTK Payload:")
    print(json.dumps(decoded, indent=2))

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
    ("client", {
        "userId": "U001",
        "accessType": "client",
        "fullName": "Example Client",
        "loginTime": "2025-04-25 15:10:30",
        "expiryTimestamp": "1781934720",
        "Order ID": "RVIS-03072025-001",
        # "relationship": ["user_xyz", "user_1222"],
        # "iss": "https://auth.ttk.com/",
        # "aud": "https://lyik.com",
    }),
    ("maker", {
        "userId": "U002",
        "accessType": "maker",
        "fullName": "Example Maker",
        "loginTime": "2025-04-25 15:10:30",
        "expiryTimestamp": "1781934720",
        "Order ID": "RVIS-03072025-001",
    }),
    ("checker", {
        "userId": "U003",
        "accessType": "checker",
        "fullName": "Example Checker",
        "loginTime": "2025-04-25 15:10:30",
        "expiryTimestamp": "1781934720",
        "Order ID": "RVIS-03072025-001",
    }),
    ("admin", {
        "userId": "U004",
        "accessType": "admin",
        "fullName": "Debasish Client",
        "loginTime": "2025-04-25 15:10:30",
        "expiryTimestamp": "1781934720",
        # "Order ID": "RVIS-03072025-001",
        # "relationship": ["user_xyz", "user_1222"],
        # "iss": "https://auth.ttk.com/",
        # "aud": "https://lyik.com",
    }),
]

if __name__ == "__main__":
    for role, pl in payloads:
        run_for_payload(role, pl)


'''

==========================================================================================
🚀 Role: client

🔐 TTK Token (client):
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJVMDAxIiwiYWNjZXNzVHlwZSI6ImNsaWVudCIsImZ1bGxOYW1lIjoiRXhhbXBsZSBDbGllbnQiLCJsb2dpblRpbWUiOiIyMDI1LTA0LTI1IDE1OjEwOjMwIiwiZXhwaXJ5VGltZXN0YW1wIjoiMTc4MTkzNDcyMCIsIk9yZGVyIElEIjoiUlZJUy0wMzA3MjAyNS0wMDEifQ._nfPlaaXBKVM9Cqxo5ys2A7ObK__Tjdpn5h4qGzUlsU

📜 Decoded TTK Payload:
{
  "userId": "U001",
  "accessType": "client",
  "fullName": "Example Client",
  "loginTime": "2025-04-25 15:10:30",
  "expiryTimestamp": "1781934720",
  "Order ID": "RVIS-03072025-001"
}

🔑 LYIK Token (client):
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2x5aWsuY29tIiwiYXVkIjoiaHR0cHM6Ly9seWlrLmNvbSIsInN1YiI6IlUwMDEiLCJ1c2VyX21ldGFkYXRhIjp7InVzZXJfaW5mbyI6eyJ1c2VyX2lkIjoiVTAwMSIsInBob25lX251bWJlciI6bnVsbCwiZW1haWwiOm51bGwsInJvbGVzIjpbImNsaWVudCJdLCJyZWxhdGlvbnNoaXAiOm51bGwsIm9yZ2FuaXphdGlvbl9pZCI6Im9yZzExMjU2MTE1IiwiZGlzcGxheV9uYW1lIjoiRXhhbXBsZSBDbGllbnQiLCJwbHVnaW5fcHJvdmlkZXIiOiJodHRwczovL2F1dGgudHRrLmNvbS8ifSwidXNlcl9yZWxhdGlvbnNoaXBfaW5mbyI6bnVsbCwib3duZXJfb2YiOlsib3JnMTEyNTYxMTUiXSwicGVybWlzc2lvbnMiOnsid2VpZ2h0IjoxMDAsInBlcnNvbmEiOlsiQ0xJIl0sInBlcm1pc3Npb24iOm51bGx9fSwiZXhwIjoxNzgxOTM0NzIwLCJpYXQiOjE3NTQ4OTUwMzIsIm5iZiI6MTc1NDg5NTAzMiwicHJvdmlkZXJfaW5mbyI6eyJwcm92aWRlcl9uYW1lIjoiaHR0cHM6Ly9hdXRoLnR0ay5jb20vIiwidG9rZW4iOiJleUpoYkdjaU9pSklVekkxTmlJc0luUjVjQ0k2SWtwWFZDSjkuZXlKMWMyVnlTV1FpT2lKVk1EQXhJaXdpWVdOalpYTnpWSGx3WlNJNkltTnNhV1Z1ZENJc0ltWjFiR3hPWVcxbElqb2lSWGhoYlhCc1pTQkRiR2xsYm5RaUxDSnNiMmRwYmxScGJXVWlPaUl5TURJMUxUQTBMVEkxSURFMU9qRXdPak13SWl3aVpYaHdhWEo1VkdsdFpYTjBZVzF3SWpvaU1UYzRNVGt6TkRjeU1DSXNJazl5WkdWeUlFbEVJam9pVWxaSlV5MHdNekEzTWpBeU5TMHdNREVpZlEuX25mUGxhYVhCS1ZNOUNxeG81eXMyQTdPYktfX1RqZHBuNWg0cUd6VWxzVSJ9fQ.dIqlRirww-g1ZSFlRqLZ8AMrKNo0b6rdPR-t9y6Nw65IYlZaa2mgyxFAX74V4PSyHAV55_8LlI_QEPuABuUUa5wSXrQSjiie0trVUewO2UC7qUmEDuuUlpcNuBam6j6Phx6ZjEodQiA_e47TWY3J9gFAbbBt7rOrlJN_o1tyVWkMuA98_bp9KkQMoKaqLaX5kZf_4k-x7OzCWEdGyoF9JGFcda_iOoCB73QMfLTbzdFiPHSgbYYjMHvdgcsjqjiXlcxKhNauiAOdA0hZDyqBwibM7eI8ohdDwpXyUO2X8BoMkqA_rUAR9vgcZm1C7hNjDsnH0V0TQwAzSRQvAqdOqQ

📦 Base64URL Encoded LYIK Token (client):
ZXlKaGJHY2lPaUpTVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBjM01pT2lKb2RIUndjem92TDJ4NWFXc3VZMjl0SWl3aVlYVmtJam9pYUhSMGNITTZMeTlzZVdsckxtTnZiU0lzSW5OMVlpSTZJbFV3TURFaUxDSjFjMlZ5WDIxbGRHRmtZWFJoSWpwN0luVnpaWEpmYVc1bWJ5STZleUoxYzJWeVgybGtJam9pVlRBd01TSXNJbkJvYjI1bFgyNTFiV0psY2lJNmJuVnNiQ3dpWlcxaGFXd2lPbTUxYkd3c0luSnZiR1Z6SWpwYkltTnNhV1Z1ZENKZExDSnlaV3hoZEdsdmJuTm9hWEFpT201MWJHd3NJbTl5WjJGdWFYcGhkR2x2Ymw5cFpDSTZJbTl5WnpFeE1qVTJNVEUxSWl3aVpHbHpjR3hoZVY5dVlXMWxJam9pUlhoaGJYQnNaU0JEYkdsbGJuUWlMQ0p3YkhWbmFXNWZjSEp2ZG1sa1pYSWlPaUpvZEhSd2N6b3ZMMkYxZEdndWRIUnJMbU52YlM4aWZTd2lkWE5sY2w5eVpXeGhkR2x2Ym5Ob2FYQmZhVzVtYnlJNmJuVnNiQ3dpYjNkdVpYSmZiMllpT2xzaWIzSm5NVEV5TlRZeE1UVWlYU3dpY0dWeWJXbHpjMmx2Ym5NaU9uc2lkMlZwWjJoMElqb3hNREFzSW5CbGNuTnZibUVpT2xzaVEweEpJbDBzSW5CbGNtMXBjM05wYjI0aU9tNTFiR3g5ZlN3aVpYaHdJam94TnpneE9UTTBOekl3TENKcFlYUWlPakUzTlRRNE9UVXdNeklzSW01aVppSTZNVGMxTkRnNU5UQXpNaXdpY0hKdmRtbGtaWEpmYVc1bWJ5STZleUp3Y205MmFXUmxjbDl1WVcxbElqb2lhSFIwY0hNNkx5OWhkWFJvTG5SMGF5NWpiMjB2SWl3aWRHOXJaVzRpT2lKbGVVcG9Za2RqYVU5cFNrbFZla2t4VG1sSmMwbHVValZqUTBrMlNXdHdXRlpEU2prdVpYbEtNV015Vm5sVFYxRnBUMmxLVmsxRVFYaEphWGRwV1ZkT2FscFlUbnBXU0d4M1dsTkpOa2x0VG5OaFYxWjFaRU5KYzBsdFdqRmlSM2hQV1ZjeGJFbHFiMmxTV0dob1lsaENjMXBUUWtSaVIyeHNZbTVSYVV4RFNuTmlNbVJ3WW14U2NHSlhWV2xQYVVsNVRVUkpNVXhVUVRCTVZFa3hTVVJGTVU5cVJYZFBhazEzU1dsM2FWcFlhSGRoV0VvMVZrZHNkRnBZVGpCWlZ6RjNTV3B2YVUxVVl6Uk5WR3Q2VGtSamVVMURTWE5KYXpsNVdrZFdlVWxGYkVWSmFtOXBWV3hhU2xWNU1IZE5la0V6VFdwQmVVNVRNSGROUkVWcFpsRXVYMjVtVUd4aFlWaENTMVpOT1VOeGVHODFlWE15UVRkUFlrdGZYMVJxWkhCdU5XZzBjVWQ2Vld4elZTSjlmUS5kSXFsUmlyd3ctZzFaU0ZsUnFMWjhBTXJLTm8wYjZyZFBSLXQ5eTZOdzY1SVlsWmFhMm1neXhGQVg3NFY0UFN5SEFWNTVfOExsSV9RRVB1QUJ1VVVhNXdTWHJRU2ppaWUwdHJWVWV3TzJVQzdxVW1FRHV1VWxwY051QmFtNmo2UGh4NlpqRW9kUWlBX2U0N1RXWTNKOWdGQWJiQnQ3ck9ybEpOX28xdHlWV2tNdUE5OF9icDlLa1FNb0thcUxhWDVrWmZfNGsteDdPekNXRWRHeW9GOUpHRmNkYV9pT29DQjczUU1mTFRiemRGaVBIU2diWVlqTUh2ZGdjc2pxamlYbGN4S2hOYXVpQU9kQTBoWkR5cUJ3aWJNN2VJOG9oZER3cFh5VU8yWDhCb01rcUFfclVBUjl2Z2NabTFDN2hOakRzbkgwVjBUUXdBelNSUXZBcWRPcVE

==========================================================================================
🚀 Role: maker

🔐 TTK Token (maker):
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJVMDAyIiwiYWNjZXNzVHlwZSI6Im1ha2VyIiwiZnVsbE5hbWUiOiJFeGFtcGxlIE1ha2VyIiwibG9naW5UaW1lIjoiMjAyNS0wNC0yNSAxNToxMDozMCIsImV4cGlyeVRpbWVzdGFtcCI6IjE3ODE5MzQ3MjAiLCJPcmRlciBJRCI6IlJWSVMtMDMwNzIwMjUtMDAxIn0.EM0esr4jDhJk7RWwbJCDsU4FR-FoPsNzVjJW8icPryo

📜 Decoded TTK Payload:
{
  "userId": "U002",
  "accessType": "maker",
  "fullName": "Example Maker",
  "loginTime": "2025-04-25 15:10:30",
  "expiryTimestamp": "1781934720",
  "Order ID": "RVIS-03072025-001"
}

🔑 LYIK Token (maker):
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2x5aWsuY29tIiwiYXVkIjoiaHR0cHM6Ly9seWlrLmNvbSIsInN1YiI6IlUwMDIiLCJ1c2VyX21ldGFkYXRhIjp7InVzZXJfaW5mbyI6eyJ1c2VyX2lkIjoiVTAwMiIsInBob25lX251bWJlciI6bnVsbCwiZW1haWwiOm51bGwsInJvbGVzIjpbIm1ha2VyIl0sInJlbGF0aW9uc2hpcCI6bnVsbCwib3JnYW5pemF0aW9uX2lkIjoib3JnMTEyNTYxMTUiLCJkaXNwbGF5X25hbWUiOiJFeGFtcGxlIE1ha2VyIiwicGx1Z2luX3Byb3ZpZGVyIjoiaHR0cHM6Ly9hdXRoLnR0ay5jb20vIn0sInVzZXJfcmVsYXRpb25zaGlwX2luZm8iOm51bGwsIm93bmVyX29mIjpbIm9yZzExMjU2MTE1Il0sInBlcm1pc3Npb25zIjp7IndlaWdodCI6MTAwLCJwZXJzb25hIjpbIk1LUiJdLCJwZXJtaXNzaW9uIjpudWxsfX0sImV4cCI6MTc4MTkzNDcyMCwiaWF0IjoxNzU0ODk1MDMyLCJuYmYiOjE3NTQ4OTUwMzIsInByb3ZpZGVyX2luZm8iOnsicHJvdmlkZXJfbmFtZSI6Imh0dHBzOi8vYXV0aC50dGsuY29tLyIsInRva2VuIjoiZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SjFjMlZ5U1dRaU9pSlZNREF5SWl3aVlXTmpaWE56Vkhsd1pTSTZJbTFoYTJWeUlpd2lablZzYkU1aGJXVWlPaUpGZUdGdGNHeGxJRTFoYTJWeUlpd2liRzluYVc1VWFXMWxJam9pTWpBeU5TMHdOQzB5TlNBeE5Ub3hNRG96TUNJc0ltVjRjR2x5ZVZScGJXVnpkR0Z0Y0NJNklqRTNPREU1TXpRM01qQWlMQ0pQY21SbGNpQkpSQ0k2SWxKV1NWTXRNRE13TnpJd01qVXRNREF4SW4wLkVNMGVzcjRqRGhKazdSV3diSkNEc1U0RlItRm9Qc056VmpKVzhpY1ByeW8ifX0.aUc1ppYQSqjgvxBtw1ndSVcVdk6rxFlDsOPlBptnH-S6zHPKesFs1b9qHkKCxhJnDBRBsXLHR6hCiayD3JdqBAqrH4o8eGfIFl_ugUaIi2SrParpjKa1Idv0tolmVszSA3mGwDa6X93cctOwdMf_agn6w72InZXBMZ3vXE6TBHP3RO1efCWq48kXq2WpsfER2QDlGp_E-TOqBjw9mOt0OLVKUIZPoChLFgfhIlvtCcK95CNclXMefX14kWJeEGJv6HeEwOxp-XVeLYa-HQZcyFzFlVx22RqIRzYPwb34JA6TmbqTdbXcIXZVl4C38xP3mGYEnk8OfKROawryz4uI1A

📦 Base64URL Encoded LYIK Token (maker):
ZXlKaGJHY2lPaUpTVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBjM01pT2lKb2RIUndjem92TDJ4NWFXc3VZMjl0SWl3aVlYVmtJam9pYUhSMGNITTZMeTlzZVdsckxtTnZiU0lzSW5OMVlpSTZJbFV3TURJaUxDSjFjMlZ5WDIxbGRHRmtZWFJoSWpwN0luVnpaWEpmYVc1bWJ5STZleUoxYzJWeVgybGtJam9pVlRBd01pSXNJbkJvYjI1bFgyNTFiV0psY2lJNmJuVnNiQ3dpWlcxaGFXd2lPbTUxYkd3c0luSnZiR1Z6SWpwYkltMWhhMlZ5SWwwc0luSmxiR0YwYVc5dWMyaHBjQ0k2Ym5Wc2JDd2liM0puWVc1cGVtRjBhVzl1WDJsa0lqb2liM0puTVRFeU5UWXhNVFVpTENKa2FYTndiR0Y1WDI1aGJXVWlPaUpGZUdGdGNHeGxJRTFoYTJWeUlpd2ljR3gxWjJsdVgzQnliM1pwWkdWeUlqb2lhSFIwY0hNNkx5OWhkWFJvTG5SMGF5NWpiMjB2SW4wc0luVnpaWEpmY21Wc1lYUnBiMjV6YUdsd1gybHVabThpT201MWJHd3NJbTkzYm1WeVgyOW1JanBiSW05eVp6RXhNalUyTVRFMUlsMHNJbkJsY20xcGMzTnBiMjV6SWpwN0luZGxhV2RvZENJNk1UQXdMQ0p3WlhKemIyNWhJanBiSWsxTFVpSmRMQ0p3WlhKdGFYTnphVzl1SWpwdWRXeHNmWDBzSW1WNGNDSTZNVGM0TVRrek5EY3lNQ3dpYVdGMElqb3hOelUwT0RrMU1ETXlMQ0p1WW1ZaU9qRTNOVFE0T1RVd016SXNJbkJ5YjNacFpHVnlYMmx1Wm04aU9uc2ljSEp2ZG1sa1pYSmZibUZ0WlNJNkltaDBkSEJ6T2k4dllYVjBhQzUwZEdzdVkyOXRMeUlzSW5SdmEyVnVJam9pWlhsS2FHSkhZMmxQYVVwSlZYcEpNVTVwU1hOSmJsSTFZME5KTmtscmNGaFdRMG81TG1WNVNqRmpNbFo1VTFkUmFVOXBTbFpOUkVGNVNXbDNhVmxYVG1wYVdFNTZWa2hzZDFwVFNUWkpiVEZvWVRKV2VVbHBkMmxhYmxaellrVTFhR0pYVldsUGFVcEdaVWRHZEdOSGVHeEpSVEZvWVRKV2VVbHBkMmxpUnpsdVlWYzFWV0ZYTVd4SmFtOXBUV3BCZVU1VE1IZE9RekI1VGxOQmVFNVViM2hOUkc5NlRVTkpjMGx0VmpSalIyeDVaVlpTY0dKWFZucGtSMFowWTBOSk5rbHFSVE5QUkVVMVRYcFJNMDFxUVdsTVEwcFFZMjFTYkdOcFFrcFNRMGsyU1d4S1YxTldUWFJOUkUxM1RucEpkMDFxVlhSTlJFRjRTVzR3TGtWTk1HVnpjalJxUkdoS2F6ZFNWM2RpU2tORWMxVTBSbEl0Um05UWMwNTZWbXBLVnpocFkxQnllVzhpZlgwLmFVYzFwcFlRU3FqZ3Z4QnR3MW5kU1ZjVmRrNnJ4RmxEc09QbEJwdG5ILVM2ekhQS2VzRnMxYjlxSGtLQ3hoSm5EQlJCc1hMSFI2aENpYXlEM0pkcUJBcXJING84ZUdmSUZsX3VnVWFJaTJTclBhcnBqS2ExSWR2MHRvbG1Wc3pTQTNtR3dEYTZYOTNjY3RPd2RNZl9hZ242dzcySW5aWEJNWjN2WEU2VEJIUDNSTzFlZkNXcTQ4a1hxMldwc2ZFUjJRRGxHcF9FLVRPcUJqdzltT3QwT0xWS1VJWlBvQ2hMRmdmaElsdnRDY0s5NUNOY2xYTWVmWDE0a1dKZUVHSnY2SGVFd094cC1YVmVMWWEtSFFaY3lGekZsVngyMlJxSVJ6WVB3YjM0SkE2VG1icVRkYlhjSVhaVmw0QzM4eFAzbUdZRW5rOE9mS1JPYXdyeXo0dUkxQQ

==========================================================================================
🚀 Role: checker

🔐 TTK Token (checker):
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJVMDAzIiwiYWNjZXNzVHlwZSI6ImNoZWNrZXIiLCJmdWxsTmFtZSI6IkV4YW1wbGUgQ2hlY2tlciIsImxvZ2luVGltZSI6IjIwMjUtMDQtMjUgMTU6MTA6MzAiLCJleHBpcnlUaW1lc3RhbXAiOiIxNzgxOTM0NzIwIiwiT3JkZXIgSUQiOiJSVklTLTAzMDcyMDI1LTAwMSJ9.IkMnE_CRTsI7q0grkpr3pcdGuybRkttm0dV6n16QD30

📜 Decoded TTK Payload:
{
  "userId": "U003",
  "accessType": "checker",
  "fullName": "Example Checker",
  "loginTime": "2025-04-25 15:10:30",
  "expiryTimestamp": "1781934720",
  "Order ID": "RVIS-03072025-001"
}

🔑 LYIK Token (checker):
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2x5aWsuY29tIiwiYXVkIjoiaHR0cHM6Ly9seWlrLmNvbSIsInN1YiI6IlUwMDMiLCJ1c2VyX21ldGFkYXRhIjp7InVzZXJfaW5mbyI6eyJ1c2VyX2lkIjoiVTAwMyIsInBob25lX251bWJlciI6bnVsbCwiZW1haWwiOm51bGwsInJvbGVzIjpbImNoZWNrZXIiXSwicmVsYXRpb25zaGlwIjpudWxsLCJvcmdhbml6YXRpb25faWQiOiJvcmcxMTI1NjExNSIsImRpc3BsYXlfbmFtZSI6IkV4YW1wbGUgQ2hlY2tlciIsInBsdWdpbl9wcm92aWRlciI6Imh0dHBzOi8vYXV0aC50dGsuY29tLyJ9LCJ1c2VyX3JlbGF0aW9uc2hpcF9pbmZvIjpudWxsLCJvd25lcl9vZiI6WyJvcmcxMTI1NjExNSJdLCJwZXJtaXNzaW9ucyI6eyJ3ZWlnaHQiOjEwMCwicGVyc29uYSI6WyJQQVJFTlQiLCJDS1IiXSwicGVybWlzc2lvbiI6bnVsbH19LCJleHAiOjE3ODE5MzQ3MjAsImlhdCI6MTc1NDg5NTAzMiwibmJmIjoxNzU0ODk1MDMyLCJwcm92aWRlcl9pbmZvIjp7InByb3ZpZGVyX25hbWUiOiJodHRwczovL2F1dGgudHRrLmNvbS8iLCJ0b2tlbiI6ImV5SmhiR2NpT2lKSVV6STFOaUlzSW5SNWNDSTZJa3BYVkNKOS5leUoxYzJWeVNXUWlPaUpWTURBeklpd2lZV05qWlhOelZIbHdaU0k2SW1Ob1pXTnJaWElpTENKbWRXeHNUbUZ0WlNJNklrVjRZVzF3YkdVZ1EyaGxZMnRsY2lJc0lteHZaMmx1VkdsdFpTSTZJakl3TWpVdE1EUXRNalVnTVRVNk1UQTZNekFpTENKbGVIQnBjbmxVYVcxbGMzUmhiWEFpT2lJeE56Z3hPVE0wTnpJd0lpd2lUM0prWlhJZ1NVUWlPaUpTVmtsVExUQXpNRGN5TURJMUxUQXdNU0o5LklrTW5FX0NSVHNJN3EwZ3JrcHIzcGNkR3V5YlJrdHRtMGRWNm4xNlFEMzAifX0.C-qg7vUxpjt7kEkHLBQofCa-WcLJVwZPVgxjd2CwgMQyEbXIegBtdMKEeAL5q980-8zA2j8yt8xUTQvZwfA4TqKMdKqsIiaT-J8ww82UQH36kuS6YqpMuufUTEDyvMVlrtF8G56u-4UWPTNcCwdzp7VIo91I36UbBoHJC5x4Trxuk05RFIbt7nqFD_X26T5U9hBIGxawOyb2dtO9a8D9pVFRhfcI5b6BQq5uHyim5k8uVMbUjWvz6y4OJ7gaDrsnblZ1zxhQt8s_DTWr5gXSklFQnzgEP_fOBz6GIwXyAHVtC8OKDmhSfDWzW0SCpvBc4g_fC5vDvUJexB1PrsVzug

📦 Base64URL Encoded LYIK Token (checker):
ZXlKaGJHY2lPaUpTVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBjM01pT2lKb2RIUndjem92TDJ4NWFXc3VZMjl0SWl3aVlYVmtJam9pYUhSMGNITTZMeTlzZVdsckxtTnZiU0lzSW5OMVlpSTZJbFV3TURNaUxDSjFjMlZ5WDIxbGRHRmtZWFJoSWpwN0luVnpaWEpmYVc1bWJ5STZleUoxYzJWeVgybGtJam9pVlRBd015SXNJbkJvYjI1bFgyNTFiV0psY2lJNmJuVnNiQ3dpWlcxaGFXd2lPbTUxYkd3c0luSnZiR1Z6SWpwYkltTm9aV05yWlhJaVhTd2ljbVZzWVhScGIyNXphR2x3SWpwdWRXeHNMQ0p2Y21kaGJtbDZZWFJwYjI1ZmFXUWlPaUp2Y21jeE1USTFOakV4TlNJc0ltUnBjM0JzWVhsZmJtRnRaU0k2SWtWNFlXMXdiR1VnUTJobFkydGxjaUlzSW5Cc2RXZHBibDl3Y205MmFXUmxjaUk2SW1oMGRIQnpPaTh2WVhWMGFDNTBkR3N1WTI5dEx5SjlMQ0oxYzJWeVgzSmxiR0YwYVc5dWMyaHBjRjlwYm1adklqcHVkV3hzTENKdmQyNWxjbDl2WmlJNld5SnZjbWN4TVRJMU5qRXhOU0pkTENKd1pYSnRhWE56YVc5dWN5STZleUozWldsbmFIUWlPakV3TUN3aWNHVnljMjl1WVNJNld5SlFRVkpGVGxRaUxDSkRTMUlpWFN3aWNHVnliV2x6YzJsdmJpSTZiblZzYkgxOUxDSmxlSEFpT2pFM09ERTVNelEzTWpBc0ltbGhkQ0k2TVRjMU5EZzVOVEF6TWl3aWJtSm1Jam94TnpVME9EazFNRE15TENKd2NtOTJhV1JsY2w5cGJtWnZJanA3SW5CeWIzWnBaR1Z5WDI1aGJXVWlPaUpvZEhSd2N6b3ZMMkYxZEdndWRIUnJMbU52YlM4aUxDSjBiMnRsYmlJNkltVjVTbWhpUjJOcFQybEtTVlY2U1RGT2FVbHpTVzVTTldORFNUWkphM0JZVmtOS09TNWxlVW94WXpKV2VWTlhVV2xQYVVwV1RVUkJla2xwZDJsWlYwNXFXbGhPZWxaSWJIZGFVMGsyU1cxT2IxcFhUbkphV0VscFRFTktiV1JYZUhOVWJVWjBXbE5KTmtsclZqUlpWekYzWWtkVloxRXlhR3haTW5Sc1kybEpjMGx0ZUhaYU1teDFWa2RzZEZwVFNUWkpha2wzVFdwVmRFMUVVWFJOYWxWblRWUlZOazFVUVRaTmVrRnBURU5LYkdWSVFuQmpibXhWWVZjeGJHTXpVbWhpV0VGcFQybEplRTU2WjNoUFZFMHdUbnBKZDBscGQybFVNMHByV2xoSloxTlZVV2xQYVVwVFZtdHNWRXhVUVhwTlJHTjVUVVJKTVV4VVFYZE5VMG81TGtsclRXNUZYME5TVkhOSk4zRXdaM0pyY0hJemNHTmtSM1Y1WWxKcmRIUnRNR1JXTm00eE5sRkVNekFpZlgwLkMtcWc3dlV4cGp0N2tFa0hMQlFvZkNhLVdjTEpWd1pQVmd4amQyQ3dnTVF5RWJYSWVnQnRkTUtFZUFMNXE5ODAtOHpBMmo4eXQ4eFVUUXZad2ZBNFRxS01kS3FzSWlhVC1KOHd3ODJVUUgzNmt1UzZZcXBNdXVmVVRFRHl2TVZscnRGOEc1NnUtNFVXUFROY0N3ZHpwN1ZJbzkxSTM2VWJCb0hKQzV4NFRyeHVrMDVSRklidDducUZEX1gyNlQ1VTloQklHeGF3T3liMmR0TzlhOEQ5cFZGUmhmY0k1YjZCUXE1dUh5aW01azh1Vk1iVWpXdno2eTRPSjdnYURyc25ibFoxenhoUXQ4c19EVFdyNWdYU2tsRlFuemdFUF9mT0J6NkdJd1h5QUhWdEM4T0tEbWhTZkRXelcwU0NwdkJjNGdfZkM1dkR2VUpleEIxUHJzVnp1Zw

==========================================================================================
🚀 Role: admin

🔐 TTK Token (admin):
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJVMDA0IiwiYWNjZXNzVHlwZSI6ImFkbWluIiwiZnVsbE5hbWUiOiJEZWJhc2lzaCBDbGllbnQiLCJsb2dpblRpbWUiOiIyMDI1LTA0LTI1IDE1OjEwOjMwIiwiZXhwaXJ5VGltZXN0YW1wIjoiMTc4MTkzNDcyMCJ9.oiEyCQrvqGNYf_Ru21JA5nRRRMp2vtUgzcy1WMsB-KM

📜 Decoded TTK Payload:
{
  "userId": "U004",
  "accessType": "admin",
  "fullName": "Debasish Client",
  "loginTime": "2025-04-25 15:10:30",
  "expiryTimestamp": "1781934720"
}

🔑 LYIK Token (admin):
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2x5aWsuY29tIiwiYXVkIjoiaHR0cHM6Ly9seWlrLmNvbSIsInN1YiI6IlUwMDQiLCJ1c2VyX21ldGFkYXRhIjp7InVzZXJfaW5mbyI6eyJ1c2VyX2lkIjoiVTAwNCIsInBob25lX251bWJlciI6bnVsbCwiZW1haWwiOm51bGwsInJvbGVzIjpbImFkbWluIl0sInJlbGF0aW9uc2hpcCI6bnVsbCwib3JnYW5pemF0aW9uX2lkIjoib3JnMTEyNTYxMTUiLCJkaXNwbGF5X25hbWUiOiJEZWJhc2lzaCBDbGllbnQiLCJwbHVnaW5fcHJvdmlkZXIiOiJodHRwczovL2F1dGgudHRrLmNvbS8ifSwidXNlcl9yZWxhdGlvbnNoaXBfaW5mbyI6bnVsbCwib3duZXJfb2YiOlsib3JnMTEyNTYxMTUiXSwicGVybWlzc2lvbnMiOnsid2VpZ2h0IjoxMDAwMCwicGVyc29uYSI6WyJBRE1JTiIsIkNSRUFUT1IiXSwicGVybWlzc2lvbiI6bnVsbH19LCJleHAiOjE3ODE5MzQ3MjAsImlhdCI6MTc1NDg5NTAzMiwibmJmIjoxNzU0ODk1MDMyLCJwcm92aWRlcl9pbmZvIjp7InByb3ZpZGVyX25hbWUiOiJodHRwczovL2F1dGgudHRrLmNvbS8iLCJ0b2tlbiI6ImV5SmhiR2NpT2lKSVV6STFOaUlzSW5SNWNDSTZJa3BYVkNKOS5leUoxYzJWeVNXUWlPaUpWTURBMElpd2lZV05qWlhOelZIbHdaU0k2SW1Ga2JXbHVJaXdpWm5Wc2JFNWhiV1VpT2lKRVpXSmhjMmx6YUNCRGJHbGxiblFpTENKc2IyZHBibFJwYldVaU9pSXlNREkxTFRBMExUSTFJREUxT2pFd09qTXdJaXdpWlhod2FYSjVWR2x0WlhOMFlXMXdJam9pTVRjNE1Ua3pORGN5TUNKOS5vaUV5Q1FydnFHTllmX1J1MjFKQTVuUlJSTXAydnRVZ3pjeTFXTXNCLUtNIn19.nzQOgaKqgw2wSGBeTJD-B1l0sIzmdAkFQ4JH2R_RPmBlzJb5KlPOIKq_IOkBFbp87WxEpoq6TvJ7kSPbdV1DpuEX8Yhcr8z-4mmAcE2UeW3dSSxRCzuW38wzJN_ft_c5YdZl3OadxnFxOqz-CKagDaVmi_wKoQ9zIQcos3BmourD31_LvKdJpiEdXbPtdevUENlqEpPUUfS5O3UEUS8qz9SdGvYxH8YUDgm25sB4R8y3_vL37imVKisbWT4HjdrQ8dK2E3zMWZaNITxhioAunkuelfm4JAD74xcUhcVtiYjKAHFUDzgawddaovgw8iyAUNtubIUdI2oiVFoC7o4VVw

📦 Base64URL Encoded LYIK Token (admin):
ZXlKaGJHY2lPaUpTVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBjM01pT2lKb2RIUndjem92TDJ4NWFXc3VZMjl0SWl3aVlYVmtJam9pYUhSMGNITTZMeTlzZVdsckxtTnZiU0lzSW5OMVlpSTZJbFV3TURRaUxDSjFjMlZ5WDIxbGRHRmtZWFJoSWpwN0luVnpaWEpmYVc1bWJ5STZleUoxYzJWeVgybGtJam9pVlRBd05DSXNJbkJvYjI1bFgyNTFiV0psY2lJNmJuVnNiQ3dpWlcxaGFXd2lPbTUxYkd3c0luSnZiR1Z6SWpwYkltRmtiV2x1SWwwc0luSmxiR0YwYVc5dWMyaHBjQ0k2Ym5Wc2JDd2liM0puWVc1cGVtRjBhVzl1WDJsa0lqb2liM0puTVRFeU5UWXhNVFVpTENKa2FYTndiR0Y1WDI1aGJXVWlPaUpFWldKaGMybHphQ0JEYkdsbGJuUWlMQ0p3YkhWbmFXNWZjSEp2ZG1sa1pYSWlPaUpvZEhSd2N6b3ZMMkYxZEdndWRIUnJMbU52YlM4aWZTd2lkWE5sY2w5eVpXeGhkR2x2Ym5Ob2FYQmZhVzVtYnlJNmJuVnNiQ3dpYjNkdVpYSmZiMllpT2xzaWIzSm5NVEV5TlRZeE1UVWlYU3dpY0dWeWJXbHpjMmx2Ym5NaU9uc2lkMlZwWjJoMElqb3hNREF3TUN3aWNHVnljMjl1WVNJNld5SkJSRTFKVGlJc0lrTlNSVUZVVDFJaVhTd2ljR1Z5YldsemMybHZiaUk2Ym5Wc2JIMTlMQ0psZUhBaU9qRTNPREU1TXpRM01qQXNJbWxoZENJNk1UYzFORGc1TlRBek1pd2libUptSWpveE56VTBPRGsxTURNeUxDSndjbTkyYVdSbGNsOXBibVp2SWpwN0luQnliM1pwWkdWeVgyNWhiV1VpT2lKb2RIUndjem92TDJGMWRHZ3VkSFJyTG1OdmJTOGlMQ0owYjJ0bGJpSTZJbVY1U21oaVIyTnBUMmxLU1ZWNlNURk9hVWx6U1c1U05XTkRTVFpKYTNCWVZrTktPUzVsZVVveFl6SldlVk5YVVdsUGFVcFdUVVJCTUVscGQybFpWMDVxV2xoT2VsWkliSGRhVTBrMlNXMUdhMkpYYkhWSmFYZHBXbTVXYzJKRk5XaGlWMVZwVDJsS1JWcFhTbWhqTW14NllVTkNSR0pIYkd4aWJsRnBURU5LYzJJeVpIQmliRkp3WWxkVmFVOXBTWGxOUkVreFRGUkJNRXhVU1RGSlJFVXhUMnBGZDA5cVRYZEphWGRwV2xob2QyRllTalZXUjJ4MFdsaE9NRmxYTVhkSmFtOXBUVlJqTkUxVWEzcE9SR041VFVOS09TNXZhVVY1UTFGeWRuRkhUbGxtWDFKMU1qRktRVFZ1VWxKU1RYQXlkblJWWjNwamVURlhUWE5DTFV0TkluMTkubnpRT2dhS3FndzJ3U0dCZVRKRC1CMWwwc0l6bWRBa0ZRNEpIMlJfUlBtQmx6SmI1S2xQT0lLcV9JT2tCRmJwODdXeEVwb3E2VHZKN2tTUGJkVjFEcHVFWDhZaGNyOHotNG1tQWNFMlVlVzNkU1N4UkN6dVczOHd6Sk5fZnRfYzVZZFpsM09hZHhuRnhPcXotQ0thZ0RhVm1pX3dLb1E5eklRY29zM0Jtb3VyRDMxX0x2S2RKcGlFZFhiUHRkZXZVRU5scUVwUFVVZlM1TzNVRVVTOHF6OVNkR3ZZeEg4WVVEZ20yNXNCNFI4eTNfdkwzN2ltVktpc2JXVDRIamRyUThkSzJFM3pNV1phTklUeGhpb0F1bmt1ZWxmbTRKQUQ3NHhjVWhjVnRpWWpLQUhGVUR6Z2F3ZGRhb3ZndzhpeUFVTnR1YklVZEkyb2lWRm9DN280VlZ3
'''