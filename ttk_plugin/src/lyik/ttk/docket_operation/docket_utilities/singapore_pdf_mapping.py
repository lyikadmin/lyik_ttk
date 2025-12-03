from lyik.ttk.models.forms.singaporevisaapplicationform import (
    Singaporevisaapplicationform,
    CIVILMARITALSTATUSSGP,
    COUNTRY3,
    GENDERSGP,
    OPTION,
    PASSPORTTYPESGP,
    RELATIONSHIP,
    RELATIONSHIPWITHAPPLICANTSGP,
    SGPSTAY,
    SPOUSENATIONALITY,
    VISATYPE,
    RootPassportPassportDetails,
    RootPassportOtherDetails,
    RootPassportTravelCompanionDetails,
    RootResidentialAddressResidentialAddressCardV1,
    RootVisaRequestInformationVisaRequest,
    RootWorkAddressWorkDetails,
    RootWorkAddressEducationDetails,
    RootAccomodationBookedAppointment,
    RootAccomodationInvitationDetails,
    RootAdditionalDetailsResidenceInOtherCountryGroupOthercountryresidenceCountryResidence,
    RootAdditionalDetails,
    RootDeclarationApplicantAntecedent,
)
from lyik.ttk.models.pdf.Singaporepdfmodel import Singaporepdfmodel
from datetime import date

from typing import Type, Any, Tuple, Dict, List


def build_typed_from_optional(maybe_model_or_dict: Any, model_cls: Type[Any]) -> Any:
    """
    If maybe_model_or_dict is a Pydantic model -> use its model_dump() dict.
    If it's a dict -> use as-is.
    If it's None -> use {} so model_cls will be created with defaults/None.
    Returns an instance of model_cls.
    """
    if maybe_model_or_dict is None:
        raw = {}
    elif hasattr(maybe_model_or_dict, "model_dump"):
        raw = maybe_model_or_dict.model_dump()
    elif isinstance(maybe_model_or_dict, dict):
        raw = maybe_model_or_dict
    else:
        raw = {}

    return model_cls(**raw)


def extract_country_residences(additional_details: RootAdditionalDetails):
    CountryResidenceCls = RootAdditionalDetailsResidenceInOtherCountryGroupOthercountryresidenceCountryResidence
    groups = (
        additional_details.residence_in_other_country_group
        if additional_details
        else None
    ) or []

    country_residences = []
    for grp in groups:
        # grp is FieldGrpRootAdditionalDetailsResidenceInOtherCountryGroup or None
        # its .othercountryresidence may be None or a model
        othercountry = grp.othercountryresidence if grp else None

        # othercountry.country_residence may be None or a model/dict
        country_res = None
        if othercountry is not None:
            # Use helper to build typed instance safely
            country_res = build_typed_from_optional(
                othercountry.country_residence, CountryResidenceCls
            )
        else:
            # create empty typed instance so downstream always gets one
            country_res = CountryResidenceCls(**{})

        country_residences.append(country_res)

    return country_residences


def split_date(d: date) -> Tuple[str, str, str]:
    """
    Takes a date object, formats it as DD-MM-YYYY,
    and returns (dd, mm, yyyy) as strings.
    """
    formatted = d.strftime("%d-%m-%Y")
    dd, mm, yyyy = formatted.split("-")
    return dd, mm, yyyy


def split_in_chunks(s: str, chunk_size: int) -> List[str]:
    """
    Split a string into chunks of size `chunk_size`.
    Returns a list of chunk strings.
    """
    return [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]


def map_singapore_to_pdf(form_data: Dict) -> Dict:
    pdf_model = Singaporepdfmodel()

    form_model = Singaporevisaapplicationform(**form_data)

    raw_passport_details = (
        form_model.passport.passport_details.model_dump()
        if form_model.passport and form_model.passport.passport_details
        else {}
    )
    raw_other_details = (
        form_model.passport.other_details.model_dump()
        if form_model.passport and form_model.passport.other_details
        else {}
    )
    raw_travel_companion_details = (
        form_model.passport.travel_companion_details.model_dump()
        if form_model.passport and form_model.passport.travel_companion_details
        else {}
    )
    travel_companion_details = RootPassportTravelCompanionDetails(
        **raw_travel_companion_details
    )
    other_details = RootPassportOtherDetails(**raw_other_details)
    passport_details = RootPassportPassportDetails(**raw_passport_details)

    raw_residential_address = (
        form_model.residential_address.residential_address_card_v1.model_dump()
        if form_model.residential_address
        and form_model.residential_address.residential_address_card_v1
        else {}
    )
    residential_address = RootResidentialAddressResidentialAddressCardV1(
        **raw_residential_address
    )

    raw_visa_request = (
        form_model.visa_request_information.visa_request.model_dump()
        if form_model.visa_request_information
        and form_model.visa_request_information.visa_request
        else {}
    )
    visa_request = RootVisaRequestInformationVisaRequest(**raw_visa_request)

    raw_work_details = (
        form_model.work_address.work_details.model_dump()
        if form_model.work_address and form_model.work_address.work_details
        else {}
    )
    raw_education_details = (
        form_model.work_address.education_details.model_dump()
        if form_model.work_address and form_model.work_address.education_details
        else {}
    )
    work_details = RootWorkAddressWorkDetails(**raw_work_details)
    education_details = RootWorkAddressEducationDetails(**raw_education_details)

    raw_booked_appointment = (
        form_model.accomodation.booked_appointment.model_dump()
        if form_model.accomodation and form_model.accomodation.booked_appointment
        else {}
    )
    raw_invitation_details = (
        form_model.accomodation.invitation_details.model_dump()
        if form_model.accomodation and form_model.accomodation.invitation_details
        else {}
    )
    booked_appointment = RootAccomodationBookedAppointment(**raw_booked_appointment)
    invitation_details = RootAccomodationInvitationDetails(**raw_invitation_details)

    country_residences = (
        extract_country_residences(additional_details=form_model.additional_details)
        if form_model.additional_details
        else None
    )

    raw_application_antecedent = (
        form_model.declaration.applicant_antecedent.model_dump()
        if form_model.declaration and form_model.declaration.applicant_antecedent
        else {}
    )
    application_antecedent = RootDeclarationApplicantAntecedent(
        **raw_application_antecedent
    )

    pdf_model.passport_passport_details_first_name = passport_details.first_name or ""
    pdf_model.passport_passport_details_surname = passport_details.surname or ""
    pdf_model.passport_passport_details_alias1 = passport_details.alias
    pdf_model.passport_passport_details_alias2 = ""
    if passport_details.date_of_birth:
        dd, mm, yyyy = split_date(passport_details.date_of_birth)
        pdf_model.passport_passport_details_date_of_birth_dd = dd
        pdf_model.passport_passport_details_date_of_birth_mm = mm
        pdf_model.passport_passport_details_date_of_birth_yy = yyyy
    pdf_model.passport_passport_details_gender_mpassport_travel_companion_details_companion_gender_m = (
        "",
    )
    pdf_model.passport_travel_companion_details_companion_gender_f = (
        travel_companion_details.companion_gender == GENDERSGP.FEMALE
    )
    pdf_model.passport_travel_companion_details_companion_gender_m = (
        travel_companion_details.companion_gender == GENDERSGP.MALE
    )
    pdf_model.passport_travel_companion_details_relationship_with_applicant = (
        travel_companion_details.relationship_with_applicant.value
        if travel_companion_details.relationship_with_applicant
        else ""
    )
    if travel_companion_details.companion_name:
        name_parts = split_in_chunks(
            s=travel_companion_details.companion_name, chunk_size=25
        )
        pdf_model.passport_travel_companion_details_companion_name1 = name_parts[0]
        pdf_model.passport_travel_companion_details_companion_name2 = name_parts[1]
    if travel_companion_details.companion_dob:
        c_dd, c_mm, c_yyyy = split_date(travel_companion_details.companion_dob)
        pdf_model.passport_travel_companion_details_companion_dob_dd = c_dd
        pdf_model.passport_travel_companion_details_companion_dob_mm = c_mm
        pdf_model.passport_travel_companion_details_companion_dob_yy = c_yyyy
    pdf_model.passport_travel_companion_details_companion_nationality = (
        travel_companion_details.companion_nationality or ""
    )
    pdf_model.passport_travel_companion_details_companion_passport_num = (
        travel_companion_details.companion_passport_num or ""
    )
    pdf_model.passport_other_details_other_civil_status_single = (
        other_details.civil_status == CIVILMARITALSTATUSSGP.SINGLE
    )
    pdf_model.passport_other_details_other_civil_status_married = (
        other_details.civil_status == CIVILMARITALSTATUSSGP.MARRIED
    )
    pdf_model.passport_other_details_other_civil_status_seperated = (
        other_details.civil_status == CIVILMARITALSTATUSSGP.SEPERATED
    )
    pdf_model.passport_other_details_other_civil_status_divorced = (
        other_details.civil_status == CIVILMARITALSTATUSSGP.DIVORCED
    )
    pdf_model.passport_other_details_other_civil_status_widowed = (
        other_details.civil_status == CIVILMARITALSTATUSSGP.WIDOWED
    )
    pdf_model.passport_other_details_other_civil_status_cohabitated = (
        other_details.civil_status == CIVILMARITALSTATUSSGP.COHABITED
    )
    pdf_model.passport_other_details_other_civil_status_customary = (
        other_details.civil_status == CIVILMARITALSTATUSSGP.CUSTOMARY
    )
    pdf_model.passport_other_details_spouse_nationality_singapore = (
        other_details.spouse_nationality == SPOUSENATIONALITY.SINGAPORE_CITIZEN
    )
    pdf_model.passport_other_details_spouse_nationality_singapore_perm_res = (
        other_details.spouse_nationality
        == SPOUSENATIONALITY.SINGAPORE_PERMANENT_RESIDENT
    )
    pdf_model.passport_other_details_spouse_others_nationality_oth = (
        other_details.spouse_nationality == SPOUSENATIONALITY.OTHERS
    )
    pdf_model.passport_other_details_spouse_others_nationality_oth_txt = (
        other_details.spouse_others_nationality or ""
    )
    if other_details.spouse_nationality == SPOUSENATIONALITY.SINGAPORE_CITIZEN:
        pdf_model.passport_other_details_nric_num1 = other_details.nric_num or ""
    if (
        other_details.spouse_nationality
        == SPOUSENATIONALITY.SINGAPORE_PERMANENT_RESIDENT
    ):
        pdf_model.passport_other_details_nric_num2 = other_details.nric_num or ""
    pdf_model.residential_address_residential_address_card_v1_country = (
        passport_details.country_of_birth.value
        if passport_details.country_of_birth
        else ""
    )
    pdf_model.residential_address_residential_address_card_v1_state = ""
    pdf_model.passport_passport_details_race = ""
    pdf_model.passport_passport_details_nationality = ""
    pdf_model.passport_passport_details_type_of_passport_international = ""
    pdf_model.passport_passport_details_type_of_passport_service = ""
    pdf_model.passport_passport_details_type_of_passport_oth = ""
    pdf_model.passport_passport_details_type_of_passport_diplomatic = ""
    pdf_model.passport_passport_details_type_of_passport_doi = ""
    pdf_model.passport_passport_details_type_of_passport_official = ""
    pdf_model.passport_passport_details_type_of_passport_id_certificate = ""
    pdf_model.field_1passport_passport_details_type_of_passport_oth_txt = ""
    pdf_model.passport_passport_details_passport_number = ""
    pdf_model.passport_passport_details_date_of_issue_dd = ""
    pdf_model.passport_passport_details_date_of_issue_mm = ""
    pdf_model.passport_passport_details_date_of_issue_yy = ""
    pdf_model.passport_passport_details_date_of_expiry_dd = ""
    pdf_model.passport_passport_details_date_of_expiry_mm = ""
    pdf_model.passport_passport_details_date_of_expiry_yy = ""
    pdf_model.passport_passport_details_place_of_issue = ""
    pdf_model.passport_passport_details_country = ""
    pdf_model.passport_passport_details_state = ""
    pdf_model.Prefecture_of_Origin = ""
    pdf_model.CountyDistrict_of_Origin = ""
    pdf_model.passport_passport_details_address_line_1 = ""
    pdf_model.visa_request_information_visa_request_email_id = ""
    pdf_model.visa_request_information_visa_request_phone_number = ""
    pdf_model.work_address_work_details_occupation = ""
    pdf_model.work_address_education_details_academic_qualification_na = ""
    pdf_model.work_address_education_details_academic_qualification_primary = ""
    pdf_model.work_address_education_details_academic_qualification_secondary = ""
    pdf_model.work_address_education_details_academic_qualification_preuni = ""
    pdf_model.work_address_education_details_academic_qualification_diploma = ""
    pdf_model.work_address_education_details_academic_qualification_uni = ""
    pdf_model.work_address_education_details_academic_qualification_postgrad = ""
    pdf_model.work_annual_income = ""
    pdf_model.passport_passport_details_religion = ""
    pdf_model.visa_request_information_visa_request_arrival_date_dd = ""
    pdf_model.visa_request_information_visa_request_arrival_date_mm = ""
    pdf_model.visa_request_information_visa_request_arrival_date_yy = ""
    pdf_model.visa_request_information_visa_request_visa_type_single = ""
    pdf_model.visa_request_information_visa_request_visa_type_double = ""
    pdf_model.visa_request_information_visa_request_visa_type_triple = ""
    pdf_model.visa_request_information_visa_request_visa_type_multi = ""
    pdf_model.visa_request_information_visa_request_visa_type_social = ""
    pdf_model.visa_request_information_visa_request_visa_type_business = ""
    pdf_model.visa_request_information_visa_request_purpose_of_stay = ""
    pdf_model.visa_request_information_visa_request_length_of_stay_sgp_30less = ""
    pdf_model.visa_request_information_visa_request_length_of_stay_sgp_30more = ""
    pdf_model.visa_request_information_visa_request_reason_for_length_of_stay_l1 = ""
    pdf_model.visa_request_information_visa_request_reason_for_length_of_stay_l2 = ""
    pdf_model.accomodation_invitation_details_relationship_kin = ""
    pdf_model.accomodation_invitation_details_relationship_relative = ""
    pdf_model.accomodation_invitation_details_relationship_friend = ""
    pdf_model.accomodation_invitation_details_relationshiphotel = ""
    pdf_model.accomodation_invitation_details_relationship_oth = ""
    pdf_model.accomodation_invitation_details_relationship_oth_txt = ""
    pdf_model.BlockHouse_No = ""
    pdf_model.Floor_No = ""
    pdf_model.Unit_No = ""
    pdf_model.Postal_Code = ""
    pdf_model.Street_Name = ""
    pdf_model.Contact_No = ""
    pdf_model.Building_Name = ""
    pdf_model.additional_details_reside_in_other_country1 = ""
    pdf_model.additional_details_country_residence_address1 = ""
    pdf_model.additional_details_country_residence_stay_period_from1 = ""
    pdf_model.additional_details_country_residence_stay_period_to1 = ""
    pdf_model.additional_details_reside_in_other_country_yes = ""
    pdf_model.additional_details_reside_in_other_country_no = ""
    pdf_model.additional_details_reside_in_other_country2 = ""
    pdf_model.additional_details_country_residence_address2 = ""
    pdf_model.additional_details_country_residence_stay_period_from2 = ""
    pdf_model.additional_details_country_residence_stay_period_to2 = ""
    pdf_model.additional_details_reside_in_other_country3 = ""
    pdf_model.additional_details_country_residence_address3 = ""
    pdf_model.additional_details_country_residence_stay_period_from3 = ""
    pdf_model.additional_details_country_residence_stay_period_to3 = ""
    pdf_model.additional_details_reside_in_other_country4 = ""
    pdf_model.additional_details_country_residence_address4 = ""
    pdf_model.additional_details_country_residence_stay_period_from4 = ""
    pdf_model.additional_details_country_residence_stay_period_to4 = ""
    pdf_model.accomodation_booked_appointment_accommodation_name_l1 = ""
    pdf_model.accomodation_booked_appointment_accommodation_name = ""
    pdf_model.accomodation_invitation_details_relationship = ""
    pdf_model.accomodation_booked_appointment_accommodation_phone = ""
    pdf_model.accomodation_booked_appointment_accommodation_email = ""
    pdf_model.declaration_applicant_antecedent_furnish_details1 = ""
    pdf_model.declaration_applicant_antecedent_furnish_details2 = ""
    pdf_model.declaration_applicant_antecedent_furnish_details3 = ""
    pdf_model.Date = ""
    pdf_model.undefined_21 = ""
    pdf_model.declaration_applicant_antecedent_denied_entry_yes = ""
    pdf_model.declaration_applicant_antecedent_convincted_yes = ""
    pdf_model.declaration_applicant_antecedent_prohibited_entry_yes = ""
    pdf_model.declaration_applicant_antecedent_different_passport_yes = ""
    pdf_model.declaration_applicant_antecedent_denied_entry_no = ""
    pdf_model.declaration_applicant_antecedent_convincted_no = ""
    pdf_model.declaration_applicant_antecedent_prohibited_entry_no = ""
    pdf_model.declaration_applicant_antecedent_different_passport_no = ""

    return pdf_model.model_dump(by_alias=True)
