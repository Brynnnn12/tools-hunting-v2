from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from jinja2 import Template

from core.utils import ensure_dir
from .statistics import Stats


HTML_TEMPLATE = """<!doctype html>
<html lang=\"en\" data-bs-theme=\"dark\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>JSHunter Report</title>
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css\" rel=\"stylesheet\">
    <style>
      body { background: #0f1116; }
      .card { background: #161b22; border-color: #30363d; }
      .table { color: #c9d1d9; }
      .table thead th { color: #e6edf3; }
      .badge { background: #30363d; }
    </style>
  </head>
  <body>
    <div class=\"container py-4\">
      <div class=\"d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4\">
        <div>
          <h1 class=\"h3 mb-1\">JSHunter Report</h1>
          <div class=\"text-secondary\">Target: {{ target }} | {{ timestamp }} | <span class=\"text-info\">brynnnn12</span></div>
        </div>
        <span class=\"badge rounded-pill px-3 py-2\">JavaScript Intelligence</span>
      </div>

      <div class=\"row g-3 mb-4\">
        {% for label, value in stats.items() %}
        <div class=\"col-6 col-lg-3\">
          <div class=\"card p-3 h-100\">
            <div class=\"text-secondary small\">{{ label }}</div>
            <div class=\"fs-4 fw-semibold\">{{ value }}</div>
          </div>
        </div>
        {% endfor %}
      </div>

      <div class=\"card p-3 mb-4\">
        <h2 class=\"h5\">Frameworks Detected</h2>
        <div>
          {% if frameworks %}
            {% for fw in frameworks %}
              <span class=\"badge rounded-pill me-2 mb-2\">{{ fw }}</span>
            {% endfor %}
          {% else %}
            <div class=\"text-secondary\">No frameworks detected.</div>
          {% endif %}
        </div>
      </div>

      <div class=\"card p-3 mb-4\">
        <h2 class=\"h5\">Endpoints</h2>
        <div class=\"table-responsive\">
          <table class=\"table table-sm table-hover\">
            <thead><tr><th>Endpoint</th></tr></thead>
            <tbody>
              {% for item in endpoints %}
              <tr><td>{{ item }}</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>

      <div class=\"card p-3\">
        <h2 class=\"h5\">URLs</h2>
        <div class=\"table-responsive\">
          <table class=\"table table-sm table-hover\">
            <thead><tr><th>URL</th></tr></thead>
            <tbody>
              {% for item in urls %}
              <tr><td>{{ item }}</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </body>
</html>
"""


class Reporter:
    def __init__(self, output_root: Path, logger) -> None:
        self.output_root = output_root
        self.logger = logger

    def _write_list(self, path: Path, items: Iterable[str]) -> None:
        ordered = sorted(set(items))
        content = "\n".join(ordered)
        if content:
            content += "\n"
        path.write_text(content, encoding="utf-8")

    def write_outputs(
        self,
        target: str,
        results: dict,
        stats: Stats,
        timestamp: str,
        write_json: bool,
        write_html: bool,
    ) -> None:
        target_dir = self.output_root / target
        ensure_dir(target_dir)

        self._write_list(target_dir / "endpoints.txt", results.get("endpoints", []))
        self._write_list(target_dir / "urls.txt", results.get("urls", []))
        self._write_list(target_dir / "graphql.txt", results.get("graphql", []))
        self._write_list(target_dir / "websockets.txt", results.get("websockets", []))
        self._write_list(target_dir / "storage.txt", results.get("storage", []))
        self._write_list(target_dir / "keywords.txt", results.get("keywords", []))
        self._write_list(target_dir / "frameworks.txt", results.get("frameworks", []))
        self._write_list(target_dir / "sourcemaps.txt", results.get("sourcemaps", []))
        self._write_list(target_dir / "secrets.txt", results.get("secrets", []))

        if write_json:
            report = {
                "target": target,
                "author": "brynnnn12",
                "timestamp": timestamp,
                **stats.to_dict(),
                "frameworks": sorted(results.get("frameworks", [])),
            }
            (target_dir / "report.json").write_text(
                json.dumps(report, indent=2),
                encoding="utf-8",
            )

        if write_html:
            template = Template(HTML_TEMPLATE)
            html = template.render(
                target=target,
                timestamp=timestamp,
                stats={
                    "Total JS Files": stats.total_js_files,
                    "Total Endpoints": stats.total_endpoints,
                    "Total URLs": stats.total_urls,
                    "Total GraphQL": stats.total_graphql,
                    "Total WebSockets": stats.total_websockets,
                    "Total Storage": stats.total_storage,
                    "Total Keywords": stats.total_keywords,
                },
                frameworks=sorted(results.get("frameworks", [])),
                endpoints=sorted(results.get("endpoints", [])),
                urls=sorted(results.get("urls", [])),
            )
            (target_dir / "report.html").write_text(html, encoding="utf-8")

        self.logger.info("Reports saved to %s", target_dir)
