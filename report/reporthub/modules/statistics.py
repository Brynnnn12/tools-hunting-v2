from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List


@dataclass
class Stats:
    total_subdomains: int
    total_live_hosts: int
    total_urls: int
    total_endpoints: int
    total_secrets: int
    total_api: int
    total_admin: int
    total_upload: int
    total_graphql: int
    total_frameworks: int
    total_keywords: int
    total_github_findings: int
    total_scan_ports: int

    def to_dict(self) -> Dict[str, int]:
        return asdict(self)

    @classmethod
    def from_data(cls, data: Dict[str, object]) -> "Stats":
        categories = data.get("categories", {}) or {}
        github = data.get("github", {}) or {}
        scan = data.get("scan", {}) or {}
        total_github = 0
        if isinstance(github, dict):
            for v in github.values():
                total_github += len(v) if isinstance(v, list) else 0
        scan_ports = 0
        if isinstance(scan, dict):
            nmap_data = scan.get("nmap", {}) or {}
            scan_ports = nmap_data.get("open_ports", 0) if isinstance(nmap_data, dict) else 0
        return cls(
            total_subdomains=len(data.get("subdomains", [])),
            total_live_hosts=len(data.get("live_hosts", [])),
            total_urls=len(data.get("urls", [])),
            total_endpoints=len(data.get("endpoints", [])),
            total_secrets=len(data.get("secrets", [])),
            total_api=len(categories.get("API", [])),
            total_admin=len(categories.get("Admin", [])),
            total_upload=len(categories.get("Upload", [])),
            total_graphql=len(data.get("graphql", [])),
            total_frameworks=len(data.get("frameworks", [])),
            total_keywords=len(data.get("keywords", [])),
            total_github_findings=total_github,
            total_scan_ports=scan_ports,
        )
