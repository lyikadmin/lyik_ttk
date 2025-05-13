from typing import Dict
from pydantic import Field, BaseModel
from typing_extensions import Doc, Annotated

import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    PreActionProcessorSpec,
    ContextModel,
    GenericFormRecordModel,
    PluginException,
)
from ..models.forms.schengentouristvisa import Org26843479Frm5809021Model
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.info)

impl = pluggy.HookimplMarker(getProjectName())


class dbClient(BaseModel):
    """
    Data model storing the details of a records client
    """

    contact_id: str = Field(None, description="Phone number or Email of the client")


# class ClientInformation(PreActionProcessorSpec):
class AppendMakerId(PreActionProcessorSpec):
    @impl
    async def pre_action_processor(
        self,
        context: ContextModel,
        action: Annotated[
            str,
            Doc("The action of the processor like: 'save' and 'submit'"),
        ],
        current_state: Annotated[
            str | None,
            Doc(
                "Current state of the record like: 'save', 'submit', 'approved'"
                "This state will be the already saved state of the record"
            ),
        ],
        new_state: Annotated[
            str | None,
            Doc(
                "New state of the record like: 'save', 'submit', 'approved'"
                "This state will be the new state which will be sent in the request"
            ),
        ],
        payload: Annotated[
            GenericFormRecordModel,
            Doc("The payload of form record data to be pre processed to append maker_id in owner's list."),
        ],
    ) -> Annotated[
        GenericFormRecordModel,
        Doc("The updated form record data."),
    ]:
        """
        This preaction processor will append maker_id into the _owner list of the record.
        """
        logger.debug(f"Entering preaction with payload: {payload}")
        if not context or not hasattr(context, "token") or not context.token:
            logger.debug("No token found in context. Passing through AppendMakerId preaction.")
            return payload
        try:
            record_payload = Org26843479Frm5809021Model(**payload.model_dump()) 
            maker_id = record_payload.travel.travel_details.maker_id

            if maker_id:
                new_record_payload = _set_owner(record_payload.model_dump(), maker_id) 
                return Org26843479Frm5809021Model.model_validate(new_record_payload)
            else:
                return Org26843479Frm5809021Model.model_validate(record_payload.model_dump())

        except Exception as e:
            logger.error(f"Error processing payload: {e}")
            return payload # Important:  Return original payload on error to prevent data loss.



def _set_owner(rec: dict, client: str) -> dict:
    """
    Updates the record with current owner, if not already present.
    """
    owner_list = rec.get("_owner", [])
    current_owner = client

    # Set to ensure unique owners
    owner_set = set(owner_list)
    owner_set.add(current_owner)

    # Convert the set back to a list to update record
    rec["_owner"] = list(owner_set)
    return rec
