from __future__ import annotations

from typing import Dict, Set

from .classifier import Classifier
from .extractor import Extractor


class Analyzer:
    def __init__(self, logger) -> None:
        self.extractor = Extractor()
        self.classifier = Classifier()
        self.logger = logger

    def analyze(self, contents: Dict[str, str]) -> Dict[str, Set[str]]:
        results: Dict[str, Set[str]] = {
            "endpoints": set(),
            "urls": set(),
            "graphql": set(),
            "websockets": set(),
            "storage": set(),
            "keywords": set(),
            "frameworks": set(),
            "sourcemaps": set(),
        }

        for url, content in contents.items():
            if not content:
                continue

            data = self.extractor.extract(content)
            for key in ("endpoints", "urls", "graphql", "websockets", "storage", "keywords", "sourcemaps"):
                results[key].update(data[key])

            frameworks = self.classifier.detect(content)
            results["frameworks"].update(frameworks)

        self.logger.info("Analysis complete")
        return results
