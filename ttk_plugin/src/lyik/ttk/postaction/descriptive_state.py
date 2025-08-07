# plugins/progress/form_status_display.py
from __future__ import annotations

import logging
from typing import Annotated, Dict, Any

import apluggy as pluggy
from lyikpluginmanager import (
    ContextModel,
    GenericFormRecordModel,
    PostActionProcessorSpec,
    getProjectName,
)
from typing_extensions import Doc

from ..models.forms.new_schengentouristvisa import Schengentouristvisa, RootLetsGetStarted  # adjust path

logger = logging.getLogger(__name__)
impl = pluggy.HookimplMarker(getProjectName())

_DISPLAY_STATE: dict[str, str] = {
    "SAVE": "Saved",
    "SUBMIT": "Completed",
    "APPROVED": "Approved",
    "DISCREPANCY": "Needs Correction",
    "COMPLETED": "Finalised",
    "INITIALIZED": "Form Created",
}

class FormStatusDisplay(PostActionProcessorSpec):
    """
    Converts the technical *state* into a user-friendly text and stores it
    under ``lets_get_started.form_status`` in a payload.
    """

    @impl
    async def post_action_processor(
        self,
        context: ContextModel,
        action: Annotated[str, "Sates of actions"],
        previous_state: Annotated[str | None, "previous record state"],
        current_state: Annotated[str | None, "new record state"],
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
            return payload

        # If no state at all, set it to 'INITIALIZED'
        if not current_state:
            form_state = "INITIALIZED"
        else:
            form_state = current_state


        if action.value == "SUBMIT":
            form_state = "SUBMIT"

        # 2)  Look up human label
        user_friendly_label = _DISPLAY_STATE.get(form_state, form_state or "INITIALIZED")

        # 3)  get the lets_get_started dict value
        # 3.1) add/update the user understandable message as per the form state
        if not form.lets_get_started:
            form.lets_get_started = RootLetsGetStarted()

        form.lets_get_started.form_status = user_friendly_label

        data_dict = form.model_dump()

        # 4)  Return updated record
        return GenericFormRecordModel.model_validate(data_dict)
