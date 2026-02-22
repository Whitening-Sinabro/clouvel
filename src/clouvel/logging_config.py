# -*- coding: utf-8 -*-
"""Clouvel Logging Configuration

Provides get_logger() for structured debug logging.
Controlled by CLOUVEL_DEBUG environment variable.
"""

import os
import logging


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the given module name.

    Logging level controlled by CLOUVEL_DEBUG env var:
    - Not set: WARNING (only errors/warnings)
    - "1": DEBUG (verbose)
    - "info": INFO
    """
    logger = logging.getLogger(f"clouvel.{name}")

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "[clouvel.%(name)s] %(levelname)s: %(message)s"
        ))
        logger.addHandler(handler)

    debug_level = os.getenv("CLOUVEL_DEBUG", "").lower()
    if debug_level in ("1", "true", "debug"):
        logger.setLevel(logging.DEBUG)
    elif debug_level == "info":
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    return logger
