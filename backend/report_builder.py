"""Build the final research report."""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
from settings import load

cfg = load()
RESEARCH_TITLE = cfg["research"]["title"]
START_YEAR = cfg["research"]["start_year"]
END_YEAR = cfg["research"]["end_year"]
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")


def run():
    os.makedirs(os.path.join(BASE_DIR, "final_figures"), exist_ok=True)

    report = f"# FINAL SCIENTOMETRIC RESEARCH REPORT\n## Topic: {RESEARCH_TITLE}\n\n"
    report += "## 1. Methodology\n"
    report += f"- **Topic**: {RESEARCH_TITLE}\n"
    report += f"- **Period**: {START_YEAR}-{END_YEAR}\n"
    report += "- Phase 1: Semantic boundary refinement and noise removal.\n"
    report += "- Phase 2: Thematic consolidation into 8-15 core themes.\n"
    report += "- Phase 3: Bibliometric analysis (CAGR, H-index, Networks).\n"
    report += "- Phase 4: Advanced interpretation (Evolution, Burst detection).\n\n"

    report += "## 2. Key Visualizations\n"
    visuals = [
        ("outputs/figures/figure1_growth_timeline.png", "Publication Growth Timeline"),
        ("outputs/figures/figure2_keyword_network.png", "Keyword Co-occurrence Network"),
        ("outputs/figures/figure4_thematic_evolution.png", "Thematic Evolution"),
        ("outputs/figures/figure5_cluster_landscape.png", "Cluster Landscape"),
        ("outputs/evolution/theme_evolution.png", "Theme Evolution Detail"),
    ]
    figs_dir = os.path.join(BASE_DIR, "final_figures")
    for src, title in visuals:
        src_path = os.path.join(BASE_DIR, src)
        if os.path.exists(src_path):
            dst = os.path.join(figs_dir, os.path.basename(src))
            import shutil
            shutil.copy(src_path, dst)
            report += f"### {title}\n![{title}]({dst})\n\n"

    narr_path = os.path.join(OUTPUTS_DIR, "narrative", "discussion_draft.md")
    if os.path.exists(narr_path):
        with open(narr_path) as f:
            report += "## 3. Executive Discussion\n" + f.read() + "\n"

    report += "## 4. Output Data Inventory\n"
    report += "| Phase | File | Description |\n|-------|------|-------------|\n"
    report += "| Phase 3 | `top_sources.csv` | Top journals |\n"
    report += "| Phase 3 | `keyword_cooccurrence_edges.csv` | Network data |\n"
    report += "| Phase 4 | `burst_detection.csv` | Burst keywords |\n"
    report += "| Phase 5 | `final_figures/` | Manuscript figures |\n"

    with open(os.path.join(BASE_DIR, "FINAL_RESEARCH_REPORT.md"), "w") as f:
        f.write(report)
    print("Report generated")


if __name__ == "__main__":
    run()
