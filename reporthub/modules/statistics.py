from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List


@dataclass
class Stats:
    total_subdomains: int
    total_live_hosts: int
    total_urls: int
    total_endpoints: int
    total_api: int
    total_admin: int
    total_upload: int
    total_graphql: int
    total_frameworks: int
    total_keywords: int

    def to_dict(self) -> Dict[str, int]:
        return asdict(self)

    @classmethod
    def from_data(cls, data: Dict[str, object]) -> "Stats":
        categories = data.get("categories", {}) or {}
        return cls(
            total_subdomains=len(data.get("subdomains", [])),
            total_live_hosts=len(data.get("live_hosts", [])),
            total_urls=len(data.get("urls", [])),
            total_endpoints=len(data.get("endpoints", [])),
            total_api=len(categories.get("API", [])),
            total_admin=len(categories.get("Admin", [])),
            total_upload=len(categories.get("Upload", [])),
            total_graphql=len(data.get("graphql", [])),
            total_frameworks=len(data.get("frameworks", [])),
            total_keywords=len(data.get("keywords", [])),
        )
