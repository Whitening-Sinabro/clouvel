# CLI 템플릿

> 커맨드라인 도구 (Click, Typer, Commander 등)

---

## 자동 감지 조건

다음 중 하나라도 있으면 `cli`로 감지:

- `bin/` 폴더
- `cli.py`, `cli.js`
- `__main__.py`
- `pyproject.toml`에 `[project.scripts]`
- 의존성: `commander`, `yargs`, `click`, `typer`, `argparse`

---

## PRD 질문 가이드

| 순서 | 섹션         | 질문                        | 예시                       |
| ---- | ------------ | --------------------------- | -------------------------- |
| 1    | summary      | 이 CLI가 해결하려는 문제는? | 프로젝트 초기화가 반복적임 |
| 2    | target       | 주요 사용자는?              | 백엔드 개발자              |
| 3    | commands     | 핵심 명령어 3-5개           | init, run, build, deploy   |
| 4    | options      | 주요 옵션/플래그            | --verbose, --config        |
| 5    | out_of_scope | 제외할 기능                 | GUI, 자동 업데이트         |

---

## PRD 예시

````markdown
# mycli PRD

## 1. 프로젝트 개요

### 1.1 목적

프로젝트 초기화 및 배포 자동화 CLI 도구

### 1.2 타겟 사용자

- 백엔드 개발자
- DevOps 엔지니어

### 1.3 성공 지표

| 지표         | 목표        |
| ------------ | ----------- |
| 설치 수      | 100+ (PyPI) |
| GitHub Stars | 50+         |

---

## 2. 명령어 스펙

### 2.1 핵심 명령어

| 명령어   | 설명            | 예시                    |
| -------- | --------------- | ----------------------- |
| `init`   | 프로젝트 초기화 | `mycli init myapp`      |
| `run`    | 개발 서버 실행  | `mycli run --port 3000` |
| `build`  | 프로덕션 빌드   | `mycli build`           |
| `deploy` | 배포            | `mycli deploy --prod`   |

### 2.2 글로벌 옵션

| 옵션        | 단축 | 설명                    |
| ----------- | ---- | ----------------------- |
| `--verbose` | `-v` | 상세 로그 출력          |
| `--config`  | `-c` | 설정 파일 경로          |
| `--dry-run` |      | 실제 실행 없이 미리보기 |
| `--help`    | `-h` | 도움말                  |

### 2.3 설정 파일

```yaml
# mycli.yaml
name: myapp
version: 1.0.0
deploy:
  target: railway
  region: ap-northeast-1
```
````

---

## 3. 제외 범위

- GUI 인터페이스
- 자동 업데이트
- Windows 지원 (v2에서)

---

## 4. 기술 스택

- Language: Python 3.10+
- CLI Framework: Typer
- 배포: PyPI

```

---

## 체크리스트

- [ ] 명령어 구조가 직관적인가?
- [ ] 도움말이 충분한가?
- [ ] 에러 메시지가 명확한가?
- [ ] 설정 파일 포맷이 결정되었는가?
- [ ] 배포 방법이 결정되었는가? (PyPI/npm)
```
