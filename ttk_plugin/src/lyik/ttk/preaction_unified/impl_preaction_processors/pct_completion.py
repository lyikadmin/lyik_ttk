# plugins/progress/pct_completion.py
from __future__ import annotations
import logging
from typing import Annotated, List
from pydantic import BaseModel

import apluggy as pluggy
from lyikpluginmanager import (
    ContextModel,
    GenericFormRecordModel,
)
from typing_extensions import Doc
from lyik.ttk.models.generated.universal_model import (
    UniversalModel,
    RootLetsGetStarted,
    VISATYPE,
)
from .._base_preaction import BaseUnifiedPreActionProcessor

from lyik.ttk.utils.form_indicator import FormIndicator
from lyik.ttk.utils.form_utils import FormConfig

logger = logging.getLogger(__name__)

_RELEVANT_PANES: List[str] = [
    # 1st tab
    "visa_request_information",
    "appointment",
    # 2nd tab
    "passport",
    "photograph",
    "residential_address",
    "work_address",
    "itinerary_accomodation",
    "accomodation",
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

_BUSINESS_PANES: List[str] = ["company_bank_statement", "company_itr", "company_docs"]


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
        form_indicator: Annotated[
            FormIndicator,
            Doc("The form indicator for the form"),
        ],
        payload: Annotated[GenericFormRecordModel, "entire form record model"],
    ) -> Annotated[
        GenericFormRecordModel,
        Doc("form record with pct_completion refreshed"),
    ]:

        try:
            form: UniversalModel = UniversalModel(**payload.model_dump())
        except Exception as exc:  # defensive – don’t break save/submit
            logger.error("pct_completion: cannot parse payload – %s", exc)
            record = payload.model_dump()
            return GenericFormRecordModel.model_validate(record)

        frm_config = FormConfig(form_indicator=form_indicator)

        # Start with relevant panes from helper (so later can come from config)
        panes_to_check = frm_config.get_relevant_infopane_list()

        if (
            form.visa_request_information
            and form.visa_request_information.visa_request
            and form.visa_request_information.visa_request.visa_type
        ):
            visa_type: VISATYPE = form.visa_request_information.visa_request.visa_type
            if visa_type and visa_type.value and visa_type.value.lower() == "business":
                # Add business panes via helper
                panes_to_check += frm_config.get_business_panes_list()

        # 1) Figure out share-flag mapping
        if (
            form.visa_request_information
            and form.visa_request_information.visa_request
            and form.visa_request_information.visa_request.traveller_type
        ):
            vt = form.visa_request_information.visa_request.traveller_type
        else:
            vt = ""

        if form.shared_travell_info and form.shared_travell_info.shared:
            shared = form.shared_travell_info.shared
        else:
            shared = None

        shared_count = 0
        share_removed: List[str] = []

        if vt and vt.lower() != "primary" and shared:
            # Only panes that are allowed to be shared (from common_infopanes_list)
            common_infopanes = set(frm_config.get_common_infopanes_list())

            # Map pane name -> attribute name on `shared`
            pane_flag_attrs = {
                "itinerary_accomodation": "itinerary_same",
                "accomodation": "accommodation_same",
                "ticketing": "flight_ticket_same",
            }

            mapping = []
            for pane_name, attr_name in pane_flag_attrs.items():
                if pane_name in common_infopanes:
                    flag = getattr(shared, attr_name, None)
                    mapping.append((pane_name, flag))

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
            frm_config.get_relevant_infopane_list(),
            panes_to_check,
            share_removed,
            shared_count,
        )

        # 3) Status scan with detailed tracking
        completed = 0
        completed_panes: List[str] = []
        incomplete_panes: List[str] = []
        missing_attrs: List[str] = []

        for pane_name in panes_to_check:
            pane: BaseModel = getattr(form, pane_name, None)
            if pane is None:
                missing_attrs.append(pane_name)
                continue
            pane_dict: dict = pane.model_dump(exclude_none=True)
            if _has_success_ver_status(pane_dict):
                completed += 1
                completed_panes.append(pane_name)
            else:
                # Optional: capture the status we saw for easier debugging
                status = pane_dict.get("_ver_status", {}).get("status")
                incomplete_panes.append(f"{pane_name} (status={status!r})")

        logger.info(
            "pct_completion: panes_considered=%s | panes_completed=%s | panes_incomplete=%s | missing_attrs=%s",
            panes_to_check,
            completed_panes,
            incomplete_panes,
            missing_attrs,
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
            total,
            completed,
            pct_str,
        )

        # 6) Write back into lets_get_started
        if not getattr(form, "lets_get_started", None):
            form.lets_get_started = RootLetsGetStarted()

        form.lets_get_started.infopanes_total = total
        form.lets_get_started.infopanes_completed = completed
        form.lets_get_started.pct_completion = pct_str

        return GenericFormRecordModel.model_validate(form.model_dump())
