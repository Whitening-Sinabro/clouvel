# -*- coding: utf-8 -*-
"""E2E Free User Scenario Tests — v6.0: all features free.

v6.0: Scenarios updated to reflect no Pro gating.
Scenarios 1-2 now verify that everything is allowed.
Scenarios 3-6 test features that still work (warn count, events, A/B).
"""

import json
import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def setup_clean_env(tmp_dir):
    """Clean ~/.clouvel simulation in temp dir."""
    clouvel_dir = Path(tmp_dir) / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir


# ============================================================
# SCENARIO 1: Project Registration (v6.0: always allowed)
# ============================================================
def test_scenario_1_project_limit():
    """v6.0: All projects are allowed, no limit."""
    with tempfile.TemporaryDirectory() as tmp:
        clouvel_dir = setup_clean_env(tmp)

        from clouvel.licensing.projects import register_project

        r1 = register_project(str(Path(tmp) / "project-alpha"))
        assert r1["allowed"] is True

        r2 = register_project(str(Path(tmp) / "project-beta"))
        assert r2["allowed"] is True

        r3 = register_project(str(Path(tmp) / "project-gamma"))
        assert r3["allowed"] is True


# ============================================================
# SCENARIO 3: Weekly Meeting Trial
# ============================================================
def test_scenario_3_weekly_meeting():
    with tempfile.TemporaryDirectory() as tmp:
        clouvel_dir = setup_clean_env(tmp)
        weekly_file = clouvel_dir / "weekly_meeting.json"

        project_path = str(Path(tmp) / "my-project")

        with patch("clouvel.licensing.quotas._get_weekly_meeting_path", return_value=weekly_file):
            from clouvel.licensing.quotas import can_use_weekly_full_meeting, mark_weekly_meeting_used

            check1 = can_use_weekly_full_meeting(project_path)
            assert check1["available"] is True

            mark_weekly_meeting_used(project_path)

            check2 = can_use_weekly_full_meeting(project_path)
            assert check2["available"] is False


# ============================================================
# SCENARIO 4: WARN Accumulation
# ============================================================
def test_scenario_4_warn_accumulation():
    with tempfile.TemporaryDirectory() as tmp:
        clouvel_dir = setup_clean_env(tmp)
        warn_file = clouvel_dir / "warn_count.json"

        project_path = str(Path(tmp) / "my-project")

        with patch("clouvel.licensing.quotas._get_warn_count_path", return_value=warn_file):
            from clouvel.licensing.quotas import increment_warn_count, get_warn_count

            results = []
            for i in range(1, 6):
                count = increment_warn_count(project_path)
                results.append(count)

            assert results == [1, 2, 3, 4, 5]
            final_count = get_warn_count(project_path)
            assert final_count == 5


# ============================================================
# SCENARIO 5: Event Logging
# ============================================================
def test_scenario_5_event_logging():
    with tempfile.TemporaryDirectory() as tmp:
        clouvel_dir = Path(tmp) / ".clouvel"
        clouvel_dir.mkdir(parents=True, exist_ok=True)

        with patch("clouvel.analytics.Path.home", return_value=Path(tmp)):
            with patch.dict(os.environ, {"USERPROFILE": tmp}):
                from clouvel.analytics import log_event

                log_event("test_event_1", {"key": "value"})
                log_event("test_event_2", {"key": "value"})


# ============================================================
# SCENARIO 6: A/B Test Flags
# ============================================================
def test_scenario_6_ab_flags():
    with tempfile.TemporaryDirectory() as tmp:
        clouvel_dir = Path(tmp) / ".clouvel"
        clouvel_dir.mkdir(parents=True, exist_ok=True)
        ab_file = clouvel_dir / "ab_flags.json"

        with patch("clouvel.licensing.experiments._get_ab_flags_path", return_value=ab_file):
            from clouvel.licensing.experiments import get_experiment_variant, EXPERIMENTS

            group1 = get_experiment_variant("pain_point_message")
            valid_variants = EXPERIMENTS.get("pain_point_message", {}).get("variants", ["control"])
            assert group1 in valid_variants

            group2 = get_experiment_variant("pain_point_message")
            assert group1 == group2
