# Conversation Generator
# 동적 회의 시뮬레이션 로직

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# .env 파일 자동 로드 (글로벌 → 프로젝트 순서)
def _load_env():
    """
    환경변수 로드 순서:
    1. ~/.clouvel/.env (글로벌) - 기본값
    2. 프로젝트 .env - override

    python-dotenv 없으면 수동으로 파싱
    """
    loaded_files = []

    # 1. 글로벌 ~/.clouvel/.env 먼저 로드
    if os.name == 'nt':
        home = Path(os.environ.get('USERPROFILE', '~'))
    else:
        home = Path.home()
    global_env = home / ".clouvel" / ".env"

    # 2. 프로젝트 .env 찾기
    project_env = None
    current = Path(__file__).resolve().parent
    for _ in range(10):
        env_file = current / ".env"
        if env_file.exists():
            project_env = env_file
            break
        if (current / ".git").exists():
            project_env = current / ".env"
            break
        current = current.parent

    # dotenv 패키지 시도
    try:
        from dotenv import load_dotenv
        if global_env.exists():
            load_dotenv(global_env, override=False)
            loaded_files.append(str(global_env))
        if project_env and project_env.exists():
            load_dotenv(project_env, override=True)
            loaded_files.append(str(project_env))
        return
    except ImportError:
        pass

    # python-dotenv 없으면 수동 파싱
    def _parse_env_file(filepath: Path):
        if not filepath.exists():
            return
        try:
            for line in filepath.read_text(encoding='utf-8').splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, _, value = line.partition('=')
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:  # 기존 환경변수 우선
                        os.environ[key] = value
        except Exception:
            pass

    if global_env.exists():
        _parse_env_file(global_env)
    if project_env and project_env.exists():
        _parse_env_file(project_env)

_load_env()

from ..prompts import (
    PERSONAS,
    get_persona,
    get_system_prompt,
    get_topic_guide,
    get_conversation_starter,
    format_examples_for_prompt,
)
from ..utils import _analyze_context
from .collector import save_meeting_log


@dataclass
class MeetingConfig:
    """회의 시뮬레이션 설정"""
    # 기본 설정
    max_turns: int = 8  # 최대 대화 턴 수
    include_action_items: bool = True
    include_warnings: bool = True

    # 매니저 설정
    auto_select_managers: bool = True
    forced_managers: List[str] = field(default_factory=list)
    excluded_managers: List[str] = field(default_factory=list)

    # Few-shot 설정
    include_examples: bool = True
    example_count: int = 1

    # 로깅 설정
    auto_log: bool = True
    log_path: Optional[str] = None

    # 출력 설정
    output_format: str = "markdown"  # markdown, json, raw


class MeetingGenerator:
    """회의 시뮬레이션 생성기"""

    def __init__(self, config: Optional[MeetingConfig] = None):
        self.config = config or MeetingConfig()
        self._last_meeting = None

    def generate(
        self,
        context: str,
        topic: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        회의록을 생성합니다.

        Args:
            context: 회의 주제/상황 설명
            topic: 토픽 (auto-detect if None)
            additional_context: 추가 컨텍스트 (파일 내용 등)

        Returns:
            회의 결과 딕셔너리
        """
        # 1. 토픽 감지
        if topic is None:
            detected_topics = _analyze_context(context)
            topic = detected_topics[0] if detected_topics else "feature"

        # 2. 참여 매니저 결정
        active_managers = self._select_managers(topic)

        # 3. 프롬프트 조합
        system_prompt = self._build_system_prompt(topic, active_managers)
        user_prompt = self._build_user_prompt(context, topic, additional_context)

        # 4. 결과 구조화
        result = {
            "context": context,
            "topic": topic,
            "active_managers": active_managers,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "timestamp": datetime.now().isoformat(),
            "config": {
                "max_turns": self.config.max_turns,
                "include_examples": self.config.include_examples,
            }
        }

        # 5. 로깅 (설정된 경우)
        if self.config.auto_log:
            save_meeting_log(result, self.config.log_path)

        self._last_meeting = result
        return result

    def _select_managers(self, topic: str) -> List[str]:
        """토픽에 맞는 매니저를 선택합니다."""
        # 강제 포함 매니저
        if self.config.forced_managers:
            managers = list(self.config.forced_managers)
        elif self.config.auto_select_managers:
            # 토픽 가이드 기반 선택
            guide = get_topic_guide(topic)
            managers = guide.get("participants", ["PM", "CTO", "QA"])
        else:
            managers = list(PERSONAS.keys())

        # 제외 매니저 필터링
        managers = [m for m in managers if m not in self.config.excluded_managers]

        # PM은 항상 포함
        if "PM" not in managers:
            managers.insert(0, "PM")

        return managers

    def _build_system_prompt(self, topic: str, active_managers: List[str]) -> str:
        """시스템 프롬프트를 조합합니다."""
        parts = []

        # 1. 기본 시스템 프롬프트
        parts.append(get_system_prompt(active_managers))

        # 2. 토픽 가이드
        guide = get_topic_guide(topic)
        parts.append(f"""
## 이번 회의 정보
- **토픽**: {topic}
- **리드**: {guide['lead']}
- **포커스**: {guide['focus']}
- **핵심 질문**: {', '.join(guide['key_questions'])}
""")

        # 3. Few-shot 예시 (설정된 경우)
        if self.config.include_examples:
            examples = format_examples_for_prompt(topic, self.config.example_count)
            if examples:
                parts.append(examples)

        return "\n\n".join(parts)

    def _build_user_prompt(
        self,
        context: str,
        topic: str,
        additional_context: Optional[str] = None
    ) -> str:
        """유저 프롬프트를 조합합니다."""
        parts = []

        # 1. 메인 컨텍스트
        parts.append(f"## 회의 안건\n\n{context}")

        # 2. 추가 컨텍스트 (있는 경우)
        if additional_context:
            parts.append(f"## 추가 정보\n\n{additional_context}")

        # 3. 출력 지시
        parts.append("""
## 출력 요청

위 안건에 대해 C-Level 회의를 시뮬레이션해주세요.

요구사항:
1. 매니저들이 서로 대화하듯 자연스럽게
2. 컨텍스트에 맞는 구체적인 의견 (일반론 X)
3. 의견 충돌이 있으면 논의 후 합의
4. 실행 가능한 액션 아이템으로 마무리
5. 솔로 개발자 현실 고려 (리소스 제약)
""")

        return "\n\n".join(parts)

    def get_prompt_for_claude(self) -> Dict[str, str]:
        """
        Claude API 호출용 프롬프트를 반환합니다.

        Returns:
            {"system": str, "user": str} 형태의 딕셔너리
        """
        if not self._last_meeting:
            raise ValueError("generate()를 먼저 호출해야 합니다.")

        return {
            "system": self._last_meeting["system_prompt"],
            "user": self._last_meeting["user_prompt"]
        }


def generate_meeting(
    context: str,
    topic: Optional[str] = None,
    config: Optional[MeetingConfig] = None,
    additional_context: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    회의록 생성 편의 함수

    Args:
        context: 회의 주제/상황 설명
        topic: 토픽 (auto-detect if None)
        config: MeetingConfig 인스턴스
        additional_context: 추가 컨텍스트 (Knowledge Base 등)
        **kwargs: MeetingConfig에 전달할 추가 인자

    Returns:
        회의 결과 딕셔너리
    """
    if config is None:
        config = MeetingConfig(**kwargs)

    generator = MeetingGenerator(config)
    return generator.generate(context, topic, additional_context)


def _generate_fallback_meeting(
    context: str,
    topic: Optional[str],
    result: dict,
    error: Optional[str] = None
) -> str:
    """Generate a static meeting response when API is not available.

    This provides basic manager feedback without the dynamic Claude API call.
    """
    detected_topic = result.get("topic", topic or "general")
    managers = result.get("managers", ["PM", "CTO", "QA"])
    action_items = result.get("action_items", [])

    output = f"""## 🏢 C-Level 회의록 (Static Mode)

> ⚠️ Dynamic meeting generation unavailable. Using static responses.
"""

    if error:
        output += f"> Error: {error[:100]}\n"

    output += f"""
**Topic**: {detected_topic}
**Participants**: {', '.join(managers)}

---

### 💡 Manager Perspectives

"""

    # Generate basic static feedback based on topic
    static_feedback = {
        "PM": f"Context reviewed. Key points identified. Recommend creating detailed action items.",
        "CTO": f"Technical aspects noted. Architecture considerations should be documented.",
        "QA": f"Quality checkpoints needed. Test cases should be defined for key features.",
        "CDO": f"Design consistency important. UI/UX patterns should follow established guidelines.",
        "CMO": f"Market positioning noted. Communication strategy should align with goals.",
        "CFO": f"Cost implications reviewed. Budget allocation should be planned.",
        "CSO": f"Security considerations flagged. Access controls and data protection needed.",
    }

    for mgr in managers[:4]:  # Limit to 4 managers in fallback
        output += f"**{mgr}**: {static_feedback.get(mgr, 'Reviewed and noted.')}\n\n"

    output += """---

### 📋 Recommended Next Steps

1. Define specific action items based on discussion
2. Assign owners and deadlines
3. Schedule follow-up review

---

> 💡 For dynamic meeting generation, set ANTHROPIC_API_KEY environment variable.
> 💡 Or install: `pip install anthropic`
"""

    return output


def _get_kb_context_for_meeting(context: str, topic: str, project_path: str = None) -> str:
    """Get KB context for meeting generation."""
    try:
        from clouvel.db.knowledge import (
            search_knowledge,
            get_recent_decisions,
            get_or_create_project,
            KNOWLEDGE_DB_PATH,
        )
        if not KNOWLEDGE_DB_PATH.exists():
            return ""

        project_id = None
        if project_path:
            project_name = Path(project_path).name
            project_id = get_or_create_project(project_name, project_path)

        sections = []

        # Search for relevant past decisions
        search_results = search_knowledge(topic or "feature", project_id=project_id, limit=5)
        relevant = [r for r in search_results if r.get('type') == 'decision']

        if relevant:
            sections.append("### 📚 Relevant Past Decisions")
            for r in relevant[:3]:
                sections.append(f"- {r.get('content', '')[:120]}...")

        # Get recent decisions
        recent = get_recent_decisions(project_id=project_id, limit=3)
        if recent:
            sections.append("\n### 🕐 Recent Project Decisions")
            for d in recent:
                sections.append(f"- **[{d.get('category', '')}]** {d.get('decision', '')[:80]}")

        if sections:
            return "\n---\n## 💡 Project History\n_Reference these when asking questions:_\n\n" + "\n".join(sections)
        return ""
    except Exception:
        return ""


def generate_meeting_sync(
    context: str,
    topic: Optional[str] = None,
    anthropic_client=None,
    model: str = "claude-sonnet-4-20250514",
    project_path: Optional[str] = None,
    **kwargs
) -> str:
    """
    Anthropic API를 사용해 회의록을 직접 생성합니다.

    Args:
        context: 회의 주제/상황 설명
        topic: 토픽 (auto-detect if None)
        anthropic_client: Anthropic 클라이언트 인스턴스
        model: 사용할 모델
        project_path: 프로젝트 경로 (회의록 저장용 + KB 조회)
        **kwargs: MeetingConfig에 전달할 추가 인자

    Returns:
        생성된 회의록 문자열 (저장 경로 + 안내 포함)
    """
    # Get KB context
    kb_context = _get_kb_context_for_meeting(context, topic, project_path)

    # 프롬프트 생성
    config = MeetingConfig(**kwargs)
    generator = MeetingGenerator(config)
    result = generator.generate(context, topic, additional_context=kb_context)
    prompts = generator.get_prompt_for_claude()

    # Anthropic API 호출
    if anthropic_client is None:
        try:
            import anthropic
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                # Fallback: return static response without API
                return _generate_fallback_meeting(context, topic, result)
            anthropic_client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            # Fallback: return static response without anthropic package
            return _generate_fallback_meeting(context, topic, result)

    try:
        response = anthropic_client.messages.create(
            model=model,
            max_tokens=4096,
            system=prompts["system"],
            messages=[
                {"role": "user", "content": prompts["user"]}
            ]
        )
        meeting_output = response.content[0].text
    except Exception as e:
        # Fallback on API error
        return _generate_fallback_meeting(context, topic, result, error=str(e))

    # 로깅 (튜닝 데이터 수집)
    if config.auto_log:
        save_meeting_log(
            {
                **result,
                "output": meeting_output,
                "model": model,
            },
            config.log_path
        )

    # 회의록 파일 저장 (project_path가 있는 경우)
    meeting_file_path = None
    if project_path:
        try:
            meetings_dir = Path(project_path) / ".claude" / "planning" / "meetings"
            meetings_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
            detected_topic = result.get("topic", "meeting")
            filename = f"{timestamp}_{detected_topic}.md"
            meeting_file_path = meetings_dir / filename

            # 회의록 파일 저장
            meeting_content = f"""# 회의록: {detected_topic}

> 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> 컨텍스트: {context[:200]}{'...' if len(context) > 200 else ''}

---

{meeting_output}
"""
            meeting_file_path.write_text(meeting_content, encoding='utf-8')
        except Exception as e:
            # 저장 실패해도 회의록은 반환
            pass

    # 안내 메시지 추가
    footer = """

---

## 다음 단계

회의 결과를 확인하셨으면, 실행 계획이 필요할 때 `plan` 도구를 요청하세요.

> 💡 회의 결과가 저장되었습니다."""

    if meeting_file_path:
        footer += f"\n> 📁 저장 위치: `{meeting_file_path}`"

    return meeting_output + footer


# 프롬프트 미리보기 함수
def preview_prompt(
    context: str,
    topic: Optional[str] = None,
    **kwargs
) -> None:
    """
    생성될 프롬프트를 미리 출력합니다 (디버깅용)

    Args:
        context: 회의 주제/상황 설명
        topic: 토픽
    """
    config = MeetingConfig(**kwargs)
    generator = MeetingGenerator(config)
    result = generator.generate(context, topic)

    print("=" * 60)
    print("SYSTEM PROMPT")
    print("=" * 60)
    print(result["system_prompt"][:2000])
    print("\n... (truncated)\n")

    print("=" * 60)
    print("USER PROMPT")
    print("=" * 60)
    print(result["user_prompt"])

    print("=" * 60)
    print(f"Topic: {result['topic']}")
    print(f"Active Managers: {result['active_managers']}")
    print("=" * 60)
