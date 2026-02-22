# -*- coding: utf-8 -*-
"""서버사이드 콘텐츠 API 클라이언트

패키지 추출 공격 방어:
- 템플릿/커맨드가 로컬에 없음
- 서버에서 실시간으로 가져옴
- 라이선스 + 7일 + machine_id 검증 후에만 제공

DEV_MODE:
- CLOUVEL_DEV=1 환경변수로 활성화
- 로컬 shovel 디렉토리에서 콘텐츠 로드
- 테스트/개발 용도
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

# 라이선스 모듈 import (Pro 버전이 없으면 Free stub 사용)
try:
    from .license import get_machine_id
except ImportError:
    from .license_free import get_machine_id

# 개발 모드 (표준 is_developer() 사용)
def _is_dev_mode() -> bool:
    try:
        from .licensing.core import is_developer
        return is_developer()
    except ImportError:
        # Fallback: CLOUVEL_DEV=1 (통합된 개발 모드 변수)
        return os.environ.get("CLOUVEL_DEV") == "1"

DEV_MODE = _is_dev_mode()

# 클라이언트 버전 (서버에서 검증됨)
CLIENT_VERSION = "1.2.0"

# 콘텐츠 서버 URL
CONTENT_SERVER_URL = os.environ.get(
    "CLOUVEL_CONTENT_SERVER_URL",
    "https://clouvel-license-webhook.vnddns999.workers.dev"
)

# 로컬 캐시 경로 (임시, 24시간만 유효)
CONTENT_CACHE_FILE = Path.home() / ".clouvel-content-cache"
CACHE_VALID_HOURS = 24

# 로컬 Shovel 디렉토리 (DEV_MODE용)
# site-packages/clouvel_pro/content_api.py → site-packages/shovel
SHOVEL_DIR = Path(__file__).parent.parent / "shovel"


def _load_local_shovel_content() -> dict:
    """DEV_MODE: 로컬 shovel 디렉토리에서 콘텐츠 로드"""
    if not SHOVEL_DIR.exists():
        return None

    content = {
        "claude_md": "",
        "commands": {},
        "templates": {},
        "config": {},
        "settings": {},
        "roles": {},
        "role_triggers": ""
    }

    # CLAUDE.md
    claude_md_path = SHOVEL_DIR / "CLAUDE.md"
    if claude_md_path.exists():
        content["claude_md"] = claude_md_path.read_text(encoding="utf-8")

    # Commands
    commands_dir = SHOVEL_DIR / ".claude" / "commands"
    if commands_dir.exists():
        for cmd_file in commands_dir.glob("*.md"):
            content["commands"][cmd_file.stem] = cmd_file.read_text(encoding="utf-8")

    # Templates
    templates_dir = SHOVEL_DIR / ".claude" / "templates"
    if templates_dir.exists():
        for tpl_file in templates_dir.glob("*.md"):
            content["templates"][tpl_file.stem] = tpl_file.read_text(encoding="utf-8")

    # Config
    config_dir = SHOVEL_DIR / ".claude" / "config"
    if config_dir.exists():
        for cfg_file in config_dir.glob("*"):
            if cfg_file.is_file():
                try:
                    content["config"][cfg_file.name] = cfg_file.read_text(encoding="utf-8")
                except Exception:
                    pass

    # Settings
    settings_path = SHOVEL_DIR / ".claude" / "settings.json"
    if settings_path.exists():
        try:
            content["settings"] = json.loads(settings_path.read_text(encoding="utf-8"))
        except Exception:
            content["settings"] = {}

    # Roles (C-Level 역할 정의)
    roles_dir = SHOVEL_DIR / "roles"
    if roles_dir.exists():
        for role_file in roles_dir.glob("*.yaml"):
            try:
                content["roles"][role_file.stem] = role_file.read_text(encoding="utf-8")
            except Exception:
                pass

    # Role Triggers (컨텍스트 → 역할 매핑)
    triggers_path = SHOVEL_DIR / "role-triggers.yaml"
    if triggers_path.exists():
        try:
            content["role_triggers"] = triggers_path.read_text(encoding="utf-8")
        except Exception:
            pass

    return content


def _load_license_info() -> dict:
    """라이선스 파일에서 정보 로드"""
    license_file = Path.home() / ".clouvel-license"
    if not license_file.exists():
        return None

    try:
        return json.loads(license_file.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_cached_content() -> dict:
    """로컬 캐시에서 콘텐츠 로드 (24시간 유효)"""
    if not CONTENT_CACHE_FILE.exists():
        return None

    try:
        data = json.loads(CONTENT_CACHE_FILE.read_text(encoding="utf-8"))

        # 캐시 유효성 확인
        cached_at = data.get("cached_at")
        if cached_at:
            cached_time = datetime.fromisoformat(cached_at)
            if datetime.now() - cached_time < timedelta(hours=CACHE_VALID_HOURS):
                return data.get("content")

        return None
    except Exception:
        return None


def _save_content_cache(content: dict):
    """콘텐츠 캐시 저장"""
    cache_data = {
        "cached_at": datetime.now().isoformat(),
        "content": content
    }
    CONTENT_CACHE_FILE.write_text(json.dumps(cache_data, ensure_ascii=False), encoding="utf-8")


def fetch_content_bundle() -> dict:
    """서버에서 프리미엄 콘텐츠 번들 가져오기

    Returns:
        {
            "success": True,
            "version": "4.0.0",
            "content": {
                "claude_md": "...",
                "commands": {...},
                "templates": {...},
                "config": {...},
                "settings": {...}
            }
        }

        또는 에러:
        {
            "success": False,
            "error": "에러 코드",
            "message": "에러 메시지"
        }
    """
    # 0. DEV_MODE: 로컬 콘텐츠 사용
    if DEV_MODE:
        local_content = _load_local_shovel_content()
        if local_content:
            return {
                "success": True,
                "version": "dev-local",
                "content": local_content,
                "cached": False,
                "dev_mode": True
            }
        else:
            return {
                "success": False,
                "error": "dev_no_content",
                "message": "DEV_MODE: 로컬 shovel 디렉토리를 찾을 수 없습니다."
            }

    # 1. 캐시 확인
    cached = _load_cached_content()
    if cached:
        return {
            "success": True,
            "version": cached.get("version", "cached"),
            "content": cached,
            "cached": True
        }

    # 2. 라이선스 정보 로드
    license_info = _load_license_info()
    if not license_info:
        return {
            "success": False,
            "error": "no_license",
            "message": "라이선스가 활성화되지 않았습니다. activate_license를 먼저 실행하세요."
        }

    license_key = license_info.get("license_key")
    activated_at = license_info.get("activated_at")

    if not license_key:
        return {
            "success": False,
            "error": "invalid_license",
            "message": "라이선스 키를 찾을 수 없습니다."
        }

    if not activated_at:
        return {
            "success": False,
            "error": "no_activation_date",
            "message": "활성화 날짜를 찾을 수 없습니다. 라이선스를 다시 활성화하세요."
        }

    # 3. 머신 ID 확인
    machine_id = license_info.get("machine_id") or get_machine_id()

    # 4. 서버에 요청 (machine_id + client_version 포함)
    try:
        response = requests.post(
            f"{CONTENT_SERVER_URL}/content/bundle",
            json={
                "license_key": license_key,
                "activated_at": activated_at,
                "machine_id": machine_id,
                "client_version": CLIENT_VERSION
            },
            timeout=30
        )

        data = response.json()

        if response.status_code == 200 and data.get("success"):
            # 캐시 저장
            _save_content_cache(data.get("content"))
            return {
                "success": True,
                "version": data.get("version"),
                "content": data.get("content"),
                "cached": False
            }

        # 에러 응답
        return {
            "success": False,
            "error": data.get("error", "unknown"),
            "message": data.get("message", "콘텐츠를 가져올 수 없습니다."),
            "days_remaining": data.get("days_remaining"),
            "unlock_date": data.get("unlock_date")
        }

    except requests.exceptions.Timeout:
        # 타임아웃 시 캐시 시도 (만료되어도)
        if CONTENT_CACHE_FILE.exists():
            try:
                data = json.loads(CONTENT_CACHE_FILE.read_text(encoding="utf-8"))
                content = data.get("content")
                if content:
                    return {
                        "success": True,
                        "version": "cached-offline",
                        "content": content,
                        "cached": True,
                        "offline": True
                    }
            except Exception:
                pass

        return {
            "success": False,
            "error": "timeout",
            "message": "서버 연결 시간 초과. 인터넷 연결을 확인하세요."
        }

    except requests.exceptions.ConnectionError:
        # 연결 실패 시 캐시 시도
        if CONTENT_CACHE_FILE.exists():
            try:
                data = json.loads(CONTENT_CACHE_FILE.read_text(encoding="utf-8"))
                content = data.get("content")
                if content:
                    return {
                        "success": True,
                        "version": "cached-offline",
                        "content": content,
                        "cached": True,
                        "offline": True
                    }
            except Exception:
                pass

        return {
            "success": False,
            "error": "connection_error",
            "message": "서버에 연결할 수 없습니다. 인터넷 연결을 확인하세요."
        }

    except Exception as e:
        return {
            "success": False,
            "error": "unknown",
            "message": f"콘텐츠 로드 오류: {str(e)}"
        }


def fetch_content_manifest() -> dict:
    """서버에서 콘텐츠 목록만 가져오기 (내용 없음)

    7일 잠금 상관없이 목록은 볼 수 있음 (티저 용도)
    """
    license_info = _load_license_info()
    if not license_info:
        return {
            "success": False,
            "error": "no_license",
            "message": "라이선스가 필요합니다."
        }

    license_key = license_info.get("license_key")

    try:
        response = requests.get(
            f"{CONTENT_SERVER_URL}/content/manifest",
            headers={"Authorization": f"Bearer {license_key}"},
            timeout=10
        )

        if response.status_code == 200:
            return {
                "success": True,
                **response.json()
            }

        data = response.json()
        return {
            "success": False,
            "error": data.get("error", "unknown"),
            "message": data.get("message", "목록을 가져올 수 없습니다.")
        }

    except Exception as e:
        return {
            "success": False,
            "error": "request_failed",
            "message": str(e)
        }


def clear_content_cache():
    """콘텐츠 캐시 삭제"""
    if CONTENT_CACHE_FILE.exists():
        CONTENT_CACHE_FILE.unlink()


def get_cache_status() -> dict:
    """캐시 상태 확인"""
    if not CONTENT_CACHE_FILE.exists():
        return {"cached": False}

    try:
        data = json.loads(CONTENT_CACHE_FILE.read_text(encoding="utf-8"))
        cached_at = data.get("cached_at")
        if cached_at:
            cached_time = datetime.fromisoformat(cached_at)
            age_hours = (datetime.now() - cached_time).total_seconds() / 3600
            return {
                "cached": True,
                "cached_at": cached_at,
                "age_hours": round(age_hours, 1),
                "valid": age_hours < CACHE_VALID_HOURS
            }
    except Exception:
        pass

    return {"cached": False}
