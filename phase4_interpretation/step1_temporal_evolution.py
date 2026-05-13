import pandas as pd
import matplotlib.pyplot as plt
import os
import re

# Configuration
INPUT_FILE = "../phase2_validation/final_thematic_dataset.csv"
FALLBACK_FILE = "../advanced_pipeline/data/processed/topic_dataset.csv"
OUTPUT_DIR = "outputs/evolution"

# Themes to track
THEMES = {
    'Research Security': r'research security|safeguarding research|national security',
    'AI Governance': r'ai governance|ai ethics|artificial intelligence governance|generative ai',
    'Ransomware': r'ransomware|cyber extortion|malware',
    'Open Science': r'open science|fair data|open access|scholarly communication',
    'Cybersecurity': r'cybersecurity|information security|cyber attack'
}

def run_temporal_evolution():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load data
    if os.path.exists(INPUT_FILE):
        df = pd.read_csv(INPUT_FILE)
    elif os.path.exists(FALLBACK_FILE):
        df = pd.read_csv(FALLBACK_FILE)
    else:
        print("Error: No dataset found.")
        return

    # Clean year
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)
    df = df[(df['year'] >= 2010) & (df['year'] <= 2024)]

    # Combine text for searching
    df['text_corpus'] = (df['title'].fillna('') + " " + 
                         df['abstract'].fillna('') + " " + 
                         df['keywords'].fillna('')).str.lower()

    # Track themes
    evolution_data = []
    for year in sorted(df['year'].unique()):
        year_df = df[df['year'] == year]
        row = {'year': year}
        for theme_name, pattern in THEMES.items():
            count = year_df['text_corpus'].str.contains(pattern, case=False, regex=True).sum()
            row[theme_name] = count
        evolution_data.append(row)

    evo_df = pd.DataFrame(evolution_data)
    evo_df.to_csv(os.path.join(OUTPUT_DIR, 'theme_evolution.csv'), index=False)

    # Visualization
    plt.figure(figsize=(12, 7))
    for theme in THEMES.keys():
        plt.plot(evo_df['year'], evo_df[theme], marker='o', label=theme, linewidth=2)

    plt.axvline(x=2020, color='red', linestyle='--', alpha=0.4, label='COVID-19 Turning Point')
    plt.title('Temporal Evolution of Key Research Themes (2010-2024)', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Publication Count (Theme-Specific)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()

    plot_path = os.path.join(OUTPUT_DIR, 'theme_evolution.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Saved evolution plot to {plot_path}")

if __name__ == "__main__":
    run_temporal_evolution()
