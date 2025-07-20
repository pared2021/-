# 🔧 配置指南

## 📖 概述

本文档详细介绍游戏自动化工具的配置系统，包括配置文件结构、配置选项说明、配置最佳实践和故障排除指导。

## 🏗️ 配置系统概述

### 配置架构

游戏自动化工具采用分层配置架构：

```
配置优先级（从高到低）：
┌─────────────────────┐
│    运行时参数配置      │  最高优先级
├─────────────────────┤
│    用户配置文件       │  settings.json
├─────────────────────┤
│    模块默认配置       │  各模块内置默认值
├─────────────────────┤
│    系统默认配置       │  最低优先级
└─────────────────────┘
```

### 配置管理器

```python
from src.services.config import Config

# 获取配置管理器
config = Config()

# 读取配置值
window_interval = config.get('window.screenshot_interval', 0.1)

# 设置配置值
config.set('analysis.confidence_threshold', 0.9)

# 保存配置
config.save()
```

## 📁 配置文件结构

### 主配置文件 (`settings.json`)

```json
{
  "version": "1.0.0",
  "last_modified": "2024-01-01T00:00:00Z",
  
  "window": {
    "screenshot_interval": 0.1,
    "activation_delay": 0.5,
    "capture_method": "auto",
    "target_fps": 30,
    "max_window_search_time": 5.0
  },
  
  "analysis": {
    "mode": "hybrid",
    "confidence_threshold": 0.8,
    "max_processing_time": 1.0,
    "enable_caching": true,
    "cache_size": 100,
    "parallel_processing": true,
    "max_workers": 4
  },
  
  "detection": {
    "object_detection": {
      "enabled": true,
      "model_path": "models/yolo_v5.onnx",
      "confidence_threshold": 0.7,
      "nms_threshold": 0.4,
      "max_detections": 100,
      "input_size": [640, 640],
      "class_names": ["button", "text", "icon", "menu"]
    },
    
    "text_recognition": {
      "enabled": true,
      "engine": "easyocr",
      "languages": ["en", "zh"],
      "min_confidence": 0.6,
      "preprocess": true,
      "gpu_acceleration": false
    },
    
    "ui_detection": {
      "enabled": true,
      "element_types": ["button", "text", "image", "input"],
      "state_detection": true,
      "color_analysis": true,
      "template_matching": {
        "enabled": true,
        "threshold": 0.8,
        "template_path": "templates/"
      }
    }
  },
  
  "automation": {
    "action_delay": {
      "min": 0.1,
      "max": 0.3,
      "random": true
    },
    "mouse": {
      "move_speed": 1.0,
      "click_duration": 0.05,
      "double_click_interval": 0.2,
      "smooth_movement": true,
      "bezier_curves": true
    },
    "keyboard": {
      "key_press_duration": 0.05,
      "key_interval": 0.02,
      "typing_speed": 100
    },
    "retry": {
      "max_attempts": 3,
      "retry_delay": 1.0,
      "exponential_backoff": true
    }
  },
  
  "performance": {
    "memory_limit": "1GB",
    "gpu_memory_limit": "2GB",
    "optimization_level": "balanced",
    "profiling_enabled": false,
    "threading": {
      "max_threads": 8,
      "thread_pool_size": 4
    }
  },
  
  "logging": {
    "level": "INFO",
    "file_enabled": true,
    "console_enabled": true,
    "log_file": "logs/automation.log",
    "max_file_size": "10MB",
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "modules": {
      "src.core": "DEBUG",
      "src.services": "INFO",
      "src.ui": "WARNING"
    }
  },
  
  "security": {
    "safe_mode": true,
    "allowed_processes": ["game.exe", "notepad.exe"],
    "blocked_operations": ["file_delete", "registry_modify"],
    "sandbox_mode": false
  },
  
  "ui": {
    "theme": "dark",
    "language": "zh_CN",
    "font_size": 12,
    "window_size": [1200, 800],
    "auto_save_interval": 300,
    "remember_settings": true
  },
  
  "plugins": {
    "enabled": ["core_analyzer", "basic_automation"],
    "disabled": ["experimental_features"],
    "plugin_paths": ["plugins/", "custom_plugins/"],
    "auto_load": true
  }
}
```

### 模块特定配置

#### 游戏特定配置 (`games/`)

```json
// games/example_game.json
{
  "game_name": "ExampleGame",
  "executable": "game.exe",
  "window_title": "Example Game",
  "
  
  "ui_elements": {
    "main_menu": {
      "start_button": {"bbox": [400, 300, 200, 50], "confidence": 0.9},
      "settings_button": {"bbox": [400, 360, 200, 50], "confidence": 0.9}
    },
    "in_game": {
      "health_bar": {"bbox": [50, 50, 200, 20], "type": "progress_bar"},
      "inventory_button": {"bbox": [750, 50, 50, 50], "type": "button"}
    }
  },
  
  "states": {
    "main_menu": {
      "detection_method": "template_matching",
      "template": "templates/main_menu.png",
      "confidence": 0.8
    },
    "in_game": {
      "detection_method": "ui_elements",
      "required_elements": ["health_bar", "inventory_button"]
    }
  },
  
  "actions": {
    "start_game": {
      "sequence": [
        {"type": "click", "target": "start_button"},
        {"type": "wait", "duration": 3.0}
      ]
    },
    "open_inventory": {
      "sequence": [
        {"type": "click", "target": "inventory_button"}
      ]
    }
  }
}
```

#### 模型配置 (`models/config.json`)

```json
{
  "object_detection": {
    "yolo_v5": {
      "model_path": "models/yolo_v5.onnx",
      "input_size": [640, 640],
      "confidence_threshold": 0.7,
      "nms_threshold": 0.4,
      "providers": ["CUDAExecutionProvider", "CPUExecutionProvider"]
    }
  },
  
  "text_recognition": {
    "easyocr": {
      "model_storage_directory": "models/easyocr/",
      "download": true,
      "gpu": false
    },
    "paddleocr": {
      "model_dir": "models/paddleocr/",
      "use_angle_cls": true,
      "use_gpu": false
    }
  },
  
  "classification": {
    "ui_classifier": {
      "model_path": "models/ui_classifier.onnx",
      "input_size": [224, 224],
      "class_names": ["button", "text", "icon", "background"]
    }
  }
}
```

## ⚙️ 配置选项详解

### 窗口捕获配置 (`window`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `screenshot_interval` | float | 0.1 | 截图间隔（秒） |
| `activation_delay` | float | 0.5 | 窗口激活延迟 |
| `capture_method` | string | "auto" | 捕获方式：auto/gdi/dxgi/mss |
| `target_fps` | int | 30 | 目标帧率 |
| `max_window_search_time` | float | 5.0 | 最大窗口搜索时间 |

**捕获方式说明**:
- `auto`: 自动选择最优方式
- `gdi`: Windows GDI捕获（兼容性好）
- `dxgi`: DirectX捕获（性能高，适合游戏）
- `mss`: MSS库捕获（跨平台）

### 分析配置 (`analysis`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `mode` | string | "hybrid" | 分析模式：traditional/deep_learning/hybrid/adaptive |
| `confidence_threshold` | float | 0.8 | 全局置信度阈值 |
| `max_processing_time` | float | 1.0 | 最大处理时间（秒） |
| `enable_caching` | bool | true | 是否启用结果缓存 |
| `cache_size` | int | 100 | 缓存大小 |
| `parallel_processing` | bool | true | 是否启用并行处理 |
| `max_workers` | int | 4 | 最大工作线程数 |

**分析模式说明**:
- `traditional`: 仅使用传统图像处理（速度快）
- `deep_learning`: 仅使用深度学习（准确度高）
- `hybrid`: 混合使用（平衡性能和准确性）
- `adaptive`: 根据内容自适应选择

### 检测配置 (`detection`)

#### 目标检测 (`object_detection`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | true | 是否启用目标检测 |
| `model_path` | string | - | 模型文件路径 |
| `confidence_threshold` | float | 0.7 | 检测置信度阈值 |
| `nms_threshold` | float | 0.4 | NMS阈值 |
| `max_detections` | int | 100 | 最大检测数量 |
| `input_size` | array | [640, 640] | 模型输入尺寸 |

#### 文本识别 (`text_recognition`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | true | 是否启用文本识别 |
| `engine` | string | "easyocr" | OCR引擎：easyocr/paddleocr/tesseract |
| `languages` | array | ["en", "zh"] | 支持的语言 |
| `min_confidence` | float | 0.6 | 最小置信度 |
| `preprocess` | bool | true | 是否预处理图像 |
| `gpu_acceleration` | bool | false | 是否使用GPU加速 |

### 自动化配置 (`automation`)

#### 动作延迟 (`action_delay`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `min` | float | 0.1 | 最小延迟（秒） |
| `max` | float | 0.3 | 最大延迟（秒） |
| `random` | bool | true | 是否随机延迟 |

#### 鼠标配置 (`mouse`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `move_speed` | float | 1.0 | 移动速度倍数 |
| `click_duration` | float | 0.05 | 点击持续时间 |
| `double_click_interval` | float | 0.2 | 双击间隔 |
| `smooth_movement` | bool | true | 是否平滑移动 |
| `bezier_curves` | bool | true | 是否使用贝塞尔曲线 |

### 性能配置 (`performance`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `memory_limit` | string | "1GB" | 内存限制 |
| `gpu_memory_limit` | string | "2GB" | GPU内存限制 |
| `optimization_level` | string | "balanced" | 优化级别：speed/balanced/accuracy |
| `profiling_enabled` | bool | false | 是否启用性能分析 |

### 日志配置 (`logging`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `level` | string | "INFO" | 日志级别：DEBUG/INFO/WARNING/ERROR |
| `file_enabled` | bool | true | 是否输出到文件 |
| `console_enabled` | bool | true | 是否输出到控制台 |
| `log_file` | string | "logs/automation.log" | 日志文件路径 |
| `max_file_size` | string | "10MB" | 最大文件大小 |
| `backup_count` | int | 5 | 备份文件数量 |

## 🎯 配置最佳实践

### 1. 性能优化配置

#### 高性能配置（牺牲一些准确性换取速度）

```json
{
  "analysis": {
    "mode": "traditional",
    "confidence_threshold": 0.7,
    "max_processing_time": 0.5,
    "parallel_processing": true,
    "max_workers": 8
  },
  "detection": {
    "object_detection": {
      "input_size": [416, 416],
      "max_detections": 50
    },
    "text_recognition": {
      "engine": "easyocr",
      "gpu_acceleration": true,
      "preprocess": false
    }
  },
  "window": {
    "screenshot_interval": 0.05,
    "capture_method": "dxgi"
  }
}
```

#### 高精度配置（牺牲一些速度换取准确性）

```json
{
  "analysis": {
    "mode": "deep_learning",
    "confidence_threshold": 0.9,
    "max_processing_time": 2.0,
    "enable_caching": true
  },
  "detection": {
    "object_detection": {
      "input_size": [640, 640],
      "confidence_threshold": 0.8,
      "max_detections": 200
    },
    "text_recognition": {
      "engine": "paddleocr",
      "min_confidence": 0.8,
      "preprocess": true
    }
  },
  "window": {
    "screenshot_interval": 0.2,
    "capture_method": "auto"
  }
}
```

### 2. 内存优化配置

```json
{
  "performance": {
    "memory_limit": "512MB",
    "optimization_level": "speed"
  },
  "analysis": {
    "cache_size": 50,
    "max_workers": 2
  },
  "detection": {
    "object_detection": {
      "input_size": [320, 320],
      "max_detections": 30
    }
  }
}
```

### 3. 开发调试配置

```json
{
  "logging": {
    "level": "DEBUG",
    "modules": {
      "src.core": "DEBUG",
      "src.services": "DEBUG",
      "src.ui": "INFO"
    }
  },
  "performance": {
    "profiling_enabled": true
  },
  "analysis": {
    "enable_caching": false
  }
}
```

## 🔧 配置API使用

### 基本配置操作

```python
from src.services.config import Config

# 创建配置管理器
config = Config()

# 读取配置
screenshot_interval = config.get('window.screenshot_interval')
analysis_mode = config.get('analysis.mode', 'hybrid')

# 设置配置
config.set('analysis.confidence_threshold', 0.9)
config.set('logging.level', 'DEBUG')

# 批量更新配置
config.update({
    'window.screenshot_interval': 0.05,
    'analysis.mode': 'traditional',
    'detection.object_detection.enabled': True
})

# 保存配置到文件
config.save()

# 重新加载配置
config.reload()
```

### 配置验证

```python
# 验证配置
try:
    config.validate()
    print("配置验证通过")
except ConfigError as e:
    print(f"配置错误: {e}")

# 获取配置架构
schema = config.get_schema()
print(f"支持的配置项: {schema.keys()}")

# 检查配置项是否存在
if config.has('analysis.mode'):
    print("分析模式配置存在")
```

### 配置监听

```python
# 注册配置变化监听器
def on_config_changed(key, old_value, new_value):
    print(f"配置 {key} 从 {old_value} 变更为 {new_value}")

config.add_listener('analysis.mode', on_config_changed)

# 移除监听器
config.remove_listener('analysis.mode', on_config_changed)
```

### 运行时配置

```python
# 临时配置（不保存到文件）
with config.temporary():
    config.set('analysis.mode', 'traditional')
    # 在这个上下文中使用临时配置
    result = analyze_frame(frame)
# 退出上下文后配置自动恢复

# 配置上下文管理器
with config.context({'analysis.mode': 'deep_learning'}):
    # 使用临时配置进行分析
    result = analyze_frame(frame)
```

## 🚨 故障排除

### 常见配置问题

#### 1. 配置文件格式错误

**错误现象**: 程序启动时报JSON解析错误

**解决方法**:
```bash
# 验证JSON格式
python -m json.tool settings.json

# 或使用在线JSON验证器
# 检查是否有多余的逗号、缺少引号等
```

#### 2. 配置路径不存在

**错误现象**: 模型或模板文件找不到

**解决方法**:
```json
{
  "detection": {
    "object_detection": {
      "model_path": "models/yolo_v5.onnx"  // 确保文件存在
    }
  }
}
```

检查文件是否存在：
```python
import os
model_path = "models/yolo_v5.onnx"
if not os.path.exists(model_path):
    print(f"模型文件不存在: {model_path}")
```

#### 3. 内存配置过低

**错误现象**: 程序运行时内存不足

**解决方法**:
```json
{
  "performance": {
    "memory_limit": "2GB",  // 增加内存限制
    "optimization_level": "speed"
  },
  "analysis": {
    "cache_size": 50,       // 减少缓存大小
    "max_workers": 2        // 减少工作线程数
  }
}
```

#### 4. GPU配置问题

**错误现象**: GPU加速失败

**解决方法**:
```json
{
  "detection": {
    "text_recognition": {
      "gpu_acceleration": false  // 暂时禁用GPU
    }
  }
}
```

检查GPU可用性：
```python
import torch
print(f"CUDA可用: {torch.cuda.is_available()}")
print(f"GPU数量: {torch.cuda.device_count()}")
```

### 配置重置

#### 重置为默认配置

```python
from src.services.config import Config

config = Config()

# 重置所有配置
config.reset_to_defaults()

# 重置特定模块配置
config.reset_module('analysis')

# 备份当前配置
config.backup('backup_20240101.json')

# 从备份恢复配置
config.restore('backup_20240101.json')
```

#### 配置迁移

```python
# 从旧版本配置迁移
config.migrate_from_version('0.9.0')

# 手动迁移配置项
old_config = load_old_config()
new_config = {
    'window.screenshot_interval': old_config.get('capture_interval', 0.1),
    'analysis.mode': old_config.get('analysis_type', 'hybrid')
}
config.update(new_config)
```

## 📊 配置监控和调试

### 配置状态监控

```python
# 获取当前配置状态
status = config.get_status()
print(f"配置文件: {status['config_file']}")
print(f"最后修改: {status['last_modified']}")
print(f"配置项数量: {status['item_count']}")
print(f"验证状态: {status['validation_status']}")

# 获取配置使用统计
stats = config.get_usage_stats()
print(f"最常用配置项: {stats['most_used']}")
print(f"从未使用配置项: {stats['unused']}")
```

### 配置调试

```python
# 启用配置调试模式
config.enable_debug_mode()

# 跟踪配置访问
config.set_trace_mode(True)

# 导出配置报告
config.export_debug_report('config_debug.json')
```

---

**文档版本**: v1.0  
**最后更新**: 2024年  
**相关文档**: [README.md](../../README.md) | [架构设计](../architecture/architecture.md) | [开发者指南](developer-guide.md)

<div align="center">

**🔧 配置是系统的灵魂，合理的配置让自动化更智能！**

</div>