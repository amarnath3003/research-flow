"""FastAPI bridge between React frontend and the ResearchFlow pipeline."""
import os
import sys
import json
import asyncio
import subprocess
import shutil
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))
from settings import load as load_cfg

app = FastAPI(title="ResearchFlow API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory task state ──────────────────────────────────────────
pipeline_task: Optional[subprocess.Popen] = None
pipeline_log: list[str] = []
LOG_FILE = BASE_DIR / "pipeline_run.log"


# ── Helpers ───────────────────────────────────────────────────────

def _read_config_raw() -> dict:
    path = BASE_DIR / "research_config.yaml"
    if not path.exists():
        raise HTTPException(404, "Config file not found")
    with open(path) as f:
        return yaml.safe_load(f)


def _write_config_raw(cfg: dict):
    path = BASE_DIR / "research_config.yaml"
    with open(path, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)


def _csv_to_json(rel_path: str) -> list[dict]:
    import pandas as pd
    abs_path = BASE_DIR / rel_path
    if not abs_path.exists():
        raise HTTPException(404, f"File not found: {rel_path}")
    df = pd.read_csv(abs_path)
    return df.fillna("").to_dict(orient="records")


def _detect_stage_status():
    """Check which pipeline stage outputs exist to determine status."""
    checks = {
        "scientometric": BASE_DIR / "data" / "cleaned" / "final_dataset.csv",
        "advanced": BASE_DIR / "data" / "processed" / "topic_dataset.csv",
        "phase1-export": BASE_DIR / "outputs" / "stats" / "topic_classification.csv",
        "phase1-refine": BASE_DIR / "data" / "processed" / "final_curated_dataset.csv",
        "phase2-prepare": BASE_DIR / "outputs" / "stats" / "topic_merging_map.csv",
        "phase2-merge": BASE_DIR / "data" / "processed" / "final_thematic_dataset.csv",
        "phase3": BASE_DIR / "outputs" / "trends" / "trend_summary.csv",
        "phase4": BASE_DIR / "outputs" / "evolution" / "theme_evolution.csv",
        "phase5": BASE_DIR / "outputs" / "figures" / "figure1_growth_timeline.png",
        "finalize": BASE_DIR / "FINAL_RESEARCH_REPORT.md",
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
    for sid in checks:
        status = "pending"
        if checks[sid].exists():
            status = "completed"
        elif not found_current:
            status = "current"
            found_current = True
        stages.append({
            "id": sid,
            "name": stage_names.get(sid, sid),
            "description": "",
            "status": status,
        })
    return stages


# ── Config Endpoints ───────────────────────────────────────────────

@app.get("/api/config")
def get_config():
    cfg = _read_config_raw()
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


@app.post("/api/config")
def update_config(payload: ConfigPayload):
    cfg = _read_config_raw()
    cfg.setdefault("research", {})
    cfg["research"]["search_query"] = payload.searchQuery
    cfg["research"]["start_year"] = payload.startYear
    cfg["research"]["end_year"] = payload.endYear
    cfg["research"]["max_results"] = payload.maxResults
    cfg["research"]["email"] = payload.email
    cfg["research"]["description"] = payload.description
    cfg.setdefault("embedding", {})
    cfg["embedding"]["model"] = payload.embeddingModel
    cfg["embedding"]["min_topic_size"] = payload.minTopicSize
    cfg.setdefault("llm", {})
    cfg["llm"]["provider"] = payload.llmProvider
    cfg["llm"]["model"] = payload.llmModel
    _write_config_raw(cfg)
    return {"success": True}


# ── Pipeline Runner ───────────────────────────────────────────────

@app.post("/api/run/{stage}")
def run_stage(stage: str, background_tasks: BackgroundTasks):
    global pipeline_task

    valid_stages = [
        "scientometric", "advanced", "phase1-export", "phase1-refine",
        "phase2-prepare", "phase2-merge", "phase3", "phase4", "phase5",
        "finalize", "all-auto", "post-curation", "all-after-manual",
    ]
    if stage not in valid_stages:
        raise HTTPException(400, f"Invalid stage. Valid: {valid_stages}")

    runner = BASE_DIR / "run.py"
    if not runner.exists():
        raise HTTPException(500, "run.py not found")

    def _run():
        global pipeline_task, pipeline_log
        pipeline_log = []
        env = os.environ.copy()
        with open(LOG_FILE, "w") as lf:
            pipeline_task = subprocess.Popen(
                [sys.executable, str(runner), stage],
                cwd=str(BASE_DIR),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            for line in iter(pipeline_task.stdout.readline, ""):
                pipeline_log.append(line)
                with open(LOG_FILE, "a") as lf:
                    lf.write(line)
            pipeline_task.wait()
        pipeline_task = None

    background_tasks.add_task(_run)
    return {"success": True, "stage": stage, "message": f"Started {stage}"}


# ── Log Streaming (SSE) ───────────────────────────────────────────

@app.get("/api/logs/stream")
async def stream_logs():
    async def event_generator():
        sent_lines = 0
        while True:
            while sent_lines < len(pipeline_log):
                yield f"data: {json.dumps({'line': pipeline_log[sent_lines]})}\n\n"
                sent_lines += 1
            if pipeline_task is None and sent_lines >= len(pipeline_log):
                yield f"data: {json.dumps({'line': '', 'done': True})}\n\n"
                break
            await asyncio.sleep(0.1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/logs")
def get_logs():
    return {"lines": pipeline_log[-200:]}


# ── Status ─────────────────────────────────────────────────────────

@app.get("/api/status")
def get_status():
    stages = _detect_stage_status()
    total = len(stages)
    done = sum(1 for s in stages if s["status"] == "completed")
    return {
        "stages": stages,
        "progress": round(done / total * 100) if total else 0,
        "running": pipeline_task is not None,
        "currentStage": next((s["name"] for s in stages if s["status"] == "current"), None),
    }


# ── Stats (Dashboard) ──────────────────────────────────────────────

@app.get("/api/stats")
def get_stats():
    stats = {"papersFetched": 0, "uniqueTopics": 0, "keyAuthors": 0, "avgGrowthRate": "0%"}
    try:
        import pandas as pd
        ds = BASE_DIR / "data" / "processed" / "topic_dataset.csv"
        if ds.exists():
            df = pd.read_csv(ds)
            stats["papersFetched"] = len(df)
            stats["uniqueTopics"] = df["topic"].nunique() if "topic" in df.columns else 0
            if "authors" in df.columns:
                all_authors = set()
                for a in df["authors"].dropna():
                    all_authors.update(a.split(";"))
                stats["keyAuthors"] = len(all_authors)
        ts = BASE_DIR / "outputs" / "trends" / "trend_summary.csv"
        if ts.exists():
            trend = pd.read_csv(ts)
            cagr = trend[trend["Metric"] == "Total CAGR"]["Value"].values
            if len(cagr):
                stats["avgGrowthRate"] = cagr[0]
    except Exception:
        pass
    return stats


# ── Topics (Explorer) ──────────────────────────────────────────────

@app.get("/api/topics")
def get_topics():
    path = BASE_DIR / "outputs" / "stats" / "topic_info.csv"
    class_path = BASE_DIR / "outputs" / "stats" / "topic_classification.csv"
    if not path.exists():
        return []

    import pandas as pd
    df = pd.read_csv(path)
    df = df[df["Topic"] != -1].sort_values("Count", ascending=False)

    classification = {}
    if class_path.exists():
        cdf = pd.read_csv(class_path)
        for _, r in cdf.iterrows():
            classification[r["topic_id"]] = {
                "label": r.get("label", ""),
                "status": r.get("classification", ""),
            }

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


# ── Figures ────────────────────────────────────────────────────────

@app.get("/api/figures")
def list_figures():
    figs_dir = BASE_DIR / "outputs" / "figures"
    if not figs_dir.exists():
        return []
    figures = []
    for f in sorted(figs_dir.iterdir()):
        if f.suffix in (".png", ".jpg", ".jpeg", ".html"):
            figures.append({
                "filename": f.name,
                "path": f"/figures/{f.name}",
                "type": f.suffix[1:],
                "size": f.stat().st_size,
            })
    return figures


@app.get("/figures/{filename}")
def serve_figure(filename: str):
    figs_dir = BASE_DIR / "outputs" / "figures"
    path = figs_dir / filename
    if not path.exists():
        raise HTTPException(404, "Figure not found")
    return FileResponse(str(path))


# ── Report ─────────────────────────────────────────────────────────

@app.get("/api/report")
def get_report():
    path = BASE_DIR / "FINAL_RESEARCH_REPORT.md"
    if not path.exists():
        return {"content": "", "exists": False}
    with open(path) as f:
        return {"content": f.read(), "exists": True}


# ── Generic CSV data endpoint ─────────────────────────────────────

@app.get("/api/data/{data_type:path}")
def get_data(data_type: str):
    mapping = {
        "trends": "outputs/trends/yearly_counts.csv",
        "sources": "outputs/sources/top_sources.csv",
        "networks/edges": "outputs/networks/keyword_cooccurrence_edges.csv",
        "networks/nodes": "outputs/networks/keyword_nodes.csv",
        "bursts": "outputs/bursts/burst_detection.csv",
        "evolution": "outputs/evolution/theme_evolution.csv",
        "narrative": "outputs/narrative/discussion_draft.md",
    }
    if data_type not in mapping:
        raise HTTPException(404, f"Unknown data type: {data_type}")
    return _csv_to_json(mapping[data_type])


# ── Health Check ──────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "backend": str(BASE_DIR)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
