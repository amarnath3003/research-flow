# Phase 2: Semantic Quality Validation

This folder contains tools to consolidate your 79 clusters into 8–15 high-level, academically meaningful themes.

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
- Identify which topics are semantically identical (e.g., "AI ethics" and "AI governance").

### Step 2: Define Major Themes
Generate the merging template:
```bash
python phase2_validation/generate_template.py
```
Open `phase2_validation/topic_merging_map.csv` in Excel.
- For every `original_topic_id`, assign a **`new_major_theme_name`**.
- **Example**: Map topics 5, 12, and 18 all to "Governance and Ethical Security Challenges in AI-Driven Scholarly Ecosystems".
- **Target**: Ensure only 8–15 unique theme names exist in this column.

### Step 3: Apply Merges
Once the CSV is saved, run the merge script:
```bash
python phase2_validation/step2_apply_merges.py
```
This will create `final_thematic_dataset.csv`.

## Academic Renaming Tips
Avoid generic labels:
- **BAD**: AI governance
- **GOOD**: Governance and Ethical Security Challenges in AI-Driven Scholarly Ecosystems

- **BAD**: Ransomware
- **GOOD**: Socio-Technical Vulnerabilities in Open Scholarly Infrastructure

These names should be used in your paper's results section.
