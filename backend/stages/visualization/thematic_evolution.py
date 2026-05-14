"""Figure 4: Thematic Evolution Stacked Area."""
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import load, BASE_DIR

cfg = load()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")


def run():
    path = os.path.join(OUTPUTS_DIR, "evolution", "theme_evolution.csv")
    if not os.path.exists(path):
        print("Evolution data not found.")
        return

    df = pd.read_csv(path).sort_values("year")
    themes = [c for c in df.columns if c != "year"]

    plt.figure(figsize=(12, 7))
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"]
    plt.stackplot(df["year"], [df[t] for t in themes], labels=themes, alpha=0.8,
                  colors=colors[:len(themes)])

    plt.title(f"Thematic Evolution ({int(df['year'].min())}-{int(df['year'].max())})", fontsize=16, fontweight="bold", pad=20)
    plt.xlabel("Year")
    plt.ylabel("Cumulative Theme Frequency")
    plt.legend(loc="upper left", frameon=True, facecolor="white", framealpha=0.9)
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.xlim(df["year"].min(), df["year"].max())

    figs_dir = os.path.join(OUTPUTS_DIR, "figures")
    os.makedirs(figs_dir, exist_ok=True)
    plt.savefig(os.path.join(figs_dir, "figure4_thematic_evolution.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("Figure 4 generated")
