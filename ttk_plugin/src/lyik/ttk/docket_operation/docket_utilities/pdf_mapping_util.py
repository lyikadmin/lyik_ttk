from lyik.ttk.utils.form_indicator import FormIndicator
from lyik.ttk.docket_operation.docket_utilities.singapore_pdf_mapping import (
    map_singapore_to_pdf,
)
from lyik.ttk.docket_operation.docket_utilities.mexico_pdf_mapping import map_mexico_pdf
from lyik.ttk.docket_operation.docket_utilities.japan_pdf_mapping import map_japan_pdf
from lyik.ttk.docket_operation.docket_utilities.egypt_pdf_mapping import map_egypt_pdf


class PDFMappingUtil:
    """Utility to dynamically map form data to PDF structures based on form indicator."""

    # Registry: indicator → mapper function
    _MAPPERS = {
        FormIndicator.SGP_SINGAPORE: map_singapore_to_pdf,
        FormIndicator.MEX_MEXICO: map_mexico_pdf,
        FormIndicator.JPN_JAPAN: map_japan_pdf,
        FormIndicator.EGY_EGYPT: map_egypt_pdf,
    }

    def __init__(self, form_data: dict):
        self.form_data = form_data

    def get_mapped_data(self, form_indicator):
        """Return the mapped PDF data for the given form indicator."""
        mapper = self._MAPPERS.get(form_indicator)

        if not mapper:
            raise ValueError(f"No PDF mapper registered for: {form_indicator}")

        return mapper(form_data=self.form_data)
