"""OperationRecorder 单元测试"""
import pytest
from unittest.mock import patch, MagicMock, mock_open
import json
import time
from src.operation_recorder import OperationRecorder


@pytest.fixture
def operation_recorder():
    """创建 OperationRecorder 实例"""
    return OperationRecorder()


def test_init(operation_recorder):
    """测试初始化"""
    assert operation_recorder.recording == False
    assert isinstance(operation_recorder.operations, list)
    assert len(operation_recorder.operations) == 0


def test_start_recording(operation_recorder):
    """测试开始录制"""
    operation_recorder.start_recording()
    assert operation_recorder.recording == True


def test_stop_recording(operation_recorder):
    """测试停止录制"""
    operation_recorder.recording = True
    operation_recorder.stop_recording()
    assert operation_recorder.recording == False


def test_record_operation(operation_recorder):
    """测试记录操作"""
    operation_recorder.recording = True
    operation_recorder.record_operation("click", {"x": 100, "y": 200})

    assert len(operation_recorder.operations) == 1
    operation = operation_recorder.operations[0]
    assert operation["type"] == "click"
    assert operation["params"] == {"x": 100, "y": 200}
    assert "timestamp" in operation


def test_record_operation_not_recording(operation_recorder):
    """测试在未录制状态下记录操作"""
    operation_recorder.recording = False
    operation_recorder.record_operation("click", {"x": 100, "y": 200})
    assert len(operation_recorder.operations) == 0


def test_clear_operations(operation_recorder):
    """测试清除操作记录"""
    operation_recorder.operations = [
        {"type": "click", "params": {"x": 100, "y": 200}, "timestamp": time.time()}
    ]
    operation_recorder.clear_operations()
    assert len(operation_recorder.operations) == 0


def test_save_operations(operation_recorder):
    """测试保存操作记录"""
    operation_recorder.operations = [
        {"type": "click", "params": {"x": 100, "y": 200}, "timestamp": time.time()}
    ]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        operation_recorder.save_operations("test.json")
        mock_file.assert_called_once_with("test.json", "w", encoding="utf-8")
        handle = mock_file()
        assert handle.write.call_count > 0


def test_load_operations(operation_recorder):
    """测试加载操作记录"""
    operations = [
        {"type": "click", "params": {"x": 100, "y": 200}, "timestamp": time.time()}
    ]

    with patch("builtins.open", mock_open(read_data=json.dumps(operations))):
        operation_recorder.load_operations("test.json")
        assert len(operation_recorder.operations) == 1
        assert operation_recorder.operations[0]["type"] == "click"


def test_load_operations_file_not_found(operation_recorder):
    """测试加载不存在的操作记录文件"""
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = FileNotFoundError()
        operation_recorder.load_operations("nonexistent.json")
        assert len(operation_recorder.operations) == 0


def test_load_operations_invalid_json(operation_recorder):
    """测试加载无效的 JSON 操作记录"""
    with patch("builtins.open", mock_open(read_data="invalid json")):
        operation_recorder.load_operations("invalid.json")
        assert len(operation_recorder.operations) == 0


@patch("time.sleep")
def test_replay_operations(mock_sleep, operation_recorder):
    """测试回放操作记录"""
    mock_executor = MagicMock()
    operation_recorder.operations = [
        {"type": "click", "params": {"x": 100, "y": 200}, "timestamp": time.time()}
    ]

    operation_recorder.replay_operations(mock_executor)
    mock_executor.execute_action.assert_called_once_with("click", {"x": 100, "y": 200})


def test_get_operation_count(operation_recorder):
    """测试获取操作记录数量"""
    operation_recorder.operations = [
        {"type": "click", "params": {"x": 100, "y": 200}, "timestamp": time.time()},
        {"type": "move", "params": {"x": 300, "y": 400}, "timestamp": time.time()},
    ]
    assert operation_recorder.get_operation_count() == 2


def test_get_operation_types(operation_recorder):
    """测试获取操作类型统计"""
    operation_recorder.operations = [
        {"type": "click", "params": {"x": 100, "y": 200}, "timestamp": time.time()},
        {"type": "click", "params": {"x": 300, "y": 400}, "timestamp": time.time()},
        {"type": "move", "params": {"x": 500, "y": 600}, "timestamp": time.time()},
    ]

    type_counts = operation_recorder.get_operation_types()
    assert type_counts["click"] == 2
    assert type_counts["move"] == 1
