# 👨‍💻 开发者指南

## 📖 概述

欢迎加入游戏自动化工具的开发！本指南将帮助您快速上手项目开发，了解代码规范、开发流程和最佳实践。

## 🚀 开发环境设置

### 系统要求

- **Python**: 3.8+ （推荐 3.9+）
- **操作系统**: Windows 10/11 （主要开发平台）
- **内存**: 最小 8GB RAM （推荐 16GB+）
- **硬盘**: 至少 2GB 可用空间
- **IDE**: 推荐 VS Code 或 PyCharm

### 环境配置步骤

#### 1. 克隆项目

```bash
# 克隆主仓库
git clone https://github.com/yourusername/game-automation-tool.git
cd game-automation-tool

# 创建开发分支
git checkout -b feature/your-feature-name
```

#### 2. 设置虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 升级pip
python -m pip install --upgrade pip
```

#### 3. 安装依赖

```bash
# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 或使用开发脚本
python setup.py develop
```

#### 4. IDE配置

**VS Code 推荐配置** (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "python.sortImports.args": ["--multi-line=3", "--trailing-comma", "--force-grid-wrap=0"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

**推荐扩展**:
- Python
- Pylance
- Black Formatter
- GitLens
- Better Comments

### 验证环境

```bash
# 运行基础测试
python src/tests/directory_refactor_test.py
python src/tests/service_responsibility_test.py

# 检查代码风格
python -m pylint src/
python -m black --check src/

# 类型检查
python -m mypy src/
```

## 📋 代码规范和最佳实践

### 代码风格

我们遵循 **PEP 8** 标准，并使用以下工具强制执行：

#### 格式化工具
```bash
# Black 代码格式化
black src/

# isort 导入排序
isort src/

# 自动修复常见问题
autopep8 --in-place --recursive src/
```

#### 静态分析
```bash
# Pylint 代码质量检查
pylint src/

# Flake8 风格检查
flake8 src/

# Mypy 类型检查
mypy src/
```

### 命名规范

#### 1. 文件和目录命名
```python
# ✅ 推荐
src/core/game_analyzer.py
src/ui/main_window.py
src/services/config_manager.py

# ❌ 避免
src/core/GameAnalyzer.py
src/ui/MainWindow.py
src/services/configManager.py
```

#### 2. 类命名
```python
# ✅ 推荐：Pascal命名法
class GameAnalyzer:
    pass

class ConfigManager:
    pass

# ❌ 避免
class game_analyzer:
    pass

class configManager:
    pass
```

#### 3. 函数和变量命名
```python
# ✅ 推荐：snake_case
def analyze_game_frame(frame_data):
    analysis_result = process_frame(frame_data)
    return analysis_result

# ❌ 避免
def analyzeGameFrame(frameData):
    analysisResult = processFrame(frameData)
    return analysisResult
```

#### 4. 常量命名
```python
# ✅ 推荐：UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30
ANALYSIS_THRESHOLD = 0.8

# ❌ 避免
maxRetryCount = 3
default_timeout = 30
```

### 文档字符串规范

使用 **Google 风格** 的文档字符串：

```python
def analyze_frame(self, frame: np.ndarray, threshold: float = 0.8) -> Dict[str, Any]:
    """分析游戏画面帧。
    
    Args:
        frame: 游戏画面的numpy数组
        threshold: 检测阈值，范围0-1
        
    Returns:
        包含分析结果的字典，格式如下：
        {
            'objects': List[Dict],  # 检测到的对象
            'confidence': float,    # 整体置信度
            'timestamp': float      # 分析时间戳
        }
        
    Raises:
        ValueError: 当frame为空或threshold不在有效范围时
        AnalysisError: 当分析过程出现错误时
        
    Example:
        >>> analyzer = GameAnalyzer()
        >>> frame = capture_game_frame()
        >>> result = analyzer.analyze_frame(frame, threshold=0.9)
        >>> print(f"Found {len(result['objects'])} objects")
    """
    if frame is None or frame.size == 0:
        raise ValueError("Frame cannot be empty")
    
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1")
    
    # 实现分析逻辑...
```

### 异常处理规范

#### 1. 使用分层异常体系
```python
# ✅ 推荐：使用具体的异常类型
from src.common.exceptions import GameAutomationError
from src.services.exceptions import ImageProcessingError

try:
    result = process_image(frame)
except ImageProcessingError as e:
    logger.error(f"Image processing failed: {e}")
    recovery_manager.handle_error(e)
except GameAutomationError as e:
    logger.error(f"General automation error: {e}")
    raise
```

#### 2. 异常链和上下文
```python
# ✅ 推荐：保持异常链
try:
    risky_operation()
except ValueError as e:
    raise ConfigError("Invalid configuration") from e
```

#### 3. 资源清理
```python
# ✅ 推荐：使用上下文管理器
from contextlib import contextmanager

@contextmanager
def managed_capture():
    capture = initialize_capture()
    try:
        yield capture
    finally:
        capture.cleanup()

# 使用方式
with managed_capture() as capture:
    frame = capture.get_frame()
```

### 类型注解规范

```python
from typing import Dict, List, Optional, Union, Callable
import numpy as np

class GameAnalyzer:
    def __init__(self, config: 'Config', logger: 'Logger') -> None:
        self.config = config
        self.logger = logger
        self.detectors: List[Callable] = []
    
    def add_detector(self, detector: Callable[[np.ndarray], Dict]) -> None:
        """添加检测器。"""
        self.detectors.append(detector)
    
    def analyze(self, frame: np.ndarray) -> Optional[Dict[str, Union[str, float]]]:
        """分析帧数据。"""
        if not self.detectors:
            return None
        
        results = {}
        for detector in self.detectors:
            result = detector(frame)
            results.update(result)
        
        return results
```

## 🏗️ 新功能开发流程

### 1. 分析和设计阶段

#### 确定功能归属层次
```python
# 决策流程图
if is_user_interface_related:
    target_layer = "UI"
elif is_business_logic:
    target_layer = "Core"
elif is_technical_service:
    target_layer = "Services"
elif is_infrastructure:
    target_layer = "Common"
```

#### 设计接口
```python
# 示例：设计新的游戏检测器
from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np

class BaseDetector(ABC):
    """检测器基类"""
    
    @abstractmethod
    def detect(self, frame: np.ndarray) -> Dict[str, Any]:
        """检测方法"""
        pass
    
    @abstractmethod
    def configure(self, config: Dict[str, Any]) -> None:
        """配置方法"""
        pass

class ButtonDetector(BaseDetector):
    """按钮检测器实现"""
    
    def detect(self, frame: np.ndarray) -> Dict[str, Any]:
        """检测按钮"""
        # 实现检测逻辑
        return {"buttons": []}
    
    def configure(self, config: Dict[str, Any]) -> None:
        """配置检测器"""
        self.threshold = config.get("threshold", 0.8)
```

### 2. 实现阶段

#### 创建功能分支
```bash
# 创建特性分支
git checkout -b feature/button-detector
git push -u origin feature/button-detector
```

#### 编写实现代码
```python
# src/core/analyzers/button_detector.py
from typing import Dict, Any, List
import cv2
import numpy as np
from ..base_detector import BaseDetector
from ...services.logger import GameLogger

class ButtonDetector(BaseDetector):
    """按钮检测器"""
    
    def __init__(self, logger: GameLogger):
        self.logger = logger
        self.threshold = 0.8
        self.template_cache = {}
    
    def detect(self, frame: np.ndarray) -> Dict[str, Any]:
        """检测画面中的按钮"""
        self.logger.debug("Starting button detection")
        
        try:
            buttons = self._find_buttons(frame)
            self.logger.info(f"Detected {len(buttons)} buttons")
            return {"buttons": buttons}
        except Exception as e:
            self.logger.error(f"Button detection failed: {e}")
            raise
    
    def _find_buttons(self, frame: np.ndarray) -> List[Dict]:
        """查找按钮的核心逻辑"""
        # 实现具体检测算法
        return []
```

#### 编写测试用例
```python
# src/tests/test_button_detector.py
import unittest
import numpy as np
from unittest.mock import Mock
from src.core.analyzers.button_detector import ButtonDetector

class TestButtonDetector(unittest.TestCase):
    """按钮检测器测试"""
    
    def setUp(self):
        """测试设置"""
        self.mock_logger = Mock()
        self.detector = ButtonDetector(self.mock_logger)
    
    def test_detect_empty_frame(self):
        """测试空帧检测"""
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        result = self.detector.detect(frame)
        self.assertEqual(result["buttons"], [])
    
    def test_detect_with_buttons(self):
        """测试含按钮的帧检测"""
        # 创建包含按钮的测试帧
        frame = self._create_test_frame_with_buttons()
        result = self.detector.detect(frame)
        self.assertGreater(len(result["buttons"]), 0)
    
    def _create_test_frame_with_buttons(self):
        """创建包含按钮的测试帧"""
        frame = np.zeros((300, 400, 3), dtype=np.uint8)
        # 绘制按钮形状
        cv2.rectangle(frame, (50, 50), (150, 100), (255, 255, 255), -1)
        return frame

if __name__ == '__main__':
    unittest.main()
```

### 3. 集成阶段

#### 更新依赖注入配置
```python
# src/common/containers.py
def _setup_analyzers(self):
    """设置分析器"""
    # 注册新的按钮检测器
    self.register(
        'ButtonDetector',
        lambda: ButtonDetector(self.get('Logger')),
        singleton=True
    )
    
    # 更新统一分析器
    unified_analyzer = self.get('UnifiedGameAnalyzer')
    unified_analyzer.add_detector('button', self.get('ButtonDetector'))
```

#### 更新配置文件
```json
{
  "analyzers": {
    "button_detector": {
      "enabled": true,
      "threshold": 0.8,
      "template_path": "templates/buttons/"
    }
  }
}
```

### 4. 测试和验证

#### 运行测试套件
```bash
# 运行单元测试
python -m pytest src/tests/test_button_detector.py -v

# 运行集成测试
python -m pytest src/tests/integration/ -v

# 运行架构测试
python src/tests/service_responsibility_test.py
```

#### 性能测试
```python
# src/tests/performance/test_button_detector_performance.py
import time
import numpy as np
from src.core.analyzers.button_detector import ButtonDetector

def test_detection_performance():
    """测试检测性能"""
    detector = ButtonDetector(mock_logger)
    frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
    
    # 预热
    for _ in range(10):
        detector.detect(frame)
    
    # 性能测试
    start_time = time.time()
    for _ in range(100):
        detector.detect(frame)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 100
    assert avg_time < 0.05, f"Detection too slow: {avg_time:.3f}s"
```

## 🐛 调试和测试指南

### 调试技巧

#### 1. 使用日志进行调试
```python
# 设置详细日志级别
import logging
logging.getLogger('src.core').setLevel(logging.DEBUG)

# 在关键位置添加日志
self.logger.debug(f"Processing frame: shape={frame.shape}")
self.logger.info(f"Detection result: {len(objects)} objects found")
```

#### 2. 使用调试工具
```python
# 使用pdb调试
import pdb
pdb.set_trace()

# 使用ipdb（推荐）
import ipdb
ipdb.set_trace()

# 使用IDE断点
# 在IDE中设置断点进行调试
```

#### 3. 可视化调试
```python
def visualize_detection_result(frame, result):
    """可视化检测结果"""
    import cv2
    vis_frame = frame.copy()
    
    for obj in result.get('objects', []):
        x, y, w, h = obj['bbox']
        cv2.rectangle(vis_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(vis_frame, obj['label'], (x, y-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    cv2.imshow('Detection Result', vis_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
```

### 测试策略

#### 1. 单元测试
```python
# 测试单个功能
class TestGameAnalyzer(unittest.TestCase):
    def test_analyze_empty_frame(self):
        """测试空帧分析"""
        analyzer = GameAnalyzer()
        result = analyzer.analyze(np.zeros((100, 100, 3)))
        self.assertIsNotNone(result)
        self.assertEqual(len(result['objects']), 0)
```

#### 2. 集成测试
```python
# 测试组件集成
class TestAnalyzerIntegration(unittest.TestCase):
    def test_full_pipeline(self):
        """测试完整分析流水线"""
        container = DIContainer()
        container.initialize()
        
        analyzer = container.get('UnifiedGameAnalyzer')
        frame = load_test_frame()
        
        result = analyzer.analyze_frame(frame)
        self.assertIn('objects', result)
        self.assertIn('confidence', result)
```

#### 3. 性能测试
```python
# 性能基准测试
def benchmark_analysis():
    """分析性能基准测试"""
    frames = load_test_frames(100)
    analyzer = create_analyzer()
    
    start_time = time.time()
    for frame in frames:
        analyzer.analyze(frame)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / len(frames)
    print(f"Average analysis time: {avg_time:.3f}s")
```

## ❓ 常见问题解答

### Q1: 如何添加新的游戏支持？

**A**: 在 `src/core/automation/` 目录下创建新的游戏适配器：

```python
# src/core/automation/new_game_adapter.py
from ..game_adapter import BaseGameAdapter

class NewGameAdapter(BaseGameAdapter):
    def __init__(self):
        super().__init__()
        self.game_name = "NewGame"
    
    def detect_game_state(self, frame):
        """检测游戏状态"""
        # 实现游戏特定的状态检测
        pass
    
    def get_available_actions(self, state):
        """获取可用动作"""
        # 返回当前状态下可执行的动作
        pass
```

### Q2: 如何优化图像处理性能？

**A**: 使用以下策略：

```python
# 1. 图像预处理优化
def preprocess_frame(frame):
    # 降低分辨率
    frame = cv2.resize(frame, (640, 480))
    # 转换颜色空间
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return frame

# 2. 使用缓存
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_template_match(template_hash, frame_hash):
    # 缓存模板匹配结果
    pass

# 3. 并行处理
from concurrent.futures import ThreadPoolExecutor

def parallel_analysis(frame):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(detect_objects, frame),
            executor.submit(detect_text, frame),
            executor.submit(detect_ui, frame)
        ]
        results = [f.result() for f in futures]
    return combine_results(results)
```

### Q3: 如何处理复杂的错误场景？

**A**: 使用分层错误处理：

```python
# 定义具体的错误类型
class GameStateError(GameAutomationError):
    """游戏状态异常"""
    pass

class AnalysisTimeoutError(GameStateError):
    """分析超时异常"""
    pass

# 实现错误处理
def robust_analysis(frame, timeout=5.0):
    try:
        with timeout_context(timeout):
            return analyze_frame(frame)
    except TimeoutError:
        raise AnalysisTimeoutError("Analysis timeout")
    except Exception as e:
        # 使用恢复管理器
        recovery_manager.handle_error(e)
        return default_result()
```

### Q4: 如何扩展UI组件？

**A**: 遵循组件设计模式：

```python
# src/ui/widgets/custom_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from .base_widget import BaseWidget

class CustomWidget(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout()
        # 添加子组件
        self.setLayout(layout)
    
    def connect_signals(self):
        """连接信号槽"""
        # 连接事件处理
        pass
    
    def update_data(self, data):
        """更新显示数据"""
        # 更新UI显示
        pass
```

## 🤝 贡献指南

### 提交代码流程

#### 1. 创建Pull Request
```bash
# 确保代码是最新的
git checkout main
git pull origin main

# 创建特性分支
git checkout -b feature/your-feature

# 提交变更
git add .
git commit -m "feat: add new button detector"
git push origin feature/your-feature
```

#### 2. 代码审查清单

**功能性检查**:
- [ ] 功能按预期工作
- [ ] 边界条件处理正确
- [ ] 错误处理完善
- [ ] 性能符合要求

**代码质量检查**:
- [ ] 遵循代码规范
- [ ] 有充分的注释和文档
- [ ] 变量和函数命名清晰
- [ ] 没有重复代码

**架构合规性检查**:
- [ ] 遵循分层架构原则
- [ ] 职责分配正确
- [ ] 依赖方向正确
- [ ] 使用依赖注入

**测试覆盖**:
- [ ] 有对应的单元测试
- [ ] 测试覆盖率 > 80%
- [ ] 集成测试通过
- [ ] 性能测试通过

#### 3. 提交消息规范

使用 **Conventional Commits** 格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**示例**:
```
feat(core): add button detection analyzer

- Implement template-based button detection
- Add confidence threshold configuration
- Support multiple button templates

Closes #123
```

**类型说明**:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码风格调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

## 📊 发布流程

### 版本管理

使用 **语义化版本** (Semantic Versioning):
- **主版本号**: 不兼容的API修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

### 发布步骤

#### 1. 准备发布
```bash
# 更新版本号
echo "1.2.3" > VERSION

# 更新CHANGELOG
# 编辑 CHANGELOG.md 添加新版本信息

# 运行完整测试套件
python -m pytest
python src/tests/directory_refactor_test.py
python src/tests/service_responsibility_test.py
```

#### 2. 创建发布
```bash
# 提交版本更新
git add VERSION CHANGELOG.md
git commit -m "chore: bump version to 1.2.3"

# 创建标签
git tag -a v1.2.3 -m "Release v1.2.3"

# 推送到远程
git push origin main
git push origin v1.2.3
```

#### 3. 构建和分发
```bash
# 构建分发包
python setup.py sdist bdist_wheel

# 上传到PyPI（如果适用）
twine upload dist/*
```

---

**文档版本**: v1.0  
**最后更新**: 2024年  
**相关文档**: [README.md](../../README.md) | [架构设计](../architecture/architecture.md) | [API文档](../api/)

<div align="center">

**👨‍💻 Happy Coding! 让我们一起构建更好的游戏自动化工具！**

</div>