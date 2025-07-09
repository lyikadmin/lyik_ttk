from ...models.forms.new_schengentouristvisa import (
    Schengentouristvisa,
    CIVILMARITALSTATUS,
    PASSPORTTYPE,
    SPONSORTYPE1,
    SPONSORTYPE4,
    PAYMENTMETHOD1,
    PAYMENTMETHOD2,
    PAYMENTMETHOD3,
    PAYMENTMETHOD4,
    PAYMENTMETHOD5,
    PAYMENTMETHOD6,
    RELATIONSHIPWITHEU,
    OPTION,
    PURPOSEOFVISAORTRAVEL,
    GENDER,
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
            pdf_model.visa_1st_arrival_date = schengen_visa_data.visa_request_information.visa_request.arrival_date.strftime(
                "%d-%m-%Y"
            )
            pdf_model.visa_addl_stay_info = (
                schengen_visa_data.visa_request_information.visa_request.visa_type.value  # Adjusted as we need the value of the Enum
            )

            pdf_model.visa_first_name = (
                schengen_visa_data.passport.passport_details.first_name
            )
            pdf_model.visa_surname_family_name = (
                schengen_visa_data.passport.passport_details.surname
            )
            pdf_model.visa_surname_at_birth = (
                schengen_visa_data.passport.passport_details.surname
            )
            pdf_model.visa_dob = (
                schengen_visa_data.passport.passport_details.date_of_birth.strftime(
                    "%d-%m-%Y"
                )
            )
            pdf_model.visa_pob = (
                schengen_visa_data.passport.passport_details.place_of_birth
            )
            pdf_model.visa_cob = schengen_visa_data.passport.passport_details.country
            pdf_model.visa_sex_male = (
                schengen_visa_data.passport.passport_details.gender
                == GENDER.M  # Adjusted
            )
            pdf_model.visa_sex_female = (
                schengen_visa_data.passport.passport_details.gender
                == GENDER.F  # Adjusted
            )
            pdf_model.visa_sex_oth = (
                schengen_visa_data.passport.passport_details.gender != GENDER.M
                and schengen_visa_data.passport.passport_details.gender
                != GENDER.F  # Adjusted
            )

            pdf_model.visa_curr_natl = (
                schengen_visa_data.passport.passport_details.nationality
            )
            pdf_model.visa_oth_natl = (
                schengen_visa_data.passport.other_details.other_nationality
            )
            pdf_model.visa_natl_at_birth = (
                schengen_visa_data.passport.passport_details.nationality
                if not schengen_visa_data.passport.other_details.nationality_of_birth
                else schengen_visa_data.passport.other_details.nationality_of_birth
            )
            pdf_model.visa_civil_sts_single = (
                schengen_visa_data.passport.other_details.civil_status
                == CIVILMARITALSTATUS.SINGLE
            )
            pdf_model.visa_civil_sts_married = (
                schengen_visa_data.passport.other_details.civil_status
                == CIVILMARITALSTATUS.MARRIED
            )
            pdf_model.visa_civil_sts_seperated = (
                schengen_visa_data.passport.other_details.civil_status
                == CIVILMARITALSTATUS.SEPARATED
            )
            pdf_model.visa_civil_sts_divorced = (
                schengen_visa_data.passport.other_details.civil_status
                == CIVILMARITALSTATUS.DIVORCED
            )
            pdf_model.visa_civil_widow = (
                schengen_visa_data.passport.other_details.civil_status
                == CIVILMARITALSTATUS.WIDOWED
            )
            # pdf_model.visa_civil_sts_reg_partner=schengen_visa_data.passport.other_details.civil_status== CIVILMARITALSTATUS.REGISTERED_PARTNER
            pdf_model.visa_parental_auth = (
                schengen_visa_data.passport.passport_details.father_name
                + " & "
                + schengen_visa_data.passport.passport_details.mother_name
            )

            pdf_model.visa_trav_cost_self = (
                schengen_visa_data.additional_details.sponsorship.sponsorship_options_1
                == SPONSORTYPE1.SELF
            )
            pdf_model.visa_trav_cost_self_cash = (
                schengen_visa_data.additional_details.sponsorship.support_means_cash
                == PAYMENTMETHOD1.CASH
            )
            pdf_model.visa_trav_cost_self_tc = (
                schengen_visa_data.additional_details.sponsorship.support_means_travellers_cheque
                == PAYMENTMETHOD2.TRAVELLERS_CHEQUE
            )
            pdf_model.visa_trav_cost_self_cc = (
                schengen_visa_data.additional_details.sponsorship.support_means_credit_card
                == PAYMENTMETHOD3.CREDIT_CARD
            )
            pdf_model.visa_trav_cost_self_ppa = (
                schengen_visa_data.additional_details.sponsorship.support_means_prepaid_accommodation
                == PAYMENTMETHOD4.PREPAID_ACCOMMODATION
            )
            pdf_model.visa_trav_cost_self_ppt = (
                schengen_visa_data.additional_details.sponsorship.support_means_prepaid_transport
                == PAYMENTMETHOD5.PREPAID_TRANSPORT
            )
            pdf_model.visa_trav_cost_self_oth = (
                schengen_visa_data.additional_details.sponsorship.sponsorship_options_4
                == SPONSORTYPE4.OTHER
            )
            if pdf_model.visa_trav_cost_self_oth:
                pdf_model.visa_trav_cost_self_oth_txt = (
                    schengen_visa_data.additional_details.sponsorship.others_specify
                )
            pdf_model.visa_means_supportoth_oth = (
                schengen_visa_data.additional_details.sponsorship.support_means_other
                == PAYMENTMETHOD6.OTHER
            )
            if pdf_model.visa_means_supportoth_oth:
                pdf_model.visa_means_support_oth_txt = (
                    schengen_visa_data.additional_details.sponsorship.others_specify_1
                )
            # pdf_model.visa_trav_cost_31_32=
            pdf_model.visa_nat_id_num = (
                schengen_visa_data.additional_details.national_id.aadhaar_number
            )
            pdf_model.visa_typ_trav_doc_ord = (
                schengen_visa_data.passport.passport_details.type_of_passport
                == PASSPORTTYPE.ORDINARY
            )
            pdf_model.visa_typ_trav_doc_service = (
                schengen_visa_data.passport.passport_details.type_of_passport
                == PASSPORTTYPE.OFFICIAL
            )
            pdf_model.visa_typ_trav_doc_special = (
                schengen_visa_data.passport.passport_details.type_of_passport
                == PASSPORTTYPE.SPECIAL
            )
            pdf_model.visa_typ_trav_doc_diplomatic = (
                schengen_visa_data.passport.passport_details.type_of_passport
                == PASSPORTTYPE.DIPLOMATIC
            )
            pdf_model.visa_typ_trav_doc_official = (
                schengen_visa_data.passport.passport_details.type_of_passport
                == PASSPORTTYPE.OFFICIAL
            )

            pdf_model.visa_num_trav_doc = (
                schengen_visa_data.passport.passport_details.passport_number
            )
            pdf_model.visa_typ_trav_doc_oth = (
                schengen_visa_data.passport.passport_details.type_of_passport
                == PASSPORTTYPE.OTHER
            )

            pdf_model.visa_doi = (
                schengen_visa_data.passport.passport_details.date_of_issue.strftime(
                    "%d-%m-%Y"
                )
            )
            pdf_model.visa_val_til = (
                schengen_visa_data.passport.passport_details.date_of_expiry.strftime(
                    "%d-%m-%Y"
                )
            )
            pdf_model.visa_issued_by_ctry = (
                schengen_visa_data.passport.passport_details.issued_by
            )

            pdf_model.visa_fam_mem_eu_1st_nm = (
                schengen_visa_data.additional_details.family_eu.given_name
            )
            pdf_model.visa_fam_mem_eu_surname = (
                schengen_visa_data.additional_details.family_eu.surname
            )
            pdf_model.visa_fam_mem_eu_dob = (
                schengen_visa_data.additional_details.family_eu.date_of_birth.strftime(
                    "%d-%m-%Y"
                )
            )
            pdf_model.visa_fam_mem_eu_natl = (
                schengen_visa_data.additional_details.family_eu.nationality
            )
            pdf_model.visa_fam_mem_eu_num_trav_doc = (
                schengen_visa_data.additional_details.family_eu.travel_document_id
            )
            pdf_model.visa_mem_1st_entry = (
                schengen_visa_data.additional_details.travel_info.start_date_of_visa
            )
            pdf_model.visa_dptr_date = (
                schengen_visa_data.additional_details.travel_info.end_date_of_visa
            )
            pdf_model.visa_fam_rs_eu_spouse = (
                schengen_visa_data.additional_details.family_eu.relationship
                == RELATIONSHIPWITHEU.SPOUSE
            )
            pdf_model.visa_fam_rs_eu_child = (
                schengen_visa_data.additional_details.family_eu.relationship
                == RELATIONSHIPWITHEU.CHILD
            )
            pdf_model.visa_fam_rs_eu_gc = (
                schengen_visa_data.additional_details.family_eu.relationship
                == RELATIONSHIPWITHEU.GRANDCHILD
            )
            pdf_model.visa_entry_num_req_single = (
                schengen_visa_data.additional_details.travel_info.travelling_to_other_country
                == OPTION.NO
            )
            pdf_model.visa_entry_num_req_two = (
                schengen_visa_data.additional_details.travel_info.travelling_to_other_country
                == OPTION.YES
            )
            # pdf_model.visa_fam_rs_eu_dependent=schengen_visa_data.additional_details.family_eu.relationship == RELATIONSHIPWITHEU.DEPENDENT
            pdf_model.visa_fam_rs_eu_registered = (
                schengen_visa_data.additional_details.family_eu.relationship
                == RELATIONSHIPWITHEU.REGISTERED_PARTNER
            )
            pdf_model.visa_fam_rs_eu_oth = (
                schengen_visa_data.additional_details.family_eu.relationship
                == RELATIONSHIPWITHEU.OTHER
            )
            pdf_model.visa_fam_rs_eu_oth_txt = (
                schengen_visa_data.additional_details.family_eu.relationship
                if schengen_visa_data.additional_details.family_eu.relationship
                not in [
                    RELATIONSHIPWITHEU.SPOUSE,
                    RELATIONSHIPWITHEU.CHILD,
                    RELATIONSHIPWITHEU.GRANDCHILD,
                    RELATIONSHIPWITHEU.REGISTERED_PARTNER,
                    RELATIONSHIPWITHEU.OTHER,
                ]
                else ""
            )

            pdf_model.visa_app_addr = (
                schengen_visa_data.additional_details.app_details.address_line_1
                + ", "
                + schengen_visa_data.additional_details.app_details.address_line_2
                + ", "
                + schengen_visa_data.additional_details.app_details.city
                + ", "
                + schengen_visa_data.additional_details.app_details.state
                + ", "
                + schengen_visa_data.additional_details.app_details.pin_code
                + ", "
                + schengen_visa_data.additional_details.app_details.country
                + ","
                + schengen_visa_data.additional_details.app_details.email_address
            )
            pdf_model.visa_app_addr = pdf_model.visa_app_addr.strip(", ")
            pdf_model.visa_app_tel_num = (
                schengen_visa_data.additional_details.app_details.telephone_mobile_number
            )

            pdf_model.visa_fingerprint_no = (
                schengen_visa_data.previous_visas.fingerprint_details.fingerprint_collected
                == OPTION.NO
            )
            pdf_model.visa_fingerprint_yes = (
                schengen_visa_data.previous_visas.fingerprint_details.fingerprint_collected
                == OPTION.YES
            )
            if pdf_model.visa_fingerprint_yes:
                pdf_model.visa_fingerprint_yes_date = (
                    schengen_visa_data.previous_visas.fingerprint_details.date_of_previous_visa
                )
                pdf_model.visa_fingerprint_yes_sticker_num = (
                    schengen_visa_data.previous_visas.fingerprint_details.visa_sticker_number
                )

            pdf_model.visa_jrn_purpose_visit_fnf = (
                schengen_visa_data.previous_visas.previous_visas_details.purpose_of_visa
                == PURPOSEOFVISAORTRAVEL.VISIT_FAMILY_FRIENDS
            )
            pdf_model.visa_jrn_purpose_tour = (
                schengen_visa_data.previous_visas.previous_visas_details.purpose_of_visa
                == PURPOSEOFVISAORTRAVEL.TOURISM
            )
            pdf_model.visa_jrn_purpose_business = (
                schengen_visa_data.previous_visas.previous_visas_details.purpose_of_visa
                == PURPOSEOFVISAORTRAVEL.BUSINESS
            )
            pdf_model.visa_jrn_purpose_culture = (
                schengen_visa_data.previous_visas.previous_visas_details.purpose_of_visa
                == PURPOSEOFVISAORTRAVEL.CULTURAL
            )
            pdf_model.visa_jrn_purpose_official = (
                schengen_visa_data.previous_visas.previous_visas_details.purpose_of_visa
                == PURPOSEOFVISAORTRAVEL.OFFICIAL_VISIT
            )
            pdf_model.visa_jrn_purpose_study = (
                schengen_visa_data.previous_visas.previous_visas_details.purpose_of_visa
                == PURPOSEOFVISAORTRAVEL.STUDY
            )
            pdf_model.visa_jrn_purpose_med = (
                schengen_visa_data.previous_visas.previous_visas_details.purpose_of_visa
                == PURPOSEOFVISAORTRAVEL.MEDICAL
            )
            pdf_model.visa_jrn_purpose_sports = (
                schengen_visa_data.previous_visas.previous_visas_details.purpose_of_visa
                == PURPOSEOFVISAORTRAVEL.SPORTS
            )
            pdf_model.visa_jrn_purpose_transit = (
                schengen_visa_data.previous_visas.previous_visas_details.purpose_of_visa
                == PURPOSEOFVISAORTRAVEL.AIRPORT_TRANSIT
            )
            pdf_model.visa_jrn_purpose_oth = (
                schengen_visa_data.previous_visas.previous_visas_details.purpose_of_visa
                == PURPOSEOFVISAORTRAVEL.OTHER
            )
            if pdf_model.visa_jrn_purpose_oth:
                pass
                # pdf_model.visa_jrn_purpose_oth_txt=schengen_visa_data.previous_visas.previous_visas_details.

            pdf_model.visa_permit_final_ctry_dest_issued_by = (
                schengen_visa_data.previous_visas.previous_visas_details.country_of_issue
            )
            pdf_model.visa_permit_final_ctry_dest_valid_from = (
                schengen_visa_data.previous_visas.previous_visas_details.start_date
            )
            pdf_model.visa_permit_final_ctry_dest_til = (
                schengen_visa_data.previous_visas.previous_visas_details.end_date
            )

            pdf_model.visa_invite_temp_accom_tel_mun = (
                schengen_visa_data.work_address.work_details.work_phone
            )
            pdf_model.visa_invite_org_comm_details = (
                schengen_visa_data.work_address.work_details.work_address
            )
            pdf_model.visa_invite_org = (
                schengen_visa_data.work_address.work_details.employer_name
            )
            pdf_model.visa_invite_temp_accom_tel_num = (
                schengen_visa_data.accomodation.invitation_details.mobile_number
            )
            pdf_model.visa_invite_temp_accom = (
                schengen_visa_data.accomodation.invitation_details.inviter_name
            )
            pdf_model.visa_invite_temp_accom_comm_details = (
                schengen_visa_data.accomodation.invitation_details.inviter_address
                + ","
                + schengen_visa_data.accomodation.invitation_details.email_id
            )
            pdf_model.visa_curr_occ = (
                schengen_visa_data.work_address.work_details.occupation
            )
            pdf_model.visa_emp_stu_add_tel = (
                schengen_visa_data.work_address.work_details.employer_name
                + ","
                + schengen_visa_data.work_address.work_details.work_address
                + ","
                + schengen_visa_data.work_address.work_details.work_phone
            )
            # pdf_model.visa_oth_trav_doc_txt=schengen_visa_data.shared_travell_info.
            pdf_model.visa_applicant_diff_addr = (
                schengen_visa_data.residential_address.residential_address_card_v1.address_line_1
                + ","
                + schengen_visa_data.residential_address.residential_address_card_v1.address_line_2
                + ","
                + schengen_visa_data.residential_address.residential_address_card_v1.city
                + ","
                + schengen_visa_data.residential_address.residential_address_card_v1.country
            )
            pdf_model.visa_applicant_diff_tel_num = (
                schengen_visa_data.visa_request_information.visa_request.phone_number
            )

            pdf_model.visa_mem_main_dst = (
                schengen_visa_data.visa_request_information.visa_request.to_country
            )
            pdf_model.visa_applicant_diff_surnm_nm = (
                schengen_visa_data.additional_details.app_details.first_name
                + ","
                + schengen_visa_data.additional_details.app_details.surname
            )

            return pdf_model

        except PluginException as pe:
            raise

        except Exception as e:
            raise PluginException(
                message="Internal error occurred. Please contact support.",
                detailed_message=f"Unhandled exception occurred during field mapping for PDF. Error: {str(e)}",
            )
