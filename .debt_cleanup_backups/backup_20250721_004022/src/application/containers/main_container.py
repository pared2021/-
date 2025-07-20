"""
主依赖注入容器

基于dependency-injector库的企业级依赖注入容器
遵循Clean Architecture原则和FastAPI最佳实践
"""
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from src.core.interfaces.services import IGameAnalyzer, IAutomationService, IStateManager
from src.core.interfaces.repositories import IConfigRepository, ITemplateRepository
from src.core.interfaces.adapters import IWindowAdapter, IInputAdapter

from src.infrastructure.services.game_analyzer_service import GameAnalyzerService
from src.infrastructure.services.automation_service import AutomationService
from src.infrastructure.services.state_manager_service import StateManagerService
from src.infrastructure.repositories.config_repository import ConfigRepository
from src.infrastructure.repositories.template_repository import TemplateRepository
from src.infrastructure.adapters.window_adapter import WindowAdapter
from src.infrastructure.adapters.input_adapter import InputAdapter
from src.infrastructure.providers.config_provider import ConfigProvider


class MainContainer(containers.DeclarativeContainer):
    """
    主依赖注入容器
    
    遵循Clean Architecture原则：
    - 配置提供者：提供配置信息
    - 仓储层：数据访问接口
    - 适配器层：外部系统接口
    - 服务层：业务逻辑实现
    """
    
    # 配置提供者
    config_provider = providers.Singleton(ConfigProvider)
    
    # 仓储层 - 数据访问
    config_repository = providers.Singleton(ConfigRepository)
    
    template_repository = providers.Singleton(
        TemplateRepository,
        config_repository=config_repository
    )
    
    # 适配器层 - 外部系统接口
    window_adapter = providers.Singleton(
        WindowAdapter,
        config_repository=config_repository
    )
    
    input_adapter = providers.Singleton(
        InputAdapter,
        config_repository=config_repository
    )
    
    # 服务层 - 业务逻辑
    game_analyzer = providers.Singleton(
        GameAnalyzerService,
        config_repository=config_repository,
        template_repository=template_repository,
        window_adapter=window_adapter
    )
    
    automation_service = providers.Singleton(
        AutomationService,
        game_analyzer=game_analyzer,
        input_adapter=input_adapter,
        config_repository=config_repository
    )
    
    state_manager = providers.Singleton(
        StateManagerService,
        config_repository=config_repository,
        game_analyzer=game_analyzer
    )
    
    # 应用服务层
    # 这里可以添加更多的应用服务
    
    @classmethod
    def create_container(cls) -> 'MainContainer':
        """创建容器实例"""
        container = cls()
        container.wire(packages=[
            'src.presentation',
            'src.application',
            'src.core.use_cases'
        ])
        return container
    
    def get_game_analyzer(self) -> IGameAnalyzer:
        """获取游戏分析器服务"""
        return self.game_analyzer()
    
    def get_automation_service(self) -> IAutomationService:
        """获取自动化服务"""
        return self.automation_service()
    
    def get_state_manager(self) -> IStateManager:
        """获取状态管理器服务"""
        return self.state_manager()


# 全局容器实例
main_container = MainContainer.create_container() 