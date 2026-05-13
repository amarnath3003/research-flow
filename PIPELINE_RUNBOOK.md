# Pipeline Runbook

This repository has one end-to-end flow:

1. `scientometric_pipeline`
2. `advanced_pipeline`
3. `phase1_refinement`
4. `phase2_validation`
5. `phase3_analysis`
6. `phase4_interpretation`
7. `phase5_visualizations`
8. `gather_final_outputs.py` -> `FinalOutputs/`

Use the root runner so each script executes from the correct working directory.

## Full flow

### First pass: automatic setup and topic export
```powershell
python run_research_pipeline.py all-auto
```

This does:
- base data fetch and cleaning
- embeddings and BERTopic generation
- diagnostic exports
- exports `phase1_refinement/topic_classification.csv`

### Manual step 1: classify topics
Open:
```text
phase1_refinement/topic_classification.csv
```

Fill these columns:
- `label`
- `classification`
- `keep/remove`

Then run:
```powershell
python run_research_pipeline.py post-curation
```

This does:
- apply Phase 1 refinement
- generate Phase 2 sampling report
- generate `phase2_validation/topic_merging_map.csv`

### Manual step 2: merge topics into major themes
Open:
```text
phase2_validation/topic_merging_map.csv
```

Fill:
- `new_major_theme_name`

Then run:
```powershell
python run_research_pipeline.py all-after-manual
```

This does:
- apply Phase 2 merges
- run Phases 3, 4, and 5
- generate the final report
- rebuild `FinalOutputs`

## Individual stage commands

```powershell
python run_research_pipeline.py scientometric
python run_research_pipeline.py advanced
python run_research_pipeline.py phase1-export
python run_research_pipeline.py phase1-refine
python run_research_pipeline.py phase2-prepare
python run_research_pipeline.py phase2-merge
python run_research_pipeline.py phase3
python run_research_pipeline.py phase4
python run_research_pipeline.py phase5
python run_research_pipeline.py finalize
```

## What lands in `FinalOutputs`

- `Reports/`
  - final consolidated report
- `Figures/`
  - manuscript-ready PNG/HTML visualizations
- `Data/`
  - trend, source, network, collaboration, burst, evolution, and diagnostic files
- `Methodology/`
  - phase READMEs and pipeline notes

## Notes

- `advanced_pipeline/ai_interpreter.py` depends on local `ollama`.
- `phase1_refinement` and `phase2_validation` are intentionally semi-manual.
- If you rerun `finalize`, `FinalOutputs` is refreshed from the latest phase outputs.
