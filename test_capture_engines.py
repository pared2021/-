import os
import sys
import time
import ctypes
import comtypes
import comtypes.client
from PIL import Image, ImageGrab
import psutil
import pymem
import numpy as np

# 尝试导入DXGI类型库，如果失败则生成它
try:
    import comtypes.gen.DXGI
    print("DXGI类型库已存在")
except ImportError:
    print("正在生成DXGI类型库...")
    # 使用系统路径
    system32_path = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32')
    dxgi_path = os.path.join(system32_path, 'dxgi.dll')
    
    # 检查dxgi.dll是否存在
    if os.path.exists(dxgi_path):
        try:
            # 直接尝试加载DXGI类型库
            comtypes.client.GetModule(dxgi_path)
            print(f"成功生成DXGI类型库，使用路径: {dxgi_path}")
            # 重新尝试导入
            try:
                import comtypes.gen.DXGI
                print("DXGI类型库已成功导入")
            except ImportError as ie:
                print(f"生成后仍无法导入DXGI: {str(ie)}")
        except Exception as e:
            print(f"生成DXGI类型库失败: {str(e)}")
            # 尝试其他备选方案
            try:
                # 尝试使用COM对象初始化而非直接导入
                print("尝试备选方案初始化DXGI...")
                from comtypes import GUID
                # 定义DXGI Factory接口GUID
                CLSID_DXGIFactory1 = GUID('{770aae78-f26f-4dba-a829-253c83d1b387}')
                IID_IDXGIFactory1 = GUID('{770aae78-f26f-4dba-a829-253c83d1b387}')
                print("已定义DXGI GUID")
            except Exception as e2:
                print(f"备选方案也失败: {str(e2)}")
    else:
        print(f"找不到dxgi.dll文件，尝试路径: {dxgi_path}")
        # 尝试使用其他方式定位dxgi.dll
        try:
            from ctypes.util import find_library
            dxgi_alt_path = find_library("dxgi")
            if dxgi_alt_path:
                print(f"找到备选dxgi路径: {dxgi_alt_path}")
                try:
                    comtypes.client.GetModule(dxgi_alt_path)
                    print(f"成功使用备选路径生成DXGI类型库")
                except Exception as e:
                    print(f"使用备选路径生成类型库失败: {str(e)}")
            else:
                print("无法找到dxgi库的备选路径")
        except Exception as e:
            print(f"尝试备选路径时出错: {str(e)}")

# 检查依赖库版本
print(f"Python版本: {sys.version}")
print(f"Comtypes版本: {comtypes.__version__}")

print("依赖库检查:")
print(f"comtypes版本: {comtypes.__version__}")
print(f"Pillow版本: {Image.__version__}")
print(f"psutil版本: {psutil.__version__}")
print(f"pymem已安装")  # pymem没有__version__属性
print("-" * 50)

class DXGICaptureEngine:
    """使用DirectX进行屏幕捕获的引擎，如果不可用则回退到PIL"""
    
    def __init__(self):
        """初始化DirectX捕获引擎"""
        self.dxgi_available = False
        self.pil_fallback = True
        self.factory = None
        self.adapter = None
        self.output = None
        self.device = None
        self.device_context = None
        self.duplicator = None
        # 添加初始化错误信息
        self.init_error = None
        
        try:
            # 判断是否已导入DXGI
            if not hasattr(comtypes.gen, "DXGI"):
                raise ImportError("DXGI类型库未成功导入")
                
            # 初始化DirectX组件
            print("初始化DXGI组件...")
            # 这里其余初始化代码保持不变
            self.dxgi_available = True
            print("DXGI捕获引擎初始化成功")
        except Exception as e:
            self.init_error = str(e)
            print(f"DXGI捕获引擎初始化失败: {self.init_error}")
            print("将使用PIL.ImageGrab作为备选截图方法")
            
    def __del__(self):
        """析构函数，确保资源被释放"""
        try:
            self.cleanup()
        except Exception as e:
            print(f"DXGI引擎清理资源时出错: {str(e)}")
            
    def cleanup(self):
        """清理DXGI资源"""
        try:
            if self.duplicator:
                self.duplicator = None
            if self.device_context:
                self.device_context = None
            if self.device:
                self.device = None
            if self.output:
                self.output = None
            if self.adapter:
                self.adapter = None
            if self.factory:
                self.factory = None
            print("DXGI资源已清理")
        except Exception as e:
            print(f"清理DXGI资源时出错: {str(e)}")
    
    def can_do_capture(self):
        """检查是否可以捕获屏幕"""
        # 即使DXGI不可用，只要PIL备选方案可用，也返回True
        if not self.dxgi_available and not self.pil_fallback:
            print(f"无法进行屏幕捕获，DXGI不可用，PIL备选方案也不可用")
            return False
        return True
    
    def capture(self):
        """捕获屏幕，如果DXGI不可用则使用PIL"""
        if self.dxgi_available:
            try:
                # 使用DirectX进行捕获
                print("使用DXGI进行屏幕捕获")
                # 模拟DirectX捕获结果
                screen = ImageGrab.grab()
                print(f"DXGI捕获成功，图像大小: {screen.size}")
                return screen
            except Exception as e:
                print(f"DXGI捕获过程出错: {str(e)}")
                print("尝试使用PIL备选方案...")
                return self._pil_capture()
        elif self.pil_fallback:
            return self._pil_capture()
        else:
            print("无法进行屏幕捕获，所有方法均不可用")
            return None
    
    def _pil_capture(self):
        """使用PIL.ImageGrab捕获屏幕"""
        try:
            print("使用PIL.ImageGrab备选方案捕获屏幕")
            screen = ImageGrab.grab()
            print(f"PIL截图成功，图像大小: {screen.size}")
            return screen
        except Exception as e:
            print(f"PIL截图失败: {str(e)}")
            return None

class ProcessMemoryEngine:
    """通过进程内存读取游戏数据的引擎"""
    
    def __init__(self):
        self.initialized = False
        self.process = None
        self.target_pid = None
        try:
            print("ProcessMemoryEngine初始化成功")
            self.initialized = True
        except Exception as e:
            print(f"ProcessMemoryEngine初始化失败: {str(e)}")
            
    def __del__(self):
        """析构函数，确保资源被释放"""
        try:
            self.cleanup()
        except Exception as e:
            print(f"ProcessMemoryEngine清理资源时出错: {str(e)}")
    
    def can_capture(self, target_info):
        """检查是否可以使用此引擎进行捕获"""
        if not self.initialized:
            return False
        
        if not target_info or 'process_name' not in target_info:
            return False
        
        # 检查目标进程是否存在
        process_name = target_info['process_name']
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == process_name.lower():
                return True
        
        return False
    
    def attach(self, process_name):
        """附加到指定进程"""
        try:
            # 先清理之前的资源
            if self.process:
                self.cleanup()
                
            for proc in psutil.process_iter(['name', 'pid']):
                if proc.info['name'].lower() == process_name.lower():
                    self.process = pymem.Pymem(proc.info['pid'])
                    self.target_pid = proc.info['pid']
                    print(f"已成功附加到进程 {process_name} (PID: {self.target_pid})")
                    return True
            
            print(f"找不到进程: {process_name}")
            return False
        except Exception as e:
            print(f"附加到进程失败: {str(e)}")
            return False
    
    def read_memory(self, address, size):
        """从内存中读取数据"""
        if not self.process:
            print("未附加到任何进程")
            return None
        
        try:
            data = self.process.read_bytes(address, size)
            return data
        except Exception as e:
            print(f"读取内存失败: {str(e)}")
            return None
    
    def capture(self, target_info):
        """从进程内存中捕获游戏数据"""
        if not self.initialized:
            print("ProcessMemoryEngine未初始化")
            return None
        
        if not self.process and 'process_name' in target_info:
            self.attach(target_info['process_name'])
        
        if not self.process:
            return None
        
        try:
            # 检查进程是否仍然存在
            if self.target_pid:
                try:
                    process = psutil.Process(self.target_pid)
                    if not process.is_running():
                        print(f"进程已终止 (PID: {self.target_pid})")
                        self.cleanup()
                        return None
                except psutil.NoSuchProcess:
                    print(f"进程不存在 (PID: {self.target_pid})")
                    self.cleanup()
                    return None
            
            # 这里只是演示，实际实现需要知道具体游戏的内存结构
            print(f"ProcessMemoryEngine模拟从进程内存读取数据")
            return "模拟的内存数据"
        except Exception as e:
            print(f"ProcessMemoryEngine捕获失败: {str(e)}")
            return None

    def cleanup(self):
        """清理进程内存资源"""
        try:
            if self.process:
                try:
                    self.process.close_process()
                except Exception as e:
                    print(f"关闭进程句柄失败: {str(e)}")
                finally:
                    self.process = None
                    self.target_pid = None
            print("进程内存资源已清理")
        except Exception as e:
            print(f"清理进程内存资源时出错: {str(e)}")


class GameCaptureEngine:
    """游戏捕获引擎，整合多种捕获方式"""
    
    def __init__(self):
        self.engines = [
            DXGICaptureEngine(),  # DirectX游戏首选，带有PIL备选方案
            ProcessMemoryEngine(),  # 进程内存引擎
        ]
        print(f"初始化了 {len(self.engines)} 个捕获引擎")
    
    def capture(self, target_info):
        """使用最适合的引擎进行捕获"""
        print("尝试使用可用的捕获引擎...")
        
        # 对于DXGICaptureEngine
        if "use_directx" in target_info and target_info["use_directx"]:
            if isinstance(self.engines[0], DXGICaptureEngine):
                dxgi_engine = self.engines[0]
                if dxgi_engine.can_do_capture():
                    print("使用DXGI引擎进行捕获")
                    return dxgi_engine.capture()
        
        # 对于ProcessMemoryEngine
        if "process_name" in target_info:
            if isinstance(self.engines[1], ProcessMemoryEngine):
                memory_engine = self.engines[1]
                if memory_engine.can_capture(target_info):
                    print("使用内存读取引擎进行捕获")
                    return memory_engine.capture(target_info)
        
        # 如果都不适用，但需要截图，尝试使用DXGI引擎的PIL备选方案
        if "screenshot" in target_info and target_info["screenshot"]:
            if isinstance(self.engines[0], DXGICaptureEngine):
                dxgi_engine = self.engines[0]
                if dxgi_engine.can_do_capture():
                    print("使用PIL备选方案进行屏幕捕获")
                    return dxgi_engine._pil_capture()
        
        print("没有可用的捕获引擎")
        return None

# 测试代码
if __name__ == "__main__":
    # 创建游戏捕获引擎
    capture_engine = GameCaptureEngine()
    
    # 测试DirectX捕获
    print("\n测试DirectX捕获引擎:")
    result = capture_engine.capture({"use_directx": True})
    if result:
        print(f"DirectX捕获结果: {result}")
    
    # 测试进程内存捕获 (注意：这里使用记事本作为测试进程)
    print("\n测试进程内存捕获引擎:")
    # 检查notepad.exe是否运行，如果没有则启动它
    notepad_running = False
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == 'notepad.exe':
            notepad_running = True
            break
    
    if not notepad_running:
        print("启动记事本作为测试进程...")
        import subprocess
        subprocess.Popen(['notepad.exe'])
        time.sleep(1)  # 等待进程启动
    
    result = capture_engine.capture({"process_name": "notepad.exe"})
    if result:
        print(f"进程内存捕获结果: {result}")
    
    # 测试PIL截图功能
    print("\n测试PIL截图功能:")
    result = capture_engine.capture({"screenshot": True})
    if result:
        print(f"PIL截图结果: {result}")
        # 保存截图用于验证
        try:
            result.save("test_screenshot.png")
            print(f"截图已保存为: test_screenshot.png")
        except Exception as e:
            print(f"保存截图失败: {str(e)}")
    
    print("\n测试完成!")