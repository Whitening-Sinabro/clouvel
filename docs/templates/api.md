# API 템플릿

> REST API 서버 (FastAPI, Express, Flask 등)

---

## 자동 감지 조건

다음 중 하나라도 있으면 `api`로 감지:

- `server.py`, `server.js`
- `app.py`, `main.py`, `index.js`
- 의존성: `express`, `fastapi`, `flask`, `django`, `koa`, `hono`, `gin`

---

## PRD 질문 가이드

| 순서 | 섹션         | 질문                        | 예시                                         |
| ---- | ------------ | --------------------------- | -------------------------------------------- |
| 1    | summary      | 이 API가 해결하려는 문제는? | 프론트엔드에서 데이터 접근 필요              |
| 2    | clients      | 주요 API 소비자는?          | 웹 프론트엔드, 모바일 앱                     |
| 3    | endpoints    | 핵심 엔드포인트 5개         | POST /auth/login, GET /users                 |
| 4    | auth         | 인증 방식은?                | JWT Bearer Token                             |
| 5    | side_effects | 기존 시스템/데이터에 영향?  | 기존 API 호환성, DB 스키마 변경, 캐시 무효화 |
| 6    | out_of_scope | 제외할 것은?                | GraphQL, WebSocket                           |

---

## PRD 예시

````markdown
# Todo API PRD

## 1. 프로젝트 개요

### 1.1 목적

Todo 앱을 위한 백엔드 REST API

### 1.2 API 소비자

- 웹 프론트엔드 (React)
- 추후 모바일 앱

### 1.3 성공 지표

| 지표      | 목표          |
| --------- | ------------- |
| 응답 시간 | < 200ms (p95) |
| 가용성    | 99.9%         |

---

## 2. API 스펙

### 2.1 인증

- 방식: JWT Bearer Token
- 만료: 24시간
- Refresh Token: 7일

### 2.2 핵심 엔드포인트

| Method | Path             | 설명      |
| ------ | ---------------- | --------- |
| POST   | `/auth/register` | 회원가입  |
| POST   | `/auth/login`    | 로그인    |
| GET    | `/todos`         | 목록 조회 |
| POST   | `/todos`         | 생성      |
| PATCH  | `/todos/:id`     | 수정      |
| DELETE | `/todos/:id`     | 삭제      |

### 2.3 응답 형식

```json
{
  "success": true,
  "data": {...},
  "error": null
}
```
````

### 2.4 에러 코드

| 코드 | 설명        |
| ---- | ----------- |
| 400  | 잘못된 요청 |
| 401  | 인증 필요   |
| 404  | 리소스 없음 |
| 500  | 서버 에러   |

---

## 3. 제외 범위

- GraphQL 지원
- WebSocket 실시간 동기화
- 파일 업로드

---

## 4. 기술 스택

- Framework: FastAPI
- DB: PostgreSQL
- ORM: SQLAlchemy
- 배포: Railway

```

---

## 체크리스트

- [ ] 핵심 엔드포인트가 정의되었는가?
- [ ] 인증 방식이 결정되었는가?
- [ ] 응답 형식이 통일되었는가?
- [ ] 에러 처리가 정의되었는가?
- [ ] DB 스키마가 설계되었는가?
```
