# Clouvel

> **No spec, no code.** Guardrails that catch what AI misses.

[![PyPI](https://img.shields.io/pypi/v/clouvel)](https://pypi.org/project/clouvel/)
[![Python](https://img.shields.io/pypi/pyversions/clouvel)](https://pypi.org/project/clouvel/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Solo coding, team-level review.** 8 AI managers catch your blind spots before code ships.

---

![Demo](docs/landing/assets/demo.gif)

---

## Why Clouvel?

AI coding is powerful but dangerous:

| The Pain | What Actually Happens |
|----------|----------------------|
| AI skips requirements | "Build login" → No password reset, no social auth |
| No one reviews your code | Ship bugs you'd catch with a second pair of eyes |
| You forget past decisions | Repeat the same debates, waste hours rediscovering context |
| Vibe coding trap | Works today, breaks tomorrow |

**You're building alone. Clouvel makes sure you're not thinking alone.**

---

## What Clouvel Does

### 1. Gate — Think before AI codes
```
You: "Build login"
AI:  ❌ BLOCKED - No PRD found. Write a spec first.

You: *writes PRD with requirements*
AI:  ✅ PASS - Ready to code.
```

### 2. Feedback — 8 managers review in 30 seconds
```
👔 PM:  "User story covers happy path, but what about failed attempts?"
🛠️ CTO: "Consider rate limiting for brute force protection."
🔒 CSO: "⚠️ Password hashing not implemented."
```

### 3. Memory — Never forget what you decided
```
You: "Why did we use JWT instead of sessions?"
AI:  Found decision #42: "JWT chosen for stateless scaling" (2024-01-15)
```

**Gate + Feedback + Memory = Solo dev with team discipline.**

---

## FREE vs PRO

| | FREE | PRO ($7.99/mo) |
|---|---|---|
| **Projects** | 3 | Unlimited |
| **Templates** | `lite` (~150 lines) | All (`lite` + `standard` + `detailed`) |
| **Managers** | 1 (PM only) | 8 (PM, CTO, QA, CDO, CMO, CFO, CSO, Error) |
| **can_code** | WARN (doesn't block) | BLOCK (enforces PRD) |
| **Knowledge Base** | - | Remembers all decisions |
| **Error Learning** | - | Learns from your mistakes |

**[Get Pro →](https://polar.sh/clouvel)** Use code `FIRST1` for first month $1

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

## Key Tools

| Tool | What it does | FREE | PRO |
|------|--------------|------|-----|
| `can_code` | Checks if you can start coding | WARN | BLOCK |
| `start` | Project onboarding + PRD templates | `lite` | All templates |
| `manager` | C-Level review meeting | PM only | 8 managers |
| `meeting` | Natural meeting transcript | 1 manager | All managers |
| `plan` | Detailed execution planning | ✓ | ✓ |
| `ship` | lint → test → build pipeline | - | ✓ |
| `record_decision` | Save decisions to Knowledge Base | - | ✓ |
| `error_learn` | Learn from mistakes | - | ✓ |

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

**Manual - Windows:**
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

**Manual - Mac/Linux:**
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

### v1.9 Consolidated Tools

```bash
# Before: Multiple tools
get_prd_template(template="web-app")
get_prd_guide()
init_docs()

# After: Single tool with options
start --template=web-app    # Get template
start --guide               # Get PRD writing guide
start --init                # Initialize docs folder

# Before: Separate hook tools
init_rules(template="web")
hook_design(trigger="pre_code")
hook_verify(trigger="post_code")

# After: Single tool with options
setup_cli --rules=web              # Initialize rules
setup_cli --hook=design            # Create design hook
setup_cli --hook=verify            # Create verify hook
```

---

## Documentation

- [Full Documentation](https://whitening-sinabro.github.io/clouvel/)
- [PRD Templates](https://whitening-sinabro.github.io/clouvel/templates)
- [FAQ](https://whitening-sinabro.github.io/clouvel/faq)

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

- [Report bugs](https://github.com/Whitening-Sinabro/clouvel/issues)
- [Request features](https://github.com/Whitening-Sinabro/clouvel/issues)
- [Join discussions](https://github.com/Whitening-Sinabro/clouvel/discussions)

---

## Deprecation Notice (v1.9)

The following tools show deprecation warnings and will be removed in v2.0:

| Deprecated | Use Instead |
|------------|-------------|
| `scan_docs` | `can_code` |
| `analyze_docs` | `can_code` |
| `verify` | `ship` |
| `gate` | `ship` |
| `get_prd_template` | `start --template` |
| `get_prd_guide` | `start --guide` |
| `init_docs` | `start --init` |
| `init_rules` | `setup_cli --rules` |
| `hook_design` | `setup_cli --hook=design` |
| `hook_verify` | `setup_cli --hook=verify` |
| `handoff` | `record_decision` + `update_progress` |

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>Solo coding, team-level thinking. That's Clouvel.</b><br>
  <a href="https://whitening-sinabro.github.io/clouvel/">Website</a> •
  <a href="https://github.com/Whitening-Sinabro/clouvel/issues">Issues</a> •
  <a href="https://polar.sh/clouvel">Get Pro</a>
</p>
