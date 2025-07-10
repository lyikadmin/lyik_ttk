import json
import logging
from functools import lru_cache
from typing import List, Dict
from pathlib import Path
from lyikpluginmanager import PluginException

logger = logging.getLogger(__name__)


class AddonLoader:

    def __init__(self, file_path: str):
        self.file_path = Path(file_path).resolve()

    @lru_cache()
    def load_addons(self) -> List[Dict]:
        """
        Loads add-on data from a JSON file and caches it using LRU.
        Returns:
            List of add-on entries as dictionaries.
        """
        try:
            if not self.file_path.exists():
                logging.error(f"File not found: {self.file_path}")
                raise PluginException(
                    message="Internal error occurred.",
                    detailed_message=f"File not found: {self.file_path}",
                )

            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not data or not isinstance(data, list):
                logging.warning("Expected list at root of JSON")
                raise PluginException(
                    message="Internal error occurred.",
                    detailed_message="Invalid JSON structure. Expected list at root of JSON.",
                )

            logging.info(f"Loaded {len(data)} add-ons from {self.file_path}")
            return data

        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error in {self.file_path}: {e}")
            raise
        except Exception as e:
            logging.exception(
                f"Unexpected error while loading add-ons from {self.file_path}"
            )
            raise
