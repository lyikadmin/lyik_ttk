import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    PluginException,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
)
from lyikpluginmanager.annotation import RequiredVars
from typing import Annotated
from typing_extensions import Doc
from lyik.ttk.models.generated.universal_model_with_all_financial_documents import (
    RootSalarySlip,
    RootBankStatement,
    RootItrAcknowledgement,
)
import logging
from lyik.ttk.utils.message import get_error_message

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())

ACTOR = "system"


class SalarySlipVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootSalarySlip,
            Doc("Salary Slip payload."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response after validating the Salary Slips."),
    ]:
        """
        This verifier validates the data of the Salary Slip section.
        Checks if skipped or uploaded files.
        """
        skip_salary_slips = None
        if payload and payload.skip_salary_slips:
            skip_salary_slips = payload.skip_salary_slips

        salary_slip_file = None
        if payload and payload.upload and payload.upload.salary_slip:
            salary_slip_file = payload.upload.salary_slip

        if not (skip_salary_slips or salary_slip_file):
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=get_error_message("LYIK_ERR_NO_SALARY_OPTION"),
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )

        return VerifyHandlerResponseModel(
            actor=ACTOR,
            message="Verified by System",
            status=VERIFY_RESPONSE_STATUS.SUCCESS,
        )


class BankStatementVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootBankStatement,
            Doc("Bank Statement payload."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response after validating the Bank Statement."),
    ]:
        """
        This verifier validates the data of the Bank Statement section.
        Checks if skipped or uploaded files.
        """
        skip_bank_statement = None
        if payload and payload.skip_bank_statements:
            skip_bank_statement = payload.skip_bank_statements

        bank_statement_file = None
        if payload and payload.upload and payload.upload.bank_statements:
            bank_statement_file = payload.upload.bank_statements

        if not (skip_bank_statement or bank_statement_file):
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=get_error_message("LYIK_ERR_NO_BANK_OPTION"),
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )

        return VerifyHandlerResponseModel(
            actor=ACTOR,
            message="Verified by System",
            status=VERIFY_RESPONSE_STATUS.SUCCESS,
        )


class ITRAcknowledgeVerifier(VerifyHandlerSpec):

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootItrAcknowledgement,
            Doc("ITR Acknowledgements payload."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        Doc("Response after validating the ITR Acknowledgements."),
    ]:
        """
        This verifier validates the data of the ITR Acknowledgements section.
        Checks if skipped or uploaded files.
        """
        skip_itr_upload = None
        if payload and payload.itr_options:
            skip_itr_upload = payload.itr_options

        itr_acklowledgement_file = None
        if payload and payload.upload and payload.upload.itr_acknowledgement:
            itr_acklowledgement_file = payload.upload.itr_acknowledgement

        if not (skip_itr_upload or itr_acklowledgement_file):
            return VerifyHandlerResponseModel(
                actor=ACTOR,
                message=get_error_message("LYIK_ERR_NO_ITR_OPTION"),
                status=VERIFY_RESPONSE_STATUS.FAILURE,
            )

        return VerifyHandlerResponseModel(
            actor=ACTOR,
            message="Verified by System",
            status=VERIFY_RESPONSE_STATUS.SUCCESS,
        )
