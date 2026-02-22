# -*- coding: utf-8 -*-
"""
Clouvel Tool Schema Definitions

All MCP Tool() objects defining the tool interface.
Extracted from server.py for maintainability.
"""

from mcp.types import Tool

TOOL_DEFINITIONS = [
    # === Core Tools ===
    Tool(
        name="can_code",
        description="Check before writing code. Verifies project docs exist so you don't start coding without a plan.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project docs folder path"},
                "mode": {"type": "string", "enum": ["pre", "post"], "description": "pre (default): check before coding, post: verify file tracking after coding"}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="scan_docs",
        description="Scan project docs folder. Returns file list.",
        inputSchema={
            "type": "object",
            "properties": {"path": {"type": "string", "description": "docs folder path"}},
            "required": ["path"]
        }
    ),
    Tool(
        name="analyze_docs",
        description="Analyze docs folder. Check required documents.",
        inputSchema={
            "type": "object",
            "properties": {"path": {"type": "string", "description": "docs folder path"}},
            "required": ["path"]
        }
    ),
    Tool(
        name="init_docs",
        description="Initialize docs folder + generate templates.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "project_name": {"type": "string", "description": "Project name"}
            },
            "required": ["path", "project_name"]
        }
    ),

    # === Docs Tools ===
    Tool(
        name="get_prd_template",
        description="Generate PRD template. Choose template and layout.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Project name"},
                "output_path": {"type": "string", "description": "Output path"},
                "template": {"type": "string", "enum": ["web-app", "api", "cli", "generic"], "description": "Template type"},
                "layout": {"type": "string", "enum": ["lite", "standard", "detailed"], "description": "Layout (content amount)"}
            },
            "required": ["project_name", "output_path"]
        }
    ),
    Tool(
        name="list_templates",
        description="List available PRD templates.",
        inputSchema={"type": "object", "properties": {}}
    ),
    Tool(
        name="write_prd_section",
        description="PRD section writing guide.",
        inputSchema={
            "type": "object",
            "properties": {
                "section": {"type": "string", "enum": ["summary", "principles", "input_spec", "output_spec", "errors", "state_machine", "api_endpoints", "db_schema"]},
                "content": {"type": "string", "description": "Section content"}
            },
            "required": ["section"]
        }
    ),
    Tool(name="get_prd_guide", description="PRD writing guide.", inputSchema={"type": "object", "properties": {}}),
    Tool(name="get_verify_checklist", description="Verification checklist.", inputSchema={"type": "object", "properties": {}}),
    Tool(
        name="get_setup_guide",
        description="Installation/setup guide.",
        inputSchema={
            "type": "object",
            "properties": {"platform": {"type": "string", "enum": ["desktop", "code", "vscode", "cursor", "all"]}}
        }
    ),
    Tool(
        name="get_analytics",
        description="Tool usage statistics.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project path"},
                "days": {"type": "integer", "description": "Query period (default: 30 days)"}
            }
        }
    ),
    Tool(
        name="get_ab_report",
        description="A/B testing analytics report. Shows experiment results, conversion rates, and recommendations. (v3.3)",
        inputSchema={
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "Analysis period in days (default: 7)"},
                "experiment": {"type": "string", "description": "Specific experiment name (optional, shows all if not specified)"}
            }
        }
    ),
    Tool(
        name="get_monthly_report",
        description="Monthly KPI dashboard with conversion funnel, pain point effectiveness, and recommendations. (v3.3 Week 4)",
        inputSchema={
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "Analysis period in days (default: 30)"}
            }
        }
    ),
    Tool(
        name="decide_winner",
        description="Analyze A/B test and decide if a winner can be promoted to 100% rollout. (v3.3 Week 4)",
        inputSchema={
            "type": "object",
            "properties": {
                "experiment": {"type": "string", "description": "Experiment name to analyze"},
                "min_confidence": {"type": "string", "enum": ["low", "medium", "high"], "description": "Minimum confidence level required (default: medium)"}
            },
            "required": ["experiment"]
        }
    ),

    # === Setup Tools ===
    Tool(
        name="init_clouvel",
        description="Clouvel onboarding. Custom setup after platform selection.",
        inputSchema={
            "type": "object",
            "properties": {"platform": {"type": "string", "enum": ["desktop", "vscode", "cli", "ask"]}}
        }
    ),
    Tool(
        name="setup_cli",
        description="CLI environment setup. Generate hooks, CLAUDE.md, pre-commit. Now includes: --rules, --hook, --proactive options. (v2.0 extended)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "level": {"type": "string", "enum": ["remind", "strict", "full"]},
                "rules": {"type": "string", "description": "Initialize rules (replaces init_rules)", "enum": ["web", "api", "fullstack", "minimal"]},
                "hook": {"type": "string", "description": "Create hook (replaces hook_design, hook_verify)", "enum": ["design", "verify"]},
                "hook_trigger": {"type": "string", "description": "Trigger for hook", "enum": ["pre_code", "pre_feature", "pre_refactor", "pre_api", "post_code", "post_feature", "pre_commit", "pre_push"]},
                "proactive": {"type": "string", "description": "Setup proactive hooks (v2.0) - auto PRD check, drift detection", "enum": ["free", "pro"]}
            },
            "required": ["path"]
        }
    ),

    # === Rules Tools (v0.5) ===
    Tool(
        name="init_rules",
        description="v0.5: Initialize rules modularization.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "template": {"type": "string", "enum": ["web", "api", "fullstack", "minimal"]}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="get_rule",
        description="v0.5: Load rules based on path.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "context": {"type": "string", "enum": ["coding", "review", "debug", "test"]}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="add_rule",
        description="v0.5: Add new rule.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "rule_type": {"type": "string", "enum": ["never", "always", "prefer"]},
                "content": {"type": "string", "description": "Rule content"},
                "category": {"type": "string", "enum": ["api", "frontend", "database", "security", "general"]}
            },
            "required": ["path", "rule_type", "content"]
        }
    ),

    # === Verify Tools (v0.5) ===
    Tool(
        name="verify",
        description="v0.5: Context Bias removal verification.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Verification target path"},
                "scope": {"type": "string", "enum": ["file", "feature", "full"]},
                "checklist": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="gate",
        description="Run lint, test, and build in sequence. Catches broken code before you commit.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "steps": {"type": "array", "items": {"type": "string"}},
                "fix": {"type": "boolean"}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="handoff",
        description="v0.5: Record intent.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "feature": {"type": "string", "description": "Completed feature"},
                "decisions": {"type": "string"},
                "warnings": {"type": "string"},
                "next_steps": {"type": "string"}
            },
            "required": ["path", "feature"]
        }
    ),

    # === Planning Tools (v0.6, v1.3) ===
    Tool(
        name="init_planning",
        description="v0.6: Initialize persistent context.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "task": {"type": "string", "description": "Current task"},
                "goals": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["path", "task"]
        }
    ),
    Tool(
        name="plan",
        description="Generate a detailed execution plan with action items, dependencies, and verification points.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "task": {"type": "string", "description": "Task to perform"},
                "goals": {"type": "array", "items": {"type": "string"}, "description": "Goals to achieve"},
                "meeting_file": {"type": "string", "description": "Previous meeting file name (e.g., 2026-01-24_14-00_feature.md). If provided, generates plan based on meeting results"}
            },
            "required": ["path", "task"]
        }
    ),
    Tool(
        name="save_finding",
        description="v0.6: Save research findings.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "topic": {"type": "string"},
                "question": {"type": "string"},
                "findings": {"type": "string"},
                "source": {"type": "string"},
                "conclusion": {"type": "string"}
            },
            "required": ["path", "topic", "findings"]
        }
    ),
    Tool(
        name="refresh_goals",
        description="v0.6: Goals reminder.",
        inputSchema={
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Project root path"}},
            "required": ["path"]
        }
    ),
    Tool(
        name="update_progress",
        description="v0.6: Update progress status.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "completed": {"type": "array", "items": {"type": "string"}},
                "in_progress": {"type": "string"},
                "blockers": {"type": "array", "items": {"type": "string"}},
                "next": {"type": "string"}
            },
            "required": ["path"]
        }
    ),

    # === Context Checkpoint (Free) ===
    Tool(
        name="context_save",
        description="Save your working state before context runs out. One call captures everything needed for recovery.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "reason": {"type": "string", "description": "Why saving (e.g., 'before refactor')"},
                "notes": {"type": "string", "description": "Important context to preserve"},
                "active_files": {"type": "array", "items": {"type": "string"}, "description": "Files currently being worked on"},
                "decisions_this_session": {"type": "array", "items": {"type": "string"}, "description": "Decisions made this session"},
                "depth": {"type": "string", "enum": ["quick", "full"], "description": "quick: current.md + git only, full: everything (default)"},
                "task": {"type": "string", "description": "Current task description (initializes planning context)"},
                "goals": {"type": "array", "items": {"type": "string"}, "description": "Session goals to track"},
                "findings": {"type": "string", "description": "Research findings to preserve"},
                "handoff": {"type": "string", "description": "Handoff notes for next session (what was done, what's next)"},
            },
            "required": ["path"],
        },
    ),
    Tool(
        name="context_load",
        description="Restore your working state after context compression or a new session.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "checkpoint": {"type": "string", "description": "\"latest\" (default) or specific filename"},
                "show_goals": {"type": "boolean", "description": "Include saved goals in the loaded context (default: true)"},
            },
            "required": ["path"],
        },
    ),

    # === Agent Tools (v0.7) ===
    Tool(
        name="spawn_explore",
        description="v0.7: Exploration specialist agent.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "query": {"type": "string", "description": "Exploration question"},
                "scope": {"type": "string", "enum": ["file", "folder", "project", "deep"]},
                "save_findings": {"type": "boolean"}
            },
            "required": ["path", "query"]
        }
    ),
    Tool(
        name="spawn_librarian",
        description="v0.7: Librarian agent.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "topic": {"type": "string", "description": "Research topic"},
                "type": {"type": "string", "enum": ["library", "api", "migration", "best_practice"]},
                "depth": {"type": "string", "enum": ["quick", "standard", "thorough"]}
            },
            "required": ["path", "topic"]
        }
    ),

    # === Hook Tools (v0.8) ===
    Tool(
        name="hook_design",
        description="v0.8: Create design hook.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "trigger": {"type": "string", "enum": ["pre_code", "pre_feature", "pre_refactor", "pre_api"]},
                "checks": {"type": "array", "items": {"type": "string"}},
                "block_on_fail": {"type": "boolean"}
            },
            "required": ["path", "trigger"]
        }
    ),
    Tool(
        name="hook_verify",
        description="v0.8: Create verification hook.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "trigger": {"type": "string", "enum": ["post_code", "post_feature", "pre_commit", "pre_push"]},
                "steps": {"type": "array", "items": {"type": "string"}},
                "parallel": {"type": "boolean"},
                "continue_on_error": {"type": "boolean"}
            },
            "required": ["path", "trigger"]
        }
    ),

    # === Start Tool (Free, v1.2 → v1.9 extended) ===
    Tool(
        name="start",
        description="Set up a new project. Auto-detects project type, checks for PRD, and guides you through onboarding.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "project_name": {"type": "string", "description": "Project name (optional)"},
                "project_type": {"type": "string", "description": "Force project type (optional)", "enum": ["web-app", "api", "cli", "chrome-ext", "discord-bot", "landing-page", "generic"]},
                "template": {"type": "string", "description": "Get PRD template (replaces get_prd_template)", "enum": ["web-app", "api", "cli", "chrome-ext", "discord-bot", "landing-page", "saas", "generic"]},
                "layout": {"type": "string", "description": "Template layout", "enum": ["lite", "standard", "detailed"], "default": "standard"},
                "guide": {"type": "boolean", "description": "Show PRD writing guide (replaces get_prd_guide)", "default": False},
                "init": {"type": "boolean", "description": "Initialize docs folder with templates", "default": False},
                "rules": {"type": "string", "description": "Initialize coding rules template (web, api, fullstack, minimal)", "enum": ["web", "api", "fullstack", "minimal"]},
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="save_prd",
        description="Save your PRD to the project docs folder. Write requirements through conversation, then persist them.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "content": {"type": "string", "description": "PRD content (markdown)"},
                "project_name": {"type": "string", "description": "Project name (optional)"},
                "project_type": {"type": "string", "description": "Project type (optional)"}
            },
            "required": ["path", "content"]
        }
    ),

    # === Project Management Tools (Free, v3.3) ===
    Tool(
        name="archive_project",
        description="Archive a project to free up the active slot. Free tier allows 1 active project. (Free)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project path to archive"}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="list_projects",
        description="List all registered projects with their status (active/archived). (Free)",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),

    # === Knowledge Base Tools (Pro, v1.4) ===
    Tool(
        name="record_decision",
        description="Save an architectural or design decision. Persists across sessions so context is never lost.",
        inputSchema={
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Decision category (architecture, pricing, security, feature, etc.)"},
                "decision": {"type": "string", "description": "The actual decision made"},
                "reasoning": {"type": "string", "description": "Why this decision was made"},
                "alternatives": {"type": "array", "items": {"type": "string"}, "description": "Other options that were considered"},
                "project_name": {"type": "string", "description": "Project name (optional)"},
                "project_path": {"type": "string", "description": "Project path (optional)"},
                "locked": {"type": "boolean", "description": "If true, decision is LOCKED and should not be changed without explicit unlock"}
            },
            "required": ["category", "decision"]
        }
    ),
    Tool(
        name="record_location",
        description="Record a code location to the knowledge base. Track where important code lives. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Descriptive name (e.g., 'License validation endpoint')"},
                "repo": {"type": "string", "description": "Repository name (e.g., 'clouvel-workers')"},
                "path": {"type": "string", "description": "File path within repo (e.g., 'src/index.js:42')"},
                "description": {"type": "string", "description": "What this code does"},
                "project_name": {"type": "string", "description": "Project name (optional)"},
                "project_path": {"type": "string", "description": "Project path (optional)"}
            },
            "required": ["name", "repo", "path"]
        }
    ),
    Tool(
        name="search_knowledge",
        description="Search past decisions, code locations, and context from your knowledge base.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (FTS5 syntax supported)"},
                "project_name": {"type": "string", "description": "Filter by project (optional)"},
                "project_path": {"type": "string", "description": "Project path (for dev mode auto-detection)"},
                "limit": {"type": "integer", "description": "Max results (default 20)"}
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="get_context",
        description="Get recent context for a project. Returns recent decisions and code locations. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Project name"},
                "project_path": {"type": "string", "description": "Project path"},
                "include_decisions": {"type": "boolean", "description": "Include recent decisions (default true)"},
                "include_locations": {"type": "boolean", "description": "Include code locations (default true)"},
                "limit": {"type": "integer", "description": "Max items per category (default 10)"}
            }
        }
    ),
    Tool(
        name="init_knowledge",
        description="Initialize the knowledge base. Creates SQLite database at ~/.clouvel/knowledge.db. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Project path (for dev mode auto-detection)"}
            }
        }
    ),
    Tool(
        name="rebuild_index",
        description="Rebuild the knowledge base search index. Use if search results seem incomplete. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Project path (for dev mode auto-detection)"}
            }
        }
    ),
    Tool(
        name="unlock_decision",
        description="Unlock a locked decision. Requires explicit reason. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "decision_id": {"type": "integer", "description": "The ID of the decision to unlock"},
                "reason": {"type": "string", "description": "Why this decision is being unlocked (required for audit)"},
                "project_path": {"type": "string", "description": "Project path (for dev mode auto-detection)"}
            },
            "required": ["decision_id", "reason"]
        }
    ),
    Tool(
        name="list_locked_decisions",
        description="List all locked decisions. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Filter by project name (optional)"},
                "project_path": {"type": "string", "description": "Filter by project path (optional)"}
            }
        }
    ),

    # === Tracking Tools (v1.5) ===
    Tool(
        name="record_file",
        description="Record a file creation to .claude/files/created.md. Use this when creating important files that should not be deleted.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "file_path": {"type": "string", "description": "Relative path of the created file"},
                "purpose": {"type": "string", "description": "What this file does"},
                "deletable": {"type": "boolean", "description": "Whether this file can be deleted (default: false)"},
                "session": {"type": "string", "description": "Session name for grouping (optional)"}
            },
            "required": ["path", "file_path", "purpose"]
        }
    ),
    Tool(
        name="list_files",
        description="List all recorded files from .claude/files/created.md.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"}
            },
            "required": ["path"]
        }
    ),

    # === Manager Tool (Pro, v1.2) ===
    Tool(
        name="manager",
        description="Context-based collaborative feedback from 8 C-Level managers. PM/CTO/QA/CDO/CMO/CFO/CSO/Error. Set use_dynamic=true for natural meeting transcript generation. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "context": {"type": "string", "description": "Content to review (plan, code, questions, etc.)"},
                "mode": {"type": "string", "enum": ["auto", "all", "specific"], "description": "Manager selection mode"},
                "managers": {"type": "array", "items": {"type": "string"}, "description": "Manager list when mode=specific"},
                "include_checklist": {"type": "boolean", "description": "Include checklist"},
                "use_dynamic": {"type": "boolean", "description": "If true, generate natural meeting transcript via Claude API (ANTHROPIC_API_KEY required)"},
                "topic": {"type": "string", "enum": ["auth", "api", "payment", "ui", "feature", "launch", "error", "security", "performance", "maintenance", "design"], "description": "Meeting topic hint (when use_dynamic=true)"}
            },
            "required": ["context"]
        }
    ),
    Tool(
        name="list_managers",
        description="List available managers. (Pro)",
        inputSchema={"type": "object", "properties": {}}
    ),
    Tool(
        name="quick_perspectives",
        description="Get 3-4 critical questions before coding. Surfaces blind spots you might miss.",
        inputSchema={
            "type": "object",
            "properties": {
                "context": {"type": "string", "description": "What you're about to build/do"},
                "max_managers": {"type": "integer", "description": "Max managers to include (default 4)"},
                "questions_per_manager": {"type": "integer", "description": "Questions per manager (default 2)"}
            },
            "required": ["context"]
        }
    ),

    # === Ship Tool (Pro, v1.2) ===
    Tool(
        name="ship",
        description="One-click ship: lint, typecheck, test, build in sequence. Generates verification evidence.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "feature": {"type": "string", "description": "Feature name to verify (optional)"},
                "steps": {"type": "array", "items": {"type": "string"}, "description": "Steps to execute ['lint', 'typecheck', 'test', 'build']"},
                "generate_evidence": {"type": "boolean", "description": "Generate evidence file"},
                "auto_fix": {"type": "boolean", "description": "Attempt auto-fix for lint errors"}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="quick_ship",
        description="Quick ship - run lint and test only. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "feature": {"type": "string", "description": "Feature name to verify (optional)"}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="full_ship",
        description="Full ship - all verification steps + auto fix. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "feature": {"type": "string", "description": "Feature name to verify (optional)"}
            },
            "required": ["path"]
        }
    ),

    # === Error Learning Tools (Pro, v1.4) ===
    Tool(
        name="error_record",
        description="Record an error with 5 Whys root cause analysis. Builds your project's error memory.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "error_text": {"type": "string", "description": "Error message"},
                "context": {"type": "string", "description": "Error context description"},
                "five_whys": {"type": "array", "items": {"type": "string"}, "description": "5 Whys analysis results"},
                "root_cause": {"type": "string", "description": "Root cause"},
                "solution": {"type": "string", "description": "Solution"},
                "prevention": {"type": "string", "description": "Prevention measures"}
            },
            "required": ["path", "error_text"]
        }
    ),
    Tool(
        name="error_check",
        description="Check for known error patterns before modifying code. Warns you before repeating past mistakes.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "context": {"type": "string", "description": "Current work context"},
                "file_path": {"type": "string", "description": "File path to modify"},
                "operation": {"type": "string", "description": "Operation to perform"}
            },
            "required": ["path", "context"]
        }
    ),
    Tool(
        name="error_learn",
        description="Analyze error patterns and auto-generate NEVER/ALWAYS rules for CLAUDE.md.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "auto_update_claude_md": {"type": "boolean", "description": "Auto update CLAUDE.md"},
                "min_count": {"type": "integer", "description": "Minimum error count for NEVER rule generation"}
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="memory_status",
        description="See your error memory dashboard: active patterns, hit counts, and time saved.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="memory_list",
        description="List regression memories. Filter by category, show archived. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "category": {"type": "string", "description": "Filter by error category (optional)"},
                "include_archived": {"type": "boolean", "description": "Include archived memories (default false)"},
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="memory_search",
        description="Search your error memories by keyword. Find past root causes and prevention rules.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "query": {"type": "string", "description": "Search keyword"},
                "category": {"type": "string", "description": "Filter by category (optional)"},
            },
            "required": ["path", "query"]
        }
    ),
    Tool(
        name="memory_archive",
        description="Archive or unarchive a regression memory. Archived memories are excluded from matching. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "memory_id": {"type": "integer", "description": "Memory ID to archive/unarchive"},
                "action": {"type": "string", "enum": ["archive", "unarchive"], "description": "Action (default: archive)"},
            },
            "required": ["path", "memory_id"]
        }
    ),
    Tool(
        name="memory_report",
        description="Monthly regression memory report. Shows savings, prevention count, top patterns, and time saved estimate. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "days": {"type": "integer", "description": "Report period in days (default 30)"},
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="memory_promote",
        description="Promote a local regression memory to global. Shared across all projects. Only root_cause and prevention_rule are promoted (no raw error text). Requires hit_count >= 1. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "memory_id": {"type": "integer", "description": "Local memory ID to promote"},
            },
            "required": ["path", "memory_id"]
        }
    ),
    Tool(
        name="memory_global_search",
        description="Search error patterns across all your projects. Reuse lessons learned everywhere.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "query": {"type": "string", "description": "Search keyword"},
                "category": {"type": "string", "description": "Filter by error category (optional)"},
                "domain": {"type": "string", "description": "Filter by domain (personal/work/client). Auto-detected if not specified.", "enum": ["personal", "work", "client"]},
            },
            "required": ["path", "query"]
        }
    ),

    Tool(
        name="set_project_domain",
        description="Set the domain for the current project. Domains isolate memories: personal/work/client. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Project root path"},
                "domain": {"type": "string", "description": "Domain scope", "enum": ["personal", "work", "client"]},
            },
            "required": ["path", "domain"]
        }
    ),

    # === License Tools ===
    Tool(
        name="activate_license",
        description="Activate license. Supports Polar.sh or test license.",
        inputSchema={
            "type": "object",
            "properties": {
                "license_key": {"type": "string", "description": "License key"}
            },
            "required": ["license_key"]
        }
    ),
    Tool(
        name="license_status",
        description="Check your Clouvel license, trial status, and available features.",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["status", "activate", "trial", "upgrade"],
                    "description": "Action: status (default), activate (with license_key), trial (start 7-day), upgrade (show Pro guide)",
                },
                "license_key": {
                    "type": "string",
                    "description": "License key (required when action=activate)",
                },
            },
        },
    ),
    Tool(
        name="start_trial",
        description="Start 7-day Full Pro trial. No credit card required. All Pro features unlocked for 7 days.",
        inputSchema={"type": "object", "properties": {}}
    ),

    # === Pro Guide ===
    Tool(
        name="upgrade_pro",
        description="Clouvel Pro guide. Shovel auto-install, Error Learning, etc.",
        inputSchema={"type": "object", "properties": {}}
    ),

    # === Architecture Guard (v1.8) ===
    Tool(
        name="arch_check",
        description="Check existing code before adding new function/module. Prevents duplicate definitions.",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"description": "Function/class name to add", "type": "string"},
                "purpose": {"description": "Purpose description", "type": "string"},
                "path": {"description": "Project root path", "type": "string"},
            },
            "required": ["name", "purpose"]
        }
    ),
    Tool(
        name="check_imports",
        description="Validate server.py import patterns. Detects architecture rule violations.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"description": "Project root path", "type": "string"},
            },
        }
    ),
    Tool(
        name="check_duplicates",
        description="Detect duplicate function definitions across __init__.py files.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"description": "Project root path", "type": "string"},
            },
        }
    ),
    # v3.1: Sideeffect sync checker
    Tool(
        name="check_sync",
        description="v3.1: Verify sync between file pairs (license.py ↔ license_free.py, messages/en.py ↔ ko.py). Detects missing functions and signature mismatches.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"description": "Project root path", "type": "string"},
            },
        }
    ),
    # v3.2: Debug runtime environment (MCP debugging)
    Tool(
        name="debug_runtime",
        description="Debug MCP runtime environment. Shows Python executable, clouvel path, and entitlement status. Use to diagnose MCP/interpreter issues.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path for is_developer check", "type": "string"},
            },
        }
    ),
    # v2.0: Proactive MCP tools
    Tool(
        name="drift_check",
        description="Detect when your work drifts from original goals. Catches scope creep early.",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"description": "Project root path", "type": "string"},
                "silent": {"description": "If True, return minimal output (for hooks)", "type": "boolean"},
            },
            "required": ["path"],
        }
    ),
    Tool(
        name="pattern_watch",
        description="v2.0: Watch for repeated error patterns. Detects when same error occurs multiple times. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"description": "Project root path", "type": "string"},
                "threshold": {"description": "Number of occurrences to trigger alert (default: 3)", "type": "integer"},
                "check_only": {"description": "If True, only check without recording", "type": "boolean"},
            },
            "required": ["path"],
        }
    ),
    Tool(
        name="auto_remind",
        description="v2.0: Configure automatic progress reminders. Reminds to update current.md periodically. (Pro)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"description": "Project root path", "type": "string"},
                "interval": {"description": "Reminder interval in minutes (default: 30)", "type": "integer"},
                "enabled": {"description": "Enable or disable reminders", "type": "boolean"},
            },
            "required": ["path"],
        }
    ),
    # Meeting (Free, v2.1)
    Tool(
        name="meeting",
        description="Simulate a C-Level review with 8 virtual managers (PM, CTO, QA, CSO, CDO, CMO, CFO, Error). Get multi-perspective feedback on your plan or code.",
        inputSchema={
            "type": "object",
            "properties": {
                "context": {"description": "Meeting topic or situation to review", "type": "string"},
                "topic": {
                    "description": "Topic hint for auto-selecting relevant managers",
                    "type": "string",
                    "enum": ["auth", "api", "payment", "ui", "feature", "launch", "error", "security", "performance", "design", "cost", "maintenance"],
                },
                "managers": {
                    "description": "Specific managers to include (auto-selected if omitted): PM, CTO, QA, CSO, CDO, CMO, CFO, ERROR",
                    "type": "array",
                    "items": {"type": "string"},
                },
                "project_path": {"description": "Project path (for Knowledge Base integration)", "type": "string"},
                "include_example": {"description": "Include few-shot examples (default: true)", "type": "boolean"},
            },
            "required": ["context"],
        }
    ),
    Tool(
        name="meeting_topics",
        description="List available meeting topics.",
        inputSchema={
            "type": "object",
            "properties": {},
        }
    ),
    # Meeting Feedback & Tuning (Free, v2.2)
    Tool(
        name="rate_meeting",
        description="Rate meeting quality (1-5) with optional feedback.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
                "meeting_id": {"description": "Meeting ID (shown after running meeting tool)", "type": "string"},
                "rating": {"description": "Quality rating (1-5). 1: not helpful, 3: average, 5: very useful", "type": "integer", "minimum": 1, "maximum": 5},
                "feedback": {"description": "Text feedback (optional)", "type": "string"},
                "tags": {"description": "Tags (e.g., natural, actionable, specific)", "type": "array", "items": {"type": "string"}},
            },
            "required": ["project_path", "meeting_id", "rating"],
        }
    ),
    Tool(
        name="get_meeting_stats",
        description="Meeting quality statistics by topic and version.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
                "days": {"description": "Analysis period in days", "type": "integer"},
            },
            "required": ["project_path"],
        }
    ),
    Tool(
        name="export_training_data",
        description="Export high-quality meeting transcripts (rating >= 4).",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
                "min_rating": {"description": "Minimum rating (default: 4)", "type": "integer"},
            },
            "required": ["project_path"],
        }
    ),
    Tool(
        name="enable_ab_testing",
        description="Enable A/B testing for prompt variants.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
                "variants": {"description": "Variants to test (default: all)", "type": "array", "items": {"type": "string"}},
            },
            "required": ["project_path"],
        }
    ),
    Tool(
        name="disable_ab_testing",
        description="Disable A/B testing. Optionally set a winner.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
                "set_winner": {"description": "Variant to set as active", "type": "string"},
            },
            "required": ["project_path"],
        }
    ),
    Tool(
        name="get_variant_performance",
        description="Compare prompt variant performance.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
            },
            "required": ["project_path"],
        }
    ),
    Tool(
        name="list_variants",
        description="List available prompt variants.",
        inputSchema={
            "type": "object",
            "properties": {},
        }
    ),
    # Meeting Personalization (Free, v2.3)
    Tool(
        name="configure_meeting",
        description="Configure meeting settings per project: manager weights, default managers by topic, language/format.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
                "manager_weights": {
                    "description": "Weight per manager (0.0-2.0). Example: {\"CSO\": 1.5, \"CDO\": 0.5}",
                    "type": "object",
                },
                "default_managers": {
                    "description": "Default managers per topic. Example: {\"auth\": [\"PM\", \"CTO\", \"CSO\"]}",
                    "type": "object",
                },
                "preferences": {
                    "description": "Language (ko/en), format (formal/casual), detail (full/summary/minimal)",
                    "type": "object",
                },
            },
            "required": ["project_path"],
        }
    ),
    Tool(
        name="add_persona_override",
        description="Customize a manager persona with project-specific phrases and focus areas.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
                "manager": {"description": "Manager key (PM, CTO, QA, CSO, CDO, CMO, CFO, ERROR)", "type": "string"},
                "overrides": {
                    "description": "Override settings. Example: {\"pet_phrases\": [\"watch tech debt\"], \"focus_areas\": [\"security\"]}",
                    "type": "object",
                },
            },
            "required": ["project_path", "manager", "overrides"],
        }
    ),
    Tool(
        name="get_meeting_config",
        description="View current meeting configuration.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
            },
            "required": ["project_path"],
        }
    ),
    Tool(
        name="reset_meeting_config",
        description="Reset meeting configuration to defaults.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {"description": "Project path", "type": "string"},
            },
            "required": ["project_path"],
        }
    ),
]
