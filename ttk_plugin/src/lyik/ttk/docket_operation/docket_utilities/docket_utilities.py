from ...models.forms.new_schengentouristvisa import (
    Schengentouristvisa,
    PASSPORTTYPE,
    RELATIONSHIPWITHEU,
    Schengentouristvisa,
    CIVILMARITALSTATUS,
    PASSPORTTYPE,
)
from datetime import date, datetime
from ...models.pdf.pdf_model import EditableForm, FieldToggle
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
            my_editable_form.visa_surname_family_name = (
                self.safe_getattr(
                    schengen_visa_data, "passport.passport_details.father_name"
                )
                or ""
            )
            my_editable_form.visa_surname_at_birth = (
                self.safe_getattr(
                    schengen_visa_data, "passport.passport_details.mother_name"
                )
                or ""
            )
            my_editable_form.visa_first_name = (
                self.safe_getattr(
                    schengen_visa_data, "passport.passport_details.first_name"
                )
                or ""
            )
            my_editable_form.visa_cob = (
                self.safe_getattr(
                    schengen_visa_data, "passport.passport_details.country"
                )
                or ""
            )
            my_editable_form.visa_dob = (
                self.format_date(
                    self.safe_getattr(
                        schengen_visa_data, "passport.passport_details.date_of_birth"
                    )
                )
                or ""
            )
            my_editable_form.visa_pob = (
                self.safe_getattr(
                    schengen_visa_data, "passport.passport_details.place_of_birth"
                )
                or ""
            )
            my_editable_form.visa_fam_mem_eu_surname = (
                self.safe_getattr(
                    schengen_visa_data, "additional_details.family_eu.surname"
                )
                or ""
            )
            my_editable_form.visa_fam_mem_eu_dob = (
                self.format_date(
                    self.safe_getattr(
                        schengen_visa_data, "additional_details.family_eu.date_of_birth"
                    )
                )
                or ""
            )
            my_editable_form.visa_fam_mem_eu_1st_nm = (
                self.safe_getattr(
                    schengen_visa_data, "additional_details.family_eu.given_name"
                )
                or ""
            )
            my_editable_form.visa_fam_mem_eu_natl = (
                self.safe_getattr(
                    schengen_visa_data, "additional_details.family_eu.nationality"
                )
                or ""
            )
            my_editable_form.visa_fam_mem_eu_num_trav_doc = (
                self.safe_getattr(
                    schengen_visa_data,
                    "additional_details.family_eu.travel_document_id",
                )
                or ""
            )
            my_editable_form.visa_fam_rs_eu_spouse = (
                FieldToggle(value=FieldToggle.YES)
                if self.safe_getattr(
                    schengen_visa_data, "additional_details.family_eu.relationship"
                )
                == RELATIONSHIPWITHEU.SPOUSE
                else FieldToggle(value=FieldToggle.NO)
            )
            my_editable_form.visa_fam_rs_eu_child = (
                FieldToggle(value=FieldToggle.YES)
                if self.safe_getattr(
                    schengen_visa_data, "additional_details.family_eu.relationship"
                )
                == RELATIONSHIPWITHEU.CHILD
                else FieldToggle(value=FieldToggle.NO)
            )
            my_editable_form.visa_fam_rs_eu_gc = (
                FieldToggle(value=FieldToggle.YES)
                if self.safe_getattr(
                    schengen_visa_data, "additional_details.family_eu.relationship"
                )
                == RELATIONSHIPWITHEU.GRANDCHILD
                else FieldToggle(value=FieldToggle.NO)
            )
            my_editable_form.visa_fam_rs_eu_dependent = (
                FieldToggle(value=FieldToggle.YES)
                if self.safe_getattr(
                    schengen_visa_data, "additional_details.family_eu.relationship"
                )
                == RELATIONSHIPWITHEU.DEPENDENT_ASCENDANT
                else FieldToggle(value=FieldToggle.NO)
            )
            my_editable_form.visa_fam_rs_eu_registered = (
                FieldToggle(value=FieldToggle.YES)
                if self.safe_getattr(
                    schengen_visa_data, "additional_details.family_eu.relationship"
                )
                == RELATIONSHIPWITHEU.REGISTERED_PARTNER
                else FieldToggle(value=FieldToggle.NO)
            )
            my_editable_form.visa_fam_rs_eu_oth = (
                FieldToggle(value=FieldToggle.YES)
                if self.safe_getattr(
                    schengen_visa_data, "additional_details.family_eu.relationship"
                )
                == RELATIONSHIPWITHEU.OTHER
                else FieldToggle(value=FieldToggle.NO)
            )
            my_editable_form.visa_issued_by_ctry = (
                self.safe_getattr(
                    schengen_visa_data, "passport.passport_details.issued_by"
                )
                or ""
            )
            if (
                self.safe_getattr(
                    schengen_visa_data, "passport.other_details.civil_status"
                )
                == CIVILMARITALSTATUS.SINGLE
            ):
                my_editable_form.visa_civil_sts_single = FieldToggle(
                    value=FieldToggle.YES
                )

            my_editable_form.visa_curr_natl = (
                self.safe_getattr(
                    schengen_visa_data, "passport.other_details.other_nationality"
                )
                or ""
            )
            my_editable_form.visa_natl_at_birth = (
                self.safe_getattr(
                    schengen_visa_data, "passport.other_details.nationality_of_birth"
                )
                or ""
            )
            if (
                self.safe_getattr(
                    schengen_visa_data, "passport.passport_details.type_of_passport"
                )
                == PASSPORTTYPE.REGULAR
            ):
                my_editable_form.visa_typ_trav_doc_ord = FieldToggle(
                    value=FieldToggle.YES
                )

            # Optional: Print or log the mapped object for debugging
            print(my_editable_form.model_dump_json(indent=2))

        except AttributeError as e:
            logger.error("Missing required fields in SchengenTouristVisa model: %s", e)
            raise ValueError(
                "Invalid or incomplete SchengenTouristVisa data structure."
            ) from e

        return my_editable_form

    def safe_getattr(self, obj, attr_path: str):
        """Safely gets nested attributes from an object using dot notation."""
        try:
            for attr in attr_path.split("."):
                obj = getattr(obj, attr)
                if obj is None:
                    return None
            return obj
        except AttributeError:
            return None
