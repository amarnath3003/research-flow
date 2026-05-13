import argparse
import os
import subprocess
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))


def run_step(label, command, workdir):
    print(f"\n{'=' * 72}")
    print(label)
    print(f"Working directory: {workdir}")
    print(f"Command: {' '.join(command)}")
    print(f"{'=' * 72}")
    result = subprocess.run(command, cwd=os.path.join(ROOT, workdir))
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

    filled = (
        df[column_name]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    if not (filled != "").any():
        raise SystemExit(f"{message}\nColumn '{column_name}' is still empty in {csv_path}")


def stage_scientometric():
    run_step(
        "Stage 0 - Base data collection and cleaning",
        ["python", "main.py"],
        "scientometric_pipeline",
    )


def stage_advanced():
    run_step(
        "Stage 1A - Advanced pipeline (embeddings, topics, networks, reports)",
        ["python", "main.py"],
        "advanced_pipeline",
    )
    run_step(
        "Stage 1B - Diagnostic exports for downstream sharing and reporting",
        ["python", "diagnostic_export.py"],
        "advanced_pipeline",
    )


def stage_phase1_export():
    require_file(
        "advanced_pipeline/data/processed/topic_dataset.csv",
        "Run the advanced pipeline first so topic assignments exist.",
    )
    run_step(
        "Stage 2A - Export topic classification template",
        ["python", "phase1_refinement/step1_export_topics.py"],
        ".",
    )
    print(
        "\nManual action required:\n"
        "Open phase1_refinement/topic_classification.csv and fill "
        "'label', 'classification', and 'keep/remove'."
    )


def stage_phase1_refine():
    require_nonempty_column(
        "phase1_refinement/topic_classification.csv",
        "keep/remove",
        "Phase 1 classification is incomplete.",
    )
    run_step(
        "Stage 2B - Apply Phase 1 dataset refinement",
        ["python", "phase1_refinement/step2_refine_dataset.py"],
        ".",
    )


def stage_phase2_prepare():
    require_file(
        "phase1_refinement/final_curated_dataset.csv",
        "Complete Phase 1 refinement before Phase 2.",
    )
    run_step(
        "Stage 3A - Generate semantic validation report",
        ["python", "phase2_validation/step1_sampling_report.py"],
        ".",
    )
    run_step(
        "Stage 3B - Generate theme-merging template",
        ["python", "phase2_validation/generate_template.py"],
        ".",
    )
    print(
        "\nManual action required:\n"
        "Open phase2_validation/topic_merging_map.csv and fill "
        "'new_major_theme_name' for each original_topic_id."
    )


def stage_phase2_merge():
    require_nonempty_column(
        "phase2_validation/topic_merging_map.csv",
        "new_major_theme_name",
        "Phase 2 theme mapping is incomplete.",
    )
    run_step(
        "Stage 3C - Apply Phase 2 thematic merges",
        ["python", "phase2_validation/step2_apply_merges.py"],
        ".",
    )


def stage_phase3():
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
        run_step(f"Stage 4 - {script}", ["python", script], "phase3_analysis")


def stage_phase4():
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
        run_step(f"Stage 5 - {script}", ["python", script], "phase4_interpretation")


def stage_phase5():
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
        run_step(f"Stage 6 - {script}", ["python", script], "phase5_visualizations")


def stage_finalize():
    run_step(
        "Stage 7 - Build final report and consolidate FinalOutputs",
        ["python", "gather_final_outputs.py"],
        ".",
    )


def stage_all_auto():
    stage_scientometric()
    stage_advanced()
    stage_phase1_export()


def stage_post_curation():
    stage_phase1_refine()
    stage_phase2_prepare()
    print(
        "\nStop here after the template is generated, edit the Phase 2 mapping CSV, "
        "then run 'phase2-merge' or 'all-after-manual'."
    )


def stage_all_after_manual():
    stage_phase2_merge()
    stage_phase3()
    stage_phase4()
    stage_phase5()
    stage_finalize()


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
        choices=sorted(STAGES.keys()),
        help="Which stage to run.",
    )
    args = parser.parse_args()
    STAGES[args.stage]()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
