# 窗口管理器迁移指南

## 概述

本指南说明如何从旧的窗口管理系统迁移到新的统一窗口管理系统。新系统解决了以下核心问题：

- **多重WindowInfo定义冲突**：统一了所有WindowInfo数据结构
- **数据流混乱**：提供了清晰的数据转换和流向
- **架构层次混乱**：建立了清晰的架构边界
- **接口不一致**：统一了所有窗口操作接口

## 新架构组件

### 1. 统一数据模型
- `src/core/domain/window_models.py` - 统一的WindowInfo和相关数据结构

### 2. 统一窗口管理器
- `src/infrastructure/window_manager/unified_window_manager.py` - 核心窗口管理器
- `src/infrastructure/window_manager/window_manager_factory.py` - 工厂模式创建管理器

### 3. 向后兼容适配器
- `src/infrastructure/adapters/legacy_window_adapter.py` - 平滑迁移适配器

### 4. 统一接口
- `src/core/interfaces/window_manager.py` - 标准化接口定义

## 迁移步骤

### 步骤1：使用遗留适配器（推荐）

最简单的迁移方式是使用`LegacyWindowAdapter`，它提供了与旧接口兼容的方法：

```python
# 旧代码
from src.services.window_manager import GameWindowManager
window_manager = GameWindowManager()
windows = window_manager.get_all_windows()

# 新代码 - 使用遗留适配器
from src.infrastructure.adapters.legacy_window_adapter import get_legacy_window_adapter
adapter = get_legacy_window_adapter()
windows = adapter.get_window_list()  # 返回(hwnd, title)元组列表
```

### 步骤2：逐步迁移到统一接口

```python
# 获取统一格式的窗口信息
from src.infrastructure.adapters.legacy_window_adapter import get_legacy_window_adapter
adapter = get_legacy_window_adapter()

# 获取统一格式的窗口列表
unified_windows = adapter.get_unified_window_list()  # 返回UnifiedWindowInfo对象列表

# 获取单个窗口的统一信息
window_info = adapter.get_unified_window_info(hwnd)
```

### 步骤3：直接使用统一窗口管理器

```python
# 使用工厂创建窗口管理器
from src.infrastructure.window_manager import get_window_manager

window_manager = get_window_manager({
    'cache_enabled': True,
    'auto_refresh': True,
    'refresh_interval': 1.0
})

# 使用统一接口
windows = window_manager.get_window_list()
window_info = window_manager.find_window_by_title("游戏窗口")
screenshot = window_manager.capture_window(window_info.handle)
```

## 主要变化

### WindowInfo数据结构

**旧版本（多个不兼容的定义）：**
```python
# services.py中的WindowInfo
class WindowInfo:
    handle: int
    title: str
    class_name: str
    rect: Rectangle
    is_visible: bool
    is_active: bool

# adapters.py中的WindowInfo  
class WindowInfo:
    title: str
    handle: int
    pid: int
    rect: tuple
    is_visible: bool
    is_active: bool
```

**新版本（统一定义）：**
```python
# core/domain/window_models.py
@dataclass
class WindowInfo:
    handle: int
    title: str
    class_name: str
    process_id: int
    rect: WindowRect
    state: WindowState
    window_type: WindowType
    parent_handle: Optional[int] = None
    child_handles: List[int] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
```

### 接口变化

| 旧接口 | 新接口 | 说明 |
|--------|--------|------|
| `get_all_windows()` | `get_window_list()` | 返回格式统一 |
| `get_window_info(hwnd)` | `get_window_info(handle)` | 参数名统一 |
| `capture_window(hwnd)` | `capture_window(handle)` | 参数名统一 |
| 多个不同的WindowInfo | 统一的WindowInfo | 数据结构统一 |

## 错误处理

新系统提供了统一的错误处理：

```python
from src.core.interfaces.window_manager import (
    WindowManagerError,
    WindowNotFoundError,
    WindowOperationError
)

try:
    window_info = window_manager.find_window_by_title("不存在的窗口")
except WindowNotFoundError as e:
    print(f"窗口未找到: {e}")
except WindowOperationError as e:
    print(f"窗口操作失败: {e}")
except WindowManagerError as e:
    print(f"窗口管理器错误: {e}")
```

## 性能优化

新系统包含多项性能优化：

1. **缓存机制**：避免重复的系统调用
2. **批量操作**：支持批量窗口操作
3. **异步支持**：支持异步窗口操作
4. **事件驱动**：支持窗口事件监听

```python
# 启用缓存
window_manager = get_window_manager({'cache_enabled': True})

# 批量操作
handles = [hwnd1, hwnd2, hwnd3]
window_infos = window_manager.get_windows_info(handles)

# 事件监听
def on_window_created(window_info):
    print(f"新窗口创建: {window_info.title}")

window_manager.add_event_handler('window_created', on_window_created)
window_manager.start_monitoring()
```

## 配置选项

新系统支持丰富的配置选项：

```python
config = {
    'cache_enabled': True,           # 启用缓存
    'cache_ttl': 5.0,               # 缓存生存时间（秒）
    'auto_refresh': True,           # 自动刷新
    'refresh_interval': 1.0,        # 刷新间隔（秒）
    'include_minimized': False,     # 包含最小化窗口
    'include_hidden': False,        # 包含隐藏窗口
    'capture_format': 'RGB',        # 截图格式
    'capture_quality': 95,          # 截图质量
    'event_monitoring': True,       # 事件监控
    'performance_monitoring': True, # 性能监控
    'debug_mode': False            # 调试模式
}

window_manager = get_window_manager(config)
```

## 测试

新系统包含完整的测试覆盖：

```bash
# 运行窗口管理器测试
python -m pytest tests/infrastructure/window_manager/ -v

# 运行适配器测试
python -m pytest tests/infrastructure/adapters/test_legacy_window_adapter.py -v
```

## 故障排除

### 常见问题

1. **导入错误**：确保新模块路径正确
2. **数据格式不匹配**：使用遗留适配器进行转换
3. **性能问题**：检查缓存配置和刷新间隔
4. **窗口找不到**：检查窗口过滤条件

### 调试模式

```python
# 启用调试模式
window_manager = get_window_manager({'debug_mode': True})

# 查看详细日志
import logging
logging.getLogger('window_manager').setLevel(logging.DEBUG)
```

## 总结

新的统一窗口管理系统提供了：

✅ **统一的数据模型**：解决了多重定义冲突  
✅ **清晰的架构**：明确的层次和职责分离  
✅ **向后兼容**：平滑的迁移路径  
✅ **性能优化**：缓存、批量操作、异步支持  
✅ **丰富的功能**：事件监听、配置管理、错误处理  
✅ **完整的测试**：确保系统稳定性  

建议采用渐进式迁移策略，先使用遗留适配器，然后逐步迁移到统一接口。