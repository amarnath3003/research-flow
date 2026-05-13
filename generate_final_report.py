import os
import shutil

# Configuration
PHASES = ['phase1_refinement', 'phase2_validation', 'phase3_analysis', 'phase4_interpretation']
FIGURES_DIR = "final_figures"
REPORT_FILE = "FINAL_RESEARCH_REPORT.md"

def consolidate_results():
    print("Consolidating Scientometric Analysis Results...")
    os.makedirs(FIGURES_DIR, exist_ok=True)
    
    report_content = "# FINAL SCIENTOMETRIC RESEARCH REPORT\n"
    report_content += "## Topic: Scholarly Communication & Research Security (2010-2024)\n\n"
    
    # 1. Methodology Summary
    report_content += "## 1. Methodology\n"
    report_content += "- **Phase 1**: Semantic boundary refinement and noise removal.\n"
    report_content += "- **Phase 2**: Thematic consolidation of BERTopic clusters into 8-15 core themes.\n"
    report_content += "- **Phase 3**: Core bibliometric analysis (CAGR, H-index, Networks).\n"
    report_content += "- **Phase 4**: Advanced interpretation (Temporal evolution, Burst detection).\n\n"

    # 2. Key Visuals
    report_content += "## 2. Key Visualizations\n"
    visuals = [
        ('phase5_visualizations/outputs/figure1_growth_timeline.png', 'Publication Growth Timeline'),
        ('phase5_visualizations/outputs/figure2_keyword_network.png', 'Keyword Co-occurrence Network'),
        ('phase5_visualizations/outputs/figure4_thematic_evolution.png', 'Thematic Evolution Timeline'),
        ('phase5_visualizations/outputs/figure5_cluster_landscape.png', 'BERTopic Cluster Landscape'),
        ('phase4_interpretation/outputs/evolution/theme_evolution.png', 'Thematic Evolution Detail')
    ]
    
    for src, title in visuals:
        if os.path.exists(src):
            dst = os.path.join(FIGURES_DIR, os.path.basename(src))
            shutil.copy(src, dst)
            report_content += f"### {title}\n![{title}]({dst})\n\n"

    # 3. Discussion Snippets
    report_content += "## 3. Executive Discussion\n"
    narrative_src = "phase4_interpretation/outputs/narrative/discussion_draft.md"
    if os.path.exists(narrative_src):
        with open(narrative_src, 'r') as f:
            content = f.read()
            # Remove the top-level header from the draft
            content = content.replace("# Scholarly Interpretation & Discussion Snippets\n\n", "")
            report_content += content + "\n"

    # 4. Data Inventory
    report_content += "## 4. Output Data Inventory\n"
    report_content += "| Phase | File | Description |\n"
    report_content += "|-------|------|-------------|\n"
    report_content += "| Phase 3 | `top_sources.csv` | Top journals by influence |\n"
    report_content += "| Phase 3 | `keyword_cooccurrence_edges.csv` | Network data for VOSviewer |\n"
    report_content += "| Phase 4 | `burst_detection.csv` | Sudden topic emergence data |\n"
    report_content += "| Phase 5 | `final_figures/` | Consolidated plots for manuscript |\n\n"

    with open(REPORT_FILE, 'w') as f:
        f.write(report_content)
    
    print(f"Final report generated: {REPORT_FILE}")
    print(f"All figures consolidated in: {FIGURES_DIR}")

if __name__ == "__main__":
    consolidate_results()
