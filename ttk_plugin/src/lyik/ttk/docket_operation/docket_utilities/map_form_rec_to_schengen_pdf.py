from lyik.ttk.models.forms.schengentouristvisa import (
    Schengentouristvisa,
    VISATYPE,
    CIVILMARITALSTATUS,
    PASSPORTTYPE,
    SPONSORTYPE1,
    SPONSORTYPE2,
    SPONSORTYPE3,
    SPONSORTYPE4,
    PAYMENTMETHOD1,
    PAYMENTMETHOD2,
    PAYMENTMETHOD3,
    PAYMENTMETHOD4,
    PAYMENTMETHOD5,
    PAYMENTMETHOD6,
    RELATIONSHIPWITHEU,
    OPTION,
    GENDER,
    SAMEASPASSADDR,
    CURRENTOCCUPATIONSTATUS,
    NUMBEROFENTRIES,
    EXPENSECOVERAGE1,
    EXPENSECOVERAGE2,
    EXPENSECOVERAGE3,
    EXPENSECOVERAGE4,
    EXPENSECOVERAGE5,
    ACCOMMODATIONARRANGEMENT,
)
from lyikpluginmanager import PluginException
from datetime import date, datetime
from lyik.ttk.models.pdf.schengen_pdf_model import SchengenPDFModel

# from .utils import ISO3ToCountryModel
from lyik.ttk.utils.utils import ISO3ToCountryModel
from lyik.ttk.utils.message import get_error_message
import logging

logger = logging.getLogger(__name__)


class DocketUtilities:

    def map_schengen_to_pdf_model(
        self,
        schengen_visa_data: Schengentouristvisa,
    ) -> SchengenPDFModel:
        """
        Maps relevant fields from a SchengenTouristVisa model instance to an EditableForm instance.

        Args:
            schengen_visa_data (SchengenTouristVisa): The input model containing the source data.

        Returns:
            EditableForm: A new instance populated with values from the SchengenTouristVisa model.
        """
        pdf_model = SchengenPDFModel()

        try:
            visa_info = schengen_visa_data.visa_request_information
            if visa_info and visa_info.visa_request:
                pdf_model.visa_app_tel_num = visa_info.visa_request.phone_number  #
                pdf_model.visa_entry_num_req_single = (
                    visa_info.visa_request.no_of_entries == NUMBEROFENTRIES.Single  #
                )
                pdf_model.visa_entry_num_req_two = (
                    visa_info.visa_request.no_of_entries == NUMBEROFENTRIES.Two  #
                )
                pdf_model.visa_entry_num_req_multi = (
                    visa_info.visa_request.no_of_entries == NUMBEROFENTRIES.Multiple  #
                )
                if visa_info.visa_request.departure_date:
                    pdf_model.visa_1st_arrival_date = (
                        visa_info.visa_request.departure_date.strftime("%d-%m-%Y")  #
                    )
                if visa_info.visa_request.arrival_date:
                    pdf_model.visa_dptr_date = (
                        visa_info.visa_request.arrival_date.strftime("%d-%m-%Y")  #
                    )

                pdf_model.visa_addl_stay_info = (
                    visa_info.visa_request.purpose_of_stay  #
                )
                pdf_model.visa_jrn_purpose_visit_fnf = (
                    visa_info.visa_request.visa_type == VISATYPE.Visitor
                )  #
                pdf_model.visa_jrn_purpose_tour = (
                    visa_info.visa_request.visa_type == VISATYPE.Tourist
                )  #
                pdf_model.visa_jrn_purpose_business = (
                    visa_info.visa_request.visa_type == VISATYPE.Business
                )  #
                pdf_model.visa_jrn_purpose_official = (
                    visa_info.visa_request.visa_type == VISATYPE.Work
                )  #
                pdf_model.visa_jrn_purpose_study = (
                    visa_info.visa_request.visa_type == VISATYPE.Student
                )  #
                pdf_model.visa_jrn_purpose_sports = (
                    visa_info.visa_request.visa_type == VISATYPE.Sports
                )  #

            passport = schengen_visa_data.passport
            if passport and passport.passport_details:
                pdf_model.visa_surname_family_name = (
                    passport.passport_details.surname
                )  #
                pdf_model.visa_surname_at_birth = (
                    passport.passport_details.surname_at_birth
                )  #
                pdf_model.visa_first_name = passport.passport_details.first_name  #
                if passport.passport_details.date_of_birth:
                    pdf_model.visa_dob = (
                        passport.passport_details.date_of_birth.strftime("%d-%m-%Y")  #
                    )
                pdf_model.visa_pob = passport.passport_details.place_of_birth  #
                pdf_model.visa_cob = (
                    ISO3ToCountryModel(
                        iso3_input=passport.passport_details.country_of_birth
                    ).country_name()
                    if passport.passport_details.country_of_birth
                    else ""
                )  #
                pdf_model.visa_curr_natl = passport.passport_details.nationality  #
                pdf_model.visa_sex_male = (
                    passport.passport_details.gender == GENDER.M
                )  #
                pdf_model.visa_sex_female = (
                    passport.passport_details.gender == GENDER.F
                )  #
                pdf_model.visa_sex_oth = (
                    passport.passport_details.gender != GENDER.M
                    and passport.passport_details.gender != GENDER.F  #
                )

                pdf_model.visa_typ_trav_doc_ord = (
                    passport.passport_details.type_of_passport
                    == PASSPORTTYPE.ORDINARY  #
                )
                pdf_model.visa_typ_trav_doc_service = (
                    passport.passport_details.type_of_passport
                    == PASSPORTTYPE.SERVICE  #
                )
                pdf_model.visa_typ_trav_doc_special = (
                    passport.passport_details.type_of_passport
                    == PASSPORTTYPE.SPECIAL  #
                )
                pdf_model.visa_typ_trav_doc_diplomatic = (
                    passport.passport_details.type_of_passport
                    == PASSPORTTYPE.DIPLOMATIC  #
                )
                pdf_model.visa_typ_trav_doc_official = (
                    passport.passport_details.type_of_passport
                    == PASSPORTTYPE.OFFICIAL  #
                )
                pdf_model.visa_typ_trav_doc_oth = (
                    passport.passport_details.type_of_passport == PASSPORTTYPE.OTHER  #
                )

                pdf_model.visa_num_trav_doc = (
                    passport.passport_details.passport_number
                )  #

                if passport.passport_details.date_of_issue:
                    pdf_model.visa_doi = (
                        passport.passport_details.date_of_issue.strftime("%d-%m-%Y")  #
                    )
                if passport.passport_details.date_of_expiry:
                    pdf_model.visa_val_til = (
                        passport.passport_details.date_of_expiry.strftime("%d-%m-%Y")  #
                    )
                pdf_model.visa_issued_by_ctry = passport.passport_details.country  #

            if passport and passport.other_details:
                pdf_model.visa_oth_natl = passport.other_details.other_nationality  #
                pdf_model.visa_civil_sts_single = (
                    passport.other_details.civil_status == CIVILMARITALSTATUS.SINGLE  #
                )
                pdf_model.visa_civil_sts_married = (
                    passport.other_details.civil_status == CIVILMARITALSTATUS.MARRIED  #
                )
                pdf_model.visa_civil_sts_seperated = (
                    passport.other_details.civil_status
                    == CIVILMARITALSTATUS.SEPARATED  #
                )
                pdf_model.visa_civil_sts_divorced = (
                    passport.other_details.civil_status
                    == CIVILMARITALSTATUS.DIVORCED  #
                )
                pdf_model.visa_civil_sts_widow = (
                    passport.other_details.civil_status == CIVILMARITALSTATUS.WIDOWED  #
                )

                pdf_model.visa_civil_sts_oth = (
                    schengen_visa_data.passport.other_details.civil_status
                    == CIVILMARITALSTATUS.OTHER  #
                )

                # Set 'other' civil status text if applicable
                if pdf_model.visa_civil_sts_oth:
                    add_other_detail(pdf_model, schengen_visa_data)

                pdf_model.visa_natl_at_birth = (
                    passport.other_details.nationality_of_birth  #
                )

                if passport.other_details.minor_status == OPTION.YES:
                    parent_details = passport.parental_guardian_details

                    if parent_details:
                        parent_surname = parent_details.surname or ""
                        parent_first_name = parent_details.first_name or ""
                        parent_addr = parent_details.address or ""
                        parent_phone = parent_details.phone_number or ""
                        parent_email = parent_details.email_address or ""
                        parent_nationality = parent_details.nationality or ""

                        pdf_model.visa_parental_auth = ", ".join(
                            part
                            for part in [
                                parent_surname,
                                parent_first_name,
                                parent_addr,
                                parent_phone,
                                parent_email,
                                parent_nationality,
                            ]
                            if part.strip()  #
                        )

            additional_details = schengen_visa_data.additional_details
            if additional_details:
                pdf_model.visa_trav_cost_self = (
                    additional_details.sponsorship_options_1 == SPONSORTYPE1.SELF  #
                )
                if pdf_model.visa_trav_cost_self:
                    pdf_model.visa_trav_cost_self_cash = (
                        additional_details.means_of_support_myself.support_means_cash
                        == PAYMENTMETHOD1.CASH
                    )
                    pdf_model.visa_trav_cost_self_tc = (
                        additional_details.means_of_support_myself.support_means_travellers_cheque
                        == PAYMENTMETHOD2.TRAVELLERS_CHEQUE
                    )
                    pdf_model.visa_trav_cost_self_cc = (
                        additional_details.means_of_support_myself.support_means_credit_card
                        == PAYMENTMETHOD3.CREDIT_CARD
                    )
                    pdf_model.visa_trav_cost_self_ppa = (
                        additional_details.means_of_support_myself.support_means_prepaid_accommodation
                        == PAYMENTMETHOD4.PREPAID_ACCOMMODATION
                    )
                    pdf_model.visa_trav_cost_self_ppt = (
                        additional_details.means_of_support_myself.support_means_prepaid_transport
                        == PAYMENTMETHOD5.PREPAID_TRANSPORT
                    )
                    pdf_model.visa_trav_cost_self_oth = (
                        additional_details.means_of_support_myself.support_means_other
                        == PAYMENTMETHOD6.OTHER
                    )
                    if pdf_model.visa_trav_cost_self_oth:
                        pdf_model.visa_trav_cost_self_oth_txt = (
                            additional_details.means_of_support_myself.others_specify_1
                        )

                pdf_model.visa_trav_cost_spons = (
                    additional_details.sponsorship_options_2 == SPONSORTYPE2.SPONSOR  #
                )
                pdf_model.visa_trav_cost_31_32 = (
                    additional_details.sponsorship_options_3 == SPONSORTYPE3.INVITER  #
                )
                pdf_model.visa_trav_cost_oth = (
                    additional_details.sponsorship_options_4 == SPONSORTYPE4.OTHER  #
                )
                if pdf_model.visa_trav_cost_oth:
                    pdf_model.visa_trav_cost_oth_txt = (
                        additional_details.others_specify  #
                    )
                if (
                    pdf_model.visa_trav_cost_spons
                    | pdf_model.visa_trav_cost_31_32
                    | pdf_model.visa_trav_cost_oth
                ):  #
                    pdf_model.visa_means_support_oth_cash = (
                        additional_details.means_of_support_sponser.coverage_expense_cash
                        == EXPENSECOVERAGE1.CASH
                    )
                    pdf_model.visa_means_support_oth_ap = (
                        additional_details.means_of_support_sponser.coverage_accommodation_provided
                        == EXPENSECOVERAGE2.ACCOMMODATION_PROVIDED
                    )
                    pdf_model.visa_means_support_oth_expn_covered = (
                        additional_details.means_of_support_sponser.coverage_all_covered
                        == EXPENSECOVERAGE3.ALL_COVERED
                    )
                    pdf_model.visa_means_support_oth_ppt = (
                        additional_details.means_of_support_sponser.coverage_prepaid_transport
                        == EXPENSECOVERAGE4.PREPAID_TRANSPORT
                    )
                    pdf_model.visa_means_support_oth = (
                        additional_details.means_of_support_sponser.coverage_other
                        == EXPENSECOVERAGE5.OTHER
                    )
                    if pdf_model.visa_means_support_oth:
                        pdf_model.visa_means_support_oth_txt = (
                            additional_details.means_of_support_sponser.others_specify_2
                        )

            if additional_details and additional_details.national_id:
                pdf_model.visa_nat_id_num = (
                    additional_details.national_id.aadhaar_number  #
                )

            if additional_details and additional_details.family_eu:
                pdf_model.visa_fam_mem_eu_surname = (
                    additional_details.family_eu.surname
                )  #
                pdf_model.visa_fam_mem_eu_1st_nm = (
                    additional_details.family_eu.given_name  #
                )
                if additional_details.family_eu.date_of_birth:
                    pdf_model.visa_fam_mem_eu_dob = (
                        additional_details.family_eu.date_of_birth.strftime(
                            "%d-%m-%Y"
                        )  #
                    )
                pdf_model.visa_fam_mem_eu_natl = (
                    additional_details.family_eu.nationality  #
                )
                pdf_model.visa_fam_mem_eu_num_trav_doc = (
                    additional_details.family_eu.travel_document_id  #
                )
                pdf_model.visa_fam_rs_eu_spouse = (
                    additional_details.family_eu.relationship
                    == RELATIONSHIPWITHEU.SPOUSE  #
                )
                pdf_model.visa_fam_rs_eu_child = (
                    additional_details.family_eu.relationship
                    == RELATIONSHIPWITHEU.CHILD  #
                )
                pdf_model.visa_fam_rs_eu_gc = (
                    additional_details.family_eu.relationship
                    == RELATIONSHIPWITHEU.GRANDCHILD  #
                )
                pdf_model.visa_fam_rs_eu_dependent = (
                    additional_details.family_eu.relationship
                    == RELATIONSHIPWITHEU.DEPENDENT_ASCENDANT  #
                )
                pdf_model.visa_fam_rs_eu_registered = (
                    additional_details.family_eu.relationship
                    == RELATIONSHIPWITHEU.REGISTERED_PARTNER  #
                )
                pdf_model.visa_fam_rs_eu_oth = (
                    additional_details.family_eu.relationship
                    == RELATIONSHIPWITHEU.OTHER  #
                )

            if additional_details and additional_details.travel_other == OPTION.YES:

                other_schengen_countries = additional_details.other_schengen_countries

                if other_schengen_countries:

                    def get_country_name(code: str | None) -> str:
                        return (
                            ISO3ToCountryModel(iso3_input=code).country_name()
                            if code
                            else ""
                        )

                    pdf_model.visa_mem_1st_entry = get_country_name(
                        other_schengen_countries.schengen_country_arrival  #
                    )

                    to_country_full_name = visa_info.visa_request.to_country_full_name
                    arrival_country = get_country_name(
                        other_schengen_countries.schengen_country_arrival
                    )
                    departure_country = get_country_name(
                        other_schengen_countries.schengen_country_departure
                    )
                    any_other_schengen_country = get_country_name(
                        other_schengen_countries.any_other_schengen_country
                    )

                    countries_list = [
                        arrival_country,
                        to_country_full_name,
                        any_other_schengen_country,
                        departure_country,
                    ]

                    # Remove None/empty and duplicates while preserving order
                    unique_countries = []
                    for country in filter(None, countries_list):
                        if country not in unique_countries:
                            unique_countries.append(country)

                    pdf_model.visa_mem_main_dst = ", ".join(unique_countries)

            else:
                pdf_model.visa_mem_main_dst = (
                    visa_info.visa_request.to_country_full_name  #
                )
                pdf_model.visa_mem_1st_entry = (
                    visa_info.visa_request.to_country_full_name
                )  #

            if (
                additional_details
                and additional_details.travelling_to_other_country == OPTION.YES
            ):
                travel_info = additional_details.travel_info

                if travel_info:
                    pdf_model.visa_permit_final_ctry_dest_issued_by = (  #
                        ISO3ToCountryModel(
                            iso3_input=travel_info.country_of_travel
                        ).country_name()
                        if travel_info.country_of_travel
                        else ""
                    )
                    if travel_info.valid_visa_for_country == OPTION.YES:
                        if travel_info.start_date_of_visa:
                            pdf_model.visa_permit_final_ctry_dest_valid_from = (
                                travel_info.start_date_of_visa.strftime("%d-%m-%Y")  #
                            )

                        if travel_info.end_date_of_visa:
                            pdf_model.visa_permit_final_ctry_dest_til = (
                                travel_info.end_date_of_visa.strftime("%d-%m-%Y")  #
                            )

            resi_address = schengen_visa_data.residential_address
            if resi_address:
                if (
                    resi_address.same_as_passport_address
                    == SAMEASPASSADDR.SAME_AS_PASS_ADDR
                ):
                    resi_addr_card2 = resi_address.residential_address_card_v2

                    line1 = resi_addr_card2.address_line_1 or ""
                    line2 = resi_addr_card2.address_line_2 or ""
                    city = resi_addr_card2.city or ""
                    state = resi_addr_card2.state or ""
                    pin = resi_addr_card2.pin_code or ""
                    country = resi_addr_card2.country or ""
                    email = ""

                    if visa_info and visa_info.visa_request:
                        email = visa_info.visa_request.email_id or ""

                    pdf_model.visa_app_addr = ", ".join(
                        part
                        for part in [line1, line2, city, state, pin, country, email]  #
                        if part.strip()
                    )
                else:
                    resi_addr_card = resi_address.residential_address_card_v1

                    if resi_addr_card:
                        line1 = resi_addr_card.address_line_1 or ""
                        line2 = resi_addr_card.address_line_2 or ""
                        city = resi_addr_card.city or ""
                        state = resi_addr_card.state or ""
                        pin = resi_addr_card.pin_code or ""
                        country = resi_addr_card.country or ""
                        email = ""

                        if visa_info and visa_info.visa_request:
                            email = visa_info.visa_request.email_id or ""

                        pdf_model.visa_app_addr = ", ".join(
                            part
                            for part in [
                                line1,
                                line2,
                                city,
                                state,
                                pin,
                                country,
                                email,
                            ]
                            if part.strip()  #
                        )

                pdf_model.visa_oth_natl_no = (
                    resi_address.other_nationality == OPTION.NO
                )  #
                pdf_model.visa_oth_natl_yes = (
                    resi_address.other_nationality == OPTION.YES
                )  #

                if pdf_model.visa_oth_natl_yes:
                    res_oth_country = resi_address.resident_in_other_country
                    if res_oth_country:
                        pdf_model.visa_oth_natl_yes_res_num = (
                            resi_address.resident_in_other_country.residence_permit_number
                        )  #
                        if resi_address.resident_in_other_country.permit_date_of_expiry:
                            pdf_model.visa_oth_natl_yes_val_til = resi_address.resident_in_other_country.permit_date_of_expiry.strftime(  #
                                "%d-%m-%Y"
                            )

            if additional_details and additional_details.app_details:
                app_details = additional_details.app_details

                first_name = app_details.first_name or ""
                surname = app_details.surname or ""

                pdf_model.visa_applicant_diff_surnm_nm = ", ".join(
                    part for part in [first_name, surname] if part.strip()  #
                )

                app_line1 = app_details.address_line_1 or ""
                app_line2 = app_details.address_line_2 or ""
                app_city = app_details.city or ""
                app_state = app_details.state or ""
                app_pin = app_details.pin_code or ""
                app_country = app_details.country or ""
                app_email = app_details.email_address or ""

                pdf_model.visa_applicant_diff_addr = ", ".join(
                    part
                    for part in [
                        app_line1,
                        app_line2,
                        app_city,
                        app_state,
                        app_pin,
                        app_country,
                        app_email,
                    ]
                    if part.strip()  #
                )

                pdf_model.visa_applicant_diff_tel_num = (
                    app_details.telephone_mobile_number  #
                )

            previous_visas = schengen_visa_data.previous_visas

            pdf_model.visa_fingerprint_no = (
                previous_visas.fingerprint_collected == OPTION.NO  #
            )
            pdf_model.visa_fingerprint_yes = (
                previous_visas.fingerprint_collected == OPTION.YES  #
            )
            if pdf_model.visa_fingerprint_yes:
                if previous_visas.fingerprint_details.date_of_previous_visa:
                    pdf_model.visa_fingerprint_yes_date = previous_visas.fingerprint_details.date_of_previous_visa.strftime(  #
                        "%d-%m-%Y"
                    )
                pdf_model.visa_fingerprint_yes_sticker_num = (
                    previous_visas.fingerprint_details.visa_sticker_number  #
                )

            work_address = schengen_visa_data.work_address

            if (
                work_address
                and work_address.current_occupation_status
                == CURRENTOCCUPATIONSTATUS.EMPLOYEE
            ):
                work_details = work_address.work_details

                if work_details and work_details.occupation:
                    pdf_model.visa_curr_occ = work_address.work_details.occupation  #

                if work_details:
                    employer = work_details.employer_name or ""
                    address = work_details.work_address or ""
                    phone = work_details.work_phone or ""

                    pdf_model.visa_emp_stu_add_tel = ", ".join(
                        part for part in [employer, address, phone] if part.strip()  #
                    )
            elif (
                work_address
                and work_address.current_occupation_status
                == CURRENTOCCUPATIONSTATUS.STUDENT
            ):
                pdf_model.visa_curr_occ = "Student"  #
                edu_details = work_address.education_details

                if edu_details:
                    edu_estb = edu_details.establishment_name or ""
                    edu_estb_addr = edu_details.establishment_address or ""
                    edu_estb_phone = edu_details.establishment_contact or ""

                    pdf_model.visa_emp_stu_add_tel = ", ".join(
                        part
                        for part in [edu_estb, edu_estb_addr, edu_estb_phone]  #
                        if part.strip()
                    )
            elif (
                work_address
                and work_address.current_occupation_status
                == CURRENTOCCUPATIONSTATUS.NOTAPPLICABLE
            ):
                pdf_model.visa_curr_occ = "N/A"  #
                pdf_model.visa_emp_stu_add_tel = "N/A"  #
            else:
                pass

            accomodation = schengen_visa_data.accomodation
            if (
                accomodation
                and accomodation.accommodation_choice
                and accomodation.accommodation_choice.accommodation_option
                == ACCOMMODATIONARRANGEMENT.BOOKED
            ):
                booked = accomodation.booked_appointment

                if booked:
                    pdf_model.visa_invite_temp_accom = booked.accommodation_name
                    pdf_model.visa_invite_temp_accom_tel_num = (
                        booked.accommodation_phone
                    )

                    address = booked.accommodation_address or ""
                    email = booked.accommodation_email or ""

                    # Join only non-empty parts with comma
                    pdf_model.visa_invite_temp_accom_comm_details = ", ".join(  #
                        part for part in [address, email] if part.strip()
                    )
            else:
                inviter = accomodation.invitation_details

                if inviter:
                    pdf_model.visa_invite_temp_accom = inviter.inviter_name
                    pdf_model.visa_invite_temp_accom_tel_num = inviter.mobile_number

                    address = inviter.inviter_address or ""
                    email = inviter.email_id or ""

                    # Join only non-empty parts with comma
                    pdf_model.visa_invite_temp_accom_comm_details = ", ".join(  #
                        part for part in [address, email] if part.strip()
                    )

            return pdf_model

        except PluginException as pe:
            raise

        except Exception as e:
            raise PluginException(
                message=get_error_message(
                    error_message_code="LYIK_ERR_UNEXPECTED_ERROR"
                ),
                detailed_message=f"Unhandled exception occurred during field mapping for PDF. Error: {str(e)}",
            )


def add_other_detail(
    pdf_model: SchengenPDFModel, schengen_visa_data: Schengentouristvisa
) -> SchengenPDFModel:
    pdf_model.visa_civil_sts_oth_txt = (
        schengen_visa_data.passport.other_details.other_civil_status
    )
    return None
