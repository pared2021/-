"""
代码编辑器测试
"""
import pytest
from unittest.mock import Mock, patch
from src.editor.script_editor import ScriptEditor
from src.editor.code_formatter import CodeFormatter
from src.editor.project_manager import ProjectManager


@pytest.fixture
def editor(qtbot):
    """创建脚本编辑器实例"""
    editor = ScriptEditor()
    qtbot.addWidget(editor)
    return editor


@pytest.fixture
def formatter():
    """创建代码格式化器实例"""
    return CodeFormatter()


@pytest.fixture
def project_manager():
    """创建项目管理器实例"""
    return ProjectManager()


def test_editor_basic(editor):
    """测试编辑器基本功能"""
    # 测试设置和获取文本
    test_code = "def test():\n    pass"
    editor.setPlainText(test_code)
    assert editor.toPlainText() == test_code

    # 测试光标位置
    editor.setCursorPosition(1, 4)
    cursor = editor.textCursor()
    assert cursor.blockNumber() == 1
    assert cursor.columnNumber() == 4


def test_editor_syntax_highlighting(editor):
    """测试语法高亮"""
    # Python关键字
    test_code = "def class import"
    editor.setPlainText(test_code)

    # 验证关键字格式
    format = editor.getFormat(0, 3)  # "def"的格式
    assert format.foreground().color().name() in editor.KEYWORD_COLORS


def test_editor_code_completion(editor):
    """测试代码补全"""
    # 模拟输入
    editor.setPlainText("import ")
    editor.setCursorPosition(0, 7)

    # 触发补全
    completions = editor.get_completions()
    assert "os" in completions
    assert "sys" in completions
    assert "json" in completions


def test_editor_file_operations(editor, tmp_path):
    """测试文件操作"""
    # 创建测试文件
    test_file = tmp_path / "test.py"
    test_file.write_text("def test():\n    pass")

    # 加载文件
    editor.load_file(str(test_file))
    assert editor.toPlainText() == "def test():\n    pass"

    # 修改内容
    editor.setPlainText("def modified():\n    return True")

    # 保存文件
    editor.save_file()
    assert test_file.read_text() == "def modified():\n    return True"


def test_formatter_format_code(formatter):
    """测试代码格式化"""
    # 格式化前的代码
    unformatted = "def test():\n  return True"

    # 格式化
    formatted = formatter.format_code(unformatted)
    assert formatted == "def test():\n    return True"


def test_formatter_check_syntax(formatter):
    """测试语法检查"""
    # 正确的代码
    valid_code = "def test():\n    return True"
    assert formatter.check_syntax(valid_code) == []

    # 错误的代码
    invalid_code = "def test()\n    return True"
    errors = formatter.check_syntax(invalid_code)
    assert len(errors) > 0
    assert "SyntaxError" in errors[0]["message"]


def test_formatter_lint_code(formatter):
    """测试代码风格检查"""
    # 不符合PEP8的代码
    code = "def test( ):\n  return True"
    issues = formatter.lint_code(code)
    assert len(issues) > 0

    # 验证问题类型
    assert any("whitespace" in issue["message"].lower() for issue in issues)


def test_project_manager_create_project(project_manager, tmp_path):
    """测试项目创建"""
    # 创建项目
    project_path = tmp_path / "test_project"
    project_manager.create_project(project_path, "TestProject")

    # 验证项目结构
    assert project_path.exists()
    assert (project_path / "src").exists()
    assert (project_path / "tests").exists()
    assert (project_path / "requirements.txt").exists()
    assert (project_path / "README.md").exists()


def test_project_manager_open_project(project_manager, tmp_path):
    """测试项目打开"""
    # 创建测试项目
    project_path = tmp_path / "test_project"
    project_path.mkdir()
    (project_path / "src").mkdir()
    (project_path / "requirements.txt").touch()

    # 打开项目
    project_manager.open_project(project_path)
    assert project_manager.current_project is not None
    assert project_manager.current_project.path == project_path


def test_project_manager_file_operations(project_manager, tmp_path):
    """测试项目文件操作"""
    # 创建并打开项目
    project_path = tmp_path / "test_project"
    project_manager.create_project(project_path, "TestProject")
    project_manager.open_project(project_path)

    # 创建文件
    file_path = project_path / "src" / "test.py"
    project_manager.create_file(file_path)
    assert file_path.exists()

    # 重命名文件
    new_path = project_path / "src" / "renamed.py"
    project_manager.rename_file(file_path, new_path)
    assert not file_path.exists()
    assert new_path.exists()

    # 删除文件
    project_manager.delete_file(new_path)
    assert not new_path.exists()


def test_project_manager_recent_files(project_manager, tmp_path):
    """测试最近文件记录"""
    # 创建测试文件
    file1 = tmp_path / "test1.py"
    file2 = tmp_path / "test2.py"
    file1.touch()
    file2.touch()

    # 添加到最近文件
    project_manager.add_recent_file(file1)
    project_manager.add_recent_file(file2)

    # 获取最近文件列表
    recent_files = project_manager.get_recent_files()
    assert str(file1) in recent_files
    assert str(file2) in recent_files

    # 验证顺序（最新的在前）
    assert recent_files[0] == str(file2)


def test_project_manager_dependencies(project_manager, tmp_path):
    """测试依赖管理"""
    # 创建项目
    project_path = tmp_path / "test_project"
    project_manager.create_project(project_path, "TestProject")

    # 添加依赖
    project_manager.add_dependency("pytest", ">=6.0.0")
    project_manager.add_dependency("black", ">=21.0")

    # 验证requirements.txt
    requirements = (project_path / "requirements.txt").read_text()
    assert "pytest>=6.0.0" in requirements
    assert "black>=21.0" in requirements

    # 移除依赖
    project_manager.remove_dependency("black")
    requirements = (project_path / "requirements.txt").read_text()
    assert "black>=21.0" not in requirements
