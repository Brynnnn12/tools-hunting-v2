from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Set

from lib.utils import ensure_dir, extract_domain, now_timestamp, read_lines, safe_filename  # noqa: F401


@dataclass
class InputBundle:
    subdomains: Set[str]
    live_hosts: Set[str]
    urls: Set[str]
    js_files: Set[str]
    endpoints: Set[str]
    graphql: Set[str]
    websockets: Set[str]
    storage: Set[str]
    frameworks: Set[str]
    keywords: Set[str]
    secrets: Set[str] = field(default_factory=set)


def dedupe(items: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    ordered: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered
