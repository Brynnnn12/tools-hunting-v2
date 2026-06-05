from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict


from lib.dotenv import find_and_load_dotenv  # noqa: F401


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
