# Phase 2: Semantic Quality Validation

This folder contains tools to consolidate your clusters into 8–15 high-level, academically meaningful themes.

## Goal
Transform fragmented technical clusters into mature research themes for your paper's discussion.

## Workflow

### Step 1: Representative Sampling
Generate a sampling report to inspect the coherence of each cluster.
```bash
python phase2_validation/step1_sampling_report.py
```
Open `phase2_validation/semantic_validation_report.md`.
- Read titles and abstracts for each topic.
- Identify which topics are semantically identical.

### Step 2: Define Major Themes
Generate the merging template:
```bash
python phase2_validation/generate_template.py
```
Open `phase2_validation/topic_merging_map.csv` in Excel.
- For every `original_topic_id`, assign a **`new_major_theme_name`**.
- Group similar topics under unified theme names.
- **Target**: Ensure only 8–15 unique theme names exist in this column.

### Step 3: Apply Merges
Once the CSV is saved, run the merge script:
```bash
python phase2_validation/step2_apply_merges.py
```
This will create `final_thematic_dataset.csv`.

## Tips for Academic Theme Naming
Use descriptive, academically appropriate names:
- Avoid generic labels (e.g., "AI")
- Prefer precise descriptions (e.g., "Ethical and Governance Challenges in AI-Driven Ecosystems")
- These names will appear in your paper's results section.
