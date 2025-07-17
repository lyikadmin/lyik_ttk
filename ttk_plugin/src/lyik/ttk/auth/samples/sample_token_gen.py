import datetime
import jwt

TTK_TOKEN_SECRET = "BmThdDKu4lPOFiiqwHG1GQVm7iGeVIqALcqwJDM6VySzVdOwZ1UMoylzwhIDgXl6"


payload = {
    "userId": "U001",
    "accessType": "client",
    "fullName": "Debasish Client",
    "loginTime": "2025-04-25 15:10:30",
    "expiryTimestamp": "1781934720",
    "Order ID": "RVIS-03072025-001",
    # "relationship": ["user_xyz", "user_1222"],
    # "iss": "https://auth.ttk.com/",
    # "aud": "https://lyik.com",
}

# Admin token payload
# payload = {
#     "userId": "U001",
#     "accessType": "admin",
#     "fullName": "Debasish Client",
#     "loginTime": "2025-04-25 15:10:30",
#     "expiryTimestamp": "1781934720",
#     # "Order ID": "RVIS-03072025-001",
#     # "relationship": ["user_xyz", "user_1222"],
#     # "iss": "https://auth.ttk.com/",
#     # "aud": "https://lyik.com",
# }

token = jwt.encode(
    payload,
    TTK_TOKEN_SECRET,
    algorithm="HS256",
)

# If token is bytes, decode it to str
if isinstance(token, bytes):
    token = token.decode("utf-8")

print("🔐 JWT Token:")
print(token)

deco = jwt.decode(
    token,
    TTK_TOKEN_SECRET,
    algorithms=["HS256"],
)

print(deco)
