"""Config类单元测试"""
import unittest
import os
import shutil
from tempfile import mkdtemp
from ....src.services.config import Config

class TestConfig(unittest.TestCase):
    """测试配置类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录用于测试
        self.temp_dir = mkdtemp()
        
    def tearDown(self):
        """测试后清理"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_config_values(self):
        """测试默认配置值"""
        config = Config()
        
        # 测试几个关键配置是否有默认值
        self.assertEqual(config.window.screenshot_interval, 0.1)
        self.assertEqual(config.action.mouse_speed, 0.5)
        self.assertEqual(config.image_processor.template_match_threshold, 0.8)
    
    def test_post_init_directory_creation(self):
        """测试初始化后目录创建"""
        # 修改配置，使用临时目录
        config = Config()
        config.template.output_dir = os.path.join(self.temp_dir, 'templates')
        config.logging.log_dir = os.path.join(self.temp_dir, 'logs')
        
        # 调用初始化后处理
        config.__post_init__()
        
        # 检查目录是否创建
        self.assertTrue(os.path.exists(config.template.output_dir))
        self.assertTrue(os.path.exists(config.logging.log_dir))
    
    def test_config_customization(self):
        """测试配置定制"""
        config = Config()
        
        # 修改配置
        config.window.window_title = "测试游戏"
        config.action.mouse_speed = 0.8
        config.image_processor.template_match_threshold = 0.9
        
        # 检查是否修改成功
        self.assertEqual(config.window.window_title, "测试游戏")
        self.assertEqual(config.action.mouse_speed, 0.8)
        self.assertEqual(config.image_processor.template_match_threshold, 0.9)

if __name__ == '__main__':
    unittest.main()