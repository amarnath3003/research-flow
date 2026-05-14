# Phase 4: Advanced Interpretation Layer

This phase focuses on extracting scholarly meaning from the quantitative data generated in Phase 3. It provides the "Discussion" and "Evolution" foundations for the final research paper.

## Analysis Scripts

### 1. Temporal Evolution Analysis (`step1_temporal_evolution.py`)
- **Focus**: Tracks specific themes over time.
- **Goal**: Identify thematic shifts and turning points.
- **Themes Tracked**: Configured in `research_config.yaml` under `tracking.themes`.
- **Outputs**:
  - `outputs/evolution/theme_evolution.png`
  - `outputs/evolution/theme_evolution.csv`

### 2. Burst Detection (`step2_burst_detection.py`)
- **Focus**: Statistical detection of sudden keyword frequency spikes.
- **Logic**: Uses Z-score anomalies to identify "surging" topics.
- **Outputs**:
  - `outputs/bursts/burst_detection.csv`

### 3. Narrative Generator (`step3_narrative_generator.py`)
- **Focus**: Synthesis of findings into scholarly prose.
- **Goal**: Transition from "What happened" to "Why it happened."
- **Outputs**:
  - `outputs/narrative/discussion_draft.md`

## Execution Order
1. `step1_temporal_evolution.py`
2. `step2_burst_detection.py`
3. `step3_narrative_generator.py`

## Discussion Themes
The narrative is generated dynamically from the data — the top themes, highest growth periods, and burst keywords are identified automatically rather than hardcoded.
