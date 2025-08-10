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
DIGI_CODE_VERIFIER=""

# Add your SMS Message Template. Note, {otp} will be replaced with the actual otp.
OTP_MESSAGE_TEMPLATE="TTK registration process requests you to use {otp} as the OTP to validate your mobile number."


# If you're using ValueFirst SMS services, add the credentials for Value First SMS Service
VALUEFIRST_USERNAME=""
VALUEFIRST_PASSWORD=""
VALUEFIRST_SENDER=""

# If you're using TextLocal SMS services, add credentials for SMS Services
TEXTLOCAL_SENDER=""
TEXTLOCAL_API_KEY=""

# To use email services from SENDGRID, add the API credentials
SENDGRID_API_KEY=""
SENDGRID_SENDER_EMAIL="no-reply@lyik.com"


# Plugin MAX Weight
PLUGIN_MAX_WEIGHT="TPL_PLUGIN_MAX_WEIGHT" # change this to restrict higher weighted plugins!

# Add your KRA credentials
KRA_AUTH_TOKEN=''
KRA_AUTH_TOKEN_VALIDITY=''
KRA_AUTH_API_KEY="TPL_KRA_API_KEY"
KRA_AUTH_API_USERNAME="TPL_KRA_API_USERNAME"
POSCODE="TPL_KRA_POSCODE"
KRA_AUTH_API_PASSWORD="TPL_KRA_API_PASSWORD"
KRA_AES_KEY="TPL_KRA_AES_KEY"
SFTP_USERNAME="TPL_KRA_SFTP_USERNAME"
SFTP_PASSWORD="TPL_KRA_SFTP_PASSWORD"

# Add credentials for NSDL DEMAT
NSDL_REQUESTOR_ID=""
NSDL_TRANSACTION_TYPE=""
NSDL_REQUESTOR=""
NSDLREQUEST_REF=""
NSDL_PEM_FILE_PATH=""
NSDL_UAT_ENABLED=""

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
PROTEAN_ESIGN_PFX_PASSWORD=''
PROTEAN_ESIGN_PFX_ALIAS=''
PROTEAN_ESIGN_PFX_ASP_ID='TPL_PROTEAN_ASP_ID'
PROTEAN_ESIGN_PFX='' # thid file need to be added to plugin_files directory

# Protean PAN Verification credentials
PROTEAN_PAN_USER_ID="TPL_PROTEAN_OPV_USER_ID"
PROTEAN_PAN_PFX=''
PROTEAN_PAN_PFX_PASSWORD=''

# mount path for the cred files
CRED_FILES_MOUNT_PATH='/lyik/certificate'
LYIK_ROOT_PATH='/lyik'

# path for plugin files
LINKED_RECORD_FILE='linked_record.json'

APPLICATION_NUMBER_SEQUENCE_START=130000

# Payment
FORM_FILLING_PORTAL_ENDPOINT="TPL_SPA_DOMAIN_URL"
PAYMENT_SUCCESS_ROUTE="/success"
PAYMENT_FAILURE_ROUTE="/failure"
PAYMENT_GATEWAY_NAME="TPL_PAYMENT_GATEWAY_NAME"
