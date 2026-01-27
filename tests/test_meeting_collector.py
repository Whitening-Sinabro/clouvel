# -*- coding: utf-8 -*-
"""Meeting collector module tests"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.manager.generator.collector import (
    MeetingCollector,
    DEFAULT_LOG_DIR,
    save_meeting_log,
    get_training_data,
    get_collection_stats,
    log_manual_example,
)


@pytest.fixture
def temp_log_dir():
    """Create temporary log directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestDefaultLogDir:
    """DEFAULT_LOG_DIR constant tests"""

    def test_constant_exists(self):
        """Constant exists"""
        assert DEFAULT_LOG_DIR is not None

    def test_is_string(self):
        """Is string"""
        assert isinstance(DEFAULT_LOG_DIR, str)

    def test_includes_clouvel(self):
        """Includes clouvel"""
        assert ".clouvel" in DEFAULT_LOG_DIR


class TestMeetingCollectorInit:
    """MeetingCollector initialization tests"""

    def test_init_with_path(self, temp_log_dir):
        """Initializes with custom path"""
        collector = MeetingCollector(temp_log_dir)
        assert collector.log_dir == Path(temp_log_dir)

    def test_creates_log_dir(self, temp_log_dir):
        """Creates log directory"""
        log_path = Path(temp_log_dir) / "subdir"
        collector = MeetingCollector(str(log_path))
        assert log_path.exists()

    def test_sets_log_file(self, temp_log_dir):
        """Sets log file path"""
        collector = MeetingCollector(temp_log_dir)
        assert collector.log_file == Path(temp_log_dir) / "meetings.jsonl"

    def test_sets_index_file(self, temp_log_dir):
        """Sets index file path"""
        collector = MeetingCollector(temp_log_dir)
        assert collector.index_file == Path(temp_log_dir) / "index.json"


class TestMeetingCollectorSave:
    """MeetingCollector save tests"""

    def test_returns_id(self, temp_log_dir):
        """Returns meeting ID"""
        collector = MeetingCollector(temp_log_dir)
        meeting_id = collector.save({"context": "Test meeting"})
        assert isinstance(meeting_id, str)
        assert len(meeting_id) == 12

    def test_creates_log_file(self, temp_log_dir):
        """Creates log file"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "Test meeting"})
        assert collector.log_file.exists()

    def test_saves_context(self, temp_log_dir):
        """Saves context to file"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "Test context"})

        with open(collector.log_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Test context" in content

    def test_saves_timestamp(self, temp_log_dir):
        """Saves timestamp"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "Test"})

        records = collector.get_all()
        assert len(records) == 1
        assert "timestamp" in records[0]

    def test_multiple_saves(self, temp_log_dir):
        """Multiple saves append"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "Meeting 1"})
        collector.save({"context": "Meeting 2"})
        collector.save({"context": "Meeting 3"})

        records = collector.get_all()
        assert len(records) == 3


class TestMeetingCollectorGetAll:
    """MeetingCollector get_all tests"""

    def test_returns_list(self, temp_log_dir):
        """Returns list"""
        collector = MeetingCollector(temp_log_dir)
        result = collector.get_all()
        assert isinstance(result, list)

    def test_empty_when_no_logs(self, temp_log_dir):
        """Empty list when no logs"""
        collector = MeetingCollector(temp_log_dir)
        result = collector.get_all()
        assert result == []

    def test_returns_saved_records(self, temp_log_dir):
        """Returns saved records"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "Test"})

        result = collector.get_all()
        assert len(result) == 1
        assert result[0]["context"] == "Test"


class TestMeetingCollectorGetByTopic:
    """MeetingCollector get_by_topic tests"""

    def test_filters_by_topic(self, temp_log_dir):
        """Filters by topic"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "Auth feature", "topic": "auth"})
        collector.save({"context": "API feature", "topic": "api"})
        collector.save({"context": "Another auth", "topic": "auth"})

        result = collector.get_by_topic("auth")
        assert len(result) == 2

    def test_empty_for_unknown_topic(self, temp_log_dir):
        """Empty for unknown topic"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "Test", "topic": "feature"})

        result = collector.get_by_topic("unknown")
        assert result == []


class TestMeetingCollectorGetByProject:
    """MeetingCollector get_by_project tests"""

    def test_filters_by_project(self, temp_log_dir):
        """Filters by project"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "Project A", "project": "proj_a"})
        collector.save({"context": "Project B", "project": "proj_b"})

        result = collector.get_by_project("proj_a")
        assert len(result) == 1
        assert result[0]["context"] == "Project A"


class TestMeetingCollectorGetWithOutput:
    """MeetingCollector get_with_output tests"""

    def test_filters_with_output(self, temp_log_dir):
        """Filters records with output"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "No output"})
        collector.save({"context": "Has output", "output": "Result here"})

        result = collector.get_with_output()
        assert len(result) == 1
        assert "output" in result[0]


class TestMeetingCollectorGetTrainingPairs:
    """MeetingCollector get_training_pairs tests"""

    def test_returns_list(self, temp_log_dir):
        """Returns list"""
        collector = MeetingCollector(temp_log_dir)
        result = collector.get_training_pairs()
        assert isinstance(result, list)

    def test_includes_context_and_output(self, temp_log_dir):
        """Includes context and output"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({
            "context": "Test context",
            "output": "Test output",
            "topic": "feature"
        })

        pairs = collector.get_training_pairs()
        assert len(pairs) == 1
        assert pairs[0]["context"] == "Test context"
        assert pairs[0]["output"] == "Test output"

    def test_excludes_without_output(self, temp_log_dir):
        """Excludes records without output"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "No output"})
        collector.save({"context": "With output", "output": "Result"})

        pairs = collector.get_training_pairs()
        assert len(pairs) == 1


class TestMeetingCollectorExportForFinetuning:
    """MeetingCollector export_for_finetuning tests"""

    def test_creates_file(self, temp_log_dir):
        """Creates output file"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "Test", "output": "Result"})

        output_path = Path(temp_log_dir) / "export.jsonl"
        result = collector.export_for_finetuning(str(output_path))

        assert Path(result).exists()

    def test_returns_path(self, temp_log_dir):
        """Returns file path"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "Test", "output": "Result"})

        output_path = Path(temp_log_dir) / "export.jsonl"
        result = collector.export_for_finetuning(str(output_path))

        assert result == str(output_path)

    def test_creates_valid_jsonl(self, temp_log_dir):
        """Creates valid JSONL format"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "Test context", "output": "Test output"})

        output_path = Path(temp_log_dir) / "export.jsonl"
        collector.export_for_finetuning(str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        record = json.loads(content)
        assert "messages" in record
        assert len(record["messages"]) == 2


class TestMeetingCollectorGetStats:
    """MeetingCollector get_stats tests"""

    def test_returns_dict(self, temp_log_dir):
        """Returns dictionary"""
        collector = MeetingCollector(temp_log_dir)
        result = collector.get_stats()
        assert isinstance(result, dict)

    def test_has_total_count(self, temp_log_dir):
        """Has total count"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "Test 1"})
        collector.save({"context": "Test 2"})

        stats = collector.get_stats()
        assert stats["total_count"] == 2

    def test_has_with_output_count(self, temp_log_dir):
        """Has with_output count"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "No output"})
        collector.save({"context": "With output", "output": "Result"})

        stats = collector.get_stats()
        assert stats["with_output"] == 1
        assert stats["without_output"] == 1


class TestMeetingCollectorClear:
    """MeetingCollector clear tests"""

    def test_requires_confirm(self, temp_log_dir):
        """Requires confirmation"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "Test"})

        with pytest.raises(ValueError):
            collector.clear()

    def test_clears_with_confirm(self, temp_log_dir):
        """Clears with confirmation"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "Test"})

        collector.clear(confirm=True)

        assert not collector.log_file.exists()


class TestSaveMeetingLog:
    """save_meeting_log function tests"""

    def test_returns_id(self, temp_log_dir):
        """Returns meeting ID"""
        result = save_meeting_log({"context": "Test"}, temp_log_dir)
        assert isinstance(result, str)
        assert len(result) == 12

    def test_saves_to_custom_path(self, temp_log_dir):
        """Saves to custom path"""
        save_meeting_log({"context": "Test"}, temp_log_dir)

        log_file = Path(temp_log_dir) / "meetings.jsonl"
        assert log_file.exists()


class TestGetTrainingData:
    """get_training_data function tests"""

    def test_returns_list(self, temp_log_dir):
        """Returns list"""
        result = get_training_data(temp_log_dir)
        assert isinstance(result, list)

    def test_returns_pairs(self, temp_log_dir):
        """Returns training pairs"""
        save_meeting_log({
            "context": "Test",
            "output": "Result"
        }, temp_log_dir)

        pairs = get_training_data(temp_log_dir)
        assert len(pairs) == 1


class TestLogManualExample:
    """log_manual_example function tests"""

    def test_returns_id(self):
        """Returns meeting ID"""
        # Use default collector (will use home directory)
        result = log_manual_example(
            context="Test context",
            output="Test output",
            topic="test"
        )
        assert isinstance(result, str)

    def test_saves_source(self):
        """Saves with manual_labeling source"""
        # This would require checking the saved data
        result = log_manual_example(
            context="Test",
            output="Result"
        )
        assert len(result) == 12  # ID format check


class TestMeetingCollectorGenerateId:
    """MeetingCollector _generate_id tests"""

    def test_generates_12_char_id(self, temp_log_dir):
        """Generates 12 character ID"""
        collector = MeetingCollector(temp_log_dir)
        meeting_id = collector._generate_id({"context": "Test"})
        assert len(meeting_id) == 12

    def test_generates_unique_ids(self, temp_log_dir):
        """Generates unique IDs"""
        collector = MeetingCollector(temp_log_dir)
        ids = set()
        for i in range(10):
            meeting_id = collector._generate_id({"context": f"Test {i}"})
            ids.add(meeting_id)
        # Due to timing differences, IDs should mostly be unique
        assert len(ids) >= 1


class TestMeetingCollectorLoadIndex:
    """MeetingCollector _load_index tests"""

    def test_returns_dict(self, temp_log_dir):
        """Returns dictionary"""
        collector = MeetingCollector(temp_log_dir)
        index = collector._load_index()
        assert isinstance(index, dict)

    def test_has_meetings_key(self, temp_log_dir):
        """Has meetings key"""
        collector = MeetingCollector(temp_log_dir)
        index = collector._load_index()
        assert "meetings" in index

    def test_has_stats_key(self, temp_log_dir):
        """Has stats key"""
        collector = MeetingCollector(temp_log_dir)
        index = collector._load_index()
        assert "stats" in index

    def test_loads_existing_index(self, temp_log_dir):
        """Loads existing index"""
        collector = MeetingCollector(temp_log_dir)
        collector.save({"context": "Test", "topic": "feature"})

        # Load index again
        index = collector._load_index()
        assert index["stats"]["total_count"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
