"""Temporal evolution of research themes."""
import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import load, BASE_DIR

cfg = load()
RESEARCH_TITLE = cfg["research"]["title"]
CONFIG_THEMES = cfg["tracking"].get("themes", [])
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")


def run():
    df_path = os.path.join(BASE_DIR, "data", "processed", "final_thematic_dataset.csv")
    fallback_path = os.path.join(BASE_DIR, "data", "processed", "topic_dataset.csv")

    if os.path.exists(df_path):
        df = pd.read_csv(df_path)
    elif os.path.exists(fallback_path):
        df = pd.read_csv(fallback_path)
    else:
        print("No dataset found.")
        return

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    start = cfg["research"]["start_year"]
    end = cfg["research"]["end_year"]
    df = df[(df["year"] >= start) & (df["year"] <= end)]
    df["text_corpus"] = (
        df["title"].fillna("").astype(str) + " " +
        df["abstract"].fillna("").astype(str) + " " +
        df["keywords"].fillna("").astype(str)
    ).str.lower()

    themes = {}
    if CONFIG_THEMES:
        for t in CONFIG_THEMES:
            themes[t["name"]] = t["pattern"]
    elif "new_major_theme_name" in df.columns:
        top = df["new_major_theme_name"].value_counts().head(50).index.tolist()
        for name in top[:5]:
            themes[name] = re.escape(name.lower())
    else:
        print("No themes configured and no theme column found.")
        return

    evo = []
    for year in sorted(df["year"].unique()):
        yd = df[df["year"] == year]
        row = {"year": year}
        for name, pattern in themes.items():
            row[name] = yd["text_corpus"].str.contains(pattern, case=False, regex=True).sum()
        evo.append(row)

    evo_df = pd.DataFrame(evo)
    evo_dir = os.path.join(OUTPUTS_DIR, "evolution")
    os.makedirs(evo_dir, exist_ok=True)
    evo_df.to_csv(os.path.join(evo_dir, "theme_evolution.csv"), index=False)

    plt.figure(figsize=(12, 7))
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"]
    for i, name in enumerate(themes.keys()):
        plt.plot(evo_df["year"], evo_df[name], marker="o", label=name, linewidth=2, color=colors[i % len(colors)])
    plt.title(f"Thematic Evolution ({start}-{end})", fontsize=14)
    plt.xlabel("Year")
    plt.ylabel("Publication Count")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.savefig(os.path.join(evo_dir, "theme_evolution.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print("Temporal evolution complete")
