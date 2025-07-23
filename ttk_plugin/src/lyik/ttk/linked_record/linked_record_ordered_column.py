import os
import logging
from typing import List, Dict, OrderedDict
from collections import OrderedDict

from typing_extensions import Annotated, Doc
from lyikpluginmanager import ContextModel
from lyikpluginmanager.annotation import RequiredEnv, RequiredVars
import apluggy as pluggy

from ..utils.loader_utils import LinkRecordOrderedMappingLoader
from lyikpluginmanager import getProjectName
from lyikpluginmanager.core import LinkRecordOrderSpec

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

impl = pluggy.HookimplMarker(getProjectName())

class LinkRecordColumnOrderPlugin(LinkRecordOrderSpec):
    @impl
    async def get_ordered_column_mapping(
        self,
        context: ContextModel,
    ) -> Annotated[
        OrderedDict | None,
        RequiredEnv(["CRED_FILES_MOUNT_PATH", "LINK_RECORD_ORDER_FILE"]),
        RequiredVars([]),
        Doc("The ordered mapping of column names to display titles."),
    ]:
        try:
            mount_path = os.getenv("CRED_FILES_MOUNT_PATH")
            file_name = os.getenv("LINK_RECORD_ORDER_FILE")

            if not mount_path or not file_name:
                logger.error("CRED_FILES_MOUNT_PATH or LINK_RECORD_ORDER_FILE is not set.")
                return None

            file_path = os.path.join(mount_path, file_name)
            loader = LinkRecordOrderedMappingLoader(file_path=file_path)
            config_data = loader.load_link_record_mapping_config()

            if not config_data.get("enable", False):
                logger.info("Link record column mapping is globally disabled.")
                return None

            ordered_fields = sorted(
                [
                    (entry["order"], entry["link_attribute"], entry["title"])
                    for entry in config_data.get("order", [])
                    if entry.get("enable", False)
                    and not entry["link_attribute"].startswith("_")
                ],
                key=lambda x: x[0],
            )

            if not ordered_fields:
                logger.info("No valid enabled fields found in the config.")
                return None

            return OrderedDict((field, title) for _, field, title in ordered_fields)

        except Exception as e:
            logger.exception(f"Error while building ordered mapping: {e}")
            return None