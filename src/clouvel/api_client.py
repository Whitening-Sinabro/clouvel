# -*- coding: utf-8 -*-
"""
Clouvel API Client

Pro features (manager, ship) are served via Cloudflare Workers API.
This client handles API communication and fallback.
"""

import os
import hashlib
import platform
import requests
from typing import Dict, Any, Optional

# API Configuration
API_BASE_URL = os.environ.get("CLOUVEL_API_URL", "https://clouvel-api.vnddns999.workers.dev")
API_TIMEOUT = 30  # seconds


def _get_client_id() -> str:
    """Generate a unique client ID for trial tracking."""
    # Combine machine info for unique ID
    machine_info = f"{platform.node()}-{platform.machine()}-{os.getlogin() if hasattr(os, 'getlogin') else 'user'}"
    return hashlib.sha256(machine_info.encode()).hexdigest()[:32]


def _get_license_key() -> Optional[str]:
    """Get license key from environment or file."""
    # 1. Environment variable
    license_key = os.environ.get("CLOUVEL_LICENSE_KEY")
    if license_key:
        return license_key

    # 2. License file
    try:
        from pathlib import Path
        license_file = Path.home() / ".clouvel" / "license.json"
        if license_file.exists():
            import json
            data = json.loads(license_file.read_text())
            return data.get("key")
    except Exception:
        pass

    return None


def call_manager_api(
    context: str,
    topic: Optional[str] = None,
    mode: str = "auto",
    managers: list = None,
    use_dynamic: bool = False,
    include_checklist: bool = True,
) -> Dict[str, Any]:
    """
    Call manager API.

    Args:
        context: Content to review
        topic: Topic hint (auth, api, payment, etc.)
        mode: 'auto', 'all', or 'specific'
        managers: List of managers when mode='specific'
        use_dynamic: If True, generates dynamic meeting via Claude API
        include_checklist: Whether to include checklist

    Returns:
        Manager feedback and recommendations
    """
    # Developer mode: bypass API, use local fallback with full features
    try:
        from .license_common import is_developer
        if is_developer():
            return _dev_mode_response(
                context=context,
                topic=topic,
                mode=mode,
                managers=managers,
                use_dynamic=use_dynamic,
                include_checklist=include_checklist,
            )
    except ImportError:
        pass

    try:
        payload = {
            "context": context,
            "mode": mode,
        }

        if topic:
            payload["topic"] = topic
        if managers:
            payload["managers"] = managers

        # Add license key if available
        license_key = _get_license_key()
        if license_key:
            payload["licenseKey"] = license_key

        response = requests.post(
            f"{API_BASE_URL}/api/manager",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-Clouvel-Client": _get_client_id(),
            },
            timeout=API_TIMEOUT,
        )

        if response.status_code == 402:
            # Trial exhausted
            data = response.json()
            return {
                "error": "trial_exhausted",
                "message": data.get("message", "Trial exhausted"),
                "upgrade_url": data.get("upgrade_url", "https://polar.sh/clouvel"),
                "formatted_output": f"""
==================================================
⏰ TRIAL EXHAUSTED
==================================================

{data.get('message', 'You have used all your free trial uses.')}

Upgrade to Pro for unlimited access:
{data.get('upgrade_url', 'https://polar.sh/clouvel')}

==================================================
"""
            }

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        return _fallback_response("API timeout. Using offline mode.")

    except requests.exceptions.ConnectionError:
        return _fallback_response("Cannot connect to API. Using offline mode.")

    except Exception as e:
        return _fallback_response(f"API error: {str(e)}")


def call_ship_api(
    path: str,
    feature: str = "",
) -> Dict[str, Any]:
    """
    Check ship permission via API.

    Ship runs locally but requires API validation for trial/license.
    """
    # Developer mode: always allow
    try:
        from .license_common import is_developer
        if is_developer():
            return {
                "allowed": True,
                "dev_mode": True,
                "message": "Developer mode - unlimited ship access",
            }
    except ImportError:
        pass

    try:
        payload = {
            "path": path,
            "feature": feature,
        }

        license_key = _get_license_key()
        if license_key:
            payload["licenseKey"] = license_key

        response = requests.post(
            f"{API_BASE_URL}/api/ship",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-Clouvel-Client": _get_client_id(),
            },
            timeout=API_TIMEOUT,
        )

        if response.status_code == 402:
            data = response.json()
            return {
                "allowed": False,
                "error": "trial_exhausted",
                "message": data.get("message"),
                "upgrade_url": data.get("upgrade_url"),
            }

        response.raise_for_status()
        return response.json()

    except Exception as e:
        # Allow ship to run if API is unavailable (graceful degradation)
        return {
            "allowed": True,
            "message": f"API unavailable, running locally. ({str(e)})",
        }


def get_trial_status() -> Dict[str, Any]:
    """Get current trial status from API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/trial/status",
            headers={
                "X-Clouvel-Client": _get_client_id(),
            },
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        return {
            "error": str(e),
            "features": {},
        }


def _dev_mode_response(
    context: str,
    topic: Optional[str] = None,
    mode: str = "auto",
    managers: list = None,
    use_dynamic: bool = False,
    include_checklist: bool = True,
) -> Dict[str, Any]:
    """Developer mode response - use local manager module with full features."""
    try:
        # Dynamic meeting: use generate_meeting_sync (calls Claude API if available)
        if use_dynamic:
            from .tools.manager import generate_meeting_sync
            meeting_output = generate_meeting_sync(
                context=context,
                topic=topic,
            )
            return {
                "dev_mode": True,
                "formatted_output": meeting_output,
                "active_managers": ["PM", "CTO", "QA", "CDO", "CFO", "CSO", "CMO"],
            }

        # Regular mode: use local manager module
        from .tools.manager import manager
        result = manager(
            context=context,
            mode=mode,
            managers=managers,
            topic=topic,
            use_dynamic=False,
            include_checklist=include_checklist,
        )
        result["dev_mode"] = True
        return result
    except ImportError:
        pass

    # Fallback: return mock full response for dev testing
    return {
        "topic": topic or "feature",
        "dev_mode": True,
        "active_managers": ["PM", "CTO", "QA", "CDO", "CFO", "CSO", "CMO"],
        "feedback": {
            "PM": {"emoji": "👔", "title": "Product Manager", "questions": ["Is this in the PRD?", "What is the MVP scope?"]},
            "CTO": {"emoji": "🛠️", "title": "CTO", "questions": ["Does this follow existing patterns?", "What is the maintenance burden?"]},
            "QA": {"emoji": "🧪", "title": "QA Lead", "questions": ["What are the edge cases?", "How will you test this?"]},
            "CDO": {"emoji": "🎨", "title": "Design Officer", "questions": ["Is the UX intuitive?", "Does it match the design system?"]},
            "CFO": {"emoji": "💰", "title": "CFO", "questions": ["What is the cost impact?", "ROI calculation?"]},
            "CSO": {"emoji": "🔒", "title": "Security Officer", "questions": ["Any security concerns?", "Data protection compliance?"]},
            "CMO": {"emoji": "📣", "title": "Marketing Officer", "questions": ["How will users discover this?", "Messaging strategy?"]},
        },
        "formatted_output": f"""
## 💡 C-Level Perspectives (Developer Mode)

> 🛠️ **DEV MODE**: Using local manager, no API call.

**Context**: {context[:100]}...

**👔 PM**: Is this in the PRD? What is the MVP scope?

**🛠️ CTO**: Does this follow existing patterns?

**🧪 QA**: What are the edge cases? How will you test this?

**🎨 CDO**: Is the UX intuitive?

**🔒 CSO**: Any security concerns?

---

> Developer mode - unlimited access
""",
    }


def _fallback_response(error_message: str) -> Dict[str, Any]:
    """Fallback response when API is unavailable."""
    return {
        "topic": "feature",
        "active_managers": ["PM", "CTO", "QA"],
        "feedback": {
            "PM": {
                "emoji": "👔",
                "title": "Product Manager",
                "questions": [
                    "Is this in the PRD?",
                    "What is the MVP scope?",
                ],
            },
            "CTO": {
                "emoji": "🛠️",
                "title": "CTO",
                "questions": [
                    "Does this follow existing patterns?",
                    "What is the maintenance burden?",
                ],
            },
            "QA": {
                "emoji": "🧪",
                "title": "QA Lead",
                "questions": [
                    "What are the edge cases?",
                    "How will you test this?",
                ],
            },
        },
        "formatted_output": f"""
## 💡 C-Level Perspectives (Offline Mode)

> ⚠️ {error_message}

**👔 PM**: Is this in the PRD? What is the MVP scope?

**🛠️ CTO**: Does this follow existing patterns?

**🧪 QA**: What are the edge cases? How will you test this?

---

> 💡 For full feedback, ensure API connectivity.
""",
        "offline": True,
    }
