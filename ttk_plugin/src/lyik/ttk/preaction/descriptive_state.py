# plugins/progress/form_status_display.py
from __future__ import annotations

import logging
from typing import Annotated

import apluggy as pluggy
from lyikpluginmanager import (
    ContextModel,
    GenericFormRecordModel,
    PreActionProcessorSpec,
    getProjectName,
)
from typing_extensions import Doc

from ..models.forms.new_schengentouristvisa import Schengentouristvisa  # adjust path

logger = logging.getLogger(__name__)
impl = pluggy.HookimplMarker(getProjectName())

_DISPLAY_STATE: dict[str, str] = {
    "SAVE":         "Form Saved",
    "SUBMIT":       "Form Submitted",
    "APPROVED":     "Form Approved",
    "DISCREPANCY":  "Form Needs Attention",
    "COMPLETED":    "Application Completed",
}

class FormStatusDisplay(PreActionProcessorSpec):
    """
    Converts the technical *state* into a user-friendly text and stores it
    under ``lets_get_started.form_status``.
    """

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
        Doc("form record with lets_get_started.form_status refreshed"),
    ]:
        # 1)  Parse into strongly-typed model (defensive – won’t break save)
        try:
            form = Schengentouristvisa(**payload.model_dump())
        except Exception as exc:
            logger.error("form_status_display: cannot parse payload - %s", exc)

        # 2)  Look up human label
        sys_state: str | None = action
        human_label = _DISPLAY_STATE.get(sys_state, sys_state or "Unknown State")

        # 3)  Persist under lets_get_started.form_status
        data_dict = form.model_dump()
        lgs = data_dict.setdefault("lets_get_started", {})
        # if lets_get_started is itself a nested model, convert to dict first

        lgs["form_status"] = human_label

        # 4)  Return updated record
        return GenericFormRecordModel.model_validate(data_dict)