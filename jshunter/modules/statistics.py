from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Iterable


@dataclass
class Stats:
    total_js_files: int
    total_endpoints: int
    total_urls: int
    total_graphql: int
    total_websockets: int
    total_storage: int
    total_keywords: int

    def to_dict(self) -> Dict[str, int]:
        return asdict(self)

    @classmethod
    def from_results(cls, js_files: Iterable[str], results: Dict[str, set]) -> "Stats":
        return cls(
            total_js_files=len(list(js_files)),
            total_endpoints=len(results.get("endpoints", [])),
            total_urls=len(results.get("urls", [])),
            total_graphql=len(results.get("graphql", [])),
            total_websockets=len(results.get("websockets", [])),
            total_storage=len(results.get("storage", [])),
            total_keywords=len(results.get("keywords", [])),
        )
