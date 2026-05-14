"""Goal orchestrator — composes and executes research goals from capability modules."""
import os
import sys
import importlib
from pathlib import Path
from typing import Callable, Optional

BASE_DIR = Path(__file__).parent.resolve()

MODULES = {
    "acquisition": ("stages.acquisition", "run_all"),
    "topic_modeling": ("stages.topic_modeling", "run_all"),
    "trends": ("stages.analysis.trends", "run"),
    "sources": ("stages.analysis.sources", "run"),
    "geopolitical": ("stages.analysis.geopolitical", "run"),
    "networks": ("stages.analysis.networks", "run"),
    "authors": ("stages.analysis.authors", "run"),
    "evolution": ("stages.interpretation.evolution", "run"),
    "bursts": ("stages.interpretation.bursts", "run"),
    "narrative": ("stages.interpretation.narrative", "run"),
    "growth_figure": ("stages.visualization.growth", "run"),
    "keyword_network_figure": ("stages.visualization.keyword_network", "run"),
    "collaboration_figure": ("stages.visualization.collaboration", "run"),
    "thematic_evolution_figure": ("stages.visualization.thematic_evolution", "run"),
    "landscape_figure": ("stages.visualization.landscape", "run"),
    "report": ("report_builder", "run"),
    "gather": ("gather_outputs", "run"),
    "export_classification": ("stages.curation.export_classification", "run"),
    "refine_dataset": ("stages.curation.refine_dataset", "run"),
    "validate_semantics": ("stages.curation.validate_semantics", "run_all"),
    "apply_merges": ("stages.curation.apply_merges", "run"),
}

MODULE_INFO = {
    "acquisition": {"name": "Data Acquisition", "description": "Fetch papers from OpenAlex, clean, deduplicate"},
    "topic_modeling": {"name": "Topic Modeling", "description": "BERTopic clustering, embeddings, keyword networks"},
    "trends": {"name": "Trend Analysis", "description": "CAGR calculation, yearly publication counts"},
    "sources": {"name": "Source Analysis", "description": "Journal H-index, top venues"},
    "geopolitical": {"name": "Geopolitical Analysis", "description": "Country collaboration patterns"},
    "networks": {"name": "Network Analysis", "description": "Keyword and co-authorship networks"},
    "authors": {"name": "Author Analysis", "description": "Top authors by productivity and citations"},
    "evolution": {"name": "Thematic Evolution", "description": "Theme frequency over time"},
    "bursts": {"name": "Burst Detection", "description": "Z-score burst keyword detection"},
    "narrative": {"name": "Narrative Generation", "description": "AI-assisted discussion draft"},
    "growth_figure": {"name": "Growth Timeline", "description": "Figure 1: Publication growth timeline"},
    "keyword_network_figure": {"name": "Keyword Network", "description": "Figure 2: Keyword co-occurrence network"},
    "collaboration_figure": {"name": "Collaboration Map", "description": "Figure 3: Global collaboration choropleth"},
    "thematic_evolution_figure": {"name": "Thematic Evolution", "description": "Figure 4: Thematic evolution stacked area"},
    "landscape_figure": {"name": "Cluster Landscape", "description": "Figure 5: BERTopic cluster landscape"},
    "report": {"name": "Report Generation", "description": "Final research report assembly"},
    "gather": {"name": "Output Consolidation", "description": "Copy outputs to FinalOutputs/"},
    "export_classification": {"name": "Export Classification", "description": "Create topic classification CSV template"},
    "refine_dataset": {"name": "Refine Dataset", "description": "Apply manual topic classifications to filter dataset"},
    "validate_semantics": {"name": "Semantic Validation", "description": "Generate validation report and merge map template"},
    "apply_merges": {"name": "Apply Theme Merges", "description": "Consolidate topics into major themes"},
}


def _ensure_sys_path():
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))


def run_module(module_id: str, project_dir: Path, config_path: Path):
    """Execute a single capability module by ID.
    
    Sets PROJECT_DIR and RESEARCH_CONFIG env vars, reloads settings.py
    so BASE_DIR picks up the project directory, clears config cache,
    and calls the module's run function directly.
    """
    if module_id not in MODULES:
        raise ValueError(f"Unknown module: {module_id}")

    mod_path, func_name = MODULES[module_id]
    pdir_str = str(project_dir)

    os.environ["PROJECT_DIR"] = pdir_str
    os.environ["RESEARCH_CONFIG"] = str(config_path)

    _ensure_sys_path()

    # Patch settings.BASE_DIR to the current project (it's a module-level
    # constant frozen at server startup), then clear the config cache so
    # the next load() picks up the new project's config file.
    import settings as _settings_mod
    _settings_mod.BASE_DIR = pdir_str
    _settings_mod.clear_cache()

    mod = importlib.import_module(mod_path)

    # Fix stale module-level path constants. When a module is already
    # cached from a previous run with a different project, its path
    # variables (BASE_DIR, DATA_DIR, OUTPUTS_DIR, etc.) still point to
    # the old project directory. Patch them to the current project.
    _old_base = getattr(mod, "BASE_DIR", None)
    if _old_base and str(_old_base) != pdir_str:
        for _attr in dir(mod):
            _val = getattr(mod, _attr, None)
            if isinstance(_val, str) and str(_old_base) in _val:
                setattr(mod, _attr, _val.replace(str(_old_base), pdir_str))

    func = getattr(mod, func_name)
    func()


def run_goal(
    goal_id: str,
    project_dir: Path,
    config_path: Path,
    progress_callback: Optional[Callable] = None,
) -> list[dict]:
    """Execute a complete goal by running its module chain.
    
    Returns list of {module, status, error?} dicts for each step.
    """
    from goals import GOALS

    if goal_id not in GOALS:
        raise ValueError(f"Unknown goal: {goal_id}")

    goal = GOALS[goal_id]
    chain = goal["module_chain"]
    total = len(chain)
    results = []

    for i, module_id in enumerate(chain):
        info = MODULE_INFO.get(module_id, {})
        name = info.get("name", module_id)
        msg = f"({i+1}/{total}) {name}"

        if progress_callback:
            progress_callback(i, total, msg, "running")

        try:
            run_module(module_id, project_dir, config_path)
            results.append({"module": module_id, "status": "completed"})
            if progress_callback:
                progress_callback(i + 1, total, msg, "completed")
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            results.append({"module": module_id, "status": "failed", "error": err})
            if progress_callback:
                progress_callback(i + 1, total, f"{name} FAILED: {err}", "failed")
            break

    return results
