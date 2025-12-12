from lyik.ttk.models.forms.mexicovisaapplicationform import (
    Mexicovisaapplicationform,
    RootPassportPassportDetails,
    RootPassportOtherDetails,
    RootResidentialAddressResidentialAddressCardV1,
    RootResidentialAddressResidentialAddressCardV2,
    RootVisaRequestInformationVisaRequest,
    RootWorkAddressWorkDetails,
    RootDeclarationApplicantAntecedent,
    RootTicketingFlightTickets,
    SAMEASPASSADDR,
    GENDERMEX,
    CIVILMARITALSTATUSMEX,
    OPTION,
    LENGTHOFSTAYMEXICO,
    VISATYPE,
    PASSPORTTYPEMEX,
)
from lyik.ttk.utils.utils import ISO3ToCountryModel
from lyik.ttk.models.pdf.Mexicopdfmodel import Mexicopdfmodel
from datetime import date

from typing import Tuple, Dict, List


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


def map_mexico_pdf(form_data: Dict) -> Dict:
    pdf_model = Mexicopdfmodel()

    form_model = Mexicovisaapplicationform(**form_data)

    raw_passport_details = (
        form_model.passport.passport_details.model_dump()
        if form_model.passport and form_model.passport.passport_details
        else {}
    )
    passport_details = RootPassportPassportDetails(**raw_passport_details)
    raw_other_details = (
        form_model.passport.other_details.model_dump()
        if form_model.passport and form_model.passport.other_details
        else {}
    )
    other_details = RootPassportOtherDetails(**raw_other_details)

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
    work_details = RootWorkAddressWorkDetails(**raw_work_details)

    raw_application_antecedent = (
        form_model.declaration.applicant_antecedent.model_dump()
        if form_model.declaration and form_model.declaration.applicant_antecedent
        else {}
    )
    application_antecedent = RootDeclarationApplicantAntecedent(
        **raw_application_antecedent
    )

    raw_ticketing = (
        form_model.ticketing.flight_tickets.model_dump()
        if form_model.ticketing and form_model.ticketing.flight_tickets
        else {}
    )
    ticketing = RootTicketingFlightTickets(**raw_ticketing)

    pdf_model.passport_passport_details_first_name = passport_details.first_name or ""
    pdf_model.passport_passport_details_surname = passport_details.surname or ""

    pdf_model.passport_passport_details_gender_male = (
        passport_details.gender == GENDERMEX.MALE
    )
    pdf_model.passport_passport_details_gender_female = (
        passport_details.gender == GENDERMEX.FEMALE
    )
    pdf_model.passport_passport_details_gender_no_specific = (
        passport_details.gender == GENDERMEX.NO_SPEC
    )

    pdf_model.Text3 = ""
    if passport_details.date_of_birth:
        dd, mm, yyyy = split_date(passport_details.date_of_birth)
        pdf_model.passport_passport_details_date_of_birth_dd = dd
        pdf_model.passport_passport_details_date_of_birth_mm = mm
        pdf_model.passport_passport_details_date_of_birth_yyyy = yyyy

    pdf_model.passport_passport_details_age = passport_details.age or ""

    pdf_model.passport_passport_details_country_of_birth = (
        ISO3ToCountryModel(iso3_input=passport_details.country_of_birth).country_name()
        if passport_details.country_of_birth
        else ""
    )
    pdf_model.passport_passport_details_nationality = passport_details.nationality or ""

    pdf_model.passport_travel_companion_details_companion_passport_num = (
        passport_details.passport_number or ""
    )

    pdf_model.passport_passport_details_country_of_issue = (
        passport_details.place_of_issue or ""
    )
    pdf_model.passport_passport_details_date_of_issue = (
        passport_details.date_of_issue.strftime("%d-%m-%Y")
        if passport_details.date_of_issue
        else ""
    )

    if passport_details.date_of_expiry:
        doe_dd, doe_mm, doe_yyyy = split_date(passport_details.date_of_expiry)
        pdf_model.passport_passport_details_date_of_expiry_dd = doe_dd
        pdf_model.passport_passport_details_date_of_expiry_mm = doe_mm
        pdf_model.passport_passport_details_date_of_expiry_yyyy = doe_yyyy

    pdf_model.passport_other_details_other_civil_status_single = (
        other_details.civil_status == CIVILMARITALSTATUSMEX.SINGLE
    )
    pdf_model.passport_other_details_other_civil_status_married = (
        other_details.civil_status == CIVILMARITALSTATUSMEX.MARRIED
    )
    pdf_model.passport_other_details_other_civil_status_common_law = (
        other_details.civil_status == CIVILMARITALSTATUSMEX.COMMON_LAW
    )

    if (
        form_model.residential_address
        and form_model.residential_address.same_as_passport_address
        == SAMEASPASSADDR.SAME_AS_PASS_ADDR
    ):
        pdf_model.residential_address_residential_address_card_v1_type_of_proof = (
            residential_address_v2.address_line_1 or ""
        )
    else:
        pdf_model.residential_address_residential_address_card_v1_type_of_proof = (
            residential_address_v1.address_line_1 or ""
        )

    pdf_model.visa_request_information_visa_request_phone_number = (
        visa_request.phone_number or ""
    )
    pdf_model.visa_request_information_visa_request_email_id = (
        visa_request.email_id or ""
    )

    pdf_model.work_address_work_details_occupation = work_details.occupation or ""
    pdf_model.work_address_work_details_employer_name = work_details.employer_name or ""

    pdf_model.passport_passport_details_country = passport_details.country or ""

    pdf_model.passport_other_details_legal_migratory_status_yes = (
        other_details.legal_migratory_status == OPTION.YES
    )
    pdf_model.passport_other_details_legal_migratory_status_no = (
        other_details.legal_migratory_status == OPTION.NO
    )

    pdf_model.declaration_applicant_antecedent_convincted_yes = (
        application_antecedent.convincted == OPTION.YES
    )
    pdf_model.declaration_applicant_antecedent_convincted_no = (
        application_antecedent.convincted == OPTION.NO
    )
    pdf_model.declaration_applicant_antecedent_furnish_details = (
        application_antecedent.furnish_details or ""
    )

    if ticketing.arrival_date:
        t_dd, t_mm, t_yyyy = split_date(ticketing.arrival_date)
        pdf_model.ticketing_flight_tickets_arrival_date_dd = t_dd
        pdf_model.ticketing_flight_tickets_arrival_date_mm = t_mm
        pdf_model.ticketing_flight_tickets_arrival_date_yyyy = t_yyyy

    pdf_model.ticketing_flight_tickets_port_of_entry = ticketing.port_of_entry or ""

    pdf_model.visa_request_information_visa_request_length_of_stay_below180 = (
        visa_request.length_of_stay == LENGTHOFSTAYMEXICO.LESS_180
    )
    pdf_model.visa_request_information_visa_request_length_of_stay_above180 = (
        visa_request.length_of_stay == LENGTHOFSTAYMEXICO.BETWEEN_180_4Y
    )
    pdf_model.visa_request_information_visa_request_length_of_stay_definitive = (
        visa_request.length_of_stay == LENGTHOFSTAYMEXICO.DEFINITIVE
    )

    pdf_model.declaration_applicant_antecedent_prohibited_entry_yes = (
        application_antecedent.prohibited_entry == OPTION.YES
    )
    pdf_model.declaration_applicant_antecedent_prohibited_entry_no = (
        application_antecedent.prohibited_entry == OPTION.NO
    )

    pdf_model.declaration_applicant_antecedent_denied_entry_yes = (
        application_antecedent.denied_entry == OPTION.YES
    )
    pdf_model.declaration_applicant_antecedent_denied_entry_no = (
        application_antecedent.denied_entry == OPTION.NO
    )
    pdf_model.declaration_applicant_antecedent_furnish_details_1 = (
        application_antecedent.furnish_details_1 or ""
    )

    pdf_model.visa_request_information_visa_request_purpose_of_stay = (
        visa_request.purpose_of_stay or ""
    )

    pdf_model.visa_request_information_visa_request_visa_type_tourist = (
        visa_request.visa_type == VISATYPE.Tourist
    )
    pdf_model.visa_request_information_visa_request_visa_type_long_term_visitor = False
    pdf_model.visa_request_information_visa_request_visa_type_work = (
        visa_request.visa_type == VISATYPE.Work
    )
    pdf_model.visa_request_information_visa_request_visa_type_conducting_adoption = (
        False
    )
    pdf_model.visa_request_information_visa_request_visa_type_student = (
        visa_request.visa_type == VISATYPE.Student
    )
    pdf_model.visa_request_information_visa_request_visa_type_temp_res = False
    pdf_model.visa_request_information_visa_request_visa_type_permanent = False
    pdf_model.visa_request_information_visa_request_visa_type_diplomatic = False
    pdf_model.visa_request_information_visa_request_visa_type_official = False
    pdf_model.visa_request_information_visa_request_visa_type_service = False

    pdf_model.Check_passport_passport_details_type_of_passport_regular = (
        passport_details.type_of_passport == PASSPORTTYPEMEX.ORDINARY
    )
    pdf_model.Check_passport_passport_details_type_of_passport_regular_passer = False
    pdf_model.Check_passport_passport_details_type_of_passport_regular_special = (
        passport_details.type_of_passport == PASSPORTTYPEMEX.SPECIAL
    )

    pdf_model.Text1 = ""
    pdf_model.Text2 = ""
    pdf_model.Text4 = ""
    pdf_model.Text5 = ""

    return pdf_model.model_dump(by_alias=True)
