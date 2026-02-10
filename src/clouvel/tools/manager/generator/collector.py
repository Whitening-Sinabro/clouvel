# Meeting Collector
# 튜닝 데이터 수집 및 로깅

import os
import json
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


# 기본 로그 디렉토리
DEFAULT_LOG_DIR = ".clouvel/meeting_logs"


class MeetingCollector:
    """회의 로그 수집 및 관리 (중앙 저장소)"""

    def __init__(self, log_dir: Optional[str] = None):
        """
        Args:
            log_dir: 로그 저장 디렉토리 (None이면 홈 디렉토리)
        """
        if log_dir is None:
            # 항상 홈 디렉토리에 중앙 저장 (프로젝트 간 공유)
            self.log_dir = Path.home() / DEFAULT_LOG_DIR
        else:
            self.log_dir = Path(log_dir)

        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "meetings.jsonl"
        self.index_file = self.log_dir / "index.json"

        # 현재 프로젝트 정보 저장
        self.current_project = self._detect_project()

    def _detect_project(self) -> Optional[str]:
        """현재 프로젝트명을 감지합니다."""
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            if (parent / ".git").exists() or (parent / "docs").exists():
                return parent.name
        return None

    def save(self, meeting_data: Dict[str, Any]) -> str:
        """
        회의 데이터를 저장합니다.

        Args:
            meeting_data: 저장할 회의 데이터

        Returns:
            저장된 회의 ID
        """
        # 회의 ID 생성
        meeting_id = self._generate_id(meeting_data)

        # 메타데이터 추가 (프로젝트 정보 포함)
        record = {
            "id": meeting_id,
            "timestamp": datetime.now().isoformat(),
            "project": self.current_project,
            **meeting_data
        }

        # JSONL에 추가
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        # 인덱스 업데이트
        self._update_index(meeting_id, record)

        return meeting_id

    def _generate_id(self, data: Dict) -> str:
        """회의 데이터에서 고유 ID를 생성합니다."""
        content = json.dumps(data.get("context", ""), sort_keys=True)
        timestamp = datetime.now().isoformat()
        hash_input = f"{content}{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def _update_index(self, meeting_id: str, record: Dict):
        """인덱스 파일을 업데이트합니다."""
        index = self._load_index()

        # 인덱스 항목 추가 (프로젝트 정보 포함)
        index["meetings"][meeting_id] = {
            "timestamp": record["timestamp"],
            "topic": record.get("topic", "unknown"),
            "project": record.get("project"),
            "context_preview": record.get("context", "")[:100],
            "has_output": "output" in record,
        }

        # 통계 업데이트
        index["stats"]["total_count"] = len(index["meetings"])
        index["stats"]["last_updated"] = datetime.now().isoformat()

        # 토픽별 카운트
        topic = record.get("topic", "unknown")
        if topic not in index["stats"]["by_topic"]:
            index["stats"]["by_topic"][topic] = 0
        index["stats"]["by_topic"][topic] += 1

        # 프로젝트별 카운트
        project = record.get("project", "unknown")
        if "by_project" not in index["stats"]:
            index["stats"]["by_project"] = {}
        if project not in index["stats"]["by_project"]:
            index["stats"]["by_project"][project] = 0
        index["stats"]["by_project"][project] += 1

        # 저장
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def _load_index(self) -> Dict:
        """인덱스 파일을 로드합니다."""
        if self.index_file.exists():
            with open(self.index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "meetings": {},
            "stats": {
                "total_count": 0,
                "last_updated": None,
                "by_topic": {},
                "by_project": {}
            }
        }

    def get_all(self) -> List[Dict[str, Any]]:
        """모든 회의 로그를 반환합니다."""
        records = []
        if self.log_file.exists():
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
        return records

    def get_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """특정 토픽의 회의 로그를 반환합니다."""
        return [r for r in self.get_all() if r.get("topic") == topic]

    def get_by_project(self, project: str) -> List[Dict[str, Any]]:
        """특정 프로젝트의 회의 로그를 반환합니다."""
        return [r for r in self.get_all() if r.get("project") == project]

    def get_with_output(self) -> List[Dict[str, Any]]:
        """출력이 있는 회의 로그만 반환합니다 (튜닝용)."""
        return [r for r in self.get_all() if "output" in r]

    def get_training_pairs(self) -> List[Dict[str, str]]:
        """
        튜닝용 (context, output) 쌍을 반환합니다.

        Returns:
            [{"context": str, "output": str}, ...] 형태의 리스트
        """
        pairs = []
        for record in self.get_with_output():
            pairs.append({
                "context": record.get("context", ""),
                "output": record.get("output", ""),
                "topic": record.get("topic", "unknown"),
                "project": record.get("project"),
                "timestamp": record.get("timestamp", ""),
            })
        return pairs

    def export_for_finetuning(self, output_path: Optional[str] = None) -> str:
        """
        파인튜닝용 JSONL 파일을 생성합니다.

        Args:
            output_path: 출력 파일 경로 (None이면 기본 경로)

        Returns:
            생성된 파일 경로
        """
        if output_path is None:
            output_path = self.log_dir / "training_data.jsonl"

        pairs = self.get_training_pairs()

        with open(output_path, "w", encoding="utf-8") as f:
            for pair in pairs:
                # Anthropic/OpenAI 파인튜닝 형식
                record = {
                    "messages": [
                        {
                            "role": "user",
                            "content": pair["context"]
                        },
                        {
                            "role": "assistant",
                            "content": pair["output"]
                        }
                    ],
                    "metadata": {
                        "topic": pair["topic"],
                        "timestamp": pair["timestamp"]
                    }
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        return str(output_path)

    def get_stats(self) -> Dict[str, Any]:
        """수집 통계를 반환합니다."""
        index = self._load_index()
        stats = index["stats"].copy()

        # 추가 통계
        all_records = self.get_all()
        stats["with_output"] = len([r for r in all_records if "output" in r])
        stats["without_output"] = stats["total_count"] - stats["with_output"]

        return stats

    def clear(self, confirm: bool = False):
        """모든 로그를 삭제합니다."""
        if not confirm:
            raise ValueError("삭제를 확인하려면 confirm=True를 전달하세요.")

        if self.log_file.exists():
            self.log_file.unlink()
        if self.index_file.exists():
            self.index_file.unlink()


# 전역 collector 인스턴스
_default_collector: Optional[MeetingCollector] = None


def _get_default_collector() -> MeetingCollector:
    """기본 collector 인스턴스를 반환합니다."""
    global _default_collector
    if _default_collector is None:
        _default_collector = MeetingCollector()
    return _default_collector


def save_meeting_log(
    meeting_data: Dict[str, Any],
    log_path: Optional[str] = None
) -> str:
    """
    회의 데이터를 로그에 저장합니다.

    Args:
        meeting_data: 저장할 회의 데이터
        log_path: 로그 디렉토리 경로 (None이면 기본 경로)

    Returns:
        저장된 회의 ID
    """
    if log_path:
        collector = MeetingCollector(log_path)
    else:
        collector = _get_default_collector()

    return collector.save(meeting_data)


def get_training_data(log_path: Optional[str] = None) -> List[Dict[str, str]]:
    """
    튜닝용 데이터를 반환합니다.

    Args:
        log_path: 로그 디렉토리 경로 (None이면 기본 경로)

    Returns:
        [{"context": str, "output": str}, ...] 형태의 리스트
    """
    if log_path:
        collector = MeetingCollector(log_path)
    else:
        collector = _get_default_collector()

    return collector.get_training_pairs()


def export_training_data(output_path: Optional[str] = None) -> str:
    """
    파인튜닝용 JSONL 파일을 생성합니다.

    Args:
        output_path: 출력 파일 경로

    Returns:
        생성된 파일 경로
    """
    collector = _get_default_collector()
    return collector.export_for_finetuning(output_path)


def get_collection_stats() -> Dict[str, Any]:
    """수집 통계를 반환합니다."""
    collector = _get_default_collector()
    return collector.get_stats()


# 유틸리티 함수
def log_manual_example(
    context: str,
    output: str,
    topic: str = "feature"
) -> str:
    """
    수동으로 예시를 추가합니다 (라벨링된 데이터).

    Args:
        context: 회의 주제/상황
        output: 좋은 회의록 예시
        topic: 토픽

    Returns:
        저장된 회의 ID
    """
    meeting_data = {
        "context": context,
        "output": output,
        "topic": topic,
        "source": "manual_labeling",
        "quality": "verified"
    }

    return save_meeting_log(meeting_data)
