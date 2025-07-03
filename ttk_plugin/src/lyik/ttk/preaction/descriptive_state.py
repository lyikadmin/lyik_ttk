# plugins/progress/form_status_display.py
from __future__ import annotations

import logging
from typing import Annotated, Dict, Any

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
    "INITIALIZED": "Form Initialized"
}

class FormStatusDisplay(PreActionProcessorSpec):
    """
    Converts the technical *state* into a user-friendly text and stores it
    under ``lets_get_started.form_status`` in a payload.
    """

    @impl
    async def pre_action_processor(
        self,
        context: ContextModel,
        action: Annotated[str, "Sates of actions"],
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
            # 1.1) Get the payload in a dict format
            data_dict = form.model_dump()
        except Exception as exc:
            logger.error("form_status_display: cannot parse payload - %s", exc)
            data = payload.model_dump()
            return GenericFormRecordModel.model_validate(data)

        # If no state at all, set it to 'INITIALIZED'
        if not data_dict.get("state"):
            data_dict["state"] = "INITIALIZED"

        # 2)  Look up human label
        form_state: str | None = data_dict["state"]
        user_friendly_label = _DISPLAY_STATE.get(form_state, form_state or "INITIALIZED")

        # 3)  get the lets_get_started dict value
        # 3.1) add/update the user understandable message as per the form state
        if not isinstance(data_dict.get("lets_get_started"), dict):
            data_dict["lets_get_started"] = {}

        lgs: Dict[str, Any] = data_dict["lets_get_started"]
        lgs["form_status"] = user_friendly_label


        # 4)  Return updated record
        return GenericFormRecordModel.model_validate(data_dict)