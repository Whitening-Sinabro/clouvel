# -*- coding: utf-8 -*-
"""
Clouvel Pro 다운로더

라이선스 검증 후 S3에서 Pro 코드를 다운로드하여 설치합니다.

사용법:
    from clouvel.pro_downloader import download_pro, install_pro

    # 단일 모듈 다운로드
    download_pro("manager")

    # 전체 Pro 설치
    install_pro()
"""

import os
import json
import zipfile
import shutil
import tempfile
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    import requests
except ImportError:
    requests = None

# 설정
DOWNLOAD_API_URL = os.environ.get(
    "CLOUVEL_DOWNLOAD_API",
    "https://clouvel-pro-download.vnddns999.workers.dev"
)

# Worker 배포 완료: 2025-01-23
# Version ID: 2d43d994-df4a-4c26-a523-6c8440d007cb

# Pro 모듈 목록
PRO_MODULES = [
    "manager",
    "ship",
    "errors",
    "license",
    "context",
    "shovel",
    "team",
    "roles",
    "security",
]

# 설치 경로 (site-packages/clouvel)
def get_install_path() -> Path:
    """clouvel 패키지 설치 경로 반환"""
    import clouvel
    return Path(clouvel.__file__).parent


def get_cached_license_key() -> Optional[str]:
    """캐시된 라이선스 키 반환"""
    license_file = Path.home() / ".clouvel-license"
    if license_file.exists():
        try:
            data = json.loads(license_file.read_text(encoding="utf-8"))
            return data.get("license_key")
        except Exception:
            pass
    return os.environ.get("CLOUVEL_LICENSE")


def download_file(url: str, dest_path: Path, max_retries: int = 3) -> bool:
    """URL에서 파일 다운로드 (재시도 지원)"""
    if requests is None:
        print("requests 패키지가 필요합니다: pip install requests")
        return False

    import time

    for attempt in range(max_retries):
        try:
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"  타임아웃, 재시도 중... ({attempt + 1}/{max_retries})")
                time.sleep(2 ** attempt)  # 지수 백오프
            else:
                print("다운로드 실패: 연결 시간 초과")
                return False
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                print(f"  연결 실패, 재시도 중... ({attempt + 1}/{max_retries})")
                time.sleep(2 ** attempt)
            else:
                print("다운로드 실패: 네트워크 연결 오류")
                return False
        except Exception as e:
            print(f"다운로드 실패: {e}")
            # 부분 다운로드 파일 삭제
            if dest_path.exists():
                dest_path.unlink()
            return False

    return False


def verify_hash(file_path: Path, expected_hash: str) -> bool:
    """파일 해시 검증"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    actual_hash = sha256.hexdigest()
    return actual_hash == expected_hash


def get_download_url(
    license_key: str,
    file_name: str,
    version: Optional[str] = None,
    max_retries: int = 3
) -> Dict[str, Any]:
    """Worker API에서 다운로드 URL 요청 (재시도 지원)"""
    if requests is None:
        return {"error": "requests 패키지가 필요합니다"}

    import time

    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{DOWNLOAD_API_URL}/download",
                json={
                    "license_key": license_key,
                    "file": file_name,
                    "version": version
                },
                timeout=15
            )

            return response.json()

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return {"error": "연결 시간 초과 (재시도 실패)"}
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return {"error": "네트워크 연결 실패 (재시도 실패)"}
        except Exception as e:
            return {"error": str(e)}

    return {"error": "알 수 없는 오류"}


def download_pro(
    module_name: str,
    license_key: Optional[str] = None,
    version: Optional[str] = None,
    install: bool = True
) -> Dict[str, Any]:
    """
    Pro 모듈 다운로드 및 설치

    Args:
        module_name: 모듈 이름 (manager, ship, errors 등)
        license_key: 라이선스 키 (없으면 캐시에서)
        version: 버전 (없으면 latest)
        install: 다운로드 후 자동 설치 여부

    Returns:
        {
            "success": True/False,
            "module": "manager",
            "version": "1.3.8",
            "installed_path": "/path/to/clouvel/tools/manager/"
        }
    """
    result = {
        "success": False,
        "module": module_name,
        "version": None,
        "installed_path": None
    }

    # 라이선스 키 확인
    key = license_key or get_cached_license_key()
    if not key:
        result["error"] = "라이선스 키가 없습니다. clouvel activate <key>로 활성화하세요."
        return result

    # 모듈 확인
    if module_name not in PRO_MODULES:
        result["error"] = f"알 수 없는 모듈: {module_name}. 사용 가능: {PRO_MODULES}"
        return result

    print(f"다운로드 중: {module_name}...")

    # 다운로드 URL 요청
    url_result = get_download_url(key, module_name, version)

    if "error" in url_result:
        result["error"] = url_result["error"]
        return result

    if url_result.get("status") != "success":
        result["error"] = url_result.get("message", "다운로드 URL 획득 실패")
        return result

    download_url = url_result["download_url"]
    result["version"] = url_result.get("version")

    # 임시 디렉토리에 다운로드
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_path = temp_path / f"{module_name}.zip"

        # 다운로드
        if not download_file(download_url, zip_path):
            result["error"] = "파일 다운로드 실패"
            return result

        print(f"  다운로드 완료: {zip_path.stat().st_size:,} bytes")

        # 압축 해제
        extract_path = temp_path / "extracted"
        extract_path.mkdir()

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_path)
        except Exception as e:
            result["error"] = f"압축 해제 실패: {e}"
            return result

        # 설치
        if install:
            install_result = install_module(module_name, extract_path)
            if not install_result["success"]:
                result["error"] = install_result.get("error", "설치 실패")
                return result
            result["installed_path"] = install_result["installed_path"]

    result["success"] = True
    print(f"  설치 완료: {result.get('installed_path', 'N/A')}")
    return result


def install_module(module_name: str, source_path: Path) -> Dict[str, Any]:
    """
    다운로드된 모듈을 site-packages에 설치

    Args:
        module_name: 모듈 이름
        source_path: 압축 해제된 소스 경로

    Returns:
        {"success": True/False, "installed_path": "..."}
    """
    result = {"success": False, "installed_path": None}

    install_base = get_install_path()

    # 모듈별 설치 경로 결정
    if module_name == "manager":
        dest_path = install_base / "tools" / "manager"
        source_dir = source_path / "manager"
    elif module_name == "license":
        dest_path = install_base / "license.py"
        source_file = list(source_path.glob("*.py"))[0] if list(source_path.glob("*.py")) else None
        if source_file:
            shutil.copy2(source_file, dest_path)
            result["success"] = True
            result["installed_path"] = str(dest_path)
            return result
    else:
        # 단일 파일 모듈
        dest_path = install_base / "tools" / f"{module_name}.py"
        source_files = list(source_path.glob("*.py"))
        if source_files:
            shutil.copy2(source_files[0], dest_path)
            result["success"] = True
            result["installed_path"] = str(dest_path)
            return result

    # 폴더 모듈 (manager)
    if module_name == "manager":
        if dest_path.exists():
            shutil.rmtree(dest_path)

        if source_dir.exists():
            shutil.copytree(source_dir, dest_path)
        else:
            # manager 폴더가 압축 루트에 있는 경우
            for item in source_path.iterdir():
                if item.is_dir() and item.name == "manager":
                    shutil.copytree(item, dest_path)
                    break

        result["success"] = dest_path.exists()
        result["installed_path"] = str(dest_path)

    return result


def install_pro(
    license_key: Optional[str] = None,
    version: Optional[str] = None,
    modules: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    전체 Pro 모듈 설치

    Args:
        license_key: 라이선스 키
        version: 버전
        modules: 설치할 모듈 목록 (없으면 전체)

    Returns:
        {
            "success": True/False,
            "installed": ["manager", "ship", ...],
            "failed": ["errors"],
            "version": "1.3.8"
        }
    """
    result = {
        "success": False,
        "installed": [],
        "failed": [],
        "version": None
    }

    target_modules = modules or PRO_MODULES

    print(f"Clouvel Pro 설치 시작 ({len(target_modules)}개 모듈)")
    print()

    for module in target_modules:
        download_result = download_pro(
            module_name=module,
            license_key=license_key,
            version=version,
            install=True
        )

        if download_result["success"]:
            result["installed"].append(module)
            if not result["version"]:
                result["version"] = download_result.get("version")
        else:
            result["failed"].append({
                "module": module,
                "error": download_result.get("error", "Unknown error")
            })
            print(f"  [FAIL] {module}: {download_result.get('error')}")

    result["success"] = len(result["failed"]) == 0

    print()
    print("=== 설치 완료 ===")
    print(f"성공: {len(result['installed'])}개")
    print(f"실패: {len(result['failed'])}개")

    return result


def check_pro_installed() -> Dict[str, bool]:
    """설치된 Pro 모듈 확인"""
    install_base = get_install_path()
    status = {}

    for module in PRO_MODULES:
        if module == "manager":
            path = install_base / "tools" / "manager" / "__init__.py"
        elif module == "license":
            path = install_base / "license.py"
        else:
            path = install_base / "tools" / f"{module}.py"

        # stub인지 확인 (Pro 전용 기능입니다 문자열 확인)
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8")
                is_stub = "Pro 전용 기능입니다" in content or "Pro 전용" in content[:500]
                status[module] = not is_stub
            except Exception:
                status[module] = False
        else:
            status[module] = False

    return status


# CLI 지원
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Clouvel Pro 다운로더")
    subparsers = parser.add_subparsers(dest="command")

    # install 명령
    install_parser = subparsers.add_parser("install", help="Pro 모듈 설치")
    install_parser.add_argument("--module", "-m", help="특정 모듈만 설치")
    install_parser.add_argument("--version", "-v", help="버전 지정")

    # status 명령
    subparsers.add_parser("status", help="설치 상태 확인")

    args = parser.parse_args()

    if args.command == "install":
        if args.module:
            result = download_pro(args.module, version=args.version)
        else:
            result = install_pro(version=args.version)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "status":
        status = check_pro_installed()
        print("Clouvel Pro 설치 상태:")
        for module, installed in status.items():
            icon = "✅" if installed else "❌"
            print(f"  {icon} {module}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
