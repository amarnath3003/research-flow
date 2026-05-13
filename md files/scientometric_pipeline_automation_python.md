# Automated Scientometric Research Pipeline

## Overview

This pipeline automates:

1. Querying academic databases
2. Fetching metadata
3. Merging datasets
4. Cleaning and deduplication
5. Keyword normalization
6. Dataset generation
7. Basic scientometric statistics
8. Exporting files for VOSviewer/Bibliometrix

---

# IMPORTANT LIMITATIONS

## Scopus and Web of Science Access

Both databases are commercial.

You need:
- institutional access
- API key
- VPN/library access

## Recommended APIs

### Scopus
Use Elsevier API:
https://dev.elsevier.com/

### Crossref (Free)
https://api.crossref.org

### OpenAlex (Free and VERY GOOD)
https://openalex.org

### Semantic Scholar (Optional)
https://www.semanticscholar.org/product/api

---

# Recommended Approach

Use:

- OpenAlex for massive metadata collection
- Crossref for enrichment
- Optional Scopus API if available

This avoids institutional/API limitations.

---

# PROJECT STRUCTURE

```text
scientometric_pipeline/
│
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── exports/
│
├── outputs/
│   ├── figures/
│   └── stats/
│
├── config.py
├── fetch_data.py
├── clean_data.py
├── analyze_data.py
├── export_vosviewer.py
└── main.py
```

---

# INSTALLATION

```bash
pip install pandas requests tqdm matplotlib networkx scikit-learn nltk openpyxl pybliometrics
```

Optional:

```bash
pip install pyalex
```

---

# config.py

```python
SEARCH_QUERY = (
    'open science OR open access OR FAIR OR open data '
    'AND cybersecurity OR research security OR ransomware'
)

START_YEAR = 2010
END_YEAR = 2025

MAX_RESULTS = 5000

EMAIL = "your_email@example.com"

OPENALEX_BASE = "https://api.openalex.org/works"
```

---

# fetch_data.py

```python
import requests
import pandas as pd
from tqdm import tqdm
from config import *


class OpenAlexFetcher:

    def __init__(self):
        self.base_url = OPENALEX_BASE

    def fetch(self, query, per_page=200, max_results=5000):

        records = []
        cursor = "*"

        while True:

            params = {
                "search": query,
                "per-page": per_page,
                "cursor": cursor,
                "mailto": EMAIL,
            }

            response = requests.get(self.base_url, params=params)

            if response.status_code != 200:
                print("API Error:", response.status_code)
                break

            data = response.json()

            results = data.get("results", [])

            if not results:
                break

            for item in results:

                year = item.get("publication_year")

                if year:
                    if year < START_YEAR or year > END_YEAR:
                        continue

                title = item.get("title")

                abstract = ""
                abstract_index = item.get("abstract_inverted_index")

                if abstract_index:
                    words = sorted(
                        [(pos, word)
                         for word, positions in abstract_index.items()
                         for pos in positions]
                    )

                    abstract = " ".join([word for pos, word in words])

                authors = []
                for auth in item.get("authorships", []):
                    if auth.get("author"):
                        authors.append(auth["author"].get("display_name", ""))

                concepts = [
                    c.get("display_name")
                    for c in item.get("concepts", [])
                ]

                doi = item.get("doi")
                cited_by = item.get("cited_by_count")

                source = ""
                if item.get("primary_location"):
                    source_data = item["primary_location"].get("source")
                    if source_data:
                        source = source_data.get("display_name", "")

                records.append({
                    "title": title,
                    "abstract": abstract,
                    "authors": "; ".join(authors),
                    "keywords": "; ".join(concepts),
                    "year": year,
                    "doi": doi,
                    "citations": cited_by,
                    "journal": source,
                })

            print(f"Collected: {len(records)}")

            if len(records) >= max_results:
                break

            cursor = data["meta"].get("next_cursor")

            if not cursor:
                break

        return pd.DataFrame(records)


if __name__ == "__main__":

    fetcher = OpenAlexFetcher()

    df = fetcher.fetch(SEARCH_QUERY)

    df.to_csv("data/raw/openalex_raw.csv", index=False)

    print(df.head())
    print("Saved raw dataset")
```

---

# clean_data.py

```python
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

    exclude_terms = [
        "blockchain finance",
        "cryptocurrency",
        "industrial control",
        "supply chain",
    ]

    mask = []

    for _, row in df.iterrows():

        text = (
            str(row.get("title", "")) + " " +
            str(row.get("abstract", ""))
        ).lower()

        bad = any(term in text for term in exclude_terms)

        mask.append(not bad)

    return df[mask]


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

    df = pd.read_csv("data/raw/openalex_raw.csv")

    print("Original:", len(df))

    df["title"] = df["title"].apply(clean_text)
    df["abstract"] = df["abstract"].apply(clean_text)

    df = remove_duplicates(df)

    print("After dedup:", len(df))

    df = filter_irrelevant(df)

    print("After filtering:", len(df))

    df = normalize_keywords(df)

    df.to_csv("data/cleaned/final_dataset.csv", index=False)

    print("Saved cleaned dataset")
```

---

# analyze_data.py

```python
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter


df = pd.read_csv("data/cleaned/final_dataset.csv")


# PUBLICATION TREND
trend = df.groupby("year").size()

plt.figure(figsize=(10, 5))
plt.plot(trend.index, trend.values)
plt.xlabel("Year")
plt.ylabel("Publications")
plt.title("Publication Trend")

plt.savefig("outputs/figures/publication_trend.png")


# TOP JOURNALS
journal_counts = df["journal"].value_counts().head(20)

journal_counts.to_csv("outputs/stats/top_journals.csv")


# TOP KEYWORDS
all_keywords = []

for kws in df["keywords"]:

    if pd.isna(kws):
        continue

    split_kws = [k.strip() for k in kws.split(";")]

    all_keywords.extend(split_kws)

keyword_counts = Counter(all_keywords)

keywords_df = pd.DataFrame(
    keyword_counts.items(),
    columns=["keyword", "count"]
)

keywords_df = keywords_df.sort_values(
    by="count",
    ascending=False
)

keywords_df.to_csv(
    "outputs/stats/top_keywords.csv",
    index=False
)


print("Analysis complete")
```

---

# export_vosviewer.py

```python
import pandas as pd


# VOSviewer likes CSV with:
# title, abstract, keywords, authors


df = pd.read_csv("data/cleaned/final_dataset.csv")

vos_df = df[[
    "title",
    "abstract",
    "authors",
    "keywords",
    "year",
    "citations"
]]

vos_df.to_csv(
    "data/exports/vosviewer_ready.csv",
    index=False
)

print("VOSviewer export ready")
```

---

# main.py

```python
import os


folders = [
    "data/raw",
    "data/cleaned",
    "data/exports",
    "outputs/figures",
    "outputs/stats",
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)


print("STEP 1 - FETCHING")
os.system("python fetch_data.py")

print("STEP 2 - CLEANING")
os.system("python clean_data.py")

print("STEP 3 - ANALYSIS")
os.system("python analyze_data.py")

print("STEP 4 - EXPORT")
os.system("python export_vosviewer.py")

print("PIPELINE COMPLETE")
```

---

# HOW TO RUN

```bash
python main.py
```

---

# OUTPUTS GENERATED

The pipeline generates:

## Dataset Files

```text
final_dataset.csv
vosviewer_ready.csv
```

## Statistics

```text
top_keywords.csv
top_journals.csv
```

## Figures

```text
publication_trend.png
```

---

# USING WITH VOSVIEWER

Open:

```text
vosviewer_ready.csv
```

Then:

```text
Create Map → Co-occurrence → Author Keywords
```

You can also create:
- citation networks
- co-authorship networks
- country collaboration maps

---

# NEXT LEVEL IMPROVEMENTS

You can later add:

## Advanced NLP

- BERTopic
- LDA topic modeling
- transformer embeddings
- semantic clustering

## Citation Graphs

- networkx
- graph neural networks

## Temporal Evolution

- burst detection
- timeline visualization

## Automated Paper Generation

- auto tables
- APA references
- LaTeX export

---

# RECOMMENDED NEXT STEP

After running the pipeline:

1. Inspect dataset quality manually
2. Refine queries
3. Re-run collection
4. Generate VOSviewer maps
5. Begin interpretation

The quality of the paper depends MOSTLY on:
- dataset quality
- cleaning quality
- interpretation quality

NOT on the code itself.

