"""Constants for data pipeline."""

# Contiguous US FIPS codes (48 states + DC = 49)
# Excludes: Alaska (02), Hawaii (15), territories
CONTIGUOUS_US_FIPS: list[str] = [
    "01",  # Alabama
    "04",  # Arizona
    "05",  # Arkansas
    "06",  # California
    "08",  # Colorado
    "09",  # Connecticut
    "10",  # Delaware
    "11",  # District of Columbia
    "12",  # Florida
    "13",  # Georgia
    "16",  # Idaho
    "17",  # Illinois
    "18",  # Indiana
    "19",  # Iowa
    "20",  # Kansas
    "21",  # Kentucky
    "22",  # Louisiana
    "23",  # Maine
    "24",  # Maryland
    "25",  # Massachusetts
    "26",  # Michigan
    "27",  # Minnesota
    "28",  # Mississippi
    "29",  # Missouri
    "30",  # Montana
    "31",  # Nebraska
    "32",  # Nevada
    "33",  # New Hampshire
    "34",  # New Jersey
    "35",  # New Mexico
    "36",  # New York
    "37",  # North Carolina
    "38",  # North Dakota
    "39",  # Ohio
    "40",  # Oklahoma
    "41",  # Oregon
    "42",  # Pennsylvania
    "44",  # Rhode Island
    "45",  # South Carolina
    "46",  # South Dakota
    "47",  # Tennessee
    "48",  # Texas
    "49",  # Utah
    "50",  # Vermont
    "51",  # Virginia
    "53",  # Washington
    "54",  # West Virginia
    "55",  # Wisconsin
    "56",  # Wyoming
]

# State FIPS to name mapping (for logging/debugging)
FIPS_TO_STATE: dict[str, str] = {
    "01": "Alabama",
    "04": "Arizona",
    "05": "Arkansas",
    "06": "California",
    "08": "Colorado",
    "09": "Connecticut",
    "10": "Delaware",
    "11": "District of Columbia",
    "12": "Florida",
    "13": "Georgia",
    "16": "Idaho",
    "17": "Illinois",
    "18": "Indiana",
    "19": "Iowa",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "23": "Maine",
    "24": "Maryland",
    "25": "Massachusetts",
    "26": "Michigan",
    "27": "Minnesota",
    "28": "Mississippi",
    "29": "Missouri",
    "30": "Montana",
    "31": "Nebraska",
    "32": "Nevada",
    "33": "New Hampshire",
    "34": "New Jersey",
    "35": "New Mexico",
    "36": "New York",
    "37": "North Carolina",
    "38": "North Dakota",
    "39": "Ohio",
    "40": "Oklahoma",
    "41": "Oregon",
    "42": "Pennsylvania",
    "44": "Rhode Island",
    "45": "South Carolina",
    "46": "South Dakota",
    "47": "Tennessee",
    "48": "Texas",
    "49": "Utah",
    "50": "Vermont",
    "51": "Virginia",
    "53": "Washington",
    "54": "West Virginia",
    "55": "Wisconsin",
    "56": "Wyoming",
}

# Target CRS for all spatial operations (Albers Equal Area for US)
TARGET_CRS = "EPSG:5070"

# Coordinate quantization grid size (1cm for meters-based CRS)
QUANTIZATION_GRID_SIZE = 0.01
