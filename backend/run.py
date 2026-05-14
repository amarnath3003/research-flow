#!/usr/bin/env python3
"""Single entry point for the entire research pipeline."""
import argparse
import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
from settings import load


def _call(mod_name, func_name="run_all", cfg_path=None):
    """Import and call a stage function, passing config via env var."""
    env = os.environ.copy()
    if cfg_path:
        env["RESEARCH_CONFIG"] = os.path.abspath(cfg_path)

    subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, {BASE_DIR!r}); "
         f"from settings import load; load({cfg_path!r} if {cfg_path!r} else None); "
         f"from stages.{mod_name} import {func_name}; {func_name}()"],
        env=env,
    )


def _require(path, msg):
    if not os.path.exists(os.path.join(BASE_DIR, path)):
        raise SystemExit(f"{msg}\nMissing: {path}")


def _require_column(csv_rel, col, msg):
    import pandas as pd
    path = os.path.join(BASE_DIR, csv_rel)
    _require(csv_rel, msg)
    df = pd.read_csv(path)
    if col not in df.columns:
        raise SystemExit(f"Column '{col}' not found in {csv_rel}")
    filled = df[col].fillna("").astype(str).str.strip()
    if not (filled != "").any():
        raise SystemExit(f"{msg}\nColumn '{col}' is empty in {csv_rel}")


# ── Stage Definions ───────────────────────────────────────────────

STAGES = {}


def stage(name):
    def deco(fn):
        STAGES[name] = fn
        return fn
    return deco


@stage("scientometric")
def do_scientometric(cfg_path):
    _call("acquisition", "run_all", cfg_path)


@stage("advanced")
def do_advanced(cfg_path):
    _call("topic_modeling", "run_all", cfg_path)


@stage("phase1-export")
def do_p1_export(cfg_path):
    _require("outputs/stats/topic_info.csv", "Run advanced pipeline first.")
    _call("curation.export_classification", "run", cfg_path)


@stage("phase1-refine")
def do_p1_refine(cfg_path):
    _require_column("outputs/stats/topic_classification.csv", "keep/remove",
                    "Phase 1 classification incomplete.")
    _call("curation.refine_dataset", "run", cfg_path)


@stage("phase2-prepare")
def do_p2_prepare(cfg_path):
    _require("data/processed/final_curated_dataset.csv", "Complete Phase 1 first.")
    _call("curation.validate_semantics", "run_all", cfg_path)


@stage("phase2-merge")
def do_p2_merge(cfg_path):
    _require_column("outputs/stats/topic_merging_map.csv", "new_major_theme_name",
                    "Phase 2 mapping incomplete.")
    _call("curation.apply_merges", "run", cfg_path)


@stage("phase3")
def do_phase3(cfg_path):
    _require("data/processed/final_thematic_dataset.csv", "Complete Phase 2 first.")
    _call("analysis.trends", "run", cfg_path)
    _call("analysis.sources", "run", cfg_path)
    _call("analysis.geopolitical", "run", cfg_path)
    _call("analysis.networks", "run", cfg_path)
    _call("analysis.authors", "run", cfg_path)


@stage("phase4")
def do_phase4(cfg_path):
    _require("outputs/trends/trend_summary.csv", "Run Phase 3 first.")
    _call("interpretation.evolution", "run", cfg_path)
    _call("interpretation.bursts", "run", cfg_path)
    _call("interpretation.narrative", "run", cfg_path)


@stage("phase5")
def do_phase5(cfg_path):
    _require("outputs/evolution/theme_evolution.csv", "Run Phase 4 first.")
    _call("visualization.growth", "run", cfg_path)
    _call("visualization.keyword_network", "run", cfg_path)
    _call("visualization.collaboration", "run", cfg_path)
    _call("visualization.thematic_evolution", "run", cfg_path)
    _call("visualization.landscape", "run", cfg_path)


@stage("finalize")
def do_finalize(cfg_path):
    # Run report builder and gather from the root
    env = os.environ.copy()
    if cfg_path:
        env["RESEARCH_CONFIG"] = os.path.abspath(cfg_path)

    for script in ["report_builder.py", "gather_outputs.py"]:
        path = os.path.join(BASE_DIR, script)
        subprocess.run([sys.executable, path], cwd=BASE_DIR, env=env)


@stage("all-auto")
def do_all_auto(cfg_path):
    do_scientometric(cfg_path)
    do_advanced(cfg_path)
    do_p1_export(cfg_path)


@stage("post-curation")
def do_post_curation(cfg_path):
    do_p1_refine(cfg_path)
    do_p2_prepare(cfg_path)


@stage("all-after-manual")
def do_all_after_manual(cfg_path):
    do_p2_merge(cfg_path)
    do_phase3(cfg_path)
    do_phase4(cfg_path)
    do_phase5(cfg_path)
    do_finalize(cfg_path)


# ── Init Config Generator ─────────────────────────────────────────

def generate_init_config():
    cfg_path = os.path.join(BASE_DIR, "research_config.yaml")
    if os.path.exists(cfg_path):
        if input(f"Config exists at {cfg_path}. Overwrite? (y/N): ").lower() != "y":
            return

    print("\n=== Research Config Generator ===\n")
    t = input("Research title: ").strip() or "My Research"
    d = input("Description: ").strip() or ""
    q = input("OpenAlex search query: ").strip() or ""
    s = input("Start year [2010]: ").strip() or "2010"
    e = input("End year [2025]: ").strip() or "2025"
    email = input("Your email: ").strip() or "user@example.com"

    with open(cfg_path, "w") as f:
        f.write(f"""# Research Configuration
research:
  title: "{t}"
  description: "{d}"
  search_query: |
    {q}
  start_year: {s}
  end_year: {e}
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
""")
    print(f"\nConfig written to {cfg_path}")


# ── Main ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Research Pipeline Runner")
    parser.add_argument("stage", nargs="?", choices=sorted(STAGES.keys()) + ["init"],
                        default=None, help="Stage to run, or 'init'")
    parser.add_argument("--config", default=None, help="Path to research_config.yaml")

    args = parser.parse_args()

    if args.stage == "init" or args.stage is None:
        generate_init_config()
        return

    STAGES[args.stage](args.config)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
