"""
核心功能测试
"""
import pytest
from unittest.mock import Mock, patch
import json
from pathlib import Path
from ..src.core.resource_manager import ResourceManager
from ..src.core.task_system import TaskScheduler, Task, TaskPriority, TaskStatus
from ..src.services.error_handler import ErrorHandler
from ..src.core.game_adapter import GameAdapter


@pytest.fixture
def resource_manager(tmp_path):
    """创建资源管理器实例"""
    config_file = tmp_path / "resource.json"
    config_file.write_text(
        json.dumps(
            {"max_cpu_percent": 80, "max_memory_mb": 1024, "max_gpu_memory_mb": 512}
        )
    )
    return ResourceManager(str(config_file))


@pytest.fixture
def task_scheduler(resource_manager):
    """创建任务调度器实例"""
    return TaskScheduler(resource_manager)


@pytest.fixture
def error_handler(tmp_path):
    """创建错误处理器实例"""
    return ErrorHandler(str(tmp_path / "snapshots"))


class TestTask(Task):
    """测试任务类"""

    def __init__(self, name, priority=TaskPriority.NORMAL):
        super().__init__(name, priority)
        self.executed = False
        self.cleaned = False

    def execute(self):
        self.executed = True

    def cleanup(self):
        self.cleaned = True


def test_resource_manager_limits(resource_manager):
    """测试资源限制"""
    assert resource_manager.resource_limit.max_cpu_percent == 80
    assert resource_manager.resource_limit.max_memory_mb == 1024
    assert resource_manager.resource_limit.max_gpu_memory_mb == 512


def test_resource_manager_monitoring(resource_manager):
    """测试资源监控"""
    resource_manager.start_monitoring()
    assert resource_manager.is_monitoring

    stats = resource_manager.get_resource_stats()
    assert "cpu" in stats
    assert "memory" in stats

    resource_manager.stop_monitoring()
    assert not resource_manager.is_monitoring


def test_resource_manager_alerts(resource_manager):
    """测试资源警报"""
    # 模拟资源超限
    with patch("psutil.Process") as mock_process:
        mock_process.return_value.cpu_percent.return_value = 90.0
        mock_process.return_value.memory_info.return_value.rss = (
            1024 * 1024 * 2048
        )  # 2GB

        resource_manager.start_monitoring()
        alerts = resource_manager.check_alerts()

        assert len(alerts) == 2
        assert any("CPU" in alert for alert in alerts)
        assert any("内存" in alert for alert in alerts)

        resource_manager.stop_monitoring()


def test_task_scheduler_basic(task_scheduler):
    """测试任务调度基本功能"""
    task = TestTask("test_task")
    task_scheduler.add_task(task)

    assert len(task_scheduler.get_tasks()) == 1
    assert task_scheduler.get_task_by_name("test_task") == task


def test_task_scheduler_priority(task_scheduler):
    """测试任务优先级"""
    task1 = TestTask("task1", TaskPriority.LOW)
    task2 = TestTask("task2", TaskPriority.HIGH)
    task3 = TestTask("task3", TaskPriority.NORMAL)

    task_scheduler.add_task(task1)
    task_scheduler.add_task(task2)
    task_scheduler.add_task(task3)

    # 验证执行顺序
    tasks = task_scheduler.get_tasks()
    assert tasks[0].name == "task2"  # HIGH
    assert tasks[1].name == "task3"  # NORMAL
    assert tasks[2].name == "task1"  # LOW


def test_task_scheduler_execution(task_scheduler):
    """测试任务执行"""
    task = TestTask("test_task")
    task_scheduler.add_task(task)

    task_scheduler.start()
    task_scheduler._process_tasks()  # 手动触发处理

    assert task.executed
    assert task.status == TaskStatus.COMPLETED

    task_scheduler.stop()


def test_task_scheduler_cleanup(task_scheduler):
    """测试任务清理"""
    task = TestTask("test_task")
    task_scheduler.add_task(task)

    task_scheduler.start()
    task_scheduler._process_tasks()
    task_scheduler.stop()

    assert task.cleaned


def test_error_handler_snapshot(error_handler):
    """测试错误快照"""
    try:
        raise ValueError("测试错误")
    except Exception as e:
        snapshot = error_handler.create_snapshot(e)

        assert snapshot.error_type == "ValueError"
        assert snapshot.error_message == "测试错误"
        assert snapshot.timestamp is not None
        assert snapshot.stack_trace is not None


def test_error_handler_save_load(error_handler):
    """测试错误快照的保存和加载"""
    # 创建错误
    try:
        raise ValueError("测试错误")
    except Exception as e:
        snapshot = error_handler.create_snapshot(e)

        # 保存快照
        snapshot_path = error_handler.save_snapshot(snapshot)
        assert Path(snapshot_path).exists()

        # 加载快照
        loaded_snapshot = error_handler.load_snapshot(snapshot_path)
        assert loaded_snapshot.error_type == snapshot.error_type
        assert loaded_snapshot.error_message == snapshot.error_message


def test_error_handler_cleanup(error_handler):
    """测试错误快照清理"""
    # 创建多个快照
    for i in range(5):
        try:
            raise ValueError(f"测试错误 {i}")
        except Exception as e:
            snapshot = error_handler.create_snapshot(e)
            error_handler.save_snapshot(snapshot)

    # 清理旧快照
    error_handler.cleanup_old_snapshots(max_age_days=0)
    snapshots = list(Path(error_handler.snapshot_dir).glob("*.json"))
    assert len(snapshots) == 0


class TestGameAdapter(GameAdapter):
    """测试游戏适配器"""

    def __init__(self):
        super().__init__("TestGame")
        self._config = {}

    def get_config(self):
        return self._config

    def save_config(self, config):
        self._config = config

    def create_task(self, config):
        return TestTask("game_task")


def test_game_adapter_basic():
    """测试游戏适配器基本功能"""
    adapter = TestGameAdapter()
    assert adapter.name == "TestGame"


def test_game_adapter_config():
    """测试游戏配置管理"""
    adapter = TestGameAdapter()

    # 保存配置
    test_config = {"key": "value"}
    adapter.save_config(test_config)

    # 获取配置
    config = adapter.get_config()
    assert config == test_config


def test_game_adapter_task():
    """测试游戏任务创建"""
    adapter = TestGameAdapter()
    task = adapter.create_task({})

    assert isinstance(task, Task)
    assert task.name == "game_task"
