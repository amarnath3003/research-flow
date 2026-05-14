import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import load_config

cfg = load_config()
RESEARCH_TITLE = cfg["research"]["title"]
ANNOTATIONS = cfg["visualizations"].get("annotations", {})

DATASET_FILE = "../advanced_pipeline/data/processed/topic_dataset.csv"
OUTPUT_DIR = "outputs"

def run_growth_timeline():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_csv(DATASET_FILE)
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['year'])
    counts = df.groupby('year').size().reset_index(name='count')

    start = cfg["research"]["start_year"]
    end = cfg["research"]["end_year"]
    counts = counts[(counts['year'] >= start) & (counts['year'] <= end)]

    plt.figure(figsize=(12, 6))
    plt.plot(counts['year'], counts['count'], marker='o', color='#1f77b4', linewidth=3, markersize=8, label='Annual Publications')
    plt.fill_between(counts['year'], counts['count'], color='#1f77b4', alpha=0.1)

    # Annotations: use custom from config, or auto-detect highest growth spike
    custom_anns = ANNOTATIONS.get("custom", []) if ANNOTATIONS.get("enabled", True) else []
    if custom_anns:
        for ann in custom_anns:
            year = ann["year"]
            label = ann["label"]
            if year in counts['year'].values:
                plt.axvline(x=year, color='#d62728', linestyle='--', alpha=0.7)
                y_val = counts[counts['year'] == year]['count'].values[0]
                plt.text(year + 0.2, y_val + counts['count'].max() * 0.02,
                         label, color='#d62728', fontweight='bold', fontsize=9)
    else:
        # Auto-detect: find year with highest year-over-year growth
        counts['yoy_growth'] = counts['count'].diff()
        if not counts['yoy_growth'].isna().all():
            peak_idx = counts['yoy_growth'].idxmax()
            peak_year = counts.loc[peak_idx, 'year']
            peak_growth = counts.loc[peak_idx, 'yoy_growth']
            if peak_growth > 0:
                plt.axvline(x=peak_year, color='#d62728', linestyle='--', alpha=0.7)
                y_val = counts.loc[peak_idx, 'count']
                plt.text(peak_year + 0.2, y_val + counts['count'].max() * 0.02,
                         f'Highest Growth ({int(peak_growth)} pubs)',
                         color='#d62728', fontweight='bold', fontsize=9)

    plt.title(f'Figure 1: Publication Growth Timeline ({start}-{end})', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Number of Publications', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.xticks(range(start, end + 1, max(1, (end - start) // 5)))
    plt.ylim(0, counts['count'].max() * 1.3)
    plt.legend()

    plot_path = os.path.join(OUTPUT_DIR, 'figure1_growth_timeline.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Generated Figure 1: {plot_path}")

if __name__ == "__main__":
    run_growth_timeline()
