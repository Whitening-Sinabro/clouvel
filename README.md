# Clouvel

> **AI makes it fast. Clouvel makes it right.**

[![PyPI](https://img.shields.io/pypi/v/clouvel)](https://pypi.org/project/clouvel/)
[![Python](https://img.shields.io/pypi/pyversions/clouvel)](https://pypi.org/project/clouvel/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Your AI remembers its mistakes.** Regression Memory records every error and auto-warns before it happens again.

**Try all Pro features free for 7 days** — no credit card required. Run `start_trial` in Claude Code.

---

![Demo](docs/landing/assets/demo.gif)

---

## Why Clouvel?

AI coding is fast but forgetful:

| The Pain | What Actually Happens |
|----------|----------------------|
| AI repeats mistakes | Fixed a bug yesterday, AI recreates it today |
| No one reviews your code | Ship bugs you'd catch with a second pair of eyes |
| You forget past decisions | "Why did we do it this way?" — no one remembers |
| Context resets every session | New chat = new AI = same old mistakes |

**Free to act. Paid to remember.**

---

## What Clouvel Does

### 1. Memory — AI that learns from its mistakes
```
AI:  ⚠️ REGRESSION MATCH: This error happened before.
     Root cause: Missing null check on DB query result
     Prevention: Always validate query results before accessing properties
     (Memory #7 — hit 4 times, saved 3 bugs)
```

### 2. Feedback — 8 managers review in 30 seconds
```
👔 PM:  "User story covers happy path, but what about failed attempts?"
🛠️ CTO: "Consider rate limiting for brute force protection."
🔒 CSO: "⚠️ Password hashing not implemented."
```

### 3. Gate — Think before AI codes
```
You: "Build login"
AI:  ❌ BLOCKED - No PRD found. Write a spec first.

You: *writes PRD with requirements*
AI:  ✅ PASS - Ready to code.
```

**Memory + Feedback + Gate = AI that gets smarter over time.**

---

## Quick Start

```bash
# Install
pip install clouvel

# Add to Claude Code (auto-detects your platform)
clouvel install

# Start coding - can_code check runs automatically
claude
```

That's it. No config needed.

---

## FREE vs PRO

| | FREE | PRO ($7.99/mo) |
|---|---|---|
| **Projects** | 1 active (archive to switch) | Unlimited |
| **Templates** | `lite` + `minimal` | All (`lite` + `standard` + `detailed`) |
| **Managers** | 1 (PM only) | 8 (PM, CTO, QA, CDO, CMO, CFO, CSO, Error) |
| **Meeting** | 3 full meetings/month | Unlimited |
| **can_code** | WARN (doesn't block) | BLOCK (enforces PRD) |
| **Knowledge Base** | 7-day retention | Persistent across sessions |
| **Regression Memory** | - | Records errors, auto-warns on repeat, monthly report |
| **Error Learning** | - | Learns from your mistakes |
| **Execution Plan** | - | `plan` with step-by-step actions |

**Want to try everything?** Start a 7-day free trial — all Pro features, no credit card.

```
> start_trial
✅ 7-day Pro trial activated!
```

**[Get Pro →](https://polar.sh/clouvel)** Use code `LAUNCH70` for 70% off annual ($23.99/yr)

---

## Key Tools

| Tool | What it does | FREE | PRO |
|------|--------------|------|-----|
| `can_code` | Checks if you can start coding | WARN | BLOCK |
| `start` | Project onboarding + PRD templates | `lite` | All templates |
| `quick_perspectives` | Quick blind-spot check (3-4 managers) | ✓ | ✓ |
| `manager` | C-Level review meeting | PM only | 8 managers |
| `meeting` | Natural meeting transcript | 3/month | Unlimited |
| `plan` | Detailed execution planning | - | ✓ |
| `ship` | lint → test → build pipeline | - | ✓ |
| `record_decision` | Save decisions to Knowledge Base | - | ✓ |
| `error_learn` | Learn from mistakes | - | ✓ |
| `memory_status` | Regression Memory dashboard | - | ✓ |
| `memory_search` | Search past error patterns | - | ✓ |
| `memory_report` | Monthly savings report | - | ✓ |
| `memory_global_search` | Search memories across all projects | - | ✓ |
| `set_project_domain` | Isolate memories by domain (personal/work/client) | - | ✓ |
| `start_trial` | Activate 7-day Pro trial | ✓ | - |

**7 project types:** web-app, api, cli, chrome-ext, discord-bot, landing-page, saas

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

## Usage Examples

### Block coding without PRD

```
You: "Build a user authentication system"

Clouvel: ❌ BLOCKED
- PRD.md not found
- Architecture.md not found

💡 Write a PRD first. Use `start` to begin.
```

### Start a new project

```
You: "Start a new project"

Clouvel: 🚀 Project detected: web-app

Questions:
1. What's the main goal?
2. Who are the users?
3. What are the core features?

→ Generates PRD from your answers
```

### Get manager feedback (Pro)

```
You: "Review my login implementation"

👔 PM: User story covers happy path, but what about failed attempts?
🛠️ CTO: Consider rate limiting for brute force protection.
🧪 QA: Need tests for edge cases - empty password, SQL injection.
🔒 CSO: ⚠️ CRITICAL - Password hashing not implemented.

Status: NEEDS_REVISION
```

---

## Links

- [Documentation](https://whitening-sinabro.github.io/clouvel/)
- [Changelog](CHANGELOG.md)
- [Report bugs](https://github.com/Whitening-Sinabro/clouvel/issues)
- [Contribute](CONTRIBUTING.md)

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>AI makes it fast. Clouvel makes it right.</b><br>
  <a href="https://whitening-sinabro.github.io/clouvel/">Website</a> •
  <a href="https://github.com/Whitening-Sinabro/clouvel/issues">Issues</a> •
  <a href="https://polar.sh/clouvel">Get Pro</a>
</p>
