"""Central configuration for Half of America."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root (relative to this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
RAW_DIR = CACHE_DIR / "raw"
TIGER_DIR = RAW_DIR / "tiger"
CENSUS_DIR = RAW_DIR / "census"
PROCESSED_DIR = CACHE_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "output"
TOPOJSON_DIR = OUTPUT_DIR / "topojson"

# Census API configuration
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")

# Data year configuration (locked versions)
TIGER_YEAR = 2024
ACS_YEAR = 2022
