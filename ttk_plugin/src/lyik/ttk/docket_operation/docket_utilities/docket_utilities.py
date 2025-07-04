from ...models.forms.new_schengentouristvisa import (
    Schengentouristvisa,
)
from lyikpluginmanager import PluginException
from datetime import date, datetime
from ...models.pdf.pdf_model import PDFModel
import logging

logger = logging.getLogger(__name__)


class DocketUtilities:

    def format_date(
        self,
        raw_date: date | datetime | None | str,
    ) -> str:
        """
        This function formats the date  and datetime object and returns as date str.
        """
        if isinstance(raw_date, str):
            return raw_date
        formatted_date = ""
        if isinstance(raw_date, date):
            formatted_date = raw_date.strftime("%d/%m/%Y")
        if isinstance(raw_date, datetime):
            formatted_date = raw_date.strftime("%d/%m/%Y %H:%M:%S")

        return formatted_date

    def map_schengen_to_pdf_model(
        self,
        schengen_visa_data: Schengentouristvisa,
    ) -> PDFModel:
        """
        Maps relevant fields from a SchengenTouristVisa model instance to an EditableForm instance.

        Args:
            schengen_visa_data (SchengenTouristVisa): The input model containing the source data.

        Returns:
            EditableForm: A new instance populated with values from the SchengenTouristVisa model.
        """
        pdf_model = PDFModel()

        try:
            passport_section = schengen_visa_data.passport
            if (
                not passport_section
                or not passport_section.passport_details
                or not passport_section.other_details
            ):
                raise PluginException(
                    message="The Passport section must be completed before proceeding. If the issue persists after completing it, please contact support for further assistance.",
                    detailed_message=f"Passport section data is missing.",
                )

            passport_details = passport_section.passport_details
            other_details = passport_section.other_details

            pdf_model.visa_surname_family_name = passport_details.surname
            pdf_model.visa_surname_at_birth = passport_details.surname
            pdf_model.visa_first_name = passport_details.first_name
            pdf_model.visa_dob = (
                self.format_date(
                    schengen_visa_data.passport.passport_details.date_of_birth
                )
                or ""
            )
            pdf_model.visa_cob = passport_details.country
            pdf_model.visa_sex_male = (
                True if passport_details.gender.value == "M" else False
            )
            pdf_model.visa_sex_female = (
                True if passport_details.gender.value == "F" else False
            )
            pdf_model.visa_sex_oth = (
                True
                if passport_details.gender.value == "O"
                or passport_details.gender.value == "T"
                else False
            )
            pdf_model.visa_pob = passport_details.place_of_birth

            pdf_model.visa_curr_natl = passport_details.nationality
            pdf_model.visa_oth_natl = other_details.other_nationality

            return pdf_model

        except PluginException as pe:
            raise

        except Exception as e:
            raise PluginException(
                message="Internal error occurred. Please contact support.",
                detailed_message=f"Unhandled exception occurred during field mapping for PDF. Error: {str(e)}",
            )
