"""GDELT's ActionGeo country codes are FIPS 10-4, but map data uses ISO-3166 alpha-3.
This maps the ~130 most common FIPS codes to ISO3. Unmapped codes are skipped."""

FIPS_TO_ISO3 = {
    # Europe
    "UK": "GBR", "FR": "FRA", "GM": "DEU", "IT": "ITA", "SP": "ESP", "PO": "PRT",
    "NL": "NLD", "BE": "BEL", "SZ": "CHE", "AU": "AUT", "EI": "IRL", "DA": "DNK",
    "NO": "NOR", "SW": "SWE", "FI": "FIN", "IC": "ISL", "PL": "POL", "EZ": "CZE",
    "LO": "SVK", "HU": "HUN", "RO": "ROU", "BU": "BGR", "GR": "GRC", "HR": "HRV",
    "RI": "SRB", "BK": "BIH", "MK": "MKD", "AL": "ALB", "SI": "SVN", "MJ": "MNE",
    "EN": "EST", "LG": "LVA", "LH": "LTU", "BO": "BLR", "MD": "MDA", "UP": "UKR",
    "RS": "RUS", "LU": "LUX", "MT": "MLT", "CY": "CYP", "KV": "XKX",
    # Middle East
    "TU": "TUR", "SY": "SYR", "LE": "LBN", "IS": "ISR", "JO": "JOR", "IZ": "IRQ",
    "IR": "IRN", "SA": "SAU", "AE": "ARE", "QA": "QAT", "KU": "KWT", "BA": "BHR",
    "MU": "OMN", "YM": "YEM", "WE": "PSE", "GZ": "PSE",
    # Asia
    "CH": "CHN", "JA": "JPN", "KS": "KOR", "KN": "PRK", "TW": "TWN", "HK": "HKG",
    "MG": "MNG", "IN": "IND", "PK": "PAK", "AF": "AFG", "BG": "BGD", "CE": "LKA",
    "NP": "NPL", "BT": "BTN", "BM": "MMR", "TH": "THA", "VM": "VNM", "CB": "KHM",
    "LA": "LAO", "ID": "IDN", "MY": "MYS", "RP": "PHL", "SN": "SGP", "BX": "BRN",
    "KZ": "KAZ", "KG": "KGZ", "TI": "TJK", "TX": "TKM", "UZ": "UZB",
    "AM": "ARM", "AJ": "AZE", "GG": "GEO",
    # Africa
    "EG": "EGY", "LY": "LBY", "TS": "TUN", "AG": "DZA", "MO": "MAR", "SU": "SDN",
    "OD": "SSD", "ET": "ETH", "ER": "ERI", "DJ": "DJI", "SO": "SOM", "KE": "KEN",
    "UG": "UGA", "TZ": "TZA", "RW": "RWA", "BY": "BDI", "CG": "COD", "CF": "COG",
    "CM": "CMR", "CT": "CAF", "CD": "TCD", "NI": "NGA", "NG": "NER", "ML": "MLI",
    "MR": "MRT", "SG": "SEN", "GV": "GIN", "IV": "CIV", "GH": "GHA", "TO": "TGO",
    "BN": "BEN", "UV": "BFA", "LI": "LBR", "SL": "SLE", "GA": "GMB", "PU": "GNB",
    "MZ": "MOZ", "ZI": "ZWE", "ZA": "ZMB", "MW": "MWI", "AO": "AGO", "WA": "NAM",
    "BC": "BWA", "SF": "ZAF", "WZ": "SWZ", "LT": "LSO", "MA": "MDG", "GB": "GAB",
    "EK": "GNQ",
    # Americas
    "US": "USA", "CA": "CAN", "MX": "MEX", "GT": "GTM", "HO": "HND", "ES": "SLV",
    "NU": "NIC", "CS": "CRI", "PM": "PAN", "CU": "CUB", "HA": "HTI", "DR": "DOM",
    "JM": "JAM", "TD": "TTO", "VE": "VEN", "CO": "COL", "EC": "ECU", "PE": "PER",
    "BL": "BOL", "CI": "CHL", "AR": "ARG", "UY": "URY", "PA": "PRY", "BR": "BRA",
    "GY": "GUY", "NS": "SUR",
    # Oceania
    "AS": "AUS", "NZ": "NZL", "PP": "PNG", "FJ": "FJI",
}
