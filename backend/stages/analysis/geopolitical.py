"""Geopolitical analysis: country-level collaboration patterns."""
import pandas as pd
import os
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import load, BASE_DIR

cfg = load()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

COUNTRY_PATTERNS = [
    (r"\bUSA\b", "USA"), (r"\bUnited States\b", "USA"), (r"\bChina\b", "China"),
    (r"\bUK\b", "UK"), (r"\bUnited Kingdom\b", "UK"), (r"\bGermany\b", "Germany"),
    (r"\bIndia\b", "India"), (r"\bCanada\b", "Canada"), (r"\bAustralia\b", "Australia"),
    (r"\bFrance\b", "France"), (r"\bItaly\b", "Italy"), (r"\bJapan\b", "Japan"),
    (r"\bSpain\b", "Spain"), (r"\bSouth Korea\b", "South Korea"), (r"\bBrazil\b", "Brazil"),
    (r"\bNetherlands\b", "Netherlands"), (r"\bSwitzerland\b", "Switzerland"),
    (r"\bSweden\b", "Sweden"), (r"\bSingapore\b", "Singapore"), (r"\bRussia\b", "Russia"),
]


def run():
    df = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "final_thematic_dataset.csv"))

    def extract_countries(authors_str):
        if pd.isna(authors_str):
            return []
        found = set()
        for pattern, country in COUNTRY_PATTERNS:
            if re.search(pattern, authors_str, re.IGNORECASE):
                found.add(country)
        return list(found)

    df["countries"] = df["authors"].apply(extract_countries)

    records = []
    for _, row in df.iterrows():
        for country in row["countries"]:
            records.append({"country": country, "paper": row.get("doi", row["title"])})

    if not records:
        print("No countries extracted.")
        return

    country_df = pd.DataFrame(records)
    stats = country_df.groupby("country").agg(
        Total=("paper", "nunique"),
    ).reset_index().sort_values("Total", ascending=False)

    # MCP/SCP: papers with >1 country = MCP
    paper_countries = country_df.groupby("paper")["country"].apply(set).reset_index()
    paper_countries["type"] = paper_countries["country"].apply(lambda c: "MCP" if len(c) > 1 else "SCP")
    merged = paper_countries.explode("country").rename(columns={"country": "country_name"})
    collab = merged.groupby("country_name")["type"].value_counts().unstack(fill_value=0).reset_index()
    collab.columns.name = None
    for col in ["SCP", "MCP"]:
        if col not in collab.columns:
            collab[col] = 0
    collab["Total"] = collab["SCP"] + collab["MCP"]
    collab = collab.sort_values("Total", ascending=False)
    collab.to_csv(os.path.join(OUTPUTS_DIR, "geopolitical", "country_collaboration.csv"), index=False)
    print("Geopolitical analysis complete")
