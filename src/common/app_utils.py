import os
import sys
import ctypes
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication

def set_dpi_awareness():
    """设置DPI感知，尝试多种方法"""
    if sys.platform != "win32":
        return  # 仅在Windows平台尝试设置DPI感知
        
    try:
        # 方法1: 使用较新的API - SetProcessDpiAwarenessContext（Windows 10 1703+）
        try:
            awareness_context = -4  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
            ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_int(awareness_context))
            print("已成功设置DPI感知: SetProcessDpiAwarenessContext")
            return
        except (AttributeError, OSError):
            pass
        
        # 方法2: 使用SetProcessDpiAwareness (Windows 8.1+)
        try:
            awareness = 2  # PROCESS_PER_MONITOR_DPI_AWARE
            result = ctypes.windll.shcore.SetProcessDpiAwareness(awareness)
            if result == 0:  # S_OK
                print("已成功设置DPI感知: SetProcessDpiAwareness")
                return
        except (AttributeError, OSError):
            pass
            
        # 方法3: 使用老的API - SetProcessDPIAware (Windows Vista+)
        try:
            result = ctypes.windll.user32.SetProcessDPIAware()
            if result:
                print("已成功设置DPI感知: SetProcessDPIAware")
                return
        except (AttributeError, OSError):
            pass
            
        print("未能设置DPI感知，将使用系统默认设置")
            
    except Exception as e:
        print(f"设置DPI感知失败: {e}")
        # 忽略错误继续运行，因为这不是程序运行的必须条件

def create_manifest_file():
    """创建应用程序清单文件，以解决DPI感知问题"""
    manifest_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
      version="1.0.0.0"
      processorArchitecture="*"
      name="GameAutomationTool"
      type="win32"
  />
  <description>Game Automation Tool</description>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
          type="win32"
          name="Microsoft.Windows.Common-Controls"
          version="6.0.0.0"
          processorArchitecture="*"
          publicKeyToken="6595b64144ccf1df"
          language="*"
      />
    </dependentAssembly>
  </dependency>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <!-- Windows 10 and Windows 11 -->
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}"/>
      <!-- Windows 8.1 -->
      <supportedOS Id="{1f676c76-80e1-4239-95bb-83d0f6d0da78}"/>
      <!-- Windows 8 -->
      <supportedOS Id="{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}"/>
      <!-- Windows 7 -->
      <supportedOS Id="{35138b9a-5d96-4fbd-8e2d-a2440225f93a}"/>
    </application>
  </compatibility>
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true/pm</dpiAware>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2, PerMonitor</dpiAwareness>
    </windowsSettings>
  </application>
</assembly>"""
    
    manifest_path = "app.manifest"
    try:
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(manifest_content)
        print(f"清单文件已创建: {manifest_path}")
    except Exception as e:
        print(f"创建清单文件失败: {e}")

def set_app_style(app: QApplication):
    """设置应用样式"""
    # 设置暗色主题
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    # 设置禁用状态颜色
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor(40, 40, 40))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
    
    # 应用调色板
    app.setPalette(dark_palette)
    
    # 设置样式表
    app.setStyleSheet("""
        QToolTip { 
            color: #ffffff; 
            background-color: #2a2a2a; 
            border: 1px solid #444444; 
            border-radius: 4px;
            padding: 5px;
        }
        QScrollBar:vertical {
            border: none;
            background-color: #2d2d2d;
            width: 8px;
            border-radius: 4px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background-color: #4d4d4d;
            border-radius: 4px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #5d5d5d;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
    """)

def is_admin():
    """检查是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """以管理员权限重新运行程序"""
    if sys.argv[-1] != 'asadmin':
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:] + ['asadmin'])
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        except:
            pass
        return False
    return True

def create_default_icons():
    """创建默认图标文件"""
    icons_dir = os.path.join("resources", "icons")
    os.makedirs(icons_dir, exist_ok=True)
    
    # 检查并创建默认图标
    default_icons = {
        "window.png": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x18\x00\x00\x00\x18\x08\x06\x00\x00\x00\xe0w=\xf8\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x07tIME\x07\xe5\x04\x1a\n\x1c\x1d\x15\xe5\xf3\xe6\x00\x00\x00\x19tEXtComment\x00Created with GIMPW\x81\x0e\x17\x00\x00\x01\x02IDATH\xc7\xed\x95\xbd\n\xc2@\x10\x85?_\xc1\x80\x8d6\xf6\xf6\x82\x85\xb5X\xf9\x00>\x82\xef\xe7\x83Xy\x01\x1b\x0b\x1b\x1b\x1bk+\xc5\xc2B\x14S\x9c\x8d\x13\xad\xb8\xcd\xee\xfc\x80\x92\x0b!9\xc3\xdc\x9b\xdd\xddI\x96\xff\xd8\x0e\xc0\x1axsP\x0b\x1c\x03V\xc6\xe0\xa9\x87\xd3Q\xa4\x1c\x8aQ\xb8I\xd7\xc8\x13\x98\xf9\x1c\x1c\x81+p\x01\xd6\x86k\x12\xaf\xf5\x9d+3p\x0f\xec\x8c\xc1\xfd\x02\x8f\xaf\xb1\x03\x1e\x81%\xb0\x00\xde\x81#\xb0\x00\x9e\x81\xbb\x96p5YO\x0cW\xefD3\xcdc\x96\x89\xfc\xd1\xf1\x98%`\x06\xb3\x9d\xde\n\xd8b~\xd7\xd7\x18\xfcQ\xa1\x85\x16\x07\x10\xe3\xe9\xd8\xe4*\x86Rk\x1c\xd3\r\xadv\x14\xab#\xd3\xe4`\x9f\xe8\x9d*\x05\x12\xbb]\x8de\t\xd0b\xf8\xba\x18\xbf{\x0b\x8c\xb4t\xadUa\x81d\xfc\xaf\xd5\x90\xcd\xec=\xf5\x14\x13\x9c.\x84\xbf\x10\xb3zN.o\xb6\x87"\xf7\xc0\x16\x08\xb9\xdf[Dp\xf6\x9f%\xdb\x07\x05[\xa8r\x82\xcf\xa8T\x00\x00\x00\x00IEND\xaeB`\x82'
    }
    
    for filename, data in default_icons.items():
        icon_path = os.path.join(icons_dir, filename)
        if not os.path.exists(icon_path):
            try:
                with open(icon_path, 'wb') as f:
                    f.write(data)
            except Exception as e:
                print(f"创建图标文件失败: {e}")

def setup_environment():
    """设置应用程序环境"""
    # 在创建任何Qt对象之前设置DPI感知
    set_dpi_awareness()
    
    # 设置环境变量，手动控制Qt的DPI缩放
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
    os.environ["QT_SCALE_FACTOR"] = "1"
    os.environ["QT_FONT_DPI"] = "96"  # 使用标准DPI值
    
    # 创建清单文件
    create_manifest_file()
    
    # 创建默认图标
    create_default_icons() 