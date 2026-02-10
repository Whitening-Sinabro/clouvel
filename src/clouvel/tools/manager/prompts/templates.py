# Meeting Templates
# Prompt templates for meeting simulation

from typing import Dict, List
from .personas import PERSONAS

# Meeting simulation system prompt
MEETING_TEMPLATE = """You are simulating a startup C-Level meeting.

## Core Philosophy: AUGMENTATION, NOT AUTOMATION

**CRITICAL**: Your job is NOT to give answers. Your job is to help the solo developer THINK.

- ❌ DON'T: "Use OAuth for authentication"
- ✅ DO: "Have you considered: What's your user base like? Do they prefer social login or email?"

Solo developers must make 8 different roles' worth of decisions alone. Your job is to:
1. Surface questions they haven't thought about
2. Reveal blind spots in their thinking
3. Help them make THEIR OWN informed decisions

## Background
- Advisory board of 8 veteran managers (15-20 years experience)
- Target: Solo developers / Indie hackers
- Purpose: Help them think from 8 perspectives, not think FOR them

## Manager Roster
{manager_list}

## Meeting Rules

### 1. Conversation Flow
1. **PM** frames the decision points (not recommendations)
2. Each relevant manager raises QUESTIONS from their perspective
3. Managers may offer 2-3 OPTIONS with tradeoffs (not single answers)
4. **PM** summarizes what the DEVELOPER needs to decide

### 2. Question-First Style
- Each manager asks 1-3 probing questions from their expertise
- Questions should be specific to the context (not generic)
- After questions, offer options with clear tradeoffs
- Let the developer make the final call

### 3. Interaction Patterns
- Build on questions: "Adding to CTO's point about scale, also consider..."
- Offer perspectives: "From a security lens, the key question is..."
- Present tradeoffs: "Option A is faster but... Option B is safer but..."

### 4. Restrictions
- NO definitive answers (only options and questions)
- NO generic advice (must be specific to context)
- NO patronizing tone (developer is capable, just needs perspectives)

## Output Format

```
## 🏢 C-Level Perspectives

**👔 PM**: [Frame the decision - what's being decided here]

**🛠️ CTO**:
Questions to consider:
- [Specific technical question]
- [Architecture consideration]

Options:
1. [Option A] - Faster, but [tradeoff]
2. [Option B] - Safer, but [tradeoff]

**🧪 QA**:
Questions to consider:
- [Testing consideration]
- [Edge case to think about]

(Only relevant managers participate)

---

## 🤔 Decisions for YOU

| # | Decision | Options | Your Call |
|---|----------|---------|-----------|
| 1 | Auth approach | OAuth / Email / Magic Link | _____ |
| 2 | MVP scope | Feature X included? | Yes / No |

## 💡 Key Questions to Answer

Before proceeding, consider:
1. [Most important question from PM]
2. [Critical technical question from CTO]
3. [Key risk question from relevant manager]

## ⚠️ Watch Out For
- ❌ If you skip: [consequence]
- ✅ Must verify: [critical check]
```
"""


def get_system_prompt(active_managers: List[str] = None) -> str:
    """Generates system prompt for meeting simulation."""

    if active_managers is None:
        active_managers = list(PERSONAS.keys())

    # Build manager list
    manager_lines = []
    for key in active_managers:
        if key in PERSONAS:
            p = PERSONAS[key]

            # Get probing questions if available
            probing_qs = p.get('probing_questions', {})
            sample_questions = []
            for category, questions in list(probing_qs.items())[:2]:
                sample_questions.extend(questions[:2])

            probing_section = ""
            if sample_questions:
                qs_formatted = "\n".join(f"- {q}" for q in sample_questions[:4])
                probing_section = f"""
**Probing Questions** (use to help developer think):
{qs_formatted}
"""

            manager_lines.append(f"""
### {p['emoji']} {key} ({p['years']} years exp. {p['title']})

**Background**: {p['background']['career'][-1]}

**Expertise**: {', '.join(p['expertise'][:3])}

**Philosophy**: {p['personality']['philosophy']}
{probing_section}
**Tone**: {p['communication']['tone']}
""")

    manager_list = "\n".join(manager_lines)

    return MEETING_TEMPLATE.format(manager_list=manager_list)


def get_persona_prompt(manager_key: str) -> str:
    """Generates individual prompt for a specific manager."""

    p = PERSONAS.get(manager_key.upper())
    if not p:
        return ""

    career_str = "\n".join([f"  - {c}" for c in p['background']['career']])
    achievements_str = "\n".join([f"  - {a}" for a in p['background']['achievements']])
    expertise_str = ", ".join(p['expertise'])
    pet_phrases_str = "\n".join([f'  - "{phrase}"' for phrase in p['communication']['pet_phrases']])

    return f"""## {p['emoji']} {manager_key}

**Experience**: {p['years']} years as {p['title']}

### Career
{career_str}

### Key Achievements
{achievements_str}

### Expertise
{expertise_str}

### Personality
- Traits: {', '.join(p['personality']['traits'])}
- Philosophy: {p['personality']['philosophy']}
- Weakness: {p['personality']['weakness']}

### Communication
- Tone: {p['communication']['tone']}
- Pet Phrases:
{pet_phrases_str}

### AI Perspective
- Tools Used: {', '.join(p['ai_perspective']['tools'])}
- Opinion: {p['ai_perspective']['opinion']}
- Caution: {p['ai_perspective']['caution']}

### Interaction Rules
- Agrees With: {', '.join(p['interaction_rules']['agrees_with'])}
- Challenges: {', '.join(p['interaction_rules']['challenges'])}
- Defers To: {', '.join(p['interaction_rules']['defers_to'])}
"""


# Topic-specific meeting guides
TOPIC_GUIDES = {
    "auth": {
        "lead": "CSO",
        "participants": ["PM", "CTO", "CSO", "QA", "ERROR"],
        "focus": "Security, authentication flow, session management",
        "key_questions": [
            "OAuth vs custom auth?",
            "Session expiration policy?",
            "Password policy?"
        ]
    },
    "payment": {
        "lead": "CFO",
        "participants": ["PM", "CTO", "CFO", "CSO", "QA", "ERROR"],
        "focus": "Payment flow, payment gateway, security",
        "key_questions": [
            "Which payment gateway?",
            "Subscription or one-time?",
            "Refund policy?"
        ]
    },
    "api": {
        "lead": "CTO",
        "participants": ["PM", "CTO", "QA", "CSO", "ERROR"],
        "focus": "API design, authentication, error handling",
        "key_questions": [
            "REST vs GraphQL?",
            "Auth method?",
            "Rate limit?"
        ]
    },
    "ui": {
        "lead": "CDO",
        "participants": ["PM", "CDO", "QA", "CMO"],
        "focus": "UX, consistency, accessibility",
        "key_questions": [
            "Design system in place?",
            "Mobile responsive?",
            "Accessibility considered?"
        ]
    },
    "feature": {
        "lead": "PM",
        "participants": ["PM", "CTO", "QA"],
        "focus": "Requirements, priorities, scope",
        "key_questions": [
            "In the PRD?",
            "MVP scope?",
            "Priority?"
        ]
    },
    "launch": {
        "lead": "PM",
        "participants": ["PM", "CMO", "CTO", "QA", "CFO", "ERROR"],
        "focus": "Launch strategy, marketing, monitoring",
        "key_questions": [
            "Target users?",
            "Marketing channels?",
            "Monitoring ready?"
        ]
    },
    "error": {
        "lead": "ERROR",
        "participants": ["ERROR", "CTO", "QA", "PM"],
        "focus": "Incident analysis, recovery, prevention",
        "key_questions": [
            "Root cause?",
            "Recovery plan?",
            "Prevention measures?"
        ]
    },
    "security": {
        "lead": "CSO",
        "participants": ["CSO", "CTO", "QA", "ERROR"],
        "focus": "Vulnerabilities, auth/authz, data protection",
        "key_questions": [
            "OWASP Top 10 checked?",
            "Input validation?",
            "Sensitive data encrypted?"
        ]
    },
    "performance": {
        "lead": "CTO",
        "participants": ["CTO", "QA", "CFO", "ERROR"],
        "focus": "Performance, scalability, cost",
        "key_questions": [
            "Bottlenecks?",
            "Caching strategy?",
            "Cost impact?"
        ]
    },
    "maintenance": {
        "lead": "PM",
        "participants": ["PM", "CTO", "QA", "ERROR"],
        "focus": "Maintenance plan, tech debt, monitoring",
        "key_questions": [
            "Maintenance scope?",
            "Tech debt status?",
            "Monitoring/alerting?"
        ]
    },
    "design": {
        "lead": "CDO",
        "participants": ["CDO", "PM", "CMO", "CTO"],
        "focus": "Design system, branding, feasibility",
        "key_questions": [
            "Design principles?",
            "Brand guide exists?",
            "Implementation difficulty?"
        ]
    }
}


def get_topic_guide(topic: str) -> Dict:
    """Returns meeting guide for the given topic."""
    return TOPIC_GUIDES.get(topic, TOPIC_GUIDES["feature"])


# Situation-specific conversation starters
CONVERSATION_STARTERS = {
    "new_feature": {
        "PM": "Let's discuss the new {feature} feature. Based on the PRD...",
        "CTO": "Let me first look at technical feasibility.",
        "QA": "We should define the test scope first."
    },
    "bug_fix": {
        "ERROR": "I saw the incident report. Here's the situation...",
        "CTO": "Let me share the root cause analysis...",
        "QA": "I've documented the reproduction steps and test cases."
    },
    "security_issue": {
        "CSO": "Security issue discovered. Severity is...",
        "CTO": "I checked the impact scope...",
        "PM": "Let's first assess the timeline impact..."
    },
    "launch_prep": {
        "PM": "D-{days} to launch. Let's go through the checklist.",
        "CMO": "Here's the marketing prep status...",
        "ERROR": "I'll verify the monitoring/alerting setup."
    },
    "cost_review": {
        "CFO": "Monthly cost review.",
        "CTO": "Let me explain the infrastructure costs...",
        "PM": "From an ROI perspective..."
    },
    "maintenance_plan": {
        "PM": "Discussing maintenance plan. Current status is...",
        "CTO": "Let me share the tech debt status first...",
        "QA": "Test coverage status is...",
        "ERROR": "Looking at the ops issue patterns..."
    }
}


def get_conversation_starter(situation: str, **kwargs) -> Dict[str, str]:
    """Returns conversation starter template for the given situation."""
    starters = CONVERSATION_STARTERS.get(situation, CONVERSATION_STARTERS["new_feature"])

    # Replace template variables
    result = {}
    for manager, template in starters.items():
        result[manager] = template.format(**kwargs) if kwargs else template

    return result
