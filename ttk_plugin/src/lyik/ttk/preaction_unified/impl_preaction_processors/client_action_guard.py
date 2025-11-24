from datetime import date
import logging

import apluggy as pluggy
from typing import Any, Dict, Union
from typing_extensions import Doc, Annotated

from lyikpluginmanager import (
    ContextModel,
    GenericFormRecordModel,
    PluginException,
)
import jwt
from lyik.ttk.models.generated.universal_model_with_submission_requires_docket_status import UniversalModelWithSubmissionRequiresDocketStatus, DOCKETSTATUS
from lyik.ttk.utils.form_indicator import FormIndicator
from .._base_preaction import BaseUnifiedPreActionProcessor

from lyik.ttk.utils.form_utils import has_submission_docket_status_requirement

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ClientActionGuard(BaseUnifiedPreActionProcessor):
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
    ) -> Annotated[GenericFormRecordModel, "The (possibly unchanged) record"]:
        """
        1) If the current user is a CLIENT and the docket has been ENABLED for download,
           block any save/submit with an exception.
           NOTE: Only for forms which are applicable to have docket submission requirement.
        """
        if not context or not context.token:
            logger.error(
                "ContextModel or token is missing in the context. Passing through OrderStatusUpdate Preaction."
            )
            return payload
        token = context.token

        if not has_submission_docket_status_requirement(form_indicator=form_indicator):
            return payload

        # Step 1: Decode outer token
        # --- decode outer JWT (no signature check) ---
        try:
            outer = self._decode_jwt(token)
        except Exception as e:
            logger.error("Failed to decode JWT: %s", e)
            return payload

        # --- extract persona list ---
        persona_list = (
            outer.get("user_metadata", {}).get("permissions", {}).get("persona", [])
        )
        is_client = any(p in ("CLI", "CLIENT") for p in persona_list)

        # 0) Parse incoming payload into our Pydantic form
        try:
            form = UniversalModelWithSubmissionRequiresDocketStatus(**payload.model_dump())
        except Exception as exc:
            logger.error("ClientActionGuard: cannot parse payload – %s", exc)
            # fallback to original
            return payload

        # --- 1) freeze after docket enabled ---
        if is_client and has_submission_docket_status_requirement(form_indicator=form_indicator):
            ds = None
            if form.submit_info and form.submit_info.docket:
                ds = form.submit_info.docket.docket_status
            if ds in (DOCKETSTATUS.ENABLE_DOWNLOAD, "ENABLE_DOWNLOAD"):
                raise PluginException(
                    "Once your docket has been enabled for download, you may no longer save or submit this application."
                )

        # Nothing to modify – hand back the original record
        return payload

    def _decode_jwt(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token, algorithms=["HS256"], options={"verify_signature": False}
            )
            return payload
        except Exception as e:
            raise PluginException(
                message="Internal error occurred. Please contact support.",
                detailed_message=f"Something went wrong while decoding payload: {e}",
            )
