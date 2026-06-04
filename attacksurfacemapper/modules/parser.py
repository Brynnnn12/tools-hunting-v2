from __future__ import annotations

from pathlib import Path
from typing import Dict, Set

from core.utils import InputBundle, read_lines


class Parser:
    def __init__(self, logger) -> None:
        self.logger = logger

    def _read_optional(self, base: Path, name: str, alt_names: list[str] | None = None) -> Set[str]:
        path = base / name
        if path.exists():
            return set(read_lines(path))
        if alt_names:
            for alt in alt_names:
                alt_path = base / alt
                if alt_path.exists():
                    self.logger.info("Using %s as %s", alt, name)
                    return set(read_lines(alt_path))
        self.logger.warning("Missing input file: %s", path)
        return set()

    def parse(self, input_dir: Path) -> InputBundle:
        self.logger.info("Parsing input data")

        subdomains = self._read_optional(input_dir, "subdomains.txt")
        live_hosts = self._read_optional(input_dir, "live.txt", alt_names=["hosts.txt"])
        urls = self._read_optional(input_dir, "all_urls.txt", alt_names=["urls.txt"])
        js_files = self._read_optional(input_dir, "js.txt", alt_names=["js_files.txt"])

        endpoints = self._read_optional(input_dir, "endpoints.txt")
        graphql = self._read_optional(input_dir, "graphql.txt")
        websockets = self._read_optional(input_dir, "websockets.txt")
        storage = self._read_optional(input_dir, "storage.txt")
        frameworks = self._read_optional(input_dir, "frameworks.txt")
        keywords = self._read_optional(input_dir, "keywords.txt")

        return InputBundle(
            subdomains=subdomains,
            live_hosts=live_hosts,
            urls=urls,
            js_files=js_files,
            endpoints=endpoints,
            graphql=graphql,
            websockets=websockets,
            storage=storage,
            frameworks=frameworks,
            keywords=keywords,
        )
