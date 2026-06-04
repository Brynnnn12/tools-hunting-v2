from __future__ import annotations

import logging
from pathlib import Path


def setup_logger(log_file: Path) -> logging.Logger:
    logger = logging.getLogger("reconforge")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)

    log_file.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
