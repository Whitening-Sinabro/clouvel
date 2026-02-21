# Clouvel

> **Stop Claude Code from breaking your code.**

[![PyPI](https://img.shields.io/pypi/v/clouvel)](https://pypi.org/project/clouvel/)
[![Python](https://img.shields.io/pypi/pyversions/clouvel)](https://pypi.org/project/clouvel/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Claude Code is fast. But it forgets what it broke yesterday and breaks it again today.

**Clouvel remembers.** It records every error, warns before repeats, and blocks coding without a spec.

---

## The Problem

| What happens | Why it hurts |
|-------------|-------------|
| AI recreates a bug it fixed yesterday | No error memory between sessions |
| You ship without anyone reviewing | No second pair of eyes |
| "Why did we do it this way?" | Decisions lost when context resets |
| New session = same old mistakes | AI starts from zero every time |

## What Clouvel Does

### 1. Error Memory — AI that learns from mistakes
```
AI:  Warning: This error happened before.
     Root cause: Missing null check on DB query result
     Prevention: Always validate query results before accessing
     (Memory #7 — prevented this bug 3 times)
```

### 2. Spec Gate — Think before AI codes
```
You: "Build login"
AI:  BLOCKED - No PRD found. Write a spec first.

You: *writes PRD*
AI:  PASS - Ready to code.
```

### 3. Quick Check — Blind spots in 10 seconds
```
PM:  "What happens when login fails 5 times?"
CTO: "Rate limiting needed for brute force protection."
```

---

## Quick Start

```bash
pip install clouvel

# Auto-configure for Claude Code / Claude Desktop / VS Code
clouvel install

# Start coding
claude
```

That's it. Clouvel runs automatically.

---

## Tools

### Free (10 tools — always available)

| Tool | What it does |
|------|-------------|
| `can_code` | Blocks coding without a spec |
| `start` | Set up a new project with PRD templates |
| `save_prd` | Save your PRD from conversation |
| `error_check` | Warns before repeating past mistakes |
| `error_record` | Records errors with root cause analysis |
| `context_save` | Saves working state before context runs out |
| `context_load` | Restores state in a new session |
| `quick_perspectives` | Quick blind-spot check (2 managers) |
| `gate` | Run lint, test, build in sequence |
| `license_status` | Check plan, activate license, start trial |

### Pro (10 more tools — $7.99/mo)

| Tool | What it does |
|------|-------------|
| `error_learn` | Auto-generates NEVER/ALWAYS rules from error patterns |
| `memory_status` | Error memory dashboard with hit counts |
| `memory_search` | Search past errors by keyword |
| `memory_global_search` | Share error patterns across all projects |
| `drift_check` | Detects when work drifts from goals |
| `plan` | Detailed execution plans with dependencies |
| `meeting` | Full 8-manager C-Level review |
| `ship` | One-click lint+test+build with evidence |
| `record_decision` | Persistent knowledge base for decisions |
| `search_knowledge` | Search past decisions and context |

---

## Free vs Pro

| | Free | Pro ($7.99/mo) |
|---|---|---|
| **Error history** | Last 5 errors | Full history + patterns |
| **Context slots** | 1 (overwrites) | 50 + timeline |
| **Manager feedback** | 2 managers, 1 question | 8 managers, 2+ questions |
| **Error learning** | - | Auto-generates rules |
| **Cross-project memory** | - | Share lessons everywhere |
| **Drift detection** | - | Catches scope creep |
| **Ship pipeline** | gate (basic) | Full verify + evidence |

**Try Pro free for 7 days** — no credit card:
```
> license_status(action="trial")
```

---

## Installation

### Requirements

- Python 3.10+
- Claude Code, Claude Desktop, or VS Code with Claude extension

### Install

```bash
pip install clouvel
```

### Connect to Claude

**Automatic (recommended):**
```bash
clouvel install
```

<details>
<summary>Manual configuration</summary>

**Windows:**
```json
{
  "mcpServers": {
    "clouvel": {
      "command": "py",
      "args": ["-m", "clouvel.server"]
    }
  }
}
```

**Mac/Linux:**
```json
{
  "mcpServers": {
    "clouvel": {
      "command": "python3",
      "args": ["-m", "clouvel.server"]
    }
  }
}
```

</details>

---

## How It Works

```
Day 1:  Install → start → write PRD → can_code PASS → code
Day 3:  Error happens → error_record saves it
Day 5:  Same file → error_check warns "this broke before"
Day 7:  5+ errors → "Full history available in Pro"
Day 10: Context runs out → context_save/load preserves everything
Day 14: Decide: $7.99/mo or stay Free
```

---

## Links

- [Website](https://clouvels.com)
- [Docs](https://clouvels.com/docs-en.html)
- [Changelog](CHANGELOG.md)
- [Report bugs](https://github.com/Whitening-Sinabro/clouvel/issues)

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>Stop Claude Code from breaking your code.</b><br>
  <a href="https://github.com/Whitening-Sinabro/clouvel/issues">Issues</a>
</p>
