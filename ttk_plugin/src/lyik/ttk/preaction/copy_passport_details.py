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
    RootResidentialAddress
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
        payload: Annotated[
            GenericFormRecordModel,
            "entire form record model"
        ],
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
            address_line_1=pp_addr.address_line_1,
            address_line_2=pp_addr.address_line_2,
            pin_code=pp_addr.pin_code,
            state=pp_addr.state,
            city=pp_addr.city,
            country=pp_addr.country,
        )

        # 1. Make sure the Pydantic model has a residential_address
        if form.residential_address is None:
            form.residential_address = RootResidentialAddress()

        # 2. Assign the `RootResidentialAddressResidentialAddressCardV2` instance to it
        form.residential_address.residential_address_card_v2 = new_card

        # 3. Dump back to a dict and re-validate
        new_payload_dict = form.model_dump()  # default is a dict
        return GenericFormRecordModel.model_validate(new_payload_dict)


# # Type alias for an “operation” that inspects and possibly mutates the form
# # without using this List[Tuple[Callable[..., bool], Callable[..., None]]] directly.
# # Each operation is a tuple of two callables:
# Operation = Tuple[
#     Callable[[Schengentouristvisa], bool],  # predicate: should we run?
#     Callable[[Schengentouristvisa], None],  # action: mutate in-place
# ]


# def _copy_fields(
#     src: object,
#     dst: object,
#     fields: Union[List[str], Dict[str, str]],
# ) -> None:
#     """
#     Copy fields from `src` to `dst`.

#     - If `fields` is a list of strings, each name is used as both source and destination attr.
#     - If `fields` is a dict, keys are source-attr names and values are destination-attr names.
#     """
#     # Build uniform mapping of src_attr -> dst_attr
#     if isinstance(fields, dict):
#         mapping = fields
#     else:
#         mapping = {name: name for name in fields}

#     for src_name, dst_name in mapping.items():
#         val = getattr(src, src_name, None)
#         if val is not None:
#             setattr(dst, dst_name, val)

# def _should_copy_passport(form: Schengentouristvisa) -> bool:
#     """
#     This method checks if the residential address
#     has `same_as_passport_address` set to `SAME_AS_PASS_ADDR`
#     and if the passport address exists.
#     Returns True if the conditions are met, otherwise False.
#     """
#     ra = form.residential_address
#     return bool(
#         ra
#         and ra.same_as_passport_address == SAMEASPASSADDR.SAME_AS_PASS_ADDR
#         and form.passport
#         and form.passport.passport_details
#     )

# def _copy_passport_to_residential(form: Schengentouristvisa) -> None:
#     """
#     Copies Country, State, City, PIN Code, Address Line 1 and 2
#     from passport_address into residential_address.residential_address_card.
#     """
#     pp: RootPassportPassportDetails = form.passport.passport_details
#     # ensure residential_address_card exists
#     rc = RootResidentialAddressResidentialAddressCard(
#         address_line_1=None,
#         address_line_2=None,
#         pin_code=None,
#         state=None,
#         city=None,
#         country=None,
#     )

#     # Example usage:
#     # 1) for same-names:
#     # this works as object property shorthand (or “shorthand property names”). 
#     # When the variable name and the object key are the same, you can omit the key: part 
#     # and just list the identifier.
#     same_name_fields = [
#         "address_line_1",
#         "address_line_2",
#         "pin_code",
#         "state",
#         "city",
#         "country",
#     ]

#     # 2) if you ever need to rename:
#     # renamed_fields = {
#     #     "address_line_1": "resident_addr1",
#     #     "pin_code": "postal_code",
#     # }
#     # _copy_fields(src=pp, dst=rc, fields=renamed_fields)

#     _copy_fields(
#         src=pp,
#         dst=rc,
#         fields=same_name_fields
#     )

#     # attach it back
#     form.residential_address.residential_address_card = rc  


# # build your pipeline of “when this predicate is true, run this action”
# # (Method which is used to check for the condition, Method which does from operation based on the condition)
# OPERATIONS: List[Operation] = [
#     (_should_copy_passport, _copy_passport_to_residential),
# ]

# class FormOperationsProcessor(PreActionProcessorSpec):
#     @impl
#     async def pre_action_processor(
#         self,
#         context: ContextModel,
#         action: Annotated[str, "e.g. 'save' or 'submit'"],
#         current_state: Annotated[str | None, "previous record state"],
#         new_state: Annotated[str | None, "new record state"],
#         payload: Annotated[GenericFormRecordModel, "the raw form record"],
#     ) -> Annotated[GenericFormRecordModel, "potentially modified record"]:
#         """
#         A generic “form operations” processor.

#         1. Parse the GenericFormRecordModel into Schengentouristvisa.
#         2. Run each (predicate → action) in sequence.
#         3. Re-dump into dict and validate back to GenericFormRecordModel.
#         """

#         # 1. parse into typed model
#         try:
#             form = Schengentouristvisa(**payload.model_dump())
#         except Exception as e:
#             logger.error("Failed to parse form payload: %s", e)
#             return payload

#         # 2. run each op if its predicate matches
#         for should_run, do_run in OPERATIONS:
#             try:
#                 if should_run(form):
#                     do_run(form)
#             except Exception as e:
#                 logger.exception("Error running operation %s: %s", do_run.__name__, e)

#         # 3. dump back to dict and re-validate
#         new_data = form.model_dump(mode="json")
#         return GenericFormRecordModel.model_validate(new_data)