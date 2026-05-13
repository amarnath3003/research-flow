import pandas as pd
import os
from collections import Counter

# Configuration
INPUT_FILE = "../phase2_validation/final_thematic_dataset.csv"
FALLBACK_FILE = "../advanced_pipeline/data/processed/topic_dataset.csv"
OUTPUT_DIR = "outputs/authors"

def run_author_analysis():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load data
    if os.path.exists(INPUT_FILE):
        df = pd.read_csv(INPUT_FILE)
    elif os.path.exists(FALLBACK_FILE):
        df = pd.read_csv(FALLBACK_FILE)
    else:
        print("Error: No dataset found.")
        return

    # Clean data
    df['authors'] = df['authors'].fillna('')
    df['citations'] = pd.to_numeric(df['citations'], errors='coerce').fillna(0)
    
    # Split authors
    author_rows = []
    for _, row in df.iterrows():
        authors = [a.strip() for a in row['authors'].split(';') if a.strip()]
        for author in authors:
            author_rows.append({'author': author, 'citations': row['citations']})

    author_df = pd.DataFrame(author_rows)
    
    # Aggregate stats
    author_stats = author_df.groupby('author').agg(
        paper_count=('citations', 'count'),
        total_citations=('citations', 'sum'),
        avg_citations=('citations', 'mean')
    ).reset_index()

    author_stats = author_stats.sort_values('total_citations', ascending=False)

    # Save results
    author_stats.to_csv(os.path.join(OUTPUT_DIR, 'top_authors.csv'), index=False)
    
    print(f"Top 10 Authors by Citations:")
    print(author_stats.head(10))
    print(f"\nReport saved to {OUTPUT_DIR}/top_authors.csv")

if __name__ == "__main__":
    run_author_analysis()
