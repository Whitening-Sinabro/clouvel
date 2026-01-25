# -*- coding: utf-8 -*-
"""
Clouvel Trial System
Pro 기능 체험판 - 횟수 제한 방식

Trial 한도:
- manager: 10회
- ship: 5회
- quick_perspectives: 무제한 (맛보기)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Trial 한도 설정
TRIAL_LIMITS = {
    "manager": 10,
    "ship": 5,
    # quick_perspectives는 무제한 (리스트에 없음)
}

# Trial 데이터 저장 경로
def _get_trial_path() -> Path:
    """Get trial data file path: ~/.clouvel/trial.json"""
    if os.name == 'nt':  # Windows
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:  # Unix
        base = Path.home()

    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "trial.json"


def _load_trial_data() -> Dict[str, Any]:
    """Load trial data from file"""
    trial_path = _get_trial_path()

    if trial_path.exists():
        try:
            with open(trial_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Initialize new trial data
    return {
        "created_at": datetime.now().isoformat(),
        "usage": {},
    }


def _save_trial_data(data: Dict[str, Any]) -> None:
    """Save trial data to file"""
    trial_path = _get_trial_path()

    try:
        with open(trial_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError:
        pass  # Silently fail


def get_trial_usage(feature: str) -> int:
    """Get current usage count for a feature"""
    data = _load_trial_data()
    return data.get("usage", {}).get(feature, 0)


def get_trial_remaining(feature: str) -> Optional[int]:
    """Get remaining trial uses for a feature.

    Returns:
        int: Remaining uses
        None: If feature has no limit (unlimited)
    """
    if feature not in TRIAL_LIMITS:
        return None  # Unlimited

    limit = TRIAL_LIMITS[feature]
    used = get_trial_usage(feature)
    return max(0, limit - used)


def increment_trial_usage(feature: str) -> Dict[str, Any]:
    """Increment usage count and return status.

    Returns:
        {
            "used": int,
            "limit": int,
            "remaining": int,
            "exhausted": bool,
        }
    """
    if feature not in TRIAL_LIMITS:
        return {"unlimited": True}

    data = _load_trial_data()

    if "usage" not in data:
        data["usage"] = {}

    current = data["usage"].get(feature, 0)
    data["usage"][feature] = current + 1
    _save_trial_data(data)

    limit = TRIAL_LIMITS[feature]
    remaining = max(0, limit - (current + 1))

    return {
        "used": current + 1,
        "limit": limit,
        "remaining": remaining,
        "exhausted": remaining <= 0,
    }


def check_trial_available(feature: str) -> bool:
    """Check if trial is still available for a feature"""
    if feature not in TRIAL_LIMITS:
        return True  # Unlimited features always available

    remaining = get_trial_remaining(feature)
    return remaining is not None and remaining > 0


def get_trial_status() -> Dict[str, Any]:
    """Get overall trial status"""
    data = _load_trial_data()

    status = {
        "created_at": data.get("created_at"),
        "features": {},
    }

    for feature, limit in TRIAL_LIMITS.items():
        used = data.get("usage", {}).get(feature, 0)
        remaining = max(0, limit - used)
        status["features"][feature] = {
            "used": used,
            "limit": limit,
            "remaining": remaining,
            "exhausted": remaining <= 0,
        }

    return status


def reset_trial() -> None:
    """Reset trial data (for testing)"""
    trial_path = _get_trial_path()
    if trial_path.exists():
        trial_path.unlink()


def get_trial_exhausted_message(feature: str) -> str:
    """Get message when trial is exhausted"""
    limit = TRIAL_LIMITS.get(feature, 0)

    return f"""
==================================================
⏰ TRIAL EXHAUSTED
==================================================

You've used all {limit} free trial uses of **{feature}**.

Thank you for trying Clouvel Pro features!

### Upgrade to Pro
Unlimited access to all Pro features:
- 👔 8 C-Level manager feedback (manager)
- 🚀 One-click ship verification (ship)
- 📊 Error learning system
- And more...

### Purchase
https://polar.sh/clouvel

==================================================
"""
