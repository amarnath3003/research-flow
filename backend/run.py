#!/usr/bin/env python3
"""CLI entry point — delegates to the goal orchestrator."""
import argparse
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))


def main():
    parser = argparse.ArgumentParser(description="Research Tool — Goal Runner")
    parser.add_argument("goal", nargs="?", default=None,
                        help="Goal ID to run (e.g., landscape, topics, trends, experts, evolution, quick-scan)")
    parser.add_argument("--config", default=None, help="Path to research_config.yaml")
    parser.add_argument("--list", action="store_true", help="List available goals")

    args = parser.parse_args()

    from goals import GOALS

    if args.list:
        print("\nAvailable research goals:\n")
        for gid, g in GOALS.items():
            print(f"  {gid:15s} {g['name']}")
            print(f"  {'':15s} {g['description'][:80]}...")
            print(f"  {'':15s} Steps: {len(g['module_chain'])} | Supports refinement: {g.get('supports_refinement', False)}")
            print()
        return

    if args.goal is None or args.goal not in GOALS:
        print(f"Usage: python run.py <goal> [--config path] [--list]")
        print(f"Available goals: {', '.join(GOALS.keys())}")
        sys.exit(1)

    goal_id = args.goal
    goal = GOALS[goal_id]

    if args.config:
        config_path = Path(args.config)
    else:
        config_path = BASE_DIR / "research_config.yaml"

    project_dir = Path(os.environ.get("PROJECT_DIR", BASE_DIR))

    if not config_path.exists():
        print(f"Config not found at {config_path}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  Goal: {goal['name']}")
    print(f"  Project: {project_dir.name}")
    print(f"{'='*60}\n")

    from core.orchestrator import run_goal as _orchestrate

    def _log(current, total, message, status):
        icon = {"running": "▶", "completed": "✓", "failed": "✗"}.get(status, "•")
        print(f"  {icon} {message}")

    results = _orchestrate(goal_id, project_dir, config_path, progress_callback=_log)

    print(f"\n{'='*60}")
    failed = [r for r in results if r["status"] == "failed"]
    if failed:
        print(f"  Completed with {len(failed)} failure(s):")
        for r in failed:
            print(f"    ✗ {r['module']}: {r.get('error', 'unknown')}")
    else:
        print(f"  ✓ All {len(results)} steps completed successfully.")
    print(f"{'='*60}\n")

    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
