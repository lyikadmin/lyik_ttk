from pydantic import BaseModel
from enum import Enum

from lyik.ttk.models.forms.new_schengentouristvisa import (
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


empty_visa_application = Schengentouristvisa()

my_editable_form = EditableForm()
my_editable_form.visa_surname_family_name = (
    empty_visa_application.passport.surname_family_name or ""
)
my_editable_form.visa_surname_at_birth = (
    empty_visa_application.passport.surname_at_birth or ""
)
my_editable_form.visa_first_name = (
    empty_visa_application.passport.passport_details.first_name or ""
)
my_editable_form.visa_cob = (
    empty_visa_application.passport.passport_details.date_of_birth or ""
)
my_editable_form.visa_dob = (
    empty_visa_application.passport.passport_details.date_of_birth or ""
)
my_editable_form.visa_pob = (
    empty_visa_application.passport.passport_details.place_of_birth or ""
)
my_editable_form.visa_issued_by_ctry = (
    empty_visa_application.passport.passport_details.issued_by or ""
)


my_editable_form.visa_curr_natl = (
    empty_visa_application.passport.other_details.other_nationality or ""
)
my_editable_form.visa_natl_at_birth = (
    empty_visa_application.passport.other_details.nationality_of_birth or ""
)
if empty_visa_application.gender == GENDER.M:
    my_editable_form.visa_sex_male = FieldToggle.YES

if empty_visa_application.gender == GENDER.F:
    my_editable_form.visa_sex_female = FieldToggle.YES

if empty_visa_application.civil_status == CIVILMARITALSTATUS.SINGLE:
    my_editable_form.visa_civil_sts_single = FieldToggle.YES

if empty_visa_application.civil_status == CIVILMARITALSTATUS.MARRIED:
    my_editable_form.visa_civil_sts_married = FieldToggle.YES

if empty_visa_application.civil_status == CIVILMARITALSTATUS.SEPARATED:
    my_editable_form.visa_civil_sts_seperated = FieldToggle.YES

if empty_visa_application.civil_status == CIVILMARITALSTATUS.DIVORCED:
    my_editable_form.visa_civil_sts_divorced = FieldToggle.YES

if empty_visa_application.civil_status == CIVILMARITALSTATUS.WIDOWED:
    my_editable_form.visa_civil_widow = FieldToggle.YES

if empty_visa_application.civil_status == CIVILMARITALSTATUS.REGISTERED_PARTNER:
    my_editable_form.visa_civil_sts_reg_partner = FieldToggle.YES
if empty_visa_application.civil_status == CIVILMARITALSTATUS.OTHER:
    my_editable_form.visa_civil_sts_oth = FieldToggle.YES
    my_editable_form.visa_civil_sts_oth_txt = (
        empty_visa_application.civil_status_other or ""
    )
"""
following are not mapped:
    visa_parental_auth: str
    visa_nat_id_num: str
"""
