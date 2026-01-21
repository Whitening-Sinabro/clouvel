# Clouvel Start Tool (Free)
# 프로젝트 온보딩 + PRD 강제

import os
from pathlib import Path
from typing import Dict, Any

# PRD 템플릿
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


def start(path: str, project_name: str = "") -> Dict[str, Any]:
    """
    프로젝트 온보딩을 시작합니다.

    1. docs 폴더 확인/생성
    2. PRD.md 존재 여부 체크
    3. 없으면 템플릿 생성 + 작성 안내
    4. 있으면 구조 검증 + 다음 단계 안내

    Args:
        path: 프로젝트 루트 경로
        project_name: 프로젝트 이름 (옵션)

    Returns:
        온보딩 결과 및 다음 단계 안내
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
                "2. 필요시 `init_planning` 도구로 작업 계획 수립",
                "3. 코딩 시작!"
            ]
            result["prd_summary"] = validation["summary"]
        else:
            result["status"] = "INCOMPLETE"
            result["message"] = "⚠️ PRD가 있지만 일부 섹션이 비어있습니다."
            result["missing_sections"] = validation["missing_sections"]
            result["next_steps"] = [
                f"1. PRD의 다음 섹션을 작성하세요: {', '.join(validation['missing_sections'])}",
                "2. 작성 후 다시 `/start` 실행"
            ]
    else:
        # PRD 템플릿 생성
        today = datetime.now().strftime("%Y-%m-%d")
        prd_content = PRD_TEMPLATE.format(
            project_name=project_name,
            date=today
        )

        try:
            prd_path.write_text(prd_content, encoding="utf-8")
            result["created_files"].append("docs/PRD.md")
            result["status"] = "CREATED"
            result["message"] = f"📝 PRD 템플릿이 생성되었습니다: {prd_path}"
            result["next_steps"] = [
                "1. docs/PRD.md 파일을 열고 프로젝트 정보를 작성하세요",
                "2. 최소한 '프로젝트 개요'와 '기능 요구사항' 섹션은 필수입니다",
                "3. 작성 완료 후 다시 `/start` 실행하여 검증하세요"
            ]
        except Exception as e:
            result["status"] = "ERROR"
            result["message"] = f"PRD 생성 실패: {e}"
            return result

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


# 간단한 버전 (can_code 대신 사용 가능)
def quick_start(path: str) -> str:
    """
    빠른 시작 - PRD 유무만 체크하고 안내 메시지 반환
    """
    result = start(path)

    if result["status"] == "READY":
        return f"✅ {result['project_name']} 프로젝트 준비 완료!\n\n코딩을 시작하세요."
    elif result["status"] == "CREATED":
        return f"📝 PRD 템플릿 생성됨\n\n{result['message']}\n\n다음 단계:\n" + "\n".join(result["next_steps"])
    elif result["status"] == "INCOMPLETE":
        return f"⚠️ PRD 작성 미완료\n\n누락된 섹션: {', '.join(result.get('missing_sections', []))}\n\n다음 단계:\n" + "\n".join(result["next_steps"])
    else:
        return f"❌ 오류: {result['message']}"
