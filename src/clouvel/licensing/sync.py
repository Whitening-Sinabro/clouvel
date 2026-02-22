# -*- coding: utf-8 -*-
"""Licensing Sync Module

Server-side state synchronization client.
Talks to clouvel-api Worker KV for tamper-proof state management.

v4.0: Trial, First Project, Meeting Quota, A/B Experiments.
"""

import os
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional

from .validation import get_machine_id

# ============================================================
# Constants
# ============================================================

SYNC_API_BASE = os.environ.get(
    "CLOUVEL_SYNC_API",
    "https://clouvel-api.vnddns999.workers.dev",
)
SYNC_INTERVAL_SECONDS = 3600  # 1 hour
SYNC_TIMEOUT_SECONDS = 10
CLIENT_VERSION = "5.1.0"


def _get_clouvel_dir() -> Path:
    """Get ~/.clouvel/ directory."""
    if os.name == "nt":
        base = Path(os.environ.get("USERPROFILE", "~"))
    else:
        base = Path.home()
    d = base / ".clouvel"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _get_sync_cache_path() -> Path:
    """Get sync cache file: ~/.clouvel/sync_cache.json"""
    return _get_clouvel_dir() / "sync_cache.json"


def _load_sync_cache() -> Dict[str, Any]:
    """Load cached server state from disk."""
    p = _get_sync_cache_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return {}


def _save_sync_cache(data: Dict[str, Any]) -> None:
    """Save server state to disk cache."""
    p = _get_sync_cache_path()
    try:
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def _http_post(url: str, payload: dict) -> Optional[dict]:
    """POST JSON to URL using urllib (no external deps)."""
    import urllib.request
    import urllib.error

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Clouvel-Version": CLIENT_VERSION,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=SYNC_TIMEOUT_SECONDS) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
            # Non-200 but still JSON
            try:
                return json.loads(resp.read().decode("utf-8"))
            except (json.JSONDecodeError, ValueError):
                return None
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return None


def _http_post_with_status(url: str, payload: dict) -> tuple:
    """POST JSON and return (status_code, body_dict_or_None)."""
    import urllib.request
    import urllib.error

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Clouvel-Version": CLIENT_VERSION,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=SYNC_TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return (resp.status, data)
    except urllib.error.HTTPError as e:
        try:
            data = json.loads(e.read().decode("utf-8"))
            return (e.code, data)
        except (json.JSONDecodeError, ValueError):
            return (e.code, None)
    except (urllib.error.URLError, OSError, ValueError):
        return (0, None)


# ============================================================
# Local state readers (build payload for /api/v2/sync)
# ============================================================

def _read_local_trial() -> Optional[dict]:
    """Read local full_trial.json."""
    p = _get_clouvel_dir() / "full_trial.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def _read_local_first_project() -> Optional[dict]:
    """Read local first_project.json."""
    p = _get_clouvel_dir() / "first_project.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def _read_local_meeting_quota() -> Optional[dict]:
    """Read local monthly_meeting.json."""
    p = _get_clouvel_dir() / "monthly_meeting.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def _read_local_experiments() -> Optional[dict]:
    """Read local ab_flags.json experiments."""
    p = _get_clouvel_dir() / "ab_flags.json"
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data.get("experiments", {})
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def _build_local_state() -> dict:
    """Build local_state payload for /api/v2/sync."""
    state = {}
    trial = _read_local_trial()
    if trial:
        state["trial"] = trial
    fp = _read_local_first_project()
    if fp:
        state["first_project"] = fp
    mq = _read_local_meeting_quota()
    if mq:
        state["meeting_quota"] = mq
    exp = _read_local_experiments()
    if exp:
        state["experiments"] = exp
    return state


def _get_license_key() -> Optional[str]:
    """Try to get license key from cache."""
    try:
        from .validation import load_license_cache
        cached = load_license_cache()
        if cached and cached.get("key"):
            return cached["key"]
    except (ImportError, OSError):
        pass
    return None


# ============================================================
# Pending sync queue (for offline operations)
# ============================================================

def _get_pending_path() -> Path:
    return _get_clouvel_dir() / "sync_pending.json"


def _load_pending() -> list:
    p = _get_pending_path()
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return []


def _save_pending(items: list) -> None:
    p = _get_pending_path()
    try:
        p.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def mark_pending_sync(action: str, data: dict) -> None:
    """Queue an action for sync when server becomes available."""
    items = _load_pending()
    items.append({"action": action, "data": data, "ts": time.time()})
    # Keep last 50
    _save_pending(items[-50:])


# ============================================================
# SyncState Singleton
# ============================================================

class SyncState:
    """Server-side state synchronization singleton."""

    _instance: Optional["SyncState"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._synced_at: float = 0
        self._sync_lock = threading.Lock()
        # Load from disk cache on init
        cached = _load_sync_cache()
        if cached:
            self._state = cached.get("server_state", {})
            self._synced_at = cached.get("synced_at", 0)

    @classmethod
    def get(cls) -> "SyncState":
        """Get or create the singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton (for testing)."""
        cls._instance = None

    def needs_sync(self) -> bool:
        """Check if sync is needed (>1 hour since last sync)."""
        return time.time() - self._synced_at > SYNC_INTERVAL_SECONDS

    def sync(self, force: bool = False) -> Dict[str, Any]:
        """Synchronize state with server.

        Args:
            force: Force sync even if interval not elapsed.

        Returns:
            Server state dict, or cached state on failure.
        """
        if not force and not self.needs_sync():
            return self._state

        with self._sync_lock:
            # Double-check after acquiring lock
            if not force and not self.needs_sync():
                return self._state

            mid = get_machine_id()
            local_state = _build_local_state()
            license_key = _get_license_key()

            payload = {
                "machine_id": mid,
                "license_key": license_key,
                "client_version": CLIENT_VERSION,
                "local_state": local_state,
            }

            result = _http_post(f"{SYNC_API_BASE}/api/v2/sync", payload)
            if result and "server_state" in result:
                self._state = result["server_state"]
                self._synced_at = time.time()
                _save_sync_cache({
                    "server_state": self._state,
                    "synced_at": self._synced_at,
                })
                return self._state

            # Sync failed — return cached state
            return self._state

    def sync_async(self) -> None:
        """Run sync in background thread (fire-and-forget)."""
        t = threading.Thread(target=self._safe_sync, daemon=True)
        t.start()

    def _safe_sync(self) -> None:
        """Sync with error suppression."""
        try:
            self.sync()
        except Exception:
            pass

    # --------------------------------------------------------
    # State accessors
    # --------------------------------------------------------

    def get_trial_status(self) -> Dict[str, Any]:
        """Get trial status from server state."""
        return self._state.get("trial", {})

    def get_first_project(self) -> Dict[str, Any]:
        """Get first project info from server state."""
        return self._state.get("first_project", {})

    def get_meeting_quota(self) -> Dict[str, Any]:
        """Get meeting quota from server state."""
        return self._state.get("meeting_quota", {})

    def get_experiment(self, name: str) -> Optional[str]:
        """Get experiment variant from server state."""
        experiments = self._state.get("experiments", {})
        return experiments.get(name)

    def get_license(self) -> Dict[str, Any]:
        """Get license status from server state."""
        return self._state.get("license", {})

    def is_synced(self) -> bool:
        """Check if we have server state."""
        return self._synced_at > 0

    # --------------------------------------------------------
    # Direct server calls (for write operations)
    # --------------------------------------------------------

    def start_trial(self) -> Optional[Dict[str, Any]]:
        """Start trial via server. Returns result or None on failure."""
        mid = get_machine_id()
        status, result = _http_post_with_status(
            f"{SYNC_API_BASE}/api/v2/trial/start",
            {"machine_id": mid},
        )
        if status == 200 and result:
            return result
        if status == 409 and result:
            # Already started — return existing status
            return result
        return None

    def register_project(self, path_hash: str) -> Optional[Dict[str, Any]]:
        """Register first project via server."""
        mid = get_machine_id()
        result = _http_post(
            f"{SYNC_API_BASE}/api/v2/project/register",
            {"machine_id": mid, "path_hash": path_hash},
        )
        return result

    def consume_meeting(self, project_hash: str = None, license_key: str = None) -> Optional[Dict[str, Any]]:
        """Consume meeting quota via server."""
        mid = get_machine_id()
        payload = {"machine_id": mid}
        if project_hash:
            payload["project_hash"] = project_hash
        if license_key:
            payload["license_key"] = license_key
        result = _http_post(
            f"{SYNC_API_BASE}/api/v2/meeting/consume",
            payload,
        )
        return result

    def assign_experiment(self, experiment: str) -> Optional[str]:
        """Assign experiment variant via server. Returns variant name or None."""
        mid = get_machine_id()
        result = _http_post(
            f"{SYNC_API_BASE}/api/v2/experiment/assign",
            {"machine_id": mid, "experiment": experiment},
        )
        if result and "variant" in result:
            return result["variant"]
        return None
