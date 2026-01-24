# Changelog

All notable changes to Clouvel will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-01-24

### Changed
- **Manager v2: Augmentation Model** - Complete redesign from "answer-giving" to "question-asking"
  - 8 managers now ask probing questions instead of giving recommendations
  - New output format: "Decisions for YOU" and "Key Questions to Answer"
  - Philosophy: Help solo devs THINK from 8 perspectives, not think FOR them
  - Each manager has 4 categories of probing questions (scope, tradeoffs, risks, etc.)
  - Knowledge Base integration: managers now reference past decisions
  - Automatic context injection from project history

### Added
- **Knowledge Base**: SQLite-based persistent storage for decisions, meetings, and code locations
  - `record_decision` - Save architectural decisions with reasoning
  - `record_location` - Track important code locations
  - `search_knowledge` - FTS5 full-text search across all knowledge
  - `get_context` - Session recovery with recent decisions and locations
  - `init_knowledge` - Initialize/reset the knowledge database
  - `rebuild_index` - Rebuild FTS5 search index
- **Session Auto-load**: `can_code` now shows recent context from Knowledge Base
- **50MB Limit + Auto-archive**: Automatic archival of 30+ day old data when DB exceeds 40MB
- **API Key Fallback**: Manager works in static mode without ANTHROPIC_API_KEY
- **Meeting Auto-record**: Manager calls automatically record decisions to Knowledge Base
- **SQLite Encryption**: Optional field-level encryption via `CLOUVEL_KB_KEY` environment variable
- **Quick Perspectives**: Lightweight pre-coding check (`quick_perspectives`)
  - 3-4 relevant managers provide key probing questions
  - Topic-based manager selection (auth → CSO, UI → CDO)
  - References past decisions from Knowledge Base

### Changed
- Landing page: "Context Recovery" → "Progress Tracking" (honest messaging)

### Security
- Optional encryption for sensitive decision data using Fernet (cryptography library)

## [1.3.13] - 2026-01-24

### Fixed
- Conditional import for manager module (Free version compatibility)

## [1.3.12] - 2026-01-24

### Fixed
- Windows cp949 encoding issue resolved
- Platform-specific Python command (`py` for Windows, `python3` for Mac/Linux)

## [1.3.11] - 2026-01-23

### Added
- Dynamic meeting generation with Claude API integration in manager tool

## [1.3.10] - 2026-01-23

### Changed
- License system migrated to Polar.sh
- 6 subscription products (Personal/Team5/Team10 × Monthly/Yearly)

## [1.3.9] - 2026-01-23

### Added
- S3-based Pro module auto-download infrastructure
- Improved activate command with auto Pro installation
- Network retry with exponential backoff

## [1.3.8] - 2026-01-23

### Added
- Manager relevance score filtering (prevents off-topic questions)
- Critical checks per manager (missing items, security issues)
- Approval status display (BLOCKED / NEEDS_REVISION / APPROVED)

## [1.3.7] - 2026-01-22

### Added
- Google Antigravity integration guide

### Fixed
- Pro tool stability improvements

## [1.3.6] - 2026-01-22

### Added
- FAQ documentation page

### Fixed
- Gitignore cleanup
- Tool stability improvements

## [1.3.5] - 2026-01-22

### Fixed
- PyPI deployment: added license_free.py stub

## [1.3.4] - 2026-01-22

### Added
- 8 project templates: web-app, api, cli, chrome-ext, discord-bot, landing-page, saas, generic
- Project type auto-detection in `start` command
- Interactive PRD guide with conversation-based Q&A
- `save_prd` tool for saving PRD from conversation
- Version check with PyPI (24-hour cache)

## [1.3.0] - 2026-01-21

### Added
- Manager tool with 8 C-Level personas
- Ship tool (lint → test → build automation)
- `clouvel install` command

## [1.2.0] - 2026-01-20

### Added
- Planning tools (`init_planning`, `save_finding`, `refresh_goals`, `update_progress`)
- Agent tools (`spawn_explore`, `spawn_librarian`)
- Hook tools (`hook_design`, `hook_verify`)

## [1.1.0] - 2026-01-19

### Added
- Rules system (`init_rules`, `get_rule`, `add_rule`)
- Verification tools (`verify`, `gate`, `handoff`)

## [1.0.0] - 2026-01-18

### Added
- Initial release
- Core tools: `can_code`, `scan_docs`, `analyze_docs`, `init_docs`
- Documentation tools: `get_prd_template`, `write_prd_section`, `get_prd_guide`
- Setup tools: `init_clouvel`, `setup_cli`
