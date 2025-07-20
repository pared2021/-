# 智能模块导入系统 - 快速开始

## 🚀 系统概述

智能模块导入系统已成功集成到游戏自动化工具中，提供了强大的模块管理和别名导入功能。

## ✅ 系统状态

- ✅ 模块发现：自动发现 120+ 个模块
- ✅ 别名系统：注册了 14 个配置别名
- ✅ 懒加载：支持按需加载模块
- ✅ 性能监控：提供详细的统计信息
- ✅ 依赖管理：自动构建依赖关系图

## 🎯 快速测试

### 运行测试脚本
```bash
# 在Windows上使用py命令
py test_import.py

# 或者运行主程序
py main.py --help
py main.py --config-info
```

### 测试结果示例
```
=== 智能模块导入系统测试 ===
✅ 成功导入 src.common.module_types
✅ 初始化完成，耗时: 0.37秒

模块统计信息:
  total_modules: 123
  loaded_modules: 3
  failed_modules: 0
  total_aliases: 14

测试别名导入:
  @config -> src.services.config ✅
  @logger -> src.services.logger ✅
  @common -> src.common ✅
  @core -> src.core ✅
```

## 📋 可用别名

系统自动注册了以下别名：

- `@config` → `src.services.config`
- `@logger` → `src.services.logger`
- `@common` → `src.common`
- `@core` → `src.core`
- 以及其他 10 个配置别名

## 🔧 在代码中使用

```python
# 获取模块管理器
from src.common.module_manager import get_module_manager

manager = get_module_manager()

# 使用别名导入模块
config_module = manager.get_module('@config')
logger_module = manager.get_module('@logger')

# 获取统计信息
stats = manager.get_statistics()
print(f"已发现模块: {stats['total_modules']}")
print(f"已加载模块: {stats['loaded_modules']}")

# 发现新模块
discovered = manager.discover_modules()
print(f"发现模块数量: {len(discovered)}")
```

## 🎮 启动应用

```bash
# 启动GUI模式（自动检测）
py main.py

# 强制启动GUI
py main.py --gui

# 启动CLI模式
py main.py --cli

# 调试模式
py main.py --debug
```

## 📁 重要文件

- `src/common/module_manager.py` - 核心模块管理器
- `src/common/module_discovery.py` - 模块发现器
- `src/common/module_types.py` - 数据类型定义
- `config/module_config.json` - 模块配置文件
- `test_import.py` - 测试脚本

## 💡 注意事项

1. **Windows环境**：请使用 `py` 命令而不是 `python` 命令
2. **Python版本**：系统运行在 Python 3.11.9 上
3. **模块发现**：系统会自动扫描 `src/` 目录下的所有模块
4. **性能**：初始化耗时约 0.37 秒，后续模块加载采用懒加载机制

## 🔍 故障排除

如果遇到问题，请：

1. 确保使用 `py` 命令运行脚本
2. 检查 Python 版本：`py --version`
3. 运行测试脚本：`py test_import.py`
4. 查看配置信息：`py main.py --config-info`

---

🎉 **智能模块导入系统已成功集成并可正常使用！**