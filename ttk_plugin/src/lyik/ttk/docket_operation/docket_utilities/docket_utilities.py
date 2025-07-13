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
            visa_info = schengen_visa_data.visa_request_information
            if visa_info and visa_info.visa_request:
                pdf_model.visa_1st_arrival_date = (
                    visa_info.visa_request.arrival_date.strftime("%d-%m-%Y")
                )
                pdf_model.visa_addl_stay_info = (
                    visa_info.visa_request.visa_type.value  # Adjusted as we need the value of the Enum
                )
                pdf_model.visa_applicant_diff_tel_num = (
                    visa_info.visa_request.phone_number
                )

                pdf_model.visa_mem_main_dst = (
                    visa_info.visa_request.to_country
                )

            passport = schengen_visa_data.passport
            if passport and passport.passport_details:
                pdf_model.visa_first_name = (
                    passport.passport_details.first_name
                )
                pdf_model.visa_surname_family_name = (
                    passport.passport_details.surname
                )
                pdf_model.visa_surname_at_birth = (
                    passport.passport_details.surname
                )
                pdf_model.visa_dob = (
                    passport.passport_details.date_of_birth.strftime(
                        "%d-%m-%Y"
                    )
                )
                pdf_model.visa_pob = (
                    passport.passport_details.place_of_birth
                )
                pdf_model.visa_cob = (
                    passport.passport_details.country
                )
                pdf_model.visa_sex_male = (
                    passport.passport_details.gender
                    == GENDER.M  # Adjusted
                )
                pdf_model.visa_sex_female = (
                    passport.passport_details.gender
                    == GENDER.F  # Adjusted
                )
                pdf_model.visa_sex_oth = (
                    passport.passport_details.gender != GENDER.M
                    and passport.passport_details.gender
                    != GENDER.F  # Adjusted
                )

                pdf_model.visa_curr_natl = (
                    passport.passport_details.nationality
                )
                pdf_model.visa_typ_trav_doc_ord = (
                    passport.passport_details.type_of_passport
                    == PASSPORTTYPE.ORDINARY
                )
                pdf_model.visa_typ_trav_doc_service = (
                    passport.passport_details.type_of_passport
                    == PASSPORTTYPE.OFFICIAL
                )
                pdf_model.visa_typ_trav_doc_special = (
                    passport.passport_details.type_of_passport
                    == PASSPORTTYPE.SPECIAL
                )
                pdf_model.visa_typ_trav_doc_diplomatic = (
                    passport.passport_details.type_of_passport
                    == PASSPORTTYPE.DIPLOMATIC
                )
                pdf_model.visa_typ_trav_doc_official = (
                    passport.passport_details.type_of_passport
                    == PASSPORTTYPE.OFFICIAL
                )

                pdf_model.visa_num_trav_doc = (
                    passport.passport_details.passport_number
                )
                pdf_model.visa_typ_trav_doc_oth = (
                    passport.passport_details.type_of_passport
                    == PASSPORTTYPE.OTHER
                )

                pdf_model.visa_doi = (
                    passport.passport_details.date_of_issue.strftime(
                        "%d-%m-%Y"
                    )
                )
                pdf_model.visa_val_til = passport.passport_details.date_of_expiry.strftime(
                    "%d-%m-%Y"
                )
                pdf_model.visa_issued_by_ctry = (
                    passport.passport_details.issued_by
                )

            if passport and passport.other_details:
                pdf_model.visa_oth_natl = (
                    passport.other_details.other_nationality
                )
                pdf_model.visa_civil_sts_single = (
                    passport.other_details.civil_status
                    == CIVILMARITALSTATUS.SINGLE
                )
                pdf_model.visa_civil_sts_married = (
                    passport.other_details.civil_status
                    == CIVILMARITALSTATUS.MARRIED
                )
                pdf_model.visa_civil_sts_seperated = (
                    passport.other_details.civil_status
                    == CIVILMARITALSTATUS.SEPARATED
                )
                pdf_model.visa_civil_sts_divorced = (
                    passport.other_details.civil_status
                    == CIVILMARITALSTATUS.DIVORCED
                )
                pdf_model.visa_civil_widow = (
                    passport.other_details.civil_status
                    == CIVILMARITALSTATUS.WIDOWED
                )
                pdf_model.visa_civil_sts_single = (
                    passport.other_details.civil_status
                    == CIVILMARITALSTATUS.SINGLE
                )
                pdf_model.visa_civil_sts_married = (
                    passport.other_details.civil_status
                    == CIVILMARITALSTATUS.MARRIED
                )
                pdf_model.visa_civil_sts_seperated = (
                    passport.other_details.civil_status
                    == CIVILMARITALSTATUS.SEPARATED
                )
                pdf_model.visa_civil_sts_divorced = (
                    passport.other_details.civil_status
                    == CIVILMARITALSTATUS.DIVORCED
                )
                pdf_model.visa_civil_widow = (
                    passport.other_details.civil_status
                    == CIVILMARITALSTATUS.WIDOWED
                )

            if (
                passport
                and passport.other_details
                and passport.other_details.nationality_of_birth
            ):
                pdf_model.visa_natl_at_birth = (
                    passport.other_details.nationality_of_birth
                )
            elif (
                passport
                and passport.passport_details
                and passport.passport_details.nationality
            ):
                pdf_model.visa_natl_at_birth = (
                    passport.passport_details.nationality
                )

            # pdf_model.visa_civil_sts_reg_partner=schengen_visa_data.passport.other_details.civil_status== CIVILMARITALSTATUS.REGISTERED_PARTNER
            # pdf_model.visa_parental_auth = (
            #     schengen_visa_data.passport.passport_details.father_name
            #     + " & "
            #     + schengen_visa_data.passport.passport_details.mother_name
            # )
            additional_details = schengen_visa_data.additional_details
            if additional_details and additional_details.sponsorship:
                pdf_model.visa_trav_cost_self = (
                    additional_details.sponsorship.sponsorship_options_1
                    == SPONSORTYPE1.SELF
                )
                pdf_model.visa_trav_cost_self_cash = (
                    additional_details.sponsorship.support_means_cash
                    == PAYMENTMETHOD1.CASH
                )
                pdf_model.visa_trav_cost_self_tc = (
                    additional_details.sponsorship.support_means_travellers_cheque
                    == PAYMENTMETHOD2.TRAVELLERS_CHEQUE
                )
                pdf_model.visa_trav_cost_self_cc = (
                    additional_details.sponsorship.support_means_credit_card
                    == PAYMENTMETHOD3.CREDIT_CARD
                )
                pdf_model.visa_trav_cost_self_ppa = (
                    additional_details.sponsorship.support_means_prepaid_accommodation
                    == PAYMENTMETHOD4.PREPAID_ACCOMMODATION
                )
                pdf_model.visa_trav_cost_self_ppt = (
                    additional_details.sponsorship.support_means_prepaid_transport
                    == PAYMENTMETHOD5.PREPAID_TRANSPORT
                )
                pdf_model.visa_trav_cost_self_oth = (
                    additional_details.sponsorship.sponsorship_options_4
                    == SPONSORTYPE4.OTHER
                )
                if pdf_model.visa_trav_cost_self_oth:
                    pdf_model.visa_trav_cost_self_oth_txt = (
                        additional_details.sponsorship.others_specify
                    )
                pdf_model.visa_means_supportoth_oth = (
                    additional_details.sponsorship.support_means_other
                    == PAYMENTMETHOD6.OTHER
                )
                if pdf_model.visa_means_supportoth_oth:
                    pdf_model.visa_means_support_oth_txt = (
                        additional_details.sponsorship.others_specify_1
                    )

            if additional_details and additional_details.national_id:
                # pdf_model.visa_trav_cost_31_32=
                pdf_model.visa_nat_id_num = (
                    additional_details.national_id.aadhaar_number
                )

            if additional_details and additional_details.family_eu:
                pdf_model.visa_fam_mem_eu_1st_nm = (
                    additional_details.family_eu.given_name
                )
                pdf_model.visa_fam_mem_eu_surname = (
                    additional_details.family_eu.surname
                )
                pdf_model.visa_fam_mem_eu_dob = additional_details.family_eu.date_of_birth.strftime(
                    "%d-%m-%Y"
                )
                pdf_model.visa_fam_mem_eu_natl = (
                    additional_details.family_eu.nationality
                )
                pdf_model.visa_fam_mem_eu_num_trav_doc = (
                    additional_details.family_eu.travel_document_id
                )
                pdf_model.visa_fam_rs_eu_spouse = (
                    additional_details.family_eu.relationship
                    == RELATIONSHIPWITHEU.SPOUSE
                )
                pdf_model.visa_fam_rs_eu_child = (
                    additional_details.family_eu.relationship
                    == RELATIONSHIPWITHEU.CHILD
                )
                pdf_model.visa_fam_rs_eu_gc = (
                    additional_details.family_eu.relationship
                    == RELATIONSHIPWITHEU.GRANDCHILD
                )
                pdf_model.visa_fam_rs_eu_registered = (
                    additional_details.family_eu.relationship
                    == RELATIONSHIPWITHEU.REGISTERED_PARTNER
                )
                pdf_model.visa_fam_rs_eu_oth = (
                    additional_details.family_eu.relationship
                    == RELATIONSHIPWITHEU.OTHER
                )
                pdf_model.visa_fam_rs_eu_oth_txt = (
                    additional_details.family_eu.relationship
                    if additional_details.family_eu.relationship
                    not in [
                        RELATIONSHIPWITHEU.SPOUSE,
                        RELATIONSHIPWITHEU.CHILD,
                        RELATIONSHIPWITHEU.GRANDCHILD,
                        RELATIONSHIPWITHEU.REGISTERED_PARTNER,
                        RELATIONSHIPWITHEU.OTHER,
                    ]
                    else ""
                )

            if additional_details and additional_details.travel_info:
                pdf_model.visa_mem_1st_entry = (
                    additional_details.travel_info.start_date_of_visa
                )
                pdf_model.visa_dptr_date = (
                    additional_details.travel_info.end_date_of_visa
                )

                pdf_model.visa_entry_num_req_single = (
                    additional_details.travel_info.travelling_to_other_country
                    == OPTION.NO
                )
                pdf_model.visa_entry_num_req_two = (
                    additional_details.travel_info.travelling_to_other_country
                    == OPTION.YES
                )
            # pdf_model.visa_fam_rs_eu_dependent=schengen_visa_data.additional_details.family_eu.relationship == RELATIONSHIPWITHEU.DEPENDENT
            if additional_details and additional_details.app_details:
                app_details = additional_details.app_details

                line1 = app_details.address_line_1 or ""
                line2 = app_details.address_line_2 or ""
                city = app_details.city or ""
                state = app_details.state or ""
                pin = app_details.pin_code or ""
                country = app_details.country or ""
                email = app_details.email_address or ""

                pdf_model.visa_app_addr = ", ".join(
                    part for part in [line1, line2, city, state, pin, country, email] if part.strip()
                )

                pdf_model.visa_app_addr = pdf_model.visa_app_addr.strip(", ")
                pdf_model.visa_app_tel_num = (
                    additional_details.app_details.telephone_mobile_number
                )
                app_details = additional_details.app_details

                first_name = app_details.first_name or ""
                surname = app_details.surname or ""

                pdf_model.visa_applicant_diff_surnm_nm = ", ".join(
                    part for part in [first_name, surname] if part.strip()
                )

            previous_visas = schengen_visa_data.previous_visas
            if previous_visas and previous_visas.fingerprint_details:
                pdf_model.visa_fingerprint_no = (
                    previous_visas.fingerprint_details.fingerprint_collected
                    == OPTION.NO
                )
                pdf_model.visa_fingerprint_yes = (
                    previous_visas.fingerprint_details.fingerprint_collected
                    == OPTION.YES
                )
                if pdf_model.visa_fingerprint_yes:
                    pdf_model.visa_fingerprint_yes_date = (
                        previous_visas.fingerprint_details.date_of_previous_visa
                    )
                    pdf_model.visa_fingerprint_yes_sticker_num = (
                        previous_visas.fingerprint_details.visa_sticker_number
                    )

            if previous_visas and previous_visas.previous_visas_details:
                pdf_model.visa_jrn_purpose_visit_fnf = (
                    previous_visas.previous_visas_details.purpose_of_visa
                    == PURPOSEOFVISAORTRAVEL.VISIT_FAMILY_FRIENDS
                )
                pdf_model.visa_jrn_purpose_tour = (
                    previous_visas.previous_visas_details.purpose_of_visa
                    == PURPOSEOFVISAORTRAVEL.TOURISM
                )
                pdf_model.visa_jrn_purpose_business = (
                    previous_visas.previous_visas_details.purpose_of_visa
                    == PURPOSEOFVISAORTRAVEL.BUSINESS
                )
                pdf_model.visa_jrn_purpose_culture = (
                    previous_visas.previous_visas_details.purpose_of_visa
                    == PURPOSEOFVISAORTRAVEL.CULTURAL
                )
                pdf_model.visa_jrn_purpose_official = (
                    previous_visas.previous_visas_details.purpose_of_visa
                    == PURPOSEOFVISAORTRAVEL.OFFICIAL_VISIT
                )
                pdf_model.visa_jrn_purpose_study = (
                    previous_visas.previous_visas_details.purpose_of_visa
                    == PURPOSEOFVISAORTRAVEL.STUDY
                )
                pdf_model.visa_jrn_purpose_med = (
                    previous_visas.previous_visas_details.purpose_of_visa
                    == PURPOSEOFVISAORTRAVEL.MEDICAL
                )
                pdf_model.visa_jrn_purpose_sports = (
                    previous_visas.previous_visas_details.purpose_of_visa
                    == PURPOSEOFVISAORTRAVEL.SPORTS
                )
                pdf_model.visa_jrn_purpose_transit = (
                    previous_visas.previous_visas_details.purpose_of_visa
                    == PURPOSEOFVISAORTRAVEL.AIRPORT_TRANSIT
                )
                pdf_model.visa_jrn_purpose_oth = (
                    previous_visas.previous_visas_details.purpose_of_visa
                    == PURPOSEOFVISAORTRAVEL.OTHER
                )
                if pdf_model.visa_jrn_purpose_oth:
                    pass
                # pdf_model.visa_jrn_purpose_oth_txt=schengen_visa_data.previous_visas.previous_visas_details.

                pdf_model.visa_permit_final_ctry_dest_issued_by = (
                    previous_visas.previous_visas_details.country_of_issue
                )
                pdf_model.visa_permit_final_ctry_dest_valid_from = (
                    previous_visas.previous_visas_details.start_date
                )
                pdf_model.visa_permit_final_ctry_dest_til = (
                    previous_visas.previous_visas_details.end_date
                )

            work_address = schengen_visa_data.work_address
            if work_address and work_address.work_details:
                pdf_model.visa_invite_temp_accom_tel_mun = (
                    work_address.work_details.work_phone
                )
                pdf_model.visa_invite_org_comm_details = (
                    work_address.work_details.work_address
                )
                pdf_model.visa_invite_org = (
                    work_address.work_details.employer_name
                )
                pdf_model.visa_curr_occ = (
                    work_address.work_details.occupation
                )
                work_details = work_address.work_details

                employer = work_details.employer_name or ""
                address = work_details.work_address or ""
                phone = work_details.work_phone or ""

                pdf_model.visa_emp_stu_add_tel = ", ".join(
                    part for part in [employer, address, phone] if part.strip()
                )

            accomodation = schengen_visa_data.accomodation
            if accomodation and accomodation.invitation_details:
                pdf_model.visa_invite_temp_accom_tel_num = (
                    accomodation.invitation_details.mobile_number
                )
                pdf_model.visa_invite_temp_accom = (
                    accomodation.invitation_details.inviter_name
                )
                address = accomodation.invitation_details.inviter_address or ""
                email = accomodation.invitation_details.email_id or ""

                # Join only non-empty parts with comma
                pdf_model.visa_invite_temp_accom_comm_details = ", ".join(
                    part for part in [address, email] if part.strip()
                )

            resi_address = schengen_visa_data.residential_address
            if resi_address and resi_address.residential_address_card_v1:
                # pdf_model.visa_oth_trav_doc_txt=schengen_visa_data.shared_travell_info.
                res_address = resi_address.residential_address_card_v1

                # Extract each field safely
                line1 = res_address.address_line_1 or ""
                line2 = res_address.address_line_2 or ""
                city = res_address.city or ""
                country = res_address.country or ""

                # Join non-empty, stripped values with commas
                pdf_model.visa_applicant_diff_addr = ", ".join(
                    part for part in [line1, line2, city, country] if part.strip()
                )


            return pdf_model

        except PluginException as pe:
            raise

        except Exception as e:
            raise PluginException(
                message="Internal error occurred. Please contact support.",
                detailed_message=f"Unhandled exception occurred during field mapping for PDF. Error: {str(e)}",
            )
