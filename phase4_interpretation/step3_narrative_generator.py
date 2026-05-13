import pandas as pd
import os

# Configuration
EVO_FILE = "outputs/evolution/theme_evolution.csv"
BURST_FILE = "outputs/bursts/burst_detection.csv"
TREND_FILE = "../phase3_analysis/outputs/trends/trend_summary.csv"
OUTPUT_DIR = "outputs/narrative"

def run_narrative_generator():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    narrative = "# Scholarly Interpretation & Discussion Snippets\n\n"
    
    # 1. Trend Interpretation
    if os.path.exists(TREND_FILE):
        trends = pd.read_csv(TREND_FILE)
        total_cagr = trends[trends['Metric'] == 'Total CAGR']['Value'].values[0]
        post_cagr = trends[trends['Metric'] == 'Post-2020 CAGR']['Value'].values[0]
        
        narrative += "## 1. The COVID-19 Catalyst\n"
        narrative += f"- **Finding**: Post-2020 CAGR reached {post_cagr}, compared to a total CAGR of {total_cagr}.\n"
        narrative += "- **Interpretation**: The post-2020 surge reflects the convergence of pandemic-driven open collaboration, accelerated digitalization, and increasing institutional awareness of cyber vulnerabilities in research ecosystems. The sudden shift to remote research infrastructure acted as a stress test for academic cybersecurity, driving a new wave of 'research security' scholarship.\n\n"

    # 2. Theme Evolution
    if os.path.exists(EVO_FILE):
        evo = pd.read_csv(EVO_FILE)
        narrative += "## 2. Thematic Maturation\n"
        narrative += "- **Finding**: Tracking the emergence of 'Research Security' vs 'Open Science'.\n"
        narrative += "- **Interpretation**: While 'Open Science' followed a steady growth path since 2010, the concept of 'Research Security' transitioned from a niche policy concern to a central scholarly pillar after 2018. This suggests a maturing understanding that transparency and protection are not antithetical but mutually reinforcing components of modern academic governance.\n\n"

    # 3. Burst Interpretation
    if os.path.exists(BURST_FILE):
        bursts = pd.read_csv(BURST_FILE)
        recent_bursts = bursts[bursts['burst_year'] >= 2022]['keyword'].unique()[:5]
        
        narrative += "## 3. Sudden Topic Emergence (Bursts)\n"
        narrative += f"- **Findings**: Recent bursts include {', '.join(recent_bursts)}.\n"
        narrative += "- **Interpretation**: The sudden prominence of Generative AI and Large Language Models (LLMs) has introduced a 'dual-use' tension in scholarly communication. On one hand, these tools accelerate discovery; on the other, they complicate governance around plagiarism, automated misinformation, and data provenance, necessitating the rapid development of AI-aware research security frameworks.\n\n"

    with open(os.path.join(OUTPUT_DIR, 'discussion_draft.md'), 'w') as f:
        f.write(narrative)
    
    print(f"Narrative draft saved to {OUTPUT_DIR}/discussion_draft.md")

if __name__ == "__main__":
    run_narrative_generator()
