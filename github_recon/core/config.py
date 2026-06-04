from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    token: str = ""
    per_page: int = 100
    user_agent: str = "GitHubRecon/1.0"
    output_dir: str = "output"
    sleep_on_limit: float = 60.0
    max_results: int = 500
    search_queries: List[str] = field(default_factory=lambda: [
        "{domain}",
        "\"{domain}\" key",
        "\"{domain}\" config",
    ])
