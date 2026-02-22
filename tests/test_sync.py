# -*- coding: utf-8 -*-
"""Unit tests for clouvel.licensing.sync module.

Tests the SyncState singleton, server communication, offline fallback,
and local state mirroring.
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset SyncState singleton before each test."""
    from clouvel.licensing.sync import SyncState
    SyncState.reset()
    yield
    SyncState.reset()


@pytest.fixture
def tmp_clouvel_dir(tmp_path):
    """Create a temporary ~/.clouvel directory."""
    clouvel_dir = tmp_path / ".clouvel"
    clouvel_dir.mkdir()
    return clouvel_dir


@pytest.fixture
def patch_clouvel_dir(tmp_clouvel_dir):
    """Patch _get_clouvel_dir to use temp directory."""
    with patch("clouvel.licensing.sync._get_clouvel_dir", return_value=tmp_clouvel_dir):
        yield tmp_clouvel_dir


# ============================================================
# SyncState singleton tests
# ============================================================

class TestSyncStateSingleton:
    def test_get_returns_same_instance(self):
        from clouvel.licensing.sync import SyncState
        s1 = SyncState.get()
        s2 = SyncState.get()
        assert s1 is s2

    def test_reset_creates_new_instance(self):
        from clouvel.licensing.sync import SyncState
        s1 = SyncState.get()
        SyncState.reset()
        s2 = SyncState.get()
        assert s1 is not s2

    def test_needs_sync_initially_true(self):
        from clouvel.licensing.sync import SyncState
        ss = SyncState.get()
        assert ss.needs_sync() is True

    def test_needs_sync_false_after_sync(self, patch_clouvel_dir):
        from clouvel.licensing.sync import SyncState
        ss = SyncState.get()
        # Simulate a successful sync
        ss._synced_at = time.time()
        assert ss.needs_sync() is False

    def test_needs_sync_true_after_interval(self, patch_clouvel_dir):
        from clouvel.licensing.sync import SyncState, SYNC_INTERVAL_SECONDS
        ss = SyncState.get()
        ss._synced_at = time.time() - SYNC_INTERVAL_SECONDS - 1
        assert ss.needs_sync() is True


# ============================================================
# Local state builders
# ============================================================

class TestLocalStateBuilders:
    def test_build_empty_state(self, patch_clouvel_dir):
        from clouvel.licensing.sync import _build_local_state
        state = _build_local_state()
        assert isinstance(state, dict)

    def test_build_state_with_trial(self, patch_clouvel_dir):
        from clouvel.licensing.sync import _build_local_state
        trial_data = {"started_at": "2026-02-20T10:00:00", "machine_id": "test123abc"}
        (patch_clouvel_dir / "full_trial.json").write_text(
            json.dumps(trial_data), encoding="utf-8"
        )
        state = _build_local_state()
        assert "trial" in state
        assert state["trial"]["started_at"] == "2026-02-20T10:00:00"

    def test_build_state_with_first_project(self, patch_clouvel_dir):
        from clouvel.licensing.sync import _build_local_state
        fp_data = {"path_hash": "abc123", "machine_id": "test123abc"}
        (patch_clouvel_dir / "first_project.json").write_text(
            json.dumps(fp_data), encoding="utf-8"
        )
        state = _build_local_state()
        assert "first_project" in state
        assert state["first_project"]["path_hash"] == "abc123"

    def test_build_state_with_meeting_quota(self, patch_clouvel_dir):
        from clouvel.licensing.sync import _build_local_state
        mq_data = {"month": "2026-02", "used": 2}
        (patch_clouvel_dir / "monthly_meeting.json").write_text(
            json.dumps(mq_data), encoding="utf-8"
        )
        state = _build_local_state()
        assert "meeting_quota" in state
        assert state["meeting_quota"]["used"] == 2

    def test_build_state_with_experiments(self, patch_clouvel_dir):
        from clouvel.licensing.sync import _build_local_state
        ab_data = {"experiments": {"meeting_quota": {"variant": "variant_a"}}}
        (patch_clouvel_dir / "ab_flags.json").write_text(
            json.dumps(ab_data), encoding="utf-8"
        )
        state = _build_local_state()
        assert "experiments" in state
        assert state["experiments"]["meeting_quota"]["variant"] == "variant_a"

    def test_build_state_corrupt_file(self, patch_clouvel_dir):
        """Corrupt JSON files should not crash state building."""
        (patch_clouvel_dir / "full_trial.json").write_text("NOT JSON", encoding="utf-8")
        from clouvel.licensing.sync import _build_local_state
        state = _build_local_state()
        assert "trial" not in state


# ============================================================
# Sync cache persistence
# ============================================================

class TestSyncCache:
    def test_save_and_load_cache(self, patch_clouvel_dir):
        from clouvel.licensing.sync import _save_sync_cache, _load_sync_cache
        data = {"server_state": {"trial": {"active": True}}, "synced_at": 1234567890}
        _save_sync_cache(data)
        loaded = _load_sync_cache()
        assert loaded["synced_at"] == 1234567890
        assert loaded["server_state"]["trial"]["active"] is True

    def test_load_missing_cache(self, patch_clouvel_dir):
        from clouvel.licensing.sync import _load_sync_cache
        loaded = _load_sync_cache()
        assert loaded == {}

    def test_init_loads_from_cache(self, patch_clouvel_dir):
        from clouvel.licensing.sync import _save_sync_cache, SyncState
        _save_sync_cache({
            "server_state": {"trial": {"active": True, "remaining_days": 5}},
            "synced_at": time.time(),
        })
        SyncState.reset()
        ss = SyncState.get()
        assert ss.is_synced()
        trial = ss.get_trial_status()
        assert trial["active"] is True


# ============================================================
# Server sync (mocked)
# ============================================================

class TestSync:
    def test_sync_success(self, patch_clouvel_dir):
        from clouvel.licensing.sync import SyncState
        server_response = {
            "server_state": {
                "trial": {"active": True, "remaining_days": 5, "source": "server"},
                "first_project": {"path_hash": "abc123", "locked": True},
                "meeting_quota": {"month": "2026-02", "used": 1, "limit": 3, "remaining": 2},
                "experiments": {"meeting_quota": "variant_a"},
                "license": {"valid": False, "tier": None},
            },
            "next_sync_seconds": 3600,
        }
        with patch("clouvel.licensing.sync._http_post", return_value=server_response), \
             patch("clouvel.licensing.sync.get_machine_id", return_value="testmachineid123"), \
             patch("clouvel.licensing.sync._get_license_key", return_value=None):
            ss = SyncState.get()
            result = ss.sync(force=True)
            assert result["trial"]["active"] is True
            assert result["first_project"]["locked"] is True
            assert result["meeting_quota"]["remaining"] == 2
            assert result["experiments"]["meeting_quota"] == "variant_a"

    def test_sync_failure_returns_cached(self, patch_clouvel_dir):
        from clouvel.licensing.sync import SyncState, _save_sync_cache
        # Pre-populate cache
        _save_sync_cache({
            "server_state": {"trial": {"active": True}},
            "synced_at": time.time() - 7200,  # 2 hours ago
        })
        SyncState.reset()
        with patch("clouvel.licensing.sync._http_post", return_value=None), \
             patch("clouvel.licensing.sync.get_machine_id", return_value="testmachineid123"), \
             patch("clouvel.licensing.sync._get_license_key", return_value=None):
            ss = SyncState.get()
            result = ss.sync(force=True)
            assert result.get("trial", {}).get("active") is True

    def test_sync_skips_if_recent(self, patch_clouvel_dir):
        from clouvel.licensing.sync import SyncState
        ss = SyncState.get()
        ss._synced_at = time.time()
        ss._state = {"trial": {"active": False}}
        # Should NOT call server
        with patch("clouvel.licensing.sync._http_post") as mock_post:
            result = ss.sync()
            mock_post.assert_not_called()
            assert result["trial"]["active"] is False


# ============================================================
# State accessors
# ============================================================

class TestAccessors:
    def test_get_trial_status(self):
        from clouvel.licensing.sync import SyncState
        ss = SyncState.get()
        ss._state = {"trial": {"active": True, "remaining_days": 3}}
        assert ss.get_trial_status()["remaining_days"] == 3

    def test_get_first_project(self):
        from clouvel.licensing.sync import SyncState
        ss = SyncState.get()
        ss._state = {"first_project": {"path_hash": "xyz", "locked": True}}
        assert ss.get_first_project()["path_hash"] == "xyz"

    def test_get_meeting_quota(self):
        from clouvel.licensing.sync import SyncState
        ss = SyncState.get()
        ss._state = {"meeting_quota": {"used": 2, "remaining": 1}}
        assert ss.get_meeting_quota()["used"] == 2

    def test_get_experiment(self):
        from clouvel.licensing.sync import SyncState
        ss = SyncState.get()
        ss._state = {"experiments": {"meeting_quota": "variant_a"}}
        assert ss.get_experiment("meeting_quota") == "variant_a"
        assert ss.get_experiment("nonexistent") is None


# ============================================================
# Direct server calls (mocked)
# ============================================================

class TestDirectCalls:
    def test_start_trial_success(self):
        from clouvel.licensing.sync import SyncState
        with patch("clouvel.licensing.sync._http_post_with_status",
                    return_value=(200, {"active": True, "started_at": "2026-02-22", "remaining_days": 7})), \
             patch("clouvel.licensing.sync.get_machine_id", return_value="testmachineid123"):
            ss = SyncState.get()
            result = ss.start_trial()
            assert result["active"] is True
            assert result["remaining_days"] == 7

    def test_start_trial_already_started(self):
        from clouvel.licensing.sync import SyncState
        with patch("clouvel.licensing.sync._http_post_with_status",
                    return_value=(409, {"error": "trial_already_started", "remaining_days": 3})), \
             patch("clouvel.licensing.sync.get_machine_id", return_value="testmachineid123"):
            ss = SyncState.get()
            result = ss.start_trial()
            assert result["remaining_days"] == 3

    def test_start_trial_server_down(self):
        from clouvel.licensing.sync import SyncState
        with patch("clouvel.licensing.sync._http_post_with_status",
                    return_value=(0, None)), \
             patch("clouvel.licensing.sync.get_machine_id", return_value="testmachineid123"):
            ss = SyncState.get()
            result = ss.start_trial()
            assert result is None

    def test_register_project(self):
        from clouvel.licensing.sync import SyncState
        with patch("clouvel.licensing.sync._http_post",
                    return_value={"registered": True, "is_first": True, "tier": "first"}), \
             patch("clouvel.licensing.sync.get_machine_id", return_value="testmachineid123"):
            ss = SyncState.get()
            result = ss.register_project("abc123hash")
            assert result["is_first"] is True

    def test_consume_meeting(self):
        from clouvel.licensing.sync import SyncState
        with patch("clouvel.licensing.sync._http_post",
                    return_value={"allowed": True, "used": 1, "remaining": 2}), \
             patch("clouvel.licensing.sync.get_machine_id", return_value="testmachineid123"):
            ss = SyncState.get()
            result = ss.consume_meeting(project_hash="xyz")
            assert result["allowed"] is True
            assert result["remaining"] == 2

    def test_assign_experiment(self):
        from clouvel.licensing.sync import SyncState
        with patch("clouvel.licensing.sync._http_post",
                    return_value={"variant": "variant_a", "source": "server"}), \
             patch("clouvel.licensing.sync.get_machine_id", return_value="testmachineid123"):
            ss = SyncState.get()
            variant = ss.assign_experiment("meeting_quota")
            assert variant == "variant_a"


# ============================================================
# Pending sync queue
# ============================================================

class TestPendingSync:
    def test_mark_and_load_pending(self, patch_clouvel_dir):
        from clouvel.licensing.sync import mark_pending_sync, _load_pending
        mark_pending_sync("trial_start", {"started_at": "2026-02-22"})
        pending = _load_pending()
        assert len(pending) == 1
        assert pending[0]["action"] == "trial_start"

    def test_pending_limit_50(self, patch_clouvel_dir):
        from clouvel.licensing.sync import mark_pending_sync, _load_pending
        for i in range(60):
            mark_pending_sync(f"action_{i}", {"i": i})
        pending = _load_pending()
        assert len(pending) == 50
        # Should keep the last 50
        assert pending[0]["action"] == "action_10"


# ============================================================
# sync_async (background thread)
# ============================================================

class TestSyncAsync:
    def test_sync_async_fires_background(self, patch_clouvel_dir):
        from clouvel.licensing.sync import SyncState
        with patch("clouvel.licensing.sync._http_post", return_value=None), \
             patch("clouvel.licensing.sync.get_machine_id", return_value="testmachineid123"), \
             patch("clouvel.licensing.sync._get_license_key", return_value=None):
            ss = SyncState.get()
            ss.sync_async()
            # Give the thread a moment
            import time as t
            t.sleep(0.2)
            # No crash = success (fire-and-forget)
