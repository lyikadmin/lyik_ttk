import apluggy as pluggy
from lyikpluginmanager import (
    ContextModel,
    getProjectName,
    Operation,
    OperationsListResponseModel,
    OperationsListSpec,
    GenericFormRecordModel,
    PluginException,
)
from typing_extensions import Annotated, Doc
from typing import List
import jwt
from enum import Enum
import logging

logger = logging.getLogger(__name__)
impl = pluggy.HookimplMarker(getProjectName())


# Literals for the constants

# State literals
STATE_APPROVED = "APPROVED"
SATE_ESIGN_PENDING = "ESIGN_PENDING"
STATE_HOLDER_ESIGNED = "HOLDER_ESIGNED"
STATE_ESIGN_COMPLETE = "ESIGN_COMPLETE"
STATE_BO_ACCOUNT_CREATED = "BO_ACCOUNT_CREATED"
STATE_KRA_UPLOADED = "KRA_UPLOADED"

# Op id literals
OPR_ESIGN_EMAIL = "ESIGN_EMAIL"
OPR_W2W_ESIGNING = "W2W_ESIGNING"
OPR_TECH_XL_CREATE_ACCOUNT = "TECH_XL_CREATE_ACCOUNT"
OPR_KRA = "KRA"
OPR_KRA_STATUS = "KRA_STATUS"
OPR_PDF = "PDF"
#
OPR_NSDL_DEMAT_ACCOUNT = "NSDL_DEMAT_ACCOUNT"
OPR_UPLOAD_CDSL = "UPLOAD_CDSL"
OPR_KRA_UPLOAD_DATA = "KRA_UPLOAD_DATA"
OPR_NSDL_DEMAT_ACCOUNT_DOWNLOAD = "NSDL_DEMAT_ACCOUNT_DOWNLOAD"
OPR_CDSL_DEMAT_ACCOUNT_DOWNLOAD = "CDSL_DEMAT_ACCOUNT_DOWNLOAD"
OPR_TECH_XL_DOWNLOAD_PAYLOAD = "TECH_XL_DOWNLOAD_PAYLOAD"

KRA_TEXT = """
KRA (KYC Registration Agency) Upload is a process to upload your KYC (Know Your Customer) documents to a KYC Registration Agency. This ensures that your KYC details are verified and stored securely.

Steps to use KRA Upload:
1. **Initiate KRA Upload**: Start the KRA upload process by selecting the document you want to upload.
2. **Document Selection**: Choose the type of document you want to upload (e.g., PAN Card, Passport, etc.).
3. **Upload Document**: Upload a clear and legible copy of the selected document.
4. **Verification**: The uploaded document will be verified by the KYC Registration Agency.

Ensure that the document you upload is valid and up-to-date to avoid any delays in the verification process.
"""

ESIGN = """
Aadhaar-based eSign is an online electronic signature service that allows an Aadhaar holder to digitally sign a document. The process is simple and secure, leveraging the Aadhaar authentication framework.

Steps to use Aadhaar-based eSign:
1. **Initiate eSign Request**: Start the eSign process by pressing Continue.
2. **Aadhaar Authentication**: Enter your Aadhaar number. You will receive an OTP (One-Time Password) on your registered mobile number or email.
3. **Enter OTP**: Input the OTP received to authenticate your identity.
4. **Digital Signature**: Upon successful authentication, the document is signed digitally using your Aadhaar credentials.

Ensure your Aadhaar details are up-to-date and your mobile number is registered with UIDAI to use this service.
"""

W2W_ESIGN = """
Digitally signs the PDF on behalf of Way2Wealth.
This procees need to be triggered after the document is fully signed by all the signers.
"""

UCC_UPLOAD_TEXT = """
UCC(Unique Client Code) Upload is a process to send the client information to NSE/BSE.
"""

UCC_DOWNLOAD_TEXT = """
Download and verify the payload to be sent for UCC
"""
KRA_STATUS = """
Know the status of the KRA 
"""
ALL_OPERATIONS = [
    ## Not being used operations
    # Operation(op_id="ESIGN", op_name="eSign", display_text=ESIGN),
    # Operation(
    #     op_id="UPLOAD_UCC",
    #     op_name="UCC Upload",
    #     display_text=UCC_UPLOAD_TEXT,
    # ),
    # Operation(
    #     op_id="UCC_PAYLOAD",
    #     op_name="PREVIEW - Download UCC Payload",
    #     display_text=UCC_DOWNLOAD_TEXT,
    # ),
    ## Operations
    Operation(
        op_id=OPR_ESIGN_EMAIL,
        op_name="Esign Email Notification",
        display_text="To notify all kyc holders to esign the documents.",
        params={"transformer": "esign_notification.j2"},
    ),
    Operation(
        op_id=OPR_W2W_ESIGNING,
        op_name="Way2Wealth eSign of AOF",
        display_text=W2W_ESIGN,
    ),
    Operation(
        op_id=OPR_NSDL_DEMAT_ACCOUNT,
        op_name="Demat Account Creation",
        display_text="To create a demat account in the NSDL depository",
    ),
    Operation(
        op_id=OPR_UPLOAD_CDSL,
        op_name="Demat Account Creation",
        display_text="To create a demat account in the CDSL depository",
    ),
    Operation(
        op_id=OPR_TECH_XL_CREATE_ACCOUNT,
        op_name="Trading Account/BackOffice Update",
        display_text="To create/update an account.",
    ),
    Operation(
        op_id=OPR_KRA_STATUS,
        op_name="KRA PAN Status",
        display_text=KRA_STATUS,
    ),
    Operation(
        op_id=OPR_KRA,
        op_name="KRA Update",
        display_text=KRA_TEXT,
    ),
    ## Helper Operations
    Operation(
        op_id=OPR_PDF,
        op_name="PREVIEW - Account Opening Form",
        display_text="Generates the PDF(s) and gives the link to download the file(s).",
    ),
    Operation(
        op_id=OPR_KRA_UPLOAD_DATA,
        op_name="PREVIEW - CVL KRA Payload",
        display_text="Download and verify the payload to be sent for CVL KRA",
    ),
    Operation(
        op_id=OPR_NSDL_DEMAT_ACCOUNT_DOWNLOAD,
        op_name="PREVIEW - Demat(NSDL) Payload",
        display_text="To download and review the payload data to be sent to NSDL depository for Demat Account creation.",
    ),
    Operation(
        op_id=OPR_CDSL_DEMAT_ACCOUNT_DOWNLOAD,
        op_name="PREVIEW - Demat(CDSL) Payload",
        display_text="To download and review the payload data to be sent to CDSL depository for Demat Account creation.",
    ),
    Operation(
        op_id=OPR_TECH_XL_DOWNLOAD_PAYLOAD,
        op_name="PREVIEW - TechXL Payload",
        display_text="To download and review the payload data to be sent to TechXL Backoffice for Trading Account creation.",
    ),
]


class DepositoryName(str, Enum):
    NSDL = "nsdl"
    CDSL = "cdsl"


# Map form state to core operations
STATE_MAIN_OPS_MAP = {
    STATE_APPROVED: [OPR_ESIGN_EMAIL],
    SATE_ESIGN_PENDING: [OPR_ESIGN_EMAIL],
    STATE_HOLDER_ESIGNED: [OPR_W2W_ESIGNING],
    STATE_ESIGN_COMPLETE: [OPR_TECH_XL_CREATE_ACCOUNT],
    STATE_BO_ACCOUNT_CREATED: [OPR_KRA],
    STATE_KRA_UPLOADED: [OPR_KRA_STATUS],
}


class OperationsListPlugin(OperationsListSpec):
    """
    Plugin for fetching the list of operations available based on user roles and form data.
    """

    def get_user_roles(self, token: str) -> List[str]:
        """
        Extracts user roles from the provided JWT token.

        Args:
            token (str): The JWT token containing user metadata.

        Returns:
            List[str]: A list of roles assigned to the user.

        Raises:
            PluginException: If roles cannot be extracted or token is invalid.
        """
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            roles = (
                decoded.get("user_metadata", {}).get("user_info", {}).get("roles", [])
            )
            if not roles:
                raise PluginException("No roles found in token") from e
            return roles
        except Exception as e:
            raise PluginException("Error decoding token") from e

    def get_digilocker_status(self, form_record: GenericFormRecordModel) -> bool:
        """
        Checks if KYC Digilocker is selected in the form record.

        Args:
            form_record (GenericFormRecordModel): The form data.

        Returns:
            bool: True if Digilocker is selected, False otherwise.
        """
        try:
            form_dict = form_record.model_dump()
            return (
                form_dict.get("application_details", {})
                .get("kyc_digilocker", "")
                .upper()
                == "YES"
            )
        except Exception as e:
            return False

    def get_exchange_depository(
        self, form_record: GenericFormRecordModel
    ) -> DepositoryName | None:
        """
        Checks which depository is selected in the form record.

        Args:
            form_record (GenericFormRecordModel): The form data.

        Returns:
            Enum: Return depository type based on form record.
        """
        try:
            form_dict = form_record.model_dump()
            depository_name = (
                form_dict.get("dp_information", {})
                .get("dp_Account_information", {})
                .get("depository", "")
            )
            if not depository_name:
                return None
            if depository_name == "NSDL":
                return DepositoryName.NSDL
            return DepositoryName.CDSL
        except Exception as e:
            return None

    def get_application_type(self, form_record: GenericFormRecordModel) -> bool:
        """
        To get application type
        Args:
            form_record (GenericFormRecordModel): form data
        Returns:
            str | None: Returns application type if found, else None
        """
        try:
            form_dict = form_record.model_dump()
            type_pf_application = (
                form_dict.get("application_details", {})
                .get("general_application_details", {})
                .get("application_type", "")
            )
            if not type_pf_application:
                return None
            return type_pf_application
        except Exception as e:
            logger.error(f"Unable to get application type from form record: {e}")
            return None

    def get_state(self, form_record: GenericFormRecordModel) -> str | None:
        state = getattr(form_record, "state", None)
        return state

    @impl
    async def get_operations_list(
        self,
        context: ContextModel,
        form_record: Annotated[
            GenericFormRecordModel,
            Doc("The form record for which the operations list is required"),
        ],
    ) -> Annotated[
        OperationsListResponseModel,
        Doc("The list of operations available for the current form as per user role"),
    ]:
        """
        Determines the list of operations available for a user based on their role,
        form state, application type, and depository selection.

        Rules:
        - Maker & Client: Only the PDF operation is returned.
        - Checker & Admin: Main operations depend on the form state.
        - Helper (preview) operations continue to use existing depository and app type logic.
        - E-Sign-related operations are excluded if Digilocker is not selected.
        - If form state is not listed in STATE_MAIN_OPS_MAP, no main operations are shown.

        Args:
            context (ContextModel): Metadata including auth token.
            form_record (GenericFormRecordModel): The form data.

        Returns:
            OperationsListResponseModel: The final operations allowed for this form/user.
        """
        return OperationsListResponseModel(
            operations=[
                Operation(
                    op_id="SAMPLE_PDF",
                    op_name="SAMPLE PDF",
                    display_text="Description",
                    params=None,
                )
            ]
        )
        try:
            token = context.token
            if not token:
                raise ValueError("Token is not provided")

            # Extract roles, digilocker flag, depository, app type, and current state
            roles = self.get_user_roles(token=token)
            digilocker_selected = self.get_digilocker_status(form_record=form_record)
            depository_type: DepositoryName | None = self.get_exchange_depository(
                form_record=form_record
            )
            app_type = self.get_application_type(form_record=form_record)
            form_state = self.get_state(form_record=form_record)

            # Rule 1: Maker & Client get only PDF operation
            if "client" in roles:
                return OperationsListResponseModel(
                    operations=[op for op in ALL_OPERATIONS if op.op_id == OPR_PDF]
                )

            if "maker" in roles:
                operations = [
                    op
                    for op in ALL_OPERATIONS
                    if op.op_id == OPR_PDF
                    or (
                        form_state in {STATE_APPROVED, SATE_ESIGN_PENDING}
                        and op.op_id == OPR_ESIGN_EMAIL
                    )
                ]
                return OperationsListResponseModel(operations=operations)

            selected_ops = []

            # Rule 2: Add main operations based on form state if mapped
            if form_state in STATE_MAIN_OPS_MAP:
                for op_id in STATE_MAIN_OPS_MAP[form_state]:
                    # Skip eSign ops if Digilocker is not selected
                    if (
                        op_id in {OPR_ESIGN_EMAIL, OPR_W2W_ESIGNING}
                        and not digilocker_selected
                    ):
                        continue
                    selected_ops.extend(
                        [op for op in ALL_OPERATIONS if op.op_id == op_id]
                    )

            # Rule 3: Always include preview/helper ops based on app type and depository
            for op in ALL_OPERATIONS:
                if op.op_id.startswith("PREVIEW") or "PREVIEW" in op.op_name:
                    # Skip demat preview ops if only trading account is selected
                    if app_type in ["TRADING", "TRADING_KTK"]:
                        if op.op_id in [
                            OPR_NSDL_DEMAT_ACCOUNT_DOWNLOAD,
                            OPR_CDSL_DEMAT_ACCOUNT_DOWNLOAD,
                        ]:
                            continue
                    # Exclude NSDL preview if CDSL selected and vice versa
                    elif (
                        depository_type == DepositoryName.NSDL
                        and op.op_id == OPR_CDSL_DEMAT_ACCOUNT_DOWNLOAD
                    ):
                        continue
                    elif (
                        depository_type == DepositoryName.CDSL
                        and op.op_id == OPR_NSDL_DEMAT_ACCOUNT_DOWNLOAD
                    ):
                        continue
                    selected_ops.append(op)

            return OperationsListResponseModel(operations=selected_ops)
        except Exception as e:
            logger.debug(f"No operations available: {str(e)}")
            raise PluginException(
                f"No operations available for the current form record"
            ) from e
