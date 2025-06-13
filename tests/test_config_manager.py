"""ConfigManager 单元测试"""
import pytest
from unittest.mock import mock_open, patch
import json
from src.services.config import Config as ConfigManager


@pytest.fixture
def config_manager():
    """创建 ConfigManager 实例"""
    return ConfigManager()


@pytest.fixture
def sample_config():
    """创建示例配置"""
    return {
        "window_title": "Game Window",
        "hotkeys": {"start": "F1", "stop": "F2"},
        "actions": {"click_interval": 1000, "move_speed": 2},
    }


def test_init(config_manager):
    """测试初始化"""
    assert isinstance(config_manager.config, dict)
    assert len(config_manager.config) == 0


def test_load_config():
    """测试加载配置"""
    config_data = json.dumps({"test": "value"})
    with patch("builtins.open", mock_open(read_data=config_data)):
        manager = ConfigManager("config.json")
        assert manager.config == {"test": "value"}


def test_load_config_file_not_found():
    """测试加载不存在的配置文件"""
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = FileNotFoundError()
        manager = ConfigManager("nonexistent.json")
        assert isinstance(manager.config, dict)
        assert len(manager.config) == 0


def test_load_config_invalid_json():
    """测试加载无效的 JSON 配置"""
    with patch("builtins.open", mock_open(read_data="invalid json")):
        manager = ConfigManager("invalid.json")
        assert isinstance(manager.config, dict)
        assert len(manager.config) == 0


def test_save_config(config_manager, sample_config):
    """测试保存配置"""
    config_manager.config = sample_config
    mock_file = mock_open()
    with patch("builtins.open", mock_file) as mock_file_handle:
        config_manager.save_config("config.json")
        mock_file_handle.assert_called_once_with("config.json", "w", encoding="utf-8")
        handle = mock_file()
        assert handle.write.call_count > 0


def test_get_config(config_manager, sample_config):
    """测试获取配置"""
    config_manager.config = sample_config
    assert config_manager.get_config("window_title") == "Game Window"
    assert config_manager.get_config("hotkeys.start") == "F1"
    assert config_manager.get_config("nonexistent") is None
    assert config_manager.get_config("nonexistent", "default") == "default"


def test_set_config(config_manager):
    """测试设置配置"""
    config_manager.set_config("test.key", "value")
    assert config_manager.get_config("test.key") == "value"

    config_manager.set_config("nested.key1.key2", 123)
    assert config_manager.get_config("nested.key1.key2") == 123


def test_delete_config(config_manager, sample_config):
    """测试删除配置"""
    config_manager.config = sample_config
    config_manager.delete_config("hotkeys.start")
    assert config_manager.get_config("hotkeys.start") is None
    assert config_manager.get_config("hotkeys.stop") == "F2"


def test_clear_config(config_manager, sample_config):
    """测试清空配置"""
    config_manager.config = sample_config
    config_manager.clear_config()
    assert len(config_manager.config) == 0
