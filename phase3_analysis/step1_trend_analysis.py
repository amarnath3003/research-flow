import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Configuration
INPUT_FILE = "../phase2_validation/final_thematic_dataset.csv"
FALLBACK_FILE = "../advanced_pipeline/data/processed/topic_dataset.csv"
OUTPUT_DIR = "outputs/trends"

def calculate_cagr(start_val, end_val, num_years):
    if start_val == 0 or num_years == 0:
        return 0
    return (pow((end_val / start_val), (1 / num_years)) - 1) * 100

def run_trend_analysis():
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

    # Clean year column
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)

    # Filter to a reasonable range (e.g., 2010-2024)
    df = df[(df['year'] >= 2010) & (df['year'] <= 2024)]

    # 1. Publication Trend
    trend = df.groupby('year').size().reset_index(name='count')
    trend = trend.sort_values('year')

    # 2. CAGR Calculation
    start_year = trend['year'].min()
    end_year = trend['year'].max()
    start_count = trend[trend['year'] == start_year]['count'].values[0]
    end_count = trend[trend['year'] == end_year]['count'].values[0]
    total_cagr = calculate_cagr(start_count, end_count, end_year - start_year)

    # 3. Era Segmentation (Pre-2020 vs Post-2020)
    pre_2020 = trend[trend['year'] < 2020]
    post_2020 = trend[trend['year'] >= 2020]

    pre_cagr = 0
    if not pre_2020.empty:
        pre_cagr = calculate_cagr(pre_2020['count'].iloc[0], pre_2020['count'].iloc[-1], len(pre_2020) - 1)

    post_cagr = 0
    if not post_2020.empty:
        post_cagr = calculate_cagr(post_2020['count'].iloc[0], post_2020['count'].iloc[-1], len(post_2020) - 1)

    # Visualization
    plt.figure(figsize=(12, 6))
    plt.plot(trend['year'], trend['count'], marker='o', linestyle='-', color='#1f77b4', linewidth=2, label='Annual Publications')
    
    # Highlight 2020 (COVID start)
    plt.axvline(x=2020, color='red', linestyle='--', alpha=0.5, label='COVID-19 Boundary (2020)')
    
    plt.title('Scholarly Communication & Research Security: Publication Trends', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Number of Publications', fontsize=12)
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.legend()
    
    # Annotate CAGR
    plt.annotate(f'Total CAGR: {total_cagr:.2f}%', xy=(0.05, 0.95), xycoords='axes fraction', fontsize=10, bbox=dict(boxstyle="round", fc="w"))
    plt.annotate(f'Post-2020 CAGR: {post_cagr:.2f}%', xy=(0.05, 0.88), xycoords='axes fraction', fontsize=10, bbox=dict(boxstyle="round", fc="w", ec="red"))

    plot_path = os.path.join(OUTPUT_DIR, 'publication_trend.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {plot_path}")

    # Save Stats
    stats = {
        'Metric': ['Total Papers', 'Start Year', 'End Year', 'Total CAGR', 'Pre-2020 CAGR', 'Post-2020 CAGR'],
        'Value': [len(df), start_year, end_year, f"{total_cagr:.2f}%", f"{pre_cagr:.2f}%", f"{post_cagr:.2f}%"]
    }
    pd.DataFrame(stats).to_csv(os.path.join(OUTPUT_DIR, 'trend_summary.csv'), index=False)
    trend.to_csv(os.path.join(OUTPUT_DIR, 'yearly_counts.csv'), index=False)
    print("Saved trend stats to CSV.")

if __name__ == "__main__":
    run_trend_analysis()
