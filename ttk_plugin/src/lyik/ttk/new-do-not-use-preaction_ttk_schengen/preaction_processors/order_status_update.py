from __future__ import annotations

import logging
from typing import Annotated, Dict, Any, Union

import apluggy as pluggy
from lyikpluginmanager import (
    ContextModel,
    GenericFormRecordModel,
    getProjectName,
    PluginException,
)
import jwt
from lyikpluginmanager.annotation import RequiredEnv
from typing_extensions import Doc
import os
import httpx

from ...models.forms.schengentouristvisa import Schengentouristvisa
from ._base_preaction import BasePreActionProcessor

logger = logging.getLogger(__name__)
impl = pluggy.HookimplMarker(getProjectName())


class PreactionOrderStatusUpdate(BasePreActionProcessor):
    async def pre_action_processor(
        self,
        context: ContextModel,
        action: Annotated[str, "Save / Submit"],
        current_state: Annotated[str | None, "Previous record state"],
        new_state: Annotated[str | None, "New record state"],
        payload: Annotated[GenericFormRecordModel, "Entire form record model"],
    ) -> Annotated[
        GenericFormRecordModel,
        RequiredEnv(["TTK_API_BASE_URL"]),
        Doc("Form record"),
    ]:
        "This plugin will update the order / progree status in the TTK Appication."
        try:

            if not context or not context.token:
                logger.error(
                    "ContextModel or token is missing in the context. Passing through OrderStatusUpdate Preaction."
                )
                return payload
            token = context.token

            api_prefix = os.getenv("TTK_API_BASE_URL")
            if not api_prefix:
                logger.error(
                    "Api prefix is missing. Skipping OrderStatusUpdate Preaction process."
                )
                return payload

            order_status_update_api = api_prefix + "api/v2/orderUpdate/"

            # Step 1: Decode outer token
            outer_payload = self._decode_jwt(token=token)

            # Step 2: Search for 'token'
            inner_token = self.find_token_field(outer_payload)
            if not inner_token:
                logger.error("Inner token not found in the decoded payload.")
                return payload

            parsed_form_rec = Schengentouristvisa(**payload.model_dump())

            body = {
                "orderId": parsed_form_rec.visa_request_information.visa_request.order_id,
                "completedSection": parsed_form_rec.infopanes_completed,
                "totalSection": parsed_form_rec.infopanes_total,
                "travellerId": "",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    order_status_update_api,
                    json=body,
                    headers={"Authorization": f"Bearer {inner_token}"},
                )

                try:
                    response_json = response.json()
                except Exception as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    return payload

                if response_json.get("status") != "success":
                    logger.error(
                        f"Order status update API returned error status. Full response: {response_json}"
                    )
                else:
                    logger.info("Order status update API call successful.")

            return payload
        except PluginException as pe:
            logger.error(pe.detailed_message)
            return payload
        except Exception as e:
            logger.error(
                f"Unhandles exception raised during OrderStatusUpdate preaction process. Error: {str(e)}"
            )
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

    def find_token_field(self, data: Dict[str, Any]) -> Union[str, None]:
        if isinstance(data, dict):
            provider_info = data.get("provider_info")
            if isinstance(provider_info, dict):
                token = provider_info.get("token")
                if isinstance(token, str):
                    return token

        return None
