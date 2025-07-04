from typing import get_args, get_origin, Union, Dict, Any
from pydantic import BaseModel
from enum import Enum
import inspect
import fitz
from new_schengentouristvisa import (
    Schengentouristvisa,
    GENDER,
    CIVILMARITALSTATUS,
    RELATIONSHIPWITHEU,
    PAYMENTMETHOD1,
    PAYMENTMETHOD2,
    PAYMENTMETHOD3,
    PAYMENTMETHOD4,
    PAYMENTMETHOD5,
    PAYMENTMETHOD6,
    SPONSORTYPE1,
)
from Switzerland6 import Switzerland6


def unwrap_optional(t):
    if get_origin(t) is Union:
        args = [a for a in get_args(t) if a is not type(None)]
        if len(args) == 1:
            return args[0]
    return t


def is_enum_or_primitive(t):
    return inspect.isclass(t) and issubclass(t, (str, int, float, bool, Enum))


def create_dummy_value(t):
    if inspect.isclass(t) and issubclass(t, Enum):
        return list(t)[0]
    elif t == str:
        return "example"
    elif t == int:
        return 123
    elif t == float:
        return 1.23
    elif t == bool:
        return True
    return None


def build_model_with_dummy_values(model_class: type[BaseModel]):
    instance_data = {}
    for field_name, field in model_class.model_fields.items():
        field_type = unwrap_optional(field.annotation)
        if is_enum_or_primitive(field_type):
            instance_data[field_name] = create_dummy_value(field_type)
        elif inspect.isclass(field_type) and issubclass(field_type, BaseModel):
            instance_data[field_name] = build_model_with_dummy_values(field_type)
        else:
            instance_data[field_name] = None
    return model_class(**instance_data)


def flatten_model_fields(model: BaseModel, prefix=""):
    items = {}
    for name, value in model:
        key = f"{prefix}.{name}" if prefix else name
        if isinstance(value, BaseModel):
            items.update(flatten_model_fields(value, key))
        else:
            items[key] = (type(value).__name__, value)
    return items
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
# def resolve_attr_path(obj, path: str):
#     """Safely resolves a dotted attribute path from an object."""
#     try:
#         for attr in path.split("."):
#             if obj is None:
#                 return None
#             obj = getattr(obj, attr)
#         return obj
#     except AttributeError:
#         return None
def resolve_attr_path(obj, path: str):
    """Safely resolves a dotted attribute path from an object."""
    try:
        for attr in path.split("."):
            if obj is None:
                return None
            obj = getattr(obj, attr)
        return obj
    except AttributeError:
        return None
def resolve_path(obj, path: str):
    """Resolve dotted attribute path and return value or empty string if None."""
    try:
        for attr in path.split('.'):
            obj = getattr(obj, attr)
        return obj if obj is not None else ""
    except AttributeError:
        return ""    
def is_boolean_expression(expr: str):
    """Checks if a manual mapping string is a boolean expression."""
    return any(op in expr for op in ["==", "!=", "in", "not in", "any(", " and ", " or "])
    
if __name__ == "__main__":

    # Step 1: Create dummy models
    schengen_model = build_model_with_dummy_values(Schengentouristvisa)
    swiss_model = Switzerland6()

    schengen_flat = flatten_model_fields(schengen_model)
    swiss_flat = flatten_model_fields(swiss_model)

    # Step 2: Manual flat mappings
    manual_mappings = {
        "visa_first_name": "passport.passport_details.first_name",
        "visa_surname_family_name": "passport.passport_details.surname",
        "visa_dob": "passport.passport_details.date_of_birth",
        "visa_num_trav_doc": "passport.passport_details.passport_number",
        "visa_issued_by_ctry": "passport.passport_details.issued_by",
        "visa_val_til": "passport.passport_details.date_of_expiry",
        "visa_doi": "passport.passport_details.date_of_issue",
        "visa_nat_id_num": "additional_details.national_id.aadhaar_number",
        "visa_cob": "passport.passport_details.place_of_birth",
        "visa_natl_at_birth": "passport.other_details.nationality_of_birth",
        "visa_curr_natl": "passport.passport_details.nationality",
        "visa_fam_mem_eu_surname": "additional_details.family_eu.surname",
        "visa_fam_mem_eu_1st_nm": "additional_details.family_eu.given_name",
        "visa_fam_mem_eu_dob": "additional_details.family_eu.date_of_birth",
        "visa_fam_mem_eu_natl": "additional_details.family_eu.nationality",
        "visa_fam_mem_eu_num_trav_doc": "additional_details.family_eu.travel_document_id",
        # "visa_1st_arrival_date": "visa_request_information.visa_request.arrival_date",
    }

    # Step 3: Boolean field mappings
    boolean_mappings = {}
    not_mapped_boolean = []

    def try_map(key, expr_func):
        try:
            boolean_mappings[key] = expr_func()
        except Exception as e:
            not_mapped_boolean.append(key)

    try_map("visa_sex_male", lambda: schengen_model.passport.passport_details.gender == GENDER.M)
    try_map("visa_sex_female", lambda: schengen_model.passport.passport_details.gender == GENDER.F)
    try_map("visa_sex_oth", lambda: schengen_model.passport.passport_details.gender not in [GENDER.M, GENDER.F])

    try_map("visa_civil_sts_single", lambda: schengen_model.passport.other_details.civil_status == CIVILMARITALSTATUS.SINGLE)
    try_map("visa_civil_sts_married", lambda: schengen_model.passport.other_details.civil_status == CIVILMARITALSTATUS.MARRIED)
    try_map("visa_civil_sts_divorced", lambda: schengen_model.passport.other_details.civil_status == CIVILMARITALSTATUS.DIVORCED)
    try_map("visa_civil_sts_seperated", lambda: schengen_model.passport.other_details.civil_status == CIVILMARITALSTATUS.SEPARATED)
    try_map("visa_civil_sts_reg_partner", lambda: schengen_model.passport.other_details.civil_status == CIVILMARITALSTATUS.REGISTERED_PARTNER)
    try_map("visa_civil_sts_oth", lambda: schengen_model.passport.other_details.civil_status == CIVILMARITALSTATUS.OTHER)
    try_map("visa_civil_widow", lambda: schengen_model.passport.other_details.civil_status == CIVILMARITALSTATUS.WIDOWED)

    try_map("visa_fam_rs_eu_spouse", lambda: schengen_model.additional_details.family_eu.relationship == RELATIONSHIPWITHEU.SPOUSE)
    try_map("visa_fam_rs_eu_child", lambda: schengen_model.additional_details.family_eu.relationship == RELATIONSHIPWITHEU.CHILD)
    try_map("visa_fam_rs_eu_registered", lambda: schengen_model.additional_details.family_eu.relationship == RELATIONSHIPWITHEU.REGISTERED_PARTNER)
    try_map("visa_fam_rs_eu_dependent", lambda: schengen_model.additional_details.family_eu.relationship == RELATIONSHIPWITHEU.DEPENDENT)
    try_map("visa_fam_rs_eu_oth", lambda: schengen_model.additional_details.family_eu.relationship == RELATIONSHIPWITHEU.OTHER)

    try_map("visa_oth_natl_yes", lambda: bool(schengen_model.passport.other_details.other_nationality))
    try_map("visa_oth_natl_no", lambda: not schengen_model.passport.other_details.other_nationality)

    try_map("visa_entry_num_req_single", lambda: schengen_model.visa_request_information.visa_request.no_of_entries == 'SINGLE')
    try_map("visa_entry_num_req_two", lambda: schengen_model.visa_request_information.visa_request.no_of_entries == 'TWO')
    try_map("visa_entry_num_req_multi", lambda: schengen_model.visa_request_information.visa_request.no_of_entries == 'MULTIPLE')

    try_map("visa_trav_cost_self_cash", lambda: schengen_model.additional_details.sponsorship.support_means_cash == PAYMENTMETHOD1.CASH)
    try_map("visa_trav_cost_self_tc", lambda: schengen_model.additional_details.sponsorship.support_means_travellers_cheque == PAYMENTMETHOD2.TRAVELLERS_CHEQUE)
    try_map("visa_trav_cost_self_cc", lambda: schengen_model.additional_details.sponsorship.support_means_credit_card == PAYMENTMETHOD3.CREDIT_CARD)
    try_map("visa_trav_cost_self_ppa", lambda: schengen_model.additional_details.sponsorship.support_means_prepaid_accommodation == PAYMENTMETHOD4.PREPAID_ACCOMMODATION)
    try_map("visa_trav_cost_self_ppt", lambda: schengen_model.additional_details.sponsorship.support_means_prepaid_transport == PAYMENTMETHOD5.PREPAID_TRANSPORT)
    try_map("visa_trav_cost_self_oth", lambda: schengen_model.additional_details.sponsorship.support_means_other == PAYMENTMETHOD6.OTHER)

    try_map("visa_trav_cost_spons", lambda: any([
        schengen_model.additional_details.sponsorship.sponsorship_options_1,
        schengen_model.additional_details.sponsorship.sponsorship_options_2,
        schengen_model.additional_details.sponsorship.sponsorship_options_3
    ]))
    try_map("visa_trav_cost_self", lambda: schengen_model.additional_details.sponsorship.sponsorship_options_1 == SPONSORTYPE1.SELF)

    # Step 4: Output
    print("\n✅ MAPPED FIELDS (Manual):")
    sample_data = {}
    for swiss_key, schengen_key in manual_mappings.items():
    #     if swiss_key not in swiss_flat:
    #         print(f"{swiss_key} ❌ not in Switzerland6")
    #         continue

    #     if schengen_key not in schengen_flat and not is_boolean_expression(schengen_key):
    #         print(f"{schengen_key} ❌ not in Schengen model")
    #         continue

    #     if is_boolean_expression(schengen_key):
    #         try:
    #             # Evaluate the boolean expression safely in the local scope
    #             value = eval(schengen_key, globals(), {"schengen_model": schengen_model})
    #         except Exception as e:
    #             print(f"{swiss_key} ⚠️ Eval error: {e}")
    #             value = False  # or None
    #     else:
    #         value = resolve_attr_path(schengen_model, schengen_key)
    #         if value is None:
    #             value = ""

    #     print(f"{swiss_key}  <=OOOOO=>  {schengen_key}  →  {value!r}")
    #     sample_data[swiss_key] = value
    # for swiss_key, schengen_key in manual_mappings.items():
        if swiss_key not in swiss_flat:
            print(f"{swiss_key} ❌ not in Switzerland6")
            continue

        is_boolean = is_boolean_expression(schengen_key)

        if schengen_key not in schengen_flat and not is_boolean:
            print(f"{schengen_key} ❌ not in Schengen model")
            continue

        try:
            if is_boolean:
                # Evaluate expressions like: schengen_model.passport.gender == GENDER.M
                value = eval(schengen_key, globals(), {"schengen_model": schengen_model})
            else:
                value = resolve_attr_path(schengen_model, schengen_key)
                if value is None:
                    value = ""
        except Exception as e:
            print(f"{swiss_key} ⚠️ Error evaluating '{schengen_key}': {e}")
            value = "" if not is_boolean else False

        print(f"{swiss_key}  <=OOOOO=>  {schengen_key}  →  {value!r}")
        sample_data[swiss_key] = value
    print("\n✅ BOOLEAN FIELD MAPPINGS:")
    for k, v in boolean_mappings.items():
        print(f"{k}: {v}")
        sample_data[k] = v

    print("\n⚠️ BOOLEAN FIELDS NOT MAPPED (due to missing Enums or Attributes):")
    for k in not_mapped_boolean:
        print(f"{k}")

    mapped_swiss_keys = set(manual_mappings.keys()).union(boolean_mappings.keys())
    mapped_schengen_keys = set(manual_mappings.values())

    unmapped_swiss = set(swiss_flat.keys()) - mapped_swiss_keys
    unmapped_schengen = set(schengen_flat.keys()) - mapped_schengen_keys

    print("\n❌ UNMAPPED FIELDS IN Switzerland6:")
    for key in sorted(unmapped_swiss):
        t, v = swiss_flat[key]
        print(f"{key}: {v!r} (type: {t})")

    print("\n❌ UNMAPPED FIELDS IN Schengentouristvisa:")
    for key in sorted(unmapped_schengen):
        t, v = schengen_flat[key]
        print(f"{key}: {v!r} (type: {t})")
    template_pdf = "Switzerland6_original.pdf"
    filled_pdf = f"{template_pdf}_filled.pdf"
    print(f"Filling Switzerland6 PDF form with sample data... {sample_data}")
    model_instance = Switzerland6(**sample_data)

    # Then call the PDF fill function
    fill_pdf_form(template_pdf, filled_pdf, model_instance)    
    # fill_pdf_form(template_pdf, filled_pdf, sample_data)