# Phase 4: Advanced Interpretation Layer

This phase focuses on extracting scholarly meaning from the quantitative data generated in Phase 3. It provides the "Discussion" and "Evolution" foundations for the final research paper.

## Analysis Scripts

### 1. Temporal Evolution Analysis (`step1_temporal_evolution.py`)
- **Focus**: Tracks specific high-value terms over time.
- **Goal**: Identify when security entered the open science discourse and if COVID was a turning point.
- **Key Themes Tracked**:
  - Research Security
  - AI Governance
  - Ransomware
  - Open Science (FAIR data, etc.)
- **Outputs**:
  - `outputs/evolution/theme_evolution.png`: Multi-line plot showing theme trajectories.
  - `outputs/evolution/theme_evolution.csv`: Yearly theme counts.

### 2. Burst Detection (`step2_burst_detection.py`)
- **Focus**: Statistical detection of sudden keyword frequency spikes.
- **Logic**: Uses Z-score anomalies (mimicking CiteSpace burst detection) to identify "surging" topics.
- **Outputs**:
  - `outputs/bursts/burst_detection.csv`: List of keywords that experienced significant bursts, categorized by year.

### 3. Narrative Generator (`step3_narrative_generator.py`)
- **Focus**: Synthesis of findings into scholarly prose.
- **Goal**: Transition from "What happened" to "Why it happened."
- **Outputs**:
  - `outputs/narrative/discussion_draft.md`: A collection of high-quality interpretation snippets for your manuscript.

## Execution Order
1. Run `step1_temporal_evolution.py`
2. Run `step2_burst_detection.py`
3. Run `step3_narrative_generator.py` (requires Phase 3 results to be present)

## Discussion Themes for the Paper
- **The Shift (2018-2020)**: Moving from general open science to "Research Security" as a distinct discipline.
- **The Acceleration (2020-2024)**: How the pandemic and Generative AI combined to create a "perfect storm" for academic cybersecurity governance.
- **Emerging Frontiers**: Identifying the newest bursts (e.g., Sovereign AI, secure data sharing) that define future research directions.
