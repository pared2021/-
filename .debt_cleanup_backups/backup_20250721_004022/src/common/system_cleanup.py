from typing import Optional

def cleanup(container=None):
    """
    清理系统资源
    
    Args:
        container: 依赖注入容器实例
    """
    if container is not None:
        try:
            # 清理窗口管理器资源
            window_manager = container.window_manager()
            if window_manager is not None:
                window_manager.cleanup()
            
            # 清理日志资源
            logger = container.logger()
            if logger is not None:
                logger.cleanup()
                
            # 以下是安全检查，确保这些对象存在cleanup方法再调用
            # 清理图像处理资源
            image_processor = container.image_processor()
            if image_processor is not None and hasattr(image_processor, 'cleanup'):
                image_processor.cleanup()
                
            # 清理自动操作资源
            auto_operator = container.auto_operator()
            if auto_operator is not None and hasattr(auto_operator, 'cleanup'):
                auto_operator.cleanup()
                
            # 清理游戏分析服务资源
            game_analyzer = container.game_analyzer()
            if game_analyzer is not None and hasattr(game_analyzer, 'cleanup'):
                game_analyzer.cleanup()
                
        except Exception as e:
            print(f"清理资源时出错: {e}") 