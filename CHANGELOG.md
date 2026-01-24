# Changelog

All notable changes to Clouvel will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
