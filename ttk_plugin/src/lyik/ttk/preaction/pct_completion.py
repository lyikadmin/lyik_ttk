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
from typing_extensions import Doc
from lyik.ttk.models.forms.schengentouristvisa import Schengentouristvisa

logger = logging.getLogger(__name__)
impl = pluggy.HookimplMarker(getProjectName())

_RELEVANT_PANES: List[str] = [
    "visa_request_information",
    "appointment",
    "passport",
    "photograph",
    "residential_address",
    "itinerary_accomodation",  # ← shareable
    "accomodation",            # ← shareable
    "ticketing",               # ← shareable
    "travel_insurance",
    "previous_visas",
    "additional_details",
]


def _has_success_ver_status(data: dict) -> bool:
    """
    Returns True if data.get('_ver_status',{}).get('status') == 'success'.
    """
    ver = data.get("_ver_status")
    return isinstance(ver, dict) and ver.get("status") == "success"


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

        # 1) Figure out share-flag mapping
        vt     = getattr(form.visa_request_information.visa_request, "traveller_type", "")
        shared = getattr(form.shared_travell_info, "shared", None)

        # 2) Start with the full list, and remove any share‑flagged panes
        panes_to_check = _RELEVANT_PANES.copy()
        shared_count   = 0

        if vt and vt.lower() != "primary" and shared:
            # for each shareable pane, if they clicked it → remove & credit
            mapping = [
                ("itinerary_accomodation", shared.itinerary_same),
                ("accomodation",           shared.accommodation_same),
                ("ticketing",              shared.flight_ticket_same),
            ]
            for pane_name, flag in mapping:
                if flag and flag.value:
                    if pane_name in panes_to_check:
                        panes_to_check.remove(pane_name)
                    shared_count += 1

        # 3) Now loop over whatever remains for real _ver_status checks
        completed = 0
        for pane_name in panes_to_check:
            pane = getattr(form, pane_name, None)
            if not pane:
                continue
            pane_dict = pane.model_dump(exclude_none=True)
            if _has_success_ver_status(pane_dict):
                completed += 1

        # 4) Totals and final completed count
        total     = len(panes_to_check) + shared_count
        completed = completed + shared_count

        # 5) Compute, clamp, format
        pct = round((completed / total) * 100) if total else 0
        pct = min(pct, 100)
        pct_str = f"{pct}%"

        # 6) Write back into the lets_get_started sub‑dict
        record = form.model_dump()
        # get or create the nested dict
        lets = record.get("lets_get_started", {})
        lets["infopanes_total"]     = total
        lets["infopanes_completed"] = completed
        lets["pct_completion"]      = pct_str
        record["lets_get_started"] = lets

        return GenericFormRecordModel.model_validate(record)
