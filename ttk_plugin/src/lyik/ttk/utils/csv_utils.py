import csv
from typing import List, Dict
from functools import lru_cache

@lru_cache(maxsize=32)
def load_csv_rows(file_path: str) -> List[Dict[str, str]]:
    """
    Generic CSV loader.

    - Reads CSV using utf-8 encoding
    - Returns a list of row dicts from csv.DictReader
    - Does NOT apply any domain-specific sorting or coercion
    - Cached for repeated access to the same file_path
    """
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Materialize as list so the cached value is reusable
        return list(reader)


    
