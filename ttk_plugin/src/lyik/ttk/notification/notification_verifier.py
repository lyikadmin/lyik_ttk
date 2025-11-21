import apluggy as pluggy
import os
import jwt
import logging
import requests
from typing import Any, Dict, Annotated
from pydantic import BaseModel

from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    VerifyHandlerSpec,
    VerifyHandlerResponseModel,
    VERIFY_RESPONSE_STATUS,
    PluginException,
)
from lyik.ttk.models.forms.schengentouristvisa import Schengentouristvisa, RootCoverLetterInfoSendEmail
from lyikpluginmanager.annotation import RequiredEnv
from typing_extensions import Doc
from lyik.ttk.utils.message import get_error_message

logger = logging.getLogger(__name__)
impl = pluggy.HookimplMarker(getProjectName())

COVERING_LETTER_KEY = "COVERING_LETTER"
INVITATION_LETTER_KEY = "INVITATION_LETTER"

notification_type_map = {
    COVERING_LETTER_KEY: "Covering Letter",
    INVITATION_LETTER_KEY: "Invitation Letter"
}

class NotificationVerifier(VerifyHandlerSpec):
    """
    CTA Verifier that calls TTK Notification API (POST api/v2/notification)
    with a hardcoded message: 'Example Notification message'.
    """

    @impl
    async def verify_handler(
        self,
        context: ContextModel,
        payload: Annotated[
            RootCoverLetterInfoSendEmail,
            Doc("Optional payload. If it contains orderId, we will use it."),
        ],
    ) -> Annotated[
        VerifyHandlerResponseModel,
        RequiredEnv(["TTK_API_BASE_URL", "TTK_NOTIFICATION_API_ROUTE"]),
        Doc("Calls notification API"),
    ]:
        try:
            if not context or not context.config:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="Missing context or config.",
                )
            if not context.token:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="Missing outer JWT context.token.",
                )
            
            notification_type = COVERING_LETTER_KEY

            if isinstance(payload, BaseModel):
                notification_type = payload.notification_type   
            elif isinstance(payload, dict):
                notification_type = payload.get("notification_type", COVERING_LETTER_KEY)

            section_name = notification_type_map.get(notification_type, "Unknown")

            # Extract ttk token from outer JWT
            ttk_token = self._extract_ttk_token(context.token)
            if not ttk_token:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="TTK token not found inside provider_info.token.",
                )

            # Build URL from envs 
            base_url = os.getenv("TTK_API_BASE_URL", "").rstrip("/")
            route = os.getenv("TTK_NOTIFICATION_API_ROUTE", "").lstrip("/")
            if not base_url or not route:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message="Environment variables TTK_API_BASE_URL or TTK_NOTIFICATION_API_ROUTE are missing.",
                )
            url = f"{base_url}/{route}"

            order_id = None

            if context.record:
                # Adjust the path below to your record structure if needed.
                # Get the order_id from the record
                full_form_record = Schengentouristvisa(**context.record)
                order_id = (
                    full_form_record.visa_request_information.visa_request.order_id
                )

            if not order_id:
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message=f"Notification API call failed. Could not find the Order ID for this record.",
                )

            # --- Compose request ----------------------------------------------
            body = {
                "orderId": order_id,
                "sectionName": section_name,
                "notificationType": "Document",
                "notificationMessage": f"The {section_name} has been generated for your Order: '{order_id}'.",
            }
            headers = {
                "Authorization": f"Bearer {ttk_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            logger.info(f"Calling Notification API: {url} with orderId={order_id}")
            resp = requests.post(url, json=body, headers=headers, timeout=20)

            # --- Handle response ----------------------------------------------
            if not resp.ok:
                detail = f"HTTP {resp.status_code}: {resp.text[:400]}"
                raise PluginException(
                    message=get_error_message(
                        error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                    ),
                    detailed_message=f"Notification API call failed. {detail}",
                )

            data = {}
            try:
                data = resp.json()
                logger.info(f"Details from Notification API: {data}")
            except Exception:
                # If API returns non-JSON body
                data = {"raw": resp.text}

            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.DATA_ONLY,
                actor="system",
                message="Notification Sent successfully.",
            )

        except PluginException as pe:
            logger.error(pe)
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                actor="system",
                message=pe.message,
            )
        except Exception as e:
            logger.exception("Unexpected error in NotificationVerifier")
            return VerifyHandlerResponseModel(
                status=VERIFY_RESPONSE_STATUS.FAILURE,
                actor="system",
                message=get_error_message(
                    error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                ),
            )

    # ----------------------------- helpers -----------------------------------

    def _extract_ttk_token(self, outer_jwt: str) -> str:
        """
        Decodes the outer JWT (no signature verification) and returns provider_info.token if present.
        """
        try:
            payload = jwt.decode(
                outer_jwt, algorithms=["HS256"], options={"verify_signature": False}
            )
            provider_info = payload.get("provider_info") or {}
            token = provider_info.get("token")
            if isinstance(token, str) and token.strip():
                return token.strip()
        except Exception as e:
            logger.error(f"Failed to decode outer JWT: {e}")
        return ""
