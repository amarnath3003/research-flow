import pandas as pd
import numpy as np
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import load_config

cfg = load_config()
START_YEAR = cfg["research"]["start_year"]
END_YEAR = cfg["research"]["end_year"]
RECENT_THRESHOLD = END_YEAR - 3  # last 3 years of the range

INPUT_FILE = "../phase2_validation/final_thematic_dataset.csv"
FALLBACK_FILE = "../advanced_pipeline/data/processed/topic_dataset.csv"
OUTPUT_DIR = "outputs/bursts"

def run_burst_detection():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if os.path.exists(INPUT_FILE):
        df = pd.read_csv(INPUT_FILE)
    elif os.path.exists(FALLBACK_FILE):
        df = pd.read_csv(FALLBACK_FILE)
    else:
        print("Error: No dataset found.")
        return

    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)

    def get_keywords(k):
        if not isinstance(k, str): return []
        return [x.strip().lower() for x in k.replace(';', ',').split(',') if x.strip()]

    df['kw_list'] = df['keywords'].apply(get_keywords)

    kw_year_counts = []
    for year in sorted(df['year'].unique()):
        year_df = df[df['year'] == year]
        all_kw = [kw for sublist in year_df['kw_list'] for kw in sublist]
        counts = Counter(all_kw)
        for kw, count in counts.items():
            kw_year_counts.append({'year': year, 'keyword': kw, 'count': count})

    kw_df = pd.DataFrame(kw_year_counts)
    pivot_df = kw_df.pivot(index='year', columns='keyword', values='count').fillna(0)

    bursts = []
    top_kw = pivot_df.sum().sort_values(ascending=False).head(200).index

    for kw in top_kw:
        series = pivot_df[kw]
        mean = series.mean()
        std = series.std()
        if std == 0:
            continue
        for year, val in series.items():
            z_score = (val - mean) / std
            if z_score > 2.5 and val > 5:
                bursts.append({
                    'keyword': kw,
                    'burst_year': year,
                    'count': val,
                    'z_score': round(z_score, 2)
                })

    burst_df = pd.DataFrame(bursts).sort_values(['burst_year', 'z_score'], ascending=[True, False])
    burst_df.to_csv(os.path.join(OUTPUT_DIR, 'burst_detection.csv'), index=False)

    print(f"Burst detection complete. Identified {len(burst_df)} bursts.")
    print(f"Top recent bursts ({RECENT_THRESHOLD}-{END_YEAR}):")
    recent = burst_df[burst_df['burst_year'] >= RECENT_THRESHOLD].head(15)
    print(recent)

if __name__ == "__main__":
    run_burst_detection()
