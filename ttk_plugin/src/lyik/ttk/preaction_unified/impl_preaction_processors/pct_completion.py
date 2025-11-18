# plugins/progress/pct_completion.py
from __future__ import annotations
import logging
from typing import Annotated, List

import apluggy as pluggy
from lyikpluginmanager import (
    ContextModel,
    GenericFormRecordModel,
)
from typing_extensions import Doc
from lyik.ttk.models.forms.schengentouristvisa import Schengentouristvisa, RootLetsGetStarted, VISATYPE
from .._base_preaction import BaseUnifiedPreActionProcessor

logger = logging.getLogger(__name__)

# 🔧 VERIFY THESE NAMES MATCH YOUR Pydantic MODEL FIELDS EXACTLY.
# If your model uses "accommodation" (correct spelling), update both lines below.
_RELEVANT_PANES: List[str] = [
    # 1st tab
    "visa_request_information",
    "appointment",
    # 2nd tab
    "passport",
    "photograph",
    "residential_address",
    "work_address",
    "itinerary_accomodation",   # ← check spelling; likely "itinerary_accommodation"
    "accomodation",             # ← check spelling; likely "accommodation"
    "ticketing",
    "travel_insurance",
    "previous_visas",
    "additional_details",
    "additional_documents_pane",
    # 3rd tab
    "salary_slip",
    "bank_statement",
    "itr_acknowledgement",
    # 4th tab
    "cover_letter_info",
    "invitation",
]

_BUSINESS_PANES: List[str] = [
    "company_bank_statement",
    "company_itr",
    "company_docs"
]

def _has_success_ver_status(data: dict) -> bool:
    ver = data.get("_ver_status")
    return isinstance(ver, dict) and ver.get("status") == "success"


class PctCompletion(BaseUnifiedPreActionProcessor):
    """Calculates traveller progress and writes it into ``pct_completion``."""
    async def unified_pre_action_processor_impl(
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
        
        panes_to_check = _RELEVANT_PANES.copy()
        if (form.visa_request_information and
            form.visa_request_information.visa_request and
            form.visa_request_information.visa_request.visa_type):

            # visa_type = form.visa_request_information.visa_request.visa_type.value
            # if visa_type and visa_type.lower() == "business":
            #     panes_to_check += _BUSINESS_PANES

            visa_type: VISATYPE = form.visa_request_information.visa_request.visa_type
            if visa_type and visa_type.value and visa_type.value.lower() == "business":
                panes_to_check += _BUSINESS_PANES

        # 1) Figure out share-flag mapping
        if (form.visa_request_information and 
            form.visa_request_information.visa_request and 
            form.visa_request_information.visa_request.traveller_type):
            vt = form.visa_request_information.visa_request.traveller_type
        else:
            vt = ''

        if (form.shared_travell_info and form.shared_travell_info.shared):
            shared = form.shared_travell_info.shared
        else:
            shared = None

        # vt = getattr(getattr(form, "visa_request_information", None), "visa_request", None)
        # vt = getattr(vt, "traveller_type", "") or ""
        # shared = getattr(getattr(form, "shared_travell_info", None), "shared", None)

        # panes_to_check = _RELEVANT_PANES.copy()
        shared_count = 0
        share_removed: List[str] = []

        if vt and vt.lower() != "primary" and shared:
            mapping = [
                ("itinerary_accomodation", shared.itinerary_same),
                ("accomodation", shared.accommodation_same),
                ("ticketing", shared.flight_ticket_same),
            ]
            for pane_name, flag in mapping:
                try:
                    is_on = bool(flag and getattr(flag, "value", flag))
                except Exception:
                    is_on = False
                if is_on:
                    if pane_name in panes_to_check:
                        panes_to_check.remove(pane_name)
                        share_removed.append(pane_name)
                    shared_count += 1

        logger.info(
            "pct_completion: relevant_panes=%s | panes_to_check(after share)=%s | shared_removed=%s | shared_count=%d",
            _RELEVANT_PANES, panes_to_check, share_removed, shared_count
        )

        # 3) Status scan with detailed tracking
        completed = 0
        completed_panes: List[str] = []
        incomplete_panes: List[str] = []
        missing_attrs: List[str] = []

        for pane_name in panes_to_check:
            pane = getattr(form, pane_name, None)
            if pane is None:
                missing_attrs.append(pane_name)
                continue
            pane_dict = pane.model_dump(exclude_none=True)
            if _has_success_ver_status(pane_dict):
                completed += 1
                completed_panes.append(pane_name)
            else:
                # Optional: capture the status we saw for easier debugging
                status = pane_dict.get("_ver_status", {}).get("status")
                incomplete_panes.append(f"{pane_name} (status={status!r})")

        logger.info(
            "pct_completion: panes_considered=%s | panes_completed=%s | panes_incomplete=%s | missing_attrs=%s",
            panes_to_check, completed_panes, incomplete_panes, missing_attrs
        )

        # 4) Totals and final completed count
        total = len(panes_to_check) + shared_count
        completed = completed + shared_count

        # 5) Compute, clamp, format
        pct = round((completed / total) * 100) if total else 0
        pct = min(pct, 100)
        pct_str = f"{pct}%"

        logger.info(
            "pct_completion: totals -> total=%d, completed=%d, pct=%s",
            total, completed, pct_str
        )

        # 6) Write back into lets_get_started
        if not getattr(form, "lets_get_started", None):
            form.lets_get_started = RootLetsGetStarted()

        form.lets_get_started.infopanes_total = total
        form.lets_get_started.infopanes_completed = completed
        form.lets_get_started.pct_completion = pct_str

        return GenericFormRecordModel.model_validate(form.model_dump())
