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
from lyikpluginmanager.core.utils import StrEnum
from typing_extensions import Doc

from lyik.ttk.models.generated.universal_model_with_submission_requires_docket_status import (
    UniversalModelWithSubmissionRequiresDocketStatus,
    RootLetsGetStarted,
    DOCKETSTATUS,
)  # adjust path

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


class DisplayStatus(StrEnum):
    """
    1	A Record is created	New
    2	Traveller started filling the record	In Progress
    3	Maker Chooses "Submit application for additional review"	In Progress
    4	Maker Chooses: Enable Docket	Completed
    5	Checker Approved	Completed
    6	Checker Discrepancy	In Review
    """

    NEW = "New"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    IN_REVIEW = "In Review"


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
            form = UniversalModelWithSubmissionRequiresDocketStatus(
                **payload.model_dump()
            )
        except Exception as exc:
            logger.error("form_status_display: cannot parse payload - %s", exc)
            return payload

        if not current_state:
            current_state = ""

        if not form.lets_get_started:
            form.lets_get_started = RootLetsGetStarted()

        form_display_status = form.lets_get_started.form_status

        if action.value == "SAVE":
            form_display_status = DisplayStatus.IN_PROGRESS

        if not previous_state:
            form_display_status = DisplayStatus.NEW

        if action.value == "SUBMIT" or current_state == "SUBMIT":
            if (
                form.submit_info
                and form.submit_info.docket
                and form.submit_info.docket.docket_status
            ):
                if (
                    form.submit_info.docket.docket_status
                    == DOCKETSTATUS.ADDITIONAL_REVIEW
                ):
                    form_display_status = DisplayStatus.IN_PROGRESS
                elif (
                    form.submit_info.docket.docket_status
                    == DOCKETSTATUS.ENABLE_DOWNLOAD
                ):
                    form_display_status = DisplayStatus.COMPLETED

        if current_state == "APPROVED":
            form_display_status = DisplayStatus.COMPLETED

        if current_state == "DISCREPANCY":
            form_display_status = DisplayStatus.IN_REVIEW

        form.lets_get_started.form_status = form_display_status

        data_dict = form.model_dump()

        # 4)  Return updated record
        return GenericFormRecordModel.model_validate(data_dict)

        # # If no state at all, set it to 'INITIALIZED'
        # if not current_state:
        #     form_state = "INITIALIZED"
        # else:
        #     form_state = current_state

        # if action.value == "SUBMIT":
        #     form_state = "SUBMIT"

        # # 2)  Look up human label
        # user_friendly_label = _DISPLAY_STATE.get(form_state, form_state or "INITIALIZED")

        # # 3)  get the lets_get_started dict value
        # # 3.1) add/update the user understandable message as per the form state
        # if not form.lets_get_started:
        #     form.lets_get_started = RootLetsGetStarted()

        # form.lets_get_started.form_status = user_friendly_label

        # data_dict = form.model_dump()

        # # 4)  Return updated record
        # return GenericFormRecordModel.model_validate(data_dict)
