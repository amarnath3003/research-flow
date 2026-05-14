"""Data acquisition stage: fetch from OpenAlex, clean, analyze, export."""
import pandas as pd
import requests
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from settings import load, BASE_DIR

cfg = load()
OPENALEX_BASE = "https://api.openalex.org/works"
DATA_DIR = os.path.join(BASE_DIR, "data")


# ── OpenAlex Fetcher ──────────────────────────────────────────────

def fetch_openalex():
    query = " ".join(cfg["research"]["search_query"].split())
    max_results = cfg["research"]["max_results"]
    start = cfg["research"]["start_year"]
    end = cfg["research"]["end_year"]
    email = cfg["research"]["email"]

    print(f"Query: {query}")
    records = []
    cursor = "*"
    per_page = 200

    while True:
        params = {
            "search": query,
            "per-page": per_page,
            "cursor": cursor,
            "mailto": email,
        }
        resp = requests.get(OPENALEX_BASE, params=params, timeout=30)
        if resp.status_code != 200:
            print(f"API Error: {resp.status_code}")
            break
        data = resp.json()
        results = data.get("results", [])
        if not results:
            break
        for item in results:
            year = item.get("publication_year")
            if year and (year < start or year > end):
                continue
            title = item.get("title")
            abstract = ""
            inv_index = item.get("abstract_inverted_index")
            if inv_index:
                words = sorted(
                    [(pos, word) for word, positions in inv_index.items() for pos in positions]
                )
                abstract = " ".join([w for _, w in words])
            authors = []
            for auth in item.get("authorships", []):
                if auth.get("author"):
                    authors.append(auth["author"].get("display_name", ""))
            concepts = [c.get("display_name") for c in item.get("concepts", [])]
            doi = item.get("doi")
            source = ""
            if item.get("primary_location") and item["primary_location"].get("source"):
                source = item["primary_location"]["source"].get("display_name", "")
            records.append({
                "title": title,
                "abstract": abstract,
                "authors": "; ".join(authors),
                "keywords": "; ".join(concepts),
                "year": year,
                "doi": doi,
                "citations": item.get("cited_by_count"),
                "journal": source,
            })
        print(f"Collected: {len(records)}")
        if len(records) >= max_results:
            break
        cursor = data["meta"].get("next_cursor")
        if not cursor:
            break

    df = pd.DataFrame(records)
    raw_dir = os.path.join(DATA_DIR, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    df.to_csv(os.path.join(raw_dir, "openalex_raw.csv"), index=False)
    print(f"Saved {len(df)} records")
    return df


# ── Cleaning ──────────────────────────────────────────────────────

def _clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def _remove_duplicates(df):
    if "doi" in df.columns:
        df = df.drop_duplicates(subset=["doi"])
    return df.drop_duplicates(subset=["title"])


def _filter_relevant(df):
    c = cfg["cleaning"]
    if not c.get("enabled", True):
        return df

    combined = df["title"].fillna("").str.lower() + " " + df["abstract"].fillna("").str.lower()

    mask = pd.Series(True, index=df.index)
    for term in c.get("hard_exclusions", []):
        mask &= ~combined.str.contains(fr"\b{term}\b", case=False, na=False, regex=True)

    is_high = pd.Series(False, index=df.index)
    for concept in c.get("high_priority_concepts", []):
        is_high |= combined.str.contains(fr"\b{concept}\b", case=False, na=False, regex=True)

    has_core = pd.Series(False, index=df.index)
    for concept in c.get("core_concepts", []):
        has_core |= combined.str.contains(fr"\b{concept}\b", case=False, na=False, regex=True)

    has_context = pd.Series(False, index=df.index)
    for kw in c.get("context_keywords", []):
        has_context |= combined.str.contains(fr"\b{kw}\b", case=False, na=False, regex=True)

    has_security = pd.Series(False, index=df.index)
    for term in c.get("security_terms", []):
        has_security |= combined.str.contains(fr"\b{term}\b", case=False, na=False, regex=True)

    return df[mask & (is_high | has_core | (has_security & has_context))]


def _normalize_keywords(df):
    replacements = {
        "open science": "open_science",
        "open access": "open_access",
        "research security": "research_security",
        "cyber security": "cybersecurity",
        "fair": "fair_data",
    }
    normalized = []
    for kws in df["keywords"]:
        if pd.isna(kws):
            normalized.append("")
            continue
        kws = kws.lower()
        for old, new in replacements.items():
            kws = kws.replace(old, new)
        normalized.append(kws)
    df["keywords"] = normalized
    return df


def clean_dataset():
    raw_path = os.path.join(DATA_DIR, "raw", "openalex_raw.csv")
    if not os.path.exists(raw_path):
        print("No raw data found. Run acquisition fetch first.")
        return

    df = pd.read_csv(raw_path)
    print(f"Original: {len(df)}")
    df["title"] = df["title"].apply(_clean_text)
    df["abstract"] = df["abstract"].apply(_clean_text)
    df = _remove_duplicates(df)
    print(f"After dedup: {len(df)}")
    df = _filter_relevant(df)
    print(f"After filtering: {len(df)}")
    df = _normalize_keywords(df)

    cleaned_dir = os.path.join(DATA_DIR, "cleaned")
    os.makedirs(cleaned_dir, exist_ok=True)
    df.to_csv(os.path.join(cleaned_dir, "final_dataset.csv"), index=False)
    print("Saved cleaned dataset")
    return df


# ── Basic Analysis ────────────────────────────────────────────────

def run_basic_analysis():
    df = pd.read_csv(os.path.join(DATA_DIR, "cleaned", "final_dataset.csv"))

    trend = df.groupby("year").size()
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 5))
    plt.plot(trend.index, trend.values, marker='o')
    plt.xlabel("Year")
    plt.ylabel("Publications")
    plt.title("Publication Trend")
    plt.grid(True)
    figs_dir = os.path.join(BASE_DIR, "outputs", "figures")
    os.makedirs(figs_dir, exist_ok=True)
    plt.savefig(os.path.join(figs_dir, "publication_trend.png"))
    plt.close()

    df["journal"].value_counts().head(20).to_csv(
        os.path.join(BASE_DIR, "outputs", "stats", "top_journals.csv")
    )

    all_kw = []
    for kws in df["keywords"]:
        if pd.isna(kws):
            continue
        all_kw.extend(k.strip() for k in kws.split(";"))
    kw_df = pd.DataFrame(Counter(all_kw).items(), columns=["keyword", "count"]).sort_values("count", ascending=False)
    kw_df.to_csv(os.path.join(BASE_DIR, "outputs", "stats", "top_keywords.csv"), index=False)

    print("Basic analysis complete")


# ── VOSviewer Export ──────────────────────────────────────────────

def export_vosviewer():
    df = pd.read_csv(os.path.join(DATA_DIR, "cleaned", "final_dataset.csv"))
    exports_dir = os.path.join(DATA_DIR, "exports")
    os.makedirs(exports_dir, exist_ok=True)
    df[["title", "abstract", "authors", "keywords", "year", "citations"]].to_csv(
        os.path.join(exports_dir, "vosviewer_ready.csv"), index=False
    )
    print("VOSviewer export ready")


# ── Orchestrator ──────────────────────────────────────────────────

def run_all():
    fetch_openalex()
    clean_dataset()
    run_basic_analysis()
    export_vosviewer()
