from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    domain: str
    output_root: Path
    output_dir: Path
    json_enabled: bool
    html_enabled: bool = False
    version: str = "0.2.0"
