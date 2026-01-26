# Changelog

All notable changes to Clouvel will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.0] - 2026-01-26

### Added
- **Tool Consolidation**: 52 MCP tools analyzed and standardized into 9 groups
  - `start` now supports `--template`, `--layout`, `--guide`, `--init` options
  - `setup_cli` now supports `--rules`, `--hook`, `--hook_trigger` options
- **Deprecation Warnings**: 11 tools show deprecation notice (removed in v2.0)
  - `scan_docs`, `analyze_docs` → use `can_code`
  - `verify`, `gate` → use `ship`
  - `get_prd_template`, `get_prd_guide`, `init_docs` → use `start` with options
  - `init_rules`, `hook_design`, `hook_verify` → use `setup_cli` with options
  - `handoff` → use `record_decision` + `update_progress`
- **Developer Mode Fix**: Trial bypass for developers (no more `trial_exhausted` in dev)

### Changed
- **Architecture**: MCP tools consolidated from 52 to 12 standard + 18 keep + 6 merge + 5 deprecate
- **Documentation**: MCP_CATALOG.md, MCP_GROUPS.md, MCP_STANDARDIZATION_PLAN.md

### Philosophy
- **"One tool, one purpose"** - Consolidate similar tools with options instead of separate commands

---

## [1.8.0] - 2026-01-26

### Changed
- **Manager Architecture**: Moved from local execution to Worker API
  - `_wrap_manager()` now calls `call_manager_api()` instead of local module
  - `_wrap_quick_perspectives()` also uses Worker API
  - Local `tools/manager/` only used in developer mode
- **Architecture Documentation**: Added SSOT documentation system
  - `ENTRYPOINTS.md` - Entry points (CLI, MCP, Packaging)
  - `SIDE_EFFECTS.md` - Side effects matrix
  - `SMOKE_LOGS.md` - Execution verification records
  - `CALL_FLOWS/` - Call flow diagrams
  - `DECISION_LOG/` - Architecture Decision Records

### Added
- **Architecture Guard**: Tools for architecture validation
  - `arch_check` - Check existing code before adding new functions
  - `check_imports` - Validate import patterns
  - `check_duplicates` - Detect duplicate function definitions

---

## [1.6.0] - 2026-01-25

### Added
- **API-based Pro Features**: Pro features now served via Cloudflare Workers API
  - `manager`: 8 C-Level manager feedback via API
  - `ship`: Trial/license validation via API, execution local
  - Secure - Pro code never distributed in PyPI package
  - Reliable - Trial tracking on server, not local file

- **Trial System**: Pro features free trial (server-managed)
  - `manager`: 10 free uses
  - `ship`: 5 free uses
  - Trial usage tracked per client via API
  - Exhaustion message with upgrade link

- **Start Tool Trial Info**: `start` now shows Trial availability
  - Shows remaining trial uses for Pro features
  - Quick start guide: "Try now: `manager(context=..., topic=...)`"

### Changed
- **Architecture**: Pro features moved from local to API
  - PyPI package only contains API client
  - Pro logic runs on Cloudflare Workers
  - Offline fallback with basic responses

### Philosophy
- **"맛보기가 전환을 만든다"** (Trial drives conversion) - Let users experience Pro before purchase
- **"Pro 코드는 서버에"** (Pro code stays on server) - Better security and control

## [1.5.0] - 2026-01-25

### Added
- **Record Tracking**: New file tracking tools for session continuity
  - `record_file` - Record file creations to `.claude/files/created.md`
  - `list_files` - List all recorded files with purpose and status
  - Prevents "forgotten files" issue across sessions
- **Pre-commit Hook Enhancement**: Stronger enforcement
  - `clouvel setup --hooks` command for hook installation
  - Blocks commit if `.claude/files/created.md` missing
  - Blocks commit if `.claude/status/current.md` missing
- **Manager Topic Expansion**: Better context understanding
  - New topics: `mcp`, `internal`, `tracking`, `maintenance`
  - Pattern-based detection for problems and requests

### Changed
- **can_code DoD Check**: Now detects more DoD patterns
  - Added: `## DoD`, `## Definition of Done`, `## Criteria`, `## 완료 정의`
  - Test message improved: warns when no tests exist
- **Manager LLM Optimization**: Improved output for Claude's attention patterns
  - XML structure with `<critical_summary>`, `<situation_analysis>`, `<meeting_notes>`
  - Bookending technique: critical issues at beginning AND end
  - U-shaped attention curve optimization (primacy + recency bias)
- **Context Analysis**: Enhanced pattern detection
  - Problem patterns: "없다", "안 됨", "느려", "취약" → error/performance/security
  - Request patterns: "추가", "구현", "수정" → feature/maintenance

### Philosophy
- **"기록을 잃지 않는다"** (Don't lose records) - Now enforced, not just documented

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
