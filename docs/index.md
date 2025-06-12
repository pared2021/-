# 游戏自动化工具

这是一个功能强大的游戏自动化工具，支持宏录制、脚本编辑和性能监控等功能。

## 功能特点

1. **宏录制和播放**
   - 录制键盘和鼠标操作
   - 支持播放速度调整
   - 可编辑和优化录制的宏
   - 支持循环播放

2. **脚本编辑器**
   - 语法高亮
   - 代码补全
   - 代码格式化
   - 语法检查
   - 代码风格检查

3. **性能监控**
   - CPU使用率监控
   - 内存使用监控
   - 帧率(FPS)监控
   - 实时图表显示
   - 历史数据查看
   - 性能报告生成

4. **项目管理**
   - 创建和打开项目
   - 文件树浏览
   - 最近文件记录
   - 项目配置管理

## 安装

1. 安装Python 3.8或更高版本
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用说明

### 宏录制

1. 点击工具栏的"录制宏"按钮开始录制
2. 执行需要录制的操作
3. 再次点击按钮停止录制
4. 在宏编辑器中查看和编辑录制的操作
5. 点击"播放宏"按钮回放录制的操作

### 脚本编辑

1. 创建新项目或打开现有项目
2. 在项目浏览器中双击文件打开
3. 使用内置编辑器编写脚本
4. 使用工具栏的格式化和检查功能保证代码质量
5. Ctrl+S保存文件

### 性能监控

1. 选择要监控的游戏
2. 在性能监控窗口查看实时数据
3. 切换到历史视图查看历史数据
4. 使用工具栏的导出功能生成报告

## 开发指南

### 项目结构

```
游戏自动操作工具/
├── src/
│   ├── core/           # 核心功能
│   ├── gui/            # 界面相关
│   ├── macro/          # 宏相关
│   ├── editor/         # 编辑器相关
│   └── performance/    # 性能监控相关
├── tests/              # 单元测试
├── docs/               # 文档
└── requirements.txt    # 依赖
```

### 添加新功能

1. 在相应模块下创建新的Python文件
2. 实现功能类和方法
3. 在`gui/main_window.py`中集成新功能
4. 添加单元测试
5. 更新文档

### 运行测试

```bash
pytest tests/
```

## API文档

### MacroRecorder类

```python
class MacroRecorder:
    """宏录制器"""

    def start(self):
        """开始录制"""

    def stop(self):
        """停止录制"""

    @property
    def is_recording(self) -> bool:
        """是否正在录制"""
```

### MacroPlayer类

```python
class MacroPlayer:
    """宏播放器"""

    def load_events(self, events: List[MacroEvent]):
        """加载事件"""

    def start(self):
        """开始播放"""

    def stop(self):
        """停止播放"""
```

### PerformanceMonitor类

```python
class PerformanceMonitor:
    """性能监控器"""

    def start(self):
        """开始监控"""

    def stop(self):
        """停止监控"""

    def get_current_metrics(self) -> PerformanceMetrics:
        """获取当前指标"""
```

## 常见问题

1. **Q: 如何调整宏播放速度？**
   A: 在宏编辑器中选择宏，使用速度调节滑块调整。

2. **Q: 为什么性能监控数据不显示？**
   A: 确保已选择正确的游戏窗口，且游戏正在运行。

3. **Q: 如何导出性能报告？**
   A: 在性能监控窗口中点击"导出报告"按钮，选择导出格式。

4. **Q: 脚本编辑器支持哪些快捷键？**
   A: 支持常见的编辑器快捷键，如：
   - Ctrl+S：保存
   - Ctrl+Z：撤销
   - Ctrl+Y：重做
   - Ctrl+F：查找
   - F3：查找下一个

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

MIT License
