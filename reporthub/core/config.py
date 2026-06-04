from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    version: str = "1.0"
    reports_dir: Path = Path("reports")
    output_dir: Path = Path("output")
    logs_dir: Path = Path("logs")
    log_file: Path = Path("logs/reporthub.log")
