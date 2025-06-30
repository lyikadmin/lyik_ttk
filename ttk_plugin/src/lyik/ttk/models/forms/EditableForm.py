from pydantic import BaseModel
from enum import Enum
from datetime import date

from new_schengentouristvisa import (
    COUNTRY3,
    EXPENSECOVERAGE1,
    EXPENSECOVERAGE2,
    EXPENSECOVERAGE3,
    EXPENSECOVERAGE4,
    EXPENSECOVERAGE5,
    FAMILYMEMBEROFEU,
    OPTION,
    PASSPORTTYPE,
    PAYMENTMETHOD1,
    PAYMENTMETHOD2,
    PAYMENTMETHOD3,
    PAYMENTMETHOD4,
    PAYMENTMETHOD5,
    PAYMENTMETHOD6,
    RELATIONSHIPWITHEU,
    SPONSORTYPE1,
    SPONSORTYPE2,
    SPONSORTYPE3,
    SPONSORTYPE4,
    RootAdditionalDetails,
    RootAdditionalDetailsAppDetails,
    RootAdditionalDetailsFamilyEu,
    RootAdditionalDetailsNationalId,
    RootAdditionalDetailsSponsorship,
    RootAdditionalDetailsTravelInfo,
    RootPassport,
    RootPassportInstructionPassport,
    RootPassportOtherDetails,
    RootPassportPassportDetails,
    Schengentouristvisa,
    GENDER,
    CIVILMARITALSTATUS,
    PASSPORTTYPE,
)


class FieldToggle(Enum):
    YES = "Yes"
    NO = "No"


class EditableForm(BaseModel):
    visa_surname_family_name: str
    visa_surname_at_birth: str
    visa_first_name: str
    visa_dob: str
    visa_cob: str
    visa_sex_male: FieldToggle
    visa_sex_female: FieldToggle
    visa_sex_divers: FieldToggle
    visa_civil_sts_single: FieldToggle
    visa_civil_sts_married: FieldToggle
    visa_civil_sts_seperated: FieldToggle
    visa_civil_sts_divorced: FieldToggle
    visa_civil_widow: FieldToggle
    visa_civil_sts_reg_partner: FieldToggle
    visa_civil_sts_oth: FieldToggle
    visa_pob: str
    visa_curr_natl: str
    visa_natl_at_birth: str
    visa_civil_sts_oth_txt: str
    visa_parental_auth: str
    visa_nat_id_num: str
    visa_typ_trav_doc_ord: FieldToggle
    visa_typ_trav_doc_service: FieldToggle
    visa_typ_trav_doc_special: FieldToggle
    visa_num_trav_doc: str
    visa_fam_mem_eu_surname: str
    visa_fam_mem_eu_dob: str
    visa_doi: str
    visa_val_til: str
    visa_issued_by_ctry: str
    visa_fam_mem_eu_1st_nm: str
    visa_fam_mem_eu_natl: str
    visa_fam_mem_eu_num_trav_doc: str
    visa_fam_rs_eu_spouse: FieldToggle
    visa_fam_rs_eu_child: FieldToggle
    visa_fam_rs_eu_gc: FieldToggle
    visa_fam_rs_eu_dependent: FieldToggle
    visa_fam_rs_eu_registered: FieldToggle
    visa_fam_rs_eu_oth: FieldToggle
    visa_oth_trav_doc_txt: str
    visa_fam_rs_eu_oth_txt: str
    visa_typ_trav_doc_diplomatic: FieldToggle
    visa_typ_trav_doc_official: FieldToggle
    visa_typ_trav_doc_oth: FieldToggle
    visa_app_addr: str
    visa_app_tel_num: str
    visa_oth_natl_no: FieldToggle
    visa_oth_natl_yes: FieldToggle
    visa_curr_occ: str
    visa_emp_stu_add_tel_: str
    visa_jrn_purpose_visit_fnf: FieldToggle
    visa_jrn_purpose_tour: FieldToggle
    visa_jrn_purpose_business: FieldToggle
    visa_jrn_purpose_culture: FieldToggle
    visa_jrn_purpose_official: FieldToggle
    visa_jrn_purpose_study: FieldToggle
    visa_jrn_purpose_med: FieldToggle
    visa_jrn_purpose_sports: FieldToggle
    visa_jrn_purpose_transit: FieldToggle
    visa_jrn_purpose_oth: FieldToggle
    visa_addl_stay_info: str
    visa_mem_main_dst: str
    visa_mem_1st_entry: str
    visa_entry_num_req_single: FieldToggle
    visa_entry_num_req_two: FieldToggle
    visa_entry_num_req_multi: FieldToggle
    visa_oth_natl_yes_res_num: str
    visa_oth_natl_yes_val_til: str
    visa_jrn_purpose_oth_txt: str
    visa_invite_temp_accom: str
    visa_invite_temp_accom_comm_details: str
    visa_invite_org: str
    visa_invite_org_comm_details: str
    visa_trav_cost_self: FieldToggle
    visa_trav_cost_self_cash: FieldToggle
    visa_trav_cost_self_tc: FieldToggle
    visa_trav_cost_self_cc: FieldToggle
    visa_trav_cost_self_ppa: FieldToggle
    visa_trav_cost_self_ppt: FieldToggle
    visa_trav_cost_self_oth: FieldToggle
    visa_invite_temp_accom_tel_num: str
    visa_invite_temp_accom_tel_mun: str
    visa_1st_arrival_date_: str
    visa_dptr_date: str
    visa_fingerprint_yes_date: str
    visa_fingerprint_yes_sticker_num: str
    visa_permit_final_ctry_dest_issued_by: str
    visa_permit_final_ctry_dest_valid_from: str
    visa_permit_final_ctry_dest_til: str
    visa_trav_cost_self_oth_txt: str
    visa_fingerprint_no: FieldToggle
    visa_fingerprint_yes: FieldToggle
    visa_trav_cost_spons: FieldToggle
    visa_trav_cost_31_32: FieldToggle
    visa_trav_cost: FieldToggle
    visa_means_support_oth_cash: FieldToggle
    visa_means_support_oth_ap: FieldToggle
    visa_means_support_oth_expn_covered: FieldToggle
    visa_means_support_oth_ppt: FieldToggle
    visa_means_supportoth_oth: FieldToggle
    visa_applicant_diff_surnm_nm: str
    visa_applicant_diff_addr: str
    visa_applicant_diff_tel_num: str
    visa_trav_cost_sponsor_txt: str
    visa_trav_cost_oth_txt: str
    visa_means_support_oth_txt: str


my_editable_form = EditableForm(
    visa_surname_family_name="",
    visa_surname_at_birth="",
    visa_first_name="",
    visa_dob="",
    visa_cob="",
    visa_sex_male=FieldToggle(value=FieldToggle.YES),
    visa_sex_female=FieldToggle(value=FieldToggle.NO),
    visa_sex_divers=FieldToggle(value=FieldToggle.NO),
    visa_civil_sts_single=FieldToggle(value=FieldToggle.YES),
    visa_civil_sts_married=FieldToggle(value=FieldToggle.NO),
    visa_civil_sts_seperated=FieldToggle(value=FieldToggle.NO),
    visa_civil_sts_divorced=FieldToggle(value=FieldToggle.NO),
    visa_civil_widow=FieldToggle(value=FieldToggle.NO),
    visa_civil_sts_reg_partner=FieldToggle(value=FieldToggle.NO),
    visa_civil_sts_oth=FieldToggle(value=FieldToggle.NO),
    visa_pob="",
    visa_curr_natl="",
    visa_natl_at_birth="",
    visa_civil_sts_oth_txt="",
    visa_parental_auth="",
    visa_nat_id_num="",
    visa_typ_trav_doc_ord=FieldToggle(value=FieldToggle.NO),
    visa_typ_trav_doc_service=FieldToggle(value=FieldToggle.NO),
    visa_typ_trav_doc_special=FieldToggle(value=FieldToggle.NO),
    visa_num_trav_doc="",
    visa_fam_mem_eu_surname="",
    visa_fam_mem_eu_dob="",
    visa_doi="",
    visa_val_til="",
    visa_issued_by_ctry="",
    visa_fam_mem_eu_1st_nm="",
    visa_fam_mem_eu_natl="",
    visa_fam_mem_eu_num_trav_doc="",
    visa_fam_rs_eu_spouse=FieldToggle(value=FieldToggle.YES),
    visa_fam_rs_eu_child=FieldToggle(value=FieldToggle.NO),
    visa_fam_rs_eu_gc=FieldToggle(value=FieldToggle.NO),
    visa_fam_rs_eu_dependent=FieldToggle(value=FieldToggle.NO),
    visa_fam_rs_eu_registered=FieldToggle(value=FieldToggle.NO),
    visa_fam_rs_eu_oth=FieldToggle(value=FieldToggle.NO),
    visa_oth_trav_doc_txt="",
    visa_fam_rs_eu_oth_txt="",
    visa_typ_trav_doc_diplomatic=FieldToggle(value=FieldToggle.NO),
    visa_typ_trav_doc_official=FieldToggle(value=FieldToggle.NO),
    visa_typ_trav_doc_oth=FieldToggle(value=FieldToggle.NO),
    visa_app_addr="",
    visa_app_tel_num="",
    visa_oth_natl_no=FieldToggle(value=FieldToggle.NO),
    visa_oth_natl_yes=FieldToggle(value=FieldToggle.NO),
    visa_curr_occ="",
    visa_emp_stu_add_tel_="",
    visa_jrn_purpose_visit_fnf=FieldToggle(value=FieldToggle.NO),
    visa_jrn_purpose_tour=FieldToggle(value=FieldToggle.YES),
    visa_jrn_purpose_business=FieldToggle(value=FieldToggle.NO),
    visa_jrn_purpose_culture=FieldToggle(value=FieldToggle.NO),
    visa_jrn_purpose_official=FieldToggle(value=FieldToggle.NO),
    visa_jrn_purpose_study=FieldToggle(value=FieldToggle.NO),
    visa_jrn_purpose_med=FieldToggle(value=FieldToggle.NO),
    visa_jrn_purpose_sports=FieldToggle(value=FieldToggle.NO),
    visa_jrn_purpose_transit=FieldToggle(value=FieldToggle.NO),
    visa_jrn_purpose_oth=FieldToggle(value=FieldToggle.NO),
    visa_addl_stay_info="",
    visa_mem_main_dst="",
    visa_mem_1st_entry="",
    visa_entry_num_req_single=FieldToggle(value=FieldToggle.YES),
    visa_entry_num_req_two=FieldToggle(value=FieldToggle.NO),
    visa_entry_num_req_multi=FieldToggle(value=FieldToggle.NO),
    visa_oth_natl_yes_res_num="",
    visa_oth_natl_yes_val_til="",
    visa_jrn_purpose_oth_txt="",
    visa_invite_temp_accom="",
    visa_invite_temp_accom_comm_details="",
    visa_invite_org="",
    visa_invite_org_comm_details="",
    visa_trav_cost_self=FieldToggle(value=FieldToggle.YES),
    visa_trav_cost_self_cash=FieldToggle(value=FieldToggle.YES),
    visa_trav_cost_self_tc=FieldToggle(value=FieldToggle.NO),
    visa_trav_cost_self_cc=FieldToggle(value=FieldToggle.YES),
    visa_trav_cost_self_ppa=FieldToggle(value=FieldToggle.NO),
    visa_trav_cost_self_ppt=FieldToggle(value=FieldToggle.NO),
    visa_trav_cost_self_oth=FieldToggle(value=FieldToggle.NO),
    visa_invite_temp_accom_tel_num="",
    visa_invite_temp_accom_tel_mun="",  # Assuming this is a typo and should be the same as above or a different number.
    visa_1st_arrival_date_="",
    visa_dptr_date="",
    visa_fingerprint_yes_date="",
    visa_fingerprint_yes_sticker_num="",
    visa_permit_final_ctry_dest_issued_by="",
    visa_permit_final_ctry_dest_valid_from="",
    visa_permit_final_ctry_dest_til="",
    visa_trav_cost_self_oth_txt="",
    visa_fingerprint_no=FieldToggle(value=FieldToggle.NO),
    visa_fingerprint_yes=FieldToggle(value=FieldToggle.YES),
    visa_trav_cost_spons=FieldToggle(value=FieldToggle.NO),
    visa_trav_cost_31_32=FieldToggle(value=FieldToggle.YES),
    visa_trav_cost=FieldToggle(value=FieldToggle.YES),
    visa_means_support_oth_cash=FieldToggle(value=FieldToggle.NO),
    visa_means_support_oth_ap=FieldToggle(value=FieldToggle.NO),
    visa_means_support_oth_expn_covered=FieldToggle(value=FieldToggle.NO),
    visa_means_support_oth_ppt=FieldToggle(value=FieldToggle.NO),
    visa_means_supportoth_oth=FieldToggle(value=FieldToggle.NO),
    visa_applicant_diff_surnm_nm="",
    visa_applicant_diff_addr="",
    visa_applicant_diff_tel_num="",
    visa_trav_cost_sponsor_txt="",
    visa_trav_cost_oth_txt="",
    visa_means_support_oth_txt="",
)
# Create an object of Schengentouristvisa with sample data
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
            visa_copy={
                "file_name": "uk_visa.jpg",
                "url": "https://example.com/uk_visa.jpg",
            },
        ),
        app_details=RootAdditionalDetailsAppDetails(
            # No specific fields defined in RootAdditionalDetailsAppDetails, so it's empty for now
            # example_field="Some application detail"
        ),
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
            sponsorship_options_1=SPONSORTYPE1.SELF,  # Example of selecting one
            sponsorship_options_2=SPONSORTYPE2.SPONSOR,  # Example of selecting multiple
            sponsorship_options_3=SPONSORTYPE3.INVITER,
            sponsorship_options_4=SPONSORTYPE4.OTHER,
            display_sponsorship_support="Please select the Means of Support for covering your own costs. You can select more than one.",
            support_means_cash=PAYMENTMETHOD1.CASH,
            support_means_travellers_cheque=PAYMENTMETHOD2.TRAVELLERS_CHEQUE,
            support_means_credit_card=PAYMENTMETHOD3.CREDIT_CARD,
            support_means_prepaid_accommodation=PAYMENTMETHOD4.PREPAID_ACCOMMODATION,
            support_means_prepaid_transport=PAYMENTMETHOD5.PREPAID_TRANSPORT,
            support_means_other=PAYMENTMETHOD6.OTHER,
            display_sponsorship_coverage="Please enter the Means of Support for the sponsor(s). You can select more than one.",
            coverage_expense_cash=EXPENSECOVERAGE1.CASH,
            coverage_accommodation_provided=EXPENSECOVERAGE2.ACCOMMODATION_PROVIDED,
            coverage_all_covered=EXPENSECOVERAGE3.ALL_COVERED,
            coverage_prepaid_transport=EXPENSECOVERAGE4.PREPAID_TRANSPORT,
            coverage_other=EXPENSECOVERAGE5.OTHER,  # Example
        ),
    ),
)
if __name__ == "__main__":
    # You can now print the object or convert it to a dictionary/JSON
    # print(schengen_visa_data.model_dump_json(indent=2))

    my_editable_form.visa_surname_family_name = (
        schengen_visa_data.passport.passport_details.father_name or ""
    )
    my_editable_form.visa_surname_at_birth = (
        schengen_visa_data.passport.passport_details.mother_name or ""
    )
    my_editable_form.visa_first_name = (
        schengen_visa_data.passport.passport_details.first_name or ""
    )
    my_editable_form.visa_cob = (
        schengen_visa_data.passport.passport_details.country or ""
    )
    my_editable_form.visa_dob = (
        schengen_visa_data.passport.passport_details.date_of_birth or ""
    )
    my_editable_form.visa_pob = (
        schengen_visa_data.passport.passport_details.place_of_birth or ""
    )
    my_editable_form.visa_fam_mem_eu_surname = (
        schengen_visa_data.additional_details.family_eu.surname or ""
    )
    my_editable_form.visa_fam_mem_eu_dob = (
        schengen_visa_data.additional_details.family_eu.date_of_birth or ""
    )
    my_editable_form.visa_fam_mem_eu_1st_nm = (
        schengen_visa_data.additional_details.family_eu.given_name or ""
    )
    my_editable_form.visa_fam_mem_eu_natl = (
        schengen_visa_data.additional_details.family_eu.nationality or ""
    )
    my_editable_form.visa_fam_mem_eu_num_trav_doc = (
        schengen_visa_data.additional_details.family_eu.travel_document_id or ""
    )
    my_editable_form.visa_fam_rs_eu_spouse = (
        FieldToggle(value=FieldToggle.YES)
        if schengen_visa_data.additional_details.family_eu.relationship
        == RELATIONSHIPWITHEU.SPOUSE
        else FieldToggle(value=FieldToggle.NO)
    )
    my_editable_form.visa_fam_rs_eu_child = (
        FieldToggle(value=FieldToggle.YES)
        if schengen_visa_data.additional_details.family_eu.relationship
        == RELATIONSHIPWITHEU.CHILD
        else FieldToggle(value=FieldToggle.NO)
    )
    my_editable_form.visa_fam_rs_eu_gc = (
        FieldToggle(value=FieldToggle.YES)
        if schengen_visa_data.additional_details.family_eu.relationship
        == RELATIONSHIPWITHEU.GRANDCHILD
        else FieldToggle(value=FieldToggle.NO)
    )
    my_editable_form.visa_fam_rs_eu_dependent = (
        FieldToggle(value=FieldToggle.YES)
        if schengen_visa_data.additional_details.family_eu.relationship
        == RELATIONSHIPWITHEU.DEPENDENT_ASCENDANT
        else FieldToggle(value=FieldToggle.NO)
    )
    my_editable_form.visa_fam_rs_eu_registered = (
        FieldToggle(value=FieldToggle.YES)
        if schengen_visa_data.additional_details.family_eu.relationship
        == RELATIONSHIPWITHEU.REGISTERED_PARTNER
        else FieldToggle(value=FieldToggle.NO)
    )
    my_editable_form.visa_fam_rs_eu_oth = (
        FieldToggle(value=FieldToggle.YES)
        if schengen_visa_data.additional_details.family_eu.relationship
        == RELATIONSHIPWITHEU.OTHER
        else FieldToggle(value=FieldToggle.NO)
    )
    my_editable_form.visa_issued_by_ctry = (
        schengen_visa_data.passport.passport_details.issued_by or ""
    )
    if (
        schengen_visa_data.passport.other_details.civil_status
        == CIVILMARITALSTATUS.SINGLE
    ):
        my_editable_form.visa_civil_sts_single = FieldToggle(value=FieldToggle.YES)

    my_editable_form.visa_curr_natl = (
        schengen_visa_data.passport.other_details.other_nationality or ""
    )
    my_editable_form.visa_natl_at_birth = (
        schengen_visa_data.passport.other_details.nationality_of_birth or ""
    )
    if (
        schengen_visa_data.passport.passport_details.type_of_passport
        == PASSPORTTYPE.REGULAR
    ):
        my_editable_form.visa_typ_trav_doc_ord = FieldToggle(value=FieldToggle.YES)

    # print(my_editable_form.model_dump_json(indent=2))

    unset_keys = []
    set_key_values = {}

    # Iterate over all fields defined in the model
    for field_name, field_info in EditableForm.model_fields.items():
        current_value = getattr(my_editable_form, field_name)

        if isinstance(current_value, FieldToggle):
            if not current_value.value:
                unset_keys.append(field_name)
            else:
                set_key_values[field_name] = (
                    current_value.value
                )  # Store boolean value for clarity
        elif current_value is None:
            unset_keys.append(field_name)
        elif isinstance(current_value, str) and current_value == "":
            # For string fields, consider empty string as "not set" if that's the desired interpretation
            unset_keys.append(field_name)
        else:
            set_key_values[field_name] = current_value
    print(
        "--- Keys which have not been explicitly set (or are empty/default false) ---"
    )
    for key in unset_keys:
        print(f"- {key}")

    # print("\n--- Keys and values which are set ---")
    # for key, value in set_key_values.items():
    #     print(f"- {key}: {value}")
"""
following are not mapped:
    visa_parental_auth: str
    visa_nat_id_num: str
"""
