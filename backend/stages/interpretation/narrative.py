"""Data-driven narrative generation from analysis outputs."""
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from settings import load, BASE_DIR

cfg = load()
RESEARCH_TITLE = cfg["research"]["title"]
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")


def run():
    evo_file = os.path.join(OUTPUTS_DIR, "evolution", "theme_evolution.csv")
    burst_file = os.path.join(OUTPUTS_DIR, "bursts", "burst_detection.csv")
    trend_file = os.path.join(OUTPUTS_DIR, "trends", "trend_summary.csv")

    narrative = f"# Interpretation & Discussion: {RESEARCH_TITLE}\n\n"

    # Growth
    if os.path.exists(trend_file):
        trends = pd.read_csv(trend_file)
        total_row = trends[trends["Metric"] == "Total CAGR"]
        if not total_row.empty:
            total_cagr = total_row["Value"].values[0]
            cagr_periods = {"Total": total_cagr}
            for _, row in trends.iterrows():
                m = row["Metric"]
                if m != "Total CAGR" and "CAGR" in m:
                    cagr_periods[m.replace(" CAGR", "")] = row["Value"]
            numeric = {}
            for k, v in cagr_periods.items():
                try:
                    numeric[k] = float(str(v).replace("%", ""))
                except (ValueError, TypeError):
                    pass
            best = max(numeric, key=numeric.get) if numeric else "Total"
            narrative += "## 1. Growth Analysis\n"
            narrative += f"- **Total CAGR**: {total_cagr}\n"
            narrative += f"- **Highest growth period**: {best} ({numeric.get(best, 'N/A'):.2f}%)\n"
            narrative += "- This acceleration may reflect increased scholarly attention, external drivers, or policy developments.\n\n"

    # Themes
    if os.path.exists(evo_file):
        evo = pd.read_csv(evo_file)
        theme_cols = [c for c in evo.columns if c != "year"]
        if theme_cols:
            totals = evo[theme_cols].sum().sort_values(ascending=False)
            top3 = totals.head(3)
            narrative += "## 2. Thematic Landscape\n"
            narrative += "- **Dominant themes** from the data:\n"
            for name, count in top3.items():
                narrative += f"  - **{name}**: {int(count)} occurrences\n"
            narrative += "- These represent the core research pillars within this domain.\n\n"

    # Bursts
    if os.path.exists(burst_file):
        bursts = pd.read_csv(burst_file)
        if not bursts.empty:
            top = bursts.nlargest(10, "z_score")["keyword"].unique()[:5]
            narrative += "## 3. Burst Keywords\n"
            narrative += f"- **Emerging topics**: {', '.join(top)}\n"
            narrative += "- These rapidly growing keywords may signal shifting research priorities or emerging sub-fields.\n"

    narr_dir = os.path.join(OUTPUTS_DIR, "narrative")
    os.makedirs(narr_dir, exist_ok=True)
    with open(os.path.join(narr_dir, "discussion_draft.md"), "w") as f:
        f.write(narrative)
    print("Narrative generated")
