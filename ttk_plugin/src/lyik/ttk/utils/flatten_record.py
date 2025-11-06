import json
from pathlib import Path


class JSONFlattener:
    """
    A utility class for flattening nested JSON structures into a single-level dictionary.

    This class can be used to flatten deeply nested JSON files or Python dictionaries.
    """

    def __init__(self, separator: str = "."):
        """
        :param separator: String used to join nested keys (default is '.').
        """
        self.separator = separator

    def flatten(self, data: dict, parent_key: str = "") -> dict:
        """
        Recursively flatten a nested dictionary or list.

        :param data: The JSON object (dict or list) to flatten.
        :param parent_key: Internal use only; used to track nested keys during recursion.
        :return: A flat dictionary where nested keys are joined by the separator.
        """
        items = {}
        try:
            if isinstance(data, dict):
                for key, value in data.items():
                    new_key = (
                        f"{parent_key}{self.separator}{key}" if parent_key else key
                    )
                    items.update(self.flatten(value, new_key))
            elif isinstance(data, list):
                for i, value in enumerate(data):
                    new_key = f"{parent_key}[{i}]"
                    items.update(self.flatten(value, new_key))
            else:
                items[parent_key] = data
        except Exception as e:
            raise
        return items
