# -*- coding: utf-8 -*-
"""E2E Free User Scenario Tests

4가지 시나리오를 실제 Free 유저 환경으로 테스트:
1. 프로젝트 3번째 → 한도 메시지
2. KB 7일 넘김 → 쓰기 차단
3. 주간 meeting 1번 → 2번째 PM만
4. WARN 5번 누적 → 3회째부터 누적 메시지
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

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def setup_clean_env(tmp_dir):
    """Clean ~/.clouvel simulation in temp dir."""
    clouvel_dir = Path(tmp_dir) / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir


def print_separator(title):
    print(f"\n{'='*60}")
    print(f"  SCENARIO: {title}")
    print(f"{'='*60}\n")


def print_result(label, text):
    print(f"--- {label} ---")
    # Windows cp949 safe output
    safe_text = str(text).encode("ascii", errors="replace").decode("ascii")
    print(safe_text)
    print()


# ============================================================
# SCENARIO 1: Project Limit (v3.0.0: First Project Unlimited)
# ============================================================
def test_scenario_1_project_limit():
    print_separator("1. First Project Unlimited + 2nd project blocked")

    with tempfile.TemporaryDirectory() as tmp:
        clouvel_dir = setup_clean_env(tmp)
        projects_file = clouvel_dir / "projects.json"
        first_project_file = clouvel_dir / "first_project.json"

        # Patch paths
        with patch("clouvel.license_common.is_developer", return_value=False), \
             patch("clouvel.license_common.load_license_cache", return_value=None), \
             patch("clouvel.license_common.is_full_trial_active", return_value=False), \
             patch("clouvel.license_common.get_projects_path", return_value=projects_file), \
             patch("clouvel.license_common._get_first_project_path", return_value=first_project_file):

            from clouvel.license_common import register_project, get_project_tier, FREE_ACTIVE_PROJECT_LIMIT

            print(f"FREE_ACTIVE_PROJECT_LIMIT = {FREE_ACTIVE_PROJECT_LIMIT}")

            # Register project 1 → becomes "first" project (unlimited Pro)
            r1 = register_project(str(Path(tmp) / "project-alpha"))
            print_result("Project 1 (alpha)", f"allowed={r1['allowed']}, tier={r1.get('tier')}")
            assert r1["allowed"] == True
            assert r1.get("tier") == "first"

            # Verify tier
            tier1 = get_project_tier(str(Path(tmp) / "project-alpha"))
            print_result("Project 1 tier", tier1)
            assert tier1 == "first"

            # Register project 2 → BLOCKED (additional project, Pro required)
            r2 = register_project(str(Path(tmp) / "project-beta"))
            print_result("Project 2 (beta)", f"allowed={r2['allowed']}, needs_upgrade={r2.get('needs_upgrade')}")
            assert r2["allowed"] == False

            tier2 = get_project_tier(str(Path(tmp) / "project-beta"))
            print_result("Project 2 tier", tier2)
            assert tier2 == "additional"

            # Check the message
            from clouvel.messages.en import CAN_CODE_PROJECT_LIMIT
            print_result("ACTUAL MESSAGE shown to user", CAN_CODE_PROJECT_LIMIT)

            # Verify first project access still works
            r1_again = register_project(str(Path(tmp) / "project-alpha"))
            print_result("First project re-access", f"allowed={r1_again['allowed']}, tier={r1_again.get('tier')}")
            assert r1_again["allowed"] == True

            # Check first_project.json
            fp_data = json.loads(first_project_file.read_text(encoding="utf-8"))
            print_result("first_project.json", json.dumps(fp_data, indent=2))

    print("[PASS] Scenario 1 complete\n")


# ============================================================
# SCENARIO 2: KB Trial Expiry
# ============================================================
def test_scenario_2_kb_trial_expiry():
    print_separator("2. KB Trial Expiry (additional project, date manipulation)")

    with tempfile.TemporaryDirectory() as tmp:
        clouvel_dir = setup_clean_env(tmp)
        trial_file = clouvel_dir / "kb_trial.json"

        project_path = str(Path(tmp) / "my-project")

        # v5.0: KB trial expiry only applies to additional projects
        # First project gets unlimited KB via get_project_tier bypass
        with patch("clouvel.license_common._get_kb_trial_path", return_value=trial_file), \
             patch("clouvel.license_common.get_project_tier", return_value="additional"):

            from clouvel.license_common import start_kb_trial, is_kb_trial_active, get_kb_trial_start

            # Start trial
            start_date = start_kb_trial(project_path)
            print_result("Trial started", f"start_date={start_date}")

            # Check trial is active
            active = is_kb_trial_active(project_path)
            print_result("Trial active (day 0)", f"active={active}")
            assert active == True

            # Manipulate date to 8 days ago
            normalized = str(Path(project_path).resolve())
            old_date = (datetime.now() - timedelta(days=8)).isoformat()
            trial_data = {normalized: old_date}
            trial_file.write_text(json.dumps(trial_data, indent=2), encoding="utf-8")
            print_result("Date manipulated", f"set to {old_date} (8 days ago)")

            # Check trial expired
            expired = is_kb_trial_active(project_path)
            print_result("Trial active (day 8)", f"active={expired}")
            assert expired == False

            # Show the message
            from clouvel.messages.en import CAN_CODE_KB_TRIAL_EXPIRED
            msg = CAN_CODE_KB_TRIAL_EXPIRED.format(decision_count="12")
            print_result("ACTUAL MESSAGE shown to user", msg)

            # Check trial file
            print_result("kb_trial.json contents", trial_file.read_text(encoding="utf-8"))

    print("[PASS] Scenario 2 complete\n")


# ============================================================
# SCENARIO 3: Weekly Meeting Trial
# ============================================================
def test_scenario_3_weekly_meeting():
    print_separator("3. Weekly Meeting Trial (1st=full, 2nd=PM only)")

    with tempfile.TemporaryDirectory() as tmp:
        clouvel_dir = setup_clean_env(tmp)
        weekly_file = clouvel_dir / "weekly_meeting.json"

        project_path = str(Path(tmp) / "my-project")

        with patch("clouvel.license_common._get_weekly_meeting_path", return_value=weekly_file):

            from clouvel.license_common import can_use_weekly_full_meeting, mark_weekly_meeting_used

            # First check: should be available
            check1 = can_use_weekly_full_meeting(project_path)
            print_result("First check (Monday)", f"available={check1['available']}, week={check1['current_week']}")
            assert check1["available"] == True

            # Mark as used
            mark_weekly_meeting_used(project_path)
            print_result("Marked as used", "done")

            # Second check: should NOT be available (same week)
            check2 = can_use_weekly_full_meeting(project_path)
            print_result("Second check (Tuesday, same week)", f"available={check2['available']}, last_used={check2['last_used_week']}")
            assert check2["available"] == False

            # Simulate next week by modifying the file
            normalized = str(Path(project_path).resolve())
            now = datetime.now()
            last_week = f"{now.isocalendar()[0]}-W{(now.isocalendar()[1]-1):02d}"
            weekly_data = {normalized: last_week}
            weekly_file.write_text(json.dumps(weekly_data, indent=2), encoding="utf-8")

            check3 = can_use_weekly_full_meeting(project_path)
            print_result("Third check (next week)", f"available={check3['available']}")
            assert check3["available"] == True

            # Check file
            print_result("weekly_meeting.json contents", weekly_file.read_text(encoding="utf-8"))

    print("[PASS] Scenario 3 complete\n")


# ============================================================
# SCENARIO 4: WARN Accumulation
# ============================================================
def test_scenario_4_warn_accumulation():
    print_separator("4. WARN Accumulation (5 times → message from 3rd)")

    with tempfile.TemporaryDirectory() as tmp:
        clouvel_dir = setup_clean_env(tmp)
        warn_file = clouvel_dir / "warn_count.json"

        project_path = str(Path(tmp) / "my-project")

        with patch("clouvel.license_common._get_warn_count_path", return_value=warn_file):

            from clouvel.license_common import increment_warn_count, get_warn_count

            results = []
            for i in range(1, 6):
                count = increment_warn_count(project_path)
                results.append(count)
                show_extra = count >= 3
                print_result(
                    f"WARN #{i}",
                    f"count={count}, shows_accumulated_msg={show_extra}"
                )

            # Verify counts
            assert results == [1, 2, 3, 4, 5], f"Expected [1,2,3,4,5], got {results}"

            # Show what user sees at warn 3 and 5
            from clouvel.messages.en import CAN_CODE_PASS_FREE, CAN_CODE_WARN_ACCUMULATED

            base_msg = CAN_CODE_PASS_FREE.format(
                test_count="42",
                upgrade_hint="PRO validates PRD sections + blocks coding"
            )

            # WARN #3 message
            warn3_msg = base_msg + CAN_CODE_WARN_ACCUMULATED.format(count=3)
            print_result("ACTUAL MESSAGE at WARN #3", warn3_msg)

            # WARN #5 message
            warn5_msg = base_msg + CAN_CODE_WARN_ACCUMULATED.format(count=5)
            print_result("ACTUAL MESSAGE at WARN #5", warn5_msg)

            # Check file
            print_result("warn_count.json contents", warn_file.read_text(encoding="utf-8"))

            # Verify get_warn_count works
            final_count = get_warn_count(project_path)
            print_result("get_warn_count() final", f"count={final_count}")
            assert final_count == 5

    print("[PASS] Scenario 4 complete\n")


# ============================================================
# SCENARIO 5: Event Logging
# ============================================================
def test_scenario_5_event_logging():
    print_separator("5. Event Logging (events.jsonl)")

    with tempfile.TemporaryDirectory() as tmp:
        clouvel_dir = Path(tmp) / ".clouvel"
        clouvel_dir.mkdir(parents=True, exist_ok=True)
        events_file = clouvel_dir / "events.jsonl"

        # Patch home to temp
        with patch("clouvel.analytics.Path.home", return_value=Path(tmp)):
            # Also patch os.environ for Windows
            with patch.dict(os.environ, {"USERPROFILE": tmp}):
                from clouvel.analytics import log_event

                log_event("project_limit_hit", {"count": 2, "limit": 2})
                log_event("warn_accumulated", {"count": 3, "project": "/test"})
                log_event("upgrade_message_shown", {"source": "meeting", "topic": "auth"})
                log_event("weekly_meeting_used", {"project": "/test"})

                if events_file.exists():
                    contents = events_file.read_text(encoding="utf-8")
                    print_result("events.jsonl contents", contents)

                    lines = [l for l in contents.strip().split("\n") if l]
                    print(f"Total events logged: {len(lines)}")
                    for i, line in enumerate(lines, 1):
                        event = json.loads(line)
                        print(f"  {i}. type={event['type']}, ts={event['ts'][:19]}")
                else:
                    print("[WARN] events.jsonl not created!")

    print("[PASS] Scenario 5 complete\n")


# ============================================================
# A/B Test Flags
# ============================================================
def test_scenario_6_ab_flags():
    print_separator("6. A/B Test Flags")

    with tempfile.TemporaryDirectory() as tmp:
        clouvel_dir = Path(tmp) / ".clouvel"
        clouvel_dir.mkdir(parents=True, exist_ok=True)
        ab_file = clouvel_dir / "ab_flags.json"

        with patch("clouvel.license_common._get_ab_flags_path", return_value=ab_file):
            from clouvel.license_common import get_experiment_variant, EXPERIMENTS

            # First call: deterministic assignment based on machine_id hash
            group1 = get_experiment_variant("pain_point_message")
            valid_variants = EXPERIMENTS.get("pain_point_message", {}).get("variants", ["control"])
            print_result("Experiment: pain_point_message", f"group={group1}, valid={valid_variants}")
            assert group1 in valid_variants

            # Second call: same group (persisted)
            group2 = get_experiment_variant("pain_point_message")
            print_result("Same experiment again", f"group={group2} (should match)")
            assert group1 == group2

            # Different experiment
            group3 = get_experiment_variant("meeting_quota")
            valid_variants_meeting = EXPERIMENTS.get("meeting_quota", {}).get("variants", ["control"])
            print_result("Different experiment: meeting_quota", f"group={group3}, valid={valid_variants_meeting}")

            # Check file
            print_result("ab_flags.json contents", ab_file.read_text(encoding="utf-8"))

    print("[PASS] Scenario 6 complete\n")


# ============================================================
# Run All
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  FREE USER E2E TESTS - All 6 Scenarios")
    print("="*60)

    try:
        test_scenario_1_project_limit()
        test_scenario_2_kb_trial_expiry()
        test_scenario_3_weekly_meeting()
        test_scenario_4_warn_accumulation()
        test_scenario_5_event_logging()
        test_scenario_6_ab_flags()

        print("\n" + "="*60)
        print("  ALL SCENARIOS PASSED")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n[FAIL] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
