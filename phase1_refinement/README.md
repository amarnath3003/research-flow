# Phase 1: Dataset Boundary Refinement

This folder contains the tools to refine your dataset by filtering out "Noise" and "Supporting" topics that don't align with the core research identity.

## Goal
Prevent thematic contamination by manually validating BERTopic clusters.

## Workflow

### Step 1: Export Topic Summary
Run the export script to generate a list of all 79 topics with representative titles and abstracts.
```bash
python phase1_refinement/step1_export_topics.py
```
This will create `topic_classification.csv`.

### Step 2: Manual Classification
Open `topic_classification.csv` in Excel or a CSV editor. For each topic, fill in:
- **label**: A short descriptive name for the topic.
- **classification**: `CORE`, `SUPPORTING`, or `NOISE`.
- **keep/remove**: Enter `keep` or `remove`.

**Classification Rules:**
- **CORE**: scholarly communication, academic data governance, research security, university cybersecurity. (**MUST remain**)
- **SUPPORTING**: AI governance, legal frameworks, cloud collaboration. (**Keep selectively**)
- **NOISE**: Industrial IoT, smart farming, generic blockchain, telecom security. (**Remove**)

### Step 3: Create Final Curated Dataset
Once you have saved your edits in `topic_classification.csv`, run the refinement script:
```bash
python phase1_refinement/step2_refine_dataset.py
```
This will generate `final_curated_dataset.csv`.

## Methodology Note for Paper
> "Multi-stage semantic filtering and manual validation were conducted to preserve thematic alignment with scholarly communication and research security."
