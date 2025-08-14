import logging
from typing import Annotated, Callable, Dict, List, Tuple, Union
import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    PreActionProcessorSpec,
    ContextModel,
    GenericFormRecordModel,
)
from lyik.ttk.models.forms.schengentouristvisa import (
    Schengentouristvisa,
    SAMEASPASSADDR,
    RootPassportPassportDetails,
    RootResidentialAddressResidentialAddressCardV2,
    RootResidentialAddress,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

impl = pluggy.HookimplMarker(getProjectName())


class CopyPassportAddress(PreActionProcessorSpec):
    @impl
    async def pre_action_processor(
        self,
        context: ContextModel,
        action: Annotated[str, "save or submit"],
        current_state: Annotated[str | None, "previous record state"],
        new_state: Annotated[str | None, "new record state"],
        payload: Annotated[GenericFormRecordModel, "entire form record model"],
    ) -> Annotated[GenericFormRecordModel, "possibly modified record"]:
        """
        If `same_as_passport_address` is set, copy the values
        Country, State, City, PIN Code, Address Line 2, and Address Line 1
        from the passport address into the residential-address card V2.
        """
        # Turn into our strong-typed form model
        try:
            form = Schengentouristvisa(**payload.model_dump())
        except Exception as e:
            logger.error("Failed to parse form payload for address copy: %s", e)
            return payload

        # Grab the passport details
        pp_addr: RootPassportPassportDetails | None = (
            form.passport.passport_details if form.passport else None
        )
        if not pp_addr:
            logger.warning("no Passport Details found")
            return payload

        # Build new residential_address_card
        new_card = RootResidentialAddressResidentialAddressCardV2(
            address_line_1=default_if_empty(pp_addr.address_line_1),
            address_line_2=default_if_empty(pp_addr.address_line_2),
            pin_code=default_if_empty(pp_addr.pin_code),
            state=default_if_empty(pp_addr.state),
            city=default_if_empty(pp_addr.city),
            country=default_if_empty(pp_addr.country),
        )

        # 1. Make sure the Pydantic model has a residential_address
        if form.residential_address is None:
            form.residential_address = RootResidentialAddress()

        # 2. Assign the `RootResidentialAddressResidentialAddressCardV2` instance to it
        form.residential_address.residential_address_card_v2 = new_card

        # 3. Dump back to a dict and re-validate
        new_payload_dict = form.model_dump()  # default is a dict
        return GenericFormRecordModel.model_validate(new_payload_dict)


def default_if_empty(value, default="nil"):
    return value if (value is not None and str(value).strip()) else default
