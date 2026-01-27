# -*- coding: utf-8 -*-
"""
Clouvel Ship Tool - Pro / Trial (API-based)

One-click test → verify → evidence generation tool.

Trial/License validation via API, execution is local.

v3.1: Runtime entitlement checks (no import-time constants).
v3.2: project_path based detection for MCP compatibility.
"""

from pathlib import Path
from typing import Dict, Any, List

from ..api_client import call_ship_api
from ..utils.entitlements import is_developer


def _trial_exhausted_response() -> Dict[str, Any]:
    """Response when trial is exhausted"""
    return {
        "error": "Trial exhausted",
        "message": "You've used all 5 free trial uses of ship.",
        "upgrade_url": "https://polar.sh/clouvel",
        "formatted_output": """
==================================================
⏰ TRIAL EXHAUSTED
==================================================

You've used all 5 free trial uses of **ship**.

Upgrade to Pro for unlimited access:
https://polar.sh/clouvel

==================================================
"""
    }


def ship(
    path: str,
    feature: str = "",
    steps: List[str] = None,
    generate_evidence: bool = True,
    auto_fix: bool = False
) -> Dict[str, Any]:
    """
    One-click test, verification, and evidence generation.

    - lint: Code style check
    - typecheck: Type check
    - test: Run tests
    - build: Build verification

    Pro feature with 5 free trial uses.
    """
    # Dev mode bypass (runtime check with project_path, not import-time)
    if is_developer(path):
        try:
            from .ship_pro import ship as ship_impl
            return ship_impl(
                path=path,
                feature=feature,
                steps=steps,
                generate_evidence=generate_evidence,
                auto_fix=auto_fix
            )
        except ImportError:
            pass

    # Check permission via API
    api_result = call_ship_api(path=path, feature=feature)

    if not api_result.get("allowed", False):
        if api_result.get("error") == "trial_exhausted":
            return _trial_exhausted_response()
        return {
            "error": api_result.get("error", "Not allowed"),
            "message": api_result.get("message", "Ship not available"),
            "formatted_output": f"Error: {api_result.get('message', 'Ship not available')}"
        }

    # Run ship locally
    try:
        from .ship_pro import ship as ship_impl
        result = ship_impl(
            path=path,
            feature=feature,
            steps=steps,
            generate_evidence=generate_evidence,
            auto_fix=auto_fix
        )

        # Add trial banner if applicable
        if "trial" in api_result.get("message", "").lower():
            trial_banner = "\n> 🎁 **Trial Mode** - Upgrade for unlimited: https://polar.sh/clouvel\n\n"
            if result.get("formatted_output"):
                result["formatted_output"] = trial_banner + result["formatted_output"]

        return result

    except ImportError:
        return {
            "error": "Implementation not found",
            "message": "ship_pro.py module not found. This is expected in Free version.",
            "formatted_output": """
==================================================
🔒 PRO FEATURE
==================================================

The **ship** tool requires the Pro implementation.

This error occurs because:
1. You're using the Free version, or
2. ship_pro.py is not installed

Upgrade to Pro: https://polar.sh/clouvel

==================================================
"""
        }


def quick_ship(path: str, feature: str = "") -> Dict[str, Any]:
    """Quick lint and test execution only."""
    return ship(path=path, feature=feature, steps=["lint", "test"])


def full_ship(path: str, feature: str = "") -> Dict[str, Any]:
    """All verification steps + auto_fix."""
    return ship(path=path, feature=feature, steps=["lint", "typecheck", "test", "build"], auto_fix=True)
