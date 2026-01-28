# Clouvel Hooks Integration Guide

> **v2.0**: Proactive MCP - 자동 PRD 체크, 드리프트 감지

## 개요

Claude Code hooks를 사용하면 Clouvel이 **자동으로** 작동합니다:
- 코드 작성 전 PRD 체크
- 주기적 드리프트 감지
- 에러 패턴 감시

## 빠른 시작

### 1. CLI 명령어 확인

```bash
# PRD 체크 (hooks용)
clouvel can_code --path ./docs --silent

# 드리프트 체크 (Pro)
clouvel drift_check --path . --silent
```

### 2. Claude Code Hooks 설정

프로젝트 루트에 `.claude/settings.local.json` 생성:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "clouvel can_code --path ./docs --silent"
          }
        ]
      }
    ]
  }
}
```

## Hook 종류

### PreToolUse (코드 작성 전)

**목적**: Edit/Write 도구 사용 전 PRD 체크

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "clouvel can_code --path ./docs --silent"
          }
        ]
      }
    ]
  }
}
```

**동작**:
- Exit code 0 → 진행
- Exit code 1 (BLOCK) → 중단

### PostToolUse (코드 작성 후)

**목적**: 드리프트 감지 (Pro)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "clouvel drift_check --path . --silent"
          }
        ]
      }
    ]
  }
}
```

## CLI 옵션

### `clouvel can_code`

| 옵션 | 설명 |
|------|------|
| `--path`, `-p` | docs 폴더 경로 (기본: `.`) |
| `--silent`, `-s` | Exit code만 반환 (출력 없음) |

**Exit codes**:
- `0`: PASS 또는 WARN
- `1`: BLOCK (PRD 없음)

### `clouvel drift_check` (Pro)

| 옵션 | 설명 |
|------|------|
| `--path`, `-p` | 프로젝트 루트 경로 |
| `--silent`, `-s` | 최소 출력 (`OK:0` 또는 `DRIFT:75`) |

**Exit codes**:
- `0`: OK (드리프트 없음)
- `1`: DRIFT (목표 이탈 감지)

## 전체 설정 예시

### Free 버전 (자동 PRD 체크만)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "clouvel can_code --path ./docs --silent"
          }
        ]
      }
    ]
  }
}
```

### Pro 버전 (전체 기능)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "clouvel can_code --path ./docs --silent"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "clouvel drift_check --path . --silent"
          }
        ]
      }
    ]
  }
}
```

## 설정 파일 위치

| 범위 | 경로 |
|------|------|
| 프로젝트 | `.claude/settings.local.json` |
| 글로벌 | `~/.claude/settings.json` |

프로젝트 설정이 글로벌 설정보다 우선합니다.

## 문제 해결

### "clouvel: command not found"

```bash
# clouvel이 PATH에 있는지 확인
which clouvel

# 또는 전체 경로 사용
python -m clouvel can_code --path ./docs --silent
```

### Hook이 실행 안 됨

1. `.claude/settings.local.json` 위치 확인 (프로젝트 루트)
2. JSON 문법 확인
3. matcher 패턴 확인 (`Edit|Write` vs `Edit\|Write`)

### BLOCK이 너무 자주 발생

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "clouvel can_code --path ./docs"
          }
        ]
      }
    ]
  }
}
```

`--silent` 제거하면 상세 메시지 출력됩니다.

## 티어별 기능

| 기능 | Free | Pro |
|------|------|-----|
| 자동 PRD 체크 | ✅ | ✅ |
| 드리프트 감지 | ❌ | ✅ |
| 에러 패턴 감시 | ❌ | ✅ |
| 진행 리마인드 | ❌ | ✅ |

## 관련 문서

- [PRD.md](./PRD.md) - v2.0 Proactive MCP 스펙
- [README.md](../README.md) - 설치 가이드
