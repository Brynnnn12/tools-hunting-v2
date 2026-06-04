from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict


@dataclass
class Stats:
    total_subdomains: int
    total_live_hosts: int
    total_urls: int
    total_js_files: int
    total_api: int
    total_auth: int
    total_upload: int
    total_admin: int
    total_graphql: int

    def to_dict(self) -> Dict[str, int]:
        return asdict(self)

    @classmethod
    def from_data(cls, data, categories) -> "Stats":
        return cls(
            total_subdomains=len(data.subdomains),
            total_live_hosts=len(data.live_hosts),
            total_urls=len(data.urls),
            total_js_files=len(data.js_files),
            total_api=len(categories.get("API", [])),
            total_auth=len(categories.get("Authentication", [])),
            total_upload=len(categories.get("Upload", [])),
            total_admin=len(categories.get("Admin", [])),
            total_graphql=len(categories.get("GraphQL", [])),
        )
