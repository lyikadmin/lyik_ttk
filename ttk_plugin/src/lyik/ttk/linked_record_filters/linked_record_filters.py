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

    def get_filters_from_token(self, token: str) -> Dict:
        # Todo: Extract filters from the token and return it.

        # Dummy filter
        filters = {}

        return filters
