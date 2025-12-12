from lyik.ttk.models.forms.egyptvisaapplicationform import (
    Egyptvisaapplicationform,
    RootPassportPassportDetails,
    RootResidentialAddressResidentialAddressCardV1,
    RootResidentialAddressResidentialAddressCardV2,
    RootResidentialAddressPermanentAddressDetails,
    RootVisaRequestInformationVisaRequest,
    RootWorkAddressWorkDetails,
    RootTicketingFlightTickets,
    RootAdditionalDetailsNationalId,
    RootAccomodationBookedAppointment,
    RootAccomodationInvitationDetails,
    SAMEASPASSADDR,
    ACCOMMODATIONARRANGEMENT,
    OPTION,
    VISATYPE,
)
from lyik.ttk.models.pdf.Egyptpdfmodel import Egyptpdfmodel

from typing import Tuple, Dict, List


def map_egypt_pdf(form_data: Dict) -> Dict:
    pdf_model = Egyptpdfmodel()

    form_model = Egyptvisaapplicationform(**form_data)

    raw_passport_details = (
        form_model.passport.passport_details.model_dump()
        if form_model.passport and form_model.passport.passport_details
        else {}
    )
    passport_details = RootPassportPassportDetails(**raw_passport_details)

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

    raw_invitation_Details = (
        accomodation.invitation_details.model_dump()
        if accomodation and accomodation.invitation_details
        else {}
    )
    invitation_details = RootAccomodationInvitationDetails(**raw_invitation_Details)

    pdf_model.passport_passport_details_surname = passport_details.surname or ""
    pdf_model.passport_passport_details_first_name = passport_details.first_name or ""
    pdf_model.Text3 = ""

    pdf_model.passport_passport_details_date_of_birth = (
        passport_details.date_of_birth.strftime("%d-%m-%Y")
        if passport_details.date_of_birth
        else ""
    )
    pdf_model.passport_passport_details_place_of_birth = (
        passport_details.place_of_birth or ""
    )
    pdf_model.passport_passport_details_gender = passport_details.gender or ""

    pdf_model.passport_passport_details_nationality = passport_details.nationality or ""
    pdf_model.passport_passport_details_nationality_of_origin = (
        passport_details.nationality_of_origin or ""
    )
    pdf_model.work_address_work_details_occupation = work_details.occupation or ""
    pdf_model.Text10 = ""

    pdf_model.passport_passport_details_passport_number = (
        passport_details.passport_number or ""
    )
    pdf_model.passport_passport_details_place_of_issue = (
        passport_details.place_of_issue or ""
    )
    pdf_model.passport_passport_details_date_of_expiry = (
        passport_details.date_of_expiry.strftime("%d-%m-%Y")
        if passport_details.date_of_expiry
        else ""
    )
    pdf_model.passport_passport_details_date_of_issue = (
        passport_details.date_of_issue.strftime("%d-%m-%Y")
        if passport_details.date_of_issue
        else ""
    )

    pdf_model.residential_address_residential_address_card_v1_address_line_1_present_address = (
        ""
    )
    pdf_model.residential_address_residential_address_card_v1_address_line_1_permanent_address = (
        ""
    )
    pdf_model.visa_request_information_visa_request_phone_number_permanent_address = ""
    pdf_model.visa_request_information_visa_request_phone_number_present_address = ""
    pdf_model.visa_request_information_visa_request_purpose_of_stay = ""
    pdf_model.ticketing_flight_tickets_arrival_date = ""
    pdf_model.visa_request_information_visa_request_length_of_stay = ""
    pdf_model.visa_request_information_visa_request_no_of_entries = ""
    pdf_model.ticketing_flight_tickets_port_of_entry = ""
    pdf_model.Text24 = ""
    pdf_model.accomodation_invitation_details_inviter_name1 = ""
    pdf_model.accomodation_invitation_details_inviter_name2 = ""
    pdf_model.accomodation_invitation_details_inviter_name3 = ""
    pdf_model.accomodation_invitation_details_inviter_name4 = ""
    pdf_model.accomodation_invitation_details_inviter_address1 = ""
    pdf_model.accomodation_invitation_details_inviter_address2 = ""
    pdf_model.accomodation_invitation_details_inviter_address3 = ""
    pdf_model.accomodation_invitation_details_inviter_address4 = ""
    pdf_model.Text33 = ""
    pdf_model.Text34 = ""
    pdf_model.passport_travel_companion_details_companion_name1 = ""
    pdf_model.passport_travel_companion_details_relationship_with_applicant1 = ""
    pdf_model.passport_travel_companion_details_companion_dob1 = ""
    pdf_model.Text50 = ""
    pdf_model.Text55 = ""
    pdf_model.previous_visas_visit_details_previous_visit_date1 = ""
    pdf_model.previous_visas_visit_details_previous_visit_purpose1 = ""
    pdf_model.previous_visas_visit_details_previous_visit_address1 = ""
    pdf_model.Text43 = ""
    pdf_model.Text44 = ""
    pdf_model.Text45 = ""
    pdf_model.Text46 = ""
    pdf_model.Text47 = ""
    pdf_model.Text48 = ""
    pdf_model.passport_travel_companion_details_companion_name2 = ""
    pdf_model.passport_travel_companion_details_companion_name3 = ""
    pdf_model.passport_travel_companion_details_companion_name4 = ""
    pdf_model.passport_travel_companion_details_companion_name5 = ""
    pdf_model.passport_travel_companion_details_relationship_with_applicant2 = ""
    pdf_model.passport_travel_companion_details_relationship_with_applicant3 = ""
    pdf_model.passport_travel_companion_details_relationship_with_applicant4 = ""
    pdf_model.passport_travel_companion_details_relationship_with_applicant5 = ""
    pdf_model.passport_travel_companion_details_companion_dob2 = ""
    pdf_model.passport_travel_companion_details_companion_dob3 = ""
    pdf_model.passport_travel_companion_details_companion_dob4 = ""
    pdf_model.passport_travel_companion_details_companion_dob5 = ""
    pdf_model.previous_visas_visit_details_previous_visit_address2 = ""
    pdf_model.previous_visas_visit_details_previous_visit_address3 = ""
    pdf_model.previous_visas_visit_details_previous_visit_address4 = ""
    pdf_model.previous_visas_visit_details_previous_visit_address5 = ""
    pdf_model.previous_visas_visit_details_previous_visit_date2 = ""
    pdf_model.previous_visas_visit_details_previous_visit_date3 = ""
    pdf_model.previous_visas_visit_details_previous_visit_date4 = ""
    pdf_model.previous_visas_visit_details_previous_visit_date5 = ""
    pdf_model.previous_visas_visit_details_previous_visit_purpose2 = ""
    pdf_model.previous_visas_visit_details_previous_visit_purpose3 = ""
    pdf_model.previous_visas_visit_details_previous_visit_purpose4 = ""
    pdf_model.previous_visas_visit_details_previous_visit_purpose5 = ""
    pdf_model.Text51 = ""
    pdf_model.Text38 = ""
    pdf_model.Text54 = ""
    pdf_model.Text56 = ""
    pdf_model.Text57 = ""
    pdf_model.Text58 = ""
    pdf_model.Text59 = ""
    pdf_model.passport_travel_companion_details_companion_place_of_birth1 = ""
    pdf_model.passport_travel_companion_details_companion_place_of_birth2 = ""
    pdf_model.passport_travel_companion_details_companion_place_of_birth3 = ""
    pdf_model.passport_travel_companion_details_companion_place_of_birth4 = ""
    pdf_model.passport_travel_companion_details_companion_place_of_birth5 = ""
    pdf_model.Text66 = ""
    pdf_model.Text67 = ""
    pdf_model.Text68 = ""
    pdf_model.Text69 = ""
    pdf_model.Text70 = ""
