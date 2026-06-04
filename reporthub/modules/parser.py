from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from core.utils import InputPaths, read_json, read_lines


class Parser:
    def __init__(self, logger) -> None:
        self.logger = logger

    def _read_optional_lines(self, path: Path, alt_paths: list[Path] | None = None) -> List[str]:
        if path.exists():
            return read_lines(path)
        if alt_paths:
            for alt in alt_paths:
                if alt.exists():
                    self.logger.info("Using %s as %s", alt.name, path.name)
                    return read_lines(alt)
        self.logger.warning("Missing file: %s", path)
        return []

    def _read_optional_json(self, path: Path) -> dict:
        if not path.exists():
            self.logger.warning("Missing file: %s", path)
            return {}
        try:
            return read_json(path)
        except ValueError as exc:
            self.logger.error("Malformed JSON %s: %s", path, exc)
            return {}

    def parse(self, input_dir: Path) -> Dict[str, object]:
        self.logger.info("Parsing ReconForge output")
        recon_dir = input_dir / "recon"
        jshunter_dir = input_dir / "jshunter"
        asm_dir = input_dir / "asm"

        data = {
            "subdomains": self._read_optional_lines(recon_dir / "subdomains.txt"),
            "live_hosts": self._read_optional_lines(recon_dir / "live.txt", alt_paths=[recon_dir / "hosts.txt"]),
            "urls": self._read_optional_lines(recon_dir / "urls.txt"),
            "endpoints": self._read_optional_lines(jshunter_dir / "endpoints.txt"),
            "graphql": self._read_optional_lines(jshunter_dir / "graphql.txt"),
            "frameworks": self._read_optional_lines(jshunter_dir / "frameworks.txt"),
            "keywords": self._read_optional_lines(jshunter_dir / "keywords.txt"),
            "asm": self._read_optional_json(asm_dir / "attack_surface.json"),
            "attack_surface_png": asm_dir / "attack_surface.png",
        }

        self.logger.info("Parsing JSHunter output")
        if not jshunter_dir.exists():
            self.logger.warning("Missing JSHunter folder: %s", jshunter_dir)

        self.logger.info("Parsing ASM output")
        if not asm_dir.exists():
            self.logger.warning("Missing ASM folder: %s", asm_dir)

        return data
