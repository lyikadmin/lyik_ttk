from datetime import datetime, date
from typing import get_origin, get_args, Union, List, Any, Dict, Tuple, Set, Type, Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from enum import Enum
import inspect
import yaml
import fitz
# --- Mock Models for testing and demonstration ---
# These models are crucial for the script to run standalone.
# If your actual files exist, ensure they are in your Python path.

# Define mock Enum classes if not imported
from new_schengentouristvisa import (
    COUNTRY3,SAMEASPASSADDR,SPONSORTYPE2,SPONSORTYPE3,SPONSORTYPE4,
    VISAMODE,ADDRESSPROOFTYPE,PAYMENTMETHOD2,PAYMENTMETHOD3,EXPENSECOVERAGE4,
    RootVisaRequestInformationVisaRequest,EXPENSECOVERAGE2,
    RootAppointmentAppointmentScheduled,RootAdditionalDetailsTravelInfo,
    RootAppointment,RootTicketingFlightTickets,RootConsultantInfoAppointments,
    RootPhotographPassportPhoto,RootPreviousVisasPreviousVisasDetails,
    Schengentouristvisa, RootTravelInsuranceFlightReservationDetails,
    RootPassport, RootPassportPassportDetails, RootPassportOtherDetails,
    RootAdditionalDetails, RootAdditionalDetailsNationalId,
    RootPreviousVisasFingerprintDetails,RootAdditionalDetailsAppDetails,
    RootLetsGetStarted, RootVisaRequestInformation, RootAppointment,
    RootPhotograph, RootResidentialAddress, RootWorkAddress,
    RootSharedTravellInfo, RootItineraryAccomodation, RootAccomodation,
    RootAccomodationAddOnService,RootTicketingAddOnService,
    RootTicketing, RootTravelInsurance, RootPreviousVisas,
    RootAdditionalDetailsFamilyEu,RootAdditionalDetailsSponsorship,
    RootSalarySlip, RootBankStatement, RootItrAcknowledgement,
    RootAddons, RootConsultantInfo, RootSubmitInfo, RootDocketInfo,
    RootResidentialAddressResidentialAddressCardV1,
    RootResidentialAddressResidentialAddressCardV2,
    RootItineraryAccomodationItineraryCard,RootAccomodationAccommodationChoice,
    RootAccomodationInvitationDetails,RootAccomodationBookedAppointment,
    RootWorkAddressWorkDetails,RootSharedTravellInfoShared
)
from new_schengentouristvisa import (
    PREFLOC,HOURSELECT,MINUTESELECT,ADDONSERVICEAPPOINTMENT,
    RELATIONSHIP,COUNTRY,FAMILYMEMBEROFEU,
    ACCOMMODATIONARRANGEMENT,
    SAMEITINERARYASPRIMARY,SAMEACCOMMODATIONASPRIMARY,SAMEFLIGHTTICKETASPRIMARY,
    CURRENTOCCUPATIONSTATUS,
    GENDER, CIVILMARITALSTATUS, RELATIONSHIPWITHEU,
    PAYMENTMETHOD1, PAYMENTMETHOD2, PAYMENTMETHOD3, PAYMENTMETHOD4,
    PAYMENTMETHOD5, PAYMENTMETHOD6, SPONSORTYPE1, PURPOSEOFVISAORTRAVEL,
    VISATYPE, PASSPORTTYPE, OPTION, EXPENSECOVERAGE1, EXPENSECOVERAGE5, EXPENSECOVERAGE3,
)
from Switzerland6 import Switzerland6 # This will be redefined below

def process_pdf_model(pdf_model: BaseModel) -> BaseModel:
    """
    Iterates through the fields of a Pydantic model instance.
    If a string-type field is currently None, it assigns the field's name to it.

    Args:
        pdf_model: An instance of a Pydantic model.

    Returns:
        The modified model instance.
    """
    for field_name, field_info in pdf_model.model_fields.items():
        current_value = getattr(pdf_model, field_name)

        # Resolve real type
        annotation = field_info.annotation
        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is Union:
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                real_type = non_none_args[0]
            else:
                continue  # skip ambiguous Union types
        else:
            real_type = annotation
        if real_type == bool and not current_value:
            print(f"field_name not set {field_name}")
        # If it's a string field and is currently None
        if real_type == str and (current_value is None or current_value == ""):
            setattr(pdf_model, field_name, field_name)

    return pdf_model

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
if __name__ == "__main__":
    # --- Create object of Schengentouristvisa and assign valid data ---
    print("--- Creating and populating Schengentouristvisa object ---")
    data_model = Schengentouristvisa( 
        lets_get_started=RootLetsGetStarted(
            instruction_display="Please fill out the form carefully.",
            form_status="Draft",
        ),
        visa_request_information=RootVisaRequestInformation(
            visa_request=RootVisaRequestInformationVisaRequest(
                phone_number="+919876543210",
                email_id="sample@email.com",
                from_country=COUNTRY3.IND,
                to_country=COUNTRY3.FRA,
                departure_date=datetime(2025, 9, 1),
                arrival_date=datetime(2025, 9, 15),
                visa_type=VISATYPE.Tourist,
                length_of_stay=14,
                validity=30,
                visa_mode=VISAMODE.Sticker,
                traveller_type="Individual",
                earliest_appointment_availability="2025-08-01",
                visa_processing_type="Standard",
            ),
        ),
        appointment=RootAppointment(
            appointment_scheduled=RootAppointmentAppointmentScheduled(
                scheduled_location=PREFLOC.Bengaluru,
                appointment_date=datetime(2025, 8, 15),
                scheduled_hour=HOURSELECT.integer_10,
                scheduled_minute=MINUTESELECT.integer_50,
            ),
            lock_appointment="Yes",
            add_on_service_option=ADDONSERVICEAPPOINTMENT.YES
        ),
        passport=RootPassport(
            passport_details=RootPassportPassportDetails(
                type_of_passport=PASSPORTTYPE.REGULAR,
                first_name="John",
                surname="Doe",
                date_of_birth=datetime(1990, 5, 15),
                passport_number="P1234567",
                date_of_issue=datetime(2020, 1, 10),
                date_of_expiry=datetime(2030, 1, 9),
                gender=GENDER.M,
                place_of_birth="Mumbai",
                nationality="Indian",
                issued_by="India",
                father_name="Richard Doe",
                mother_name="Jane Doe",
                spouse_name="Alice Doe",
                address_line_1="123 Main St",
                address_line_2="Apt 456",
                city="Bengaluru",
                pin_code="560001",
                state="Karnataka",
                country="India",
                desired_validity="6 months",                
            ),
            other_details=RootPassportOtherDetails(
                civil_status=CIVILMARITALSTATUS.SINGLE,
                nationality_of_birth="Jaunpur",
                other_nationality="Indian",
            )
        ),
        photograph=RootPhotograph(
            passport_photo=RootPhotographPassportPhoto(
                upload_photo_display="Upload your passport photo",
                photo="base64_encoded_image_string",
            )
        ),
        residential_address=RootResidentialAddress(
            same_as_passport_address=SAMEASPASSADDR.SAME_AS_PASS_ADDR,
            residential_address_card_v1=RootResidentialAddressResidentialAddressCardV1(
                type_of_proof=ADDRESSPROOFTYPE.ELECTRICITY,
                address_proof_upload="base64_encoded_address_proof_string",
                address_line_1="123 Main St",
                address_line_2="Apt 456",
                pin_code="560001",
                city="Bengaluru",
                state="Karnataka",
                country="India",
            ),
            residential_address_card_v2=RootResidentialAddressResidentialAddressCardV2(
                address_line_1="123 Main St",
                address_line_2="Apt 456",
                pin_code="560001",
                city="Bengaluru",
                state="Karnataka",
                country="India",

            )
        ),
        work_address=RootWorkAddress(
            current_occupation_status=CURRENTOCCUPATIONSTATUS.EMPLOYEE,
            work_details=RootWorkAddressWorkDetails(
                employer_name="Tech Solutions Inc.",
                occupation="Software Engineer",
                date_of_joining=datetime(2020, 1, 15),
                work_phone="+919876543210",
                work_address="456 Business Rd, Bengaluru, Karnataka, 560001, India",
            )
        ),
        shared_travell_info=RootSharedTravellInfo(
            shared=RootSharedTravellInfoShared(
                itinerary_same=SAMEITINERARYASPRIMARY.ITINERARY,
                accommodation_same=SAMEACCOMMODATIONASPRIMARY.ACCOMMODATION,
                flight_ticket_same=SAMEFLIGHTTICKETASPRIMARY.FLIGHT_TICKET,
            )

        ),
        itinerary_accomodation=RootItineraryAccomodation(
            lock_itinerary="Yes",
            itinerary_card=RootItineraryAccomodationItineraryCard(
                display_itinerary_card_instructions="Please fill out your itinerary details.",
                upload_itinerary="base64_encoded_itinerary_string",
            )
        )
        ,
        accomodation=RootAccomodation(
            lock_accommodation="Yes",
            accommodation_choice=RootAccomodationAccommodationChoice(
                accommodation_option=ACCOMMODATIONARRANGEMENT.BOOKED
            ),
            invitation_details=RootAccomodationInvitationDetails(
                    inviter_name="Jane Smith",
                    relationship=RELATIONSHIP.SPOUSE,
                    inviter_address="789 Guest St, Paris, France",
                    mobile_number="+33123456789",
                    email_id="jane@email.com",
                    accommodation_proof="base64_encoded_accommodation_proof_string",   
                ),
            booked_appointment=RootAccomodationBookedAppointment(
                accommodation_name="Hotel Paris",
                accommodation_address="123 Hotel St, Paris, France",
                accommodation_email="email@mail.com",
                accommodation_phone="+33123456789",
            ),
            add_on_service=RootAccomodationAddOnService(                
            ),
        ),
        ticketing=RootTicketing(
            lock_ticket="Yes",
            flight_tickets=RootTicketingFlightTickets(
                display_flight_tickets_instructions="Flight from Bengaluru to Paris on 2025-09-01, return on 2025-09-15",
                flight_tickets="base64_encoded_flight_ticket_string",
            ),
            add_on_service=RootTicketingAddOnService(
                display_add_on="Yes"
            ),

        ),
        travel_insurance=RootTravelInsurance(
            lock_travel_insurance="Yes",
            flight_reservation_details=RootTravelInsuranceFlightReservationDetails()
        ),
        previous_visas=RootPreviousVisas(
            previous_visas_details=RootPreviousVisasPreviousVisasDetails(
                have_past_visa=OPTION.YES,
                previous_visa_copy="base64_encoded_previous_visa_string",
                visa_number="V1234567",
                visa_type="Tourist",
                country_of_issue=COUNTRY.GRC,
                start_date=datetime(2023, 5, 15),
                end_date=datetime(2023, 11, 15),
                purpose_of_visa=PURPOSEOFVISAORTRAVEL.TOURISM,
                utilized_visa=OPTION.YES,
            ),
            fingerprint_details=RootPreviousVisasFingerprintDetails(
                fingerprint_collected=OPTION.YES,
                visa_sticker_number="GER123ABC",
                date_of_previous_visa=datetime(2023, 5, 15),
            )
        ),
        additional_details=RootAdditionalDetails(
            national_id=RootAdditionalDetailsNationalId(
                aadhaar_number="1234-5678-9012",
            ),
            travel_info=RootAdditionalDetailsTravelInfo(
                travelling_to_other_country=OPTION.YES,
                country_of_travel=COUNTRY3.IND,
                valid_visa_for_country=OPTION.YES,
                start_date_of_visa=datetime(2025, 1, 1),
                end_date_of_visa=datetime(2025, 12, 31),
            ),
            app_details=RootAdditionalDetailsAppDetails(
                application_on_behalf=OPTION.NO,
                surname="Doe",
                first_name="John",
                address_line_1="123 Main St",
                address_line_2="Apt 456",
                pin_code="560001",
                city="Bengaluru",
                state="Karnataka",
                country="India",
                email_address="mail@email.com",
                telephone_mobile_number="+919876543210",
            ),
            family_eu=RootAdditionalDetailsFamilyEu(
                is_family_member=FAMILYMEMBEROFEU.YES,
                given_name="Alice",
                surname="Doe",
                nationality="indian",
                date_of_birth=datetime(1985, 3, 20),
                travel_document_id="DE12345678",
                relationship=RELATIONSHIPWITHEU.SPOUSE

            ),
            sponsorship=RootAdditionalDetailsSponsorship(
                sponsorship_options_1=SPONSORTYPE1.SELF,
                sponsorship_options_2=SPONSORTYPE2.SPONSOR,
                sponsorship_options_3=SPONSORTYPE3.INVITER,
                sponsorship_options_4=SPONSORTYPE4.OTHER,
                others_specify="Other Sponsor",
                support_means_cash=PAYMENTMETHOD1.CASH,
                support_means_travellers_cheque=PAYMENTMETHOD2.TRAVELLERS_CHEQUE,
                support_means_credit_card=PAYMENTMETHOD3.CREDIT_CARD,
                support_means_prepaid_accommodation=PAYMENTMETHOD4.PREPAID_ACCOMMODATION,
                support_means_prepaid_transport=PAYMENTMETHOD5.PREPAID_TRANSPORT,
                support_means_other=PAYMENTMETHOD6.OTHER,
                others_specify_1="Other Payment Method",
                coverage_expense_cash=EXPENSECOVERAGE1.CASH,
                coverage_accommodation_provided=EXPENSECOVERAGE2.ACCOMMODATION_PROVIDED,
                coverage_all_covered=EXPENSECOVERAGE3.ALL_COVERED,
                coverage_prepaid_transport=EXPENSECOVERAGE4.PREPAID_TRANSPORT,
                coverage_other= EXPENSECOVERAGE5.OTHER,
                others_specify_2="Other Coverage Method",
            )
        ),
        salary_slip= RootSalarySlip(
        ),
        bank_statement=RootBankStatement(),
        itr_acknowledgement=RootItrAcknowledgement(),
        addons=RootAddons(
        ),
        consultant_info=RootConsultantInfo(
            appointments=RootConsultantInfoAppointments(
                scheduled_location=PREFLOC.Bengaluru,
                scheduled_date=datetime(2025, 8, 15),
                scheduled_hour=HOURSELECT.integer_10,
                scheduled_minute=MINUTESELECT.integer_50,
            ),

        ),

                                                   
    )

    pdf_model = Switzerland6()
    pdf_model.visa_1st_arrival_date=data_model.visa_request_information.visa_request.arrival_date.strftime("%Y-%m-%d")
    pdf_model.visa_addl_stay_info=data_model.visa_request_information.visa_request.visa_type

    pdf_model.visa_first_name=data_model.passport.passport_details.first_name
    pdf_model.visa_surname_family_name=data_model.passport.passport_details.surname
    pdf_model.visa_surname_at_birth=data_model.passport.passport_details.surname
    pdf_model.visa_dob=data_model.passport.passport_details.date_of_birth.strftime("%Y-%m-%d")
    pdf_model.visa_pob=data_model.passport.passport_details.place_of_birth
    pdf_model.visa_cob=data_model.passport.passport_details.country
    pdf_model.visa_sex_male=data_model.passport.passport_details.gender== "M"
    pdf_model.visa_sex_female=data_model.passport.passport_details.gender== "F"
    pdf_model.visa_sex_oth=data_model.passport.passport_details.gender!= "F" and data_model.passport.passport_details.gender != "M"

    pdf_model.visa_curr_natl= data_model.passport.passport_details.nationality
    pdf_model.visa_oth_natl= data_model.passport.other_details.other_nationality
    pdf_model.visa_natl_at_birth= data_model.passport.other_details.nationality_of_birth
    pdf_model.visa_civil_sts_single=data_model.passport.other_details.civil_status== CIVILMARITALSTATUS.SINGLE
    pdf_model.visa_civil_sts_married=data_model.passport.other_details.civil_status== CIVILMARITALSTATUS.MARRIED
    pdf_model.visa_civil_sts_seperated=data_model.passport.other_details.civil_status== CIVILMARITALSTATUS.SEPARATED
    pdf_model.visa_civil_sts_divorced=data_model.passport.other_details.civil_status== CIVILMARITALSTATUS.DIVORCED
    pdf_model.visa_civil_widow=data_model.passport.other_details.civil_status== CIVILMARITALSTATUS.WIDOWED
    # pdf_model.visa_civil_sts_reg_partner=data_model.passport.other_details.civil_status== CIVILMARITALSTATUS.REGISTERED_PARTNER
    pdf_model.visa_parental_auth=data_model.passport.passport_details.father_name + " & " + data_model.passport.passport_details.mother_name

    pdf_model.visa_trav_cost_self=data_model.additional_details.sponsorship.sponsorship_options_1==SPONSORTYPE1.SELF
    pdf_model.visa_trav_cost_self_cash=data_model.additional_details.sponsorship.support_means_cash==PAYMENTMETHOD1.CASH
    pdf_model.visa_trav_cost_self_tc=data_model.additional_details.sponsorship.support_means_travellers_cheque==PAYMENTMETHOD2.TRAVELLERS_CHEQUE
    pdf_model.visa_trav_cost_self_cc=data_model.additional_details.sponsorship.support_means_credit_card==PAYMENTMETHOD3.CREDIT_CARD
    pdf_model.visa_trav_cost_self_ppa=data_model.additional_details.sponsorship.support_means_prepaid_accommodation==PAYMENTMETHOD4.PREPAID_ACCOMMODATION
    pdf_model.visa_trav_cost_self_ppt=data_model.additional_details.sponsorship.support_means_prepaid_transport==PAYMENTMETHOD5.PREPAID_TRANSPORT
    pdf_model.visa_trav_cost_self_oth=data_model.additional_details.sponsorship.sponsorship_options_4==SPONSORTYPE4.OTHER
    if pdf_model.visa_trav_cost_self_oth:
        pdf_model.visa_trav_cost_self_oth_txt=data_model.additional_details.sponsorship.others_specify
    pdf_model.visa_means_supportoth_oth=data_model.additional_details.sponsorship.support_means_other==PAYMENTMETHOD6.OTHER
    if pdf_model.visa_means_supportoth_oth:
        pdf_model.visa_means_support_oth_txt=data_model.additional_details.sponsorship.others_specify_1
    # pdf_model.visa_trav_cost_31_32=
    pdf_model.visa_nat_id_num=data_model.additional_details.national_id.aadhaar_number
    pdf_model.visa_typ_trav_doc_ord=data_model.passport.passport_details.type_of_passport == PASSPORTTYPE.REGULAR
    # pdf_model.visa_typ_trav_doc_service=data_model.passport.passport_details.type_of_passport == PASSPORTTYPE.OFFICIAL
    # pdf_model.visa_typ_trav_doc_special=data_model.passport.passport_details.type_of_passport == PASSPORTTYPE.SPECIAL
    pdf_model.visa_typ_trav_doc_diplomatic=data_model.passport.passport_details.type_of_passport == PASSPORTTYPE.DIPLOMATIC
    pdf_model.visa_typ_trav_doc_official=data_model.passport.passport_details.type_of_passport == PASSPORTTYPE.OFFICIAL

    pdf_model.visa_num_trav_doc=data_model.passport.passport_details.passport_number
    # pdf_model.visa_typ_trav_doc_oth=data_model.passport.passport_details.type_of_passport == PASSPORTTYPE.OTHER

    pdf_model.visa_doi=data_model.passport.passport_details.date_of_issue.strftime("%Y-%m-%d")
    pdf_model.visa_val_til=data_model.passport.passport_details.date_of_expiry.strftime("%Y-%m-%d")
    pdf_model.visa_issued_by_ctry=data_model.passport.passport_details.issued_by

    pdf_model.visa_fam_mem_eu_1st_nm=data_model.additional_details.family_eu.given_name
    pdf_model.visa_fam_mem_eu_surname=data_model.additional_details.family_eu.surname
    pdf_model.visa_fam_mem_eu_dob=data_model.additional_details.family_eu.date_of_birth.strftime("%Y-%m-%d")
    pdf_model.visa_fam_mem_eu_natl=data_model.additional_details.family_eu.nationality
    pdf_model.visa_fam_mem_eu_num_trav_doc=data_model.additional_details.family_eu.travel_document_id
    pdf_model.visa_mem_1st_entry=data_model.additional_details.travel_info.start_date_of_visa
    pdf_model.visa_dptr_date=data_model.additional_details.travel_info.end_date_of_visa
    pdf_model.visa_fam_rs_eu_spouse=data_model.additional_details.family_eu.relationship == RELATIONSHIPWITHEU.SPOUSE
    pdf_model.visa_fam_rs_eu_child=data_model.additional_details.family_eu.relationship == RELATIONSHIPWITHEU.CHILD
    pdf_model.visa_fam_rs_eu_gc=data_model.additional_details.family_eu.relationship == RELATIONSHIPWITHEU.GRANDCHILD
    pdf_model.visa_entry_num_req_single=data_model.additional_details.travel_info.travelling_to_other_country==OPTION.NO
    pdf_model.visa_entry_num_req_two=data_model.additional_details.travel_info.travelling_to_other_country==OPTION.YES
    # pdf_model.visa_fam_rs_eu_dependent=data_model.additional_details.family_eu.relationship == RELATIONSHIPWITHEU.DEPENDENT
    pdf_model.visa_fam_rs_eu_registered=data_model.additional_details.family_eu.relationship == RELATIONSHIPWITHEU.REGISTERED_PARTNER
    pdf_model.visa_fam_rs_eu_oth=data_model.additional_details.family_eu.relationship == RELATIONSHIPWITHEU.OTHER
    pdf_model.visa_fam_rs_eu_oth_txt=data_model.additional_details.family_eu.relationship if data_model.additional_details.family_eu.relationship not in [RELATIONSHIPWITHEU.SPOUSE, RELATIONSHIPWITHEU.CHILD, RELATIONSHIPWITHEU.GRANDCHILD, RELATIONSHIPWITHEU.REGISTERED_PARTNER, RELATIONSHIPWITHEU.OTHER] else ""

    pdf_model.visa_app_addr=data_model.additional_details.app_details.address_line_1 + ", " + data_model.additional_details.app_details.address_line_2 + ", " + data_model.additional_details.app_details.city + ", " + data_model.additional_details.app_details.state + ", " + data_model.additional_details.app_details.pin_code + ", " + data_model.additional_details.app_details.country +"," +data_model.additional_details.app_details.email_address
    pdf_model.visa_app_addr = pdf_model.visa_app_addr.strip(", ")
    pdf_model.visa_app_tel_num=data_model.additional_details.app_details.telephone_mobile_number

    pdf_model.visa_fingerprint_no=data_model.previous_visas.fingerprint_details.fingerprint_collected==OPTION.NO
    pdf_model.visa_fingerprint_yes=data_model.previous_visas.fingerprint_details.fingerprint_collected==OPTION.YES
    if pdf_model.visa_fingerprint_yes:
        pdf_model.visa_fingerprint_yes_date=data_model.previous_visas.fingerprint_details.date_of_previous_visa
        pdf_model.visa_fingerprint_yes_sticker_num=data_model.previous_visas.fingerprint_details.visa_sticker_number
    
    pdf_model.visa_jrn_purpose_visit_fnf=data_model.previous_visas.previous_visas_details.purpose_of_visa==PURPOSEOFVISAORTRAVEL.VISIT_FAMILY_FRIENDS
    pdf_model.visa_jrn_purpose_tour=data_model.previous_visas.previous_visas_details.purpose_of_visa==PURPOSEOFVISAORTRAVEL.TOURISM
    pdf_model.visa_jrn_purpose_business=data_model.previous_visas.previous_visas_details.purpose_of_visa==PURPOSEOFVISAORTRAVEL.BUSINESS
    pdf_model.visa_jrn_purpose_culture=data_model.previous_visas.previous_visas_details.purpose_of_visa==PURPOSEOFVISAORTRAVEL.CULTURAL
    pdf_model.visa_jrn_purpose_official=data_model.previous_visas.previous_visas_details.purpose_of_visa==PURPOSEOFVISAORTRAVEL.OFFICIAL_VISIT
    pdf_model.visa_jrn_purpose_study=data_model.previous_visas.previous_visas_details.purpose_of_visa==PURPOSEOFVISAORTRAVEL.STUDY
    pdf_model.visa_jrn_purpose_med=data_model.previous_visas.previous_visas_details.purpose_of_visa==PURPOSEOFVISAORTRAVEL.MEDICAL
    pdf_model.visa_jrn_purpose_sports=data_model.previous_visas.previous_visas_details.purpose_of_visa==PURPOSEOFVISAORTRAVEL.SPORTS
    pdf_model.visa_jrn_purpose_transit=data_model.previous_visas.previous_visas_details.purpose_of_visa==PURPOSEOFVISAORTRAVEL.AIRPORT_TRANSIT
    pdf_model.visa_jrn_purpose_oth=data_model.previous_visas.previous_visas_details.purpose_of_visa==PURPOSEOFVISAORTRAVEL.OTHER
    if pdf_model.visa_jrn_purpose_oth:
        pass
        # pdf_model.visa_jrn_purpose_oth_txt=data_model.previous_visas.previous_visas_details.

    pdf_model.visa_permit_final_ctry_dest_issued_by=data_model.previous_visas.previous_visas_details.country_of_issue
    pdf_model.visa_permit_final_ctry_dest_valid_from=data_model.previous_visas.previous_visas_details.start_date
    pdf_model.visa_permit_final_ctry_dest_til=data_model.previous_visas.previous_visas_details.end_date

    pdf_model.visa_invite_temp_accom_tel_mun=data_model.work_address.work_details.work_phone
    pdf_model.visa_invite_org_comm_details=data_model.work_address.work_details.work_address
    pdf_model.visa_invite_org=data_model.work_address.work_details.employer_name
    pdf_model.visa_invite_temp_accom_tel_num=data_model.accomodation.invitation_details.mobile_number
    pdf_model.visa_invite_temp_accom=data_model.accomodation.invitation_details.inviter_name
    pdf_model.visa_invite_temp_accom_comm_details=data_model.accomodation.invitation_details.inviter_address + ","+ data_model.accomodation.invitation_details.email_id
    pdf_model.visa_curr_occ=data_model.work_address.work_details.occupation
    pdf_model.visa_emp_stu_add_tel=data_model.work_address.work_details.employer_name +","+ data_model.work_address.work_details.work_address+","+data_model.work_address.work_details.work_phone
    # pdf_model.visa_oth_trav_doc_txt=data_model.shared_travell_info.
    pdf_model.visa_applicant_diff_addr=data_model.residential_address.residential_address_card_v1.address_line_1 +","+data_model.residential_address.residential_address_card_v1.address_line_2 +","+data_model.residential_address.residential_address_card_v1.city+","+data_model.residential_address.residential_address_card_v1.country
    pdf_model.visa_applicant_diff_tel_num=data_model.visa_request_information.visa_request.phone_number

    pdf_model.visa_mem_main_dst=data_model.visa_request_information.visa_request.to_country
    pdf_model.visa_applicant_diff_surnm_nm=data_model.additional_details.app_details.first_name +","+data_model.additional_details.app_details.surname
    template_pdf = "Switzerland6_original.pdf"
    filled_pdf = f"{template_pdf}_filled.pdf"
    # print(f"Filling Switzerland6 PDF form with sample data... {sample_data}")
    # model_instance = Switzerland6(**sample_data)
    # pdf_model1=process_pdf_model(pdf_model=pdf_model)
    # Then call the PDF fill function
    fill_pdf_form(template_pdf, filled_pdf, pdf_model)    
    # print(f"pdf_model1 is {pdf_model1} ")
    # print(f"\n--- Mapping Schengentouristvisa to Schengentouristvisa --- {data_model}")  
