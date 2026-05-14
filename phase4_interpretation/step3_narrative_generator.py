import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import load_config

cfg = load_config()
RESEARCH_TITLE = cfg["research"]["title"]

EVO_FILE = "outputs/evolution/theme_evolution.csv"
BURST_FILE = "outputs/bursts/burst_detection.csv"
TREND_FILE = "../phase3_analysis/outputs/trends/trend_summary.csv"
OUTPUT_DIR = "outputs/narrative"

def run_narrative_generator():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    narrative = f"# Interpretation & Discussion: {RESEARCH_TITLE}\n\n"

    # 1. Trend Interpretation — data-driven: find highest growth period
    if os.path.exists(TREND_FILE):
        trends = pd.read_csv(TREND_FILE)
        total_cagr = trends[trends['Metric'] == 'Total CAGR']['Value'].values[0]

        # Dynamically discover all CAGR periods from the CSV
        cagr_periods = {'Total': total_cagr}
        for _, row in trends.iterrows():
            metric = row['Metric']
            if metric != 'Total CAGR' and 'CAGR' in metric:
                cagr_periods[metric.replace(' CAGR', '')] = row['Value']

        numeric_cagrs = {}
        for k, v in cagr_periods.items():
            try:
                numeric_cagrs[k] = float(str(v).replace('%', ''))
            except (ValueError, TypeError):
                pass

        best_period = max(numeric_cagrs, key=numeric_cagrs.get) if numeric_cagrs else 'Total'

        narrative += "## 1. Growth Analysis\n"
        narrative += f"- **Finding**: Total CAGR reached {total_cagr}. The **{best_period}** period shows the highest growth.\n"
        narrative += "- **Interpretation**: The data reveals significant growth patterns in this research domain. The acceleration may reflect increased scholarly attention, external events, or policy developments that shaped the field.\n\n"

    # 2. Theme Evolution — data-driven: report top themes from data
    if os.path.exists(EVO_FILE):
        evo = pd.read_csv(EVO_FILE)
        theme_cols = [c for c in evo.columns if c != 'year']
        if theme_cols:
            totals = evo[theme_cols].sum().sort_values(ascending=False)
            top_themes = totals.head(3)

            narrative += "## 2. Thematic Maturation\n"
            narrative += "- **Finding**: The dominant themes identified from the data are:\n"
            for theme, count in top_themes.items():
                narrative += f"  - **{theme}**: {int(count)} occurrences\n"
            narrative += "- **Interpretation**: These themes represent the core research directions within this field. Their relative prominence and growth trajectories reflect the evolving scholarly discourse.\n\n"

    # 3. Burst Interpretation — data-driven
    if os.path.exists(BURST_FILE):
        bursts = pd.read_csv(BURST_FILE)
        if not bursts.empty:
            top_bursts = bursts.nlargest(10, 'z_score')['keyword'].unique()[:5]

            narrative += "## 3. Sudden Topic Emergence (Bursts)\n"
            narrative += f"- **Findings**: The most significant burst keywords include {', '.join(top_bursts)}.\n"
            narrative += "- **Interpretation**: These burst keywords indicate rapidly growing sub-topics that may represent emerging frontiers, shifting research priorities, or responses to external developments in the field.\n\n"

    with open(os.path.join(OUTPUT_DIR, 'discussion_draft.md'), 'w') as f:
        f.write(narrative)

    print(f"Narrative draft saved to {OUTPUT_DIR}/discussion_draft.md")

if __name__ == "__main__":
    run_narrative_generator()
