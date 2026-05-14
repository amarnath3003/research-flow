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

# ── Init ───────────────────────────────────────────────────────────
init_db()

app = FastAPI(title="ResearchFlow API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

# ── Per-project pipeline state ─────────────────────────────────────
_pipeline_tasks: dict[str, subprocess.Popen] = {}
_pipeline_logs: dict[str, list[str]] = {}


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
        if p.is_default:
            raise HTTPException(400, "Cannot delete the default project")

        # Delete files BEFORE DB row to avoid orphaned data on failure
        pdir = get_project_dir(pid)
        if pdir.exists():
            shutil.rmtree(pdir)

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
    try:
        new_project = cp(payload.name.strip(), payload.description, db=db)
    finally:
        db.close()

    new_dir = get_project_dir(new_project.id)

    try:
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
        # Cleanup on failure
        if new_dir.exists():
            shutil.rmtree(new_dir)
        raise

    return {"id": new_project.id, "name": new_project.name}


# ═══════════════════════════════════════════════════════════════════
#  CONFIG (scoped to project)
# ═══════════════════════════════════════════════════════════════════

class ConfigPayload(BaseModel):
    searchQuery: str = ""
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
    llm = cfg.get("llm", {})
    return {
        "searchQuery": r.get("search_query", ""),
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
    if not payload.searchQuery.strip():
        raise HTTPException(422, "Search query is required")
    if not payload.email.strip():
        raise HTTPException(422, "Email is required")

    cfg = _read_config(pid)
    cfg.setdefault("research", {})
    cfg["research"]["search_query"] = payload.searchQuery.strip()
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
#  PIPELINE RUNNER
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/{pid}/run/{stage}")
def run_stage(pid: str, stage: str, background_tasks: BackgroundTasks):
    if stage not in VALID_STAGES:
        raise HTTPException(400, f"Invalid stage. Valid: {VALID_STAGES}")

    if pid in _pipeline_tasks and _pipeline_tasks[pid] is not None:
        ret = _pipeline_tasks[pid].poll()
        if ret is None:
            raise HTTPException(409, f"Project {pid} already has a running pipeline")

    pdir = _active_project_dir(pid)
    runner = BASE_DIR / "run.py"
    if not runner.exists():
        raise HTTPException(500, "run.py not found")

    def _run():
        _pipeline_logs[pid] = []
        env = os.environ.copy()
        env["PROJECT_DIR"] = str(pdir)
        env["RESEARCH_CONFIG"] = str(pdir / "research_config.yaml")
        log_file = pdir / "pipeline_run.log"

        proc = subprocess.Popen(
            [sys.executable, str(runner), stage],
            cwd=str(BASE_DIR),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        _pipeline_tasks[pid] = proc
        for line in iter(proc.stdout.readline, ""):
            _pipeline_logs.setdefault(pid, []).append(line)
            with open(log_file, "a") as lf:
                lf.write(line)
        proc.wait()

        if pid in _pipeline_tasks and _pipeline_tasks[pid] is proc:
            del _pipeline_tasks[pid]

        db = SessionLocal()
        try:
            p = db.query(Project).filter(Project.id == pid).first()
            if p:
                p.status = "completed" if proc.returncode == 0 else "failed"
                db.commit()
        finally:
            db.close()

    db = SessionLocal()
    try:
        p = db.query(Project).filter(Project.id == pid).first()
        if not p:
            raise HTTPException(404, "Project not found")
        p.status = "running"
        db.commit()
    finally:
        db.close()

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
            proc = _pipeline_tasks.get(pid)
            if proc is None and sent_lines >= len(log):
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
    proc = _pipeline_tasks.get(pid)
    running = proc is not None and proc.poll() is None
    return {
        "stages": stages,
        "progress": round(done / total * 100) if total else 0,
        "running": running,
        "currentStage": next((s["name"] for s in stages if s["status"] == "current"), None),
    }


# ═══════════════════════════════════════════════════════════════════
#  STATS
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/{pid}/stats")
def get_stats(pid: str):
    pdir = _active_project_dir(pid)
    stats = {"papersFetched": 0, "uniqueTopics": 0, "keyAuthors": 0, "avgGrowthRate": "0%"}
    try:
        import pandas as pd
        ds = pdir / "data" / "processed" / "topic_dataset.csv"
        if ds.exists():
            df = pd.read_csv(ds)
            stats["papersFetched"] = len(df)
            stats["uniqueTopics"] = df["topic"].nunique() if "topic" in df.columns else 0
            if "authors" in df.columns:
                all_authors = set()
                for a in df["authors"].dropna():
                    all_authors.update(a.split(";"))
                stats["keyAuthors"] = len(all_authors)
        ts = pdir / "outputs" / "trends" / "trend_summary.csv"
        if ts.exists():
            trend = pd.read_csv(ts)
            cagr = trend[trend["Metric"] == "Total CAGR"]["Value"].values
            if len(cagr):
                stats["avgGrowthRate"] = cagr[0]
    except Exception:
        pass
    return stats


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

    classification = {}
    if class_path.exists():
        cdf = pd.read_csv(class_path)
        for _, r in cdf.iterrows():
            classification[r["topic_id"]] = {"label": r.get("label", ""), "status": r.get("classification", "")}

    topics = []
    for _, r in df.iterrows():
        tid = int(r["Topic"])
        cls = classification.get(tid, {})
        topics.append({
            "id": tid,
            "label": cls.get("label", r.get("Name", "")),
            "count": int(r["Count"]),
            "keywords": "",
            "status": cls.get("status", "PENDING"),
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
    "sources": "outputs/sources/top_sources.csv",
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
#  HEALTH
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0", "projectsDir": str(PROJECTS_DIR)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
