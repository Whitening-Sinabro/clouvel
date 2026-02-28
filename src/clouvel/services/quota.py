# -*- coding: utf-8 -*-
"""Quota Service — Business logic for rate limits and feature quotas.

Extracts quota/limit logic from tool_dispatch.py _wrap_* functions.
"""

from dataclasses import dataclass
from typing import Optional

# Constants
FREE_PERSPECTIVES_MANAGERS = 2
FREE_PERSPECTIVES_QUESTIONS = 1
PRO_DEFAULT_PERSPECTIVES_MANAGERS = 4
PRO_DEFAULT_PERSPECTIVES_QUESTIONS = 2


@dataclass
class QuotaResult:
    allowed: bool
    message: str = ""
    remaining: int = -1  # -1 = unlimited


def get_perspectives_limits(project_path: Optional[str] = None) -> dict:
    """v6.0: Always returns Pro limits — all features free."""
    return {
        "max_managers": PRO_DEFAULT_PERSPECTIVES_MANAGERS,
        "max_questions": PRO_DEFAULT_PERSPECTIVES_QUESTIONS,
    }
