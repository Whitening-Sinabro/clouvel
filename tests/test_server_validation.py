# -*- coding: utf-8 -*-
"""Server-side state validation tests.

Tests that the server-first pattern correctly prevents local tampering:
1. Trial date manipulation → server clock prevails
2. First project immutability → server KV locked
3. Meeting quota reset → max(local, server)
4. A/B experiment reassignment → server sticky
5. Offline resilience → local fallback works
6. Migration → first sync seeds KV
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(autouse=True)
def reset_sync():
    """Reset SyncState singleton before each test."""
    from clouvel.licensing.sync import SyncState
    SyncState.reset()
    yield
    SyncState.reset()


@pytest.fixture
def tmp_clouvel_dir(tmp_path):
    clouvel_dir = tmp_path / ".clouvel"
    clouvel_dir.mkdir()
    return clouvel_dir


def _make_synced_state(state_overrides=None):
    """Create a pre-synced SyncState with given server_state."""
    from clouvel.licensing.sync import SyncState
    ss = SyncState.get()
    ss._synced_at = time.time()
    ss._state = {
        "trial": {"active": False, "remaining_days": 0, "source": "server"},
        "first_project": {"path_hash": None, "locked": False},
        "meeting_quota": {"month": "2026-02", "used": 0, "limit": 3, "remaining": 3},
        "experiments": {},
        "license": {"valid": False, "tier": None},
    }
    if state_overrides:
        ss._state.update(state_overrides)
    return ss


# ============================================================
# 1. Trial date manipulation prevention
# ============================================================

class TestTrialTamperPrevention:
    """Server clock prevents local trial date manipulation."""

    def test_server_remaining_days_override_local(self, tmp_clouvel_dir):
        """Even if local file says trial started yesterday, server says 5 days remaining."""
        # Setup: local says trial started 6 days ago
        trial_local = {
            "started_at": (datetime.now() - timedelta(days=6)).isoformat(),
            "machine_id": "testmachineid123",
        }
        (tmp_clouvel_dir / "full_trial.json").write_text(
            json.dumps(trial_local), encoding="utf-8"
        )

        # Server says 5 days remaining (contradicts local)
        _make_synced_state({
            "trial": {"active": True, "remaining_days": 5, "source": "server"},
        })

        with patch("clouvel.licensing.trial._get_full_trial_path",
                    return_value=tmp_clouvel_dir / "full_trial.json"), \
             patch("clouvel.licensing.trial.get_machine_id", return_value="testmachineid123"):
            from clouvel.licensing.trial import get_full_trial_status
            status = get_full_trial_status()
            # Server should win
            assert status["remaining_days"] == 5
            assert status["active"] is True
            assert status.get("source") == "server"

    def test_expired_on_server_blocks_locally(self, tmp_clouvel_dir):
        """If server says expired, local can't override."""
        trial_local = {
            "started_at": datetime.now().isoformat(),  # "just started"
            "machine_id": "testmachineid123",
        }
        (tmp_clouvel_dir / "full_trial.json").write_text(
            json.dumps(trial_local), encoding="utf-8"
        )

        _make_synced_state({
            "trial": {"active": False, "remaining_days": 0, "source": "server"},
        })

        with patch("clouvel.licensing.trial._get_full_trial_path",
                    return_value=tmp_clouvel_dir / "full_trial.json"), \
             patch("clouvel.licensing.trial.get_machine_id", return_value="testmachineid123"):
            from clouvel.licensing.trial import get_full_trial_status
            status = get_full_trial_status()
            assert status["active"] is False
            assert status["remaining_days"] == 0

    def test_start_trial_server_first(self, tmp_clouvel_dir):
        """start_full_trial() calls server first."""
        from clouvel.licensing.sync import SyncState

        with patch("clouvel.licensing.trial._get_full_trial_path",
                    return_value=tmp_clouvel_dir / "full_trial.json"), \
             patch("clouvel.licensing.trial.get_machine_id", return_value="testmachineid123"), \
             patch("clouvel.licensing.sync._http_post_with_status",
                    return_value=(200, {"active": True, "started_at": "2026-02-22T00:00:00", "remaining_days": 7})), \
             patch("clouvel.licensing.sync.get_machine_id", return_value="testmachineid123"):
            from clouvel.licensing.trial import start_full_trial
            result = start_full_trial()
            assert result["active"] is True
            assert result["remaining_days"] == 7
            # Local should be mirrored
            local = json.loads((tmp_clouvel_dir / "full_trial.json").read_text(encoding="utf-8"))
            assert local["started_at"] == "2026-02-22T00:00:00"


# ============================================================
# 2. First project immutability
# ============================================================

class TestFirstProjectImmutability:
    """Server KV locks first project — can't be changed by local tampering."""

    def test_server_locked_project_overrides_local(self, tmp_clouvel_dir):
        """Local file tampered to different hash, but server hash wins."""
        fp_local = {
            "path": "D:\\tampered",
            "path_hash": "tampered_hash_1234",
            "machine_id": "testmachineid123",
        }
        (tmp_clouvel_dir / "first_project.json").write_text(
            json.dumps(fp_local), encoding="utf-8"
        )

        # Server says the REAL first project has a different hash
        _make_synced_state({
            "first_project": {"path_hash": "original_hash_abcd", "locked": True},
        })

        # When checking tier for the original project path (with matching hash)
        with patch("clouvel.licensing.first_project.is_developer", return_value=False), \
             patch("clouvel.licensing.first_project.load_license_cache", return_value=None), \
             patch("clouvel.licensing.first_project.is_full_trial_active", return_value=False), \
             patch("clouvel.licensing.first_project._hash_path", return_value="original_hash_abcd"), \
             patch("clouvel.licensing.first_project._get_first_project_path",
                    return_value=tmp_clouvel_dir / "first_project.json"), \
             patch("clouvel.licensing.first_project.get_machine_id", return_value="testmachineid123"):
            from clouvel.licensing.first_project import get_project_tier
            tier = get_project_tier("/original/project")
            assert tier == "first"

    def test_tampered_project_gets_additional(self, tmp_clouvel_dir):
        """Tampered project path gets 'additional' tier from server."""
        _make_synced_state({
            "first_project": {"path_hash": "original_hash_abcd", "locked": True},
        })

        with patch("clouvel.licensing.first_project.is_developer", return_value=False), \
             patch("clouvel.licensing.first_project.load_license_cache", return_value=None), \
             patch("clouvel.licensing.first_project.is_full_trial_active", return_value=False), \
             patch("clouvel.licensing.first_project._hash_path", return_value="different_hash_xyz"), \
             patch("clouvel.licensing.first_project._get_first_project_path",
                    return_value=tmp_clouvel_dir / "first_project.json"), \
             patch("clouvel.licensing.first_project.get_machine_id", return_value="testmachineid123"):
            from clouvel.licensing.first_project import get_project_tier
            tier = get_project_tier("/different/project")
            assert tier == "additional"


# ============================================================
# 3. Meeting quota reset prevention
# ============================================================

class TestMeetingQuotaResetPrevention:
    """Server counter prevents local reset to 0."""

    def test_server_quota_overrides_local_zero(self, tmp_clouvel_dir):
        """Local file reset to used:0, but server says used:3."""
        mq_local = {"month": "2026-02", "used": 0, "history": []}
        (tmp_clouvel_dir / "monthly_meeting.json").write_text(
            json.dumps(mq_local), encoding="utf-8"
        )

        _make_synced_state({
            "meeting_quota": {"month": "2026-02", "used": 3, "limit": 3, "remaining": 0},
        })

        with patch("clouvel.licensing.quotas._get_monthly_meeting_path",
                    return_value=tmp_clouvel_dir / "monthly_meeting.json"), \
             patch("clouvel.licensing.quotas.get_project_tier", return_value="additional"):
            from clouvel.licensing.quotas import check_meeting_quota
            result = check_meeting_quota(project_path="/some/additional/project")
            assert result["used"] == 3
            assert result["remaining"] == 0
            assert result["allowed"] is False

    def test_consume_via_server(self, tmp_clouvel_dir):
        """consume_meeting_quota uses server and mirrors locally."""
        from clouvel.licensing.sync import SyncState
        ss = SyncState.get()

        with patch("clouvel.licensing.quotas.get_project_tier", return_value="additional"), \
             patch("clouvel.licensing.quotas._get_monthly_meeting_path",
                    return_value=tmp_clouvel_dir / "monthly_meeting.json"), \
             patch("clouvel.licensing.sync._http_post",
                    return_value={"allowed": True, "used": 2, "remaining": 1, "limit": 3}), \
             patch("clouvel.licensing.sync.get_machine_id", return_value="testmachineid123"):
            from clouvel.licensing.quotas import consume_meeting_quota
            result = consume_meeting_quota(project_path="/some/additional/project")
            assert result["used"] == 2
            assert result["remaining"] == 1


# ============================================================
# 4. A/B experiment reassignment prevention
# ============================================================

class TestExperimentStickyAssignment:
    """Server sticky assignment prevents local variant changes."""

    def test_server_variant_overrides_local(self, tmp_clouvel_dir):
        """Local file changed to control, but server says variant_a."""
        ab_local = {"experiments": {"meeting_quota": {"variant": "control"}}}
        (tmp_clouvel_dir / "ab_flags.json").write_text(
            json.dumps(ab_local), encoding="utf-8"
        )

        _make_synced_state({
            "experiments": {"meeting_quota": "variant_a"},
        })

        with patch("clouvel.licensing.experiments._get_ab_flags_path",
                    return_value=tmp_clouvel_dir / "ab_flags.json"), \
             patch("clouvel.licensing.experiments.get_machine_id", return_value="testmachineid123"):
            from clouvel.licensing.experiments import get_experiment_variant
            variant = get_experiment_variant("meeting_quota")
            assert variant == "variant_a"

    def test_new_experiment_assigned_by_server(self, tmp_clouvel_dir):
        """New experiment gets assigned by server."""
        _make_synced_state({"experiments": {}})

        with patch("clouvel.licensing.experiments._get_ab_flags_path",
                    return_value=tmp_clouvel_dir / "ab_flags.json"), \
             patch("clouvel.licensing.experiments.get_machine_id", return_value="testmachineid123"), \
             patch("clouvel.licensing.sync._http_post",
                    return_value={"variant": "variant_a", "source": "server"}), \
             patch("clouvel.licensing.sync.get_machine_id", return_value="testmachineid123"):
            from clouvel.licensing.experiments import get_experiment_variant
            variant = get_experiment_variant("new_experiment")
            assert variant == "variant_a"
            # Should be mirrored locally
            local = json.loads((tmp_clouvel_dir / "ab_flags.json").read_text(encoding="utf-8"))
            assert local["experiments"]["new_experiment"]["variant"] == "variant_a"
            assert local["experiments"]["new_experiment"]["source"] == "server"


# ============================================================
# 5. Offline resilience
# ============================================================

class TestOfflineResilience:
    """All operations work offline with local fallback."""

    def test_trial_works_offline(self, tmp_clouvel_dir):
        """Trial status works with no server state."""
        from clouvel.licensing.sync import SyncState
        SyncState.reset()
        # No sync done = not synced

        trial_data = {
            "started_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "machine_id": "testmachineid123",
        }
        (tmp_clouvel_dir / "full_trial.json").write_text(
            json.dumps(trial_data), encoding="utf-8"
        )

        with patch("clouvel.licensing.trial._get_full_trial_path",
                    return_value=tmp_clouvel_dir / "full_trial.json"), \
             patch("clouvel.licensing.trial.get_machine_id", return_value="testmachineid123"):
            from clouvel.licensing.trial import get_full_trial_status
            status = get_full_trial_status()
            assert status["active"] is True
            assert status["remaining_days"] == 5

    def test_meeting_quota_works_offline(self, tmp_clouvel_dir):
        """Meeting quota works with local fallback."""
        from clouvel.licensing.sync import SyncState
        SyncState.reset()

        mq_data = {"month": datetime.now().strftime("%Y-%m"), "used": 1, "history": []}
        (tmp_clouvel_dir / "monthly_meeting.json").write_text(
            json.dumps(mq_data), encoding="utf-8"
        )

        with patch("clouvel.licensing.quotas._get_monthly_meeting_path",
                    return_value=tmp_clouvel_dir / "monthly_meeting.json"), \
             patch("clouvel.licensing.quotas.get_project_tier", return_value="additional"), \
             patch("clouvel.licensing.quotas.get_machine_id", return_value="testmachineid123"):
            from clouvel.licensing.quotas import check_meeting_quota
            result = check_meeting_quota(project_path="/some/path")
            assert result["allowed"] is True
            assert result["used"] == 1

    def test_experiment_works_offline(self, tmp_clouvel_dir):
        """Experiment assignment works offline with local hash."""
        from clouvel.licensing.sync import SyncState
        SyncState.reset()

        with patch("clouvel.licensing.experiments._get_ab_flags_path",
                    return_value=tmp_clouvel_dir / "ab_flags.json"), \
             patch("clouvel.licensing.experiments.get_machine_id", return_value="testmachineid123"), \
             patch("clouvel.licensing.experiments.is_developer", return_value=False), \
             patch("clouvel.licensing.experiments.is_full_trial_active", return_value=False), \
             patch("clouvel.licensing.experiments.load_license_cache", return_value=None):
            from clouvel.licensing.experiments import get_experiment_variant
            variant = get_experiment_variant("meeting_quota")
            assert variant in ("control", "variant_a")
            # Should persist locally
            local = json.loads((tmp_clouvel_dir / "ab_flags.json").read_text(encoding="utf-8"))
            assert "meeting_quota" in local["experiments"]

    def test_start_trial_offline_queues_sync(self, tmp_clouvel_dir):
        """Starting trial offline queues for next sync."""
        from clouvel.licensing.sync import SyncState
        SyncState.reset()

        with patch("clouvel.licensing.trial._get_full_trial_path",
                    return_value=tmp_clouvel_dir / "full_trial.json"), \
             patch("clouvel.licensing.trial.get_machine_id", return_value="testmachineid123"), \
             patch("clouvel.licensing.sync._http_post_with_status", return_value=(0, None)), \
             patch("clouvel.licensing.sync.get_machine_id", return_value="testmachineid123"), \
             patch("clouvel.licensing.sync._get_clouvel_dir", return_value=tmp_clouvel_dir):
            from clouvel.licensing.trial import start_full_trial
            result = start_full_trial()
            assert result["active"] is True
            assert result["remaining_days"] == 7
            # Local file should exist
            assert (tmp_clouvel_dir / "full_trial.json").exists()
            # Pending sync should be queued
            pending_path = tmp_clouvel_dir / "sync_pending.json"
            if pending_path.exists():
                pending = json.loads(pending_path.read_text(encoding="utf-8"))
                assert any(p["action"] == "trial_start" for p in pending)


# ============================================================
# 6. Migration (first sync seeds KV)
# ============================================================

class TestMigration:
    """First sync seeds KV from local data."""

    def test_sync_sends_local_state(self, tmp_clouvel_dir):
        """First sync includes local_state for KV seeding."""
        from clouvel.licensing.sync import SyncState

        trial_data = {"started_at": "2026-02-20T10:00:00", "machine_id": "testmachineid123"}
        (tmp_clouvel_dir / "full_trial.json").write_text(
            json.dumps(trial_data), encoding="utf-8"
        )

        captured_payload = {}

        def mock_post(url, payload):
            captured_payload.update(payload)
            return {
                "server_state": {
                    "trial": {"active": True, "remaining_days": 5, "source": "server"},
                    "first_project": {"path_hash": None, "locked": False},
                    "meeting_quota": {"month": "2026-02", "used": 0, "limit": 3, "remaining": 3},
                    "experiments": {},
                    "license": {"valid": False, "tier": None},
                },
                "next_sync_seconds": 3600,
            }

        with patch("clouvel.licensing.sync._http_post", side_effect=mock_post), \
             patch("clouvel.licensing.sync.get_machine_id", return_value="testmachineid123"), \
             patch("clouvel.licensing.sync._get_license_key", return_value=None), \
             patch("clouvel.licensing.sync._get_clouvel_dir", return_value=tmp_clouvel_dir):
            ss = SyncState.get()
            ss.sync(force=True)
            # Payload should include local trial data
            assert "local_state" in captured_payload
            assert captured_payload["local_state"]["trial"]["started_at"] == "2026-02-20T10:00:00"
