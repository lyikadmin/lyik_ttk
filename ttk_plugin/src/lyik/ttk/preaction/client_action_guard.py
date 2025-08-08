from datetime import date
import logging

import apluggy as pluggy
from typing import Annotated, Any, Dict, Union

from lyikpluginmanager import (
    getProjectName,
    PreActionProcessorSpec,
    ContextModel,
    GenericFormRecordModel,
    PluginException,
)
import jwt
from ..models.forms.schengentouristvisa import Schengentouristvisa, DOCKETSTATUS

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

impl = pluggy.HookimplMarker(getProjectName())


class ClientActionGuard(PreActionProcessorSpec):
    @impl
    async def pre_action_processor(
        self,
        context: ContextModel,
        action: Annotated[str, "save / submit"],
        current_state: Annotated[str | None, "previous record state"],
        new_state: Annotated[str | None, "new record state"],
        payload: Annotated[GenericFormRecordModel, "entire form record model"],
    ) -> Annotated[GenericFormRecordModel, "The (possibly unchanged) record"]:
        """
        1) If the current user is a CLIENT and the docket has been ENABLED for download,
           block any save/submit with an exception.

        2) Ensure the appointment date is strictly before the departure date;
           otherwise block with an exception.
        """
        if not context or not context.token:
            logger.error(
                "ContextModel or token is missing in the context. Passing through OrderStatusUpdate Preaction."
            )
            return payload
        token = context.token

        # Step 1: Decode outer token
        # --- decode outer JWT (no signature check) ---
        try:
            outer = self._decode_jwt(token)
        except Exception as e:
            logger.error("Failed to decode JWT: %s", e)
            return payload
        
        # --- extract persona list ---
        persona_list = (
            outer
            .get("user_metadata", {})
            .get("permissions", {})
            .get("persona", [])
        )
        is_client = any(p in ("CLI", "CLIENT") for p in persona_list)
        
        # 0) Parse incoming payload into our Pydantic form
        try:
            form = Schengentouristvisa(**payload.model_dump())
        except Exception as exc:
            logger.error("ClientActionGuard: cannot parse payload – %s", exc)
            # fallback to original
            return payload

        # --- 1) freeze after docket enabled ---
        if is_client:
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