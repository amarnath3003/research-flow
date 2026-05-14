import os
import yaml
import threading

_lock = threading.Lock()
_cached = None
_CONFIG_PATH = None

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "research_config.yaml")


def _find_config():
    candidates = [
        os.environ.get("RESEARCH_CONFIG"),
        DEFAULT_PATH,
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def set_config_path(path):
    global _CONFIG_PATH, _cached
    with _lock:
        _CONFIG_PATH = path
        _cached = None


def load_config(path=None):
    global _CONFIG_PATH, _cached

    if path:
        set_config_path(path)

    if _cached is not None:
        return _cached

    with _lock:
        if _cached is not None:
            return _cached

        resolved = path or _CONFIG_PATH or _find_config()
        if not resolved:
            raise FileNotFoundError(
                "No research_config.yaml found. "
                "Set RESEARCH_CONFIG env var, place it at the project root, "
                "or pass a path to load_config()."
            )

        with open(resolved, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        _normalize(cfg)
        _cached = cfg
        _CONFIG_PATH = resolved
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
