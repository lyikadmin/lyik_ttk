from typing import Optional
from ...models.forms.new_schengentouristvisa import (
    Schengentouristvisa,
)
from ...models.pdf.pdf_model import EditableForm
import logging

logger = logging.getLogger(__name__)


class DocketUtilities:

    def map_schengen_to_editable_form(
        self,
        schengen_visa_data: Schengentouristvisa,
    ) -> EditableForm:
        """
        Maps relevant fields from a SchengenTouristVisa model instance to an EditableForm instance.

        Args:
            schengen_visa_data (SchengenTouristVisa): The input model containing the source data.

        Returns:
            EditableForm: A new instance populated with values from the SchengenTouristVisa model.
        """
        my_editable_form = EditableForm()

        try:
            passport_details = schengen_visa_data.passport.passport_details

            my_editable_form.visa_first_name = passport_details.first_name or ""
            my_editable_form.visa_cob = passport_details.date_of_birth or ""
            my_editable_form.visa_dob = passport_details.date_of_birth or ""
            my_editable_form.visa_pob = passport_details.place_of_birth or ""
            my_editable_form.visa_issued_by_ctry = passport_details.issued_by or ""

            # Optional: Print or log the mapped object for debugging
            print(my_editable_form.model_dump_json(indent=2))

        except AttributeError as e:
            logger.error("Missing required fields in SchengenTouristVisa model: %s", e)
            raise ValueError(
                "Invalid or incomplete SchengenTouristVisa data structure."
            ) from e

        return my_editable_form
