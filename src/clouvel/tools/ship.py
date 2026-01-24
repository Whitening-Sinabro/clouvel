# -*- coding: utf-8 -*-
"""
Clouvel Ship Tool - Pro Only

One-click test → verify → evidence generation tool.

This feature is only available in the Pro version.
Purchase: https://polar.sh/clouvel
"""

from typing import Dict, Any, List


def ship(
    path: str,
    feature: str = "",
    steps: List[str] = None,
    generate_evidence: bool = True,
    auto_fix: bool = False
) -> Dict[str, Any]:
    """
    Pro-only feature.

    One-click test, verification, and evidence generation.
    - lint: Code style check
    - typecheck: Type check
    - test: Run tests
    - build: Build verification

    Purchase: https://polar.sh/clouvel
    """
    return {
        "error": "Pro-only feature",
        "message": "The ship tool is only available in the Pro version.",
        "upgrade_url": "https://polar.sh/clouvel",
        "features": [
            "Automated lint/typecheck/test/build execution",
            "Auto-detect project type",
            "Generate verification evidence files",
            "auto_fix mode",
        ],
        "formatted_output": """
==================================================
🔒 PRO-ONLY FEATURE
==================================================

The **ship** tool is only available in the Pro version.

### Included Features
- 🧪 Automated lint → typecheck → test → build
- 🔍 Auto-detect project type (Python/Node/Bun)
- 📋 Generate verification evidence files
- 🔧 lint error auto_fix mode

### Purchase
https://polar.sh/clouvel

==================================================
"""
    }


def quick_ship(path: str, feature: str = "") -> Dict[str, Any]:
    """Pro-only feature. Quick lint and test execution only."""
    return ship(path=path, feature=feature)


def full_ship(path: str, feature: str = "") -> Dict[str, Any]:
    """Pro-only feature. All verification steps + auto_fix."""
    return ship(path=path, feature=feature)
