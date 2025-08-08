# plugins/progress/pct_completion.py
from __future__ import annotations

import logging
from typing import Annotated, List

import apluggy as pluggy
from lyikpluginmanager import (
    ContextModel,
    GenericFormRecordModel,
    getProjectName,
)
from lyikpluginmanager.annotation import RequiredEnv
from typing_extensions import Doc

from ...models.forms.schengentouristvisa import Schengentouristvisa  # adjust import
from ._base_preaction import BasePreActionProcessor

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


class PreactionPctCompletion(BasePreActionProcessor):
    """Calculates traveller progress and writes it into ``pct_completion``."""

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
            record["pct_completion"] = "0"
            return GenericFormRecordModel.model_validate(record)

        total, completed = 0, 0

        for attr in _RELEVANT_PANES:

            # get the attributes from the payload else none
            pane = getattr(form, attr, None)

            if pane is None:
                continue

            pane_dict = pane.model_dump(exclude_none=True)

            # get the total relavant infopanes
            total += 1

            # Check if the fields from Infopane are null
            # and also no ver_status will be skipped
            if _all_null(pane_dict):
                continue

            #
            if _has_success_ver_status(pane_dict):
                # Increment the infopanes which only have
                # 1. _ver_status : 'Successfull'
                # 2. ignoring infopanes based only for the Backoffice and Maker
                completed += 1

        # 2) If this is a Co-traveller, factor in the “shared‐with‐primary” toggles
        vt = getattr(form.visa_request_information.visa_request, "traveller_type", None)
        shared = getattr(form.shared_travell_info, "shared", None)
        if vt and vt.lower() != "primary" and shared:
            # map each flag to a “virtual pane”
            mapping = [
                (shared.itinerary_same, "ITINERARY"),
                (shared.accommodation_same, "ACCOMMODATION"),
                (shared.flight_ticket_same, "FLIGHT_TICKET"),
            ]

            for flag, value_str in mapping:
                total += 1
                if flag and flag.value == value_str:
                    completed += 1

        percentage = round((completed / total) * 100) if total else 0

        record = form.model_dump()
        record["infopanes_total"] = total
        record["infopanes_completed"] = completed
        record["pct_completion"] = str(percentage)

        return GenericFormRecordModel.model_validate(record)
