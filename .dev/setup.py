"""安装脚本 - 支持Clean Architecture"""
from setuptools import setup, find_packages

setup(
    name="game_automation",
    version="3.0.0",  # Clean Architecture重构版本
    description="游戏自动化工具 - Clean Architecture架构",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # 核心GUI框架
        "PyQt6>=6.6.0",
        
        # 图像处理和计算机视觉
        "opencv-python>=4.9.0", 
        "opencv-contrib-python>=4.9.0",
        "numpy>=1.26.0",
        "Pillow>=10.2.0",
        "scikit-image>=0.22.0",
        "easyocr>=1.7.0",
        
        # 系统自动化
        "pyautogui>=0.9.54",
        "pygetwindow>=0.0.9", 
        "pynput>=1.7.6",
        "psutil>=5.9.5",
        
        # Clean Architecture核心
        "dependency-injector>=4.41.0",
        
        # 工具库
        "rich>=13.7.0",
        "tqdm>=4.66.1", 
        "pyyaml>=6.0.1",
        "click>=8.1.7",
        "loguru>=0.7.2",
        "pyqtgraph>=0.13.3",
        
        # AI和机器学习(可选)
        "torch>=2.1.0",
        "torchvision>=0.16.0",
        "transformers>=4.37.0",
    ],
    extras_require={
        "api": [
            "fastapi>=0.109.0",
            "uvicorn[standard]>=0.27.0", 
            "pydantic>=2.5.0",
            "httpx>=0.26.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "game-automation=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License", 
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)
