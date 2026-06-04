from __future__ import annotations

from typing import Dict, List

from core.utils import dedupe


class Aggregator:
    def __init__(self, logger) -> None:
        self.logger = logger

    def aggregate(self, data: Dict[str, object]) -> Dict[str, object]:
        subdomains = dedupe(data.get("subdomains", []))
        live_hosts = dedupe(data.get("live_hosts", []))
        urls = dedupe(data.get("urls", []))
        endpoints = dedupe(data.get("endpoints", []))
        graphql = dedupe(data.get("graphql", []))
        frameworks = dedupe(data.get("frameworks", []))
        keywords = dedupe(data.get("keywords", []))
        secrets = dedupe(data.get("secrets", []))

        asm = data.get("asm", {}) or {}
        categories = asm.get("categories", {}) if isinstance(asm, dict) else {}

        github = data.get("github", {}) or {}
        scan = data.get("scan", {}) or {}

        return {
            "subdomains": subdomains,
            "live_hosts": live_hosts,
            "urls": urls,
            "endpoints": endpoints,
            "graphql": graphql,
            "frameworks": frameworks,
            "keywords": keywords,
            "secrets": secrets,
            "categories": categories,
            "asm_raw": asm,
            "github": github,
            "scan": scan,
        }
