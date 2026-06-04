from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader

from core.utils import ensure_dir
from .statistics import Stats

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"


class Reporter:
    def __init__(self, reports_dir: Path, logger) -> None:
        self.reports_dir = reports_dir
        self.logger = logger
        self.env = Environment(loader=FileSystemLoader(str(TEMPLATES)))

    def write_json(self, payload: dict, output_path: Path) -> None:
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def write_csv(self, mapping: Dict[str, Dict[str, List[str]]], output_path: Path) -> None:
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["host", "category", "endpoint"])
            for host, categories in mapping.items():
                for category, endpoints in categories.items():
                    for endpoint in endpoints:
                        writer.writerow([host, category, endpoint])

    def write_html(
        self,
        template_name: str,
        output_path: Path,
        context: dict,
    ) -> None:
        template = self.env.get_template(template_name)
        html = template.render(**context)
        output_path.write_text(html, encoding="utf-8")

    def generate_reports(
        self,
        target: str,
        stats: Stats,
        categories: Dict[str, List[str]],
        mapping: Dict[str, Dict[str, List[str]]],
        timestamp: str,
        graph_path: str,
        write_json: bool,
        write_html: bool,
    ) -> None:
        ensure_dir(self.reports_dir)

        if write_json:
            payload = {
                "target": target,
                "author": "brynnnn12",
                "timestamp": timestamp,
                **stats.to_dict(),
            }
            self.write_json(payload, self.reports_dir / "report.json")

        if write_html:
            self.write_html(
                "report.html",
                self.reports_dir / "report.html",
                {
                    "target": target,
                    "timestamp": timestamp,
                    "stats": stats.to_dict(),
                    "categories": categories,
                    "mapping": mapping,
                    "graph_path": graph_path,
                },
            )

        self.write_csv(mapping, self.reports_dir / "assets.csv")

        self.logger.info("Reports saved to %s", self.reports_dir)
