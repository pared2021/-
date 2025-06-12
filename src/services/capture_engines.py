"""
游戏捕获引擎模块 - 实现多种截图引擎
"""
import os
import cv2
import mss
import time
import numpy as np
import win32gui
import win32ui
import win32con
import win32process
from abc import ABC, abstractmethod
from typing import Optional, Dict, Tuple, Any
from dataclasses import dataclass
import threading
import ctypes
from ctypes import wintypes

@dataclass
class TargetInfo:
    """目标游戏窗口信息"""
    hwnd: Optional[int] = None
    title: Optional[str] = ''
    process_id: Optional[int] = None
    window_rect: Optional[Tuple[int, int, int, int]] = None
    is_fullscreen: bool = False
    
    @property
    def width(self) -> int:
        """获取窗口宽度"""
        if self.window_rect:
            return self.window_rect[2] - self.window_rect[0]
        return 0
    
    @property
    def height(self) -> int:
        """获取窗口高度"""
        if self.window_rect:
            return self.window_rect[3] - self.window_rect[1]
        return 0
    
    @property
    def is_valid(self) -> bool:
        """验证窗口信息是否有效"""
        return (self.hwnd is not None and 
                (self.window_rect is not None or self.process_id is not None))

class CaptureEngine(ABC):
    """捕获引擎基类"""
    
    def __init__(self, logger=None):
        """
        初始化引擎
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger
        self._initialized = False
        self._last_error = None
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化引擎"""
        pass
    
    @abstractmethod
    def capture(self, target_info: TargetInfo) -> Optional[np.ndarray]:
        """
        捕获目标窗口/进程的画面
        
        Args:
            target_info: 目标信息
            
        Returns:
            numpy.ndarray: 捕获的图像帧，如果失败则返回None
        """
        pass
    
    @abstractmethod
    def can_capture(self, target_info: TargetInfo) -> bool:
        """
        检查是否可以捕获目标
        
        Args:
            target_info: 目标信息
            
        Returns:
            bool: 如果可以捕获则返回True，否则返回False
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理资源"""
        pass
    
    def log(self, level: str, message: str):
        """
        记录日志
        
        Args:
            level: 日志级别
            message: 日志消息
        """
        if self.logger:
            method = getattr(self.logger, level.lower(), None)
            if method:
                method(f"[{self.__class__.__name__}] {message}")
    
    @property
    def name(self) -> str:
        """获取引擎名称"""
        return self.__class__.__name__
    
    @property
    def last_error(self) -> Optional[str]:
        """获取最后一次错误信息"""
        return self._last_error
    
    def __del__(self):
        """析构函数，确保资源被释放"""
        try:
            self.cleanup()
        except:
            pass


class MSSCaptureEngine(CaptureEngine):
    """基于MSS库的屏幕捕获引擎"""
    
    def __init__(self, logger=None):
        super().__init__(logger)
        self.sct = None
    
    def initialize(self) -> bool:
        """初始化MSS引擎"""
        try:
            # 确保先清理之前的资源
            self.cleanup()
            
            # 使用上下文管理器创建MSS实例
            self.sct = mss.mss()
            self._initialized = True
            self.log('info', "MSS捕获引擎初始化成功")
            return True
        except Exception as e:
            self._last_error = str(e)
            self.log('error', f"MSS捕获引擎初始化失败: {e}")
            return False
    
    def can_capture(self, target_info: TargetInfo) -> bool:
        """检查是否可以使用MSS捕获目标窗口"""
        if not self._initialized:
            if not self.initialize():
                return False
        
        # MSS需要有效的窗口句柄和矩形区域
        if not target_info.is_valid or not target_info.window_rect:
            return False
            
        # 检查窗口是否可见
        try:
            if target_info.hwnd and not win32gui.IsWindowVisible(target_info.hwnd):
                return False
        except:
            return False
            
        # 检查窗口尺寸是否有效
        if target_info.width <= 0 or target_info.height <= 0:
            return False
            
        return True
    
    def capture(self, target_info: TargetInfo) -> Optional[np.ndarray]:
        """使用MSS捕获窗口"""
        if not self.can_capture(target_info):
            return None
        
        try:
            # 创建截图区域
            left, top, right, bottom = target_info.window_rect
            width = right - left
            height = bottom - top
            
            # 确保宽高为正值
            if width <= 0 or height <= 0:
                self.log('error', f"无效的窗口尺寸: {width}x{height}")
                return None
                
            monitor = {
                "top": top,
                "left": left,
                "width": width,
                "height": height
            }
            
            # 捕获屏幕
            screenshot = self.sct.grab(monitor)
            
            # 检查截图尺寸是否与请求的一致
            if screenshot.width != width or screenshot.height != height:
                self.log('warning', f"截图尺寸不匹配: 请求={width}x{height}, 获取={screenshot.width}x{screenshot.height}")
                # 如果差异很小，可以继续处理
                if abs(screenshot.width - width) > 10 or abs(screenshot.height - height) > 10:
                    self.log('error', "截图尺寸差异过大")
                    return None
            
            # 转换为numpy数组
            frame = np.array(screenshot)
            if frame is None or frame.size == 0:
                self.log('error', "无法转换截图为numpy数组")
                return None
            
            # 检查格式并转换
            if len(frame.shape) == 3 and frame.shape[2] == 4:
                # BGRA到BGR转换
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
            return frame
            
        except Exception as e:
            self._last_error = str(e)
            self.log('error', f"MSS捕获失败: {e}")
            
            # 尝试重新初始化
            try:
                self.cleanup()
                time.sleep(0.2)
                self.initialize()
            except Exception as reinit_error:
                self.log('error', f"MSS重新初始化失败: {reinit_error}")
                
            return None
    
    def cleanup(self):
        """清理MSS资源"""
        if self.sct:
            try:
                self.sct.close()
            except Exception as e:
                self.log('warning', f"关闭MSS资源时出错: {e}")
            finally:
                self.sct = None
                self._initialized = False


class GDICaptureEngine(CaptureEngine):
    """基于Windows GDI的窗口捕获引擎"""
    
    def initialize(self) -> bool:
        """初始化GDI引擎"""
        # GDI无需特殊初始化
        self._initialized = True
        self.log('info', "GDI捕获引擎初始化成功")
        return True
    
    def can_capture(self, target_info: TargetInfo) -> bool:
        """检查是否可以使用GDI捕获目标窗口"""
        if not self._initialized:
            if not self.initialize():
                return False
                
        # GDI需要有效的窗口句柄
        if not target_info.hwnd:
            return False
            
        # 检查窗口是否有效
        try:
            if not win32gui.IsWindow(target_info.hwnd):
                return False
                
            # 检查窗口是否可见
            if not win32gui.IsWindowVisible(target_info.hwnd):
                return False
                
            # 检查窗口是否最小化
            if win32gui.IsIconic(target_info.hwnd):
                return False
                
            # 尝试获取窗口DC，验证是否可访问
            dc = win32gui.GetWindowDC(target_info.hwnd)
            win32gui.ReleaseDC(target_info.hwnd, dc)
            
            return True
        except:
            return False
    
    def capture(self, target_info: TargetInfo) -> Optional[np.ndarray]:
        """使用GDI捕获窗口"""
        if not self.can_capture(target_info):
            return None
            
        try:
            # 获取窗口位置和大小
            if target_info.window_rect:
                left, top, right, bottom = target_info.window_rect
            else:
                try:
                    left, top, right, bottom = win32gui.GetWindowRect(target_info.hwnd)
                except Exception as e:
                    self.log('error', f"获取窗口位置失败: {e}")
                    return None
                    
            width = right - left
            height = bottom - top
            
            if width <= 0 or height <= 0:
                self.log('error', f"窗口尺寸无效: {width}x{height}")
                return None
            
            # 创建设备上下文
            hwnd_dc = win32gui.GetWindowDC(target_info.hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            
            # 创建位图对象
            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(save_bitmap)
            
            # 复制窗口内容到位图
            result = ctypes.windll.user32.PrintWindow(
                target_info.hwnd, save_dc.GetSafeHdc(), 3)
            
            # 检查是否成功
            if result == 0:
                self.log('warning', "PrintWindow返回0，尝试使用BitBlt")
                # 备用方法：使用BitBlt
                save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)
            
            # 获取位图信息
            bmp_info = save_bitmap.GetInfo()
            bmp_str = save_bitmap.GetBitmapBits(True)
            
            # 转换为numpy数组
            img = np.frombuffer(bmp_str, dtype=np.uint8)
            img.shape = (height, width, 4)  # BGRA格式
            
            # 转换为BGR格式
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # 释放资源
            win32gui.DeleteObject(save_bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(target_info.hwnd, hwnd_dc)
            
            return img
            
        except Exception as e:
            self._last_error = str(e)
            self.log('error', f"GDI捕获失败: {e}")
            return None
    
    def cleanup(self):
        """清理GDI资源"""
        # GDI无需特殊清理
        pass


class DXGICaptureEngine(CaptureEngine):
    """基于DXGI的游戏画面捕获引擎"""
    
    def __init__(self, logger=None):
        super().__init__(logger)
        # 标记是否已加载DXGI库
        self.dxgi_loaded = False
        # 保存DXGI输出复制对象
        self.output_duplication = None
        self.device = None
        self.device_context = None
        # 尝试导入所需模块
        try:
            import d3dshot
            self.d3dshot = d3dshot
            self.d3d_instance = None
            self.dxgi_loaded = True
        except ImportError:
            self.log('warning', "无法导入d3dshot模块，DXGI捕获引擎将不可用")
            self.d3dshot = None
            self.d3d_instance = None
    
    def initialize(self) -> bool:
        """初始化DXGI引擎"""
        if not self.dxgi_loaded:
            self._last_error = "未安装DXGI捕获依赖"
            return False
            
        try:
            if self.d3d_instance is None:
                self.d3d_instance = self.d3dshot.create(capture_output="numpy")
                self.log('info', "DXGI捕获引擎初始化成功")
            self._initialized = True
            return True
        except Exception as e:
            self._last_error = str(e)
            self.log('error', f"DXGI捕获引擎初始化失败: {e}")
            return False
    
    def can_capture(self, target_info: TargetInfo) -> bool:
        """检查是否可以使用DXGI捕获目标窗口"""
        if not self.dxgi_loaded or not self._initialized:
            if not self.initialize():
                return False
                
        # 检查是否全屏模式，DXGI更适合全屏模式游戏
        if target_info.is_fullscreen:
            return True
            
        # 检查是否有进程ID，这是DXGI捕获的必要条件
        if target_info.process_id:
            return True
            
        # 如果有窗口句柄，尝试获取进程ID
        if target_info.hwnd:
            try:
                _, process_id = win32process.GetWindowThreadProcessId(target_info.hwnd)
                if process_id:
                    return True
            except:
                pass
                
        return False
    
    def capture(self, target_info: TargetInfo) -> Optional[np.ndarray]:
        """使用DXGI捕获窗口"""
        if not self.can_capture(target_info):
            return None
            
        try:
            # 获取区域信息
            if target_info.window_rect:
                left, top, right, bottom = target_info.window_rect
                region = (left, top, right, bottom)
            else:
                region = None
                
            # 捕获画面
            if target_info.is_fullscreen:
                # 全屏捕获
                screenshot = self.d3d_instance.screenshot()
            else:
                # 区域捕获
                screenshot = self.d3d_instance.screenshot(region=region)
                
            if screenshot is None:
                self.log('warning', "DXGI捕获返回空结果")
                return None
                
            # 确保格式正确
            if len(screenshot.shape) == 3 and screenshot.shape[2] == 4:
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
                
            return screenshot
            
        except Exception as e:
            self._last_error = str(e)
            self.log('error', f"DXGI捕获失败: {e}")
            # 尝试重新初始化
            try:
                self.cleanup()
                self.initialize()
            except:
                pass
            return None
    
    def cleanup(self):
        """清理DXGI资源"""
        if self.d3d_instance:
            try:
                del self.d3d_instance
            except:
                pass
            self.d3d_instance = None
        self._initialized = False


class ProcessMemoryEngine(CaptureEngine):
    """基于进程内存的游戏画面捕获引擎"""
    
    def __init__(self, logger=None):
        super().__init__(logger)
        # 进程句柄
        self.process_handle = None
        self.target_process_id = None
        # 尝试导入所需模块
        try:
            import psutil
            import pymem
            self.psutil = psutil
            self.pymem = pymem
            self.memory_loaded = True
        except ImportError:
            self.log('warning', "无法导入psutil或pymem模块，进程内存捕获引擎将不可用")
            self.psutil = None
            self.pymem = None
            self.memory_loaded = False
    
    def initialize(self) -> bool:
        """初始化进程内存引擎"""
        if not self.memory_loaded:
            self._last_error = "未安装进程内存捕获依赖"
            return False
            
        self._initialized = True
        self.log('info', "进程内存捕获引擎初始化成功")
        return True
    
    def can_capture(self, target_info: TargetInfo) -> bool:
        """检查是否可以使用进程内存捕获目标窗口"""
        if not self.memory_loaded or not self._initialized:
            if not self.initialize():
                return False
                
        # 进程内存捕获需要进程ID
        if target_info.process_id is None:
            # 尝试从窗口句柄获取进程ID
            if target_info.hwnd:
                try:
                    _, process_id = win32process.GetWindowThreadProcessId(target_info.hwnd)
                    if process_id:
                        # 更新目标信息
                        target_info.process_id = process_id
                    else:
                        return False
                except:
                    return False
            else:
                return False
                
        # 检查进程是否存在且可访问
        try:
            process = self.psutil.Process(target_info.process_id)
            if not process.is_running():
                return False
            return True
        except:
            return False
    
    def capture(self, target_info: TargetInfo) -> Optional[np.ndarray]:
        """
        使用进程内存捕获窗口
        
        注意：这是一个高级捕获方法，需要针对特定游戏开发内存读取策略。
        这里提供了一个框架，但实际实现需要针对特定游戏开发。
        """
        if not self.can_capture(target_info):
            return None
            
        try:
            # 检查进程ID是否变化
            if self.target_process_id != target_info.process_id:
                self.cleanup()
                self.target_process_id = target_info.process_id
                self.process_handle = self.pymem.Pymem(self.target_process_id)
                
            # 这里需要针对特定游戏实现内存读取逻辑
            # 由于每个游戏的内存结构不同，无法提供通用实现
            # 下面是一个占位实现，实际使用时需要替换
            
            self.log('warning', "进程内存捕获需要针对特定游戏实现")
            
            # 如果没有实现特定游戏的内存读取，回退到其他捕获方式
            return None
            
        except Exception as e:
            self._last_error = str(e)
            self.log('error', f"进程内存捕获失败: {e}")
            return None
    
    def cleanup(self):
        """清理进程内存资源"""
        if self.process_handle:
            try:
                self.process_handle.close_process()
            except:
                pass
            self.process_handle = None
        self.target_process_id = None


class GameCaptureEngine:
    """
    游戏捕获引擎 - 集成多种捕获方式
    
    这个类实现了文档中建议的捕获引擎架构，集成了多种截图技术，
    能够根据游戏特性自动选择最适合的捕获方式。
    """
    
    def __init__(self, logger=None):
        """
        初始化游戏捕获引擎
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger
        self.last_successful_engine = None
        self.engines = []
        self.engine_stats = {}  # 记录每个引擎的成功率和性能数据
        
        try:
            # 初始化各种捕获引擎
            self.engines = [
                DXGICaptureEngine(logger),    # DirectX游戏首选
                GDICaptureEngine(logger),     # 传统窗口应用
                MSSCaptureEngine(logger),     # 备选方案
                ProcessMemoryEngine(logger)   # 最终兜底方案
            ]
            
            # 初始化各引擎
            for engine in self.engines:
                try:
                    engine.initialize()
                    # 初始化引擎统计数据
                    self.engine_stats[engine.name] = {
                        'success_count': 0,
                        'fail_count': 0,
                        'avg_capture_time': 0,
                        'last_success_time': 0
                    }
                except Exception as e:
                    if logger:
                        logger.error(f"初始化引擎 {engine.name} 失败: {e}")
                
            if logger:
                available_engines = [engine.name for engine in self.engines if engine._initialized]
                logger.info(f"已初始化捕获引擎: {', '.join(available_engines)}")
        except Exception as e:
            if logger:
                logger.error(f"初始化捕获引擎系统失败: {e}")
    
    def _get_engine_priority(self, target_info: TargetInfo) -> list:
        """
        根据目标窗口特性确定引擎优先级
        
        Args:
            target_info: 目标游戏信息
            
        Returns:
            list: 按优先级排序的引擎列表
        """
        # 创建引擎优先级列表的副本
        prioritized_engines = self.engines.copy()
        
        # 根据窗口特性调整优先级
        if target_info.is_fullscreen:
            # 全屏模式优先使用DXGI
            prioritized_engines.sort(key=lambda e: 0 if isinstance(e, DXGICaptureEngine) else 
                                    (1 if isinstance(e, GDICaptureEngine) else 
                                     2 if isinstance(e, MSSCaptureEngine) else 3))
        elif target_info.process_id:
            # 有进程ID但非全屏，可能是游戏窗口模式，DXGI和GDI都适合
            prioritized_engines.sort(key=lambda e: 0 if isinstance(e, DXGICaptureEngine) else 
                                    (1 if isinstance(e, GDICaptureEngine) else 
                                     2 if isinstance(e, MSSCaptureEngine) else 3))
        else:
            # 普通窗口应用，优先使用GDI
            prioritized_engines.sort(key=lambda e: 0 if isinstance(e, GDICaptureEngine) else 
                                    (1 if isinstance(e, MSSCaptureEngine) else 
                                     2 if isinstance(e, DXGICaptureEngine) else 3))
        
        # 根据历史成功率进一步调整优先级
        if self.last_successful_engine and self.last_successful_engine in prioritized_engines:
            # 如果上次成功的引擎在列表中，将其移到最前面
            prioritized_engines.remove(self.last_successful_engine)
            prioritized_engines.insert(0, self.last_successful_engine)
        
        return prioritized_engines
    
    def _update_engine_stats(self, engine, success: bool, capture_time: float = 0):
        """
        更新引擎统计数据
        
        Args:
            engine: 捕获引擎
            success: 是否成功捕获
            capture_time: 捕获耗时(秒)
        """
        if engine.name not in self.engine_stats:
            self.engine_stats[engine.name] = {
                'success_count': 0,
                'fail_count': 0,
                'avg_capture_time': 0,
                'last_success_time': 0
            }
            
        stats = self.engine_stats[engine.name]
        if success:
            stats['success_count'] += 1
            stats['last_success_time'] = time.time()
            
            # 更新平均捕获时间
            if stats['avg_capture_time'] == 0:
                stats['avg_capture_time'] = capture_time
            else:
                # 使用加权平均，新数据权重为0.3
                stats['avg_capture_time'] = stats['avg_capture_time'] * 0.7 + capture_time * 0.3
        else:
            stats['fail_count'] += 1
    
    def capture(self, target_info: TargetInfo) -> Optional[np.ndarray]:
        """
        捕获游戏画面
        
        根据目标窗口特性智能选择最适合的捕获引擎
        
        Args:
            target_info: 目标游戏信息
            
        Returns:
            numpy.ndarray: 捕获的游戏画面，失败返回None
        """
        # 验证目标信息
        if not target_info or not target_info.is_valid:
            if self.logger:
                self.logger.warning("无效的目标信息")
            return None
            
        # 检查窗口尺寸是否有效
        if target_info.width <= 0 or target_info.height <= 0:
            if self.logger:
                self.logger.warning(f"无效的窗口尺寸: {target_info.width}x{target_info.height}")
            return None
            
        try:
            # 获取针对当前窗口特性的引擎优先级
            prioritized_engines = self._get_engine_priority(target_info)
            
            # 按优先级尝试各引擎
            for engine in prioritized_engines:
                if not engine._initialized:
                    continue
                    
                try:
                    if engine.can_capture(target_info):
                        if self.logger:
                            self.logger.debug(f"尝试使用 {engine.name} 捕获画面")
                        
                        # 记录开始时间
                        start_time = time.time()
                        
                        # 执行捕获
                        frame = engine.capture(target_info)
                        
                        # 计算耗时
                        capture_time = time.time() - start_time
                        
                        if frame is not None and isinstance(frame, np.ndarray) and frame.size > 0:
                            # 检查图像是否有效（非全黑或全白）
                            mean_value = np.mean(frame)
                            if mean_value < 5 or mean_value > 250:
                                if self.logger:
                                    self.logger.warning(f"捕获的图像可能无效，平均值: {mean_value}，尝试下一个引擎")
                                self._update_engine_stats(engine, False, capture_time)
                                continue
                            
                            # 更新统计数据
                            self._update_engine_stats(engine, True, capture_time)
                            
                            # 记录成功的引擎
                            self.last_successful_engine = engine
                            if self.logger:
                                self.logger.info(f"成功使用 {engine.name} 捕获画面，耗时: {capture_time:.3f}秒")
                            return frame
                        else:
                            # 更新失败统计
                            self._update_engine_stats(engine, False, capture_time)
                            if self.logger:
                                self.logger.warning(f"{engine.name} 捕获失败，耗时: {capture_time:.3f}秒")
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"使用引擎 {engine.name} 时出错: {e}")
                    # 更新失败统计
                    self._update_engine_stats(engine, False)
                    continue
            
            if self.logger:
                self.logger.error("所有捕获引擎都失败了")
            return None
        except Exception as e:
            if self.logger:
                self.logger.error(f"捕获过程中发生未处理异常: {e}")
            return None
    
    def cleanup(self):
        """清理所有引擎资源"""
        for engine in self.engines:
            try:
                engine.cleanup()
            except Exception as e:
                if self.logger:
                    self.logger.error(f"清理引擎 {engine.name} 失败: {e}")
    
    def get_engine_status(self) -> dict:
        """
        获取各引擎状态信息
        
        Returns:
            dict: 包含各引擎状态的字典
        """
        status = {
            'last_successful_engine': self.last_successful_engine.name if self.last_successful_engine else None,
            'engines': {}
        }
        
        for engine in self.engines:
            engine_status = {
                'initialized': engine._initialized,
                'last_error': engine.last_error
            }
            
            # 添加统计数据
            if engine.name in self.engine_stats:
                engine_status.update(self.engine_stats[engine.name])
                # 计算成功率
                total = engine_status['success_count'] + engine_status['fail_count']
                if total > 0:
                    engine_status['success_rate'] = engine_status['success_count'] / total
                else:
                    engine_status['success_rate'] = 0
            
            status['engines'][engine.name] = engine_status
            
        return status
    
    def __del__(self):
        """析构函数，确保资源被释放"""
        self.cleanup()