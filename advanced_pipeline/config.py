import sys
import os

# Import from root config_loader
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import load_config

cfg = load_config()

EMBEDDING_MODEL = cfg["embedding"]["model"]
LLM_PROVIDER = cfg["llm"]["provider"]
LLM_MODEL = cfg["llm"]["model"]
LLM_API_KEY_ENV = cfg["llm"]["api_key_env"]
LLM_BASE_URL = cfg["llm"]["base_url"]
RESEARCH_TITLE = cfg["research"]["title"]
RESEARCH_DESCRIPTION = cfg["research"]["description"]

DATASET_PATH = "data/cleaned/final_dataset.csv"

MIN_TOPIC_SIZE = cfg["embedding"]["min_topic_size"]
TOP_N_TOPICS = cfg["embedding"]["top_n_topics"]

YEAR_START = cfg["research"]["start_year"]
YEAR_END = cfg["research"]["end_year"]
