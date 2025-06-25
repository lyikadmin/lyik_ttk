import fitz  # PyMuPDF
from datetime import date

from Switzerland6 import Switzerland6

from new_schengentouristvisa import (
    COUNTRY3,
    EXPENSECOVERAGE1,
    EXPENSECOVERAGE2,
    EXPENSECOVERAGE3,
    EXPENSECOVERAGE4,
    EXPENSECOVERAGE5,
    FAMILYMEMBEROFEU,
    OPTION,
    PASSPORTTYPE,
    PAYMENTMETHOD1,
    PAYMENTMETHOD2,
    PAYMENTMETHOD3,
    PAYMENTMETHOD4,
    PAYMENTMETHOD5,
    PAYMENTMETHOD6,
    RELATIONSHIPWITHEU,
    SPONSORTYPE1,
    SPONSORTYPE2,
    SPONSORTYPE3,
    SPONSORTYPE4,
    RootAdditionalDetails,
    RootAdditionalDetailsAppDetails,
    RootAdditionalDetailsFamilyEu,
    RootAdditionalDetailsNationalId,
    RootAdditionalDetailsSponsorship,
    RootAdditionalDetailsTravelInfo,
    RootPassport,
    RootPassportInstructionPassport,
    RootPassportOtherDetails,
    RootPassportPassportDetails,
    Schengentouristvisa,
    GENDER,
    CIVILMARITALSTATUS,
)


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


# Sample data from nested Schengen structure
schengen_visa_data = Schengentouristvisa(
    passport=RootPassport(
        passport_details=RootPassportPassportDetails(
            desired_validity="12",
            first_name="Dinesh",
            date_of_birth=date(1990, 5, 15),
            date_of_issue=date(2020, 1, 10),
            gender=GENDER.M,
            place_of_issue="Bengaluru",
            nationality="Indian",
            issued_by="Passport Authority",
            surname="Singh",
            passport_number="P1234567",
            date_of_expiry=date(2030, 1, 9),
            place_of_birth="Jaunpur",
            type_of_passport=PASSPORTTYPE.REGULAR,
            ovd_front={
                "file_name": "passport_front_image.jpg",
                "url": "https://example.com/passport_front_image.jpg",
            },
            ovd_back={
                "file_name": "passport_back_image.jpg",
                "url": "https://example.com/passport_back_image.jpg",
            },
            father_name="Father",
            mother_name="Mother",
            spouse_name="Sushma",
            address_line_1="10 Downing Street",
            address_line_2="Whitehall",
            pin_code="SW1A 2AA",
            city="Bengaluru",
            state="Karnataka",
            country="India",
        ),
        other_details=RootPassportOtherDetails(
            civil_status=CIVILMARITALSTATUS.SINGLE,
            nationality_of_birth="Indian",
            other_nationality="American",
        ),
    ),
    additional_details=RootAdditionalDetails(
        national_id=RootAdditionalDetailsNationalId(
            aadhaar_number="123456789012",
            aadhaar_upload={
                "file_name": "aadhaar.pdf",
                "url": "https://example.com/aadhaar.pdf",
            },
        ),
        travel_info=RootAdditionalDetailsTravelInfo(
            travelling_to_other_country=OPTION.YES,
            country_of_travel=COUNTRY3.BTN,
            valid_visa_for_country=OPTION.YES,
            start_date_of_visa=date(2025, 7, 1),
            end_date_of_visa=date(2025, 7, 30),
            visa_copy={
                "file_name": "uk_visa.jpg",
                "url": "https://example.com/uk_visa.jpg",
            },
        ),
        app_details=RootAdditionalDetailsAppDetails(),
        family_eu=RootAdditionalDetailsFamilyEu(
            is_family_member=FAMILYMEMBEROFEU.YES,
            given_name="Maria",
            surname="Gonzalez",
            nationality="Spanish",
            date_of_birth=date(1975, 1, 20),
            travel_document_id="ES987654321",
            relationship=RELATIONSHIPWITHEU.SPOUSE,
        ),
        sponsorship=RootAdditionalDetailsSponsorship(
            display_sponsorship_details="Please select the type of your sponsor(s). You may add more than one.",
            sponsorship_options_1=SPONSORTYPE1.SELF,
            sponsorship_options_2=SPONSORTYPE2.SPONSOR,
            sponsorship_options_3=SPONSORTYPE3.INVITER,
            sponsorship_options_4=SPONSORTYPE4.OTHER,
            display_sponsorship_support="Please select the Means of Support for covering your own costs.",
            support_means_cash=PAYMENTMETHOD1.CASH,
            support_means_travellers_cheque=PAYMENTMETHOD2.TRAVELLERS_CHEQUE,
            support_means_credit_card=PAYMENTMETHOD3.CREDIT_CARD,
            support_means_prepaid_accommodation=PAYMENTMETHOD4.PREPAID_ACCOMMODATION,
            support_means_prepaid_transport=PAYMENTMETHOD5.PREPAID_TRANSPORT,
            support_means_other=PAYMENTMETHOD6.OTHER,
            display_sponsorship_coverage="Please enter the Means of Support for the sponsor(s).",
            coverage_expense_cash=EXPENSECOVERAGE1.CASH,
            coverage_accommodation_provided=EXPENSECOVERAGE2.ACCOMMODATION_PROVIDED,
            coverage_all_covered=EXPENSECOVERAGE3.ALL_COVERED,
            coverage_prepaid_transport=EXPENSECOVERAGE4.PREPAID_TRANSPORT,
            coverage_other=EXPENSECOVERAGE5.OTHER,
        ),
    ),
)

if __name__ == "__main__":
    # Extract values from Schengen data to fill Switzerland6
    passport_details = schengen_visa_data.passport.passport_details
    other_details = schengen_visa_data.passport.other_details

    # Update Switzerland6 model values manually based on PDF field names
    sample_data = Switzerland6(
        first_name=passport_details.first_name,
        surname=passport_details.surname,
        passport_number=passport_details.passport_number,
        date_of_birth=str(passport_details.date_of_birth),
        date_of_issue=str(passport_details.date_of_issue),
        date_of_expiry=str(passport_details.date_of_expiry),
        place_of_birth=passport_details.place_of_birth,
        place_of_issue=passport_details.place_of_issue,
        issued_by=passport_details.issued_by,
        nationality=passport_details.nationality,
        civil_status=other_details.civil_status.value if other_details else "",
        gender=passport_details.gender.value,
        address=passport_details.address_line_1,
        city=passport_details.city,
        state=passport_details.state,
        country=passport_details.country,
        pin_code=passport_details.pin_code,
    )

    template_pdf = "Switzerland6_original.pdf"
    filled_pdf = f"{template_pdf}_filled.pdf"

    fill_pdf_form(template_pdf, filled_pdf, sample_data)
