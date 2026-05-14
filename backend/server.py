from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
import subprocess
import yaml
import json
import asyncio
from typing import Dict, Any, List
import sys

# Add backend to path so we can import settings and stages
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from settings import load, save

app = FastAPI(title="ResearchFlow API")

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state to track pipeline status
pipeline_status = {
    "current_stage": None,
    "is_running": False,
    "last_run": None,
    "logs": []
}

@app.get("/api/config")
async def get_config():
    try:
        return load()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config")
async def update_config(new_config: Dict[str, Any]):
    try:
        save(new_config)
        return {"status": "success", "message": "Configuration updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_pipeline_command(command: List[str]):
    global pipeline_status
    pipeline_status["is_running"] = True
    pipeline_status["logs"] = []
    
    # Run the command and capture output
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=BASE_DIR
    )

    async def read_stream(stream, prefix):
        while True:
            line = await stream.readline()
            if line:
                decoded_line = line.decode().strip()
                pipeline_status["logs"].append(f"[{prefix}] {decoded_line}")
                # Keep only last 500 lines
                if len(pipeline_status["logs"]) > 500:
                    pipeline_status["logs"].pop(0)
            else:
                break

    await asyncio.gather(
        read_stream(process.stdout, "INFO"),
        read_stream(process.stderr, "ERROR")
    )
    
    await process.wait()
    pipeline_status["is_running"] = False
    pipeline_status["last_run"] = "success" if process.returncode == 0 else "failed"

@app.post("/api/run/{stage}")
async def run_stage(stage: str, background_tasks: BackgroundTasks):
    global pipeline_status
    if pipeline_status["is_running"]:
        raise HTTPException(status_code=400, detail="Pipeline is already running")
    
    pipeline_status["current_stage"] = stage
    
    # The command to run. Assuming run.py is the orchestrator.
    command = ["python", "run.py", stage]
    
    background_tasks.add_task(run_pipeline_command, command)
    return {"status": "started", "stage": stage}

@app.get("/api/status")
async def get_status():
    return pipeline_status

@app.get("/api/logs")
async def get_logs():
    return {"logs": pipeline_status["logs"]}

@app.get("/api/stats")
async def get_stats():
    stats_path = os.path.join(BASE_DIR, "data", "share", "dataset_stats.json")
    if os.path.exists(stats_path):
        with open(stats_path, "r") as f:
            return json.load(f)
    return {"error": "Stats not found"}

@app.get("/api/topics")
async def get_topics():
    import pandas as pd
    topics_path = os.path.join(BASE_DIR, "outputs", "stats", "topic_info.csv")
    if os.path.exists(topics_path):
        df = pd.read_csv(topics_path)
        return df.to_dict(orient="records")
    return {"error": "Topics not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
