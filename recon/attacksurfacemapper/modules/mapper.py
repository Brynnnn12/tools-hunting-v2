from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List
from urllib.parse import urlparse


class Mapper:
    def __init__(self, logger) -> None:
        self.logger = logger

    def correlate(self, urls: Iterable[str], categories: Dict[str, List[str]]) -> Dict[str, Dict[str, List[str]]]:
        mapping: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
        for url in urls:
            host = urlparse(url).netloc or "unknown"
            path = urlparse(url).path or "/"
            for category, endpoints in categories.items():
                for endpoint in endpoints:
                    if endpoint in path:
                        mapping[host][category].append(path)
        return mapping
