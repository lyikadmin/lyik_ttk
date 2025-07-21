# plugins/progress/pct_completion.py
from __future__ import annotations

import logging
from typing import Annotated, List

import apluggy as pluggy
from lyikpluginmanager import (
    ContextModel,
    GenericFormRecordModel,
    PreActionProcessorSpec,
    getProjectName,
)
from lyikpluginmanager.annotation import RequiredEnv
from typing_extensions import Doc

from ..models.forms.new_schengentouristvisa import Schengentouristvisa  # adjust import

logger = logging.getLogger(__name__)
impl = pluggy.HookimplMarker(getProjectName())

_RELEVANT_PANES: List[str] = [
    "visa_request_information",
    "appointment",
    "passport",
    "photograph",
    "residential_address",
    "itinerary_accomodation",
    "accomodation",
    "ticketing",
    "travel_insurance",
    "previous_visas",
    "additional_details",
]

def _all_null(value) -> bool:  # noqa: ANN001
    """Recursively true when *value* is empty / None / '' / [] / {}."""
    if value is None or value == "" or value == []:
        return True
    if isinstance(value, dict):
        return all(_all_null(v) for v in value.values())
    if isinstance(value, list):
        return all(_all_null(v) for v in value)
    return False


def _has_success_ver_status(data: dict) -> bool:
    """
    Returns *True* if ``_ver_status.status == "success"`` is found under *data*.
    """
    if not isinstance(data, dict):
        return False

    ver = data.get("_ver_status")
    if isinstance(ver, dict) and ver.get("status") == "success":
        return True

    # False:- Since the _ver_status is null
    return False
    # return any(_has_success_ver_status(v) for v in data.values() if isinstance(v, dict))


class PctCompletion(PreActionProcessorSpec):
    """Calculates traveller progress and writes it into ``pct_completion``."""

    @impl
    async def pre_action_processor(
        self,
        context: ContextModel,
        action: Annotated[str, "save / submit"],
        current_state: Annotated[str | None, "previous record state"],
        new_state: Annotated[str | None, "new record state"],
        payload: Annotated[GenericFormRecordModel, "entire form record model"],
    ) -> Annotated[
        GenericFormRecordModel,
        Doc("form record with pct_completion refreshed"),
    ]:
        
        try:
            form: Schengentouristvisa = Schengentouristvisa(**payload.model_dump())
        except Exception as exc:  # defensive – don’t break save/submit
            logger.error("pct_completion: cannot parse payload – %s", exc)
            record = payload.model_dump()
            return GenericFormRecordModel.model_validate(record)

        # total, completed = 0, 0
        # 1) Base count: total = number of relevant panes; completed = count of those with status "success"
        total, completed = len(_RELEVANT_PANES), 0

        # for attr in _RELEVANT_PANES:

        #     # get the attributes from the payload else none
        #     pane = getattr(form, attr, None)

        #     if pane is None:
        #         continue 

        #     pane_dict = pane.model_dump(exclude_none=True)

        #     # get the total relavant infopanes
        #     total += 1 # for now, we are not counting the infopanes like this

        #     # Check if the fields from Infopane are null
        #     # and also no ver_status will be skipped
        #     if _all_null(pane_dict):
        #         continue

        #     # 
        #     if _has_success_ver_status(pane_dict):
        #         # Increment the infopanes which only have 
        #         # 1. _ver_status : 'Successfull'
        #         # 2. ignoring infopanes based only for the Backoffice and Maker
        #         completed += 1
        
        # 2) If this is a Co-traveller, factor in the “shared‐with‐primary” toggles
        # This part is commented out as it is not needed for the current implementation
        # vt = getattr(form.visa_request_information.visa_request, "traveller_type", None)
        # shared = getattr(form.shared_travell_info, "shared", None)
        # if vt and vt.lower() != "primary" and shared:
        #     # map each flag to a “virtual pane”
        #     mapping = [
        #         (shared.itinerary_same,    "ITINERARY"),
        #         (shared.accommodation_same, "ACCOMMODATION"),
        #         (shared.flight_ticket_same, "FLIGHT_TICKET"),
        #     ]

        #     for flag, value_str in mapping:
        #         total += 1
        #         if flag and flag.value == value_str:
        #             completed += 1


        for pane_name in _RELEVANT_PANES:
            pane = getattr(form, pane_name, None)
            if pane is None:
                continue
            pane_dict = pane.model_dump(exclude_none=True)
            if _has_success_ver_status(pane_dict):
                completed += 1

        # 2) If this is a Co-traveller, factor in the “shared‐with‐primary” toggles
        vt = getattr(form.visa_request_information.visa_request, "traveller_type", None)
        shared = getattr(form.shared_travell_info, "shared", None)
        if vt and vt.lower() != "primary" and shared:
            # map each flag to a “virtual pane”
            mapping = [
                (shared.itinerary_same,     "ITINERARY"),
                (shared.accommodation_same, "ACCOMMODATION"),
                (shared.flight_ticket_same, "FLIGHT_TICKET"),
            ]

            # count how many shares they actually clicked
            shared_count = sum(
                1
                for flag, expected in mapping
                if flag and flag.value == expected
            )

            # we no longer blindly add 3; instead subtract the un-shared ones:
            #   if they shared 0 → subtract 3  (3 − 0)
            #   if they shared 1 → subtract 2  (3 − 1)
            #   if they shared 2 → subtract 1  (3 − 2)
            #   if they shared 3 → subtract 0  (3 − 3)
            total -= (len(mapping) - shared_count)

            # and credit them for each share
            completed += shared_count

        percentage = round((completed / total) * 100) if total else 0

        record = form.model_dump()
        # get or create the nested dict
        lets = record.get("lets_get_started") or {}
        lets["infopanes_total"]     = total
        lets["infopanes_completed"] = completed
        lets["pct_completion"]      = str(percentage)
        record["lets_get_started"] = lets

        return GenericFormRecordModel.model_validate(record)
