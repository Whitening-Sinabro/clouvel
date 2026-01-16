# Clouvel

바이브코딩 프로세스를 강제하는 API + Agent 도구

## 기술 스택
- Python 3.11+
- FastAPI
- Uvicorn (포트 8000)

## 명령어
```bash
# 서버 실행
uvicorn src.main:app --reload --port 8000

# 테스트
pytest tests/
```

## 프로젝트 구조
```
src/
├── main.py          # FastAPI 앱
├── api/             # 라우터
├── services/        # 비즈니스 로직
└── models/          # Pydantic 모델
```

## 핵심 기능
1. /docs/scan - 프로젝트 docs 스캔
2. /docs/analyze - 빠진 것 감지 (PRD, 검증 등)
3. /guide/prd - PRD 작성 가이드
4. /guide/verify - Boris 검증 체크리스트

## 규칙
- 타입 힌트 필수
- Pydantic 모델 사용
- 에러는 HTTPException으로 처리


## Clouvel 규칙 (자동 생성)

> 이 규칙은 Clouvel이 자동으로 추가했습니다.

### 필수 준수 사항
1. **코드 작성 전 문서 체크**: Edit/Write 도구 사용 전 반드시 `can_code` 도구를 먼저 호출
2. **can_code 실패 시 코딩 금지**: 필수 문서가 없으면 PRD 작성부터
3. **PRD가 법**: docs/PRD.md에 없는 기능은 구현하지 않음
