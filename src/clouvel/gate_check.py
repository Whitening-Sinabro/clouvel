#!/usr/bin/env python3
"""Lightweight gate check for Claude Code PreToolUse hook.

Reads .clouvel/gate.json written by can_code() and exits:
  0 = PASS (coding allowed)
  1 = BLOCK (coding denied)

No clouvel imports — just stdlib. Starts in <0.1s.
"""
import json
import sys
import time
import os


def main():
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    gate_file = os.path.join(project_dir, ".clouvel", "gate.json")

    if not os.path.exists(gate_file):
        print("BLOCK: can_code not called yet. Run can_code first.")
        return 1

    try:
        with open(gate_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        print("BLOCK: gate.json corrupted. Run can_code again.")
        return 1

    status = data.get("status", "BLOCK")
    ts = data.get("timestamp", 0)
    ttl = data.get("ttl", 600)

    if time.time() - ts > ttl:
        print("BLOCK: Gate expired. Run can_code again.")
        return 1

    if status == "BLOCK":
        reason = data.get("reason", "")
        print(f"BLOCK: {reason}")
        return 1

    # PASS or WARN → allow
    return 0


if __name__ == "__main__":
    sys.exit(main())
