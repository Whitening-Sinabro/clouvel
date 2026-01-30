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

# v3.0: Version for API compatibility check
def _get_client_version() -> str:
    """Get current clouvel version."""
    try:
        from importlib.metadata import version
        return version("clouvel")
    except Exception:
        return "3.0.0"

CLIENT_VERSION = _get_client_version()
MIN_REQUIRED_VERSION = "3.0.0"


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
                "X-Clouvel-Version": CLIENT_VERSION,  # v3.0: Version header
            },
            timeout=API_TIMEOUT,
        )

        if response.status_code == 426:
            # v3.0: Upgrade required
            data = response.json() if response.text else {}
            return {
                "error": "upgrade_required",
                "message": data.get("message", "Clouvel v3.0+ required"),
                "formatted_output": f"""
==================================================
⛔ UPGRADE REQUIRED
==================================================

Clouvel v3.0+ is required. Your version: {CLIENT_VERSION}

Run: pip install --upgrade clouvel

Changes in v3.0:
- FREE: PM only (was 3 managers)
- FREE: WARN mode (was BLOCK)
- PRO: Full 8 managers + BLOCK mode

==================================================
"""
            }

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
                "X-Clouvel-Version": CLIENT_VERSION,  # v3.0: Version header
            },
            timeout=API_TIMEOUT,
        )

        if response.status_code == 426:
            # v3.0: Upgrade required
            return {
                "allowed": False,
                "error": "upgrade_required",
                "message": f"Clouvel v3.0+ required. Current: {CLIENT_VERSION}. Run: pip install --upgrade clouvel",
            }

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
                "X-Clouvel-Version": CLIENT_VERSION,  # v3.0: Version header
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


def _generate_dynamic_meeting_direct(context: str, topic: Optional[str], api_key: str) -> str:
    """
    Generate dynamic meeting directly using anthropic package.
    Used when tools/manager module is not available (PyPI version).
    """
    import anthropic

    topic_hint = topic or "feature"
    system_prompt = f"""당신은 소프트웨어 프로젝트 회의를 진행하는 퍼실리테이터입니다.
7명의 C-Level 임원이 참석한 회의를 자연스러운 대화체로 작성해주세요.

참석자:
- 👔 PM (Product Manager): 스펙, MVP, 우선순위
- 🛠️ CTO: 아키텍처, 기술 부채, 패턴
- 🧪 QA: 테스트, 엣지케이스, 검증
- 🎨 CDO (Design): UX, 일관성, 접근성
- 💰 CFO: 비용, ROI, 리소스
- 🔒 CSO (Security): 보안, 취약점, 컴플라이언스
- 📣 CMO: 사용자 커뮤니케이션, 포지셔닝

회의 주제: {topic_hint}

형식:
1. 각 임원이 1-2개의 핵심 질문이나 우려사항을 제기
2. 자연스러운 대화체 (예: "잠깐, 그거 보안 이슈 아니야?" "좋은 지적이에요, 근데...")
3. 마지막에 액션 아이템 정리

한국어로 작성해주세요."""

    user_prompt = f"""다음 내용에 대해 C-Level 회의를 진행해주세요:

{context}

자연스러운 회의 대화체로 작성해주세요. 각 임원의 관점에서 핵심 질문과 우려사항을 다뤄주세요."""

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    return response.content[0].text


def _dev_mode_response(
    context: str,
    topic: Optional[str] = None,
    mode: str = "auto",
    managers: list = None,
    use_dynamic: bool = False,
    include_checklist: bool = True,
) -> Dict[str, Any]:
    """Developer mode response - use local manager module with full features."""
    # 1. Try local manager module (development environment)
    try:
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

    # 2. Local module not available (PyPI version) - try direct anthropic call
    if use_dynamic:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            try:
                meeting_output = _generate_dynamic_meeting_direct(context, topic, api_key)
                return {
                    "dev_mode": True,
                    "formatted_output": f"## 🏢 C-Level 동적 회의\n\n{meeting_output}",
                    "active_managers": ["PM", "CTO", "QA", "CDO", "CFO", "CSO", "CMO"],
                }
            except ImportError:
                # anthropic package not installed
                pass
            except Exception as e:
                # API error - fall through to mock
                pass

    # 3. Fallback: return mock full response for dev testing
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
    """Fallback response when API is unavailable.

    v3.0: FREE tier = PM only (1 manager)
    """
    return {
        "topic": "feature",
        "active_managers": ["PM"],
        "feedback": {
            "PM": {
                "emoji": "👔",
                "title": "Product Manager",
                "questions": [
                    "Is this in the PRD?",
                    "What is the MVP scope?",
                    "What is the acceptance criteria?",
                ],
            },
        },
        "formatted_output": f"""
## 💡 C-Level Perspectives (FREE Tier)

> ⚠️ {error_message}

**👔 PM**: Is this in the PRD? What is the MVP scope?

---

**💎 Pro: 7 more managers** (CTO, QA, CDO, CMO, CFO, CSO, ERROR)
→ https://polar.sh/clouvel (code: FIRST01)
""",
        "offline": True,
        "missed_perspectives": {
            "CTO": {"emoji": "🛠️", "hint": "Technical architecture & code quality"},
            "QA": {"emoji": "🧪", "hint": "Test strategy & edge cases"},
            "CDO": {"emoji": "🎨", "hint": "Design & UX review"},
            "CMO": {"emoji": "📢", "hint": "Marketing & messaging"},
            "CFO": {"emoji": "💰", "hint": "Cost & ROI analysis"},
            "CSO": {"emoji": "🔒", "hint": "Security review"},
            "ERROR": {"emoji": "🔥", "hint": "Risk & failure modes"},
        },
    }
