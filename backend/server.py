"""FastAPI bridge — multi-project, project-scoped."""
import os
import sys
import json
import asyncio
import subprocess
import shutil
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from db import init_db, create_project as cp, get_project, get_project_dir, get_project_config_path, get_default_project, Project, SessionLocal, PROJECTS_DIR
from settings import load as load_cfg, clear_cache as clear_cfg_cache
from core.orchestrator import run_goal as _orchestrate, MODULE_INFO
from goals import GOALS

# ── Init ───────────────────────────────────────────────────────────
init_db()

app = FastAPI(title="ResearchFlow API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

# ── Per-project pipeline state ─────────────────────────────────────
_pipeline_tasks: dict[str, dict] = {}
_pipeline_logs: dict[str, list[str]] = {}

# ── Per-project goal state ─────────────────────────────────────────
_goal_tasks: dict[str, dict] = {}
_goal_logs: dict[str, list[dict]] = {}
_goal_results: dict[str, list[dict]] = {}


def _active_project_dir(pid: str) -> Path:
    db = SessionLocal()
    try:
        p = get_project(pid, db=db)
        if not p:
            raise HTTPException(404, f"Project not found: {pid}")
    finally:
        db.close()
    d = get_project_dir(pid)
    if not d.exists():
        raise HTTPException(404, f"Project directory not found: {pid}")
    return d


def _read_config(pid: str) -> dict:
    path = get_project_config_path(pid)
    if not path.exists():
        raise HTTPException(404, f"Config not found for project {pid}")
    with open(path) as f:
        cfg = yaml.safe_load(f) or {}
    return cfg


def _write_config(pid: str, cfg: dict):
    path = get_project_config_path(pid)
    with open(path, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)


def _csv_to_json(pid: str, rel_path: str) -> list[dict]:
    import pandas as pd
    pdir = _active_project_dir(pid)
    abs_path = pdir / rel_path
    if not abs_path.exists():
        raise HTTPException(404, f"File not found: {rel_path}")
    try:
        df = pd.read_csv(abs_path)
        return df.fillna("").to_dict(orient="records")
    except Exception as e:
        raise HTTPException(500, f"Failed to parse {rel_path}: {e}")


def _detect_stage_status(pid: str):
    pdir = _active_project_dir(pid)
    checks = {
        "scientometric": pdir / "data" / "cleaned" / "final_dataset.csv",
        "advanced": pdir / "data" / "processed" / "topic_dataset.csv",
        "phase1-export": pdir / "outputs" / "stats" / "topic_classification.csv",
        "phase1-refine": pdir / "data" / "processed" / "final_curated_dataset.csv",
        "phase2-prepare": pdir / "outputs" / "stats" / "topic_merging_map.csv",
        "phase2-merge": pdir / "data" / "processed" / "final_thematic_dataset.csv",
        "phase3": pdir / "outputs" / "trends" / "trend_summary.csv",
        "phase4": pdir / "outputs" / "evolution" / "theme_evolution.csv",
        "phase5": pdir / "outputs" / "figures" / "figure1_growth_timeline.png",
        "finalize": pdir / "FINAL_RESEARCH_REPORT.md",
    }
    stage_names = {
        "scientometric": "Stage 0: Data Collection",
        "advanced": "Stage 1: AI Processing",
        "phase1-export": "Stage 2: Topic Export",
        "phase1-refine": "Stage 3: Manual Refinement",
        "phase2-prepare": "Stage 4: Semantic Validation",
        "phase2-merge": "Stage 5: Theme Merging",
        "phase3": "Stage 6: Quantitative Analysis",
        "phase4": "Stage 7: Interpretation",
        "phase5": "Stage 8: Visualization",
        "finalize": "Stage 9: Report Generation",
    }
    stages = []
    found_current = False
    for sid, spath in checks.items():
        status = "pending"
        if spath.exists():
            status = "completed"
        elif not found_current:
            status = "current"
            found_current = True
        stages.append({"id": sid, "name": stage_names.get(sid, sid), "description": "", "status": status})
    return stages


def _get_project_summary(pid: str) -> dict:
    db = SessionLocal()
    try:
        project = get_project(pid, db=db)
        if not project:
            raise HTTPException(404, "Project not found")
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "createdAt": project.created_at.isoformat() if project.created_at else None,
            "status": project.status,
            "isDefault": project.is_default,
        }
    finally:
        db.close()


def _compute_stats(pid: str) -> dict:
    pdir = _active_project_dir(pid)
    stats = {"papersFetched": 0, "uniqueTopics": 0, "keyAuthors": 0, "avgGrowthRate": "0%"}
    try:
        import pandas as pd

        dataset_path = pdir / "data" / "processed" / "topic_dataset.csv"
        if not dataset_path.exists():
            dataset_path = pdir / "data" / "cleaned" / "final_dataset.csv"
        if dataset_path.exists():
            df = pd.read_csv(dataset_path)
            stats["papersFetched"] = len(df)
            stats["uniqueTopics"] = df["topic"].nunique() if "topic" in df.columns else 0
            if "authors" in df.columns:
                all_authors = set()
                for author_list in df["authors"].dropna():
                    all_authors.update(a.strip() for a in str(author_list).split(";") if a.strip())
                stats["keyAuthors"] = len(all_authors)

        trend_path = pdir / "outputs" / "trends" / "trend_summary.csv"
        if trend_path.exists():
            trend = pd.read_csv(trend_path)
            cagr = trend[trend["Metric"] == "Total CAGR"]["Value"].values
            if len(cagr):
                stats["avgGrowthRate"] = cagr[0]
    except Exception:
        pass
    return stats


VALID_STAGES = [
    "scientometric", "advanced", "phase1-export", "phase1-refine",
    "phase2-prepare", "phase2-merge", "phase3", "phase4", "phase5",
    "finalize", "all-auto", "post-curation", "all-after-manual",
]


# ═══════════════════════════════════════════════════════════════════
#  PROJECT CRUD
# ═══════════════════════════════════════════════════════════════════

class CreateProjectPayload(BaseModel):
    name: str
    description: str = ""


class UpdateProjectPayload(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


@app.get("/api/projects")
def list_projects():
    db = SessionLocal()
    try:
        projects = db.query(Project).order_by(Project.created_at.desc()).all()
        return [
            {"id": p.id, "name": p.name, "description": p.description,
             "createdAt": p.created_at.isoformat() if p.created_at else None,
             "status": p.status, "isDefault": p.is_default}
            for p in projects
        ]
    finally:
        db.close()


@app.post("/api/projects")
def create_project_endpoint(payload: CreateProjectPayload):
    if not payload.name or not payload.name.strip():
        raise HTTPException(422, "Project name is required")
    db = SessionLocal()
    try:
        count = db.query(Project).count()
        project = cp(payload.name.strip(), payload.description, make_default=(count == 0), db=db)
        return {"id": project.id, "name": project.name, "description": project.description,
                "createdAt": project.created_at.isoformat() if project.created_at else None,
                "status": project.status, "isDefault": project.is_default}
    finally:
        db.close()


@app.get("/api/projects/{pid}")
def get_project_route(pid: str):
    db = SessionLocal()
    try:
        p = get_project(pid, db=db)
        if not p:
            raise HTTPException(404, "Project not found")
        return {"id": p.id, "name": p.name, "description": p.description,
                "createdAt": p.created_at.isoformat() if p.created_at else None,
                "status": p.status, "isDefault": p.is_default}
    finally:
        db.close()


@app.put("/api/projects/{pid}")
def update_project(pid: str, payload: UpdateProjectPayload):
    db = SessionLocal()
    try:
        p = db.query(Project).filter(Project.id == pid).first()
        if not p:
            raise HTTPException(404, "Project not found")
        if payload.name is not None:
            if not payload.name.strip():
                raise HTTPException(422, "Project name cannot be empty")
            p.name = payload.name.strip()
        if payload.description is not None:
            p.description = payload.description
        db.commit()
        return {"success": True}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@app.delete("/api/projects/{pid}")
def delete_project_endpoint(pid: str):
    db = SessionLocal()
    try:
        p = db.query(Project).filter(Project.id == pid).first()
        if not p:
            raise HTTPException(404, "Project not found")
        # Check for running pipeline before deletion
        if pid in _pipeline_tasks or pid in _goal_tasks:
            raise HTTPException(409, "Cannot delete project while a pipeline is running")

        # Delete files BEFORE DB row to avoid orphaned data on failure
        pdir = get_project_dir(pid)
        if pdir.exists():
            shutil.rmtree(pdir)

        # Clean up pipeline/goal state
        _pipeline_logs.pop(pid, None)
        _pipeline_tasks.pop(pid, None)
        _goal_logs.pop(pid, None)
        _goal_results.pop(pid, None)
        _goal_tasks.pop(pid, None)

        if p.is_default:
            # Reassign default to another project if any remain
            other = db.query(Project).filter(Project.id != pid).first()
            if other:
                other.is_default = True

        db.delete(p)
        db.commit()
        return {"success": True}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@app.post("/api/projects/{pid}/set-default")
def set_default_project(pid: str):
    db = SessionLocal()
    try:
        p = db.query(Project).filter(Project.id == pid).first()
        if not p:
            raise HTTPException(404, "Project not found")
        db.query(Project).update({"is_default": False})
        p.is_default = True
        db.commit()
        return {"success": True}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@app.post("/api/projects/{pid}/duplicate")
def duplicate_project(pid: str, payload: CreateProjectPayload):
    """Copy an existing project's config and data to a new project."""
    if not payload.name or not payload.name.strip():
        raise HTTPException(422, "Project name is required")

    original_dir = get_project_dir(pid)
    if not original_dir.exists():
        raise HTTPException(404, "Source project data not found")

    db = SessionLocal()
    new_project = None
    try:
        new_project = cp(payload.name.strip(), payload.description, db=db)
        new_dir = get_project_dir(new_project.id)

        # Copy data directory
        src_data = original_dir / "data"
        dst_data = new_dir / "data"
        if src_data.exists():
            shutil.copytree(src_data, dst_data, dirs_exist_ok=True)

        # Copy config
        src_cfg = original_dir / "research_config.yaml"
        dst_cfg = new_dir / "research_config.yaml"
        if src_cfg.exists():
            with open(src_cfg) as f:
                cfg = yaml.safe_load(f) or {}
            cfg.setdefault("research", {})
            cfg["research"]["title"] = payload.name.strip()
            cfg["research"]["description"] = payload.description
            with open(dst_cfg, "w") as f:
                yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)
    except Exception:
        if new_project:
            pdir = get_project_dir(new_project.id)
            if pdir.exists():
                shutil.rmtree(pdir)
            db.query(Project).filter(Project.id == new_project.id).delete()
            db.commit()
        raise
    finally:
        db.close()

    return {"id": new_project.id, "name": new_project.name}


# ═══════════════════════════════════════════════════════════════════
#  CONFIG (scoped to project)
# ═══════════════════════════════════════════════════════════════════

class ConfigPayload(BaseModel):
    searchQuery: str = ""
    includeTerms: list[str] = []
    excludeTerms: list[str] = []
    startYear: int = 2010
    endYear: int = 2025
    maxResults: int = 5000
    email: str = ""
    description: str = ""
    embeddingModel: str = "all-MiniLM-L6-v2"
    minTopicSize: int = 10
    llmProvider: Optional[str] = None
    llmModel: Optional[str] = None


@app.get("/api/{pid}/config")
def get_config(pid: str):
    cfg = _read_config(pid)
    r = cfg.get("research", {})
    e = cfg.get("embedding", {})
    cl = cfg.get("cleaning", {})
    llm = cfg.get("llm", {})
    return {
        "searchQuery": r.get("search_query", ""),
        "includeTerms": r.get("include_terms", []),
        "excludeTerms": cl.get("hard_exclusions", []),
        "startYear": r.get("start_year", 2010),
        "endYear": r.get("end_year", 2025),
        "maxResults": r.get("max_results", 5000),
        "email": r.get("email", ""),
        "description": r.get("description", ""),
        "embeddingModel": e.get("model", "all-MiniLM-L6-v2"),
        "minTopicSize": e.get("min_topic_size", 10),
        "llmProvider": llm.get("provider"),
        "llmModel": llm.get("model"),
    }


@app.post("/api/{pid}/config")
def update_config(pid: str, payload: ConfigPayload):
    if payload.startYear < 1900 or payload.endYear > 2100:
        raise HTTPException(422, "Invalid year range")
    if payload.maxResults < 1:
        raise HTTPException(422, "maxResults must be positive")
    if not payload.includeTerms and not payload.searchQuery.strip():
        raise HTTPException(422, "Search terms are required")
    if not payload.email.strip():
        raise HTTPException(422, "Email is required")

    cfg = _read_config(pid)
    cfg.setdefault("research", {})
    cfg["research"]["search_query"] = payload.searchQuery.strip()
    cfg["research"]["include_terms"] = payload.includeTerms
    cfg.setdefault("cleaning", {})
    cfg["cleaning"]["hard_exclusions"] = payload.excludeTerms
    
    cfg["research"]["start_year"] = payload.startYear
    cfg["research"]["end_year"] = payload.endYear
    cfg["research"]["max_results"] = payload.maxResults
    cfg["research"]["email"] = payload.email.strip()
    cfg["research"]["description"] = payload.description
    cfg.setdefault("embedding", {})
    cfg["embedding"]["model"] = payload.embeddingModel
    cfg["embedding"]["min_topic_size"] = max(1, payload.minTopicSize)
    cfg.setdefault("llm", {})
    cfg["llm"]["provider"] = payload.llmProvider
    cfg["llm"]["model"] = payload.llmModel
    _write_config(pid, cfg)
    clear_cfg_cache()
    return {"success": True}


# ═══════════════════════════════════════════════════════════════════
#  PIPELINE RUNNER (legacy — delegates to orchestrator)
# ═══════════════════════════════════════════════════════════════════

_STAGE_MODULES = {
    "scientometric": ["acquisition"],
    "advanced": ["topic_modeling"],
    "phase1-export": ["export_classification"],
    "phase1-refine": ["refine_dataset"],
    "phase2-prepare": ["validate_semantics"],
    "phase2-merge": ["apply_merges"],
    "phase3": ["trends", "sources", "geopolitical", "networks", "authors"],
    "phase4": ["evolution", "bursts", "narrative"],
    "phase5": ["growth_figure", "keyword_network_figure", "collaboration_figure", "thematic_evolution_figure", "landscape_figure"],
    "finalize": ["report", "gather"],
    "all-auto": ["acquisition", "topic_modeling", "export_classification"],
    "post-curation": ["refine_dataset", "validate_semantics"],
    "all-after-manual": ["apply_merges", "trends", "sources", "geopolitical", "networks", "authors", "evolution", "bursts", "narrative", "growth_figure", "keyword_network_figure", "collaboration_figure", "thematic_evolution_figure", "landscape_figure", "report", "gather"],
}


@app.post("/api/{pid}/run/{stage}")
def run_stage(pid: str, stage: str, background_tasks: BackgroundTasks):
    if stage not in VALID_STAGES:
        raise HTTPException(400, f"Invalid stage. Valid: {VALID_STAGES}")

    pdir = _active_project_dir(pid)
    cfg_path = get_project_config_path(pid)

    module_ids = _STAGE_MODULES.get(stage, [])
    if not module_ids:
        raise HTTPException(400, f"No modules mapped for stage: {stage}")

    # Validate search query before running data collection
    if stage in ("scientometric", "all-auto"):
        cfg = _read_config(pid)
        sq = cfg.get("research", {}).get("search_query", "").strip()
        if not sq:
            raise HTTPException(400,
                "Search query is empty. Go to Configuration and set a boolean search query first.")

    def _run():
        _pipeline_logs[pid] = []
        _goal_logs[pid] = []
        log_file = pdir / "pipeline_run.log"

        from core.orchestrator import run_module

        all_ok = True
        for mid in module_ids:
            info = MODULE_INFO.get(mid, {})
            msg = f"Running {info.get('name', mid)}..."
            _pipeline_logs[pid].append(msg + "\n")
            _goal_logs[pid].append({"message": msg, "status": "running"})
            with open(log_file, "a", encoding="utf-8") as lf:
                lf.write(msg + "\n")
            try:
                run_module(mid, pdir, cfg_path)
                _pipeline_logs[pid].append(f"  Complete\n")
                _goal_logs[pid].append({"message": f"{info.get('name', mid)} complete", "status": "completed"})
            except Exception as e:
                err = f"  FAILED: {e}\n"
                _pipeline_logs[pid].append(err)
                _goal_logs[pid].append({"message": f"{info.get('name', mid)} failed: {e}", "status": "failed"})
                all_ok = False
                break

        db = SessionLocal()
        try:
            p = db.query(Project).filter(Project.id == pid).first()
            if p:
                p.status = "completed" if all_ok else "failed"
                db.commit()
        finally:
            db.close()
        _pipeline_tasks.pop(pid, None)

    db = SessionLocal()
    try:
        p = db.query(Project).filter(Project.id == pid).first()
        if not p:
            raise HTTPException(404, "Project not found")
        p.status = "running"
        db.commit()
    finally:
        db.close()

    _pipeline_tasks[pid] = {"stage": stage, "running": True}
    background_tasks.add_task(_run)
    return {"success": True, "stage": stage, "project": pid, "message": f"Started {stage} for {pid}"}


# ═══════════════════════════════════════════════════════════════════
#  LOGS
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/{pid}/logs/stream")
async def stream_logs(pid: str):
    async def event_generator():
        sent_lines = 0
        while True:
            log = _pipeline_logs.get(pid, [])
            while sent_lines < len(log):
                yield f"data: {json.dumps({'line': log[sent_lines]})}\n\n"
                sent_lines += 1
            task_state = _pipeline_tasks.get(pid)
            if (task_state is None or not task_state.get("running")) and sent_lines >= len(log):
                yield f"data: {json.dumps({'line': '', 'done': True})}\n\n"
                break
            await asyncio.sleep(0.1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/{pid}/logs")
def get_logs(pid: str):
    log = _pipeline_logs.get(pid, [])
    pdir = get_project_dir(pid)
    log_file = pdir / "pipeline_run.log"
    if not log and log_file.exists():
        with open(log_file) as f:
            log = f.readlines()
    return {"lines": log[-200:]}


# ═══════════════════════════════════════════════════════════════════
#  STATUS
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/{pid}/status")
def get_status(pid: str):
    stages = _detect_stage_status(pid)
    total = len(stages)
    done = sum(1 for s in stages if s["status"] == "completed")
    running = bool(_pipeline_tasks.get(pid, {}).get("running"))
    return {
        "stages": stages,
        "progress": round(done / total * 100) if total else 0,
        "running": running,
        "currentStage": next((s["name"] for s in stages if s["status"] == "current"), None),
    }


@app.get("/api/{pid}/workspace")
def get_workspace(pid: str):
    return _get_workspace(pid)


# ═══════════════════════════════════════════════════════════════════
#  CSV Editor (serve/save for manual curation files)
# ═══════════════════════════════════════════════════════════════════

ALLOWED_CSVS = {
    "topic_classification.csv": "outputs/stats/topic_classification.csv",
    "topic_merging_map.csv": "outputs/stats/topic_merging_map.csv",
}


@app.get("/api/{pid}/csv/{filename}")
def get_csv(pid: str, filename: str):
    if filename not in ALLOWED_CSVS:
        raise HTTPException(404, f"Unknown CSV: {filename}")
    pdir = _active_project_dir(pid)
    path = pdir / ALLOWED_CSVS[filename]
    if not path.exists():
        raise HTTPException(404, f"CSV not found. Run the preceding stage first.")
    import pandas as pd
    df = pd.read_csv(path)
    return {
        "columns": list(df.columns),
        "rows": df.fillna("").to_dict(orient="records"),
        "filename": filename,
    }


class CsvSavePayload(BaseModel):
    rows: list[dict]


@app.post("/api/{pid}/csv/{filename}")
def save_csv(pid: str, filename: str, payload: CsvSavePayload):
    if filename not in ALLOWED_CSVS:
        raise HTTPException(404, f"Unknown CSV: {filename}")
    pdir = _active_project_dir(pid)
    path = pdir / ALLOWED_CSVS[filename]
    import pandas as pd
    df = pd.DataFrame(payload.rows)
    df.to_csv(path, index=False)
    return {"success": True, "rows": len(df)}


# ═══════════════════════════════════════════════════════════════════
#  STATS
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/{pid}/stats")
def get_stats(pid: str):
    return _compute_stats(pid)


# ═══════════════════════════════════════════════════════════════════
#  TOPICS
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/{pid}/topics")
def get_topics(pid: str):
    pdir = _active_project_dir(pid)
    path = pdir / "outputs" / "stats" / "topic_info.csv"
    class_path = pdir / "outputs" / "stats" / "topic_classification.csv"
    if not path.exists():
        return []

    import pandas as pd
    df = pd.read_csv(path)
    df = df[df["Topic"] != -1].sort_values("Count", ascending=False)

    def _clean(value, fallback=""):
        return fallback if pd.isna(value) else value

    classification = {}
    if class_path.exists():
        cdf = pd.read_csv(class_path)
        for _, r in cdf.iterrows():
            classification[r["topic_id"]] = {
                "label": _clean(r.get("label", ""), ""),
                "status": _clean(r.get("classification", ""), ""),
            }

    topics = []
    for _, r in df.iterrows():
        tid = int(r["Topic"])
        cls = classification.get(tid, {})
        topics.append({
            "id": tid,
            "label": _clean(cls.get("label", r.get("Name", "")), ""),
            "count": int(r["Count"]),
            "keywords": "",
            "status": _clean(cls.get("status", "PENDING"), "PENDING"),
        })
    return topics


# ═══════════════════════════════════════════════════════════════════
#  FIGURES
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/{pid}/figures")
def list_figures(pid: str):
    pdir = _active_project_dir(pid)
    figs_dir = pdir / "outputs" / "figures"
    if not figs_dir.exists():
        return []
    figures = []
    for f in sorted(figs_dir.iterdir()):
        if f.suffix in (".png", ".jpg", ".jpeg", ".html"):
            figures.append({
                "filename": f.name,
                "path": f"/figures/{pid}/{f.name}",
                "type": f.suffix[1:],
                "size": f.stat().st_size,
            })
    return figures


@app.get("/figures/{pid}/{filename}")
def serve_figure(pid: str, filename: str):
    pdir = _active_project_dir(pid)
    path = pdir / "outputs" / "figures" / filename
    if not path.exists():
        raise HTTPException(404, "Figure not found")
    return FileResponse(str(path))


# ═══════════════════════════════════════════════════════════════════
#  REPORT
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/{pid}/report")
def get_report(pid: str):
    pdir = _active_project_dir(pid)
    path = pdir / "FINAL_RESEARCH_REPORT.md"
    if not path.exists():
        return {"content": "", "exists": False}
    with open(path) as f:
        return {"content": f.read(), "exists": True}


# ═══════════════════════════════════════════════════════════════════
#  DATA
# ═══════════════════════════════════════════════════════════════════

MAPPING = {
    "trends": "outputs/trends/yearly_counts.csv",
    "trends/summary": "outputs/trends/trend_summary.csv",
    "sources": "outputs/sources/top_sources.csv",
    "authors": "outputs/stats/top_authors.csv",
    "geopolitical": "outputs/geopolitical/country_collaboration.csv",
    "networks/edges": "outputs/networks/keyword_cooccurrence_edges.csv",
    "networks/nodes": "outputs/networks/keyword_nodes.csv",
    "bursts": "outputs/bursts/burst_detection.csv",
    "evolution": "outputs/evolution/theme_evolution.csv",
}

TEXT_DATA_TYPES = {"narrative": "outputs/narrative/discussion_draft.md"}

ALL_DATA_TYPES = {**MAPPING, **TEXT_DATA_TYPES}


@app.get("/api/{pid}/data/{data_type:path}")
def get_data(pid: str, data_type: str):
    if data_type in MAPPING:
        return _csv_to_json(pid, MAPPING[data_type])
    if data_type in TEXT_DATA_TYPES:
        pdir = _active_project_dir(pid)
        path = pdir / TEXT_DATA_TYPES[data_type]
        if not path.exists():
            raise HTTPException(404, f"File not found: {TEXT_DATA_TYPES[data_type]}")
        with open(path) as f:
            return {"content": f.read()}
    raise HTTPException(404, f"Unknown data type: {data_type}")


# ═══════════════════════════════════════════════════════════════════
#  GOALS (goal-oriented research endpoints)
# ═══════════════════════════════════════════════════════════════════


@app.get("/api/{pid}/goals")
def list_goal_definitions(pid: str):
    """List available research goals with metadata (no module_chain)."""
    return [
        {
            "id": gid,
            "name": g["name"],
            "description": g["description"],
            "icon": g["icon"],
            "color": g.get("color", "#6366f1"),
            "outputs": g["outputs"],
            "supportsRefinement": g.get("supports_refinement", False),
            "estimatedMinutes": g.get("estimated_minutes", ""),
            "numSteps": len(g["module_chain"]),
        }
        for gid, g in GOALS.items()
    ]


@app.post("/api/{pid}/run-goal/{goal_id}")
async def run_goal_endpoint(pid: str, goal_id: str, background_tasks: BackgroundTasks):
    """Execute a research goal asynchronously."""
    if goal_id not in GOALS:
        raise HTTPException(400, f"Unknown goal: {goal_id}. Available: {list(GOALS.keys())}")

    pdir = _active_project_dir(pid)
    cfg_path = get_project_config_path(pid)

    if not cfg_path.exists():
        raise HTTPException(400, "No configuration found. Set up your research config first.")

    # Check for search query
    cfg = _read_config(pid)
    sq = cfg.get("research", {}).get("search_query", "").strip()
    if not sq:
        raise HTTPException(400, "Search query is empty. Go to Configuration and set a boolean search query first.")

    def _run():
        _goal_logs[pid] = []
        _goal_results[pid] = []

        def _progress(current, total, message, status):
            entry = {"current": current, "total": total, "message": message, "status": status}
            _goal_logs.setdefault(pid, []).append(entry)

        try:
            results = _orchestrate(goal_id, pdir, cfg_path, progress_callback=_progress)
            _goal_results[pid] = results
            db = SessionLocal()
            try:
                p = db.query(Project).filter(Project.id == pid).first()
                if p:
                    all_ok = all(r["status"] == "completed" for r in results)
                    p.status = "completed" if all_ok else "failed"
                    db.commit()
            finally:
                db.close()
        except Exception as e:
            _goal_results[pid] = [{"module": "orchestrator", "status": "failed", "error": str(e)}]

        if pid in _goal_tasks:
            del _goal_tasks[pid]

    _goal_tasks[pid] = {"goal_id": goal_id, "running": True}
    db = SessionLocal()
    try:
        p = db.query(Project).filter(Project.id == pid).first()
        if p:
            p.status = "running"
            db.commit()
    finally:
        db.close()

    background_tasks.add_task(_run)
    return {"success": True, "goal": goal_id, "project": pid, "message": f"Started goal '{GOALS[goal_id]['name']}'"}


@app.get("/api/{pid}/goal-status")
def get_goal_status(pid: str):
    """Get completion status for all goals by checking output file existence."""
    return _list_goal_statuses(pid)


def _product_path_for_module(module_id: str, pdir: Path) -> Optional[Path]:
    """Map a module ID to its primary output file for status detection."""
    mapping = {
        "acquisition": "data/cleaned/final_dataset.csv",
        "topic_modeling": "data/processed/topic_dataset.csv",
        "trends": "outputs/trends/trend_summary.csv",
        "sources": "outputs/sources/top_sources.csv",
        "geopolitical": "outputs/geopolitical/country_collaboration.csv",
        "networks": "outputs/networks/keyword_cooccurrence_edges.csv",
        "authors": "outputs/stats/top_authors.csv",
        "evolution": "outputs/evolution/theme_evolution.csv",
        "bursts": "outputs/bursts/burst_detection.csv",
        "narrative": "outputs/narrative/discussion_draft.md",
        "growth_figure": "outputs/figures/figure1_growth_timeline.png",
        "keyword_network_figure": "outputs/figures/figure2_keyword_network.png",
        "collaboration_figure": "outputs/figures/figure3_collaboration_map.png",
        "thematic_evolution_figure": "outputs/figures/figure4_thematic_evolution.png",
        "landscape_figure": "outputs/figures/figure5_cluster_landscape.png",
        "report": "FINAL_RESEARCH_REPORT.md",
        "gather": "FinalOutputs/MANIFEST.txt",
    }
    rel = mapping.get(module_id)
    if rel:
        path = pdir / rel
        return path
    return None


def _list_goal_statuses(pid: str) -> dict:
    pdir = get_project_dir(pid)
    if not pdir.exists():
        raise HTTPException(404, "Project directory not found")

    running_goal = _goal_tasks.get(pid, {}).get("goal_id") if _goal_tasks.get(pid, {}).get("running") else None
    statuses = {}

    for gid, goal in GOALS.items():
        done = sum(
            1
            for module_id in goal["module_chain"]
            if (product_path := _product_path_for_module(module_id, pdir)) is not None and product_path.exists()
        )
        statuses[gid] = {
            "done": done,
            "total": len(goal["module_chain"]),
            "complete": done == len(goal["module_chain"]),
            "running": running_goal == gid,
        }

    return statuses


def _get_workspace(pid: str) -> dict:
    project = _get_project_summary(pid)
    cfg = _read_config(pid)
    stats = _compute_stats(pid)
    goal_statuses = _list_goal_statuses(pid)
    figures = list_figures(pid)
    report = get_report(pid)
    topics = get_topics(pid)
    refinements = get_refinement_options(pid)

    research = cfg.get("research", {})
    cleaning = cfg.get("cleaning", {})
    embedding = cfg.get("embedding", {})
    llm = cfg.get("llm", {})

    query = research.get("search_query", "").strip()
    configured = bool(query and research.get("email", "").strip())
    missing = []
    if not query:
        missing.append("Add a search strategy")
    if not research.get("email", "").strip():
        missing.append("Provide an email for OpenAlex polite-pool access")

    goals = []
    for gid, meta in GOALS.items():
        goals.append({
            "id": gid,
            "name": meta["name"],
            "description": meta["description"],
            "icon": meta["icon"],
            "color": meta.get("color", "#6366f1"),
            "outputs": meta["outputs"],
            "supportsRefinement": meta.get("supports_refinement", False),
            "estimatedMinutes": meta.get("estimated_minutes", ""),
            "numSteps": len(meta["module_chain"]),
            "status": goal_statuses.get(gid, {}),
        })

    classified_topics = sum(1 for topic in topics if topic.get("status") and topic.get("status") != "PENDING")

    return {
        "project": project,
        "config": {
            "searchQuery": query,
            "includeTerms": research.get("include_terms", []),
            "excludeTerms": cleaning.get("hard_exclusions", []),
            "startYear": research.get("start_year", 2010),
            "endYear": research.get("end_year", 2025),
            "maxResults": research.get("max_results", 5000),
            "email": research.get("email", ""),
            "description": research.get("description", ""),
            "embeddingModel": embedding.get("model", "all-MiniLM-L6-v2"),
            "minTopicSize": embedding.get("min_topic_size", 10),
            "llmProvider": llm.get("provider"),
            "llmModel": llm.get("model"),
        },
        "readiness": {
            "configured": configured,
            "missing": missing,
            "hasDataset": stats["papersFetched"] > 0,
            "hasTopics": len(topics) > 0,
            "hasReport": report.get("exists", False),
            "hasFigures": len(figures) > 0,
            "activeRun": _goal_tasks.get(pid) or _pipeline_tasks.get(pid),
            "classifiedTopics": classified_topics,
        },
        "stats": stats,
        "goalStatus": goal_statuses,
        "goals": goals,
        "refinements": refinements,
        "topicsPreview": topics[:6],
        "figuresPreview": figures[:4],
        "report": {
            "exists": report.get("exists", False),
            "preview": "\n".join(report.get("content", "").splitlines()[:12]).strip(),
        },
    }


@app.get("/api/{pid}/goal-logs/stream")
async def stream_goal_logs(pid: str):
    """SSE stream of goal execution progress events."""
    async def event_generator():
        sent = 0
        while True:
            log = _goal_logs.get(pid, [])
            while sent < len(log):
                yield f"data: {json.dumps(log[sent])}\n\n"
                sent += 1
            is_done = pid not in _goal_tasks or not _goal_tasks[pid].get("running")
            if is_done and sent >= len(log):
                yield f"data: {json.dumps({'done': True})}\n\n"
                break
            await asyncio.sleep(0.15)
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/{pid}/goal-logs")
def get_goal_logs(pid: str):
    """Get goal execution progress log as plain JSON."""
    return {"log": _goal_logs.get(pid, [])}


@app.get("/api/{pid}/goal-results")
def get_goal_results(pid: str):
    """Get the results of the last goal execution."""
    return {"results": _goal_results.get(pid, [])}


# ═══════════════════════════════════════════════════════════════════
#  REFINEMENT (post-hoc curation after seeing results)
# ═══════════════════════════════════════════════════════════════════


REFINEMENT_STEPS = {
    "classify": {
        "name": "Topic Classification",
        "description": "Export classification CSV, apply manual labels to filter dataset, and regenerate validation report.",
        "steps": ["export_classification", "refine_dataset", "validate_semantics"],
    },
    "merge": {
        "name": "Theme Merging",
        "description": "Apply manual theme merges to consolidate topics into major themes.",
        "steps": ["apply_merges"],
    },
}


@app.get("/api/{pid}/refinement-options")
def get_refinement_options(pid: str):
    """List available refinement steps based on what data exists."""
    pdir = get_project_dir(pid)
    if not pdir.exists():
        raise HTTPException(404, "Project directory not found")

    options = []
    # classify: available if topic_modeling has been run
    has_topics = (pdir / "data" / "processed" / "topic_dataset.csv").exists()
    # merge: available if validation report already exists
    has_validation = (pdir / "outputs" / "stats" / "topic_merging_map.csv").exists()

    if has_topics:
        options.append({
            "id": "classify",
            "name": "Classify Topics",
            "description": "Tag topics as CORE, SUPPORTING, or NOISE to filter your dataset",
            "csvFile": "topic_classification.csv",
            "steps": REFINEMENT_STEPS["classify"]["steps"],
        })
    if has_topics:
        options.append({
            "id": "merge",
            "name": "Merge into Themes",
            "description": "Group similar topics into major research themes (requires classification first)",
            "csvFile": "topic_merging_map.csv",
            "steps": REFINEMENT_STEPS["merge"]["steps"],
        })

    return options


@app.post("/api/{pid}/refine/{refinement_id}")
async def run_refinement(pid: str, refinement_id: str, background_tasks: BackgroundTasks):
    """Run a post-hoc refinement step (classification or theme merging)."""
    if refinement_id not in REFINEMENT_STEPS:
        raise HTTPException(400, f"Unknown refinement: {refinement_id}")

    pdir = _active_project_dir(pid)
    cfg_path = get_project_config_path(pid)
    ref = REFINEMENT_STEPS[refinement_id]

    def _run():
        _goal_logs[pid] = []  # reuse goal log streaming
        _goal_results[pid] = []

        def _progress(current, total, message, status):
            _goal_logs.setdefault(pid, []).append({
                "current": current, "total": total, "message": message, "status": status,
            })

        results = []
        try:
            for i, mid in enumerate(ref["steps"]):
                info = MODULE_INFO.get(mid, {})
                name = info.get("name", mid)
                msg = f"({i+1}/{len(ref['steps'])}) {name}"
                _progress(i, len(ref["steps"]), msg, "running")
                try:
                    from core.orchestrator import run_module as _rm
                    _rm(mid, pdir, cfg_path)
                    results.append({"module": mid, "status": "completed"})
                    _progress(i + 1, len(ref["steps"]), msg, "completed")
                except Exception as e:
                    err = f"{type(e).__name__}: {e}"
                    results.append({"module": mid, "status": "failed", "error": err})
                    _progress(i + 1, len(ref["steps"]), f"{name} FAILED: {err}", "failed")
                    break
            _goal_results[pid] = results
        finally:
            _goal_tasks.pop(pid, None)

    _goal_tasks[pid] = {"goal_id": f"refinement:{refinement_id}", "running": True}
    background_tasks.add_task(_run)
    return {"success": True, "refinement": refinement_id, "steps": ref["steps"]}


# ═══════════════════════════════════════════════════════════════════
#  HEALTH
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0", "projectsDir": str(PROJECTS_DIR)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
