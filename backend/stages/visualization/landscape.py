"""Figure 5: BERTopic Cluster Landscape."""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import load, BASE_DIR

cfg = load()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
DATA_DIR = os.path.join(BASE_DIR, "data")


def run():
    topic_info = os.path.join(OUTPUTS_DIR, "stats", "topic_info.csv")
    dataset = os.path.join(DATA_DIR, "processed", "topic_dataset.csv")

    if os.path.exists(topic_info):
        df = pd.read_csv(topic_info)
    else:
        df_full = pd.read_csv(dataset)
        df = df_full.groupby("topic").size().reset_index(name="Count")
        df["Name"] = df["topic"].apply(lambda x: f"Topic {x}")

    df = df[df["topic"] != -1].sort_values("Count", ascending=False).head(20)
    n = len(df)
    theta = np.linspace(0, 4 * np.pi, n)
    r = np.linspace(0, 10, n)
    df["x"] = r * np.cos(theta)
    df["y"] = r * np.sin(theta)

    plt.figure(figsize=(12, 10))
    scatter = plt.scatter(df["x"], df["y"], s=df["Count"] * 10, alpha=0.6, c=df["Count"], cmap="plasma")
    for _, row in df.iterrows():
        plt.text(row["x"], row["y"], str(row.get("Name", ""))[:20], fontsize=9, ha="center", fontweight="bold")

    plt.title("BERTopic Cluster Landscape (Top 20)", fontsize=16, fontweight="bold", pad=20)
    plt.colorbar(scatter, label="Document Count")
    plt.axis("off")

    figs_dir = os.path.join(OUTPUTS_DIR, "figures")
    os.makedirs(figs_dir, exist_ok=True)
    plt.savefig(os.path.join(figs_dir, "figure5_cluster_landscape.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("Figure 5 generated")
