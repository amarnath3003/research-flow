import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def get_env(cfg_path):
    env = os.environ.copy()
    if cfg_path:
        env["RESEARCH_CONFIG"] = os.path.abspath(cfg_path)
    return env


def run_step(label, command, workdir, cfg_path=None):
    print(f"\n{'=' * 72}")
    print(label)
    print(f"Working directory: {workdir}")
    print(f"Command: {' '.join(command)}")
    print(f"{'=' * 72}")
    result = subprocess.run(
        command,
        cwd=os.path.join(ROOT, workdir),
        env=get_env(cfg_path),
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def require_file(path, message):
    abs_path = os.path.join(ROOT, path)
    if not os.path.exists(abs_path):
        raise SystemExit(f"{message}\nMissing: {path}")


def require_nonempty_column(csv_path, column_name, message):
    import pandas as pd
    abs_path = os.path.join(ROOT, csv_path)
    if not os.path.exists(abs_path):
        raise SystemExit(f"{message}\nMissing: {csv_path}")
    df = pd.read_csv(abs_path)
    if column_name not in df.columns:
        raise SystemExit(f"Required column '{column_name}' not found in {csv_path}")
    filled = df[column_name].fillna("").astype(str).str.strip()
    if not (filled != "").any():
        raise SystemExit(f"{message}\nColumn '{column_name}' is still empty in {csv_path}")


def stage_scientometric(cfg_path):
    run_step(
        "Stage 0 - Base data collection and cleaning",
        ["python", "main.py"],
        "scientometric_pipeline",
        cfg_path,
    )


def stage_advanced(cfg_path):
    run_step(
        "Stage 1A - Advanced pipeline (embeddings, topics, networks, reports)",
        ["python", "main.py"],
        "advanced_pipeline",
        cfg_path,
    )
    run_step(
        "Stage 1B - Diagnostic exports for downstream sharing and reporting",
        ["python", "diagnostic_export.py"],
        "advanced_pipeline",
        cfg_path,
    )


def stage_phase1_export(cfg_path):
    require_file(
        "advanced_pipeline/data/processed/topic_dataset.csv",
        "Run the advanced pipeline first so topic assignments exist.",
    )
    run_step(
        "Stage 2A - Export topic classification template",
        ["python", "phase1_refinement/step1_export_topics.py"],
        ".",
        cfg_path,
    )
    print(
        "\nManual action required:\n"
        "Open phase1_refinement/topic_classification.csv and fill "
        "'label', 'classification', and 'keep/remove'."
    )


def stage_phase1_refine(cfg_path):
    require_nonempty_column(
        "phase1_refinement/topic_classification.csv",
        "keep/remove",
        "Phase 1 classification is incomplete.",
    )
    run_step(
        "Stage 2B - Apply Phase 1 dataset refinement",
        ["python", "phase1_refinement/step2_refine_dataset.py"],
        ".",
        cfg_path,
    )


def stage_phase2_prepare(cfg_path):
    require_file(
        "phase1_refinement/final_curated_dataset.csv",
        "Complete Phase 1 refinement before Phase 2.",
    )
    run_step(
        "Stage 3A - Generate semantic validation report",
        ["python", "phase2_validation/step1_sampling_report.py"],
        ".",
        cfg_path,
    )
    run_step(
        "Stage 3B - Generate theme-merging template",
        ["python", "phase2_validation/generate_template.py"],
        ".",
        cfg_path,
    )
    print(
        "\nManual action required:\n"
        "Open phase2_validation/topic_merging_map.csv and fill "
        "'new_major_theme_name' for each original_topic_id."
    )


def stage_phase2_merge(cfg_path):
    require_nonempty_column(
        "phase2_validation/topic_merging_map.csv",
        "new_major_theme_name",
        "Phase 2 theme mapping is incomplete.",
    )
    run_step(
        "Stage 3C - Apply Phase 2 thematic merges",
        ["python", "phase2_validation/step2_apply_merges.py"],
        ".",
        cfg_path,
    )


def stage_phase3(cfg_path):
    require_file(
        "phase2_validation/final_thematic_dataset.csv",
        "Complete Phase 2 thematic merging before Phase 3.",
    )
    scripts = [
        "step1_trend_analysis.py",
        "step2_source_analysis.py",
        "step3_geopolitical_analysis.py",
        "step4_network_analysis.py",
        "step5_author_analysis.py",
    ]
    for script in scripts:
        run_step(f"Stage 4 - {script}", ["python", script], "phase3_analysis", cfg_path)


def stage_phase4(cfg_path):
    require_file(
        "phase3_analysis/outputs/trends/trend_summary.csv",
        "Run Phase 3 before Phase 4.",
    )
    scripts = [
        "step1_temporal_evolution.py",
        "step2_burst_detection.py",
        "step3_narrative_generator.py",
    ]
    for script in scripts:
        run_step(f"Stage 5 - {script}", ["python", script], "phase4_interpretation", cfg_path)


def stage_phase5(cfg_path):
    require_file(
        "phase4_interpretation/outputs/evolution/theme_evolution.csv",
        "Run Phase 4 before Phase 5.",
    )
    scripts = [
        "fig1_growth_timeline.py",
        "fig2_keyword_network.py",
        "fig3_collaboration_map.py",
        "fig4_thematic_evolution.py",
        "fig5_cluster_landscape.py",
    ]
    for script in scripts:
        run_step(f"Stage 6 - {script}", ["python", script], "phase5_visualizations", cfg_path)


def stage_finalize(cfg_path):
    run_step(
        "Stage 7 - Build final report and consolidate FinalOutputs",
        ["python", "gather_final_outputs.py"],
        ".",
        cfg_path,
    )


def stage_all_auto(cfg_path):
    stage_scientometric(cfg_path)
    stage_advanced(cfg_path)
    stage_phase1_export(cfg_path)


def stage_post_curation(cfg_path):
    stage_phase1_refine(cfg_path)
    stage_phase2_prepare(cfg_path)
    print(
        "\nStop here after the template is generated, edit the Phase 2 mapping CSV, "
        "then run 'phase2-merge' or 'all-after-manual'."
    )


def stage_all_after_manual(cfg_path):
    stage_phase2_merge(cfg_path)
    stage_phase3(cfg_path)
    stage_phase4(cfg_path)
    stage_phase5(cfg_path)
    stage_finalize(cfg_path)


def generate_init_config():
    """Interactive config generator for new users."""
    from config_loader import DEFAULT_PATH
    cfg_path = DEFAULT_PATH
    if os.path.exists(cfg_path):
        overwrite = input(f"Config already exists at {cfg_path}. Overwrite? (y/N): ")
        if overwrite.lower() != "y":
            print("Aborted.")
            return

    print("\n=== Research Config Generator ===\n")
    title = input("Research title: ").strip() or "My Research Topic"
    desc = input("Brief description of your research: ").strip() or ""
    query = input("OpenAlex search query (boolean): ").strip() or ""
    start = input("Start year [2010]: ").strip() or "2010"
    end = input("End year [2025]: ").strip() or "2025"
    email = input("Your email (for OpenAlex API): ").strip()

    config_yaml = f"""# Research Configuration
# Generated by run_research_pipeline.py --init

research:
  title: "{title}"
  description: "{desc}"
  search_query: |
    {query}
  start_year: {start}
  end_year: {end}
  max_results: 5000
  email: "{email}"

cleaning:
  enabled: true
  hard_exclusions: []
  core_concepts: []
  context_keywords: []
  high_priority_concepts: []
  security_terms:
    - security
    - cybersecurity
    - threat

embedding:
  model: "all-MiniLM-L6-v2"
  min_topic_size: 10
  top_n_topics: 20

llm:
  provider: null
  model: null
  api_key_env: null
  base_url: null

tracking:
  themes: []

visualizations:
  annotations:
    enabled: true
    custom: []
"""
    with open(cfg_path, "w") as f:
        f.write(config_yaml)
    print(f"\nConfig written to {cfg_path}")
    print("Edit it to add cleaning rules or tracking themes, then run the pipeline.")


STAGES = {
    "scientometric": stage_scientometric,
    "advanced": stage_advanced,
    "phase1-export": stage_phase1_export,
    "phase1-refine": stage_phase1_refine,
    "phase2-prepare": stage_phase2_prepare,
    "phase2-merge": stage_phase2_merge,
    "phase3": stage_phase3,
    "phase4": stage_phase4,
    "phase5": stage_phase5,
    "finalize": stage_finalize,
    "all-auto": stage_all_auto,
    "post-curation": stage_post_curation,
    "all-after-manual": stage_all_after_manual,
}


def main():
    parser = argparse.ArgumentParser(
        description="Root runner for the scientometric research pipeline."
    )
    parser.add_argument(
        "stage",
        nargs="?",
        choices=sorted(STAGES.keys()) + ["init"],
        default=None,
        help="Which stage to run. Use 'init' to generate a config interactively.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to research_config.yaml (default: auto-discover)",
    )

    args = parser.parse_args()

    if args.stage == "init" or args.stage is None:
        generate_init_config()
        return

    cfg_path = args.config
    STAGES[args.stage](cfg_path)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
