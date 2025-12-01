from lyik.ttk.utils.form_indicator import FormIndicator
from .csv_utils import load_csv_rows
import os
from typing import List, Dict

from pydantic import BaseModel
from lyik.ttk.utils.form_indicator import FormIndicator
from .csv_utils import load_csv_rows
import os
from typing import List, Dict, Optional, Literal

from pydantic import BaseModel


class FormConfigRow(BaseModel):
    """
    Represents one row from the form_config CSV.

    Expected CSV headers:
    - relevant_infopanes
    - business_panes
    - common_infopanes
    - submit_requirement
    - has_appointment_section
    - has_submission_docket_status_requirement
    """

    relevant_infopanes: Optional[str] = None
    business_panes: Optional[str] = None
    common_infopanes: Optional[str] = None
    submit_requirement: Optional[str] = None
    has_appointment_section: Optional[str] = None
    has_submission_docket_status_requirement: Optional[str] = None



COMMON_INFOPANES = Literal["itinerary_accomodation", "accomodation", "ticketing"]


class FormConfig:
    def __init__(self, form_indicator: FormIndicator):
        self.form_indicator = form_indicator

        raw_rows = self.load_form_config_file()

        # parsed list
        self._rows: List[FormConfigRow] = [FormConfigRow(**row) for row in raw_rows]

        # derived fields
        self._relevant_infopanes: List[str] = []
        self._business_panes: List[str] = []
        self._common_infopanes: List[COMMON_INFOPANES] = []
        self._submit_requirement: List[str] = []
        self._has_appointment_section: bool = False
        self._has_submission_docket_status_requirement: bool = False

        self._parse_rows()

    def load_form_config_file(self) -> List[Dict[str, str]]:
        mount_path = os.getenv("CRED_FILES_MOUNT_PATH")

        if not mount_path:
            raise ValueError(f"Missing CRED_FILES_MOUNT_PATH")

        form_config_dir = os.path.join(mount_path, "form_config")

        if not os.path.exists(form_config_dir):
            raise FileNotFoundError(
                f"Form Config directory not found: {form_config_dir}"
            )

        expected_filename = f"{self.form_indicator.value}.csv"
        form_config_csv_file_path = os.path.join(form_config_dir, expected_filename)

        if not os.path.isfile(form_config_csv_file_path):
            raise FileNotFoundError(
                f"Form Config CSV file not found: {form_config_csv_file_path}"
            )

        return load_csv_rows(form_config_csv_file_path)

    @staticmethod
    def _parse_bool(value: Optional[str]) -> Optional[bool]:
        if not value:
            return None
        v = value.strip().lower()
        if v in ("true", "yes", "y", "1"):
            return True
        if v in ("false", "no", "n", "0"):
            return False
        return None

    def _parse_rows(self) -> None:
        """
        - First 3 columns → aggregated into lists across all rows.
        - Last 2 columns → take first non-empty boolean value.
        """
        for row in self._rows:
            # list columns (1 value per row)
            if row.relevant_infopanes:
                self._relevant_infopanes.append(row.relevant_infopanes)

            if row.business_panes:
                self._business_panes.append(row.business_panes)

            if row.common_infopanes:
                self._common_infopanes.append(row.common_infopanes)

            if row.submit_requirement:
                self._submit_requirement.append(row.submit_requirement)

            # boolean columns (first non-empty wins)
            if (not self._has_appointment_section) and row.has_appointment_section:
                parsed = self._parse_bool(row.has_appointment_section)
                if parsed is not None:
                    self._has_appointment_section = parsed

            if (
                not self._has_submission_docket_status_requirement
                and row.has_submission_docket_status_requirement
            ):
                parsed = self._parse_bool(row.has_submission_docket_status_requirement)
                if parsed is not None:
                    self._has_submission_docket_status_requirement = parsed

    # ----- Public API -----

    def get_relevant_infopane_list(self) -> List[str]:
        """
        Get the list of infopanes which are relevant for percentage completion.
        """
        return self._relevant_infopanes

    def get_business_panes_list(self) -> List[str]:
        """
        Get the infopanes which are business type, which are only used if the visa mode is business.
        """
        return self._business_panes

    def get_common_infopanes_list(self) -> List[COMMON_INFOPANES]:
        """
        Get the shared common infopanes list (Shared between the primary and co-traveller).
        """
        return self._common_infopanes
    
    def get_submit_requirement_list(self) -> List[str]:
        """
        Get the dot separated path of checkbox fields which must be checked before submitting the application
        """
        return self._submit_requirement


    def has_appointment_section(self) -> bool:
        "True if the form has an appointment section"
        return self._has_appointment_section

    def has_submission_docket_status_requirement(self) -> bool:
        "True if the form can only be submit based on docket being enabled in submit infopane."
        return self._has_submission_docket_status_requirement
