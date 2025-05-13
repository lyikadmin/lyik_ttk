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
from ..models.forms.schengentouristvisa import RootTravelTravelDetails
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
        if not context or not hasattr(context, "token") or not context.token:
            logger.debug(
                "No token found in context. Passing through AppendMakerId preaction."
            )
            return payload
        root_travel_details = RootTravelTravelDetails(**payload.model_dump())
        maker_id=root_travel_details.maker_id
        if maker_id:
            owner_list = root_travel_details.get("_owner", [])


        return GenericFormRecordModel.model_validate(payload)


import phonenumbers


def validate_phone(value: str) -> str:
    phone = phonenumbers.parse(
        number=value,
        region=phonenumbers.region_code_for_country_code(int(91)),
    )
    if not phonenumbers.is_valid_number(phone):
        raise PluginException(f"{value} does not seem like a valid phone number")

    return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)


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
