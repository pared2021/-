"""
性能监控测试
"""
import pytest
from unittest.mock import Mock, patch
import time
from src.performance.performance_monitor import PerformanceMonitor
from src.performance.performance_view import PerformanceView


@pytest.fixture
def monitor():
    """创建性能监控器实例"""
    return PerformanceMonitor("Test Window")


@pytest.fixture
def view(qtbot):
    """创建性能视图实例"""
    view = PerformanceView()
    qtbot.addWidget(view)
    return view


def test_monitor_start_stop(monitor):
    """测试监控器的开始和停止"""
    assert not monitor.is_monitoring

    monitor.start()
    assert monitor.is_monitoring

    monitor.stop()
    assert not monitor.is_monitoring


def test_monitor_metrics(monitor):
    """测试性能指标收集"""
    monitor.start()
    time.sleep(0.1)  # 等待收集数据

    metrics = monitor.get_current_metrics()
    assert metrics is not None
    assert hasattr(metrics, "cpu_usage")
    assert hasattr(metrics, "memory_usage")
    assert hasattr(metrics, "fps")

    monitor.stop()


def test_monitor_history(monitor):
    """测试历史数据记录"""
    monitor.start()
    time.sleep(0.2)  # 等待收集多个数据点

    history = monitor.get_history()
    assert len(history) > 0

    # 验证历史数据格式
    first_record = history[0]
    assert "timestamp" in first_record
    assert "metrics" in first_record

    monitor.stop()


def test_monitor_export(monitor, tmp_path):
    """测试数据导出"""
    monitor.start()
    time.sleep(0.1)
    monitor.stop()

    # 导出CSV
    csv_file = tmp_path / "performance.csv"
    monitor.export_csv(str(csv_file))
    assert csv_file.exists()

    # 导出JSON
    json_file = tmp_path / "performance.json"
    monitor.export_json(str(json_file))
    assert json_file.exists()

    # 导出HTML报告
    html_file = tmp_path / "performance.html"
    monitor.export_html(str(html_file))
    assert html_file.exists()


@patch("psutil.Process")
def test_monitor_process_metrics(mock_process, monitor):
    """测试进程指标收集"""
    mock_process.return_value.cpu_percent.return_value = 50.0
    mock_process.return_value.memory_info.return_value.rss = 1024 * 1024 * 100  # 100MB

    monitor.start()
    metrics = monitor.get_current_metrics()

    assert metrics.cpu_usage == 50.0
    assert metrics.memory_usage == 100.0  # MB

    monitor.stop()


def test_view_display(view, monitor):
    """测试性能视图显示"""
    # 模拟数据
    metrics = Mock(cpu_usage=50.0, memory_usage=100.0, fps=60.0, timestamp=time.time())

    # 更新视图
    view.update_metrics(metrics)

    # 验证图表更新
    assert len(view.cpu_data) == 1
    assert len(view.memory_data) == 1
    assert len(view.fps_data) == 1

    assert view.cpu_data[0] == 50.0
    assert view.memory_data[0] == 100.0
    assert view.fps_data[0] == 60.0


def test_view_chart_options(view):
    """测试图表选项"""
    # 测试时间范围选择
    view.set_time_range("1h")
    assert view.time_range == 3600  # 1小时的秒数

    view.set_time_range("24h")
    assert view.time_range == 86400  # 24小时的秒数

    # 测试指标选择
    view.toggle_metric("cpu")
    assert not view.cpu_chart.isVisible()

    view.toggle_metric("cpu")
    assert view.cpu_chart.isVisible()


def test_view_export(view, tmp_path):
    """测试视图导出功能"""
    # 添加一些测试数据
    metrics = Mock(cpu_usage=50.0, memory_usage=100.0, fps=60.0, timestamp=time.time())
    view.update_metrics(metrics)

    # 测试导出图片
    image_file = tmp_path / "performance.png"
    view.export_image(str(image_file))
    assert image_file.exists()

    # 测试导出数据
    data_file = tmp_path / "performance.csv"
    view.export_data(str(data_file))
    assert data_file.exists()


def test_view_alerts(view):
    """测试性能警报"""
    # 设置警报阈值
    view.set_alert_threshold("cpu", 80.0)
    view.set_alert_threshold("memory", 90.0)
    view.set_alert_threshold("fps", 30.0)

    # 测试CPU警报
    metrics = Mock(cpu_usage=85.0, memory_usage=50.0, fps=60.0, timestamp=time.time())
    with patch.object(view, "_show_alert") as mock_alert:
        view.update_metrics(metrics)
        mock_alert.assert_called_once_with("CPU使用率过高: 85.0%")
