from __future__ import annotations

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

    def write_html(self, template_name: str, output_path: Path, context: dict) -> None:
        template = self.env.get_template(template_name)
        html = template.render(**context)
        output_path.write_text(html, encoding="utf-8")

    def generate(
        self,
        target: str,
        timestamp: str,
        stats: Stats,
        data: Dict[str, object],
        charts: Dict[str, str],
        dashboard_snippets: Dict[str, str],
        include_html: bool,
        include_dashboard: bool,
        include_json: bool,
    ) -> None:
        ensure_dir(self.reports_dir)

        if include_json:
            payload = {
                "target": target,
                "author": "brynnnn12",
                "subdomains": stats.total_subdomains,
                "live_hosts": stats.total_live_hosts,
                "urls": stats.total_urls,
                "endpoints": stats.total_endpoints,
                "graphql": stats.total_graphql,
                "frameworks": stats.total_frameworks,
                "generated_at": timestamp.split(" ")[0],
            }
            self.write_json(payload, self.reports_dir / "report.json")

        if include_html:
            self.write_html(
                "report.html",
                self.reports_dir / "report.html",
                {
                    "target": target,
                    "timestamp": timestamp,
                    "stats": stats.to_dict(),
                    "data": data,
                    "charts": charts,
                },
            )

        if include_dashboard:
            self.write_html(
                "dashboard.html",
                self.reports_dir / "dashboard.html",
                {
                    "target": target,
                    "timestamp": timestamp,
                    "stats": stats.to_dict(),
                    "data": data,
                    "charts": charts,
                    "dashboard_snippets": dashboard_snippets,
                },
            )

        self.logger.info("Report generation completed")
