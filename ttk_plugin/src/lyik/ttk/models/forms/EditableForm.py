from pydantic import BaseModel
from enum import Enum
from datetime import date

from new_schengentouristvisa import (
    PASSPORTTYPE,
    RootPassport,
    RootPassportInstructionPassport,
    RootPassportPassportDetails,
    Schengentouristvisa,
    GENDER,
    CIVILMARITALSTATUS,
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
            place_of_birth="Mumbai",
        ),
    )
)
if __name__ == "__main__":
    # You can now print the object or convert it to a dictionary/JSON
    # print(schengen_visa_data.model_dump_json(indent=2))

    # my_editable_form.visa_surname_family_name = (
    #     my_editable_form.passport.surname_family_name or ""
    # )
    # my_editable_form.visa_surname_at_birth = (
    #     my_editable_form.passport.surname_at_birth or ""
    # )
    my_editable_form.visa_first_name = (
        schengen_visa_data.passport.passport_details.first_name or ""
    )
    my_editable_form.visa_cob = (
        schengen_visa_data.passport.passport_details.date_of_birth or ""
    )
    my_editable_form.visa_dob = (
        schengen_visa_data.passport.passport_details.date_of_birth or ""
    )
    my_editable_form.visa_pob = (
        schengen_visa_data.passport.passport_details.place_of_birth or ""
    )
    my_editable_form.visa_issued_by_ctry = (
        schengen_visa_data.passport.passport_details.issued_by or ""
    )
    print(my_editable_form.model_dump_json(indent=2))
    # my_editable_form.visa_curr_natl = (
    #     schengen_visa_data.passport.other_details.other_nationality
    #     or ""
    # )
    # my_editable_form.visa_natl_at_birth = (
    #     schengen_visa_data.passport.other_details.nationality_of_birth or ""
    # )
    # if my_editable_form.gender == GENDER.M:
    #     schengen_visa_data.visa_sex_male = FieldToggle.YES

    # if my_editable_form.gender == GENDER.F:
    #     schengen_visa_data.visa_sex_female = FieldToggle.YES

    # if my_editable_form.civil_status == CIVILMARITALSTATUS.SINGLE:
    #     schengen_visa_data.visa_civil_sts_single = FieldToggle.YES

    # if my_editable_form.civil_status == CIVILMARITALSTATUS.MARRIED:
    #     schengen_visa_data.visa_civil_sts_married = FieldToggle.YES

    # if my_editable_form.civil_status == CIVILMARITALSTATUS.SEPARATED:
    #     schengen_visa_data.visa_civil_sts_seperated = FieldToggle.YES

    # if my_editable_form.civil_status == CIVILMARITALSTATUS.DIVORCED:
    #     schengen_visa_data.visa_civil_sts_divorced = FieldToggle.YES

    # if my_editable_form.civil_status == CIVILMARITALSTATUS.WIDOWED:
    #     schengen_visa_data.visa_civil_widow = FieldToggle.YES

    # if my_editable_form.civil_status == CIVILMARITALSTATUS.REGISTERED_PARTNER:
    #     schengen_visa_data.visa_civil_sts_reg_partner = FieldToggle.YES
    # if my_editable_form.civil_status == CIVILMARITALSTATUS.OTHER:
    #     my_editable_form.visa_civil_sts_oth = FieldToggle.YES
    #     my_editable_form.visa_civil_sts_oth_txt = (
    #         my_editable_form.civil_status_other or ""
    #     )
"""
following are not mapped:
    visa_parental_auth: str
    visa_nat_id_num: str
"""
