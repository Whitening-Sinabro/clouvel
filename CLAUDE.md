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
