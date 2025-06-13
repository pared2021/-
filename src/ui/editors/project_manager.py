"""
项目管理器
负责管理项目配置和依赖
"""
import json
import logging
import shutil
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class ProjectConfig:
    """项目配置"""

    name: str
    path: str
    description: str = ""
    version: str = "0.1.0"
    dependencies: Dict[str, str] = field(default_factory=dict)

    def save(self):
        """保存配置"""
        try:
            config_path = Path(self.path) / "project.json"
            config_data = {
                "name": self.name,
                "description": self.description,
                "version": self.version,
                "dependencies": self.dependencies,
            }
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f)
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}", exc_info=True)

    def get_dependencies(self) -> Dict[str, str]:
        """获取依赖列表"""
        return self.dependencies

    def add_dependency(self, name: str, version: str):
        """添加依赖"""
        self.dependencies[name] = version
        self.save()

    def remove_dependency(self, name: str):
        """删除依赖"""
        if name in self.dependencies:
            del self.dependencies[name]
            self.save()

    def get_scripts(self) -> Dict[str, str]:
        """获取脚本列表"""
        return {}

    def add_script(self, name: str, command: str):
        """添加脚本"""
        pass

    def remove_script(self, name: str):
        """删除脚本"""
        pass


class ProjectManager:
    """项目管理器"""

    def __init__(self):
        """初始化项目管理器"""
        self.logger = logging.getLogger("ProjectManager")
        self.current_project: Optional[ProjectConfig] = None
        self.projects: Dict[str, ProjectConfig] = {}

    def create_project(self, path: Path, name: str) -> ProjectConfig:
        """创建新项目

        Args:
            path: 项目路径
            name: 项目名称

        Returns:
            项目配置对象
        """
        project_dir = path / name
        if project_dir.exists():
            raise ValueError(f"项目目录已存在: {project_dir}")

        try:
            # 创建项目结构
            project_dir.mkdir(parents=True)
            (project_dir / "src").mkdir()
            (project_dir / "tests").mkdir()
            (project_dir / "docs").mkdir()

            # 创建配置文件
            config = ProjectConfig(
                name=name,
                path=str(project_dir),
                description="",
                version="0.1.0",
                dependencies={},
            )
            config.save()

            # 创建基础文件
            self._create_base_files(project_dir)

            self.current_project = config
            self.projects[config.name] = config
            return config

        except Exception as e:
            self.logger.error(f"创建项目失败: {e}", exc_info=True)
            if project_dir.exists():
                shutil.rmtree(project_dir)
            raise

    def _create_base_files(self, project_dir: Path):
        """创建基础文件"""
        # README.md
        readme = project_dir / "README.md"
        readme.write_text(
            f"""# {project_dir.name}

## 简介

## 安装

## 使用

## 开发

## 许可证
""",
            encoding="utf-8",
        )

        # .gitignore
        gitignore = project_dir / ".gitignore"
        gitignore.write_text(
            """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Test
.coverage
htmlcov/
.pytest_cache/

# Logs
*.log
""",
            encoding="utf-8",
        )

        # requirements.txt
        requirements = project_dir / "requirements.txt"
        requirements.touch()

        # setup.py
        setup = project_dir / "setup.py"
        setup.write_text(
            f"""from setuptools import setup, find_packages

setup(
    name="{project_dir.name}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # 依赖列表
    ],
    author="",
    author_email="",
    description="",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
""",
            encoding="utf-8",
        )

        # 创建源代码目录
        src_init = project_dir / "src" / "__init__.py"
        src_init.touch()

        # 创建测试目录
        test_init = project_dir / "tests" / "__init__.py"
        test_init.touch()

    def open_project(self, path: Path) -> ProjectConfig:
        """打开项目

        Args:
            path: 项目路径

        Returns:
            项目配置对象
        """
        if not path.exists():
            raise ValueError(f"项目目录不存在: {path}")

        try:
            config_path = path / "project.json"
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            project_data = data
            config = ProjectConfig(
                name=project_data.get("name", ""),
                path=str(path),
                description=project_data.get("description", ""),
                version=project_data.get("version", "0.1.0"),
                dependencies=project_data.get("dependencies", {}),
            )

            self.current_project = config
            self.projects[config.name] = config
            return config

        except Exception as e:
            self.logger.error(f"打开项目失败: {e}", exc_info=True)
            raise

    def close_project(self):
        """关闭项目"""
        self.current_project = None

    def get_project_files(self) -> List[Path]:
        """获取项目文件列表"""
        if not self.current_project:
            return []

        files = []
        for file in Path(self.current_project.path).rglob("*.py"):
            if not any(p.name.startswith(".") for p in file.parents):
                files.append(file)
        return files

    def create_file(self, path: Path, content: str = ""):
        """创建文件

        Args:
            path: 文件路径
            content: 文件内容
        """
        if not self.current_project:
            raise RuntimeError("未打开项目")

        if not path.is_relative_to(Path(self.current_project.path)):
            raise ValueError("文件路径必须在项目目录内")

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def delete_file(self, path: Path):
        """删除文件

        Args:
            path: 文件路径
        """
        if not self.current_project:
            raise RuntimeError("未打开项目")

        if not path.is_relative_to(Path(self.current_project.path)):
            raise ValueError("文件路径必须在项目目录内")

        if path.exists():
            path.unlink()

    def rename_file(self, old_path: Path, new_path: Path):
        """重命名文件

        Args:
            old_path: 原文件路径
            new_path: 新文件路径
        """
        if not self.current_project:
            raise RuntimeError("未打开项目")

        if not old_path.is_relative_to(Path(self.current_project.path)):
            raise ValueError("原文件路径必须在项目目录内")

        if not new_path.is_relative_to(Path(self.current_project.path)):
            raise ValueError("新文件路径必须在项目目录内")

        if old_path.exists():
            old_path.rename(new_path)

    def create_directory(self, path: Path):
        """创建目录

        Args:
            path: 目录路径
        """
        if not self.current_project:
            raise RuntimeError("未打开项目")

        if not path.is_relative_to(Path(self.current_project.path)):
            raise ValueError("目录路径必须在项目目录内")

        path.mkdir(parents=True, exist_ok=True)

    def delete_directory(self, path: Path):
        """删除目录

        Args:
            path: 目录路径
        """
        if not self.current_project:
            raise RuntimeError("未打开项目")

        if not path.is_relative_to(Path(self.current_project.path)):
            raise ValueError("目录路径必须在项目目录内")

        if path.exists():
            shutil.rmtree(path)

    def rename_directory(self, old_path: Path, new_path: Path):
        """重命名目录

        Args:
            old_path: 原目录路径
            new_path: 新目录路径
        """
        if not self.current_project:
            raise RuntimeError("未打开项目")

        if not old_path.is_relative_to(Path(self.current_project.path)):
            raise ValueError("原目录路径必须在项目目录内")

        if not new_path.is_relative_to(Path(self.current_project.path)):
            raise ValueError("新目录路径必须在项目目录内")

        if old_path.exists():
            old_path.rename(new_path)

    def get_recent_files(self) -> List[Dict[str, Any]]:
        """获取最近打开的文件"""
        recent_file = Path(self.current_project.path) / ".recent_files"
        if not recent_file.exists():
            return []

        try:
            return json.loads(recent_file.read_text(encoding="utf-8"))
        except Exception as e:
            self.logger.error(f"读取最近文件列表失败: {e}", exc_info=True)
            return []

    def add_recent_file(self, path: Path):
        """添加最近打开的文件

        Args:
            path: 文件路径
        """
        if not self.current_project:
            return

        recent_file = Path(self.current_project.path) / ".recent_files"
        recent_files = self.get_recent_files()

        # 更新文件列表
        file_info = {
            "path": str(path.relative_to(Path(self.current_project.path))),
            "last_opened": datetime.now().isoformat(),
        }

        # 移除已存在的记录
        recent_files = [f for f in recent_files if f["path"] != file_info["path"]]

        # 添加新记录
        recent_files.insert(0, file_info)

        # 保留最近20个文件
        recent_files = recent_files[:20]

        try:
            recent_file.write_text(json.dumps(recent_files, indent=2), encoding="utf-8")
        except Exception as e:
            self.logger.error(f"保存最近文件列表失败: {e}", exc_info=True)

    def backup_project(self, backup_dir: Optional[Path] = None) -> Path:
        """备份项目

        Args:
            backup_dir: 备份目录，默认为项目目录下的backups目录

        Returns:
            备份文件路径
        """
        if not self.current_project:
            raise RuntimeError("未打开项目")

        if not backup_dir:
            backup_dir = Path(self.current_project.path) / "backups"
            backup_dir.mkdir(exist_ok=True)

        # 创建备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = (
            backup_dir / f"{Path(self.current_project.path).name}_{timestamp}.zip"
        )

        # 创建备份
        shutil.make_archive(
            str(backup_file.with_suffix("")), "zip", Path(self.current_project.path)
        )

        return backup_file

    def load_project(self, project_path: str) -> Optional[ProjectConfig]:
        """加载项目配置"""
        if not os.path.exists(project_path):
            return None

        try:
            config_path = Path(project_path) / "project.json"
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                config = ProjectConfig(
                    name=data.get("name", ""),
                    path=data.get("path", ""),
                    description=data.get("description", ""),
                    version=data.get("version", "0.1.0"),
                )
                if config.path:
                    self.current_project = config
                    self.projects[config.name] = config
                return config
        except Exception as e:
            self.logger.error(f"加载项目失败: {str(e)}")
            return None
