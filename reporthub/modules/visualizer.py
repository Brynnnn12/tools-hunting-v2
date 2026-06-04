from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt


class Visualizer:
    def __init__(self, logger) -> None:
        self.logger = logger

    def _bar_chart(self, labels: List[str], values: List[int], title: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.figure(figsize=(8, 4))
        plt.bar(labels, values, color="#4f8bff")
        plt.title(title)
        plt.xticks(rotation=20, ha="right")
        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()

    def generate(self, categories: Dict[str, List[str]], frameworks: List[str], reports_dir: Path) -> Dict[str, str]:
        self.logger.info("Generating visualization charts")
        charts = {}

        if categories:
            labels = list(categories.keys())
            values = [len(items) for items in categories.values()]
            output = reports_dir / "endpoint_chart.png"
            self._bar_chart(labels, values, "Endpoint Categories", output)
            charts["endpoint_chart"] = output.name

        if frameworks:
            labels = frameworks
            values = [1] * len(frameworks)
            output = reports_dir / "framework_chart.png"
            self._bar_chart(labels, values, "Framework Distribution", output)
            charts["framework_chart"] = output.name

        return charts
