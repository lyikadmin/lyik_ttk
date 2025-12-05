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

# Simple flag to enable/disable all debug logs in this module
ENABLE_OPERATION_LIST_LOGS = True


def _log_debug(message: str, **kwargs) -> None:
    if ENABLE_OPERATION_LIST_LOGS:
        if kwargs:
            logger.debug("%s | %s", message, kwargs)
        else:
            logger.debug(message)


def _log_error(message: str, **kwargs) -> None:
    if ENABLE_OPERATION_LIST_LOGS:
        if kwargs:
            logger.error("%s | %s", message, kwargs)
        else:
            logger.error(message)


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
        _log_debug(
            "get_operations_list called",
            has_token=bool(getattr(context, "token", None)),
        )
        try:
            token = context.token
            if not token:
                _log_error("Token not provided in context")
                raise ValueError("Token is not provided")

            _log_debug("Token found in context")
            personas = get_personas_from_encoded_token(token=token)
            _log_debug("Personas extracted from token", personas=personas)

            parsed_record = UniversalModelWithSubmissionRequiresDocketStatus(
                **form_record.model_dump()
            )
            _log_debug(
                "Parsed UniversalModelWithSubmissionRequiresDocketStatus",
                has_passport=bool(parsed_record.passport),
                has_passport_details=bool(
                    parsed_record.passport and parsed_record.passport.passport_details
                ),
            )

            context.token  # existing line kept as-is

            user_name = (
                parsed_record.passport.passport_details.first_name
                if parsed_record.passport and parsed_record.passport.passport_details
                else ""
            )
            _log_debug(
                "Extracted user name from parsed record",
                user_name_present=bool(user_name),
            )

            _log_debug("Updating ALL_OPERATIONS with user-specific names")
            for op in ALL_OPERATIONS:
                if op.op_id == OPR_DOCKET_CREATION:
                    op.op_name = (
                        f"Docket creation for {user_name}"
                        if user_name
                        else "Docket creation"
                    )
            _log_debug(
                "Updated operations list",
                operations=[
                    {"op_id": op.op_id, "op_name": op.op_name} for op in ALL_OPERATIONS
                ],
            )

            if CLIENT_PERSONA in personas:
                _log_debug("CLIENT_PERSONA detected, applying client-specific logic")
                form_state = self.get_state(form_record=form_record)
                _log_debug("Form state resolved", form_state=str(form_state))

                docket_status = (
                    parsed_record.submit_info.docket.docket_status
                    if parsed_record.submit_info and parsed_record.submit_info.docket
                    else None
                )
                _log_debug("Docket status resolved", docket_status=str(docket_status))

                if docket_status == DOCKETSTATUS.ENABLE_DOWNLOAD.value:
                    _log_debug(
                        "Docket status allows download; operations will be returned",
                    )
                    pass
                elif str(form_state) == STATE_APPROVED:
                    _log_debug(
                        "Form state is APPROVED; operations will be returned",
                    )
                    pass
                else:
                    _log_debug(
                        "Client persona but neither docket_status nor state meet criteria; returning empty operations list"
                    )
                    return OperationsListResponseModel(operations=[])

            _log_debug(
                "Returning operations list",
                operations=[
                    {"op_id": op.op_id, "op_name": op.op_name} for op in ALL_OPERATIONS
                ],
            )
            return OperationsListResponseModel(operations=ALL_OPERATIONS)
        except Exception as e:
            _log_error(
                "Error occurred in get_operations_list",
                error=str(e),
            )
            raise PluginException(
                message="Internal error occurred. Please contact support.",
                detailed_message=f"Failed to get operations for the current form. Error: {str(e)}",
            )

    def get_state(self, form_record: GenericFormRecordModel) -> str | None:
        _log_debug("Resolving state from form_record")
        state = getattr(form_record, "state", None)
        _log_debug("State resolved from form_record", state=str(state))
        return state
