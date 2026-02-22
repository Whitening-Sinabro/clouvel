# -*- coding: utf-8 -*-
"""Licensing Experiments Module

A/B testing flags (v3.3: 전환율 실험 확장).
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from .core import is_developer
from .validation import get_machine_id, load_license_cache
from .trial import is_full_trial_active


# ============================================================
# A/B 테스트 플래그 (v3.3: 전환율 실험 확장)
# ============================================================

# Experiment configurations with multiple variants
# v3.3: Added rollout_percent for gradual traffic rollout (Week 3)
EXPERIMENTS = {
    "meeting_quota": {
        "variants": ["control", "variant_a"],
        "description": "Meeting quota for additional projects: weekly vs monthly 3",
        "values": {"control": "weekly", "variant_a": "monthly_3"},
        "rollout_percent": 50,
        "started_at": "2026-02-01",
    },
    "kb_retention": {
        "variants": ["control", "variant_a"],
        "description": "KB retention for additional projects: unlimited vs 7 days",
        "values": {"control": "unlimited", "variant_a": "7_days"},
        "rollout_percent": 50,
        "started_at": "2026-02-01",
    },
    "pain_point_message": {
        "variants": ["control", "variant_a"],
        "description": "Message style: simple vs detailed",
        "values": {"control": "simple", "variant_a": "detailed"},
        "rollout_percent": 100,  # Full rollout - low risk
        "started_at": "2026-02-01",
    },
}


def _get_ab_flags_path() -> Path:
    """Get A/B test flags file path: ~/.clouvel/ab_flags.json"""
    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:
        base = Path.home()
    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "ab_flags.json"


def get_ab_group(experiment_name: str) -> str:
    """Get A/B test group for an experiment (legacy).

    Returns "control" or "treatment". Assignment is random on first call
    and persisted for consistency.
    """
    return get_experiment_variant(experiment_name)


def is_in_rollout(experiment_name: str, user_id: str = None) -> bool:
    """Check if user is in the experiment's rollout percentage.

    v3.3: Gradual traffic rollout control.
    - 10% rollout: only 10% of users see the experiment
    - 50% rollout: 50% of users see the experiment
    - 100% rollout: all users see the experiment

    Users not in rollout get "control" behavior.
    """
    if user_id is None:
        user_id = get_machine_id()

    config = EXPERIMENTS.get(experiment_name, {})
    rollout_percent = config.get("rollout_percent", 100)

    # Hash user_id + experiment to get deterministic 0-99 value
    hash_input = f"{user_id}:rollout:{experiment_name}".encode()
    hash_value = int(hashlib.sha256(hash_input).hexdigest(), 16) % 100

    return hash_value < rollout_percent


def get_experiment_variant(experiment_name: str, user_id: str = None) -> str:
    """Get experiment variant with deterministic assignment.

    v3.3: Uses hash-based assignment for consistency across sessions.
    v4.0: Server-first sticky assignment (prevents local tampering).
    Supports multiple variants per experiment and rollout control.

    Args:
        experiment_name: Name of the experiment
        user_id: Optional user ID for deterministic assignment

    Returns:
        Variant name (e.g., "control", "variant_a", "variant_b")
    """
    # v4.0: Try server state first (sticky assignment)
    try:
        from .sync import SyncState
        ss = SyncState.get()
        if ss.is_synced():
            server_variant = ss.get_experiment(experiment_name)
            if server_variant:
                # Mirror to local
                _mirror_experiment_to_local(experiment_name, server_variant, user_id)
                return server_variant
        # Try server assignment for new experiments
        server_variant = ss.assign_experiment(experiment_name)
        if server_variant:
            _mirror_experiment_to_local(experiment_name, server_variant, user_id)
            return server_variant
    except (ImportError, OSError, ConnectionError, ValueError):
        pass

    # Fallback: local logic
    path = _get_ab_flags_path()
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, ValueError):
            data = {}

    # Check if already assigned
    experiments = data.get("experiments", {})
    if experiment_name in experiments:
        return experiments[experiment_name]["variant"]

    # Get experiment config
    config = EXPERIMENTS.get(experiment_name, {
        "variants": ["control", "treatment"],
        "description": "Unknown experiment",
    })
    variants = config.get("variants", ["control", "treatment"])

    # Deterministic assignment based on machine_id + experiment name
    if user_id is None:
        user_id = get_machine_id()

    # v5.1: Detect license tier for analytics filtering
    _license_tier = "free"
    try:
        if is_developer():
            _license_tier = "developer"
        elif is_full_trial_active():
            _license_tier = "trial"
        else:
            cached = load_license_cache()
            if cached and cached.get("tier"):
                _license_tier = "pro"
    except (OSError, json.JSONDecodeError, ValueError):
        pass

    # v3.3: Check rollout percentage first
    if not is_in_rollout(experiment_name, user_id):
        variant = "control"  # Users not in rollout get control
    else:
        hash_input = f"{user_id}:{experiment_name}".encode()
        hash_value = int(hashlib.sha256(hash_input).hexdigest(), 16)
        variant = variants[hash_value % len(variants)]

    # Save assignment
    if "experiments" not in data:
        data["experiments"] = {}
    data["experiments"][experiment_name] = {
        "variant": variant,
        "assigned_at": datetime.now().isoformat(),
        "user_id_hash": user_id[:8],
        "license_tier": _license_tier,
    }

    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass

    # Queue for next sync
    try:
        from .sync import mark_pending_sync
        mark_pending_sync("experiment_assign", {"experiment": experiment_name, "variant": variant})
    except (ImportError, OSError):
        pass

    # Log assignment
    try:
        from ..analytics import log_event
        log_event("experiment_assigned", {
            "experiment": experiment_name,
            "variant": variant,
            "user_id_hash": user_id[:8],
            "license_tier": _license_tier,
        })
    except (ImportError, OSError):
        pass

    return variant


def _mirror_experiment_to_local(experiment_name: str, variant: str, user_id: str = None) -> None:
    """Mirror server experiment assignment to local ab_flags.json."""
    if user_id is None:
        user_id = get_machine_id()
    path = _get_ab_flags_path()
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, ValueError):
            data = {}
    if "experiments" not in data:
        data["experiments"] = {}
    data["experiments"][experiment_name] = {
        "variant": variant,
        "assigned_at": datetime.now().isoformat(),
        "user_id_hash": user_id[:8] if user_id else "",
        "source": "server",
    }
    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def get_experiment_value(experiment_name: str) -> Any:
    """Get the actual value for the current variant.

    Example:
        value = get_experiment_value("project_limit")  # Returns 1, 2, or 3
    """
    variant = get_experiment_variant(experiment_name)
    config = EXPERIMENTS.get(experiment_name, {})
    values = config.get("values", {})
    return values.get(variant, values.get("control"))


def get_all_experiment_assignments() -> Dict[str, Any]:
    """Get all experiment assignments for the current user."""
    path = _get_ab_flags_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("experiments", {})
    except (OSError, json.JSONDecodeError, ValueError):
        return {}


def track_conversion_event(experiment_name: str, event_type: str, metadata: Dict = None) -> None:
    """Track a conversion event for A/B testing.

    Args:
        experiment_name: The experiment this event is for
        event_type: Type of event (e.g., "upgrade_prompt_shown", "pro_conversion")
        metadata: Additional data about the event
    """
    variant = get_experiment_variant(experiment_name)

    event_data = {
        "experiment": experiment_name,
        "variant": variant,
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {},
    }

    # Log to analytics
    try:
        from ..analytics import log_event
        log_event(f"ab_{event_type}", event_data)
    except (ImportError, OSError):
        pass

    # Also save to local file for offline analysis
    path = _get_ab_flags_path()
    try:
        data = {}
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))

        if "events" not in data:
            data["events"] = []

        # Keep last 100 events
        data["events"].append(event_data)
        data["events"] = data["events"][-100:]

        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass
