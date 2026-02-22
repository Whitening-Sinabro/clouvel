# Clouvel Start Tool (Free)
# Project onboarding + PRD enforcement + interactive guide
#
# Subpackage structure:
#   detect.py  - Project type detection patterns and functions
#   prd.py     - PRD saving, validation, backup, diff, impact analysis
#   core.py    - start(), quick_start() main entry points

from .core import start, quick_start
from .prd import save_prd, _validate_prd, _calculate_prd_diff, _analyze_prd_impact, _backup_prd
from .detect import (
    _detect_project_type,
    get_prd_questions,
    PRD_QUESTIONS,
    PROJECT_TYPE_PATTERNS,
)

__all__ = [
    "start", "quick_start", "save_prd",
    # Internal (for tests)
    "_detect_project_type", "_validate_prd", "_calculate_prd_diff",
    "_analyze_prd_impact", "_backup_prd",
    "get_prd_questions", "PRD_QUESTIONS", "PROJECT_TYPE_PATTERNS",
]
