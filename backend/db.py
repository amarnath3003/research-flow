"""SQLite database for project metadata management."""
import os
import uuid
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).parent.resolve()
DB_PATH = BASE_DIR / "app.db"
PROJECTS_DIR = BASE_DIR / "projects"

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    status = Column(String, default="idle")
    is_default = Column(Boolean, default=False)


def init_db():
    Base.metadata.create_all(bind=engine)
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    _repair_project_state()


def _repair_project_state():
    """Clean orphaned dirs and fix missing configs for existing projects."""
    db = SessionLocal()
    try:
        # Get all project IDs from DB
        db_ids = {p.id for p in db.query(Project.id).all()}

        # Remove orphaned directories (no DB record)
        orphans_removed = 0
        for d in PROJECTS_DIR.iterdir():
            if d.is_dir() and d.name not in db_ids:
                shutil.rmtree(d)
                orphans_removed += 1
        if orphans_removed:
            print(f"  Cleaned {orphans_removed} orphaned project directories")

        # Fix projects with missing directories or configs
        from settings import _normalize
        import yaml
        fixed = 0
        for p in db.query(Project).all():
            pdir = PROJECTS_DIR / p.id
            cfg_path = pdir / "research_config.yaml"

            if not pdir.exists():
                # Recreate full directory structure
                for d in ["data/raw", "data/cleaned", "data/processed", "data/exports", "data/share",
                           "outputs/figures", "outputs/stats", "outputs/reports", "outputs/networks",
                           "outputs/trends", "outputs/sources", "outputs/geopolitical",
                           "outputs/evolution", "outputs/bursts", "outputs/narrative", "models"]:
                    (pdir / d).mkdir(parents=True, exist_ok=True)
                fixed += 1

            if not cfg_path.exists():
                default_cfg = {"research": {"title": p.name, "description": p.description or ""},
                               "cleaning": {"enabled": True}, "embedding": {}, "llm": {},
                               "tracking": {}, "visualizations": {}}
                _normalize(default_cfg)
                with open(cfg_path, "w") as f:
                    yaml.dump(default_cfg, f, default_flow_style=False, allow_unicode=True)
                fixed += 1

        if fixed:
            print(f"  Repaired {fixed} projects with missing directories/configs")
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_project(name: str, description: str = "", make_default: bool = False, db: Optional[SessionLocal] = None) -> Project:
    close = db is None
    if db is None:
        db = SessionLocal()
    try:
        pid = str(uuid.uuid4())
        project = Project(id=pid, name=name, description=description, status="idle", is_default=make_default)
        db.add(project)

        if make_default:
            db.query(Project).filter(Project.id != pid).update({"is_default": False})

        # Create project directory structure BEFORE commit to prevent orphaned records
        pdir = PROJECTS_DIR / pid
        for d in ["data/raw", "data/cleaned", "data/processed", "data/exports", "data/share",
                   "outputs/figures", "outputs/stats", "outputs/reports", "outputs/networks",
                   "outputs/trends", "outputs/sources", "outputs/geopolitical",
                   "outputs/evolution", "outputs/bursts", "outputs/narrative", "models"]:
            (pdir / d).mkdir(parents=True, exist_ok=True)

        # Write default config
        from settings import _normalize
        import yaml
        default_cfg = {
            "research": {"title": name, "description": description},
            "cleaning": {"enabled": True},
            "embedding": {},
            "llm": {},
            "tracking": {},
            "visualizations": {},
        }
        _normalize(default_cfg)
        with open(pdir / "research_config.yaml", "w") as f:
            yaml.dump(default_cfg, f, default_flow_style=False, allow_unicode=True)

        db.commit()
        db.refresh(project)

        return project
    except Exception:
        db.rollback()
        # Clean up any partially-created directory
        pdir = PROJECTS_DIR / pid
        if pdir.exists():
            shutil.rmtree(pdir)
        raise
    finally:
        if close:
            db.close()


def delete_project(pid: str, db: Optional[SessionLocal] = None):
    close = db is None
    if db is None:
        db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == pid).first()
        if not project:
            return False

        # Remove files BEFORE DB row to avoid orphaned data on failure
        pdir = PROJECTS_DIR / pid
        if pdir.exists():
            shutil.rmtree(pdir)

        db.delete(project)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        if close:
            db.close()


def get_project_dir(pid: str) -> Path:
    return PROJECTS_DIR / pid


def get_project_config_path(pid: str) -> Path:
    return get_project_dir(pid) / "research_config.yaml"


def get_default_project(db: Optional[SessionLocal] = None) -> Optional[Project]:
    close = db is None
    if db is None:
        db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.is_default == True).first()
        if project:
            return project
        project = db.query(Project).order_by(Project.created_at).first()
        return project
    finally:
        if close:
            db.close()


def get_project(pid: str, db: Optional[SessionLocal] = None) -> Optional[Project]:
    close = db is None
    if db is None:
        db = SessionLocal()
    try:
        return db.query(Project).filter(Project.id == pid).first()
    finally:
        if close:
            db.close()
