# Phase 1: Dataset Boundary Refinement

This folder contains tools to refine your dataset by filtering out "Noise" and "Supporting" topics that don't align with your core research identity.

## Goal
Prevent thematic contamination by manually validating BERTopic clusters.

## Workflow

### Step 1: Export Topic Summary
Run the export script to generate a list of all topics with representative titles and abstracts.
```bash
python phase1_refinement/step1_export_topics.py
```
This will create `topic_classification.csv`.

### Step 2: Manual Classification
Open `topic_classification.csv` in Excel or a CSV editor. For each topic, fill in:
- **label**: A short descriptive name for the topic.
- **classification**: `CORE`, `SUPPORTING`, or `NOISE`.
- **keep/remove**: Enter `keep` or `remove`.

**Classification Rules** (defined by your research context):
- **CORE**: Topics directly aligned with your research. (**MUST remain**)
- **SUPPORTING**: Related topics that provide context. (**Keep selectively**)
- **NOISE**: Irrelevant topics that dilute focus. (**Remove**)

### Step 3: Create Final Curated Dataset
Once you have saved your edits in `topic_classification.csv`, run the refinement script:
```bash
python phase1_refinement/step2_refine_dataset.py
```
This will generate `final_curated_dataset.csv`.

## Methodology Note
> Multi-stage semantic filtering and manual validation were conducted to preserve thematic alignment with the research focus.
