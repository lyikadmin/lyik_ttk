from typing import Any
from pydantic import BaseModel
from lyikpluginmanager.core.utils import StrEnum


class FormIndicator(StrEnum):
    SCHENGEN = "SCHENGEN"
    SGP = "SGP"
    ARE = "ARE"
    SAU = "SAU"


# Schengen Country Codes
_SCHENGEN_COUNTRY_CODES = {
    "AUT",  # Austria
    "BEL",  # Belgium
    "BGR",  # Bulgaria
    "HRV",  # Croatia
    "CZE",  # Czech Republic
    "DNK",  # Denmark
    "EST",  # Estonia
    "FIN",  # Finland
    "FRA",  # France
    "DEU",  # Germany
    "GRC",  # Greece
    "HUN",  # Hungary
    "ISL",  # Iceland
    "ITA",  # Italy
    "LVA",  # Latvia
    "LIE",  # Liechtenstein
    "LTU",  # Lithuania
    "LUX",  # Luxembourg
    "MLT",  # Malta
    "NLD",  # Netherlands (the)
    "NOR",  # Norway
    "POL",  # Poland
    "PRT",  # Portugal
    "ROU",  # Romania
    "SVK",  # Slovakia
    "SVN",  # Slovenia
    "ESP",  # Spain
    "SWE",  # Sweden
    "CHE",  # Switzerland
}

# Individual Country Codes → Indicators
_INDIVIDUAL_COUNTRY_INDICATORS: dict[str, FormIndicator] = {
    "SGP": FormIndicator.SGP,  # Singapore
    "ARE": FormIndicator.ARE,  # UAE
    "SAU": FormIndicator.SAU,  # Saudi Arabia
}


def get_form_indicator(form_rec: dict | BaseModel) -> FormIndicator | None:
    # If it's a pydantic BaseModel (or similar), convert to dict
    if isinstance(form_rec, BaseModel):
        form_rec = form_rec.model_dump()
    else:
        form_rec = form_rec or {}

    if form_rec is None:
        return None

    form_indicator: str | None = None

    # 1. Try explicit indicator(s) first
    try:
        scratch_pad = form_rec.get("scratch_pad") or {}
        form_indicator = scratch_pad.get("form_indicator")
    except AttributeError:
        pass

    if not form_indicator:
        try:
            vri = form_rec.get("visa_request_information") or {}
            vr = vri.get("visa_request") or {}
            form_indicator = vr.get("form_indicator")
        except AttributeError:
            pass

    if form_indicator:
        return str(form_indicator)

    # 2. Derive from to_country if indicator is missing
    to_country_code: str | None = None
    try:
        vri = form_rec.get("visa_request_information") or {}
        vr = vri.get("visa_request") or {}
        to_country_code = vr.get("to_country")
    except AttributeError:
        pass

    if not to_country_code:
        return None

    code = str(to_country_code).upper()

    # Schengen Country Forms
    if code in _SCHENGEN_COUNTRY_CODES:
        return FormIndicator.SCHENGEN

    # Individual Country Forms
    if code in _INDIVIDUAL_COUNTRY_INDICATORS:
        return _INDIVIDUAL_COUNTRY_INDICATORS[code]

    # 3. Fallback: unknown country type
    return None
