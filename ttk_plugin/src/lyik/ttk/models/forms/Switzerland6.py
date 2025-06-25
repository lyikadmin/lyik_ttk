from pydantic import BaseModel
import os


class Switzerland6(BaseModel):
    visa_surname_family_name: str = "Singh"  # PDF field: visa_surname_family_name
    visa_surname_at_birth: str = "Singh"  # PDF field: visa_surname_at_birth
    visa_first_name: str = "Dinesh"  # PDF field: visa_first_name
    visa_dob: str = "16-12-1971"  # PDF field: visa_dob
    visa_cob: str = "India"  # PDF field: visa_cob
    visa_sex_male: bool = True  # PDF field: visa_sex_male
    visa_sex_female: bool = False  # PDF field: visa_sex_female
    visa_sex_oth: bool = False  # PDF field: visa_sex_oth
    visa_civil_sts_single: bool = False  # PDF field: visa_civil_sts_single
    visa_civil_sts_married: bool = False  # PDF field: visa_civil_sts_married
    visa_civil_sts_seperated: bool = False  # PDF field: visa_civil_sts_seperated
    visa_civil_sts_divorced: bool = False  # PDF field: visa_civil_sts_divorced
    visa_civil_widow: bool = False  # PDF field: visa_civil_widow
    visa_civil_sts_reg_partner: bool = False  # PDF field: visa_civil_sts_reg_partner
    visa_civil_sts_oth: bool = False  # PDF field: visa_civil_sts_oth
    visa_pob: str = "Jaunpur"  # PDF field: visa_pob
    visa_curr_natl: str = "Indian"  # PDF field: visa_curr_natl
    visa_oth_natl: str = "Indian"  # PDF field: visa_oth_natl
    visa_civil_sts_oth_txt: str = ""  # PDF field: visa_civil_sts_oth_txt
    visa_natl_at_birth: str = "Indian"  # PDF field: visa_natl_at_birth
    visa_parental_auth: str = (
        "I am gardian of minor and I am Dinesh Singh"  # PDF field: visa_parental_auth
    )
    visa_nat_id_num: str = "Indian"  # PDF field: visa_nat_id_num
    visa_typ_trav_doc_ord: bool = False  # PDF field: visa_typ_trav_doc_ord
    visa_typ_trav_doc_service: bool = False  # PDF field: visa_typ_trav_doc_service
    visa_typ_trav_doc_special: bool = False  # PDF field: visa_typ_trav_doc_special
    visa_num_trav_doc: str = "aadhar no 3454654"  # PDF field: visa_num_trav_doc
    visa_fam_mem_eu_surname: str = "Singh"  # PDF field: visa_fam_mem_eu_surname
    visa_fam_mem_eu_dob: str = "16-12-1971"  # PDF field: visa_fam_mem_eu_dob
    visa_doi: str = "01-01-2020"  # PDF field: visa_doi
    visa_val_til: str = "01-01-2030"  # PDF field: visa_val_til
    visa_issued_by_ctry: str = "India"  # PDF field: visa_issued_by_ctry
    visa_fam_mem_eu_1st_nm: str = "Dinesh"  # PDF field: visa_fam_mem_eu_1st_nm
    visa_fam_mem_eu_natl: str = "Indian"  # PDF field: visa_fam_mem_eu_natl
    visa_fam_mem_eu_num_trav_doc: str = (
        "aadhar no 23453534534"  # PDF field: visa_fam_mem_eu_num_trav_doc
    )
    visa_fam_rs_eu_spouse: bool = False  # PDF field: visa_fam_rs_eu_spouse
    visa_fam_rs_eu_child: bool = False  # PDF field: visa_fam_rs_eu_child
    visa_fam_rs_eu_gc: bool = False  # PDF field: visa_fam_rs_eu_gc
    visa_fam_rs_eu_dependent: bool = False  # PDF field: visa_fam_rs_eu_dependent
    visa_fam_rs_eu_registered: bool = False  # PDF field: visa_fam_rs_eu_registered
    visa_fam_rs_eu_oth: bool = False  # PDF field: visa_fam_rs_eu_oth
    visa_oth_trav_doc_txt: str = ""  # PDF field: visa_oth_trav_doc_txt
    visa_fam_rs_eu_oth_txt: str = ""  # PDF field: visa_fam_rs_eu_oth_txt
    visa_typ_trav_doc_diplomatic: bool = (
        False  # PDF field: visa_typ_trav_doc_diplomatic
    )
    visa_typ_trav_doc_official: bool = False  # PDF field: visa_typ_trav_doc_official
    visa_typ_trav_doc_oth: bool = False  # PDF field: visa_typ_trav_doc_oth
    visa_app_addr: str = (
        "#12 10th cross, 2nd block rammurthy nagar karnataka India"  # PDF field: visa_app_addr
    )
    visa_app_tel_num: str = "34545464564"  # PDF field: visa_app_tel_num
    visa_oth_natl_no: bool = False  # PDF field: visa_oth_natl_no
    visa_oth_natl_yes: bool = True  # PDF field: visa_oth_natl_yes
    visa_curr_occ: str = "freelancer"  # PDF field: visa_curr_occ
    visa_emp_stu_add_tel: str = ""  # PDF field: visa_emp_stu_add_tel
    visa_jrn_purpose_visit_fnf: bool = False  # PDF field: visa_jrn_purpose_visit_fnf
    visa_jrn_purpose_tour: bool = False  # PDF field: visa_jrn_purpose_tour
    visa_jrn_purpose_business: bool = False  # PDF field: visa_jrn_purpose_business
    visa_jrn_purpose_culture: bool = False  # PDF field: visa_jrn_purpose_culture
    visa_jrn_purpose_official: bool = False  # PDF field: visa_jrn_purpose_official
    visa_jrn_purpose_study: bool = True  # PDF field: visa_jrn_purpose_study
    visa_jrn_purpose_med: bool = False  # PDF field: visa_jrn_purpose_med
    visa_jrn_purpose_sports: bool = False  # PDF field: visa_jrn_purpose_sports
    visa_jrn_purpose_transit: bool = False  # PDF field: visa_jrn_purpose_transit
    visa_jrn_purpose_oth: bool = False  # PDF field: visa_jrn_purpose_oth
    visa_addl_stay_info: str = "very good"  # PDF field: visa_addl_stay_info
    visa_mem_main_dst: str = "India"  # PDF field: visa_mem_main_dst
    visa_mem_1st_entry: str = "Karnataka"  # PDF field: visa_mem_1st_entry
    visa_entry_num_req_single: bool = False  # PDF field: visa_entry_num_req_single
    visa_entry_num_req_two: bool = False  # PDF field: visa_entry_num_req_two
    visa_entry_num_req_multi: bool = False  # PDF field: visa_entry_num_req_multi
    visa_oth_natl_yes_res_num: str = (
        "wreetre 435445"  # PDF field: visa_oth_natl_yes_res_num
    )
    visa_oth_natl_yes_val_til: str = "next year"  # PDF field: visa_oth_natl_yes_val_til
    visa_jrn_purpose_oth_txt: str = ""  # PDF field: visa_jrn_purpose_oth_txt
    visa_invite_temp_accom: str = "Dinesh Singh"  # PDF field: visa_invite_temp_accom
    visa_invite_temp_accom_comm_details: str = (
        "#12 10th cross, 2nd block rammurthy nagar karnataka India"  # PDF field: visa_invite_temp_accom_comm_details
    )
    visa_invite_org: str = " egger ergrgrgr"  # PDF field: visa_invite_org
    visa_invite_org_comm_details: str = (
        " ergrtgrtghrtghrthr"  # PDF field: visa_invite_org_comm_details
    )
    visa_trav_cost_self: bool = False  # PDF field: visa_trav_cost_self
    visa_trav_cost_self_cash: bool = False  # PDF field: visa_trav_cost_self_cash
    visa_trav_cost_self_tc: bool = False  # PDF field: visa_trav_cost_self_tc
    visa_trav_cost_self_cc: bool = False  # PDF field: visa_trav_cost_self_cc
    visa_trav_cost_self_ppa: bool = False  # PDF field: visa_trav_cost_self_ppa
    visa_trav_cost_self_ppt: bool = False  # PDF field: visa_trav_cost_self_ppt
    visa_trav_cost_self_oth: bool = False  # PDF field: visa_trav_cost_self_oth
    visa_invite_temp_accom_tel_num: str = (
        "2343242"  # PDF field: visa_invite_temp_accom_tel_num
    )
    visa_invite_temp_accom_tel_mun: str = (
        "2344354353"  # PDF field: visa_invite_temp_accom_tel_mun
    )
    visa_1st_arrival_date: str = "next month"  # PDF field: visa_1st_arrival_date
    visa_dptr_date: str = "next to next month"  # PDF field: visa_dptr_date
    visa_fingerprint_yes_date: str = ""  # PDF field: visa_fingerprint_yes_date
    visa_fingerprint_yes_sticker_num: str = (
        ""  # PDF field: visa_fingerprint_yes_sticker_num
    )
    visa_permit_final_ctry_dest_issued_by: str = (
        "Bengaluru"  # PDF field: visa_permit_final_ctry_dest_issued_by
    )
    visa_permit_final_ctry_dest_valid_from: str = (
        "01-01-2020"  # PDF field: visa_permit_final_ctry_dest_valid_from
    )
    visa_permit_final_ctry_dest_til: str = (
        "01-01-2030"  # PDF field: visa_permit_final_ctry_dest_til
    )
    visa_trav_cost_self_oth_txt: str = ""  # PDF field: visa_trav_cost_self_oth_txt
    visa_fingerprint_no: bool = False  # PDF field: visa_fingerprint_no
    visa_fingerprint_yes: bool = True  # PDF field: visa_fingerprint_yes
    visa_trav_cost_spons: bool = False  # PDF field: visa_trav_cost_spons
    visa_trav_cost_31_32: bool = False  # PDF field: visa_trav_cost_31_32
    visa_trav_cost: bool = False  # PDF field: visa_trav_cost
    visa_means_support_oth_cash: bool = False  # PDF field: visa_means_support_oth_cash
    visa_means_support_oth_ap: bool = False  # PDF field: visa_means_support_oth_ap
    visa_means_support_oth_expn_covered: bool = (
        False  # PDF field: visa_means_support_oth_expn_covered
    )
    visa_means_support_oth_ppt: bool = False  # PDF field: visa_means_support_oth_ppt
    visa_means_supportoth_oth: bool = False  # PDF field: visa_means_supportoth_oth
    visa_applicant_diff_surnm_nm: str = (
        "wet. reterre"  # PDF field: visa_applicant_diff_surnm_nm
    )
    visa_applicant_diff_addr: str = "freergr"  # PDF field: visa_applicant_diff_addr
    visa_applicant_diff_tel_num: str = (
        "efregergregre"  # PDF field: visa_applicant_diff_tel_num
    )
    visa_trav_cost_sponsor_txt: str = ""  # PDF field: visa_trav_cost_sponsor_txt
    visa_trav_cost_oth_txt: str = ""  # PDF field: visa_trav_cost_oth_txt
    visa_means_support_oth_txt: str = ""  # PDF field: visa_means_support_oth_txt

    def save_to_json(self, filename: str):
        """
        Writes all key-value pairs (attributes) of this EditableForm instance
        into a JSON file. This can be updated for returning a JSON string
        representation of the form data.

        Args:
            filename (str): The name of the JSON file to create or overwrite.
                            This can be a full path or a relative path.
        """
        try:
            json_data = self.model_dump_json(indent=4)  # Pydantic v2
            output_dir = os.path.dirname(filename)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json_data)
            print(f"Successfully saved form data to '{filename}'")
        except ImportError:
            print("Pydantic is likely an older version. Trying .json() method...")
            try:
                json_data = self.json(indent=4)
                output_dir = os.path.dirname(filename)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(json_data)
                print(f"Successfully saved form data to '{filename}' using .json()")
            except Exception as e:
                print(f"Error saving form data to '{filename}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving to '{filename}': {e}")
