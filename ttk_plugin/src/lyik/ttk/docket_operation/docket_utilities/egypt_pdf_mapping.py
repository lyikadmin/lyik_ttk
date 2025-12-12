from lyik.ttk.models.forms.egyptvisaapplicationform import (
    Egyptvisaapplicationform,
    RootPassport,
    RootPassportPassportDetails,
    RootPassportTravelCompanionDetailsTravelcompaniongroupTravelCompanionCard,
    RootResidentialAddressResidentialAddressCardV1,
    RootResidentialAddressResidentialAddressCardV2,
    RootResidentialAddressPermanentAddressDetails,
    RootVisaRequestInformationVisaRequest,
    RootWorkAddressWorkDetails,
    RootTicketingFlightTickets,
    RootAccomodationInvitationDetails,
    RootPreviousVisas,
    RootPreviousVisasVisitDetailsGroupVisitdetailsVisitDetails,
    SAMEASPASSADDR,
    OPTION,
)
from lyik.ttk.models.pdf.Egyptpdfmodel import Egyptpdfmodel

from typing import Dict, List, Type, Any


def map_egypt_pdf(form_data: Dict) -> Dict:
    pdf_model = Egyptpdfmodel()

    form_model = Egyptvisaapplicationform(**form_data)

    raw_passport_details = (
        form_model.passport.passport_details.model_dump()
        if form_model.passport and form_model.passport.passport_details
        else {}
    )
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

    raw_permanent_address = (
        form_model.residential_address.permanent_address_details.model_dump()
        if form_model.residential_address
        and form_model.residential_address.permanent_address_details
        else {}
    )
    permanent_address = RootResidentialAddressPermanentAddressDetails(
        **raw_permanent_address
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

    raw_invitation_Details = (
        accomodation.invitation_details.model_dump()
        if accomodation and accomodation.invitation_details
        else {}
    )
    invitation_details = RootAccomodationInvitationDetails(**raw_invitation_Details)

    travel_companions = extract_travel_companions(passport=form_model.passport)

    previous_visas = None
    if (
        form_model.previous_visas
        and form_model.previous_visas.previous_visit_egypt == OPTION.YES
    ):
        previous_visas = extract_previous_visas(
            root_previous_data=form_model.previous_visas
        )

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

    if (
        form_model.residential_address
        and form_model.residential_address.same_as_passport_address
        == SAMEASPASSADDR.SAME_AS_PASS_ADDR
    ):
        pdf_model.residential_address_residential_address_card_v1_address_line_1_present_address = (
            residential_address_v2.address_line_1 or ""
        )
    else:
        pdf_model.residential_address_residential_address_card_v1_address_line_1_present_address = (
            residential_address_v1.address_line_1 or ""
        )

    if (
        form_model.residential_address
        and form_model.residential_address.permament_address == OPTION.YES
    ):
        pdf_model.residential_address_residential_address_card_v1_address_line_1_permanent_address = (
            passport_details.address_line_1 or ""
        )
    else:
        pdf_model.residential_address_residential_address_card_v1_address_line_1_permanent_address = (
            permanent_address.address or ""
        )

    pdf_model.visa_request_information_visa_request_phone_number_permanent_address = (
        visa_request.phone_number or ""
    )
    pdf_model.visa_request_information_visa_request_phone_number_present_address = (
        visa_request.phone_number or ""
    )

    pdf_model.visa_request_information_visa_request_purpose_of_stay = (
        visa_request.purpose_of_stay or ""
    )
    pdf_model.ticketing_flight_tickets_arrival_date = (
        ticketing.arrival_date.strftime("%d-%m-%Y") if ticketing.arrival_date else ""
    )
    pdf_model.visa_request_information_visa_request_length_of_stay = (
        str(visa_request.duration_of_stay) if visa_request.duration_of_stay else ""
    )
    pdf_model.visa_request_information_visa_request_no_of_entries = (
        visa_request.no_of_entries.value if visa_request.no_of_entries else ""
    )

    pdf_model.ticketing_flight_tickets_port_of_entry = ticketing.port_of_entry or ""
    pdf_model.Text24 = ""

    pdf_model.accomodation_invitation_details_inviter_name1 = (
        invitation_details.inviter_name or ""
    )
    pdf_model.accomodation_invitation_details_inviter_name2 = ""
    pdf_model.accomodation_invitation_details_inviter_name3 = ""
    pdf_model.accomodation_invitation_details_inviter_name4 = ""
    pdf_model.accomodation_invitation_details_inviter_address1 = (
        invitation_details.inviter_address or ""
    )
    pdf_model.accomodation_invitation_details_inviter_address2 = ""
    pdf_model.accomodation_invitation_details_inviter_address3 = ""
    pdf_model.accomodation_invitation_details_inviter_address4 = ""

    pdf_model.Text33 = ""
    pdf_model.Text34 = ""
    pdf_model.Text50 = ""
    pdf_model.Text55 = ""
    pdf_model.Text43 = ""
    pdf_model.Text44 = ""
    pdf_model.Text45 = ""
    pdf_model.Text46 = ""
    pdf_model.Text47 = ""
    pdf_model.Text48 = ""

    companion1 = travel_companions[0] if len(travel_companions) > 0 else None
    companion2 = travel_companions[1] if len(travel_companions) > 1 else None
    companion3 = travel_companions[2] if len(travel_companions) > 2 else None
    companion4 = travel_companions[3] if len(travel_companions) > 3 else None
    companion5 = travel_companions[4] if len(travel_companions) > 4 else None

    if companion1:
        pdf_model.passport_travel_companion_details_companion_name1 = (
            companion1.companion_name or ""
        )
        pdf_model.passport_travel_companion_details_relationship_with_applicant1 = (
            companion1.relationship_with_applicant.value
            if companion1.relationship_with_applicant
            else ""
        )
        pdf_model.passport_travel_companion_details_companion_dob1 = (
            companion1.companion_dob.strftime("%d/%m/%Y")
            if companion1.companion_dob
            else ""
        )
        pdf_model.passport_travel_companion_details_companion_place_of_birth1 = (
            companion1.companion_place_of_birth or ""
        )

    if companion2:
        pdf_model.passport_travel_companion_details_companion_name2 = (
            companion2.companion_name or ""
        )
        pdf_model.passport_travel_companion_details_relationship_with_applicant2 = (
            companion2.relationship_with_applicant.value
            if companion2.relationship_with_applicant
            else ""
        )
        pdf_model.passport_travel_companion_details_companion_dob2 = (
            companion2.companion_dob.strftime("%d/%m/%Y")
            if companion2.companion_dob
            else ""
        )
        pdf_model.passport_travel_companion_details_companion_place_of_birth2 = (
            companion2.companion_place_of_birth or ""
        )

    if companion3:
        pdf_model.passport_travel_companion_details_companion_name3 = (
            companion3.companion_name or ""
        )
        pdf_model.passport_travel_companion_details_relationship_with_applicant3 = (
            companion3.relationship_with_applicant.value
            if companion3.relationship_with_applicant
            else ""
        )
        pdf_model.passport_travel_companion_details_companion_dob3 = (
            companion3.companion_dob.strftime("%d/%m/%Y")
            if companion3.companion_dob
            else ""
        )
        pdf_model.passport_travel_companion_details_companion_place_of_birth3 = (
            companion3.companion_place_of_birth or ""
        )

    if companion4:
        pdf_model.passport_travel_companion_details_companion_name4 = (
            companion4.companion_name or ""
        )
        pdf_model.passport_travel_companion_details_relationship_with_applicant4 = (
            companion4.relationship_with_applicant.value
            if companion4.relationship_with_applicant
            else ""
        )
        pdf_model.passport_travel_companion_details_companion_dob4 = (
            companion4.companion_dob.strftime("%d/%m/%Y")
            if companion4.companion_dob
            else ""
        )
        pdf_model.passport_travel_companion_details_companion_place_of_birth4 = (
            companion4.companion_place_of_birth or ""
        )

    if companion5:
        pdf_model.passport_travel_companion_details_companion_name5 = (
            companion5.companion_name or ""
        )
        pdf_model.passport_travel_companion_details_relationship_with_applicant5 = (
            companion5.relationship_with_applicant.value
            if companion5.relationship_with_applicant
            else ""
        )
        pdf_model.passport_travel_companion_details_companion_dob5 = (
            companion5.companion_dob.strftime("%d/%m/%Y")
            if companion5.companion_dob
            else ""
        )
        pdf_model.passport_travel_companion_details_companion_place_of_birth5 = (
            companion5.companion_place_of_birth or ""
        )

    if previous_visas:
        previous_visa1 = previous_visas[0] if len(previous_visas) > 0 else None
        previous_visa2 = previous_visas[1] if len(previous_visas) > 1 else None
        previous_visa3 = previous_visas[2] if len(previous_visas) > 2 else None
        previous_visa4 = previous_visas[3] if len(previous_visas) > 3 else None
        previous_visa5 = previous_visas[4] if len(previous_visas) > 4 else None

        if previous_visa1:
            pdf_model.previous_visas_visit_details_previous_visit_date1 = (
                previous_visa1.previous_visit_date.strftime("%d-%m-%Y")
                if previous_visa1.previous_visit_date
                else ""
            )
            pdf_model.previous_visas_visit_details_previous_visit_purpose1 = (
                previous_visa1.previous_visit_purpose or ""
            )
            pdf_model.previous_visas_visit_details_previous_visit_address1 = (
                previous_visa1.previous_visit_address or ""
            )

        if previous_visa2:
            pdf_model.previous_visas_visit_details_previous_visit_date2 = (
                previous_visa2.previous_visit_date.strftime("%d-%m-%Y")
                if previous_visa2.previous_visit_date
                else ""
            )
            pdf_model.previous_visas_visit_details_previous_visit_purpose2 = (
                previous_visa2.previous_visit_purpose or ""
            )
            pdf_model.previous_visas_visit_details_previous_visit_address2 = (
                previous_visa2.previous_visit_address or ""
            )

        if previous_visa3:
            pdf_model.previous_visas_visit_details_previous_visit_date3 = (
                previous_visa3.previous_visit_date.strftime("%d-%m-%Y")
                if previous_visa3.previous_visit_date
                else ""
            )
            pdf_model.previous_visas_visit_details_previous_visit_purpose3 = (
                previous_visa3.previous_visit_purpose or ""
            )
            pdf_model.previous_visas_visit_details_previous_visit_address3 = (
                previous_visa3.previous_visit_address or ""
            )

        if previous_visa4:
            pdf_model.previous_visas_visit_details_previous_visit_date4 = (
                previous_visa4.previous_visit_date.strftime("%d-%m-%Y")
                if previous_visa4.previous_visit_date
                else ""
            )
            pdf_model.previous_visas_visit_details_previous_visit_purpose4 = (
                previous_visa4.previous_visit_purpose or ""
            )
            pdf_model.previous_visas_visit_details_previous_visit_address4 = (
                previous_visa4.previous_visit_address or ""
            )

        if previous_visa5:
            pdf_model.previous_visas_visit_details_previous_visit_date5 = (
                previous_visa5.previous_visit_date.strftime("%d-%m-%Y")
                if previous_visa5.previous_visit_date
                else ""
            )
            pdf_model.previous_visas_visit_details_previous_visit_purpose5 = (
                previous_visa5.previous_visit_purpose or ""
            )
            pdf_model.previous_visas_visit_details_previous_visit_address5 = (
                previous_visa5.previous_visit_address or ""
            )

    pdf_model.Text51 = ""
    pdf_model.Text38 = ""
    pdf_model.Text54 = ""
    pdf_model.Text56 = ""
    pdf_model.Text57 = ""
    pdf_model.Text58 = ""
    pdf_model.Text59 = ""
    pdf_model.Text66 = ""
    pdf_model.Text67 = ""
    pdf_model.Text68 = ""
    pdf_model.Text69 = ""
    pdf_model.Text70 = ""

    return pdf_model.model_dump(by_alias=True)


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


def extract_travel_companions(passport: RootPassport):
    TravelCompanionCls = (
        RootPassportTravelCompanionDetailsTravelcompaniongroupTravelCompanionCard
    )
    groups = (passport.travel_companion_details if passport else None) or []

    travel_companions: List[
        RootPassportTravelCompanionDetailsTravelcompaniongroupTravelCompanionCard
    ] = []
    for grp in groups:
        companion_group = grp.travelcompaniongroup if grp else None

        travel_companion = None
        if companion_group is not None:
            # Use helper to build typed instance safely
            travel_companion = build_typed_from_optional(
                companion_group.travel_companion_card, TravelCompanionCls
            )
        else:
            # create empty typed instance so downstream always gets one
            travel_companion = TravelCompanionCls(**{})

        travel_companions.append(travel_companion)

    return travel_companions


def extract_previous_visas(root_previous_data: RootPreviousVisas):
    PreviousVisaCls = RootPreviousVisasVisitDetailsGroupVisitdetailsVisitDetails
    groups = (
        root_previous_data.visit_details_group if root_previous_data else None
    ) or []

    previous_visas: List[RootPreviousVisasVisitDetailsGroupVisitdetailsVisitDetails] = (
        []
    )
    for grp in groups:
        visit_group = grp.visitdetails if grp else None

        previous_visa = None
        if visit_group is not None:
            # Use helper to build typed instance safely
            previous_visa = build_typed_from_optional(
                visit_group.visit_details, PreviousVisaCls
            )
        else:
            # create empty typed instance so downstream always gets one
            previous_visa = PreviousVisaCls(**{})

        previous_visas.append(previous_visa)

    return previous_visas
