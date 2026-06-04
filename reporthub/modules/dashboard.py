from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import plotly.graph_objects as go


class DashboardBuilder:
    def __init__(self, logger) -> None:
        self.logger = logger

    def build_charts(self, categories: Dict[str, List[str]], frameworks: List[str]) -> Dict[str, str]:
        charts = {}

        if categories:
            labels = list(categories.keys())
            values = [len(items) for items in categories.values()]
            fig = go.Figure(data=[go.Bar(x=labels, y=values)])
            fig.update_layout(template="plotly_dark", height=320)
            charts["endpoint_chart"] = fig.to_html(include_plotlyjs=False, full_html=False)

        if frameworks:
            fig = go.Figure(data=[go.Pie(labels=frameworks, values=[1] * len(frameworks))])
            fig.update_layout(template="plotly_dark", height=320)
            charts["framework_chart"] = fig.to_html(include_plotlyjs=False, full_html=False)

        return charts
