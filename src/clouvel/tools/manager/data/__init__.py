# Manager Data
# 8 C-Level manager data

from .pm import PM_DATA
from .cto import CTO_DATA
from .qa import QA_DATA
from .cdo import CDO_DATA
from .cmo import CMO_DATA
from .cfo import CFO_DATA
from .cso import CSO_DATA
from .error import ERROR_DATA

MANAGERS = {
    "PM": PM_DATA,
    "CTO": CTO_DATA,
    "QA": QA_DATA,
    "CDO": CDO_DATA,
    "CMO": CMO_DATA,
    "CFO": CFO_DATA,
    "CSO": CSO_DATA,
    "ERROR": ERROR_DATA,
}

# v3.0: Free tier = 1 manager (PM only)
FREE_MANAGERS = ["PM"]

# v3.0: Pro-only = 7 managers (was 5, now includes CTO, QA)
PRO_ONLY_MANAGERS = ["CTO", "QA", "CDO", "CMO", "CFO", "CSO", "ERROR"]

# Pro-only manager descriptions (for "missed perspectives" hint)
PRO_ONLY_DESCRIPTIONS = {
    "CTO": {"emoji": "🛠️", "hint": "Technical architecture & code quality"},
    "QA": {"emoji": "🧪", "hint": "Test strategy & edge cases"},
    "CDO": {"emoji": "🎨", "hint": "Design & UX review"},
    "CMO": {"emoji": "📢", "hint": "Marketing & messaging"},
    "CFO": {"emoji": "💰", "hint": "Cost & ROI analysis"},
    "CSO": {"emoji": "🔒", "hint": "Security review"},
    "ERROR": {"emoji": "🔥", "hint": "Risk & failure modes"},
}

# Context-based manager grouping
CONTEXT_GROUPS = {
    'auth': ['CSO', 'CTO', 'QA', 'ERROR'],
    'payment': ['CFO', 'CSO', 'CTO', 'QA', 'ERROR'],
    'api': ['CTO', 'QA', 'CSO', 'ERROR'],
    'ui': ['CDO', 'PM', 'QA'],
    'feature': ['PM', 'CTO', 'QA'],
    'security': ['CSO', 'CTO', 'QA', 'ERROR'],
    'performance': ['CTO', 'QA', 'CFO'],
    'launch': ['CMO', 'PM', 'CFO', 'QA'],
    'error': ['ERROR', 'CTO', 'QA'],
    'design': ['CDO', 'PM', 'CMO'],
    'database': ['CTO', 'CSO', 'QA', 'ERROR'],
    # v1.5: MCP/Clouvel internal topics
    'mcp': ['CTO', 'PM', 'QA', 'ERROR'],
    'internal': ['PM', 'CTO', 'QA'],
    'tracking': ['PM', 'QA', 'ERROR'],
    'maintenance': ['CTO', 'QA', 'ERROR'],
}

# Phase priority (for sorting)
PHASE_ORDER = {'Prepare': 1, 'Design': 2, 'Implement': 3, 'Verify': 4}

__all__ = [
    "MANAGERS",
    "CONTEXT_GROUPS",
    "PHASE_ORDER",
    "FREE_MANAGERS",
    "PRO_ONLY_MANAGERS",
    "PRO_ONLY_DESCRIPTIONS",
]
