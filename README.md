# Clouvel

> **No spec, no code.** PRD-First gate for AI coding.

[![PyPI](https://img.shields.io/pypi/v/clouvel)](https://pypi.org/project/clouvel/)
[![Python](https://img.shields.io/pypi/pyversions/clouvel)](https://pypi.org/project/clouvel/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

![Demo](docs/assets/demo.gif)

---

## The Problem

You ask AI to "build login" and it:
- Skips password reset
- Forgets social auth
- Ignores error handling
- Builds something different every time

**Result**: Hours of debugging "almost right" code.

## The Solution

Clouvel blocks AI coding until you write a spec (PRD).

```
You: "Build login"
AI:  ❌ BLOCKED - No PRD found. Write a spec first.

You: *writes PRD with requirements*
AI:  ✅ PASS - PRD found. Coding allowed.
```

**Same input → Same output. Every time.**

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

## How It Works

1. **You ask AI to code something**
2. **Clouvel checks for PRD** (Product Requirements Document)
3. **No PRD? Blocked.** Write the spec first.
4. **PRD exists? Allowed.** AI codes with clear requirements.

### Before & After

| Without Clouvel | With Clouvel |
|-----------------|--------------|
| "Build login" → AI guesses | "Build login" → AI reads PRD |
| Missing features | All requirements included |
| Different results each time | Consistent output |
| Debug for hours | Works as specified |

---

## Features

### Free (Open Source)

| Feature | Description |
|---------|-------------|
| `can_code` | PRD gate - blocks coding without specs |
| `start` | Project onboarding with PRD templates |
| `plan` | Detailed execution planning |
| `save_prd` | Save PRD from conversation |
| Progress tracking | Track what's done and what's next |
| 8 project templates | web-app, api, cli, chrome-ext, discord-bot, landing-page, saas, generic |

### Pro ($9.99/mo)

| Feature | Description |
|---------|-------------|
| `manager` | 8 C-Level managers review your code (PM, CTO, QA, CDO, CMO, CFO, CSO, Error) |
| `ship` | One-click test → verify → evidence generation |
| Error Learning | Learn from mistakes, auto-generate NEVER/ALWAYS rules |
| Dynamic meetings | AI-powered team discussions with Claude API |

**[Get Pro →](https://polar.sh/clouvel)**

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

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>Stop debugging AI code. Start with a spec.</b><br>
  <a href="https://whitening-sinabro.github.io/clouvel/">Website</a> •
  <a href="https://github.com/Whitening-Sinabro/clouvel/issues">Issues</a> •
  <a href="https://polar.sh/clouvel">Get Pro</a>
</p>
