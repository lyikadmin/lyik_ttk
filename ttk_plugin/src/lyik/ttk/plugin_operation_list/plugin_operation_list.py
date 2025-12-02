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
from typing_extensions import Annotated, Doc, List
from lyik.ttk.models.generated.universal_model_with_submission_requires_docket_status import (
    UniversalModelWithSubmissionRequiresDocketStatus,
    DOCKETSTATUS,
)
from lyik.ttk.utils.utils import get_personas_from_encoded_token
import logging
import jwt

logger = logging.getLogger(__name__)
impl = pluggy.HookimplMarker(getProjectName())

# Literals for PERSONA
BOA_PERSONA = "BOA"
CLIENT_PERSONA = "CLI"
MAKER_PERSONA = "MKR"

STATE_APPROVED = "APPROVED"

OPR_DOCKET_CREATION = "OP_DOCKET_CREATION"

ALL_OPERATIONS = [
    Operation(
        op_id=OPR_DOCKET_CREATION,
        display_text="Operation to create Docket for the current user.",
        op_name="",
    )
]


class OperationListPlugin(OperationsListSpec):
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
        try:
            token = context.token
            if not token:
                raise ValueError("Token is not provided")

            personas = get_personas_from_encoded_token(token=token)

            parsed_record = UniversalModelWithSubmissionRequiresDocketStatus(
                **form_record.model_dump()
            )
            context.token
            user_name = (
                parsed_record.passport.passport_details.first_name
                if parsed_record.passport and parsed_record.passport.passport_details
                else ""
            )

            for op in ALL_OPERATIONS:
                if op.op_id == OPR_DOCKET_CREATION:
                    op.op_name = (
                        f"Docket creation for {user_name}"
                        if user_name
                        else "Docket creation"
                    )

            if CLIENT_PERSONA in personas:
                form_state = self.get_state(form_record=form_record)
                if (
                    parsed_record.submit_info.docket.docket_status
                    == DOCKETSTATUS.ENABLE_DOWNLOAD.value
                ):
                    pass
                elif str(form_state) == STATE_APPROVED:
                    pass
                else:
                    return OperationsListResponseModel(operations=[])

            return OperationsListResponseModel(operations=ALL_OPERATIONS)
        except Exception as e:
            raise PluginException(
                message="Internal error occurred. Please contact support.",
                detailed_message=f"Failed to get operations for the current form. Error: {str(e)}",
            )

    def get_state(self, form_record: GenericFormRecordModel) -> str | None:
        state = getattr(form_record, "state", None)
        return state
