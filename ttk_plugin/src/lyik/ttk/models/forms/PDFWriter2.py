""" PDFWriter2.py
This module provides functionality to fill a PDF form using data from a
Pydantic model. It uses the PyMuPDF library to manipulate PDF files and
fill form fields with the provided data."""

from datetime import date

# from Switzerland6 import Switzerland6
import fitz
from Switzerland6 import Switzerland6  # PyMuPDF

from new_schengentouristvisa import (CIVILMARITALSTATUS, COUNTRY3,
                                     EXPENSECOVERAGE1, EXPENSECOVERAGE2,
                                     EXPENSECOVERAGE3, EXPENSECOVERAGE4,
                                     EXPENSECOVERAGE5, FAMILYMEMBEROFEU,
                                     GENDER, OPTION, PASSPORTTYPE,
                                     PAYMENTMETHOD1, PAYMENTMETHOD2,
                                     PAYMENTMETHOD3, PAYMENTMETHOD4,
                                     PAYMENTMETHOD5, PAYMENTMETHOD6, RELATIONSHIP,
                                     RELATIONSHIPWITHEU, SPONSORTYPE1,
                                     SPONSORTYPE2, SPONSORTYPE3, SPONSORTYPE4,NUMBEROFENTRIES,
                                     RootAdditionalDetails,
                                     RootAdditionalDetailsAppDetails,
                                     RootAdditionalDetailsFamilyEu,
                                     RootAdditionalDetailsNationalId,
                                     RootAdditionalDetailsSponsorship,
                                     RootAdditionalDetailsTravelInfo,
                                     RootPassport, RootPassportOtherDetails,
                                     RootPassportPassportDetails,
                                     Schengentouristvisa)


def fill_pdf_form(
    pdf_template_path: str, output_pdf_path: str, model_data: Switzerland6
):
    """Fills a PDF form using data from a Pydantic model and saves the result."""
    try:
        doc = fitz.open(pdf_template_path)
        data_dict = model_data.dict()

        for page in doc:
            widgets = page.widgets()
            if not widgets:
                continue

            for widget in widgets:
                field_name = widget.field_name
                if field_name and field_name in data_dict:
                    value = data_dict[field_name]
                    if widget.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                        widget.field_value = "Yes" if value else "Off"
                    else:
                        widget.field_value = str(value)
                    widget.update()
        doc.bake()
        doc.save(output_pdf_path)
        print(f"✅ Filled PDF saved as: {output_pdf_path}")
    except Exception as e:
        print(f"❌ Error while filling PDF: {e}")


# Sample data from nested Schengen structure
schengen_visa_data = Schengentouristvisa(
    passport=RootPassport(
        passport_details=RootPassportPassportDetails(
            desired_validity="12",
            first_name="Dinesh",
            date_of_birth=date(1990, 5, 15),
            date_of_issue=date(2020, 1, 10),
            gender=GENDER.M,
            place_of_issue="Bengaluru",
            nationality="Indian",
            issued_by="Passport Authority",
            surname="Singh",
            passport_number="P1234567",
            date_of_expiry=date(2030, 1, 9),
            place_of_birth="Jaunpur",
            type_of_passport=PASSPORTTYPE.REGULAR,
            ovd_front={
                "file_name": "passport_front_image.jpg",
                "url": "https://example.com/passport_front_image.jpg",
            },
            ovd_back={
                "file_name": "passport_back_image.jpg",
                "url": "https://example.com/passport_back_image.jpg",
            },
            father_name="Father",
            mother_name="Mother",
            spouse_name="Sushma",
            address_line_1="10 Downing Street",
            address_line_2="Whitehall",
            pin_code="SW1A 2AA",
            city="Bengaluru",
            state="Karnataka",
            country="India",
        ),
        other_details=RootPassportOtherDetails(
            civil_status=CIVILMARITALSTATUS.SINGLE,
            nationality_of_birth="Indian",
            other_nationality="American",
        ),
    ),
    additional_details=RootAdditionalDetails(
        national_id=RootAdditionalDetailsNationalId(
            aadhaar_number="123456789012",
            aadhaar_upload={
                "file_name": "aadhaar.pdf",
                "url": "https://example.com/aadhaar.pdf",
            },
        ),
        travel_info=RootAdditionalDetailsTravelInfo(
            travelling_to_other_country=OPTION.YES,
            country_of_travel=COUNTRY3.BTN,
            valid_visa_for_country=OPTION.YES,
            start_date_of_visa=date(2025, 7, 1),
            end_date_of_visa=date(2025, 7, 30),
            number_of_entries=NUMBEROFENTRIES.SINGLE,
            visa_copy={
                "file_name": "uk_visa.jpg",
                "url": "https://example.com/uk_visa.jpg",
            },
        ),
        app_details=RootAdditionalDetailsAppDetails(),
        family_eu=RootAdditionalDetailsFamilyEu(
            is_family_member=FAMILYMEMBEROFEU.YES,
            given_name="Maria",
            surname="Gonzalez",
            nationality="Spanish",
            date_of_birth=date(1975, 1, 20),
            travel_document_id="ES987654321",
            relationship=RELATIONSHIPWITHEU.SPOUSE,
        ),
        sponsorship=RootAdditionalDetailsSponsorship(
            display_sponsorship_details="Please select the type of your sponsor(s). You may add more than one.",
            sponsorship_options_1=SPONSORTYPE1.SELF,
            sponsorship_options_2=SPONSORTYPE2.SPONSOR,
            sponsorship_options_3=SPONSORTYPE3.INVITER,
            sponsorship_options_4=SPONSORTYPE4.OTHER,
            display_sponsorship_support="Please select the Means of Support for covering your own costs.",
            support_means_cash=PAYMENTMETHOD1.CASH,
            support_means_travellers_cheque=PAYMENTMETHOD2.TRAVELLERS_CHEQUE,
            support_means_credit_card=PAYMENTMETHOD3.CREDIT_CARD,
            support_means_prepaid_accommodation=PAYMENTMETHOD4.PREPAID_ACCOMMODATION,
            support_means_prepaid_transport=PAYMENTMETHOD5.PREPAID_TRANSPORT,
            support_means_other=PAYMENTMETHOD6.OTHER,
            display_sponsorship_coverage="Please enter the Means of Support for the sponsor(s).",
            coverage_expense_cash=EXPENSECOVERAGE1.CASH,
            coverage_accommodation_provided=EXPENSECOVERAGE2.ACCOMMODATION_PROVIDED,
            coverage_all_covered=EXPENSECOVERAGE3.ALL_COVERED,
            coverage_prepaid_transport=EXPENSECOVERAGE4.PREPAID_TRANSPORT,
            coverage_other=EXPENSECOVERAGE5.OTHER,
        ),
    ),
)

if __name__ == "__main__":
    # Extract values from Schengen data to fill Switzerland6
    passport_details = schengen_visa_data.passport.passport_details
    other_details = schengen_visa_data.passport.other_details

    # Update Switzerland6 model values manually based on PDF field names
    # sample_data = Switzerland6(
    #     visa_surname_family_name=passport_details.surname,
    #     visa_surname_at_birth=passport_details.surname,
    #     visa_first_name=passport_details.first_name,
    #     visa_dob=str(passport_details.date_of_birth),
    #     visa_cob=passport_details.country,
    #     visa_sex_male=passport_details.gender.value == "male",
    #     visa_sex_female=passport_details.gender.value == "female",
    #     visa_sex_oth=passport_details.gender.value == "other",
    #     visa_civil_sts_single=other_details.civil_status.value == "single",
    #     visa_civil_sts_married=other_details.civil_status.value == "married",
    #     visa_civil_sts_seperated=other_details.civil_status.value == "separated",
    #     visa_civil_sts_divorced=other_details.civil_status.value == "divorced",
    #     visa_civil_widow=other_details.civil_status.value == "widow",
    #     visa_civil_sts_reg_partner=other_details.civil_status.value == "registered_partner",
    #     visa_civil_sts_oth=other_details.civil_status.value == "other",
    #     visa_pob=passport_details.place_of_birth,
    #     visa_curr_natl=passport_details.nationality,
    #     visa_oth_natl=other_details.other_nationality,
    #     visa_civil_sts_oth_txt="",  # <TODO>
    #     visa_natl_at_birth=other_details.nationality_of_birth,
    #     visa_parental_auth="",  # <TODO>
    #     visa_nat_id_num=schengen_visa_data.additional_details.national_id.aadhaar_number,
    #     visa_typ_trav_doc_ord=True,  # <TODO>
    #     visa_typ_trav_doc_service=False,
    #     visa_typ_trav_doc_special=False,
    #     visa_num_trav_doc=passport_details.passport_number,
    #     visa_fam_mem_eu_surname=schengen_visa_data.additional_details.family_eu.surname,
    #     visa_fam_mem_eu_dob=str(schengen_visa_data.additional_details.family_eu.date_of_birth),
    #     visa_doi=str(passport_details.date_of_issue),
    #     visa_val_til=str(passport_details.date_of_expiry),
    #     visa_issued_by_ctry=passport_details.issued_by,
    #     visa_fam_mem_eu_1st_nm=schengen_visa_data.additional_details.family_eu.given_name,
    #     visa_fam_mem_eu_natl=schengen_visa_data.additional_details.family_eu.nationality,
    #     visa_fam_mem_eu_num_trav_doc=schengen_visa_data.additional_details.family_eu.travel_document_id,
    #     visa_fam_rs_eu_spouse=schengen_visa_data.additional_details.family_eu.relationship.value == "spouse",
    #     visa_fam_rs_eu_child=schengen_visa_data.additional_details.family_eu.relationship.value == "child",
    #     visa_fam_rs_eu_gc=False,
    #     visa_fam_rs_eu_dependent=False,
    #     visa_fam_rs_eu_registered=False,
    #     visa_fam_rs_eu_oth=False,
    #     visa_oth_trav_doc_txt="",  # <TODO>
    #     visa_fam_rs_eu_oth_txt="",  # <TODO>
    #     visa_typ_trav_doc_diplomatic=False,
    #     visa_typ_trav_doc_official=False,
    #     visa_typ_trav_doc_oth=False,
    #     visa_app_addr=passport_details.address_line_1,
    #     visa_app_tel_num=passport_details.pin_code,  # <TODO: adjust if needed>
    #     visa_oth_natl_no=not bool(other_details.other_nationality),
    #     visa_oth_natl_yes=bool(other_details.other_nationality),
    #     visa_curr_occ="freelancer",  # <TODO>
    #     visa_emp_stu_add_tel="",  # <TODO>
    #     visa_jrn_purpose_visit_fnf=False,
    #     visa_jrn_purpose_tour=False,
    #     visa_jrn_purpose_business=False,
    #     visa_jrn_purpose_culture=False,
    #     visa_jrn_purpose_official=False,
    #     visa_jrn_purpose_study=True,
    #     visa_jrn_purpose_med=False,
    #     visa_jrn_purpose_sports=False,
    #     visa_jrn_purpose_transit=False,
    #     visa_jrn_purpose_oth=False,
    #     visa_addl_stay_info="very good",  # <TODO>
    #     visa_mem_main_dst=passport_details.country,
    #     visa_mem_1st_entry=passport_details.state,
    #     visa_entry_num_req_single=False,
    #     visa_entry_num_req_two=False,
    #     visa_entry_num_req_multi=False,
    #     visa_oth_natl_yes_res_num="",  # <TODO>
    #     visa_oth_natl_yes_val_til="",  # <TODO>
    #     visa_jrn_purpose_oth_txt="",  # <TODO>
    #     visa_invite_temp_accom="",  # <TODO>
    #     visa_invite_temp_accom_comm_details="",  # <TODO>
    #     visa_invite_org="",  # <TODO>
    #     visa_invite_org_comm_details="",  # <TODO>
    #     visa_trav_cost_self=False,
    #     visa_trav_cost_self_cash=schengen_visa_data.additional_details.sponsorship.support_means_cash.value,
    #     visa_trav_cost_self_tc=schengen_visa_data.additional_details.sponsorship.support_means_travellers_cheque.value,
    #     visa_trav_cost_self_cc=schengen_visa_data.additional_details.sponsorship.support_means_credit_card.value,
    #     visa_trav_cost_self_ppa=schengen_visa_data.additional_details.sponsorship.support_means_prepaid_accommodation.value,
    #     visa_trav_cost_self_ppt=schengen_visa_data.additional_details.sponsorship.support_means_prepaid_transport.value,
    #     visa_trav_cost_self_oth=schengen_visa_data.additional_details.sponsorship.support_means_other.value,
    #     visa_invite_temp_accom_tel_num="",  # <TODO>
    #     visa_invite_temp_accom_tel_mun="",  # <TODO>
    #     visa_1st_arrival_date=str(schengen_visa_data.additional_details.travel_info.start_date_of_visa),
    #     visa_dptr_date=str(schengen_visa_data.additional_details.travel_info.end_date_of_visa),
    #     visa_fingerprint_yes_date="",  # <TODO>
    #     visa_fingerprint_yes_sticker_num="",  # <TODO>
    #     visa_permit_final_ctry_dest_issued_by="",  # <TODO>
    #     visa_permit_final_ctry_dest_valid_from="",  # <TODO>
    #     visa_permit_final_ctry_dest_til="",  # <TODO>
    #     visa_trav_cost_self_oth_txt="",  # <TODO>
    #     visa_fingerprint_no=False,
    #     visa_fingerprint_yes=True,
    #     visa_trav_cost_spons=schengen_visa_data.additional_details.sponsorship.sponsorship_options_1.value,
    #     visa_trav_cost_31_32=schengen_visa_data.additional_details.sponsorship.sponsorship_options_2.value,
    #     visa_trav_cost=schengen_visa_data.additional_details.sponsorship.sponsorship_options_3.value,
    #     visa_means_support_oth_cash=schengen_visa_data.additional_details.sponsorship.coverage_expense_cash.value,
    #     visa_means_support_oth_ap=schengen_visa_data.additional_details.sponsorship.coverage_accommodation_provided.value,
    #     visa_means_support_oth_expn_covered=schengen_visa_data.additional_details.sponsorship.coverage_all_covered.value,
    #     visa_means_support_oth_ppt=schengen_visa_data.additional_details.sponsorship.coverage_prepaid_transport.value,
    #     visa_means_supportoth_oth=schengen_visa_data.additional_details.sponsorship.coverage_other.value,
    #     visa_applicant_diff_surnm_nm="",  # <TODO>
    #     visa_applicant_diff_addr="",  # <TODO>
    #     visa_applicant_diff_tel_num="",  # <TODO>
    #     visa_trav_cost_sponsor_txt="",  # <TODO>
    #     visa_trav_cost_oth_txt="",  # <TODO>
    #     visa_means_support_oth_txt="",  # <TODO>
    # )
    print(f"Filling Switzerland6 PDF form with sample data... passport_details.gender.value {passport_details.gender.value } ") 
    
    # sample_data = Switzerland6(
    #     visa_surname_family_name=passport_details.surname,
    #     visa_surname_at_birth=passport_details.surname,
    #     visa_first_name=passport_details.first_name,
    #     visa_dob=str(passport_details.date_of_birth),
    #     visa_cob=passport_details.country,
    #     visa_sex_male=passport_details.gender.value == GENDER.M,
    #     visa_sex_female=passport_details.gender.value == GENDER.F,
    #     visa_sex_oth=passport_details.gender.value == GENDER.O,
    #     visa_civil_sts_single=other_details.civil_status.value == CIVILMARITALSTATUS.SINGLE,
    #     visa_civil_sts_married=other_details.civil_status.value == CIVILMARITALSTATUS.MARRIED,
    #     visa_civil_sts_seperated=other_details.civil_status.value == CIVILMARITALSTATUS.SEPARATED,
    #     visa_civil_sts_divorced=other_details.civil_status.value == CIVILMARITALSTATUS.DIVORCED,
    #     visa_civil_widow=other_details.civil_status.value == CIVILMARITALSTATUS.WIDOWED,
    #     visa_civil_sts_reg_partner=other_details.civil_status.value == CIVILMARITALSTATUS.REGISTERED_PARTNER,
    #     visa_civil_sts_oth=other_details.civil_status.value == CIVILMARITALSTATUS.OTHER,
    #     visa_pob=passport_details.place_of_birth,
    #     visa_curr_natl=passport_details.nationality,
    #     visa_oth_natl=other_details.other_nationality,
    #     visa_civil_sts_oth_txt="",  # <TODO>
    #     visa_natl_at_birth=other_details.nationality_of_birth,
    #     visa_parental_auth="",  # <TODO>
    #     visa_nat_id_num=schengen_visa_data.additional_details.national_id.aadhaar_number,
    #     visa_typ_trav_doc_ord=True,  # <TODO>
    #     visa_typ_trav_doc_service=False,
    #     visa_typ_trav_doc_special=False,
    #     visa_num_trav_doc=passport_details.passport_number,
    #     visa_fam_mem_eu_surname=schengen_visa_data.additional_details.family_eu.surname,
    #     visa_fam_mem_eu_dob=str(schengen_visa_data.additional_details.family_eu.date_of_birth),
    #     visa_doi=str(passport_details.date_of_issue),
    #     visa_val_til=str(passport_details.date_of_expiry),
    #     visa_issued_by_ctry=passport_details.issued_by,
    #     visa_fam_mem_eu_1st_nm=schengen_visa_data.additional_details.family_eu.given_name,
    #     visa_fam_mem_eu_natl=schengen_visa_data.additional_details.family_eu.nationality,
    #     visa_fam_mem_eu_num_trav_doc=schengen_visa_data.additional_details.family_eu.travel_document_id,
    #     visa_fam_rs_eu_spouse=schengen_visa_data.additional_details.family_eu.relationship.value == "spouse",
    #     visa_fam_rs_eu_child=schengen_visa_data.additional_details.family_eu.relationship.value == "child",
    #     visa_fam_rs_eu_gc=False,
    #     visa_fam_rs_eu_dependent=False,
    #     visa_fam_rs_eu_registered=False,
    #     visa_fam_rs_eu_oth=False,
    #     visa_oth_trav_doc_txt="",  # <TODO>
    #     visa_fam_rs_eu_oth_txt="",  # <TODO>
    #     visa_typ_trav_doc_diplomatic=False,
    #     visa_typ_trav_doc_official=False,
    #     visa_typ_trav_doc_oth=False,
    #     visa_app_addr=passport_details.address_line_1,
    #     visa_app_tel_num=passport_details.pin_code,  # <TODO: check source>
    #     visa_oth_natl_no=not bool(other_details.other_nationality),
    #     visa_oth_natl_yes=bool(other_details.other_nationality),
    #     visa_curr_occ="freelancer",  # <TODO>
    #     visa_emp_stu_add_tel="",  # <TODO>
    #     visa_jrn_purpose_visit_fnf=False,
    #     visa_jrn_purpose_tour=False,
    #     visa_jrn_purpose_business=False,
    #     visa_jrn_purpose_culture=False,
    #     visa_jrn_purpose_official=False,
    #     visa_jrn_purpose_study=True,
    #     visa_jrn_purpose_med=False,
    #     visa_jrn_purpose_sports=False,
    #     visa_jrn_purpose_transit=False,
    #     visa_jrn_purpose_oth=False,
    #     visa_addl_stay_info="very good",
    #     visa_mem_main_dst=passport_details.country,
    #     visa_mem_1st_entry=passport_details.state,
    #     visa_entry_num_req_single=False,
    #     visa_entry_num_req_two=False,
    #     visa_entry_num_req_multi=False,
    #     visa_oth_natl_yes_res_num="",  # <TODO>
    #     visa_oth_natl_yes_val_til="",  # <TODO>
    #     visa_jrn_purpose_oth_txt="",  # <TODO>
    #     visa_invite_temp_accom="",  # <TODO>
    #     visa_invite_temp_accom_comm_details="",  # <TODO>
    #     visa_invite_org="",  # <TODO>
    #     visa_invite_org_comm_details="",  # <TODO>
    #     visa_trav_cost_self=False,
    #     visa_trav_cost_self_cash=schengen_visa_data.additional_details.sponsorship.support_means_cash.value == "CASH",
    #     visa_trav_cost_self_tc=schengen_visa_data.additional_details.sponsorship.support_means_travellers_cheque.value == "TRAVELLERS_CHEQUE",
    #     visa_trav_cost_self_cc=schengen_visa_data.additional_details.sponsorship.support_means_credit_card.value == "CREDIT_CARD",
    #     visa_trav_cost_self_ppa=schengen_visa_data.additional_details.sponsorship.support_means_prepaid_accommodation.value == "PREPAID_ACCOMMODATION",
    #     visa_trav_cost_self_ppt=schengen_visa_data.additional_details.sponsorship.support_means_prepaid_transport.value == "PREPAID_TRANSPORT",
    #     visa_trav_cost_self_oth=schengen_visa_data.additional_details.sponsorship.support_means_other.value == "OTHER",
    #     visa_invite_temp_accom_tel_num="",  # <TODO>
    #     visa_invite_temp_accom_tel_mun="",  # <TODO>
    #     visa_1st_arrival_date=str(schengen_visa_data.additional_details.travel_info.start_date_of_visa),
    #     visa_dptr_date=str(schengen_visa_data.additional_details.travel_info.end_date_of_visa),
    #     visa_fingerprint_yes_date="",  # <TODO>
    #     visa_fingerprint_yes_sticker_num="",  # <TODO>
    #     visa_permit_final_ctry_dest_issued_by="",  # <TODO>
    #     visa_permit_final_ctry_dest_valid_from="",  # <TODO>
    #     visa_permit_final_ctry_dest_til="",  # <TODO>
    #     visa_trav_cost_self_oth_txt="",  # <TODO>
    #     visa_fingerprint_no=False,
    #     visa_fingerprint_yes=True,
    #     visa_trav_cost_spons=schengen_visa_data.additional_details.sponsorship.sponsorship_options_1.value == "SPONSOR",
    #     visa_trav_cost_31_32=schengen_visa_data.additional_details.sponsorship.sponsorship_options_2.value == "SECTION_31_32",
    #     visa_trav_cost=schengen_visa_data.additional_details.sponsorship.sponsorship_options_3.value == "OTHER",
    #     visa_means_support_oth_cash=schengen_visa_data.additional_details.sponsorship.coverage_expense_cash.value == "CASH",
    #     visa_means_support_oth_ap=schengen_visa_data.additional_details.sponsorship.coverage_accommodation_provided.value == "ACCOMMODATION",
    #     visa_means_support_oth_expn_covered=schengen_visa_data.additional_details.sponsorship.coverage_all_covered.value == "ALL",
    #     visa_means_support_oth_ppt=schengen_visa_data.additional_details.sponsorship.coverage_prepaid_transport.value == "TRANSPORT",
    #     visa_means_supportoth_oth=schengen_visa_data.additional_details.sponsorship.coverage_other.value == "OTHER",
    #     visa_applicant_diff_surnm_nm="",  # <TODO>
    #     visa_applicant_diff_addr="",  # <TODO>
    #     visa_applicant_diff_tel_num="",  # <TODO>
    #     visa_trav_cost_sponsor_txt="",  # <TODO>
    #     visa_trav_cost_oth_txt="",  # <TODO>
    #     visa_means_support_oth_txt=""  # <TODO>
    # )
    sample_data = Switzerland6(
        visa_surname_family_name=passport_details.surname,
        visa_surname_at_birth=passport_details.surname,
        visa_first_name=passport_details.first_name,
        visa_dob=str(passport_details.date_of_birth),
        visa_cob=passport_details.country,
        visa_sex_male=passport_details.gender == GENDER.M,
        visa_sex_female=passport_details.gender == GENDER.F,
        visa_sex_oth=passport_details.gender in (GENDER.T, GENDER.O),
        visa_civil_sts_single=other_details.civil_status == CIVILMARITALSTATUS.SINGLE,
        visa_civil_sts_married=other_details.civil_status == CIVILMARITALSTATUS.MARRIED,
        visa_civil_sts_seperated=other_details.civil_status == CIVILMARITALSTATUS.SEPARATED,
        visa_civil_sts_divorced=other_details.civil_status == CIVILMARITALSTATUS.DIVORCED,
        visa_civil_widow=other_details.civil_status == CIVILMARITALSTATUS.WIDOWED,
        visa_civil_sts_reg_partner=other_details.civil_status == CIVILMARITALSTATUS.REGISTERED_PARTNER,
        visa_civil_sts_oth=other_details.civil_status == CIVILMARITALSTATUS.OTHER,
        visa_pob=passport_details.place_of_birth,
        visa_curr_natl=passport_details.nationality,
        visa_oth_natl=other_details.other_nationality,
        visa_civil_sts_oth_txt="",  # <TODO>
        visa_natl_at_birth=other_details.nationality_of_birth,
        visa_parental_auth="",  # <TODO>
        visa_nat_id_num=schengen_visa_data.additional_details.national_id.aadhaar_number,
        visa_typ_trav_doc_ord=True,  # <TODO>
        visa_typ_trav_doc_service=False,
        visa_typ_trav_doc_special=False,
        visa_num_trav_doc=passport_details.passport_number,
        visa_fam_mem_eu_surname=schengen_visa_data.additional_details.family_eu.surname,
        visa_fam_mem_eu_dob=str(schengen_visa_data.additional_details.family_eu.date_of_birth),
        visa_doi=str(passport_details.date_of_issue),
        visa_val_til=str(passport_details.date_of_expiry),
        visa_issued_by_ctry=passport_details.issued_by,
        visa_fam_mem_eu_1st_nm=schengen_visa_data.additional_details.family_eu.given_name,
        visa_fam_mem_eu_natl=schengen_visa_data.additional_details.family_eu.nationality,
        visa_fam_mem_eu_num_trav_doc=schengen_visa_data.additional_details.family_eu.travel_document_id,
        visa_fam_rs_eu_spouse=schengen_visa_data.additional_details.family_eu.relationship == RELATIONSHIPWITHEU.SPOUSE,
        visa_fam_rs_eu_child=schengen_visa_data.additional_details.family_eu.relationship == RELATIONSHIPWITHEU.CHILD,
        visa_fam_rs_eu_gc=False,
        visa_fam_rs_eu_dependent=False,
        visa_fam_rs_eu_registered=False,
        visa_fam_rs_eu_oth=False,
        visa_oth_trav_doc_txt="",  # <TODO>
        visa_fam_rs_eu_oth_txt="",  # <TODO>
        visa_typ_trav_doc_diplomatic=False,
        visa_typ_trav_doc_official=False,
        visa_typ_trav_doc_oth=False,
        visa_app_addr=passport_details.address_line_1,
        visa_app_tel_num=passport_details.pin_code,  # <TODO: check source>
        visa_oth_natl_no=not bool(other_details.other_nationality),
        visa_oth_natl_yes=bool(other_details.other_nationality),
        visa_curr_occ="freelancer",  # <TODO>
        visa_emp_stu_add_tel="",  # <TODO>
        visa_jrn_purpose_visit_fnf=False,
        visa_jrn_purpose_tour=False,
        visa_jrn_purpose_business=False,
        visa_jrn_purpose_culture=False,
        visa_jrn_purpose_official=False,
        visa_jrn_purpose_study=True,
        visa_jrn_purpose_med=False,
        visa_jrn_purpose_sports=False,
        visa_jrn_purpose_transit=False,
        visa_jrn_purpose_oth=False,
        visa_addl_stay_info="very good",
        visa_mem_main_dst=passport_details.country,
        visa_mem_1st_entry=passport_details.state,
        visa_entry_num_req_single=schengen_visa_data.additional_details.travel_info.number_of_entries == NUMBEROFENTRIES.SINGLE,
        visa_entry_num_req_two=schengen_visa_data.additional_details.travel_info.number_of_entries == NUMBEROFENTRIES.DOUBLE,
        visa_entry_num_req_multi=schengen_visa_data.additional_details.travel_info.number_of_entries == NUMBEROFENTRIES.MULTIPLE,
        visa_oth_natl_yes_res_num="",  # <TODO>
        visa_oth_natl_yes_val_til="",  # <TODO>
        visa_jrn_purpose_oth_txt="",  # <TODO>
        visa_invite_temp_accom="",  # <TODO>
        visa_invite_temp_accom_comm_details="",  # <TODO>
        visa_invite_org="",  # <TODO>
        visa_invite_org_comm_details="",  # <TODO>
        visa_trav_cost_self=False,
        visa_trav_cost_self_cash=schengen_visa_data.additional_details.sponsorship.support_means_cash.value == "CASH",
        visa_trav_cost_self_tc=schengen_visa_data.additional_details.sponsorship.support_means_travellers_cheque.value == "TRAVELLERS_CHEQUE",
        visa_trav_cost_self_cc=schengen_visa_data.additional_details.sponsorship.support_means_credit_card.value == "CREDIT_CARD",
        visa_trav_cost_self_ppa=schengen_visa_data.additional_details.sponsorship.support_means_prepaid_accommodation.value == "PREPAID_ACCOMMODATION",
        visa_trav_cost_self_ppt=schengen_visa_data.additional_details.sponsorship.support_means_prepaid_transport.value == "PREPAID_TRANSPORT",
        visa_trav_cost_self_oth=schengen_visa_data.additional_details.sponsorship.support_means_other.value == "OTHER",
        visa_invite_temp_accom_tel_num="",  # <TODO>
        visa_invite_temp_accom_tel_mun="",  # <TODO>
        visa_1st_arrival_date=str(schengen_visa_data.additional_details.travel_info.start_date_of_visa),
        visa_dptr_date=str(schengen_visa_data.additional_details.travel_info.end_date_of_visa),
        visa_fingerprint_yes_date="",  # <TODO>
        visa_fingerprint_yes_sticker_num="",  # <TODO>
        visa_permit_final_ctry_dest_issued_by="",  # <TODO>
        visa_permit_final_ctry_dest_valid_from="",  # <TODO>
        visa_permit_final_ctry_dest_til="",  # <TODO>
        visa_trav_cost_self_oth_txt="",  # <TODO>
        visa_fingerprint_no=False,
        visa_fingerprint_yes=True,
        visa_trav_cost_spons=schengen_visa_data.additional_details.sponsorship.sponsorship_options_1.value == "SPONSOR",
        visa_trav_cost_31_32=schengen_visa_data.additional_details.sponsorship.sponsorship_options_2.value == "SECTION_31_32",
        visa_trav_cost=schengen_visa_data.additional_details.sponsorship.sponsorship_options_3.value == "OTHER",
        visa_means_support_oth_cash=schengen_visa_data.additional_details.sponsorship.coverage_expense_cash.value == "CASH",
        visa_means_support_oth_ap=schengen_visa_data.additional_details.sponsorship.coverage_accommodation_provided.value == "ACCOMMODATION",
        visa_means_support_oth_expn_covered=schengen_visa_data.additional_details.sponsorship.coverage_all_covered.value == "ALL",
        visa_means_support_oth_ppt=schengen_visa_data.additional_details.sponsorship.coverage_prepaid_transport.value == "TRANSPORT",
        visa_means_supportoth_oth=schengen_visa_data.additional_details.sponsorship.coverage_other.value == "OTHER",
        visa_applicant_diff_surnm_nm="",  # <TODO>
        visa_applicant_diff_addr="",  # <TODO>
        visa_applicant_diff_tel_num="",  # <TODO>
        visa_trav_cost_sponsor_txt="",  # <TODO>
        visa_trav_cost_oth_txt="",  # <TODO>
        visa_means_support_oth_txt=""  # <TODO>
    )
    
    print(f"Sample data for Switzerland6: passport_details.gender.value == GENDER.M {passport_details.gender.value == GENDER.M}  passport_details.gender.value {passport_details.gender.value}")
    # print(f"Filling Switzerland6 PDF form with sample data... sample_data {sample_data}")
    template_pdf = "Switzerland6_original.pdf"
    filled_pdf = f"{template_pdf}_filled.pdf"

    fill_pdf_form(template_pdf, filled_pdf, sample_data)
