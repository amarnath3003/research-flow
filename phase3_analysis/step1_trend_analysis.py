import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import load_config

cfg = load_config()
RESEARCH_TITLE = cfg["research"]["title"]

INPUT_FILE = "../phase2_validation/final_thematic_dataset.csv"
FALLBACK_FILE = "../advanced_pipeline/data/processed/topic_dataset.csv"
OUTPUT_DIR = "outputs/trends"

def calculate_cagr(start_val, end_val, num_years):
    if start_val == 0 or num_years == 0:
        return 0
    return (pow((end_val / start_val), (1 / num_years)) - 1) * 100

def run_trend_analysis():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if os.path.exists(INPUT_FILE):
        df = pd.read_csv(INPUT_FILE)
        print(f"Loaded curated dataset from {INPUT_FILE}")
    elif os.path.exists(FALLBACK_FILE):
        df = pd.read_csv(FALLBACK_FILE)
        print(f"Loaded fallback dataset from {FALLBACK_FILE}")
    else:
        print("Error: No dataset found.")
        return

    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)

    start = cfg["research"]["start_year"]
    end = cfg["research"]["end_year"]
    df = df[(df['year'] >= start) & (df['year'] <= end)]

    trend = df.groupby('year').size().reset_index(name='count')
    trend = trend.sort_values('year')

    # CAGR
    start_year = trend['year'].min()
    end_year = trend['year'].max()
    start_count = trend[trend['year'] == start_year]['count'].values[0]
    end_count = trend[trend['year'] == end_year]['count'].values[0]
    total_cagr = calculate_cagr(start_count, end_count, end_year - start_year)

    # Dynamic era segmentation: split at midpoint or max growth inflection
    midpoint = (start + end) // 2
    pre = trend[trend['year'] < midpoint]
    post = trend[trend['year'] >= midpoint]

    pre_cagr = 0
    if len(pre) > 1:
        pre_cagr = calculate_cagr(pre['count'].iloc[0], pre['count'].iloc[-1], len(pre) - 1)

    post_cagr = 0
    if len(post) > 1:
        post_cagr = calculate_cagr(post['count'].iloc[0], post['count'].iloc[-1], len(post) - 1)

    # Visualization
    plt.figure(figsize=(12, 6))
    plt.plot(trend['year'], trend['count'], marker='o', linestyle='-', color='#1f77b4', linewidth=2, label='Annual Publications')

    plt.axvline(x=midpoint, color='red', linestyle='--', alpha=0.5, label=f'Mid-Period Boundary ({midpoint})')

    plt.title(f'{RESEARCH_TITLE}: Publication Trends', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Number of Publications', fontsize=12)
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.legend()

    plt.annotate(f'Total CAGR: {total_cagr:.2f}%', xy=(0.05, 0.95), xycoords='axes fraction', fontsize=10, bbox=dict(boxstyle="round", fc="w"))
    plt.annotate(f'Post-{midpoint} CAGR: {post_cagr:.2f}%', xy=(0.05, 0.88), xycoords='axes fraction', fontsize=10, bbox=dict(boxstyle="round", fc="w", ec="red"))

    plot_path = os.path.join(OUTPUT_DIR, 'publication_trend.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {plot_path}")

    stats = {
        'Metric': ['Total Papers', 'Start Year', 'End Year', 'Total CAGR', f'Pre-{midpoint} CAGR', f'Post-{midpoint} CAGR'],
        'Value': [len(df), start_year, end_year, f"{total_cagr:.2f}%", f"{pre_cagr:.2f}%", f"{post_cagr:.2f}%"]
    }
    pd.DataFrame(stats).to_csv(os.path.join(OUTPUT_DIR, 'trend_summary.csv'), index=False)
    trend.to_csv(os.path.join(OUTPUT_DIR, 'yearly_counts.csv'), index=False)
    print("Saved trend stats to CSV.")

if __name__ == "__main__":
    run_trend_analysis()
