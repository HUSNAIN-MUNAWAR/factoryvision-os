from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass(frozen=True)
class Settings:
    root: Path = Path(os.getenv("FACTORYVISION_ROOT", Path(__file__).resolve().parents[1]))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./factoryvision.db")
    artifact_dir: Path = Path(os.getenv("ARTIFACT_DIR", "artifacts"))
    secret_key: str = os.getenv("SECRET_KEY", "development-only-change-me")
    upload_max_mb: int = int(os.getenv("UPLOAD_MAX_MB", "500"))

settings = Settings()
