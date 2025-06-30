import datetime
import jwt

TTK_TOKEN_SECRET = "BmThdDKu4lPOFiiqwHG1GQVm7iGeVIqALcqwJDM6VySzVdOwZ1UMoylzwhIDgXl6"


payload = {
    "userId": "U_011",
    "accessType": "maker",
    "fullName": "Jhon Doe",
    "loginTime": "2025-04-25 15:10:30",
    "expiryTimestamp": "1781934720",
    "Order ID":  "abc_123"
    # "relationship": ["user_xyz", "user_1222"],
    # "iss": "https://auth.ttk.com/",
    # "aud": "https://lyik.com",
}

token = jwt.encode(
    payload,
    TTK_TOKEN_SECRET,
    algorithm="HS256",
)

# If token is bytes, decode it to str
if isinstance(token, bytes):
    token = token.decode('utf-8')

print("🔐 JWT Token:")
print(token)

deco = jwt.decode(
    token,
    TTK_TOKEN_SECRET,

    algorithms=["HS256"],
)

print(deco)