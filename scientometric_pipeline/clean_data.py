import pandas as pd
import re


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
    """
    Filters out papers to ensure absolute purity for the TRUE TARGET DOMAIN:
    Open Science, Scholarly Communication, Research Security, Integrity, Repositories, etc.
    """
    # 1. HARD EXCLUSIONS (Domains to absolutely remove)
    hard_exclusions = [
        "smart farming", "smart agriculture", "precision farming",
        "smart grid", "power system", "electrical grid",
        "6g", "5g", "vehicular network", "vanet", "cellular network",
        "industrial iot", "iiot", "scada", "factory", "manufacturing security",
        "clinical", "patient data", "hospital security", "medical imaging", 
        "healthcare delivery", "smart city", "smart home", "smart building",
        "blockchain infrastructure", "cryptocurrency", "bitcoin", "ethereum",
        "autonomous vehicle", "self-driving", "uav security",
        "primary education", "k-12", "school children",
        "ecommerce", "marketing ai", "consumer privacy"
    ]

    # 2. CORE CONCEPTS (Target Domains)
    core_concepts = [
        "open science", "open access", "scholarly communication",
        "research security", "academic cybersecurity", "university security",
        "repository", "repositories", "digital library",
        "research integrity", "scientific integrity", "academic integrity",
        "data sharing", "fair data", "open data", "research data management",
        "scientometrics", "bibliometrics", "scholarly publishing",
        "peer review", "preprint", "academic publishing"
    ]

    # 3. CONTEXTUAL REQUIREMENT (Must be related to the research ecosystem)
    context_keywords = [
        "university", "academia", "higher education", "scholarly", 
        "researcher", "faculty", "campus", "academic institution",
        "scientific community", "research organization"
    ]

    # Combined text column
    combined_text = (
        df["title"].fillna("").str.lower() + " " + 
        df["abstract"].fillna("").str.lower()
    )

    mask = pd.Series(True, index=df.index)

    # Apply Hard Exclusions
    for term in hard_exclusions:
        mask &= ~combined_text.str.contains(fr"\b{term}\b", case=False, na=False, regex=True)

    # Apply Target Logic
    # High priority concepts that allow the paper to stay regardless of other context
    high_priority = ["open science", "fair data", "research integrity", "scholarly communication", "repositories"]
    
    is_high_priority = pd.Series(False, index=df.index)
    for concept in high_priority:
        is_high_priority |= combined_text.str.contains(fr"\b{concept}\b", case=False, na=False, regex=True)

    # Core concepts + Context
    has_core = pd.Series(False, index=df.index)
    for concept in core_concepts:
        has_core |= combined_text.str.contains(fr"\b{concept}\b", case=False, na=False, regex=True)

    has_context = pd.Series(False, index=df.index)
    for context in context_keywords:
        has_context |= combined_text.str.contains(fr"\b{context}\b", case=False, na=False, regex=True)

    # Security in academic context
    security_terms = ["security", "cybersecurity", "cyber attack", "ransomware", "threat"]
    has_security = pd.Series(False, index=df.index)
    for term in security_terms:
        has_security |= combined_text.str.contains(fr"\b{term}\b", case=False, na=False, regex=True)

    # Final Relevance Logic:
    # (High Priority) OR (Core Concept) OR (Security AND Academic Context)
    relevance_mask = is_high_priority | has_core | (has_security & has_context)
    
    # Final Mask = Not in hard exclusion AND relevant
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
    import os
    
    # Ensure we can find the data folder relative to this script
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

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Saved cleaned dataset to {output_path}")
