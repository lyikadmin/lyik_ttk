{
  "COMPANY_NAME": "TTK",
  "APP_MODE": "DEBUG",
  "SECRETS": {
    "ENCRYPTION_DECRYPTION_KEY": "your-encryption-key"
  },
  "API_BASE_URL": "TPL_BASEURL/api",
  "API_BASE_URL_": "TPL_BASEURL/api",
  "WHATSAPP_URL":"TPL_TTK_API_BASE_URLwhatsApp?token={$user.provider_info.token}&orderNo={$user.provider_info.order_id}",
  "GENERAL_SETTINGS": {
    "SHOW_LOGOUT_BUTTON": true,
    "SHOW_BACK_BUTTON": true,
    "SHOW_VERIFIER_BUTTON": false,
    "SHOW_SIDEBAR": true,
    "DISABLE_SIDEBAR_TOGGLE": true,
    "IS_SIDEBAR_COLLAPSED": true,
    "SHOW_NAVBAR": false,
    "SIZE_LIMIT_MB": 10,
    "SHOW_PROGRESSBAR": true,
    "EXPORT_CSV_BUTTON": true,
    "USE_PERSONA_ONLY_FOR_EDITABILITY": true,
    "SHOW_WHATSAPP_ICON": true
  },
  "DEFAULT_DATA": {
    "TABLE_TITLE":"Visa Applications",
    "ACTION_BUTTON_LABEL":"View Details",
    "VERIFIER_STATUS": {
      "SUCCESS": "Verified",
      "FAILURE": "Verification Failed",
      "INDETERMINATE": "In Review"
    },
    "APPROVAL_STATUS": {
      "APPROVED": "Approved",
      "REJECTED": "Discrepancy",
      "APPROVE_TITLE": "Approve",
      "REJECT_TITLE": "Reject"
    },
    "DIGILOCKER": {
      "DIGILOCKER_CLIENT_ID": "JH168E60B6",
      "DIGILOCKER_CLIENT_SECRET": "bd4f70b64aa14614e37c",
      "DIGILOCKER_CALLBACK_URL": "http://localhost:3030/digi_redirect",
      "DIGILOCKER_CODE_VERIFIER": "1QTIzQ~~tMgU.AVpL6.FF5Hdu4ytsG0~_uv0x7GY5j5g-Z~p7vtuI3KaOPQT7~wVAi",
      "DIGILOCKER_API_PATH": ""
    }
  }
}