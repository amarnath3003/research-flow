import pandas as pd
import os
from collections import Counter
from itertools import combinations

# Configuration
INPUT_FILE = "../phase2_validation/final_thematic_dataset.csv"
FALLBACK_FILE = "../advanced_pipeline/data/processed/topic_dataset.csv"
OUTPUT_DIR = "outputs/networks"

def run_network_analysis():
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

    # 1. Keyword Co-occurrence
    print("Analyzing keyword co-occurrence...")
    df['keywords'] = df['keywords'].fillna('').str.lower()
    
    def split_keywords(k):
        if ';' in k:
            return [x.strip() for x in k.split(';') if x.strip()]
        return [x.strip() for x in k.split(',') if x.strip()]

    keyword_lists = df['keywords'].apply(split_keywords).tolist()
    
    pair_counts = Counter()
    for k_list in keyword_lists:
        if len(k_list) < 2: continue
        pairs = combinations(sorted(set(k_list)), 2)
        pair_counts.update(pairs)

    network_df = pd.DataFrame([
        {'Source': p[0], 'Target': p[1], 'Weight': count}
        for p, count in pair_counts.items() if count > 2
    ])
    network_df.to_csv(os.path.join(OUTPUT_DIR, 'keyword_cooccurrence_edges.csv'), index=False)

    # 2. Co-authorship Network
    print("Analyzing co-authorship...")
    df['authors'] = df['authors'].fillna('')
    author_lists = df['authors'].apply(lambda x: [a.strip() for a in x.split(';') if a.strip()]).tolist()
    
    author_pair_counts = Counter()
    for a_list in author_lists:
        if len(a_list) < 2: continue
        pairs = combinations(sorted(set(a_list)), 2)
        author_pair_counts.update(pairs)

    author_network_df = pd.DataFrame([
        {'Source': p[0], 'Target': p[1], 'Weight': count}
        for p, count in author_pair_counts.items() if count > 1
    ])
    author_network_df.to_csv(os.path.join(OUTPUT_DIR, 'coauthorship_edges.csv'), index=False)

    # 3. Node lists
    all_keywords = [item for sublist in keyword_lists for item in sublist]
    pd.DataFrame(Counter(all_keywords).items(), columns=['Id', 'Frequency']).to_csv(os.path.join(OUTPUT_DIR, 'keyword_nodes.csv'), index=False)

    all_authors = [item for sublist in author_lists for item in sublist]
    pd.DataFrame(Counter(all_authors).items(), columns=['Id', 'Frequency']).to_csv(os.path.join(OUTPUT_DIR, 'author_nodes.csv'), index=False)

    print(f"Network analysis complete. Files saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    run_network_analysis()
