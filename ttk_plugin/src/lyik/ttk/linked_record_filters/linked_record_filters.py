import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    LinkedRecordFilterSpec,
    PluginException,
)
from typing import Annotated, Dict
from typing_extensions import Doc
import logging
import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError
from typing import Dict, Any, Union


logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())


class CustomLinkedRecordFiltersPlugin(LinkedRecordFilterSpec):
    """
    This Plugin extract filters from a source, usually a token, and returns it.
    """

    @impl
    async def get_custom_linked_record_filters(
        self,
        context: ContextModel,
    ) -> Annotated[Dict, Doc("This is the extracted filters dictionary.")]:
        "Function to extract the filters and return."

        logger.info("Started extracting the filters.")
        try:
            if not context:
                raise PluginException(
                    message="Internal configuration error. Please contact support.",
                    detailed_message="ContextModel is missing.",
                )
            if not context.token:
                raise PluginException(
                    message="Internal configuration error. Please contact support.",
                    detailed_message="Token is missing in the context.",
                )
            token = context.token

            # Get the filters from the token.
            filters: Dict = self.get_filters_from_token(token=token)

            if not filters:
                logger.info("No filter found in the token.")

            return filters
        except PluginException as pe:
            logger.error(pe.detailed_message)
            raise
        except Exception as e:
            logger.error(f"Something went wrong: {e}")
            raise

    def get_filters_from_token(self, token: str) -> Dict[str, Any]:
        # Step 1: Decode outer token
        outer_payload = self._decode_jwt(token=token)

        # Step 2: Search for 'token'
        inner_token = self.find_token_field(outer_payload)

        if not inner_token:
            raise PluginException(
                message="Internal error occurred. Please contact support.",
                detailed_message="TTK Token not found.",
            )

        # Step 3: Decode inner JWT token
        inner_payload = self._decode_jwt(inner_token)

        # Step 4: Extract 'filter' key
        if "filter" not in inner_payload:
            raise PluginException(
                message="Internal error occurred. Please contact support.",
                detailed_message="No 'filter' key found in TTK Token.",
            )

        return inner_payload["filter"]

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
