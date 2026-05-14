import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import load_config

cfg = load_config()
RESEARCH_TITLE = cfg["research"]["title"]

INPUT_FILE = "../phase1_refinement/topic_info.csv"
DATASET_FILE = "../advanced_pipeline/data/processed/topic_dataset.csv"
OUTPUT_DIR = "outputs"

def run_cluster_landscape():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if os.path.exists(INPUT_FILE):
        df = pd.read_csv(INPUT_FILE)
    else:
        df_full = pd.read_csv(DATASET_FILE)
        df = df_full.groupby('topic').size().reset_index(name='Count')
        df['Name'] = df['topic'].apply(lambda x: f"Topic {x}")

    df = df[df['topic'] != -1].sort_values('Count', ascending=False).head(20)

    n = len(df)
    theta = np.linspace(0, 4 * np.pi, n)
    r = np.linspace(0, 10, n)
    df['x'] = r * np.cos(theta)
    df['y'] = r * np.sin(theta)

    plt.figure(figsize=(12, 10))
    scatter = plt.scatter(df['x'], df['y'], s=df['Count'] * 10, alpha=0.6, c=df['Count'], cmap='plasma')

    for i, row in df.iterrows():
        plt.text(row['x'], row['y'], row['Name'][:20], fontsize=9, ha='center', fontweight='bold')

    plt.title('BERTopic Cluster Landscape (Top 20 Themes)', fontsize=16, fontweight='bold', pad=20)
    plt.colorbar(scatter, label='Document Count')
    plt.axis('off')

    plot_path = os.path.join(OUTPUT_DIR, 'figure5_cluster_landscape.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Generated cluster landscape: {plot_path}")

if __name__ == "__main__":
    run_cluster_landscape()
