# ## This file contains all the Environment Variables required by Base LYIK API to work. This contains some dummy values. Users are expected to change this to credentials they have.

# Over riding the default config
LOG_LEVEL="TPL_LOG_LEVEL"
# Add your LYIK License Key
LICENSE_KEY="ieVieCREzfaba789dtJ3Yt0w89ZpnbPOPkAPohx99J20eG0K"

# Api domain
API_DOMAIN="TPL_BASEURL/api" # REPLACE WITH YOUR DOMAIN


# Databse Connection URL
DB_CONN_URL=TPL_MONGODB_SERVER # ADD YOUR DATABASE CONNECTION URL HERE

# Add your api token for Surepass OCR api, if you need OVD OCR services
SUREPASS_TOKEN=""


# Add your Digilocker credentials of UIDAI, for fetching data directly from user's digilocker account. The following credentials are
DIGI_CLIENT_ID="TPL_DIGILOCKER_CLIENT_ID"
DIGI_CLIENT_SECRET="TPL_DIGILOCKER_CLIENT_SECRET"
DIGI_REDIRECT_URI="TPL_BASEURL/digi_redirect"
DIGI_CODE_VERIFIER="Packmyboxwithfivedozenliquorjugs-0020002"

# Add your SMS Message Template. Note, {otp} will be replaced with the actual otp.
OTP_MESSAGE_TEMPLATE="Way2wealth Ekyc registration process requests you to use {otp} as the OTP to validate your mobile number. Way2Wealthy"


# If you're using ValueFirst SMS services, add the credentials for Value First SMS Service
VALUEFIRST_USERNAME="Waytohttp1"
VALUEFIRST_PASSWORD="wayto123"
VALUEFIRST_SENDER="WTWADV"

# If you're using TextLocal SMS services, add credentials for SMS Services
TEXTLOCAL_SENDER=""
TEXTLOCAL_API_KEY=""

# To use email services from SENDGRID, add the API credentials
SENDGRID_API_KEY=""
SENDGRID_SENDER_EMAIL="no-reply@lyik.com"


# Plugin MAX Weight
PLUGIN_MAX_WEIGHT="TPL_PLUGIN_MAX_WEIGHT" # change this to restrict higher weighted plugins!

# Add your KRA credentials
KRA_AUTH_TOKEN='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJlMTM5ODI5MjMwMWU0MTNkYjljYmNhYmRlM2JmNGJkNiIsInVuaXF1ZV9uYW1lIjoiV0VCV0FZMldFQUxUSEJST0tFUlMiLCJuYmYiOjE3MzYzOTU0NTUsImV4cCI6MTczNjQ4MTg1NSwiaWF0IjoxNzM2Mzk1NDU1LCJpc3MiOiJodHRwOi8vbG9jYWxob3N0IiwiYXVkIjoiaHR0cDovL2xvY2FsaG9zdCJ9.BRjg5huIZmstcN_UBSC6_9uXVqooyyL4ouTQKx96YRk'
KRA_AUTH_TOKEN_VALIDITY='20250110093415'
KRA_AUTH_API_KEY="TPL_KRA_API_KEY"
KRA_AUTH_API_USERNAME="TPL_KRA_API_USERNAME"
POSCODE="TPL_KRA_POSCODE"
KRA_AUTH_API_PASSWORD="TPL_KRA_API_PASSWORD"
KRA_AES_KEY="TPL_KRA_AES_KEY"
SFTP_USERNAME="TPL_KRA_SFTP_USERNAME"
SFTP_PASSWORD="TPL_KRA_SFTP_PASSWORD"

# Add credentials for NSDL DEMAT
NSDL_REQUESTOR_ID="IN303077"
NSDL_TRANSACTION_TYPE="IDD"
NSDL_REQUESTOR="IN303077-TEST"
NSDLREQUEST_REF="045415349158"

# Add credentials for UCC Upload
UCC_NSE_USERNAME='11502'
UCC_NSE_PASSWORD='Lyik@W2w'
UCC_BSE_MEMBER_CODE="3117"
UCC_BSE_USER_ID='ABC123'#"KYCREG"
UCC_BSE_PASSWORD="W2w@1234"
UCC_BSE_PUBLIC_KEY_FILE='ucc_bse_public_key.pem'

# Add Creds for NTT Atom
NTT_MERCHANT_ID="TPL_NTT_MERCHANT_ID"
NTT_MCC="TPL_NTT_MCC"
NTT_TXN_PASSWORD="TPL_NTT_TXN_PASSWORD"
NTT_REQ_ENC_KEY="TPL_NTT_REQ_ENC_KEY"
NTT_RESP_ENC_KEY="TPL_NTT_RESP_ENC_KEY"
NTT_REQ_HASH_KEY="TPL_NTT_REQ_HASH_KEY"
NTT_RESP_HASH_KEY="TPL_NTT_RESP_HASH_KEY"

# Add Protean Esign credentials
WEB_FORMFILLING_ESIGN_ENDPOINT="TPL_BASEURL/esign/" # Here just replace the domain with your formfilling domain, example https://your-domain.com/esign/
PROTEAN_ESIGN_PFX_PASSWORD='Globa1*w@w&#'
PROTEAN_ESIGN_PFX_ALIAS='te-97bb267c-8bae-42fe-a13c-0db609f90b34'
PROTEAN_ESIGN_PFX_ASP_ID='TPL_PROTEAN_ASP_ID'
PROTEAN_ESIGN_PFX='w2w_protean.pfx' # thid file need to be added to plugin_files directory

# Protean PAN Verification credentials
PROTEAN_PAN_USER_ID="TPL_PROTEAN_OPV_USER_ID"
PROTEAN_PAN_PFX='w2w_protean.pfx'
PROTEAN_PAN_PFX_PASSWORD='Globa1*w@w&#'

# mount path for the cred files
CRED_FILES_MOUNT_PATH='/lyik/certificate'
LYIK_ROOT_PATH='/lyik'

# path for plugin files
LINKED_RECORD_FILE='linked_record.json'

APPLICATION_NUMBER_SEQUENCE_START=130000