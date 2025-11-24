from lyik.ttk.utils.form_indicator import FormIndicator


# NOTE: Is it scaleable if we have to identify every form one by one through the indicator?
# What if each form mandatorily has these indentifiers in the scratch pad to identify the behavior needed later?


def has_appointment_section(form_indicator: FormIndicator) -> bool:
    if form_indicator in (
        FormIndicator.SCHENGEN,
        FormIndicator.SAUDI_ARABIA,
    ):
        return True
    # elif form_indicator in (
    #     FormIndicator.SINGAPORE,
    #     FormIndicator.UAE,
    #     FormIndicator.INDONESIA,
    # ):
    #     return False
    return False


def has_submission_docket_status_requirement(form_indicator: FormIndicator) -> bool:
    if form_indicator in (
        FormIndicator.SCHENGEN,
        FormIndicator.SINGAPORE,
        FormIndicator.INDONESIA,
    ):
        return True
    # elif form_indicator in (
    #     FormIndicator.SAUDI_ARABIA,
    #     FormIndicator.UAE,
    # ):
    #     return False
    return False
