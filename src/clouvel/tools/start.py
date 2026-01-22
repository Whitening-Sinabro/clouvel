# Clouvel Start Tool (Free)
# 프로젝트 온보딩 + PRD 강제 + 대화형 가이드

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

# 프로젝트 타입 감지 패턴
PROJECT_TYPE_PATTERNS = {
    "chrome-ext": {
        "files": ["manifest.json"],
        "content_check": {"manifest.json": ["manifest_version", "permissions"]},
        "description": "Chrome 확장프로그램"
    },
    "discord-bot": {
        "dependencies": ["discord.js", "discord.py", "discordpy", "nextcord", "pycord"],
        "files": ["bot.py", "bot.js", "cogs/"],
        "description": "디스코드 봇"
    },
    "cli": {
        "files": ["bin/", "cli.py", "cli.js", "__main__.py"],
        "dependencies": ["commander", "yargs", "click", "typer", "argparse"],
        "pyproject_check": ["[project.scripts]"],
        "description": "CLI 도구"
    },
    "landing-page": {
        "files": ["index.html"],
        "no_backend": True,
        "description": "랜딩 페이지"
    },
    "api": {
        "files": ["server.py", "server.js", "app.py", "main.py", "index.js"],
        "dependencies": ["express", "fastapi", "flask", "django", "koa", "hono", "gin"],
        "description": "API 서버"
    },
    "web-app": {
        "files": ["src/App.tsx", "src/App.jsx", "src/main.tsx", "pages/", "app/"],
        "dependencies": ["react", "vue", "svelte", "next", "nuxt", "angular"],
        "description": "웹 애플리케이션"
    },
    "saas": {
        "files": ["src/App.tsx", "pages/pricing", "app/pricing", "stripe.ts", "checkout"],
        "dependencies": ["stripe", "@stripe/stripe-js", "lemonsqueezy", "paddle"],
        "description": "SaaS MVP"
    }
}

# 타입별 PRD 작성 질문
PRD_QUESTIONS = {
    "chrome-ext": [
        {"section": "summary", "question": "이 확장프로그램이 해결하려는 문제는 무엇인가요?", "example": "예: 유튜브 광고 스킵이 번거로움"},
        {"section": "target", "question": "주요 사용자는 누구인가요?", "example": "예: 유튜브 헤비 유저, 직장인"},
        {"section": "features", "question": "핵심 기능 3가지를 알려주세요", "example": "예: 1. 광고 자동 스킵 2. 스폰서 구간 건너뛰기 3. 통계 표시"},
        {"section": "permissions", "question": "필요한 권한은 무엇인가요?", "example": "예: activeTab, storage"},
        {"section": "out_of_scope", "question": "이번 버전에서 제외할 기능은?", "example": "예: Firefox 지원, 다크모드"}
    ],
    "discord-bot": [
        {"section": "summary", "question": "이 봇이 해결하려는 문제는 무엇인가요?", "example": "예: 서버 관리가 번거로움"},
        {"section": "target", "question": "주요 사용 서버 유형과 규모는?", "example": "예: 게임 커뮤니티, 100-500명"},
        {"section": "commands", "question": "핵심 명령어 3-5개를 알려주세요", "example": "예: /경고, /뮤트, /전적, /매칭"},
        {"section": "permissions", "question": "필요한 봇 권한은?", "example": "예: 메시지 관리, 멤버 관리"},
        {"section": "out_of_scope", "question": "이번 버전에서 제외할 기능은?", "example": "예: 음성 기능, 대시보드"}
    ],
    "cli": [
        {"section": "summary", "question": "이 CLI가 해결하려는 문제는 무엇인가요?", "example": "예: 프로젝트 초기화가 반복적임"},
        {"section": "target", "question": "주요 사용자는 누구인가요?", "example": "예: 백엔드 개발자"},
        {"section": "commands", "question": "핵심 명령어 3-5개를 알려주세요", "example": "예: init, run, build, deploy"},
        {"section": "options", "question": "주요 옵션/플래그는?", "example": "예: --verbose, --config, --dry-run"},
        {"section": "out_of_scope", "question": "이번 버전에서 제외할 기능은?", "example": "예: GUI, 자동 업데이트"}
    ],
    "landing-page": [
        {"section": "summary", "question": "이 랜딩 페이지의 목표는 무엇인가요?", "example": "예: SaaS 제품 얼리버드 가입 유도"},
        {"section": "target", "question": "타겟 방문자는 누구인가요?", "example": "예: 스타트업 창업자, 개발자"},
        {"section": "cta", "question": "Primary CTA(전환 목표)는?", "example": "예: 얼리버드 가입, 데모 신청"},
        {"section": "sections", "question": "필요한 섹션들을 나열해주세요", "example": "예: Hero, Problem, Solution, Features, Pricing, FAQ"},
        {"section": "metrics", "question": "목표 지표는?", "example": "예: 전환율 5%, 이탈률 40% 미만"}
    ],
    "api": [
        {"section": "summary", "question": "이 API가 해결하려는 문제는 무엇인가요?", "example": "예: 프론트엔드에서 데이터 접근이 필요함"},
        {"section": "clients", "question": "주요 API 소비자는?", "example": "예: 웹 프론트엔드, 모바일 앱"},
        {"section": "endpoints", "question": "핵심 엔드포인트 5개를 알려주세요", "example": "예: POST /auth/login, GET /users, POST /orders"},
        {"section": "auth", "question": "인증 방식은?", "example": "예: JWT Bearer Token"},
        {"section": "out_of_scope", "question": "이번 버전에서 제외할 것은?", "example": "예: GraphQL, WebSocket"}
    ],
    "web-app": [
        {"section": "summary", "question": "이 앱이 해결하려는 문제는 무엇인가요?", "example": "예: 식단 관리가 번거로움"},
        {"section": "target", "question": "주요 사용자는 누구인가요?", "example": "예: 20-30대 직장인, 다이어터"},
        {"section": "features", "question": "핵심 기능 3-5개를 알려주세요", "example": "예: 1. 식단 기록 2. 칼로리 계산 3. 주간 리포트"},
        {"section": "pages", "question": "주요 페이지/화면은?", "example": "예: 로그인, 대시보드, 기록 입력, 통계"},
        {"section": "out_of_scope", "question": "이번 버전에서 제외할 기능은?", "example": "예: 소셜 기능, 다국어"}
    ],
    "saas": [
        {"section": "summary", "question": "이 SaaS가 해결하려는 문제는 무엇인가요?", "example": "예: 랜딩 페이지 만들기가 어려움"},
        {"section": "target", "question": "주요 타겟 사용자는?", "example": "예: 1인 창업자, 소규모 팀"},
        {"section": "features", "question": "핵심 기능 3-5개를 알려주세요", "example": "예: 1. 드래그앤드롭 빌더 2. 템플릿 3. 커스텀 도메인"},
        {"section": "pricing", "question": "가격 구조는? (Free/Pro 등)", "example": "예: Free $0 (3개 제한), Pro $15/월 (무제한)"},
        {"section": "payment", "question": "결제 방식은?", "example": "예: Stripe 구독, 연/월 결제"},
        {"section": "out_of_scope", "question": "이번 버전에서 제외할 기능은?", "example": "예: 팀 기능, 모바일 앱"}
    ],
    "generic": [
        {"section": "summary", "question": "이 프로젝트가 해결하려는 문제는 무엇인가요?"},
        {"section": "target", "question": "주요 사용자/대상은 누구인가요?"},
        {"section": "features", "question": "핵심 기능 3-5개를 알려주세요"},
        {"section": "tech", "question": "사용할 기술 스택은?"},
        {"section": "out_of_scope", "question": "이번 버전에서 제외할 것은?"}
    ]
}

# PRD 템플릿 (generic fallback)
PRD_TEMPLATE = """# {project_name} PRD

> 작성일: {date}

---

## 1. 프로젝트 개요

### 1.1 목적
[이 프로젝트가 해결하려는 문제를 작성하세요]

### 1.2 목표
- [ ] 핵심 목표 1
- [ ] 핵심 목표 2
- [ ] 핵심 목표 3

### 1.3 성공 지표
| 지표 | 목표값 | 측정 방법 |
|------|--------|-----------|
| ... | ... | ... |

---

## 2. 기능 요구사항

### 2.1 핵심 기능 (Must Have)
1. **기능 1**: 설명
2. **기능 2**: 설명

### 2.2 부가 기능 (Nice to Have)
1. **기능 1**: 설명

### 2.3 제외 범위 (Out of Scope)
- 이번 버전에서 제외할 것들

---

## 3. 기술 스펙

### 3.1 기술 스택
- Frontend:
- Backend:
- Database:
- Infra:

### 3.2 아키텍처
[아키텍처 다이어그램 또는 설명]

### 3.3 API 엔드포인트
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | /api/... | ... |

---

## 4. 데이터 모델

### 4.1 주요 엔티티
```
Entity1:
  - field1: type
  - field2: type

Entity2:
  - field1: type
```

### 4.2 관계도
[ERD 또는 관계 설명]

---

## 5. UI/UX

### 5.1 주요 화면
1. **화면 1**: 설명
2. **화면 2**: 설명

### 5.2 사용자 플로우
1. 사용자가 ...
2. 시스템이 ...

---

## 6. 에러 처리

### 6.1 예상 에러 시나리오
| 시나리오 | 에러 코드 | 사용자 메시지 |
|----------|-----------|---------------|
| ... | ... | ... |

### 6.2 복구 전략
- 전략 1: ...

---

## 7. 보안 요구사항

### 7.1 인증/인가
- 인증 방식:
- 권한 체계:

### 7.2 데이터 보호
- 암호화:
- 민감 정보 처리:

---

## 8. 테스트 계획

### 8.1 테스트 범위
- [ ] Unit Test
- [ ] Integration Test
- [ ] E2E Test

### 8.2 테스트 시나리오
| 시나리오 | 예상 결과 | 우선순위 |
|----------|-----------|----------|
| ... | ... | ... |

---

## 9. 일정

### 9.1 마일스톤
| 단계 | 내용 | 예상 완료일 |
|------|------|-------------|
| Phase 1 | ... | ... |

---

## 10. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|-----------|
| 0.1 | {date} | ... | 초안 작성 |
"""


def _detect_project_type(project_path: Path) -> Dict[str, Any]:
    """
    프로젝트 타입을 자동 감지합니다.
    파일 구조, 의존성, 설정 파일을 분석합니다.
    """
    detected = {
        "type": "generic",
        "confidence": 0,
        "signals": [],
        "description": "범용 프로젝트"
    }

    # 의존성 파일 읽기
    dependencies = set()

    # package.json
    pkg_json = project_path / "package.json"
    if pkg_json.exists():
        try:
            pkg_data = json.loads(pkg_json.read_text(encoding="utf-8"))
            deps = pkg_data.get("dependencies", {})
            dev_deps = pkg_data.get("devDependencies", {})
            dependencies.update(deps.keys())
            dependencies.update(dev_deps.keys())
        except:
            pass

    # pyproject.toml / requirements.txt
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            # 간단한 파싱 (정확하진 않지만 충분)
            for line in content.split("\n"):
                if ">=" in line or "==" in line:
                    dep = line.split(">=")[0].split("==")[0].strip().strip('"').strip("'")
                    if dep:
                        dependencies.add(dep.lower())
        except:
            pass

    requirements = project_path / "requirements.txt"
    if requirements.exists():
        try:
            for line in requirements.read_text(encoding="utf-8").split("\n"):
                dep = line.split(">=")[0].split("==")[0].split("[")[0].strip()
                if dep and not dep.startswith("#"):
                    dependencies.add(dep.lower())
        except:
            pass

    # 타입별 점수 계산
    scores = {}

    for ptype, patterns in PROJECT_TYPE_PATTERNS.items():
        score = 0
        signals = []

        # 파일 존재 체크
        if "files" in patterns:
            for f in patterns["files"]:
                if (project_path / f).exists():
                    score += 30
                    signals.append(f"파일 발견: {f}")

        # 의존성 체크
        if "dependencies" in patterns:
            for dep in patterns["dependencies"]:
                if dep.lower() in dependencies:
                    score += 40
                    signals.append(f"의존성 발견: {dep}")

        # manifest.json 내용 체크 (Chrome Extension)
        if "content_check" in patterns:
            for file, keywords in patterns["content_check"].items():
                file_path = project_path / file
                if file_path.exists():
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        for kw in keywords:
                            if kw in content:
                                score += 25
                                signals.append(f"{file}에서 '{kw}' 발견")
                    except:
                        pass

        # landing-page: 백엔드 없음 체크
        if patterns.get("no_backend"):
            has_backend = any((project_path / f).exists() for f in ["server.py", "server.js", "app.py", "main.py"])
            if not has_backend and (project_path / "index.html").exists():
                score += 20
                signals.append("백엔드 파일 없음, index.html만 존재")

        if score > 0:
            scores[ptype] = {"score": score, "signals": signals}

    # 최고 점수 타입 선택
    if scores:
        best_type = max(scores, key=lambda x: scores[x]["score"])
        best_score = scores[best_type]

        if best_score["score"] >= 30:  # 최소 신뢰도
            detected["type"] = best_type
            detected["confidence"] = min(best_score["score"], 100)
            detected["signals"] = best_score["signals"]
            detected["description"] = PROJECT_TYPE_PATTERNS[best_type]["description"]

    return detected


def start(path: str, project_name: str = "", project_type: str = "") -> Dict[str, Any]:
    """
    프로젝트 온보딩을 시작합니다.

    흐름:
    1. 프로젝트 타입 자동 감지 (또는 사용자 지정)
    2. docs 폴더 확인/생성
    3. PRD.md 존재 여부 체크
    4. 없으면 → 타입별 질문 목록 반환 (대화형 PRD 작성 가이드)
    5. 있으면 → 구조 검증 + 다음 단계 안내

    Args:
        path: 프로젝트 루트 경로
        project_name: 프로젝트 이름 (옵션)
        project_type: 프로젝트 타입 강제 지정 (옵션)

    Returns:
        온보딩 결과 및 다음 단계 안내 (또는 PRD 작성 질문)
    """
    from datetime import datetime

    project_path = Path(path).resolve()
    docs_path = project_path / "docs"
    prd_path = docs_path / "PRD.md"

    result = {
        "status": "UNKNOWN",
        "project_path": str(project_path),
        "docs_exists": False,
        "prd_exists": False,
        "prd_valid": False,
        "created_files": [],
        "next_steps": [],
        "message": ""
    }

    # 프로젝트 이름 추론
    if not project_name:
        project_name = project_path.name

    result["project_name"] = project_name

    # 프로젝트 타입 감지
    if project_type and project_type in PRD_QUESTIONS:
        detected = {
            "type": project_type,
            "confidence": 100,
            "signals": ["사용자 지정"],
            "description": PROJECT_TYPE_PATTERNS.get(project_type, {}).get("description", project_type)
        }
    else:
        detected = _detect_project_type(project_path)

    result["project_type"] = detected

    # 1. docs 폴더 확인/생성
    if not docs_path.exists():
        try:
            docs_path.mkdir(parents=True)
            result["created_files"].append("docs/")
        except Exception as e:
            result["status"] = "ERROR"
            result["message"] = f"docs 폴더 생성 실패: {e}"
            return result

    result["docs_exists"] = True

    # 2. PRD.md 확인
    if prd_path.exists():
        result["prd_exists"] = True

        # PRD 내용 검증
        prd_content = prd_path.read_text(encoding="utf-8")
        validation = _validate_prd(prd_content)

        if validation["is_valid"]:
            result["status"] = "READY"
            result["prd_valid"] = True
            result["message"] = "✅ PRD가 준비되었습니다. 코딩을 시작할 수 있습니다."
            result["next_steps"] = [
                "1. `can_code` 도구로 코딩 가능 여부 확인",
                "2. 필요시 `plan` 도구로 상세 실행 계획 수립",
                "3. 코딩 시작!"
            ]
            result["prd_summary"] = validation["summary"]
        else:
            result["status"] = "INCOMPLETE"
            result["message"] = "⚠️ PRD가 있지만 일부 섹션이 비어있습니다."
            result["missing_sections"] = validation["missing_sections"]
            result["next_steps"] = [
                f"1. PRD의 다음 섹션을 작성하세요: {', '.join(validation['missing_sections'])}",
                "2. 작성 후 다시 `start` 실행"
            ]
    else:
        # PRD가 없음 → 대화형 PRD 작성 가이드 시작
        result["status"] = "NEED_PRD"
        result["message"] = f"📝 PRD 작성이 필요합니다. {detected['description']} 프로젝트로 감지되었습니다."

        # 타입별 질문 목록 반환
        questions = PRD_QUESTIONS.get(detected["type"], PRD_QUESTIONS["generic"])
        result["prd_guide"] = {
            "detected_type": detected["type"],
            "confidence": detected["confidence"],
            "signals": detected["signals"],
            "template": detected["type"],
            "questions": questions,
            "instruction": f"""
## 🎯 PRD 작성 가이드

**감지된 프로젝트 타입**: {detected['description']} ({detected['type']})
**신뢰도**: {detected['confidence']}%

### Claude에게 지시사항

아래 질문들을 사용자에게 **대화형으로** 진행하세요:

{chr(10).join([f"{i+1}. **{q['section']}**: {q['question']}" + (f" ({q.get('example', '')})" if q.get('example') else "") for i, q in enumerate(questions)])}

### 진행 방법

1. 질문을 하나씩 또는 관련된 것끼리 묶어서 질문
2. 사용자 답변을 수집
3. 모든 답변을 받으면 `save_prd` 도구로 PRD 저장
4. 템플릿: `{detected['type']}` / 레이아웃: `standard` 권장

### 예시 대화

"안녕하세요! {detected['description']} 프로젝트시네요.
PRD를 같이 작성해볼까요? 먼저 몇 가지 질문드릴게요.

**{questions[0]['question']}**
{questions[0].get('example', '')}"
"""
        }

        result["next_steps"] = [
            "1. 위 질문들에 답변하여 PRD 작성",
            "2. 완료 후 `save_prd` 도구로 저장",
            "3. 다시 `start` 실행하여 검증"
        ]

    # 추가 docs 파일 체크
    optional_docs = {
        "ARCHITECTURE.md": "아키텍처 문서",
        "API.md": "API 문서",
        "CHANGELOG.md": "변경 이력"
    }

    result["optional_docs"] = {}
    for doc, desc in optional_docs.items():
        doc_path = docs_path / doc
        result["optional_docs"][doc] = {
            "exists": doc_path.exists(),
            "description": desc
        }

    return result


def _validate_prd(content: str) -> Dict[str, Any]:
    """
    PRD 내용을 검증합니다.

    필수 섹션:
    - 프로젝트 개요 (목적, 목표)
    - 기능 요구사항

    권장 섹션:
    - 기술 스펙
    - 데이터 모델
    - 테스트 계획
    """
    required_sections = [
        ("프로젝트 개요", ["목적", "목표"]),
        ("기능 요구사항", ["핵심 기능"]),
    ]

    recommended_sections = [
        "기술 스펙",
        "데이터 모델",
        "테스트 계획"
    ]

    missing_sections = []
    summary = {
        "sections_found": [],
        "has_goals": False,
        "has_features": False
    }

    # 필수 섹션 체크
    for section, subsections in required_sections:
        if section not in content:
            missing_sections.append(section)
        else:
            summary["sections_found"].append(section)

            # 내용이 있는지 체크 (템플릿 플레이스홀더가 아닌지)
            for sub in subsections:
                if sub in content:
                    # 플레이스홀더 체크
                    if sub == "목적" and "[이 프로젝트가 해결하려는 문제를 작성하세요]" in content:
                        missing_sections.append(f"{section} > {sub}")
                    elif sub == "목표" and "핵심 목표 1" in content:
                        pass  # 목표가 있으면 OK
                    else:
                        if section == "프로젝트 개요":
                            summary["has_goals"] = True

    # 기능 요구사항 체크
    if "기능 요구사항" in content:
        if "**기능 1**: 설명" not in content:
            summary["has_features"] = True

    # 권장 섹션 체크
    for section in recommended_sections:
        if section in content:
            summary["sections_found"].append(section)

    is_valid = len(missing_sections) == 0 and summary["has_goals"]

    return {
        "is_valid": is_valid,
        "missing_sections": missing_sections,
        "summary": summary
    }


def save_prd(
    path: str,
    content: str,
    project_name: str = "",
    project_type: str = ""
) -> Dict[str, Any]:
    """
    PRD 내용을 저장합니다.

    Claude가 사용자와 대화하며 수집한 정보를 바탕으로
    PRD를 작성한 후 이 도구로 저장합니다.

    Args:
        path: 프로젝트 루트 경로
        content: PRD 내용 (마크다운)
        project_name: 프로젝트 이름 (옵션, 헤더에 사용)
        project_type: 프로젝트 타입 (옵션, 메타데이터용)

    Returns:
        저장 결과
    """
    from datetime import datetime

    project_path = Path(path).resolve()
    docs_path = project_path / "docs"
    prd_path = docs_path / "PRD.md"

    result = {
        "status": "UNKNOWN",
        "prd_path": str(prd_path),
        "message": ""
    }

    # docs 폴더 생성
    if not docs_path.exists():
        try:
            docs_path.mkdir(parents=True)
        except Exception as e:
            result["status"] = "ERROR"
            result["message"] = f"docs 폴더 생성 실패: {e}"
            return result

    # PRD 헤더 추가 (없으면)
    if not content.strip().startswith("#"):
        today = datetime.now().strftime("%Y-%m-%d")
        name = project_name or project_path.name
        header = f"# {name} PRD\n\n> 작성일: {today}\n\n---\n\n"
        content = header + content

    # 저장
    try:
        prd_path.write_text(content, encoding="utf-8")
        result["status"] = "SAVED"
        result["message"] = f"✅ PRD가 저장되었습니다: {prd_path}"

        # 검증
        validation = _validate_prd(content)
        result["validation"] = validation

        if validation["is_valid"]:
            result["next_steps"] = [
                "PRD 저장 완료! 이제 코딩을 시작할 수 있습니다.",
                "`can_code` 도구로 확인하거나 바로 코딩을 시작하세요."
            ]
        else:
            result["next_steps"] = [
                f"PRD가 저장되었지만 일부 섹션이 부족합니다: {', '.join(validation['missing_sections'])}",
                "필요시 PRD를 보완하세요."
            ]

    except Exception as e:
        result["status"] = "ERROR"
        result["message"] = f"PRD 저장 실패: {e}"

    return result


def get_prd_questions(project_type: str = "generic") -> Dict[str, Any]:
    """
    특정 프로젝트 타입의 PRD 작성 질문 목록을 반환합니다.

    Args:
        project_type: 프로젝트 타입 (web-app, api, cli, chrome-ext, discord-bot, landing-page, generic)

    Returns:
        질문 목록 및 가이드
    """
    if project_type not in PRD_QUESTIONS:
        project_type = "generic"

    questions = PRD_QUESTIONS[project_type]
    description = PROJECT_TYPE_PATTERNS.get(project_type, {}).get("description", project_type)

    return {
        "project_type": project_type,
        "description": description,
        "questions": questions,
        "usage": f"""
## PRD 작성 질문 ({description})

아래 질문들을 사용자에게 진행하세요:

{chr(10).join([f"{i+1}. **{q['section']}**: {q['question']}" for i, q in enumerate(questions)])}

답변을 모두 수집한 후 PRD를 작성하고 `save_prd` 도구로 저장하세요.
"""
    }


# 간단한 버전 (can_code 대신 사용 가능)
def quick_start(path: str) -> str:
    """
    빠른 시작 - PRD 유무만 체크하고 안내 메시지 반환
    """
    result = start(path)

    if result["status"] == "READY":
        return f"✅ {result['project_name']} 프로젝트 준비 완료!\n\n코딩을 시작하세요."
    elif result["status"] == "NEED_PRD":
        guide = result.get("prd_guide", {})
        return f"📝 PRD 작성이 필요합니다.\n\n{guide.get('instruction', '')}"
    elif result["status"] == "INCOMPLETE":
        return f"⚠️ PRD 작성 미완료\n\n누락된 섹션: {', '.join(result.get('missing_sections', []))}\n\n다음 단계:\n" + "\n".join(result["next_steps"])
    else:
        return f"❌ 오류: {result['message']}"
