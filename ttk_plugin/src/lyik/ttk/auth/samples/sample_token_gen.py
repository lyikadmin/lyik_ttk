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
        "Order ID": "RVIS-03072025-003",
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
        "Order ID": "RVIS-03072025-003",
    }),
    ("checker", {
        "userId": "U003",
        "accessType": "checker",
        "fullName": "Example Checker",
        "loginTime": "2025-04-25 15:10:30",
        "expiryTimestamp": "1781934720",
        "Order ID": "RVIS-03072025-003",
    }),
    ("admin", {
        "userId": "U004",
        "accessType": "admin",
        "fullName": "Debasish Client",
        "loginTime": "2025-04-25 15:10:30",
        "expiryTimestamp": "1781934720",
        # "Order ID": "RVIS-03072025-003",
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
  "Order ID": "RVIS-03072025-003"
}

🔑 LYIK Token (client):
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2x5aWsuY29tIiwiYXVkIjoiaHR0cHM6Ly9seWlrLmNvbSIsInN1YiI6IlUwMDEiLCJ1c2VyX21ldGFkYXRhIjp7InVzZXJfaW5mbyI6eyJ1c2VyX2lkIjoiVTAwMSIsInBob25lX251bWJlciI6bnVsbCwiZW1haWwiOm51bGwsInJvbGVzIjpbImNsaWVudCJdLCJyZWxhdGlvbnNoaXAiOm51bGwsIm9yZ2FuaXphdGlvbl9pZCI6Im9yZzExMjU2MTE1IiwiZGlzcGxheV9uYW1lIjoiRXhhbXBsZSBDbGllbnQiLCJwbHVnaW5fcHJvdmlkZXIiOiJodHRwczovL2F1dGgudHRrLmNvbS8ifSwidXNlcl9yZWxhdGlvbnNoaXBfaW5mbyI6bnVsbCwib3duZXJfb2YiOlsib3JnMTEyNTYxMTUiXSwicGVybWlzc2lvbnMiOnsid2VpZ2h0IjoxMDAsInBlcnNvbmEiOlsiQ0xJIl0sInBlcm1pc3Npb24iOm51bGx9fSwiZXhwIjoxNzgxOTM0NzIwLCJpYXQiOjE3NTQ5Nzc4NzEsIm5iZiI6MTc1NDk3Nzg3MSwicHJvdmlkZXJfaW5mbyI6eyJwcm92aWRlcl9uYW1lIjoiaHR0cHM6Ly9hdXRoLnR0ay5jb20vIiwidG9rZW4iOiJleUpoYkdjaU9pSklVekkxTmlJc0luUjVjQ0k2SWtwWFZDSjkuZXlKMWMyVnlTV1FpT2lKVk1EQXhJaXdpWVdOalpYTnpWSGx3WlNJNkltTnNhV1Z1ZENJc0ltWjFiR3hPWVcxbElqb2lSWGhoYlhCc1pTQkRiR2xsYm5RaUxDSnNiMmRwYmxScGJXVWlPaUl5TURJMUxUQTBMVEkxSURFMU9qRXdPak13SWl3aVpYaHdhWEo1VkdsdFpYTjBZVzF3SWpvaU1UYzRNVGt6TkRjeU1DSXNJazl5WkdWeUlFbEVJam9pVWxaSlV5MHdNekEzTWpBeU5TMHdNREVpZlEuX25mUGxhYVhCS1ZNOUNxeG81eXMyQTdPYktfX1RqZHBuNWg0cUd6VWxzVSJ9fQ.B0rK4k7TLTM1Rn8JTfhsnw9-52wSdHQBqv1ijYBIcz3QtKeSrhrHA9vPHeMfOXu1Rtv4qXk9p3wIM0sfznZDAWb1JWcPYNVM6H1OPuM7ay3bWiY54spktlvLa8MXwcRZVJDLV0PNaQIuvkduAzfVt2trzYP7la4CQjixYkj6katYFcK5Z01jffZDdvdd1anQkZCVE5ovCwMDRcHfSTYTe7Q4SJwoQk46MPXD5RxTBOxUWiQxcK_uVToHgagQOaHWyfnbg5-IT5NrUko24sZZx5Bx23CRTGJfWpk13FBSB2lwdAM9BKflcTT_BUEt81vYQLd7debm5HG6hAQyyDeWrQ

📦 Base64URL Encoded LYIK Token (client):
ZXlKaGJHY2lPaUpTVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBjM01pT2lKb2RIUndjem92TDJ4NWFXc3VZMjl0SWl3aVlYVmtJam9pYUhSMGNITTZMeTlzZVdsckxtTnZiU0lzSW5OMVlpSTZJbFV3TURFaUxDSjFjMlZ5WDIxbGRHRmtZWFJoSWpwN0luVnpaWEpmYVc1bWJ5STZleUoxYzJWeVgybGtJam9pVlRBd01TSXNJbkJvYjI1bFgyNTFiV0psY2lJNmJuVnNiQ3dpWlcxaGFXd2lPbTUxYkd3c0luSnZiR1Z6SWpwYkltTnNhV1Z1ZENKZExDSnlaV3hoZEdsdmJuTm9hWEFpT201MWJHd3NJbTl5WjJGdWFYcGhkR2x2Ymw5cFpDSTZJbTl5WnpFeE1qVTJNVEUxSWl3aVpHbHpjR3hoZVY5dVlXMWxJam9pUlhoaGJYQnNaU0JEYkdsbGJuUWlMQ0p3YkhWbmFXNWZjSEp2ZG1sa1pYSWlPaUpvZEhSd2N6b3ZMMkYxZEdndWRIUnJMbU52YlM4aWZTd2lkWE5sY2w5eVpXeGhkR2x2Ym5Ob2FYQmZhVzVtYnlJNmJuVnNiQ3dpYjNkdVpYSmZiMllpT2xzaWIzSm5NVEV5TlRZeE1UVWlYU3dpY0dWeWJXbHpjMmx2Ym5NaU9uc2lkMlZwWjJoMElqb3hNREFzSW5CbGNuTnZibUVpT2xzaVEweEpJbDBzSW5CbGNtMXBjM05wYjI0aU9tNTFiR3g5ZlN3aVpYaHdJam94TnpneE9UTTBOekl3TENKcFlYUWlPakUzTlRRNU56YzROekVzSW01aVppSTZNVGMxTkRrM056ZzNNU3dpY0hKdmRtbGtaWEpmYVc1bWJ5STZleUp3Y205MmFXUmxjbDl1WVcxbElqb2lhSFIwY0hNNkx5OWhkWFJvTG5SMGF5NWpiMjB2SWl3aWRHOXJaVzRpT2lKbGVVcG9Za2RqYVU5cFNrbFZla2t4VG1sSmMwbHVValZqUTBrMlNXdHdXRlpEU2prdVpYbEtNV015Vm5sVFYxRnBUMmxLVmsxRVFYaEphWGRwV1ZkT2FscFlUbnBXU0d4M1dsTkpOa2x0VG5OaFYxWjFaRU5KYzBsdFdqRmlSM2hQV1ZjeGJFbHFiMmxTV0dob1lsaENjMXBUUWtSaVIyeHNZbTVSYVV4RFNuTmlNbVJ3WW14U2NHSlhWV2xQYVVsNVRVUkpNVXhVUVRCTVZFa3hTVVJGTVU5cVJYZFBhazEzU1dsM2FWcFlhSGRoV0VvMVZrZHNkRnBZVGpCWlZ6RjNTV3B2YVUxVVl6Uk5WR3Q2VGtSamVVMURTWE5KYXpsNVdrZFdlVWxGYkVWSmFtOXBWV3hhU2xWNU1IZE5la0V6VFdwQmVVNVRNSGROUkVWcFpsRXVYMjVtVUd4aFlWaENTMVpOT1VOeGVHODFlWE15UVRkUFlrdGZYMVJxWkhCdU5XZzBjVWQ2Vld4elZTSjlmUS5CMHJLNGs3VExUTTFSbjhKVGZoc253OS01MndTZEhRQnF2MWlqWUJJY3ozUXRLZVNyaHJIQTl2UEhlTWZPWHUxUnR2NHFYazlwM3dJTTBzZnpuWkRBV2IxSldjUFlOVk02SDFPUHVNN2F5M2JXaVk1NHNwa3RsdkxhOE1Yd2NSWlZKRExWMFBOYVFJdXZrZHVBemZWdDJ0cnpZUDdsYTRDUWppeFlrajZrYXRZRmNLNVowMWpmZlpEZHZkZDFhblFrWkNWRTVvdkN3TURSY0hmU1RZVGU3UTRTSndvUWs0Nk1QWEQ1UnhUQk94VVdpUXhjS191VlRvSGdhZ1FPYUhXeWZuYmc1LUlUNU5yVWtvMjRzWlp4NUJ4MjNDUlRHSmZXcGsxM0ZCU0IybHdkQU05QktmbGNUVF9CVUV0ODF2WVFMZDdkZWJtNUhHNmhBUXl5RGVXclE

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
  "Order ID": "RVIS-03072025-003"
}

🔑 LYIK Token (maker):
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2x5aWsuY29tIiwiYXVkIjoiaHR0cHM6Ly9seWlrLmNvbSIsInN1YiI6IlUwMDIiLCJ1c2VyX21ldGFkYXRhIjp7InVzZXJfaW5mbyI6eyJ1c2VyX2lkIjoiVTAwMiIsInBob25lX251bWJlciI6bnVsbCwiZW1haWwiOm51bGwsInJvbGVzIjpbIm1ha2VyIl0sInJlbGF0aW9uc2hpcCI6bnVsbCwib3JnYW5pemF0aW9uX2lkIjoib3JnMTEyNTYxMTUiLCJkaXNwbGF5X25hbWUiOiJFeGFtcGxlIE1ha2VyIiwicGx1Z2luX3Byb3ZpZGVyIjoiaHR0cHM6Ly9hdXRoLnR0ay5jb20vIn0sInVzZXJfcmVsYXRpb25zaGlwX2luZm8iOm51bGwsIm93bmVyX29mIjpbIm9yZzExMjU2MTE1Il0sInBlcm1pc3Npb25zIjp7IndlaWdodCI6MTAwLCJwZXJzb25hIjpbIk1LUiJdLCJwZXJtaXNzaW9uIjpudWxsfX0sImV4cCI6MTc4MTkzNDcyMCwiaWF0IjoxNzU0OTc3ODcxLCJuYmYiOjE3NTQ5Nzc4NzEsInByb3ZpZGVyX2luZm8iOnsicHJvdmlkZXJfbmFtZSI6Imh0dHBzOi8vYXV0aC50dGsuY29tLyIsInRva2VuIjoiZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SjFjMlZ5U1dRaU9pSlZNREF5SWl3aVlXTmpaWE56Vkhsd1pTSTZJbTFoYTJWeUlpd2lablZzYkU1aGJXVWlPaUpGZUdGdGNHeGxJRTFoYTJWeUlpd2liRzluYVc1VWFXMWxJam9pTWpBeU5TMHdOQzB5TlNBeE5Ub3hNRG96TUNJc0ltVjRjR2x5ZVZScGJXVnpkR0Z0Y0NJNklqRTNPREU1TXpRM01qQWlMQ0pQY21SbGNpQkpSQ0k2SWxKV1NWTXRNRE13TnpJd01qVXRNREF4SW4wLkVNMGVzcjRqRGhKazdSV3diSkNEc1U0RlItRm9Qc056VmpKVzhpY1ByeW8ifX0.azxFQsPFt9d47VZ4Ow064sZLA_S3X1m8NIkSAmZ1M1OTg5D7RxMpSJgiKP2uJ2h8dwgSlFCD1krn7SGN4TvN0FuAO9QjDw23PvWhleemFZIXrvOWXMfipu7DOYf9xqcqGglon43zS26YE4Ep8kcApHWLHsn6naBb-5pxBRy8oBTEINap1JigmOV1wQXplo5KTBPF9jmwTGZl5h4pUsWwSetFSgT1pPHQUtwKWfPsAKX9WyB5ibYpNfQXhvKc7rE-uFLWgX9ta7PssrWmfjdjo6DVoO2VZs3AGhOrm_kaI19zek3A2i-WCfbxDL68fG5W7U91C3GD-yoDQEX74eYF_A

📦 Base64URL Encoded LYIK Token (maker):
ZXlKaGJHY2lPaUpTVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBjM01pT2lKb2RIUndjem92TDJ4NWFXc3VZMjl0SWl3aVlYVmtJam9pYUhSMGNITTZMeTlzZVdsckxtTnZiU0lzSW5OMVlpSTZJbFV3TURJaUxDSjFjMlZ5WDIxbGRHRmtZWFJoSWpwN0luVnpaWEpmYVc1bWJ5STZleUoxYzJWeVgybGtJam9pVlRBd01pSXNJbkJvYjI1bFgyNTFiV0psY2lJNmJuVnNiQ3dpWlcxaGFXd2lPbTUxYkd3c0luSnZiR1Z6SWpwYkltMWhhMlZ5SWwwc0luSmxiR0YwYVc5dWMyaHBjQ0k2Ym5Wc2JDd2liM0puWVc1cGVtRjBhVzl1WDJsa0lqb2liM0puTVRFeU5UWXhNVFVpTENKa2FYTndiR0Y1WDI1aGJXVWlPaUpGZUdGdGNHeGxJRTFoYTJWeUlpd2ljR3gxWjJsdVgzQnliM1pwWkdWeUlqb2lhSFIwY0hNNkx5OWhkWFJvTG5SMGF5NWpiMjB2SW4wc0luVnpaWEpmY21Wc1lYUnBiMjV6YUdsd1gybHVabThpT201MWJHd3NJbTkzYm1WeVgyOW1JanBiSW05eVp6RXhNalUyTVRFMUlsMHNJbkJsY20xcGMzTnBiMjV6SWpwN0luZGxhV2RvZENJNk1UQXdMQ0p3WlhKemIyNWhJanBiSWsxTFVpSmRMQ0p3WlhKdGFYTnphVzl1SWpwdWRXeHNmWDBzSW1WNGNDSTZNVGM0TVRrek5EY3lNQ3dpYVdGMElqb3hOelUwT1RjM09EY3hMQ0p1WW1ZaU9qRTNOVFE1TnpjNE56RXNJbkJ5YjNacFpHVnlYMmx1Wm04aU9uc2ljSEp2ZG1sa1pYSmZibUZ0WlNJNkltaDBkSEJ6T2k4dllYVjBhQzUwZEdzdVkyOXRMeUlzSW5SdmEyVnVJam9pWlhsS2FHSkhZMmxQYVVwSlZYcEpNVTVwU1hOSmJsSTFZME5KTmtscmNGaFdRMG81TG1WNVNqRmpNbFo1VTFkUmFVOXBTbFpOUkVGNVNXbDNhVmxYVG1wYVdFNTZWa2hzZDFwVFNUWkpiVEZvWVRKV2VVbHBkMmxhYmxaellrVTFhR0pYVldsUGFVcEdaVWRHZEdOSGVHeEpSVEZvWVRKV2VVbHBkMmxpUnpsdVlWYzFWV0ZYTVd4SmFtOXBUV3BCZVU1VE1IZE9RekI1VGxOQmVFNVViM2hOUkc5NlRVTkpjMGx0VmpSalIyeDVaVlpTY0dKWFZucGtSMFowWTBOSk5rbHFSVE5QUkVVMVRYcFJNMDFxUVdsTVEwcFFZMjFTYkdOcFFrcFNRMGsyU1d4S1YxTldUWFJOUkUxM1RucEpkMDFxVlhSTlJFRjRTVzR3TGtWTk1HVnpjalJxUkdoS2F6ZFNWM2RpU2tORWMxVTBSbEl0Um05UWMwNTZWbXBLVnpocFkxQnllVzhpZlgwLmF6eEZRc1BGdDlkNDdWWjRPdzA2NHNaTEFfUzNYMW04TklrU0FtWjFNMU9UZzVEN1J4TXBTSmdpS1AydUoyaDhkd2dTbEZDRDFrcm43U0dONFR2TjBGdUFPOVFqRHcyM1B2V2hsZWVtRlpJWHJ2T1dYTWZpcHU3RE9ZZjl4cWNxR2dsb240M3pTMjZZRTRFcDhrY0FwSFdMSHNuNm5hQmItNXB4QlJ5OG9CVEVJTmFwMUppZ21PVjF3UVhwbG81S1RCUEY5am13VEdabDVoNHBVc1d3U2V0RlNnVDFwUEhRVXR3S1dmUHNBS1g5V3lCNWliWXBOZlFYaHZLYzdyRS11RkxXZ1g5dGE3UHNzcldtZmpkam82RFZvTzJWWnMzQUdoT3JtX2thSTE5emVrM0EyaS1XQ2ZieERMNjhmRzVXN1U5MUMzR0QteW9EUUVYNzRlWUZfQQ

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
  "Order ID": "RVIS-03072025-003"
}

🔑 LYIK Token (checker):
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2x5aWsuY29tIiwiYXVkIjoiaHR0cHM6Ly9seWlrLmNvbSIsInN1YiI6IlUwMDMiLCJ1c2VyX21ldGFkYXRhIjp7InVzZXJfaW5mbyI6eyJ1c2VyX2lkIjoiVTAwMyIsInBob25lX251bWJlciI6bnVsbCwiZW1haWwiOm51bGwsInJvbGVzIjpbImNoZWNrZXIiXSwicmVsYXRpb25zaGlwIjpudWxsLCJvcmdhbml6YXRpb25faWQiOiJvcmcxMTI1NjExNSIsImRpc3BsYXlfbmFtZSI6IkV4YW1wbGUgQ2hlY2tlciIsInBsdWdpbl9wcm92aWRlciI6Imh0dHBzOi8vYXV0aC50dGsuY29tLyJ9LCJ1c2VyX3JlbGF0aW9uc2hpcF9pbmZvIjpudWxsLCJvd25lcl9vZiI6WyJvcmcxMTI1NjExNSJdLCJwZXJtaXNzaW9ucyI6eyJ3ZWlnaHQiOjEwMCwicGVyc29uYSI6WyJQQVJFTlQiLCJDS1IiXSwicGVybWlzc2lvbiI6bnVsbH19LCJleHAiOjE3ODE5MzQ3MjAsImlhdCI6MTc1NDk3Nzg3MSwibmJmIjoxNzU0OTc3ODcxLCJwcm92aWRlcl9pbmZvIjp7InByb3ZpZGVyX25hbWUiOiJodHRwczovL2F1dGgudHRrLmNvbS8iLCJ0b2tlbiI6ImV5SmhiR2NpT2lKSVV6STFOaUlzSW5SNWNDSTZJa3BYVkNKOS5leUoxYzJWeVNXUWlPaUpWTURBeklpd2lZV05qWlhOelZIbHdaU0k2SW1Ob1pXTnJaWElpTENKbWRXeHNUbUZ0WlNJNklrVjRZVzF3YkdVZ1EyaGxZMnRsY2lJc0lteHZaMmx1VkdsdFpTSTZJakl3TWpVdE1EUXRNalVnTVRVNk1UQTZNekFpTENKbGVIQnBjbmxVYVcxbGMzUmhiWEFpT2lJeE56Z3hPVE0wTnpJd0lpd2lUM0prWlhJZ1NVUWlPaUpTVmtsVExUQXpNRGN5TURJMUxUQXdNU0o5LklrTW5FX0NSVHNJN3EwZ3JrcHIzcGNkR3V5YlJrdHRtMGRWNm4xNlFEMzAifX0.CSzcxPpSaCYL1NqIlAsjRb7RJmObTQqFIRVcABeYNKSmT9ylM2XQfnP7aapL25Q5i4BC1_u-Nsv0YVrRk1IASwmOOMbetnBA0LAUPflNIYHuU6vCvAdP4F0rTlHqOrpuD9FyzWIx7ggk9MqHL_-LOEYLhmoGGrDS-FaNDvydvAKYtfyDnRwXx2Jb46_wN9UcYcrLZB_YaH_aPCUx862yjwOAdlLflteEveuCpcvTaYgb92EYew6yOYX28F84_9GDR0Ym0SleGlW_MT6vKgO-a-1hAa113gubcl3lbziI3zW7nN8BBz6OmYo4swtF6I3wkB3PNg_T3fsOzv7YbZ0HOg

📦 Base64URL Encoded LYIK Token (checker):
ZXlKaGJHY2lPaUpTVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBjM01pT2lKb2RIUndjem92TDJ4NWFXc3VZMjl0SWl3aVlYVmtJam9pYUhSMGNITTZMeTlzZVdsckxtTnZiU0lzSW5OMVlpSTZJbFV3TURNaUxDSjFjMlZ5WDIxbGRHRmtZWFJoSWpwN0luVnpaWEpmYVc1bWJ5STZleUoxYzJWeVgybGtJam9pVlRBd015SXNJbkJvYjI1bFgyNTFiV0psY2lJNmJuVnNiQ3dpWlcxaGFXd2lPbTUxYkd3c0luSnZiR1Z6SWpwYkltTm9aV05yWlhJaVhTd2ljbVZzWVhScGIyNXphR2x3SWpwdWRXeHNMQ0p2Y21kaGJtbDZZWFJwYjI1ZmFXUWlPaUp2Y21jeE1USTFOakV4TlNJc0ltUnBjM0JzWVhsZmJtRnRaU0k2SWtWNFlXMXdiR1VnUTJobFkydGxjaUlzSW5Cc2RXZHBibDl3Y205MmFXUmxjaUk2SW1oMGRIQnpPaTh2WVhWMGFDNTBkR3N1WTI5dEx5SjlMQ0oxYzJWeVgzSmxiR0YwYVc5dWMyaHBjRjlwYm1adklqcHVkV3hzTENKdmQyNWxjbDl2WmlJNld5SnZjbWN4TVRJMU5qRXhOU0pkTENKd1pYSnRhWE56YVc5dWN5STZleUozWldsbmFIUWlPakV3TUN3aWNHVnljMjl1WVNJNld5SlFRVkpGVGxRaUxDSkRTMUlpWFN3aWNHVnliV2x6YzJsdmJpSTZiblZzYkgxOUxDSmxlSEFpT2pFM09ERTVNelEzTWpBc0ltbGhkQ0k2TVRjMU5EazNOemczTVN3aWJtSm1Jam94TnpVME9UYzNPRGN4TENKd2NtOTJhV1JsY2w5cGJtWnZJanA3SW5CeWIzWnBaR1Z5WDI1aGJXVWlPaUpvZEhSd2N6b3ZMMkYxZEdndWRIUnJMbU52YlM4aUxDSjBiMnRsYmlJNkltVjVTbWhpUjJOcFQybEtTVlY2U1RGT2FVbHpTVzVTTldORFNUWkphM0JZVmtOS09TNWxlVW94WXpKV2VWTlhVV2xQYVVwV1RVUkJla2xwZDJsWlYwNXFXbGhPZWxaSWJIZGFVMGsyU1cxT2IxcFhUbkphV0VscFRFTktiV1JYZUhOVWJVWjBXbE5KTmtsclZqUlpWekYzWWtkVloxRXlhR3haTW5Sc1kybEpjMGx0ZUhaYU1teDFWa2RzZEZwVFNUWkpha2wzVFdwVmRFMUVVWFJOYWxWblRWUlZOazFVUVRaTmVrRnBURU5LYkdWSVFuQmpibXhWWVZjeGJHTXpVbWhpV0VGcFQybEplRTU2WjNoUFZFMHdUbnBKZDBscGQybFVNMHByV2xoSloxTlZVV2xQYVVwVFZtdHNWRXhVUVhwTlJHTjVUVVJKTVV4VVFYZE5VMG81TGtsclRXNUZYME5TVkhOSk4zRXdaM0pyY0hJemNHTmtSM1Y1WWxKcmRIUnRNR1JXTm00eE5sRkVNekFpZlgwLkNTemN4UHBTYUNZTDFOcUlsQXNqUmI3UkptT2JUUXFGSVJWY0FCZVlOS1NtVDl5bE0yWFFmblA3YWFwTDI1UTVpNEJDMV91LU5zdjBZVnJSazFJQVN3bU9PTWJldG5CQTBMQVVQZmxOSVlIdVU2dkN2QWRQNEYwclRsSHFPcnB1RDlGeXpXSXg3Z2drOU1xSExfLUxPRVlMaG1vR0dyRFMtRmFORHZ5ZHZBS1l0ZnlEblJ3WHgySmI0Nl93TjlVY1ljckxaQl9ZYUhfYVBDVXg4NjJ5andPQWRsTGZsdGVFdmV1Q3BjdlRhWWdiOTJFWWV3NnlPWVgyOEY4NF85R0RSMFltMFNsZUdsV19NVDZ2S2dPLWEtMWhBYTExM2d1YmNsM2xiemlJM3pXN25OOEJCejZPbVlvNHN3dEY2STN3a0IzUE5nX1QzZnNPenY3WWJaMEhPZw

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
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2x5aWsuY29tIiwiYXVkIjoiaHR0cHM6Ly9seWlrLmNvbSIsInN1YiI6IlUwMDQiLCJ1c2VyX21ldGFkYXRhIjp7InVzZXJfaW5mbyI6eyJ1c2VyX2lkIjoiVTAwNCIsInBob25lX251bWJlciI6bnVsbCwiZW1haWwiOm51bGwsInJvbGVzIjpbImFkbWluIl0sInJlbGF0aW9uc2hpcCI6bnVsbCwib3JnYW5pemF0aW9uX2lkIjoib3JnMTEyNTYxMTUiLCJkaXNwbGF5X25hbWUiOiJEZWJhc2lzaCBDbGllbnQiLCJwbHVnaW5fcHJvdmlkZXIiOiJodHRwczovL2F1dGgudHRrLmNvbS8ifSwidXNlcl9yZWxhdGlvbnNoaXBfaW5mbyI6bnVsbCwib3duZXJfb2YiOlsib3JnMTEyNTYxMTUiXSwicGVybWlzc2lvbnMiOnsid2VpZ2h0IjoxMDAwMCwicGVyc29uYSI6WyJBRE1JTiIsIkNSRUFUT1IiXSwicGVybWlzc2lvbiI6bnVsbH19LCJleHAiOjE3ODE5MzQ3MjAsImlhdCI6MTc1NDk3Nzg3MSwibmJmIjoxNzU0OTc3ODcxLCJwcm92aWRlcl9pbmZvIjp7InByb3ZpZGVyX25hbWUiOiJodHRwczovL2F1dGgudHRrLmNvbS8iLCJ0b2tlbiI6ImV5SmhiR2NpT2lKSVV6STFOaUlzSW5SNWNDSTZJa3BYVkNKOS5leUoxYzJWeVNXUWlPaUpWTURBMElpd2lZV05qWlhOelZIbHdaU0k2SW1Ga2JXbHVJaXdpWm5Wc2JFNWhiV1VpT2lKRVpXSmhjMmx6YUNCRGJHbGxiblFpTENKc2IyZHBibFJwYldVaU9pSXlNREkxTFRBMExUSTFJREUxT2pFd09qTXdJaXdpWlhod2FYSjVWR2x0WlhOMFlXMXdJam9pTVRjNE1Ua3pORGN5TUNKOS5vaUV5Q1FydnFHTllmX1J1MjFKQTVuUlJSTXAydnRVZ3pjeTFXTXNCLUtNIn19.PThv0X8ewbk_yTGaTnZeJhygS1fr8DA66mKKGAzCLheDTxzgUqIgVjVrkzc_SrIvx3x6tAsdY5TLXgKP4H39AdSLqDfIkaE28EDg3Rz4TEwh6VRBTe1gFqEHwBln6NKUv7_5FjT-2AWEGCTM3Mi1rWGkl-PA2pAAKn88ylgg6IxHaFcFxMMQOAX2pnJUWBhUxO-VzwKsVTiNvxAnYsFgzykXb_bTtL0utLeul9gsFGzoauodEdU46HYYoudqtz_cxscDV0Ba3GA2Oy8Ghwks-qmjWvBnHxDS6qDYoo5t38b1XSkdvy9STO8qZRQKd8tWuJAosZy6xYfUElc0GnpgEQ

📦 Base64URL Encoded LYIK Token (admin):
ZXlKaGJHY2lPaUpTVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBjM01pT2lKb2RIUndjem92TDJ4NWFXc3VZMjl0SWl3aVlYVmtJam9pYUhSMGNITTZMeTlzZVdsckxtTnZiU0lzSW5OMVlpSTZJbFV3TURRaUxDSjFjMlZ5WDIxbGRHRmtZWFJoSWpwN0luVnpaWEpmYVc1bWJ5STZleUoxYzJWeVgybGtJam9pVlRBd05DSXNJbkJvYjI1bFgyNTFiV0psY2lJNmJuVnNiQ3dpWlcxaGFXd2lPbTUxYkd3c0luSnZiR1Z6SWpwYkltRmtiV2x1SWwwc0luSmxiR0YwYVc5dWMyaHBjQ0k2Ym5Wc2JDd2liM0puWVc1cGVtRjBhVzl1WDJsa0lqb2liM0puTVRFeU5UWXhNVFVpTENKa2FYTndiR0Y1WDI1aGJXVWlPaUpFWldKaGMybHphQ0JEYkdsbGJuUWlMQ0p3YkhWbmFXNWZjSEp2ZG1sa1pYSWlPaUpvZEhSd2N6b3ZMMkYxZEdndWRIUnJMbU52YlM4aWZTd2lkWE5sY2w5eVpXeGhkR2x2Ym5Ob2FYQmZhVzVtYnlJNmJuVnNiQ3dpYjNkdVpYSmZiMllpT2xzaWIzSm5NVEV5TlRZeE1UVWlYU3dpY0dWeWJXbHpjMmx2Ym5NaU9uc2lkMlZwWjJoMElqb3hNREF3TUN3aWNHVnljMjl1WVNJNld5SkJSRTFKVGlJc0lrTlNSVUZVVDFJaVhTd2ljR1Z5YldsemMybHZiaUk2Ym5Wc2JIMTlMQ0psZUhBaU9qRTNPREU1TXpRM01qQXNJbWxoZENJNk1UYzFORGszTnpnM01Td2libUptSWpveE56VTBPVGMzT0RjeExDSndjbTkyYVdSbGNsOXBibVp2SWpwN0luQnliM1pwWkdWeVgyNWhiV1VpT2lKb2RIUndjem92TDJGMWRHZ3VkSFJyTG1OdmJTOGlMQ0owYjJ0bGJpSTZJbVY1U21oaVIyTnBUMmxLU1ZWNlNURk9hVWx6U1c1U05XTkRTVFpKYTNCWVZrTktPUzVsZVVveFl6SldlVk5YVVdsUGFVcFdUVVJCTUVscGQybFpWMDVxV2xoT2VsWkliSGRhVTBrMlNXMUdhMkpYYkhWSmFYZHBXbTVXYzJKRk5XaGlWMVZwVDJsS1JWcFhTbWhqTW14NllVTkNSR0pIYkd4aWJsRnBURU5LYzJJeVpIQmliRkp3WWxkVmFVOXBTWGxOUkVreFRGUkJNRXhVU1RGSlJFVXhUMnBGZDA5cVRYZEphWGRwV2xob2QyRllTalZXUjJ4MFdsaE9NRmxYTVhkSmFtOXBUVlJqTkUxVWEzcE9SR041VFVOS09TNXZhVVY1UTFGeWRuRkhUbGxtWDFKMU1qRktRVFZ1VWxKU1RYQXlkblJWWjNwamVURlhUWE5DTFV0TkluMTkuUFRodjBYOGV3YmtfeVRHYVRuWmVKaHlnUzFmcjhEQTY2bUtLR0F6Q0xoZURUeHpnVXFJZ1ZqVnJremNfU3JJdngzeDZ0QXNkWTVUTFhnS1A0SDM5QWRTTHFEZklrYUUyOEVEZzNSejRURXdoNlZSQlRlMWdGcUVId0JsbjZOS1V2N181RmpULTJBV0VHQ1RNM01pMXJXR2tsLVBBMnBBQUtuODh5bGdnNkl4SGFGY0Z4TU1RT0FYMnBuSlVXQmhVeE8tVnp3S3NWVGlOdnhBbllzRmd6eWtYYl9iVHRMMHV0TGV1bDlnc0ZHem9hdW9kRWRVNDZIWVlvdWRxdHpfY3hzY0RWMEJhM0dBMk95OEdod2tzLXFtald2Qm5IeERTNnFEWW9vNXQzOGIxWFNrZHZ5OVNUTzhxWlJRS2Q4dFd1SkFvc1p5NnhZZlVFbGMwR25wZ0VR
(.lsvenv) akhilbabu@Akhils-MacBook-Pro lyik_ttk % 
'''