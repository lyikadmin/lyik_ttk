from ...models.forms.new_schengentouristvisa import (
    Schengentouristvisa,
    PASSPORTTYPE,
    RELATIONSHIPWITHEU,
    Schengentouristvisa,
    CIVILMARITALSTATUS,
    PASSPORTTYPE,
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
                    detailed_message=f"Passport section data is missing. Error: {str(e)}",
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

            # sample_data = Switzerland6(
            #     first_name=passport_details.first_name,
            #     surname=passport_details.surname,
            #     passport_number=passport_details.passport_number,
            #     date_of_birth=str(passport_details.date_of_birth),
            #     date_of_issue=str(passport_details.date_of_issue),
            #     date_of_expiry=str(passport_details.date_of_expiry),
            #     place_of_birth=passport_details.place_of_birth,
            #     place_of_issue=passport_details.place_of_issue,
            #     issued_by=passport_details.issued_by,
            #     nationality=passport_details.nationality,
            #     civil_status=other_details.civil_status.value if other_details else "",
            #     gender=passport_details.gender.value,
            #     address=passport_details.address_line_1,
            #     city=passport_details.city,
            #     state=passport_details.state,
            #     country=passport_details.country,
            #     pin_code=passport_details.pin_code,
            # )

            # passport_section = schengen_visa_data.passport
            # additional_details = schengen_visa_data.additional_details

            # if not passport_section or not passport_section.passport_details:
            #     raise PluginException(
            #         message="The Passport section must be completed before proceeding. If the issue persists after completing it, please contact support for further assistance.",
            #         detailed_message=f"Passport section data is missing. Error: {str(e)}",
            #     )
            # else:
            #     my_editable_form.visa_surname_family_name = (
            #         schengen_visa_data.passport.passport_details.father_name or ""
            #     )
            #     my_editable_form.visa_surname_at_birth = (
            #         schengen_visa_data.passport.passport_details.mother_name or ""
            #     )
            #     my_editable_form.visa_first_name = (
            #         schengen_visa_data.passport.passport_details.first_name or ""
            #     )
            #     my_editable_form.visa_cob = (
            #         schengen_visa_data.passport.passport_details.country or ""
            #     )
            #     my_editable_form.visa_dob = (
            #         self.format_date(
            #             schengen_visa_data.passport.passport_details.date_of_birth
            #         )
            #         or ""
            #     )
            #     my_editable_form.visa_pob = (
            #         schengen_visa_data.passport.passport_details.place_of_birth or ""
            #     )
            #     my_editable_form.visa_issued_by_ctry = (
            #         schengen_visa_data.passport.passport_details.issued_by or ""
            #     )
            #     if (
            #         schengen_visa_data.passport.other_details.civil_status
            #         == CIVILMARITALSTATUS.SINGLE
            #     ):
            #         my_editable_form.visa_civil_sts_single = FieldToggle(
            #             value=FieldToggle.YES
            #         )

            #     my_editable_form.visa_curr_natl = (
            #         schengen_visa_data.passport.other_details.other_nationality or ""
            #     )
            #     my_editable_form.visa_natl_at_birth = (
            #         schengen_visa_data.passport.other_details.nationality_of_birth or ""
            #     )
            #     if (
            #         schengen_visa_data.passport.passport_details.type_of_passport
            #         == PASSPORTTYPE.REGULAR
            #     ):
            #         my_editable_form.visa_typ_trav_doc_ord = FieldToggle(
            #             value=FieldToggle.YES
            #         )
            # if not additional_details or additional_details.family_eu:
            #     raise PluginException(
            #         message="The Additional Details section must be completed before proceeding. If the issue persists after completing it, please contact support for further assistance.",
            #         detailed_message=f"Additional Details section data is missing. Error: {str(e)}",
            #     )
            # else:
            #     my_editable_form.visa_fam_mem_eu_surname = (
            #         schengen_visa_data.additional_details.family_eu.surname or ""
            #     )
            #     my_editable_form.visa_fam_mem_eu_dob = (
            #         self.format_date(
            #             schengen_visa_data.additional_details.family_eu.date_of_birth
            #         )
            #         or ""
            #     )
            #     my_editable_form.visa_fam_mem_eu_1st_nm = (
            #         schengen_visa_data.additional_details.family_eu.given_name or ""
            #     )
            #     my_editable_form.visa_fam_mem_eu_natl = (
            #         schengen_visa_data.additional_details.family_eu.nationality or ""
            #     )
            #     my_editable_form.visa_fam_mem_eu_num_trav_doc = (
            #         schengen_visa_data.additional_details.family_eu.travel_document_id
            #         or ""
            #     )
            #     my_editable_form.visa_fam_rs_eu_spouse = (
            #         FieldToggle(value=FieldToggle.YES)
            #         if schengen_visa_data.additional_details.family_eu.relationship
            #         == RELATIONSHIPWITHEU.SPOUSE
            #         else FieldToggle(value=FieldToggle.NO)
            #     )
            #     my_editable_form.visa_fam_rs_eu_child = (
            #         FieldToggle(value=FieldToggle.YES)
            #         if schengen_visa_data.additional_details.family_eu.relationship
            #         == RELATIONSHIPWITHEU.CHILD
            #         else FieldToggle(value=FieldToggle.NO)
            #     )
            #     my_editable_form.visa_fam_rs_eu_gc = (
            #         FieldToggle(value=FieldToggle.YES)
            #         if schengen_visa_data.additional_details.family_eu.relationship
            #         == RELATIONSHIPWITHEU.GRANDCHILD
            #         else FieldToggle(value=FieldToggle.NO)
            #     )
            #     my_editable_form.visa_fam_rs_eu_dependent = (
            #         FieldToggle(value=FieldToggle.YES)
            #         if schengen_visa_data.additional_details.family_eu.relationship
            #         == RELATIONSHIPWITHEU.DEPENDENT_ASCENDANT
            #         else FieldToggle(value=FieldToggle.NO)
            #     )
            #     my_editable_form.visa_fam_rs_eu_registered = (
            #         FieldToggle(value=FieldToggle.YES)
            #         if schengen_visa_data.additional_details.family_eu.relationship
            #         == RELATIONSHIPWITHEU.REGISTERED_PARTNER
            #         else FieldToggle(value=FieldToggle.NO)
            #     )
            #     my_editable_form.visa_fam_rs_eu_oth = (
            #         FieldToggle(value=FieldToggle.YES)
            #         if schengen_visa_data.additional_details.family_eu.relationship
            #         == RELATIONSHIPWITHEU.OTHER
            #         else FieldToggle(value=FieldToggle.NO)
            #     )

            # # Optional: Print or log the mapped object for debugging
            # print(my_editable_form.model_dump_json(indent=2))

            # return my_editable_form

        except Exception as e:
            raise PluginException(
                message="Internal error occurred. Please contact support.",
                detailed_message=f"Unhandled exception occurred during field mapping for PDF. Error: {str(e)}",
            )
