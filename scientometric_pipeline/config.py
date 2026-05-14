import sys
import os

# Import from root config_loader
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import load_config

cfg = load_config()

SEARCH_QUERY = cfg["research"]["search_query"]
START_YEAR = cfg["research"]["start_year"]
END_YEAR = cfg["research"]["end_year"]
MAX_RESULTS = cfg["research"]["max_results"]
EMAIL = cfg["research"]["email"]
OPENALEX_BASE = "https://api.openalex.org/works"
