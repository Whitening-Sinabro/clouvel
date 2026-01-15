import re
from pathlib import Path
from datetime import datetime
from src.models.docs import (
    DocFile,
    ScanResponse,
    DetectedDoc,
    MissingDoc,
    AnalyzeResponse,
)


def scan_docs(path: str) -> ScanResponse:
    """주어진 경로의 docs 디렉토리를 스캔하여 파일 목록 반환"""
    docs_path = Path(path)

    if not docs_path.exists():
        raise FileNotFoundError(f"경로를 찾을 수 없습니다: {path}")

    if not docs_path.is_dir():
        raise NotADirectoryError(f"디렉토리가 아닙니다: {path}")

    files: list[DocFile] = []

    for file_path in docs_path.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            files.append(DocFile(
                name=file_path.name,
                size=stat.st_size,
                modified_at=datetime.fromtimestamp(stat.st_mtime),
                extension=file_path.suffix.lower(),
            ))

    files.sort(key=lambda f: f.name)

    return ScanResponse(
        path=str(docs_path.resolve()),
        total_files=len(files),
        files=files,
    )


# 필수 문서 정의
REQUIRED_DOCS = [
    {
        "type": "prd",
        "name": "PRD (Product Requirements Document)",
        "description": "제품 요구사항 정의서",
        "patterns": [r"prd", r"product.?requirement"],
        "priority": "critical",
    },
    {
        "type": "architecture",
        "name": "아키텍처 문서",
        "description": "모듈/시스템 아키텍처 설계",
        "patterns": [r"architect", r"module", r"system.?design"],
        "priority": "critical",
    },
    {
        "type": "api_spec",
        "name": "API 스펙",
        "description": "API 명세서 (OpenAPI/Swagger)",
        "patterns": [r"api", r"swagger", r"openapi"],
        "priority": "critical",
    },
    {
        "type": "db_schema",
        "name": "DB 스키마",
        "description": "데이터베이스 스키마 정의",
        "patterns": [r"schema", r"database", r"db", r"erd"],
        "priority": "critical",
    },
    {
        "type": "verification",
        "name": "검증 계획",
        "description": "테스트/검증 계획서",
        "patterns": [r"verif", r"test.?plan", r"qa"],
        "priority": "critical",
    },
    {
        "type": "dev_checklist",
        "name": "개발 체크리스트",
        "description": "개발 진행 체크리스트",
        "patterns": [r"checklist", r"dev.?guide"],
        "priority": "recommended",
    },
    {
        "type": "env_config",
        "name": "환경 설정",
        "description": "환경 변수 및 설정 예시",
        "patterns": [r"env", r"config", r"\.env"],
        "priority": "recommended",
    },
    {
        "type": "readme",
        "name": "README",
        "description": "프로젝트 소개 및 시작 가이드",
        "patterns": [r"readme"],
        "priority": "recommended",
    },
    {
        "type": "claude_md",
        "name": "CLAUDE.md",
        "description": "AI 어시스턴트용 프로젝트 컨텍스트",
        "patterns": [r"claude"],
        "priority": "optional",
    },
]


def analyze_docs(path: str) -> AnalyzeResponse:
    """docs 디렉토리를 분석하여 필수 문서 존재 여부 확인"""
    scan_result = scan_docs(path)

    detected: list[DetectedDoc] = []
    detected_types: set[str] = set()

    for file in scan_result.files:
        file_lower = file.name.lower()

        for req in REQUIRED_DOCS:
            for pattern in req["patterns"]:
                if re.search(pattern, file_lower, re.IGNORECASE):
                    # 이미 같은 타입이 감지되었으면 confidence 비교
                    existing = next(
                        (d for d in detected if d.type == req["type"]),
                        None
                    )
                    confidence = _calculate_confidence(file, req)

                    if existing is None or confidence > existing.confidence:
                        if existing:
                            detected.remove(existing)
                        detected.append(DetectedDoc(
                            type=req["type"],
                            file=file,
                            confidence=confidence,
                        ))
                        detected_types.add(req["type"])
                    break

    # 빠진 문서 찾기
    missing: list[MissingDoc] = []
    for req in REQUIRED_DOCS:
        if req["type"] not in detected_types:
            missing.append(MissingDoc(
                type=req["type"],
                name=req["name"],
                description=req["description"],
                priority=req["priority"],
            ))

    # 커버리지 계산 (critical 문서 기준)
    critical_docs = [r for r in REQUIRED_DOCS if r["priority"] == "critical"]
    critical_detected = len([d for d in detected if d.type in [r["type"] for r in critical_docs]])
    coverage = critical_detected / len(critical_docs) if critical_docs else 1.0

    # 요약 생성
    summary = _generate_summary(detected, missing, coverage)

    return AnalyzeResponse(
        path=scan_result.path,
        detected=detected,
        missing=missing,
        coverage=coverage,
        summary=summary,
    )


def _calculate_confidence(file: DocFile, req: dict) -> float:
    """파일이 해당 문서 유형과 얼마나 일치하는지 계산"""
    confidence = 0.5
    file_lower = file.name.lower()

    # 파일명에 타입이 정확히 포함되면 높은 신뢰도
    if req["type"].replace("_", "") in file_lower.replace("-", "").replace("_", ""):
        confidence += 0.3

    # 마크다운 파일이면 추가 점수
    if file.extension in [".md", ".markdown"]:
        confidence += 0.1

    # YAML/SQL 등 특정 확장자면 추가 점수
    if req["type"] == "api_spec" and file.extension in [".yaml", ".yml", ".json"]:
        confidence += 0.2
    if req["type"] == "db_schema" and file.extension == ".sql":
        confidence += 0.2
    if req["type"] == "env_config" and file.extension == ".env":
        confidence += 0.2

    return min(confidence, 1.0)


def _generate_summary(
    detected: list[DetectedDoc],
    missing: list[MissingDoc],
    coverage: float,
) -> str:
    """분석 결과 요약 생성"""
    critical_missing = [m for m in missing if m.priority == "critical"]

    if coverage >= 1.0:
        return "필수 문서 다 있음"
    elif coverage >= 0.8:
        missing_names = ", ".join(m.type for m in critical_missing)
        return f"거의 다 있는데 {missing_names} 빠짐"
    elif coverage >= 0.5:
        missing_names = ", ".join(m.type for m in critical_missing)
        return f"{missing_names} 없음. 문서화 먼저"
    else:
        return f"문서 거의 없음. {len(critical_missing)}개 빠짐"
