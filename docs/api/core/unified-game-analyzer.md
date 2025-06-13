# UnifiedGameAnalyzer API 文档

## 概述

`UnifiedGameAnalyzer` 是游戏自动化工具的核心组件，融合了传统图像处理和深度学习技术，提供统一的游戏画面分析接口。

## 类定义

```python
from src.core.unified_game_analyzer import UnifiedGameAnalyzer
```

## 构造函数

### `__init__(logger, image_processor, config)`

创建统一游戏分析器实例。

**参数**:
- `logger` (`GameLogger`): 日志记录器实例
- `image_processor` (`ImageProcessor`): 图像处理器实例  
- `config` (`Config`): 配置管理器实例

**示例**:
```python
from src.common.containers import DIContainer

container = DIContainer()
analyzer = UnifiedGameAnalyzer(
    logger=container.get('Logger'),
    image_processor=container.get('ImageProcessor'),
    config=container.get('Config')
)
```

## 核心方法

### `analyze_frame(frame, analysis_options=None)`

分析游戏画面帧，返回检测结果。

**参数**:
- `frame` (`np.ndarray`): 游戏画面的numpy数组，格式为BGR
- `analysis_options` (`Dict[str, Any]`, 可选): 分析选项配置

**返回值**:
- `Dict[str, Any]`: 分析结果字典

**返回值格式**:
```python
{
    'objects': [
        {
            'label': str,           # 对象标签
            'confidence': float,    # 置信度 (0-1)
            'bbox': (x, y, w, h),  # 边界框坐标
            'center': (x, y),      # 中心点坐标
            'metadata': dict       # 额外元数据
        }
    ],
    'text_regions': [
        {
            'text': str,           # 识别的文本
            'confidence': float,   # 置信度
            'bbox': (x, y, w, h),  # 文本区域
            'language': str        # 语言代码
        }
    ],
    'ui_elements': [
        {
            'type': str,           # UI元素类型
            'state': str,          # 元素状态
            'bbox': (x, y, w, h),  # 元素位置
            'clickable': bool      # 是否可点击
        }
    ],
    'game_state': {
        'scene': str,              # 当前场景
        'state': str,              # 游戏状态
        'progress': float,         # 进度信息
        'timestamp': float         # 分析时间戳
    },
    'analysis_info': {
        'methods_used': List[str], # 使用的分析方法
        'processing_time': float,  # 处理时间
        'confidence': float,       # 整体置信度
        'frame_hash': str          # 帧哈希值
    }
}
```

**异常**:
- `ValueError`: 当frame为空或格式不正确时
- `AnalysisError`: 当分析过程出现错误时
- `ConfigError`: 当配置不正确时

**示例**:
```python
import cv2
import numpy as np

# 捕获游戏画面
frame = capture_game_frame()

# 分析画面
result = analyzer.analyze_frame(frame)

# 处理结果
print(f"检测到 {len(result['objects'])} 个对象")
for obj in result['objects']:
    print(f"对象: {obj['label']}, 置信度: {obj['confidence']:.2f}")

# 获取可点击的UI元素
clickable_elements = [
    elem for elem in result['ui_elements'] 
    if elem['clickable']
]
```

### `add_detector(name, detector)`

添加自定义检测器。

**参数**:
- `name` (`str`): 检测器名称
- `detector` (`Callable`): 检测器函数，接受np.ndarray参数

**示例**:
```python
def custom_button_detector(frame):
    """自定义按钮检测器"""
    # 实现检测逻辑
    return {'buttons': [...]}

analyzer.add_detector('custom_button', custom_button_detector)
```

### `remove_detector(name)`

移除指定的检测器。

**参数**:
- `name` (`str`): 要移除的检测器名称

### `set_analysis_mode(mode)`

设置分析模式。

**参数**:
- `mode` (`str`): 分析模式
  - `'traditional'`: 仅使用传统图像处理
  - `'deep_learning'`: 仅使用深度学习方法
  - `'hybrid'`: 混合模式（默认）
  - `'adaptive'`: 自适应模式

**示例**:
```python
# 设置为传统模式（更快但精度较低）
analyzer.set_analysis_mode('traditional')

# 设置为深度学习模式（更准确但更慢）
analyzer.set_analysis_mode('deep_learning')

# 设置为自适应模式（根据内容自动选择）
analyzer.set_analysis_mode('adaptive')
```

### `configure(config_dict)`

动态配置分析器参数。

**参数**:
- `config_dict` (`Dict[str, Any]`): 配置字典

**配置选项**:
```python
config = {
    'detection': {
        'confidence_threshold': 0.8,    # 检测置信度阈值
        'nms_threshold': 0.4,           # NMS阈值
        'max_detections': 100           # 最大检测数量
    },
    'ocr': {
        'enabled': True,                # 是否启用OCR
        'languages': ['en', 'zh'],      # 支持的语言
        'min_confidence': 0.6           # OCR最小置信度
    },
    'ui_detection': {
        'enabled': True,                # 是否启用UI检测
        'element_types': ['button', 'text', 'image'],
        'state_detection': True         # 是否检测元素状态
    },
    'performance': {
        'max_processing_time': 1.0,     # 最大处理时间（秒）
        'enable_caching': True,         # 是否启用缓存
        'cache_size': 100               # 缓存大小
    }
}

analyzer.configure(config)
```

## 高级功能

### `analyze_sequence(frames, sequence_options=None)`

分析视频帧序列，提供时序分析。

**参数**:
- `frames` (`List[np.ndarray]`): 帧序列
- `sequence_options` (`Dict[str, Any]`, 可选): 序列分析选项

**返回值**:
- `Dict[str, Any]`: 序列分析结果

**示例**:
```python
# 分析连续帧序列
frames = capture_frame_sequence(duration=2.0)
sequence_result = analyzer.analyze_sequence(frames)

# 获取运动信息
motion_info = sequence_result['motion_analysis']
object_tracking = sequence_result['object_tracking']
```

### `batch_analyze(frames, batch_options=None)`

批量分析多个帧，支持并行处理。

**参数**:
- `frames` (`List[np.ndarray]`): 要分析的帧列表
- `batch_options` (`Dict[str, Any]`, 可选): 批处理选项

**返回值**:
- `List[Dict[str, Any]]`: 分析结果列表

**示例**:
```python
# 批量分析
frames = load_test_frames()
batch_options = {
    'parallel': True,
    'max_workers': 4,
    'chunk_size': 10
}

results = analyzer.batch_analyze(frames, batch_options)
```

### `create_analysis_pipeline(steps)`

创建自定义分析流水线。

**参数**:
- `steps` (`List[str]`): 分析步骤列表

**可用步骤**:
- `preprocess`: 预处理
- `object_detection`: 目标检测
- `text_recognition`: 文本识别
- `ui_analysis`: UI分析
- `state_recognition`: 状态识别
- `postprocess`: 后处理

**示例**:
```python
# 创建自定义分析流水线
pipeline = analyzer.create_analysis_pipeline([
    'preprocess',
    'object_detection',
    'ui_analysis'
])

# 使用自定义流水线分析
result = pipeline(frame)
```

## 性能优化

### `enable_gpu_acceleration()`

启用GPU加速（需要CUDA支持）。

### `set_cache_policy(policy)`

设置缓存策略。

**参数**:
- `policy` (`str`): 缓存策略
  - `'lru'`: 最近最少使用
  - `'fifo'`: 先进先出
  - `'adaptive'`: 自适应缓存

### `optimize_for_speed()`

优化分析器以提高速度。

### `optimize_for_accuracy()`

优化分析器以提高准确性。

## 事件和回调

### `set_progress_callback(callback)`

设置进度回调函数。

**参数**:
- `callback` (`Callable[[float], None]`): 进度回调函数

**示例**:
```python
def on_progress(progress):
    print(f"分析进度: {progress:.1%}")

analyzer.set_progress_callback(on_progress)
```

### `set_error_callback(callback)`

设置错误回调函数。

**参数**:
- `callback` (`Callable[[Exception], None]`): 错误回调函数

## 调试和诊断

### `get_performance_stats()`

获取性能统计信息。

**返回值**:
```python
{
    'total_frames_processed': int,
    'average_processing_time': float,
    'cache_hit_rate': float,
    'memory_usage': int,          # 字节
    'gpu_utilization': float,     # 0-1
    'method_usage_stats': dict    # 各方法使用统计
}
```

### `export_debug_info(frame, output_path)`

导出调试信息。

**参数**:
- `frame` (`np.ndarray`): 要调试的帧
- `output_path` (`str`): 输出路径

### `visualize_analysis(frame, result, output_path=None)`

可视化分析结果。

**参数**:
- `frame` (`np.ndarray`): 原始帧
- `result` (`Dict[str, Any]`): 分析结果
- `output_path` (`str`, 可选): 输出路径，如果为None则显示

**示例**:
```python
# 可视化分析结果
frame = capture_frame()
result = analyzer.analyze_frame(frame)
analyzer.visualize_analysis(frame, result, "debug_output.png")
```

## 错误处理

### 异常类型

- `AnalysisError`: 分析过程中的一般错误
- `ModelLoadingError`: 模型加载错误
- `InvalidFrameError`: 无效帧错误
- `ConfigurationError`: 配置错误
- `TimeoutError`: 分析超时错误

### 错误恢复

分析器内置了错误恢复机制：

```python
# 自动错误恢复示例
try:
    result = analyzer.analyze_frame(frame)
except AnalysisError as e:
    # 分析器会自动尝试恢复
    if analyzer.can_recover(e):
        result = analyzer.recover_and_retry(frame)
    else:
        # 使用默认结果
        result = analyzer.get_default_result()
```

## 使用示例

### 基本使用

```python
from src.common.containers import DIContainer

# 初始化
container = DIContainer()
container.initialize()
analyzer = container.get('UnifiedGameAnalyzer')

# 分析单帧
frame = capture_game_frame()
result = analyzer.analyze_frame(frame)

# 处理结果
for obj in result['objects']:
    print(f"发现对象: {obj['label']} at {obj['bbox']}")
```

### 高级使用

```python
# 自定义配置
config = {
    'detection': {'confidence_threshold': 0.9},
    'ocr': {'languages': ['zh']},
    'performance': {'enable_caching': True}
}
analyzer.configure(config)

# 添加自定义检测器
def detect_health_bar(frame):
    # 检测血条逻辑
    return {'health_bars': [...]}

analyzer.add_detector('health_bar', detect_health_bar)

# 设置回调
analyzer.set_progress_callback(lambda p: print(f"进度: {p:.1%}"))

# 分析
result = analyzer.analyze_frame(frame)
health_info = result.get('health_bars', [])
```

## 性能建议

1. **选择合适的分析模式**: 根据需求选择`traditional`、`deep_learning`或`hybrid`模式
2. **启用缓存**: 对于重复内容，缓存可以显著提高性能
3. **批量处理**: 对于多帧处理，使用`batch_analyze`比单独处理更高效  
4. **GPU加速**: 对于深度学习模式，启用GPU可以显著提升速度
5. **合理设置阈值**: 适当调整置信度阈值平衡准确性和召回率

---

**API版本**: v1.0  
**最后更新**: 2024年  
**相关文档**: [架构设计](../architecture.md) | [开发者指南](../developer-guide.md)