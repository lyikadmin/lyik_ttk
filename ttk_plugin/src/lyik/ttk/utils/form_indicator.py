from typing import Any
from pydantic import BaseModel
from lyikpluginmanager.core.utils import StrEnum


class FormIndicator(StrEnum):
    # Group indicator for Schengen countries
    SCHENGEN = "SCHENGEN"

    # Non-Schengen per-country indicators (ISO 3166-1 alpha-3)
    ABW_ARUBA = "ABW"
    AFG_AFGHANISTAN = "AFG"
    AGO_ANGOLA = "AGO"
    AIA_ANGUILLA = "AIA"
    ALA_ALAND_ISLANDS = "ALA"
    ALB_ALBANIA = "ALB"
    AND_ANDORRA = "AND"
    ARE_UNITED_ARAB_EMIRATES = "ARE"
    ARG_ARGENTINA = "ARG"
    ARM_ARMENIA = "ARM"
    ASM_AMERICAN_SAMOA = "ASM"
    ATA_ANTARCTICA = "ATA"
    ATF_FRENCH_SOUTHERN_TERRITORIES = "ATF"
    ATG_ANTIGUA_AND_BARBUDA = "ATG"
    AUS_AUSTRALIA = "AUS"
    AZE_AZERBAIJAN = "AZE"
    BDI_BURUNDI = "BDI"
    BEN_BENIN = "BEN"
    BES_BONAIRE_SINT_EUSTATIUS_AND_SABA = "BES"
    BFA_BURKINA_FASO = "BFA"
    BGD_BANGLADESH = "BGD"
    BHR_BAHRAIN = "BHR"
    BHS_BAHAMAS = "BHS"
    BIH_BOSNIA_AND_HERZEGOVINA = "BIH"
    BLM_SAINT_BARTHELEMY = "BLM"
    BLR_BELARUS = "BLR"
    BLZ_BELIZE = "BLZ"
    BMU_BERMUDA = "BMU"
    BOL_BOLIVIA_PLURINATIONAL_STATE_OF = "BOL"
    BRA_BRAZIL = "BRA"
    BRB_BARBADOS = "BRB"
    BRN_BRUNEI_DARUSSALAM = "BRN"
    BTN_BHUTAN = "BTN"
    BVT_BOUVET_ISLAND = "BVT"
    BWA_BOTSWANA = "BWA"
    CAF_CENTRAL_AFRICAN_REPUBLIC = "CAF"
    CAN_CANADA = "CAN"
    CCK_COCOS_KEELING_ISLANDS = "CCK"
    CHL_CHILE = "CHL"
    CHN_CHINA = "CHN"
    CIV_COTE_DIVOIRE = "CIV"
    CMR_CAMEROON = "CMR"
    COD_CONGO_DEMOCRATIC_REPUBLIC_OF_THE = "COD"
    COG_CONGO = "COG"
    COK_COOK_ISLANDS = "COK"
    COL_COLOMBIA = "COL"
    COM_COMOROS = "COM"
    CPV_CABO_VERDE = "CPV"
    CRI_COSTA_RICA = "CRI"
    CUB_CUBA = "CUB"
    CUW_CURACAO = "CUW"
    CXR_CHRISTMAS_ISLAND = "CXR"
    CYM_CAYMAN_ISLANDS = "CYM"
    CYP_CYPRUS = "CYP"
    DJI_DJIBOUTI = "DJI"
    DMA_DOMINICA = "DMA"
    DOM_DOMINICAN_REPUBLIC = "DOM"
    DZA_ALGERIA = "DZA"
    ECU_ECUADOR = "ECU"
    EGY_EGYPT = "EGY"
    ERI_ERITREA = "ERI"
    ESH_WESTERN_SAHARA = "ESH"
    ETH_ETHIOPIA = "ETH"
    FJI_FIJI = "FJI"
    FLK_FALKLAND_ISLANDS_MALVINAS = "FLK"
    FRO_FAROE_ISLANDS = "FRO"
    FSM_MICRONESIA_FEDERATED_STATES_OF = "FSM"
    GAB_GABON = "GAB"
    GBR_UNITED_KINGDOM = "GBR"
    GEO_GEORGIA = "GEO"
    GGY_GUERNSEY = "GGY"
    GHA_GHANA = "GHA"
    GIB_GIBRALTAR = "GIB"
    GIN_GUINEA = "GIN"
    GLP_GUADELOUPE = "GLP"
    GMB_GAMBIA = "GMB"
    GNB_GUINEA_BISSAU = "GNB"
    GNQ_EQUATORIAL_GUINEA = "GNQ"
    GRD_GRENADA = "GRD"
    GRL_GREENLAND = "GRL"
    GTM_GUATEMALA = "GTM"
    GUF_FRENCH_GUIANA = "GUF"
    GUM_GUAM = "GUM"
    GUY_GUYANA = "GUY"
    HKG_HONG_KONG = "HKG"
    HMD_HEARD_ISLAND_AND_MCDONALD_ISLANDS = "HMD"
    HND_HONDURAS = "HND"
    HTI_HAITI = "HTI"
    IDN_INDONESIA = "IDN"
    IMN_ISLE_OF_MAN = "IMN"
    IND_INDIA = "IND"
    IOT_BRITISH_INDIAN_OCEAN_TERRITORY = "IOT"
    IRL_IRELAND = "IRL"
    IRN_IRAN_ISLAMIC_REPUBLIC_OF = "IRN"
    IRQ_IRAQ = "IRQ"
    ISR_ISRAEL = "ISR"
    JAM_JAMAICA = "JAM"
    JEY_JERSEY = "JEY"
    JOR_JORDAN = "JOR"
    JPN_JAPAN = "JPN"
    KAZ_KAZAKHSTAN = "KAZ"
    KEN_KENYA = "KEN"
    KGZ_KYRGYZSTAN = "KGZ"
    KHM_CAMBODIA = "KHM"
    KIR_KIRIBATI = "KIR"
    KNA_SAINT_KITTS_AND_NEVIS = "KNA"
    KOR_KOREA_REPUBLIC_OF = "KOR"
    KWT_KUWAIT = "KWT"
    LAO_LAO_PEOPLES_DEMOCRATIC_REPUBLIC = "LAO"
    LBN_LEBANON = "LBN"
    LBR_LIBERIA = "LBR"
    LBY_LIBYA = "LBY"
    LCA_SAINT_LUCIA = "LCA"
    LKA_SRI_LANKA = "LKA"
    LSO_LESOTHO = "LSO"
    MAC_MACAO = "MAC"
    MAF_SAINT_MARTIN_FRENCH_PART = "MAF"
    MAR_MOROCCO = "MAR"
    MCO_MONACO = "MCO"
    MDA_MOLDOVA_REPUBLIC_OF = "MDA"
    MDG_MADAGASCAR = "MDG"
    MDV_MALDIVES = "MDV"
    MEX_MEXICO = "MEX"
    MHL_MARSHALL_ISLANDS = "MHL"
    MKD_MACEDONIA_THE_FORMER_YUGOSLAV_REPUBLIC_OF = "MKD"
    MLI_MALI = "MLI"
    MMR_MYANMAR = "MMR"
    MNE_MONTENEGRO = "MNE"
    MNG_MONGOLIA = "MNG"
    MNP_NORTHERN_MARIANA_ISLANDS = "MNP"
    MOZ_MOZAMBIQUE = "MOZ"
    MRT_MAURITANIA = "MRT"
    MSR_MONTSERRAT = "MSR"
    MTQ_MARTINIQUE = "MTQ"
    MUS_MAURITIUS = "MUS"
    MWI_MALAWI = "MWI"
    MYS_MALAYSIA = "MYS"
    MYT_MAYOTTE = "MYT"
    NAM_NAMIBIA = "NAM"
    NCL_NEW_CALEDONIA = "NCL"
    NER_NIGER = "NER"
    NFK_NORFOLK_ISLAND = "NFK"
    NGA_NIGERIA = "NGA"
    NIC_NICARAGUA = "NIC"
    NIU_NIUE = "NIU"
    NPL_NEPAL = "NPL"
    NRU_NAURU = "NRU"
    NZL_NEW_ZEALAND = "NZL"
    OMN_OMAN = "OMN"
    PAK_PAKISTAN = "PAK"
    PAN_PANAMA = "PAN"
    PCN_PITCAIRN = "PCN"
    PER_PERU = "PER"
    PHL_PHILIPPINES = "PHL"
    PLW_PALAU = "PLW"
    PNG_PAPUA_NEW_GUINEA = "PNG"
    PRI_PUERTO_RICO = "PRI"
    PRK_KOREA_DEMOCRATIC_PEOPLES_REPUBLIC_OF = "PRK"
    PRY_PARAGUAY = "PRY"
    PSE_PALESTINE_STATE_OF = "PSE"
    PYF_FRENCH_POLYNESIA = "PYF"
    QAT_QATAR = "QAT"
    REU_REUNION = "REU"
    RUS_RUSSIAN_FEDERATION = "RUS"
    RWA_RWANDA = "RWA"
    SAU_SAUDI_ARABIA = "SAU"
    SDN_SUDAN = "SDN"
    SEN_SENEGAL = "SEN"
    SGP_SINGAPORE = "SGP"
    SGS_SOUTH_GEORGIA_AND_THE_SOUTH_SANDWICH_ISLANDS = "SGS"
    SHN_SAINT_HELENA_ASCENSION_AND_TRISTAN_DA_CUNHA = "SHN"
    SJM_SVALBARD_AND_JAN_MAYEN = "SJM"
    SLB_SOLOMON_ISLANDS = "SLB"
    SLE_SIERRA_LEONE = "SLE"
    SLV_EL_SALVADOR = "SLV"
    SMR_SAN_MARINO = "SMR"
    SOM_SOMALIA = "SOM"
    SPM_SAINT_PIERRE_AND_MIQUELON = "SPM"
    SRB_SERBIA = "SRB"
    SSD_SOUTH_SUDAN = "SSD"
    STP_SAO_TOME_AND_PRINCIPE = "STP"
    SUR_SURINAME = "SUR"
    SWZ_SWAZILAND = "SWZ"
    SXM_SINT_MAARTEN_DUTCH_PART = "SXM"
    SYC_SEYCHELLES = "SYC"
    SYR_SYRIAN_ARAB_REPUBLIC = "SYR"
    TCA_TURKS_AND_CAICOS_ISLANDS = "TCA"
    TCD_CHAD = "TCD"
    TGO_TOGO = "TGO"
    THA_THAILAND = "THA"
    TJK_TAJIKISTAN = "TJK"
    TKL_TOKELAU = "TKL"
    TKM_TURKMENISTAN = "TKM"
    TLS_TIMOR_LESTE = "TLS"
    TON_TONGA = "TON"
    TTO_TRINIDAD_AND_TOBAGO = "TTO"
    TUN_TUNISIA = "TUN"
    TUR_TURKEY = "TUR"
    TUV_TUVALU = "TUV"
    TWN_TAIWAN_PROVINCE_OF_CHINA = "TWN"
    TZA_TANZANIA_UNITED_REPUBLIC_OF = "TZA"
    UGA_UGANDA = "UGA"
    UKR_UKRAINE = "UKR"
    UMI_UNITED_STATES_MINOR_OUTLYING_ISLANDS = "UMI"
    URY_URUGUAY = "URY"
    USA_UNITED_STATES_OF_AMERICA = "USA"
    UZB_UZBEKISTAN = "UZB"
    VAT_HOLY_SEE = "VAT"
    VCT_SAINT_VINCENT_AND_THE_GRENADINES = "VCT"
    VEN_VENEZUELA_BOLIVARIAN_REPUBLIC_OF = "VEN"
    VGB_VIRGIN_ISLANDS_BRITISH = "VGB"
    VIR_VIRGIN_ISLANDS_US = "VIR"
    VNM_VIET_NAM = "VNM"
    VUT_VANUATU = "VUT"
    WLF_WALLIS_AND_FUTUNA = "WLF"
    WSM_SAMOA = "WSM"
    YEM_YEMEN = "YEM"
    ZAF_SOUTH_AFRICA = "ZAF"
    ZMB_ZAMBIA = "ZMB"
    ZWE_ZIMBABWE = "ZWE"


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
# (All non-Schengen ISO 3166-1 alpha-3 codes, sorted alphabetically)
_INDIVIDUAL_COUNTRY_INDICATORS: dict[str, FormIndicator] = {
    "ABW": FormIndicator.ABW_ARUBA,
    "AFG": FormIndicator.AFG_AFGHANISTAN,
    "AGO": FormIndicator.AGO_ANGOLA,
    "AIA": FormIndicator.AIA_ANGUILLA,
    "ALA": FormIndicator.ALA_ALAND_ISLANDS,
    "ALB": FormIndicator.ALB_ALBANIA,
    "AND": FormIndicator.AND_ANDORRA,
    "ARE": FormIndicator.ARE_UNITED_ARAB_EMIRATES,
    "ARG": FormIndicator.ARG_ARGENTINA,
    "ARM": FormIndicator.ARM_ARMENIA,
    "ASM": FormIndicator.ASM_AMERICAN_SAMOA,
    "ATA": FormIndicator.ATA_ANTARCTICA,
    "ATF": FormIndicator.ATF_FRENCH_SOUTHERN_TERRITORIES,
    "ATG": FormIndicator.ATG_ANTIGUA_AND_BARBUDA,
    "AUS": FormIndicator.AUS_AUSTRALIA,
    "AZE": FormIndicator.AZE_AZERBAIJAN,
    "BDI": FormIndicator.BDI_BURUNDI,
    "BEN": FormIndicator.BEN_BENIN,
    "BES": FormIndicator.BES_BONAIRE_SINT_EUSTATIUS_AND_SABA,
    "BFA": FormIndicator.BFA_BURKINA_FASO,
    "BGD": FormIndicator.BGD_BANGLADESH,
    "BHR": FormIndicator.BHR_BAHRAIN,
    "BHS": FormIndicator.BHS_BAHAMAS,
    "BIH": FormIndicator.BIH_BOSNIA_AND_HERZEGOVINA,
    "BLM": FormIndicator.BLM_SAINT_BARTHELEMY,
    "BLR": FormIndicator.BLR_BELARUS,
    "BLZ": FormIndicator.BLZ_BELIZE,
    "BMU": FormIndicator.BMU_BERMUDA,
    "BOL": FormIndicator.BOL_BOLIVIA_PLURINATIONAL_STATE_OF,
    "BRA": FormIndicator.BRA_BRAZIL,
    "BRB": FormIndicator.BRB_BARBADOS,
    "BRN": FormIndicator.BRN_BRUNEI_DARUSSALAM,
    "BTN": FormIndicator.BTN_BHUTAN,
    "BVT": FormIndicator.BVT_BOUVET_ISLAND,
    "BWA": FormIndicator.BWA_BOTSWANA,
    "CAF": FormIndicator.CAF_CENTRAL_AFRICAN_REPUBLIC,
    "CAN": FormIndicator.CAN_CANADA,
    "CCK": FormIndicator.CCK_COCOS_KEELING_ISLANDS,
    "CHL": FormIndicator.CHL_CHILE,
    "CHN": FormIndicator.CHN_CHINA,
    "CIV": FormIndicator.CIV_COTE_DIVOIRE,
    "CMR": FormIndicator.CMR_CAMEROON,
    "COD": FormIndicator.COD_CONGO_DEMOCRATIC_REPUBLIC_OF_THE,
    "COG": FormIndicator.COG_CONGO,
    "COK": FormIndicator.COK_COOK_ISLANDS,
    "COL": FormIndicator.COL_COLOMBIA,
    "COM": FormIndicator.COM_COMOROS,
    "CPV": FormIndicator.CPV_CABO_VERDE,
    "CRI": FormIndicator.CRI_COSTA_RICA,
    "CUB": FormIndicator.CUB_CUBA,
    "CUW": FormIndicator.CUW_CURACAO,
    "CXR": FormIndicator.CXR_CHRISTMAS_ISLAND,
    "CYM": FormIndicator.CYM_CAYMAN_ISLANDS,
    "CYP": FormIndicator.CYP_CYPRUS,
    "DJI": FormIndicator.DJI_DJIBOUTI,
    "DMA": FormIndicator.DMA_DOMINICA,
    "DOM": FormIndicator.DOM_DOMINICAN_REPUBLIC,
    "DZA": FormIndicator.DZA_ALGERIA,
    "ECU": FormIndicator.ECU_ECUADOR,
    "EGY": FormIndicator.EGY_EGYPT,
    "ERI": FormIndicator.ERI_ERITREA,
    "ESH": FormIndicator.ESH_WESTERN_SAHARA,
    "ETH": FormIndicator.ETH_ETHIOPIA,
    "FJI": FormIndicator.FJI_FIJI,
    "FLK": FormIndicator.FLK_FALKLAND_ISLANDS_MALVINAS,
    "FRO": FormIndicator.FRO_FAROE_ISLANDS,
    "FSM": FormIndicator.FSM_MICRONESIA_FEDERATED_STATES_OF,
    "GAB": FormIndicator.GAB_GABON,
    "GBR": FormIndicator.GBR_UNITED_KINGDOM,
    "GEO": FormIndicator.GEO_GEORGIA,
    "GGY": FormIndicator.GGY_GUERNSEY,
    "GHA": FormIndicator.GHA_GHANA,
    "GIB": FormIndicator.GIB_GIBRALTAR,
    "GIN": FormIndicator.GIN_GUINEA,
    "GLP": FormIndicator.GLP_GUADELOUPE,
    "GMB": FormIndicator.GMB_GAMBIA,
    "GNB": FormIndicator.GNB_GUINEA_BISSAU,
    "GNQ": FormIndicator.GNQ_EQUATORIAL_GUINEA,
    "GRD": FormIndicator.GRD_GRENADA,
    "GRL": FormIndicator.GRL_GREENLAND,
    "GTM": FormIndicator.GTM_GUATEMALA,
    "GUF": FormIndicator.GUF_FRENCH_GUIANA,
    "GUM": FormIndicator.GUM_GUAM,
    "GUY": FormIndicator.GUY_GUYANA,
    "HKG": FormIndicator.HKG_HONG_KONG,
    "HMD": FormIndicator.HMD_HEARD_ISLAND_AND_MCDONALD_ISLANDS,
    "HND": FormIndicator.HND_HONDURAS,
    "HTI": FormIndicator.HTI_HAITI,
    "IDN": FormIndicator.IDN_INDONESIA,
    "IMN": FormIndicator.IMN_ISLE_OF_MAN,
    "IND": FormIndicator.IND_INDIA,
    "IOT": FormIndicator.IOT_BRITISH_INDIAN_OCEAN_TERRITORY,
    "IRL": FormIndicator.IRL_IRELAND,
    "IRN": FormIndicator.IRN_IRAN_ISLAMIC_REPUBLIC_OF,
    "IRQ": FormIndicator.IRQ_IRAQ,
    "ISR": FormIndicator.ISR_ISRAEL,
    "JAM": FormIndicator.JAM_JAMAICA,
    "JEY": FormIndicator.JEY_JERSEY,
    "JOR": FormIndicator.JOR_JORDAN,
    "JPN": FormIndicator.JPN_JAPAN,
    "KAZ": FormIndicator.KAZ_KAZAKHSTAN,
    "KEN": FormIndicator.KEN_KENYA,
    "KGZ": FormIndicator.KGZ_KYRGYZSTAN,
    "KHM": FormIndicator.KHM_CAMBODIA,
    "KIR": FormIndicator.KIR_KIRIBATI,
    "KNA": FormIndicator.KNA_SAINT_KITTS_AND_NEVIS,
    "KOR": FormIndicator.KOR_KOREA_REPUBLIC_OF,
    "KWT": FormIndicator.KWT_KUWAIT,
    "LAO": FormIndicator.LAO_LAO_PEOPLES_DEMOCRATIC_REPUBLIC,
    "LBN": FormIndicator.LBN_LEBANON,
    "LBR": FormIndicator.LBR_LIBERIA,
    "LBY": FormIndicator.LBY_LIBYA,
    "LCA": FormIndicator.LCA_SAINT_LUCIA,
    "LKA": FormIndicator.LKA_SRI_LANKA,
    "LSO": FormIndicator.LSO_LESOTHO,
    "MAC": FormIndicator.MAC_MACAO,
    "MAF": FormIndicator.MAF_SAINT_MARTIN_FRENCH_PART,
    "MAR": FormIndicator.MAR_MOROCCO,
    "MCO": FormIndicator.MCO_MONACO,
    "MDA": FormIndicator.MDA_MOLDOVA_REPUBLIC_OF,
    "MDG": FormIndicator.MDG_MADAGASCAR,
    "MDV": FormIndicator.MDV_MALDIVES,
    "MEX": FormIndicator.MEX_MEXICO,
    "MHL": FormIndicator.MHL_MARSHALL_ISLANDS,
    "MKD": FormIndicator.MKD_MACEDONIA_THE_FORMER_YUGOSLAV_REPUBLIC_OF,
    "MLI": FormIndicator.MLI_MALI,
    "MMR": FormIndicator.MMR_MYANMAR,
    "MNE": FormIndicator.MNE_MONTENEGRO,
    "MNG": FormIndicator.MNG_MONGOLIA,
    "MNP": FormIndicator.MNP_NORTHERN_MARIANA_ISLANDS,
    "MOZ": FormIndicator.MOZ_MOZAMBIQUE,
    "MRT": FormIndicator.MRT_MAURITANIA,
    "MSR": FormIndicator.MSR_MONTSERRAT,
    "MTQ": FormIndicator.MTQ_MARTINIQUE,
    "MUS": FormIndicator.MUS_MAURITIUS,
    "MWI": FormIndicator.MWI_MALAWI,
    "MYS": FormIndicator.MYS_MALAYSIA,
    "MYT": FormIndicator.MYT_MAYOTTE,
    "NAM": FormIndicator.NAM_NAMIBIA,
    "NCL": FormIndicator.NCL_NEW_CALEDONIA,
    "NER": FormIndicator.NER_NIGER,
    "NFK": FormIndicator.NFK_NORFOLK_ISLAND,
    "NGA": FormIndicator.NGA_NIGERIA,
    "NIC": FormIndicator.NIC_NICARAGUA,
    "NIU": FormIndicator.NIU_NIUE,
    "NPL": FormIndicator.NPL_NEPAL,
    "NRU": FormIndicator.NRU_NAURU,
    "NZL": FormIndicator.NZL_NEW_ZEALAND,
    "OMN": FormIndicator.OMN_OMAN,
    "PAK": FormIndicator.PAK_PAKISTAN,
    "PAN": FormIndicator.PAN_PANAMA,
    "PCN": FormIndicator.PCN_PITCAIRN,
    "PER": FormIndicator.PER_PERU,
    "PHL": FormIndicator.PHL_PHILIPPINES,
    "PLW": FormIndicator.PLW_PALAU,
    "PNG": FormIndicator.PNG_PAPUA_NEW_GUINEA,
    "PRI": FormIndicator.PRI_PUERTO_RICO,
    "PRK": FormIndicator.PRK_KOREA_DEMOCRATIC_PEOPLES_REPUBLIC_OF,
    "PRY": FormIndicator.PRY_PARAGUAY,
    "PSE": FormIndicator.PSE_PALESTINE_STATE_OF,
    "PYF": FormIndicator.PYF_FRENCH_POLYNESIA,
    "QAT": FormIndicator.QAT_QATAR,
    "REU": FormIndicator.REU_REUNION,
    "RUS": FormIndicator.RUS_RUSSIAN_FEDERATION,
    "RWA": FormIndicator.RWA_RWANDA,
    "SAU": FormIndicator.SAU_SAUDI_ARABIA,
    "SDN": FormIndicator.SDN_SUDAN,
    "SEN": FormIndicator.SEN_SENEGAL,
    "SGP": FormIndicator.SGP_SINGAPORE,
    "SGS": FormIndicator.SGS_SOUTH_GEORGIA_AND_THE_SOUTH_SANDWICH_ISLANDS,
    "SHN": FormIndicator.SHN_SAINT_HELENA_ASCENSION_AND_TRISTAN_DA_CUNHA,
    "SJM": FormIndicator.SJM_SVALBARD_AND_JAN_MAYEN,
    "SLB": FormIndicator.SLB_SOLOMON_ISLANDS,
    "SLE": FormIndicator.SLE_SIERRA_LEONE,
    "SLV": FormIndicator.SLV_EL_SALVADOR,
    "SMR": FormIndicator.SMR_SAN_MARINO,
    "SOM": FormIndicator.SOM_SOMALIA,
    "SPM": FormIndicator.SPM_SAINT_PIERRE_AND_MIQUELON,
    "SRB": FormIndicator.SRB_SERBIA,
    "SSD": FormIndicator.SSD_SOUTH_SUDAN,
    "STP": FormIndicator.STP_SAO_TOME_AND_PRINCIPE,
    "SUR": FormIndicator.SUR_SURINAME,
    "SWZ": FormIndicator.SWZ_SWAZILAND,
    "SXM": FormIndicator.SXM_SINT_MAARTEN_DUTCH_PART,
    "SYC": FormIndicator.SYC_SEYCHELLES,
    "SYR": FormIndicator.SYR_SYRIAN_ARAB_REPUBLIC,
    "TCA": FormIndicator.TCA_TURKS_AND_CAICOS_ISLANDS,
    "TCD": FormIndicator.TCD_CHAD,
    "TGO": FormIndicator.TGO_TOGO,
    "THA": FormIndicator.THA_THAILAND,
    "TJK": FormIndicator.TJK_TAJIKISTAN,
    "TKL": FormIndicator.TKL_TOKELAU,
    "TKM": FormIndicator.TKM_TURKMENISTAN,
    "TLS": FormIndicator.TLS_TIMOR_LESTE,
    "TON": FormIndicator.TON_TONGA,
    "TTO": FormIndicator.TTO_TRINIDAD_AND_TOBAGO,
    "TUN": FormIndicator.TUN_TUNISIA,
    "TUR": FormIndicator.TUR_TURKEY,
    "TUV": FormIndicator.TUV_TUVALU,
    "TWN": FormIndicator.TWN_TAIWAN_PROVINCE_OF_CHINA,
    "TZA": FormIndicator.TZA_TANZANIA_UNITED_REPUBLIC_OF,
    "UGA": FormIndicator.UGA_UGANDA,
    "UKR": FormIndicator.UKR_UKRAINE,
    "UMI": FormIndicator.UMI_UNITED_STATES_MINOR_OUTLYING_ISLANDS,
    "URY": FormIndicator.URY_URUGUAY,
    "USA": FormIndicator.USA_UNITED_STATES_OF_AMERICA,
    "UZB": FormIndicator.UZB_UZBEKISTAN,
    "VAT": FormIndicator.VAT_HOLY_SEE,
    "VCT": FormIndicator.VCT_SAINT_VINCENT_AND_THE_GRENADINES,
    "VEN": FormIndicator.VEN_VENEZUELA_BOLIVARIAN_REPUBLIC_OF,
    "VGB": FormIndicator.VGB_VIRGIN_ISLANDS_BRITISH,
    "VIR": FormIndicator.VIR_VIRGIN_ISLANDS_US,
    "VNM": FormIndicator.VNM_VIET_NAM,
    "VUT": FormIndicator.VUT_VANUATU,
    "WLF": FormIndicator.WLF_WALLIS_AND_FUTUNA,
    "WSM": FormIndicator.WSM_SAMOA,
    "YEM": FormIndicator.YEM_YEMEN,
    "ZAF": FormIndicator.ZAF_SOUTH_AFRICA,
    "ZMB": FormIndicator.ZMB_ZAMBIA,
    "ZWE": FormIndicator.ZWE_ZIMBABWE,
}


def get_form_indicator(form_rec: dict | BaseModel) -> FormIndicator | None:
    # If it's a pydantic BaseModel (or similar), convert to dict
    if isinstance(form_rec, BaseModel):
        form_rec = form_rec.model_dump()
    else:
        form_rec = form_rec or {}

    if form_rec is None:
        return None

    # Derive from to_country if indicator is missing
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

    # Individual Country Forms (non-Schengen)
    if code in _INDIVIDUAL_COUNTRY_INDICATORS:
        return _INDIVIDUAL_COUNTRY_INDICATORS[code]

    # Fallback: unknown country type
    return None
