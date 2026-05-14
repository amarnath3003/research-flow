import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import load_config

cfg = load_config()
RESEARCH_TITLE = cfg["research"]["title"]
CONFIG_THEMES = cfg["tracking"].get("themes", [])

INPUT_FILE = "../phase2_validation/final_thematic_dataset.csv"
FALLBACK_FILE = "../advanced_pipeline/data/processed/topic_dataset.csv"
OUTPUT_DIR = "outputs/evolution"

def run_temporal_evolution():
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

    start = cfg["research"]["start_year"]
    end = cfg["research"]["end_year"]
    df = df[(df['year'] >= start) & (df['year'] <= end)]

    df['text_corpus'] = (df['title'].fillna('') + " " +
                         df['abstract'].fillna('') + " " +
                         df['keywords'].fillna('')).str.lower()

    # Build themes from config, or auto-detect from Phase 2 theme column
    themes = {}
    if CONFIG_THEMES:
        for t in CONFIG_THEMES:
            themes[t["name"]] = t["pattern"]
    elif "new_major_theme_name" in df.columns:
        top_themes = df["new_major_theme_name"].value_counts().head(50).index.tolist()
        for name in top_themes[:5]:
            themes[name] = re.escape(name.lower())
    else:
        print("No themes configured and no theme column found. Skipping evolution.")
        return

    evolution_data = []
    for year in sorted(df['year'].unique()):
        year_df = df[df['year'] == year]
        row = {'year': year}
        for theme_name, pattern in themes.items():
            count = year_df['text_corpus'].str.contains(pattern, case=False, regex=True).sum()
            row[theme_name] = count
        evolution_data.append(row)

    evo_df = pd.DataFrame(evolution_data)
    evo_df.to_csv(os.path.join(OUTPUT_DIR, 'theme_evolution.csv'), index=False)

    # Visualization
    plt.figure(figsize=(12, 7))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    for i, theme in enumerate(themes.keys()):
        color = colors[i % len(colors)]
        plt.plot(evo_df['year'], evo_df[theme], marker='o', label=theme, linewidth=2, color=color)

    plt.title(f'Temporal Evolution of Research Themes ({start}-{end})', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Publication Count', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()

    plot_path = os.path.join(OUTPUT_DIR, 'theme_evolution.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Saved evolution plot to {plot_path}")

if __name__ == "__main__":
    run_temporal_evolution()
