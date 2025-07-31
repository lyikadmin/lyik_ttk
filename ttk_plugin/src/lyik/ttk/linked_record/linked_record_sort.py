import logging
from collections import OrderedDict

from typing_extensions import Annotated, Doc
from lyikpluginmanager import ContextModel
import apluggy as pluggy

from lyikpluginmanager import getProjectName
from lyikpluginmanager.core import LinkRecordSortSpec, SortOrder

logger = logging.getLogger(__name__)

impl = pluggy.HookimplMarker(getProjectName())


class LinkedRecordSortPlugin(LinkRecordSortSpec):
    @impl
    async def sort_linked_records(self, context: ContextModel) -> Annotated[
        OrderedDict[str, SortOrder] | None,
        Doc(
            "This is the sort mapping, where key is the source field name and value is the sort order."
        ),
    ]:
        sort_mapping = OrderedDict()

        sort_mapping["Order ID"] = SortOrder.ASC
        sort_mapping["Traveller Type"] = SortOrder.DESC

        return sort_mapping
