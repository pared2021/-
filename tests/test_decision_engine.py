"""DecisionEngine 单元测试"""
import pytest
import json
from unittest.mock import mock_open, patch
from ..src.engine.decision_engine import DecisionEngine, Action


@pytest.fixture
def decision_engine():
    """创建 DecisionEngine 实例"""
    return DecisionEngine()


@pytest.fixture
def sample_rules():
    """创建示例规则"""
    return [
        {
            "conditions": [{"type": "text_present", "text": "Start"}],
            "action_type": "click",
            "action_params": {"x": 100, "y": 200},
            "priority": 1,
        },
        {
            "conditions": [{"type": "button_exists", "text": "OK"}],
            "action_type": "click",
            "action_params": {"x": 300, "y": 400},
            "priority": 2,
        },
    ]


def test_init():
    """测试初始化"""
    engine = DecisionEngine()
    assert isinstance(engine.rules, list)
    assert isinstance(engine.history, list)
    assert len(engine.rules) == 0
    assert len(engine.history) == 0


def test_init_with_rules_file():
    """测试使用规则文件初始化"""
    rules_content = json.dumps([{"conditions": [], "action_type": "test"}])
    with patch("builtins.open", mock_open(read_data=rules_content)) as mock_file:
        engine = DecisionEngine("rules.json")
        mock_file.assert_called_once_with("rules.json", "r", encoding="utf-8")
        assert len(engine.rules) == 1
        assert engine.rules[0]["action_type"] == "test"


def test_load_rules_file_not_found(decision_engine):
    """测试加载不存在的规则文件"""
    decision_engine._load_rules("nonexistent.json")
    assert len(decision_engine.rules) == 0


def test_load_rules_invalid_json(decision_engine):
    """测试加载无效的JSON规则文件"""
    with patch("builtins.open", mock_open(read_data="invalid json")):
        decision_engine._load_rules("rules.json")
        assert len(decision_engine.rules) == 0


def test_analyze_state_no_rules(decision_engine):
    """测试没有规则时的状态分析"""
    current_state = {"text_content": {"full_text": "test"}}
    actions = decision_engine.analyze_state(current_state)
    assert isinstance(actions, list)
    assert len(actions) == 0


def test_analyze_state_with_rules(decision_engine, sample_rules):
    """测试有规则时的状态分析"""
    decision_engine.rules = sample_rules
    current_state = {"text_content": {"full_text": "Start button"}}

    actions = decision_engine.analyze_state(current_state)

    assert isinstance(actions, list)
    assert len(actions) == 1
    assert isinstance(actions[0], Action)
    assert actions[0].action_type == "click"
    assert actions[0].params == {"x": 100, "y": 200}


def test_check_conditions_text_present(decision_engine):
    """测试文本存在条件"""
    conditions = [{"type": "text_present", "text": "test"}]
    current_state = {"text_content": {"full_text": "this is a test message"}}

    result = decision_engine._check_conditions(conditions, current_state)
    assert result is True


def test_check_conditions_button_exists(decision_engine):
    """测试按钮存在条件"""
    conditions = [{"type": "button_exists", "text": "OK"}]
    current_state = {
        "visual_elements": {
            "buttons": [{"text": "OK", "position": {"x": 100, "y": 100}}]
        }
    }

    result = decision_engine._check_conditions(conditions, current_state)
    assert result is True


def test_check_conditions_icon_exists(decision_engine):
    """测试图标存在条件"""
    conditions = [{"type": "icon_exists", "icon_type": "close"}]
    current_state = {
        "visual_elements": {
            "icons": [{"type": "close", "position": {"x": 100, "y": 100}}]
        }
    }

    result = decision_engine._check_conditions(conditions, current_state)
    assert result is True


def test_check_conditions_progress_complete(decision_engine):
    """测试进度完成条件"""
    conditions = [{"type": "progress_complete"}]
    current_state = {
        "visual_elements": {
            "progress_bars": [{"progress": 1.0, "position": {"x": 100, "y": 100}}]
        }
    }

    result = decision_engine._check_conditions(conditions, current_state)
    assert result is True


def test_check_conditions_motion_detected(decision_engine):
    """测试动作检测条件"""
    conditions = [{"type": "motion_detected"}]
    current_state = {"motion": {"motion_detected": True, "change_ratio": 0.5}}

    result = decision_engine._check_conditions(conditions, current_state)
    assert result is True


def test_check_conditions_color_present(decision_engine):
    """测试颜色存在条件"""
    conditions = [{"type": "color_present", "color": (255, 0, 0)}]
    current_state = {"colors": {"dominant_color": (255, 0, 0)}}

    result = decision_engine._check_conditions(conditions, current_state)
    assert result is True


def test_add_rule_valid(decision_engine):
    """测试添加有效规则"""
    rule = {
        "conditions": [{"type": "text_present", "text": "test"}],
        "action_type": "click",
        "action_params": {"x": 100, "y": 100},
    }

    initial_count = len(decision_engine.rules)
    decision_engine.add_rule(rule)
    assert len(decision_engine.rules) == initial_count + 1


def test_add_rule_invalid(decision_engine):
    """测试添加无效规则"""
    rule = {"invalid": "rule"}

    initial_count = len(decision_engine.rules)
    decision_engine.add_rule(rule)
    assert len(decision_engine.rules) == initial_count


def test_save_rules(decision_engine, sample_rules):
    """测试保存规则"""
    decision_engine.rules = sample_rules
    with patch("builtins.open", mock_open()) as mock_file:
        decision_engine.save_rules("rules.json")
        mock_file.assert_called_once_with("rules.json", "w", encoding="utf-8")
        handle = mock_file()
        assert handle.write.call_count > 0


def test_record_action(decision_engine):
    """测试记录动作"""
    action = Action("click", {"x": 100, "y": 100}, 1)

    initial_count = len(decision_engine.history)
    decision_engine.record_action(action, True)
    assert len(decision_engine.history) == initial_count + 1

    record = decision_engine.history[-1]
    assert record["action_type"] == "click"
    assert record["params"] == {"x": 100, "y": 100}
    assert record["priority"] == 1
    assert record["result"] is True
    assert "timestamp" in record
