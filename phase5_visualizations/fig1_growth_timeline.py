import pandas as pd
import matplotlib.pyplot as plt
import os

# Configuration
INPUT_FILE = "../phase3_analysis/outputs/trends/trend_summary.csv" # Using calculated data
DATASET_FILE = "../advanced_pipeline/data/processed/topic_dataset.csv"
OUTPUT_DIR = "outputs"

def run_growth_timeline():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load dataset to get yearly counts
    df = pd.read_csv(DATASET_FILE)
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['year'])
    counts = df.groupby('year').size().reset_index(name='count')
    counts = counts[(counts['year'] >= 2010) & (counts['year'] <= 2024)]

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(counts['year'], counts['count'], marker='o', color='#1f77b4', linewidth=3, markersize=8, label='Annual Publications')
    plt.fill_between(counts['year'], counts['count'], color='#1f77b4', alpha=0.1)

    # Annotate Markers
    # 1. COVID-19 Marker
    plt.axvline(x=2020, color='#d62728', linestyle='--', alpha=0.7)
    plt.text(2020.2, counts[counts['year'] == 2020]['count'].values[0] + 50, 
             'COVID-19 Pandemic\n(Research Shift)', color='#d62728', fontweight='bold', fontsize=10)

    # 2. AI Boom Marker
    plt.axvline(x=2022, color='#2ca02c', linestyle='--', alpha=0.7)
    plt.text(2022.2, counts[counts['year'] == 2022]['count'].values[0] + 50, 
             'Generative AI Boom\n(ChatGPT/LLMs)', color='#2ca02c', fontweight='bold', fontsize=10)

    # Aesthetics
    plt.title('Figure 1: Publication Growth Timeline (2010-2024)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Number of Publications', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.xticks(range(2010, 2025, 2))
    plt.ylim(0, counts['count'].max() * 1.3) # Give room for labels
    plt.legend()

    # Save
    plot_path = os.path.join(OUTPUT_DIR, 'figure1_growth_timeline.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Generated Figure 1: {plot_path}")

if __name__ == "__main__":
    run_growth_timeline()
