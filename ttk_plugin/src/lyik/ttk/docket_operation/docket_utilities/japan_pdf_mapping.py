from lyik.ttk.models.forms.japanvisaapplicationform import (
    Japanvisaapplicationform,
    RootPassportPassportDetails,
    RootPassportOtherDetails,
    RootResidentialAddressResidentialAddressCardV1,
    RootResidentialAddressResidentialAddressCardV2,
    RootVisaRequestInformationVisaRequest,
    RootWorkAddressWorkDetails,
    RootDeclarationApplicantAntecedent,
    RootTicketingFlightTickets,
    RootAdditionalDetailsNationalId,
    RootAccomodationBookedAppointment,
    RootAccomodationGuarantorDetails,
    RootAccomodationInvitationDetails,
    RootPreviousVisasPreviousVisasDetails,
    SAMEASPASSADDR,
    GENDERSGP,
    CIVILMARITALSTATUSJPN,
    PASSPORTTYPEJPN,
    ACCOMMODATIONARRANGEMENT,
    RELATIONSHIPJPN,
    SAMEASGUARANTORJPN,
    OPTION,
    VISATYPE,
)
from lyik.ttk.models.pdf.Japanpdfmodel import Japanpdfmodel

from typing import Tuple, Dict, List


def map_japan_pdf(form_data: Dict) -> Dict:
    pdf_model = Japanpdfmodel()

    form_model = Japanvisaapplicationform(**form_data)

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

    raw_additional_details = (
        form_model.additional_details.national_id.model_dump()
        if form_model.additional_details and form_model.additional_details.national_id
        else {}
    )
    national_id = RootAdditionalDetailsNationalId(**raw_additional_details)

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

    accomodation = form_model.accomodation

    raw_booked_accomodation = (
        accomodation.booked_appointment.model_dump()
        if accomodation and accomodation.booked_appointment
        else {}
    )
    booked_accomodation = RootAccomodationBookedAppointment(**raw_booked_accomodation)

    raw_guarantor_details = (
        accomodation.guarantor_details.model_dump()
        if accomodation and accomodation.guarantor_details
        else {}
    )
    guarantor_details = RootAccomodationGuarantorDetails(**raw_guarantor_details)

    raw_invitation_Details = (
        accomodation.invitation_details.model_dump()
        if accomodation and accomodation.invitation_details
        else {}
    )
    invitation_details = RootAccomodationInvitationDetails(**raw_invitation_Details)

    raw_previous_visas = (
        form_model.previous_visas.previous_visas_details.model_dump()
        if form_model.previous_visas
        and form_model.previous_visas.previous_visas_details
        else {}
    )
    previous_visa = RootPreviousVisasPreviousVisasDetails(**raw_previous_visas)

    pdf_model.passport_passport_details_surname = passport_details.surname or ""
    pdf_model.passport_passport_details_first_name = passport_details.first_name or ""
    pdf_model.passport_passport_details_surname_at_birth = (
        passport_details.surname_at_birth or ""
    )

    pdf_model.passport_passport_details_date_of_birth = (
        passport_details.date_of_birth.strftime("%d/%m/%Y")
        if passport_details.date_of_birth
        else ""
    )

    pdf_model.passport_passport_details_place_of_birth = (
        passport_details.place_of_birth or ""
    )

    pdf_model.passport_passport_details_gender_male = (
        passport_details.gender == GENDERSGP.MALE
    )
    pdf_model.passport_passport_details_gender_female = (
        passport_details.gender == GENDERSGP.FEMALE
    )

    pdf_model.passport_other_details_other_civil_status_single = (
        other_details.civil_status == CIVILMARITALSTATUSJPN.SINGLE
    )
    pdf_model.passport_other_details_other_civil_status_married = (
        other_details.civil_status == CIVILMARITALSTATUSJPN.MARRIED
    )
    pdf_model.passport_other_details_other_civil_status_widowed = (
        other_details.civil_status == CIVILMARITALSTATUSJPN.WIDOWED
    )
    pdf_model.passport_other_details_other_civil_status_divorced = (
        other_details.civil_status == CIVILMARITALSTATUSJPN.DIVORCED
    )

    pdf_model.passport_passport_details_nationality = passport_details.nationality or ""
    pdf_model.passport_other_details_other_nationality = (
        other_details.other_nationality or ""
    )

    pdf_model.additional_details_national_id_aadhaar_number = (
        national_id.aadhaar_number or ""
    )

    pdf_model.passport_passport_details_type_of_passport_diplomatic = (
        passport_details.type_of_passport == PASSPORTTYPEJPN.DIPLOMATIC
    )
    pdf_model.passport_passport_details_type_of_passport_official = (
        passport_details.type_of_passport == PASSPORTTYPEJPN.OFFICIAL
    )
    pdf_model.passport_passport_details_type_of_passport_ordinary = (
        passport_details.type_of_passport == PASSPORTTYPEJPN.ORDINARY
    )
    pdf_model.passport_passport_details_type_of_passport_other = (
        passport_details.type_of_passport == PASSPORTTYPEJPN.OTHER
    )

    pdf_model.passport_passport_details_passport_number = (
        passport_details.passport_number or ""
    )

    pdf_model.passport_passport_details_place_of_issue = (
        passport_details.place_of_issue or ""
    )
    pdf_model.passport_passport_details_date_of_issue = (
        passport_details.date_of_issue.strftime("%d/%m/%Y")
        if passport_details.date_of_issue
        else ""
    )

    pdf_model.passport_passport_details_issued_by = passport_details.issued_by or ""
    pdf_model.passport_passport_details_date_of_expiry = (
        passport_details.date_of_expiry.strftime("%d/%m/%Y")
        if passport_details.date_of_expiry
        else ""
    )

    pdf_model.work_address_work_details_certificate_of_eligibility = (
        work_details.certificate_of_eligibility or ""
    )

    pdf_model.visa_request_information_visa_request_purpose_of_stay = (
        visa_request.purpose_of_stay or ""
    )

    pdf_model.visa_request_information_visa_request_length_of_stay = (
        str(visa_request.length_of_stay) if visa_request.length_of_stay else ""
    )
    pdf_model.ticketing_flight_tickets_arrival_date = (
        ticketing.arrival_date.strftime("%d/%m/%Y") if ticketing.arrival_date else ""
    )

    pdf_model.ticketing_flight_tickets_port_of_entry = ticketing.port_of_entry or ""
    pdf_model.ticketing_flight_tickets_airline = ticketing.airline or ""

    if (
        form_model.accomodation.accommodation_choice.accommodation_option
        == ACCOMMODATIONARRANGEMENT.WITH_FAMILY
    ):
        pdf_model.accomodation_booked_appointment_accommodation_name = (
            invitation_details.guarantor_inviter_name or ""
        )
        pdf_model.accomodation_booked_appointment_mobile_number = ""
        pdf_model.accomodation_booked_appointment_accommodation_address = (
            invitation_details.guarantor_inviter_address or ""
        )
    else:
        pdf_model.accomodation_booked_appointment_accommodation_name = (
            booked_accomodation.accommodation_name or ""
        )
        pdf_model.accomodation_booked_appointment_mobile_number = (
            booked_accomodation.accommodation_phone or ""
        )
        pdf_model.accomodation_booked_appointment_accommodation_address = (
            booked_accomodation.accommodation_address or ""
        )

    entry_date = (
        previous_visa.date_of_entry.strftime("%d/%m/%Y")
        if previous_visa.date_of_entry
        else ""
    )
    duration = previous_visa.duration or ""
    pdf_model.Dates_and_duration_of_previous_stays_in_Japan = (
        f"{entry_date} {duration}".strip()
    )

    if (
        form_model.residential_address
        and form_model.residential_address.same_as_passport_address
        == SAMEASPASSADDR.SAME_AS_PASS_ADDR
    ):
        pdf_model.passport_passport_details_address_line_1 = (
            residential_address_v2.address_line_1 or ""
        )
        pdf_model.Te_I = ""
        pdf_model.visa_request_information_visa_request_phone_number = ""
        pdf_model.visa_request_information_visa_request_email_id = ""
    else:
        pdf_model.passport_passport_details_address_line_1 = (
            residential_address_v1.address_line_1 or ""
        )
        pdf_model.Te_I = ""
        pdf_model.visa_request_information_visa_request_phone_number = ""
        pdf_model.visa_request_information_visa_request_email_id = ""

    pdf_model.work_address_work_details_occupation = work_details.occupation or ""
    pdf_model.work_address_work_details_employer_name = work_details.employer_name or ""
    pdf_model.work_address_work_details_work_phone = work_details.work_phone or ""
    pdf_model.work_address_work_details_work_address = work_details.work_address or ""

    pdf_model.passport_other_details_partner_parent_occupation = (
        other_details.partner_parent_occupation or ""
    )

    pdf_model.accomodation_guarantor_details_guarantor_inviter_name = (
        guarantor_details.guarantor_inviter_name or ""
    )
    pdf_model.Tel_3 = ""
    pdf_model.accomodation_guarantor_details_guarantor_inviter_address = (
        guarantor_details.guarantor_inviter_address or ""
    )
    pdf_model.accomodation_guarantor_details_guarantor_inviter_dob = (
        guarantor_details.guarantor_inviter_dob.strftime("%d/%m/%Y")
        if guarantor_details.guarantor_inviter_dob
        else ""
    )
    if (
        guarantor_details.guarantor_inviter_relationship
        and guarantor_details.guarantor_inviter_relationship != RELATIONSHIPJPN.OTHERS
    ):
        pdf_model.accomodation_guarantor_details_guarantor_inviter_relationship = (
            guarantor_details.guarantor_inviter_relationship.value
        )
    else:
        pdf_model.accomodation_guarantor_details_guarantor_inviter_relationship = (
            guarantor_details.guarantor_inviter_other_relationship or ""
        )
    pdf_model.accomodation_guarantor_details_guarantor_inviter_occupation = (
        guarantor_details.guarantor_inviter_occupation or ""
    )
    pdf_model.accomodation_guarantor_details_guarantor_inviter_nationality = (
        guarantor_details.guarantor_inviter_nationality or ""
    )
    pdf_model.accomodation_guarantor_details_guarantor_inviter_immigration_stat = (
        guarantor_details.guarantor_inviter_immigration_stat or ""
    )
    pdf_model.accomodation_guarantor_details_guarantor_inviter_gender_male = (
        guarantor_details.guarantor_inviter_gender == GENDERSGP.MALE
    )
    pdf_model.accomodation_guarantor_details_guarantor_inviter_gender_female = (
        guarantor_details.guarantor_inviter_gender == GENDERSGP.FEMALE
    )

    if (
        accomodation
        and accomodation.inviter_same_as_guarantor
        == SAMEASGUARANTORJPN.SAME_AS_GUARANTOR_JPN
    ):
        pdf_model.accomodation_invitation_details_inviter_name = "same as above"
        pdf_model.Tel_4 = ""
        pdf_model.accomodation_invitation_details_guarantor_inviter_dob = (
            "same as above"
        )
        pdf_model.accomodation_invitation_details_guarantor_inviter_gender_male = (
            guarantor_details.guarantor_inviter_gender == GENDERSGP.MALE
        )
        pdf_model.accomodation_invitation_details_guarantor_inviter_gender_female = (
            guarantor_details.guarantor_inviter_gender == GENDERSGP.FEMALE
        )
        pdf_model.accomodation_invitation_details_relationship = "same as above"
        pdf_model.accomodation_invitation_details_guarantor_inviter_occupation = (
            "same as above"
        )
        pdf_model.accomodation_invitation_details_guarantor_inviter_nationality = (
            "same as above"
        )
        pdf_model.accomodation_invitation_details_guarantor_inviter_immigration_stat = (
            "same as above"
        )
    else:
        pdf_model.accomodation_invitation_details_inviter_name = (
            invitation_details.guarantor_inviter_name or ""
        )
        pdf_model.Tel_4 = ""
        pdf_model.accomodation_invitation_details_guarantor_inviter_dob = (
            invitation_details.guarantor_inviter_dob.strftime("%d/%m/%Y")
            if invitation_details.guarantor_inviter_dob
            else ""
        )
        pdf_model.accomodation_invitation_details_guarantor_inviter_gender_male = (
            invitation_details.guarantor_inviter_gender == GENDERSGP.MALE
        )
        pdf_model.accomodation_invitation_details_guarantor_inviter_gender_female = (
            invitation_details.guarantor_inviter_gender == GENDERSGP.FEMALE
        )
        if (
            invitation_details.guarantor_inviter_relationship
            and invitation_details.guarantor_inviter_relationship
            != RELATIONSHIPJPN.OTHERS
        ):
            pdf_model.accomodation_invitation_details_relationship = (
                invitation_details.guarantor_inviter_relationship.value
            )
        else:
            pdf_model.accomodation_invitation_details_relationship = (
                invitation_details.guarantor_inviter_other_relationship or ""
            )
        pdf_model.accomodation_invitation_details_guarantor_inviter_occupation = (
            invitation_details.guarantor_inviter_occupation or ""
        )
        pdf_model.accomodation_invitation_details_guarantor_inviter_nationality = (
            invitation_details.guarantor_inviter_nationality or ""
        )
        pdf_model.accomodation_invitation_details_guarantor_inviter_immigration_stat = (
            invitation_details.guarantor_inviter_immigration_stat or ""
        )

    pdf_model.Note_Rem_arksSpec_i_a_I_circumstances_if_any = ""

    pdf_model.declaration_applicant_antecedent_crime_conviction_yes = (
        application_antecedent.crime_conviction == OPTION.YES
    )
    pdf_model.declaration_applicant_antecedent_crime_conviction_no = (
        application_antecedent.crime_conviction == OPTION.NO
    )
    pdf_model.declaration_applicant_antecedent_imprisonment_yes = (
        application_antecedent.imprisonment == OPTION.YES
    )
    pdf_model.declaration_applicant_antecedent_imprisonment_no = (
        application_antecedent.imprisonment == OPTION.NO
    )
    pdf_model.declaration_applicant_antecedent_deported_japan_yes = (
        application_antecedent.deported_japan == OPTION.YES
    )
    pdf_model.declaration_applicant_antecedent_deported_japan_no = (
        application_antecedent.deported_japan == OPTION.NO
    )
    pdf_model.declaration_applicant_antecedent_drug_offence_yes = (
        application_antecedent.drug_offence == OPTION.YES
    )
    pdf_model.declaration_applicant_antecedent_drug_offence_no = (
        application_antecedent.drug_offence == OPTION.NO
    )
    pdf_model.declaration_applicant_antecedent_prostitution_yes = (
        application_antecedent.prostitution == OPTION.YES
    )
    pdf_model.declaration_applicant_antecedent_prostitution_no = (
        application_antecedent.prostitution == OPTION.NO
    )
    pdf_model.declaration_applicant_antecedent_trafficking_yes = (
        application_antecedent.trafficking == OPTION.YES
    )
    pdf_model.declaration_applicant_antecedent_trafficking_no = (
        application_antecedent.trafficking == OPTION.NO
    )
    pdf_model.declaration_applicant_antecedent_furnish_details = (
        application_antecedent.furnish_details or ""
    )

    pdf_model.Text6 = ""

    return pdf_model.model_dump(by_alias=True)
