import os
import yaml
import threading

_lock = threading.Lock()
_cached = None
_config_path = None

# Allow override via env var for project-scoped execution
BASE_DIR = os.environ.get("PROJECT_DIR") or os.path.dirname(os.path.abspath(__file__))


def find_config():
    candidates = [
        os.environ.get("RESEARCH_CONFIG"),
        os.path.join(BASE_DIR, "research_config.yaml"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def load(path=None):
    global _cached, _config_path
    if _cached is not None and not path:
        return _cached
    with _lock:
        if _cached is not None and not path:
            return _cached
        resolved = path or _config_path or find_config()
        if not resolved:
            raise FileNotFoundError(
                "No research_config.yaml found. "
                "Place it in the backend/ directory or set RESEARCH_CONFIG env var."
            )
        with open(resolved, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        _normalize(cfg)
        _cached = cfg
        _config_path = resolved
        return cfg


def _normalize(cfg):
    r = cfg.setdefault("research", {})
    r.setdefault("title", "Untitled Research")
    r.setdefault("description", "")
    r.setdefault("search_query", "")
    r.setdefault("start_year", 2010)
    r.setdefault("end_year", 2025)
    r.setdefault("max_results", 5000)
    r.setdefault("email", "user@example.com")

    c = cfg.setdefault("cleaning", {})
    c.setdefault("enabled", True)
    c.setdefault("hard_exclusions", [])
    c.setdefault("core_concepts", [])
    c.setdefault("context_keywords", [])
    c.setdefault("high_priority_concepts", [])
    c.setdefault("security_terms", ["security", "cybersecurity", "threat"])

    e = cfg.setdefault("embedding", {})
    e.setdefault("model", "all-MiniLM-L6-v2")
    e.setdefault("min_topic_size", 10)
    e.setdefault("top_n_topics", 20)

    llm = cfg.setdefault("llm", {})
    llm.setdefault("provider", None)
    llm.setdefault("model", None)
    llm.setdefault("api_key_env", None)
    llm.setdefault("base_url", None)

    t = cfg.setdefault("tracking", {})
    t.setdefault("themes", [])

    v = cfg.setdefault("visualizations", {})
    v.setdefault("annotations", {"enabled": True, "custom": []})


def clear_cache():
    global _cached, _config_path
    with _lock:
        _cached = None
        _config_path = None
