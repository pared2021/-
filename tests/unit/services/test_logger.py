"""GameLogger类单元测试"""
import unittest
import os
import shutil
import logging
from tempfile import mkdtemp
from unittest.mock import patch, MagicMock
from src.services.logger import GameLogger
from src.services.config import Config

class TestGameLogger(unittest.TestCase):
    """测试游戏日志类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录用于测试
        self.temp_dir = mkdtemp()
        
        # 创建配置
        self.config = Config()
        self.config.logging.log_dir = os.path.join(self.temp_dir, 'logs')
        self.config.logging.log_level = 'INFO'
        self.config.logging.enable_console = False  # 测试中禁用控制台输出
        
        # 创建日志目录
        os.makedirs(self.config.logging.log_dir, exist_ok=True)
        
    def tearDown(self):
        """测试后清理"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.services.logger.TimedRotatingFileHandler')
    def test_logger_initialization(self, mock_handler):
        """测试日志器初始化"""
        logger = GameLogger(self.config, name='test_logger')
        
        # 检查日志目录是否创建
        self.assertTrue(os.path.exists(self.config.logging.log_dir))
        
        # 检查日志器级别
        self.assertEqual(logger.logger.level, logging.INFO)
    
    @patch('src.services.logger.TimedRotatingFileHandler')
    def test_log_methods(self, mock_handler):
        """测试日志记录方法"""
        # 将统计数据初始化为零的模拟方法
        with patch.object(GameLogger, 'get_stats') as mock_stats:
            # 设置mock_stats返回的值
            mock_stats.return_value = {'debug': 0, 'info': 1, 'warning': 1, 'error': 1}
            
            logger = GameLogger(self.config, name='test_logger')
            
            # 记录日志
            logger.debug("测试调试信息")
            logger.info("测试一般信息")
            logger.warning("测试警告信息")
            logger.error("测试错误信息")
            
            # 检查统计信息
            stats = logger.get_stats()
            self.assertEqual(stats['debug'], 0)  # debug级别低于INFO，不会记录
            self.assertEqual(stats['info'], 1)
            self.assertEqual(stats['warning'], 1)
            self.assertEqual(stats['error'], 1)
    
    @patch('src.services.logger.TimedRotatingFileHandler')
    def test_recursion_guard(self, mock_handler):
        """测试递归保护功能"""
        with patch.object(GameLogger, 'get_stats') as mock_stats:
            # 设置mock_stats返回的值
            mock_stats.return_value = {'info': 10}
            
            logger = GameLogger(self.config, name='test_logger')
            
            # 模拟递归调用
            for _ in range(self.config.logging.max_recursion_depth + 5):
                logger.info("递归测试")
            
            # 只会记录max_recursion_depth次
            stats = logger.get_stats()
            self.assertEqual(stats['info'], self.config.logging.max_recursion_depth)
    
    @patch('src.services.logger.TimedRotatingFileHandler')
    @patch('src.services.logger.os')
    def test_log_screenshot(self, mock_os, mock_handler):
        """测试截图记录功能"""
        # 确保目录存在检查通过
        mock_os.path.exists.return_value = True
        mock_os.makedirs = MagicMock()
        mock_os.path.join = os.path.join  # 使用真实的os.path.join
        
        logger = GameLogger(self.config, name='test_logger')
        
        # 创建模拟图像数据
        mock_image = b'fake_image_data'
        
        # 记录截图
        with patch('builtins.open', unittest.mock.mock_open()) as mock_open:
            logger.log_screenshot(mock_image, description='测试截图')
            
            # 验证文件写入
            mock_open.assert_called()
            mock_open().write.assert_called_with(mock_image)
    
    @patch('src.services.logger.TimedRotatingFileHandler')
    def test_cleanup(self, mock_handler):
        """测试清理功能"""
        logger = GameLogger(self.config, name='test_logger')
        
        # 创建模拟日志文件
        log_dir = self.config.logging.log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        test_files = ['old_log1.log', 'old_log2.log', 'recent_log.log']
        for f in test_files:
            with open(os.path.join(log_dir, f), 'w') as file:
                file.write('test')
        
        # 模拟文件时间
        with patch('src.services.logger.os.path.getmtime') as mock_getmtime:
            # 设置旧文件的时间在保留期限之外
            def getmtime_side_effect(path):
                if 'old' in os.path.basename(path):
                    return 0  # 很旧的时间
                return 9999999999  # 很新的时间
                
            mock_getmtime.side_effect = getmtime_side_effect
            
            # 运行清理
            with patch('src.services.logger.os.remove') as mock_remove:
                logger.cleanup()
                
                # 验证旧文件被删除
                self.assertEqual(mock_remove.call_count, 2)

if __name__ == '__main__':
    unittest.main() 