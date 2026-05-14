# Pipeline Runbook

## Quick Start

```bash
# 1. Generate config interactively
python run_research_pipeline.py --init

# 2. Edit research_config.yaml with your search query, years, email

# 3. Run automated data collection + topic export
python run_research_pipeline.py all-auto --config research_config.yaml

# 4. Manually classify topics in phase1_refinement/topic_classification.csv
#    (label each topic as CORE/SUPPORTING/NOISE)

# 5. Apply curation & prepare theme merging
python run_research_pipeline.py post-curation --config research_config.yaml

# 6. Manually merge themes in phase2_validation/topic_merging_map.csv

# 7. Run final analysis, interpretation, visualizations, and report
python run_research_pipeline.py all-after-manual --config research_config.yaml
```

## Pipeline Stages

| Command | What It Does |
|---------|-------------|
| `all-auto` | Data collection (OpenAlex) + cleaning + topic modeling + topic export |
| `post-curation` | Apply Phase 1 classification + generate Phase 2 merge template |
| `all-after-manual` | Theme merging + Phase 3/4/5 analysis + final report |

## Final Outputs
All outputs are consolidated in `FinalOutputs/`:
- `Reports/` — Final research report
- `Figures/` — Manuscript-ready visualizations
- `Data/` — CSV exports for all analyses
- `Methodology/` — Documentation
