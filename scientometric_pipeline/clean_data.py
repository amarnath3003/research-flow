import pandas as pd
import re
import sys
import os

# Import from root config_loader
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import load_config

cfg = load_config()


def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def remove_duplicates(df):
    if "doi" in df.columns:
        df = df.drop_duplicates(subset=["doi"])
    df = df.drop_duplicates(subset=["title"])
    return df


def filter_irrelevant(df):
    cleaning = cfg["cleaning"]

    if not cleaning.get("enabled", True):
        return df

    hard_exclusions = cleaning.get("hard_exclusions", [])
    core_concepts = cleaning.get("core_concepts", [])
    context_keywords = cleaning.get("context_keywords", [])
    high_priority = cleaning.get("high_priority_concepts", [])
    security_terms = cleaning.get("security_terms", [])

    combined_text = (
        df["title"].fillna("").str.lower() + " " +
        df["abstract"].fillna("").str.lower()
    )

    mask = pd.Series(True, index=df.index)

    for term in hard_exclusions:
        mask &= ~combined_text.str.contains(fr"\b{term}\b", case=False, na=False, regex=True)

    is_high_priority = pd.Series(False, index=df.index)
    for concept in high_priority:
        is_high_priority |= combined_text.str.contains(fr"\b{concept}\b", case=False, na=False, regex=True)

    has_core = pd.Series(False, index=df.index)
    for concept in core_concepts:
        has_core |= combined_text.str.contains(fr"\b{concept}\b", case=False, na=False, regex=True)

    has_context = pd.Series(False, index=df.index)
    for context in context_keywords:
        has_context |= combined_text.str.contains(fr"\b{context}\b", case=False, na=False, regex=True)

    has_security = pd.Series(False, index=df.index)
    for term in security_terms:
        has_security |= combined_text.str.contains(fr"\b{term}\b", case=False, na=False, regex=True)

    relevance_mask = is_high_priority | has_core | (has_security & has_context)
    final_mask = mask & relevance_mask

    return df[final_mask]


def normalize_keywords(df):
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


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, "data", "raw", "openalex_raw.csv")
    output_path = os.path.join(script_dir, "data", "cleaned", "final_dataset.csv")

    if not os.path.exists(input_path):
        print(f"Error: Could not find input file at {input_path}")
        sys.exit(1)

    df = pd.read_csv(input_path)
    print("Original:", len(df))

    df["title"] = df["title"].apply(clean_text)
    df["abstract"] = df["abstract"].apply(clean_text)
    df = remove_duplicates(df)
    print("After dedup:", len(df))

    df = filter_irrelevant(df)
    print("After filtering:", len(df))

    df = normalize_keywords(df)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned dataset to {output_path}")
