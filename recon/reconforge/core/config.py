from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


def find_and_load_dotenv() -> None:
    search_dirs = [
        Path.cwd(),
        Path(__file__).resolve().parent.parent,
        Path(__file__).resolve().parent.parent.parent.parent,
    ]
    loaded = False
    for d in search_dirs:
        env_file = d / ".env"
        if env_file.exists():
            _load_dotenv_file(env_file)
            loaded = True
    if not loaded:
        env_file = Path(__file__).resolve().parent.parent / ".env.example"
        if env_file.exists():
            pass


def _load_dotenv_file(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip("\"'")
        if key and not os.environ.get(key):
            os.environ[key] = val


@dataclass
class AppConfig:
    domain: str
    output_root: Path
    output_dir: Path
    json_enabled: bool = False
    html_enabled: bool = False
    version: str = "0.2.0"
    api_keys: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.api_keys = {
            "SHODAN_KEY": os.environ.get("SHODAN_KEY", ""),
            "SECURITYTRAILS_KEY": os.environ.get("SECURITYTRAILS_KEY", ""),
            "ALIENVAULT_KEY": os.environ.get("ALIENVAULT_KEY", ""),
            "LEAKIX_KEY": os.environ.get("LEAKIX_KEY", ""),
            "URLSCAN_KEY": os.environ.get("URLSCAN_KEY", ""),
        }
