#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt6应用配置模块
遵循PyQt6最佳实践的应用元数据设置
"""

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication


def init_application_metadata():
    """
    根据PyQt6最佳实践设置应用元数据
    必须在QApplication实例化之前或之后立即调用
    """
    QCoreApplication.setOrganizationName("GameAutomation")
    QCoreApplication.setOrganizationDomain("gameauto.com") 
    QCoreApplication.setApplicationName("GameAutomationTool")
    QCoreApplication.setApplicationVersion("1.0.0")
    
    # 设置应用显示名称（兼容性检查）
    try:
        QCoreApplication.setApplicationDisplayName("游戏自动化工具")
    except AttributeError:
        # 某些PyQt6版本可能不支持此方法
        pass


def ensure_qapp_ready():
    """
    确保QApplication实例已创建并正确配置
    返回QApplication实例
    """
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication must be created before calling this function")
    
    # 验证元数据是否已设置
    if not QCoreApplication.organizationName():
        init_application_metadata()
    
    return app


def get_app_info():
    """
    获取应用信息字典
    """
    info = {
        "organization_name": QCoreApplication.organizationName(),
        "organization_domain": QCoreApplication.organizationDomain(),
        "application_name": QCoreApplication.applicationName(),
        "application_version": QCoreApplication.applicationVersion()
    }
    
    # 兼容性检查
    try:
        info["application_display_name"] = QCoreApplication.applicationDisplayName()
    except AttributeError:
        info["application_display_name"] = QCoreApplication.applicationName()
    
    return info


def setup_application_properties(window_title=None, window_size=None, theme=None):
    """
    设置应用程序属性
    根据PyQt6文档推荐的应用程序配置
    
    Args:
        window_title: 窗口标题（用于显示）
        window_size: 窗口大小元组 (width, height)
        theme: 主题名称
    """
    app = ensure_qapp_ready()
    
    # 设置应用程序图标（如果存在）
    try:
        from PyQt6.QtGui import QIcon
        icon_path = "src/resources/icons/app_icon.png"
        import os
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
    except Exception:
        pass  # 图标不是必需的
    
    # 设置应用程序样式（可选）
    if theme == "dark":
        app.setStyle("Fusion")  # 深色主题使用Fusion
    else:
        app.setStyle("Fusion")  # 默认也使用Fusion样式以获得现代外观
    
    return app 