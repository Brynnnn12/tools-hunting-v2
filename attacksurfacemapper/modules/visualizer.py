from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import networkx as nx


class Visualizer:
    def __init__(self, logger) -> None:
        self.logger = logger

    def build_graph(self, target: str, mapping: Dict[str, Dict[str, List[str]]]) -> nx.DiGraph:
        graph = nx.DiGraph()
        graph.add_node(target)
        for host, categories in mapping.items():
            graph.add_edge(target, host)
            for category in categories:
                graph.add_edge(host, category)
        return graph

    def render(self, graph: nx.DiGraph, output_path: Path) -> None:
        self.logger.info("Generating graph visualization")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(graph, k=0.7, seed=42)
        nx.draw_networkx_nodes(graph, pos, node_size=900, node_color="#2f3b52")
        nx.draw_networkx_edges(graph, pos, edge_color="#8b949e")
        nx.draw_networkx_labels(graph, pos, font_size=8, font_color="#f0f6fc")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()
