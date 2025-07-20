# 类型统一迁移指南

本指南帮助您将现有代码从多重定义的类型迁移到新的统一类型定义。

## 概述

我们已经创建了统一的类型定义来解决多重定义问题：

- `UnifiedGameState` - 统一游戏状态
- `UnifiedPerformanceMetrics` - 统一性能指标
- `UnifiedActionType` - 统一动作类型
- `UnifiedTemplateMatchResult` - 统一模板匹配结果

## 迁移步骤

### 1. GameState 迁移

#### 原有定义位置：
- `src/services/game_state.py` - 游戏状态管理服务
- `src/services/vision/state_recognizer.py` - 视觉识别状态数据
- `src/core/game_adapter.py` - 游戏适配器状态接口

#### 迁移方法：

```python
# 旧代码
from src.services.vision.state_recognizer import GameState

# 新代码
from src.core.types import UnifiedGameState

# 兼容性转换
def migrate_vision_game_state(old_state):
    return UnifiedGameState(
        name=old_state.name,
        confidence=old_state.confidence,
        features=old_state.features,
        region=old_state.region,
        template_matches=old_state.template_matches
    )
```

### 2. PerformanceMetrics 迁移

#### 原有定义位置：
- `src/performance/performance_monitor.py` - 基础性能监控
- `src/services/monitor/performance_monitor.py` - 服务层性能监控
- `src/common/monitor.py` - 通用监控

#### 迁移方法：

```python
# 旧代码
from src.performance.performance_monitor import PerformanceMetrics

# 新代码
from src.core.types import UnifiedPerformanceMetrics

# 使用兼容方法
legacy_metrics = get_legacy_metrics()
unified_metrics = UnifiedPerformanceMetrics.from_legacy_basic(legacy_metrics)
```

### 3. ActionType 迁移

#### 原有定义位置：
- `src/core/interfaces/services.py` - 服务接口动作类型
- `src/common/action_system.py` - 动作系统类型

#### 迁移方法：

```python
# 旧代码
from src.core.interfaces.services import ActionType

# 新代码
from src.core.types import UnifiedActionType

# 使用兼容方法
old_action = ActionType.CLICK
new_action = UnifiedActionType.from_services_action(old_action)
```

### 4. TemplateMatchResult 迁移

#### 原有定义位置：
- `src/core/interfaces/services.py` - 服务接口匹配结果
- `src/services/image_processor.py` - 图像处理匹配结果

#### 迁移方法：

```python
# 旧代码
from src.services.image_processor import TemplateMatchResult

# 新代码
from src.core.types import UnifiedTemplateMatchResult

# 兼容性转换
old_result = get_template_match_result()
new_result = UnifiedTemplateMatchResult.from_legacy_image_processor(
    location=old_result.location,
    confidence=old_result.confidence,
    template_name=old_result.template_name,
    template_size=old_result.template_size
)
```

## 分阶段迁移建议

### 阶段1：核心模块迁移（高优先级）
1. 更新 `src/core/` 下的所有模块
2. 更新主要的服务接口
3. 更新游戏适配器相关代码

### 阶段2：服务层迁移（中优先级）
1. 更新 `src/services/` 下的模块
2. 更新监控和性能相关模块
3. 更新图像处理相关模块

### 阶段3：应用层迁移（低优先级）
1. 更新自动化脚本
2. 更新测试代码
3. 更新示例代码

## 兼容性保证

在迁移期间，我们提供以下兼容性保证：

1. **向后兼容方法**：所有统一类型都提供 `from_legacy_*` 方法
2. **向前兼容方法**：所有统一类型都提供 `to_legacy_*` 方法
3. **渐进式迁移**：可以逐步迁移，新旧代码可以共存

## 迁移检查清单

- [ ] 识别所有使用旧类型定义的文件
- [ ] 更新导入语句
- [ ] 使用兼容方法转换数据
- [ ] 更新类型注解
- [ ] 运行测试确保功能正常
- [ ] 更新文档和注释

## 常见问题

### Q: 迁移后性能会受影响吗？
A: 统一类型设计时考虑了性能，兼容方法只在迁移期间使用，完全迁移后性能会有所提升。

### Q: 可以部分迁移吗？
A: 是的，提供的兼容方法支持渐进式迁移，新旧代码可以共存。

### Q: 如何处理自定义扩展？
A: 统一类型都提供了 `metadata` 字段用于存储自定义数据，可以保持扩展性。

## 技术支持

如果在迁移过程中遇到问题，请：

1. 查看 `../architecture/analysis-report.md` 了解详细的架构分析
2. 参考统一类型的文档字符串和示例代码
3. 使用提供的兼容方法进行数据转换

## 迁移完成后的清理

迁移完成后，建议：

1. 删除旧的类型定义文件
2. 清理不再使用的导入语句
3. 更新项目文档
4. 运行完整的测试套件

---

**注意**：本迁移指南基于当前的架构分析结果，建议在开始迁移前仔细阅读 `../architecture/analysis-report.md` 文件。