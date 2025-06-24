import apluggy as pluggy
from lyikpluginmanager import (
    getProjectName,
    ContextModel,
    LinkedRecordFilterSpec,
    PluginException,
    LinkRecordFilter,
)
from typing import Annotated, Dict
from typing_extensions import Doc
import logging
import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError
from typing import Any, Union


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
    ) -> Annotated[
        LinkRecordFilter, Doc("The response contains the filters with filter types.")
    ]:
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
            filters: LinkRecordFilter = self.get_filters_from_token(token=token)

            return filters
        except PluginException as pe:
            logger.error(pe.detailed_message)
            raise
        except Exception as e:
            logger.error(f"Something went wrong: {e}")
            raise

    def get_filters_from_token(self, token: str) -> LinkRecordFilter:
        """
        Extracts filtering criteria from the TTK JWT token and builds a LinkRecordFilter.
        The plugin knows internally which keys to extract and how to classify them.

        Returns:
            A LinkRecordFilter instance.
        """
        # 🔧 Plugin-defined config: key → filter type
        key_classification: Dict[str, str] = {}
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
        inner_token_payload = self._decode_jwt(token=inner_token)

        # Step 4: Build the filter model using known classification
        filter_data: Dict[str, Dict[str, str]] = {}

        for key, filter_type in key_classification.items():
            if key in inner_token_payload:
                val = inner_token_payload[key]
                filter_data.setdefault(filter_type, {})[key] = str(val)
            else:
                logger.error(f"The {key} is not present in the token. Skipped.")

        if not any(filter_data.values()):
            logger.info("No filter found in the token.")

        return LinkRecordFilter(**filter_data)

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
