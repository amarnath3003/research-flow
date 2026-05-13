import pandas as pd
import os

# Configuration
INPUT_FILE = "../phase2_validation/final_thematic_dataset.csv"
FALLBACK_FILE = "../advanced_pipeline/data/processed/topic_dataset.csv"
OUTPUT_DIR = "outputs/sources"

def calculate_h_index(citations):
    """Calculates h-index for a list of citations."""
    citations = sorted(citations, reverse=True)
    h = 0
    for i, c in enumerate(citations):
        if c >= i + 1:
            h = i + 1
        else:
            break
    return h

def run_source_analysis():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load data
    if os.path.exists(INPUT_FILE):
        df = pd.read_csv(INPUT_FILE)
        print(f"Loaded curated dataset from {INPUT_FILE}")
    elif os.path.exists(FALLBACK_FILE):
        df = pd.read_csv(FALLBACK_FILE)
        print(f"Loaded fallback dataset from {FALLBACK_FILE}")
    else:
        print("Error: No dataset found.")
        return

    # Clean citations and journal
    df['citations'] = pd.to_numeric(df['citations'], errors='coerce').fillna(0)
    df['journal'] = df['journal'].fillna('Unknown Source').str.strip()

    # Aggregate by Source
    source_stats = df.groupby('journal').agg(
        paper_count=('title', 'count'),
        total_citations=('citations', 'sum'),
        avg_citations=('citations', 'mean')
    ).reset_index()

    # Calculate Source H-index
    h_indices = []
    for journal in source_stats['journal']:
        journal_citations = df[df['journal'] == journal]['citations'].tolist()
        h_indices.append(calculate_h_index(journal_citations))
    
    source_stats['h_index'] = h_indices

    # Sort by influence (H-index then count)
    source_stats = source_stats.sort_values(['h_index', 'paper_count'], ascending=False)

    # Save Top 50 Sources
    top_sources = source_stats.head(50)
    top_sources.to_csv(os.path.join(OUTPUT_DIR, 'top_sources.csv'), index=False)
    
    print(f"Top 10 Sources by H-Index:")
    print(top_sources[['journal', 'paper_count', 'total_citations', 'h_index']].head(10))
    print(f"\nFull report saved to {OUTPUT_DIR}/top_sources.csv")

if __name__ == "__main__":
    run_source_analysis()
