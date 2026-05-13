import requests
import pandas as pd
from tqdm import tqdm
from config import *


class OpenAlexFetcher:

    def __init__(self):
        self.base_url = OPENALEX_BASE

    def fetch(self, query, per_page=200, max_results=5000):

        # Clean up query string (remove newlines and extra spaces)
        query = " ".join(query.split())
        print(f"Normalized Query: {query}")

        records = []
        cursor = "*"

        while True:

            params = {
                "search": query,
                "per-page": per_page,
                "cursor": cursor,
                "mailto": EMAIL,
            }

            print(f"Fetching from {self.base_url} with cursor {cursor}...")
            response = requests.get(self.base_url, params=params, timeout=30)

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

    df = fetcher.fetch(SEARCH_QUERY, max_results=MAX_RESULTS)

    df.to_csv("data/raw/openalex_raw.csv", index=False)

    print(df.head())
    print("Saved raw dataset")
