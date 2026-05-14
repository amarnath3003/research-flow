"""Migrate existing backend/data and backend/outputs into a Default Research Project."""
import os
import sys
import shutil
import yaml
from pathlib import Path

BASE = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE))
from db import init_db, create_project, SessionLocal, Project, get_project_dir

# Init DB first
init_db()

# Check if any projects already exist
db = SessionLocal()
try:
    existing = db.query(Project).count()
finally:
    db.close()

if existing > 0:
    print(f"Already {existing} project(s) exist. Skipping migration.")
    print("If you want to re-migrate, delete backend/app.db and backend/projects/")
    sys.exit(0)

# Create default project
project = create_project("Default Research Project", "Migrated from existing data", make_default=True)
pdir = get_project_dir(project.id)
print(f"Created project: {project.id}")

# Copy existing data directories
items_to_migrate = [
    ("data", "data"),
    ("outputs", "outputs"),
    ("models", "models"),
    ("research_config.yaml", "research_config.yaml"),
    ("FINAL_RESEARCH_REPORT.md", "FINAL_RESEARCH_REPORT.md"),
]

for src_rel, dst_rel in items_to_migrate:
    src = BASE / src_rel
    dst = pdir / dst_rel
    if src.exists():
        if src.is_dir():
            # Copy contents (don't overwrite project structure)
            for item in src.iterdir():
                if item.is_dir():
                    shutil.copytree(item, dst / item.name, dirs_exist_ok=True)
                elif item.is_file():
                    shutil.copy2(item, dst / item.name)
            print(f"  Migrated {src_rel} -> {dst_rel}")
        elif src.is_file():
            shutil.copy2(src, dst)
            print(f"  Migrated {src_rel} -> {dst_rel}")

# Copy config if it exists and wasn't already copied
src_cfg = BASE / "research_config.yaml"
dst_cfg = pdir / "research_config.yaml"
if src_cfg.exists() and src_cfg != dst_cfg:
    shutil.copy2(src_cfg, dst_cfg)
    print("  Migrated research_config.yaml")

print(f"\nMigration complete. Project directory: {pdir}")
print("You can now start the server with: python server.py")
