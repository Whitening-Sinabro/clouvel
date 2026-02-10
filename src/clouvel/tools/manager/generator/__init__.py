# Manager Generator
# 동적 회의 시뮬레이션 및 튜닝 데이터 수집

from .conversation import (
    generate_meeting,
    generate_meeting_sync,
    MeetingGenerator,
    MeetingConfig,
    preview_prompt,
)
from .collector import (
    MeetingCollector,
    save_meeting_log,
    get_training_data,
    export_training_data,
    get_collection_stats,
    log_manual_example,
)

__all__ = [
    # 회의 생성
    "generate_meeting",
    "generate_meeting_sync",
    "MeetingGenerator",
    "MeetingConfig",
    "preview_prompt",

    # 데이터 수집
    "MeetingCollector",
    "save_meeting_log",
    "get_training_data",
    "export_training_data",
    "get_collection_stats",
    "log_manual_example",
]
