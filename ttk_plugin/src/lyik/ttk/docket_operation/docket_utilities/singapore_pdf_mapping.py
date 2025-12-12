from lyik.ttk.models.forms.singaporevisaapplicationform import (
    Singaporevisaapplicationform,
    CIVILMARITALSTATUSSGP,
    GENDERSGP,
    OPTION,
    PASSPORTTYPESGP,
    RELATIONSHIP,
    SGPSTAY,
    SPOUSENATIONALITY,
    ACADEMICQUALIFICATIONSGP,
    VISATYPE,
    ACCOMMODATIONARRANGEMENT,
    NUMBEROFENTRIESSGP,
    SAMEASPASSADDR,
    RootPassportPassportDetails,
    RootPassportOtherDetails,
    RootPassportTravelCompanionDetails,
    RootResidentialAddressResidentialAddressCardV1,
    RootResidentialAddressResidentialAddressCardV2,
    RootVisaRequestInformationVisaRequest,
    RootWorkAddressWorkDetails,
    RootWorkAddressEducationDetails,
    RootAccomodationBookedAppointment,
    RootAccomodationInvitationDetails,
    RootAdditionalDetailsResidenceInOtherCountryGroupOthercountryresidenceCountryResidence,
    RootAdditionalDetails,
    RootDeclarationApplicantAntecedent,
)
from lyik.ttk.utils.utils import ISO3ToCountryModel
from lyik.ttk.models.pdf.Singaporepdfmodel import Singaporepdfmodel
from datetime import date, datetime

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

    country_residences: List[
        RootAdditionalDetailsResidenceInOtherCountryGroupOthercountryresidenceCountryResidence
    ] = []
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

    raw_residential_address_v1 = (
        form_model.residential_address.residential_address_card_v1.model_dump()
        if form_model.residential_address
        and form_model.residential_address.residential_address_card_v1
        else {}
    )
    residential_address_v1 = RootResidentialAddressResidentialAddressCardV1(
        **raw_residential_address_v1
    )

    raw_residential_address_v2 = (
        form_model.residential_address.residential_address_card_v2.model_dump()
        if form_model.residential_address
        and form_model.residential_address.residential_address_card_v2
        else {}
    )
    residential_address_v2 = RootResidentialAddressResidentialAddressCardV2(
        **raw_residential_address_v2
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
    pdf_model.passport_passport_details_gender_m = (
        passport_details.gender == GENDERSGP.MALE
    )
    pdf_model.passport_passport_details_gender_f = (
        passport_details.gender == GENDERSGP.FEMALE
    )
    if passport_details.date_of_birth:
        dd, mm, yyyy = split_date(passport_details.date_of_birth)
        pdf_model.passport_passport_details_date_of_birth_dd = dd
        pdf_model.passport_passport_details_date_of_birth_mm = mm
        pdf_model.passport_passport_details_date_of_birth_yy = yyyy
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
        pdf_model.passport_travel_companion_details_companion_name1 = (
            name_parts[0] if len(name_parts) > 0 else ""
        )
        pdf_model.passport_travel_companion_details_companion_name2 = (
            name_parts[1] if len(name_parts) > 1 else ""
        )
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
        ISO3ToCountryModel(iso3_input=passport_details.country_of_birth).country_name()
        if passport_details.country_of_birth
        else ""
    )
    pdf_model.residential_address_residential_address_card_v1_state = (
        passport_details.state_of_birth.value if passport_details.state_of_birth else ""
    )
    pdf_model.passport_passport_details_race = passport_details.race or ""
    pdf_model.passport_passport_details_nationality = passport_details.nationality or ""
    pdf_model.passport_passport_details_type_of_passport_international = (
        passport_details.type_of_passport == PASSPORTTYPESGP.INTERNATIONAL_PASSPORT
    )
    pdf_model.passport_passport_details_type_of_passport_service = (
        passport_details.type_of_passport == PASSPORTTYPESGP.SERVICE_PASSPORT
    )
    pdf_model.passport_passport_details_type_of_passport_diplomatic = (
        passport_details.type_of_passport == PASSPORTTYPESGP.DIPLOMATIC_PASSPORT
    )
    pdf_model.passport_passport_details_type_of_passport_doi = (
        passport_details.type_of_passport == PASSPORTTYPESGP.DOCUMENT_OF_IDENTITY
    )
    pdf_model.passport_passport_details_type_of_passport_official = (
        passport_details.type_of_passport == PASSPORTTYPESGP.OFFICIAL_PASSPORT
    )
    pdf_model.passport_passport_details_type_of_passport_id_certificate = (
        passport_details.type_of_passport == PASSPORTTYPESGP.CERTIFICATE_OF_IDENTITY
    )
    pdf_model.passport_passport_details_type_of_passport_oth = (
        passport_details.type_of_passport == PASSPORTTYPESGP.OTHERS
    )
    pdf_model.field_1passport_passport_details_type_of_passport_oth_txt = ""
    pdf_model.passport_passport_details_passport_number = (
        passport_details.passport_number or ""
    )
    if passport_details.date_of_issue:
        doi_dd, doi_mm, doi_yyyy = split_date(passport_details.date_of_issue)
        pdf_model.passport_passport_details_date_of_issue_dd = doi_dd
        pdf_model.passport_passport_details_date_of_issue_mm = doi_mm
        pdf_model.passport_passport_details_date_of_issue_yy = doi_yyyy
    if passport_details.date_of_expiry:
        doe_dd, doe_mm, doe_yyyy = split_date(passport_details.date_of_expiry)
        pdf_model.passport_passport_details_date_of_expiry_dd = doe_dd
        pdf_model.passport_passport_details_date_of_expiry_mm = doe_mm
        pdf_model.passport_passport_details_date_of_expiry_yy = doe_yyyy
    pdf_model.passport_passport_details_place_of_issue = (
        passport_details.place_of_issue or ""
    )
    if (
        form_model.residential_address
        and form_model.residential_address.same_as_passport_address
        == SAMEASPASSADDR.SAME_AS_PASS_ADDR
    ):
        pdf_model.passport_passport_details_country = (
            residential_address_v2.country or ""
        )
        pdf_model.passport_passport_details_state = residential_address_v2.state or ""
        pdf_model.Prefecture_of_Origin = ""
        pdf_model.CountyDistrict_of_Origin = residential_address_v2.district or ""
        pdf_model.passport_passport_details_address_line_1 = (
            residential_address_v2.address_line_1 or ""
        )
    else:
        pdf_model.passport_passport_details_country = (
            residential_address_v1.country or ""
        )
        pdf_model.passport_passport_details_state = residential_address_v1.state or ""
        pdf_model.Prefecture_of_Origin = ""
        pdf_model.CountyDistrict_of_Origin = residential_address_v1.district or ""
        pdf_model.passport_passport_details_address_line_1 = (
            residential_address_v1.address_line_1 or ""
        )
    pdf_model.visa_request_information_visa_request_email_id = (
        visa_request.email_id or ""
    )
    pdf_model.visa_request_information_visa_request_phone_number = (
        visa_request.phone_number or ""
    )
    pdf_model.work_address_work_details_occupation = work_details.occupation or ""
    pdf_model.work_address_education_details_academic_qualification_na = (
        education_details.academic_qualification
        == ACADEMICQUALIFICATIONSGP.NO_FORMAL_EDUCATION
    )
    pdf_model.work_address_education_details_academic_qualification_primary = (
        education_details.academic_qualification == ACADEMICQUALIFICATIONSGP.PRIMARY
    )
    pdf_model.work_address_education_details_academic_qualification_secondary = (
        education_details.academic_qualification == ACADEMICQUALIFICATIONSGP.SECONDARY
    )
    pdf_model.work_address_education_details_academic_qualification_preuni = (
        education_details.academic_qualification
        == ACADEMICQUALIFICATIONSGP.PRE_UNIVERSITY
    )
    pdf_model.work_address_education_details_academic_qualification_diploma = (
        education_details.academic_qualification == ACADEMICQUALIFICATIONSGP.DIPLOMA
    )
    pdf_model.work_address_education_details_academic_qualification_uni = (
        education_details.academic_qualification == ACADEMICQUALIFICATIONSGP.UNIVERSITY
    )
    pdf_model.work_address_education_details_academic_qualification_postgrad = (
        education_details.academic_qualification
        == ACADEMICQUALIFICATIONSGP.POST_GRADUATE
    )
    pdf_model.work_annual_income = work_details.annual_income or ""
    pdf_model.passport_passport_details_religion = passport_details.religion or ""
    if visa_request.departure_date:
        d_dd, d_mm, d_yyyy = split_date(visa_request.departure_date)
        pdf_model.visa_request_information_visa_request_arrival_date_dd = d_dd
        pdf_model.visa_request_information_visa_request_arrival_date_mm = d_mm
        pdf_model.visa_request_information_visa_request_arrival_date_yy = d_yyyy
    pdf_model.visa_request_information_visa_request_no_of_entries_single = (
        visa_request.no_of_entries == NUMBEROFENTRIESSGP.SINGLE_JOURNEY
    )
    pdf_model.visa_request_information_visa_request_no_of_entries_double = (
        visa_request.no_of_entries == NUMBEROFENTRIESSGP.DOUBLE_JOURNEY
    )
    pdf_model.visa_request_information_visa_request_no_of_entries_triple = (
        visa_request.no_of_entries == NUMBEROFENTRIESSGP.TRIPLE_JOURNEY
    )
    pdf_model.visa_request_information_visa_request_no_of_entries_multi = (
        visa_request.no_of_entries == NUMBEROFENTRIESSGP.MULTIPLE_JOURNEY
    )
    pdf_model.visa_request_information_visa_request_visa_type_social = (
        visa_request.visa_type != VISATYPE.Business
    )
    pdf_model.visa_request_information_visa_request_visa_type_business = (
        visa_request.visa_type == VISATYPE.Business
    )
    pdf_model.visa_request_information_visa_request_purpose_of_stay = (
        visa_request.purpose_of_stay or ""
    )
    pdf_model.visa_request_information_visa_request_visa_type_30_less = (
        visa_request.length_of_stay_sgp == SGPSTAY.LESS_THAN_30_DAYS
    )
    pdf_model.visa_request_information_visa_request_visa_type_30more = (
        visa_request.length_of_stay_sgp == SGPSTAY.MORE_THAN_30_DAYS
    )
    if visa_request.reason_for_length_of_stay:
        reason_parts = split_in_chunks(
            s=visa_request.reason_for_length_of_stay, chunk_size=90
        )
        pdf_model.visa_request_information_visa_request_reason_for_length_of_stay_l1 = (
            reason_parts[0] if len(reason_parts) > 0 else ""
        )

        pdf_model.visa_request_information_visa_request_reason_for_length_of_stay_l2 = (
            reason_parts[1] if len(reason_parts) > 1 else ""
        )
    pdf_model.accomodation_invitation_details_relationship_kin = False
    if (
        form_model.accomodation
        and form_model.accomodation.accommodation_choice
        and form_model.accomodation.accommodation_choice.accommodation_option
        == ACCOMMODATIONARRANGEMENT.WITH_FAMILY
    ):
        pdf_model.accomodation_invitation_details_relationship_relative = (
            invitation_details.relationship != RELATIONSHIP.FRIEND
            and invitation_details.relationship != RELATIONSHIP.OTHERS
            if invitation_details.relationship
            else False
        )
        pdf_model.accomodation_invitation_details_relationship_friend = (
            invitation_details.relationship == RELATIONSHIP.FRIEND
        )
        pdf_model.accomodation_invitation_details_relationship_oth = (
            invitation_details.relationship == RELATIONSHIP.OTHERS
        )
        pdf_model.accomodation_invitation_details_relationship_oth_txt = (
            invitation_details.other_relationship or ""
        )
        pdf_model.BlockHouse_No = invitation_details.block_num or ""
        pdf_model.Floor_No = invitation_details.floor_num or ""
        pdf_model.Unit_No = invitation_details.unit_num or ""
        pdf_model.Postal_Code = invitation_details.postal_code or ""
        pdf_model.Street_Name = invitation_details.street_name or ""
        pdf_model.Contact_No = invitation_details.mobile_number or ""
        pdf_model.Building_Name = invitation_details.building_name or ""
    pdf_model.accomodation_invitation_details_relationshiphotel = (
        form_model.accomodation.accommodation_choice.accommodation_option
        == ACCOMMODATIONARRANGEMENT.BOOKED
        or form_model.accomodation.accommodation_choice.accommodation_option
        == ACCOMMODATIONARRANGEMENT.TTK_ASSITANCE
    )
    if pdf_model.accomodation_invitation_details_relationshiphotel:
        pdf_model.BlockHouse_No = booked_appointment.block_num or ""
        pdf_model.Floor_No = booked_appointment.floor_num or ""
        pdf_model.Unit_No = booked_appointment.unit_num or ""
        pdf_model.Postal_Code = booked_appointment.postal_code or ""
        pdf_model.Street_Name = booked_appointment.street_name or ""
        pdf_model.Contact_No = booked_appointment.accommodation_phone or ""
        pdf_model.Building_Name = booked_appointment.building_name or ""

    pdf_model.additional_details_reside_in_other_country_yes = (
        form_model.additional_details.reside_in_other_country == OPTION.YES
    )
    pdf_model.additional_details_reside_in_other_country_no = (
        form_model.additional_details.reside_in_other_country == OPTION.NO
    )

    country_1 = country_residences[0] if len(country_residences) > 0 else None
    if country_1:
        pdf_model.additional_details_reside_in_other_country1 = (
            ISO3ToCountryModel(iso3_input=country_1.country).country_name()
            if country_1.country
            else ""
        )
        pdf_model.additional_details_country_residence_address1 = (
            country_1.address or ""
        )
        pdf_model.additional_details_country_residence_stay_period_from1 = (
            country_1.stay_period_from.strftime("%d-%m-%Y")
            if country_1.stay_period_from
            else ""
        )
        pdf_model.additional_details_country_residence_stay_period_to1 = (
            country_1.stay_period_to.strftime("%d-%m-%Y")
            if country_1.stay_period_to
            else ""
        )

    country_2 = country_residences[1] if len(country_residences) > 1 else None
    if country_2:
        pdf_model.additional_details_reside_in_other_country2 = (
            ISO3ToCountryModel(iso3_input=country_2.country).country_name()
            if country_2.country
            else ""
        )
        pdf_model.additional_details_country_residence_address2 = (
            country_2.address or ""
        )
        pdf_model.additional_details_country_residence_stay_period_from2 = (
            country_2.stay_period_from.strftime("%d-%m-%Y")
            if country_2.stay_period_from
            else ""
        )
        pdf_model.additional_details_country_residence_stay_period_to2 = (
            country_2.stay_period_to.strftime("%d-%m-%Y")
            if country_2.stay_period_to
            else ""
        )

    country_3 = country_residences[2] if len(country_residences) > 2 else None
    if country_3:
        pdf_model.additional_details_reside_in_other_country3 = (
            ISO3ToCountryModel(iso3_input=country_3.country).country_name()
            if country_3.country
            else ""
        )
        pdf_model.additional_details_country_residence_address3 = (
            country_3.address or ""
        )
        pdf_model.additional_details_country_residence_stay_period_from3 = (
            country_3.stay_period_from.strftime("%d-%m-%Y")
            if country_3.stay_period_from
            else ""
        )
        pdf_model.additional_details_country_residence_stay_period_to3 = (
            country_3.stay_period_to.strftime("%d-%m-%Y")
            if country_3.stay_period_to
            else ""
        )

    country_4 = country_residences[3] if len(country_residences) > 3 else None
    if country_4:
        pdf_model.additional_details_reside_in_other_country4 = (
            ISO3ToCountryModel(iso3_input=country_4.country).country_name()
            if country_4.country
            else ""
        )
        pdf_model.additional_details_country_residence_address4 = (
            country_4.address or ""
        )
        pdf_model.additional_details_country_residence_stay_period_from4 = (
            country_4.stay_period_from.strftime("%d-%m-%Y")
            if country_4.stay_period_from
            else ""
        )
        pdf_model.additional_details_country_residence_stay_period_to4 = (
            country_4.stay_period_to.strftime("%d-%m-%Y")
            if country_4.stay_period_to
            else ""
        )

    if (
        form_model.accomodation.accommodation_choice.accommodation_option
        == ACCOMMODATIONARRANGEMENT.WITH_FAMILY
    ):
        pdf_model.accomodation_booked_appointment_accommodation_name_l1 = (
            invitation_details.inviter_name or ""
        )
        pdf_model.accomodation_booked_appointment_accommodation_name = ""
        pdf_model.accomodation_invitation_details_relationship = (
            invitation_details.relationship.value
            if invitation_details.relationship
            else ""
        )
        pdf_model.accomodation_booked_appointment_accommodation_phone = (
            invitation_details.mobile_number or ""
        )
        pdf_model.accomodation_booked_appointment_accommodation_email = (
            invitation_details.email_id or ""
        )
    else:
        pdf_model.accomodation_booked_appointment_accommodation_name_l1 = (
            booked_appointment.accommodation_name or ""
        )
        pdf_model.accomodation_booked_appointment_accommodation_name = ""
        pdf_model.accomodation_invitation_details_relationship = ""
        pdf_model.accomodation_booked_appointment_accommodation_phone = (
            booked_appointment.accommodation_phone or ""
        )
        pdf_model.accomodation_booked_appointment_accommodation_email = (
            booked_appointment.accommodation_email or ""
        )

    pdf_model.declaration_applicant_antecedent_denied_entry_yes = (
        application_antecedent.denied_entry == OPTION.YES
    )
    pdf_model.declaration_applicant_antecedent_denied_entry_no = (
        application_antecedent.denied_entry == OPTION.NO
    )
    pdf_model.declaration_applicant_antecedent_convincted_yes = (
        application_antecedent.convincted == OPTION.YES
    )
    pdf_model.declaration_applicant_antecedent_convincted_no = (
        application_antecedent.convincted == OPTION.NO
    )
    pdf_model.declaration_applicant_antecedent_prohibited_entry_yes = (
        application_antecedent.prohibited_entry == OPTION.YES
    )
    pdf_model.declaration_applicant_antecedent_prohibited_entry_no = (
        application_antecedent.prohibited_entry == OPTION.NO
    )
    pdf_model.declaration_applicant_antecedent_different_passport_yes = (
        application_antecedent.different_passport == OPTION.YES
    )
    pdf_model.declaration_applicant_antecedent_different_passport_no = (
        application_antecedent.different_passport == OPTION.NO
    )

    if application_antecedent.furnish_details:
        details_parts = split_in_chunks(
            s=application_antecedent.furnish_details, chunk_size=90
        )
        pdf_model.declaration_applicant_antecedent_furnish_details1 = (
            details_parts[0] if len(details_parts) > 0 else ""
        )
        pdf_model.declaration_applicant_antecedent_furnish_details2 = (
            details_parts[1] if len(details_parts) > 1 else ""
        )
        pdf_model.declaration_applicant_antecedent_furnish_details3 = (
            details_parts[2] if len(details_parts) > 2 else ""
        )
    pdf_model.Date = ""
    pdf_model.undefined_21 = ""

    return pdf_model.model_dump(by_alias=True)
