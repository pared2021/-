"""
遗留代码适配器
确保现有代码与新的Clean Architecture兼容
"""

from typing import Optional, Any, TYPE_CHECKING
from src.core.interfaces.services import IGameAnalyzerService, IAutomationService, IStateManagerService
from src.core.interfaces.repositories import IConfigRepository, ITemplateRepository
from src.core.interfaces.adapters import IWindowAdapter, IInputAdapter

if TYPE_CHECKING:
    from src.application.containers.main_container import MainContainer


class LegacyAdapter:
    """遗留代码适配器类"""
    
    def __init__(self, container: 'MainContainer'):
        self.container = container
        self._game_analyzer_service = None
        self._automation_service = None
        self._state_manager_service = None
        self._config_repository = None
        self._template_repository = None
        self._window_adapter = None
        self._input_adapter = None
    
    @property
    def game_analyzer_service(self) -> IGameAnalyzerService:
        """获取游戏分析服务"""
        if self._game_analyzer_service is None:
            self._game_analyzer_service = self.container.game_analyzer_service()
        return self._game_analyzer_service
    
    @property
    def automation_service(self) -> IAutomationService:
        """获取自动化服务"""
        if self._automation_service is None:
            self._automation_service = self.container.automation_service()
        return self._automation_service
    
    @property
    def state_manager_service(self) -> IStateManagerService:
        """获取状态管理服务"""
        if self._state_manager_service is None:
            self._state_manager_service = self.container.state_manager_service()
        return self._state_manager_service
    
    @property
    def config_repository(self) -> IConfigRepository:
        """获取配置仓储"""
        if self._config_repository is None:
            self._config_repository = self.container.config_repository()
        return self._config_repository
    
    @property
    def template_repository(self) -> ITemplateRepository:
        """获取模板仓储"""
        if self._template_repository is None:
            self._template_repository = self.container.template_repository()
        return self._template_repository
    
    @property
    def window_adapter(self) -> IWindowAdapter:
        """获取窗口适配器"""
        if self._window_adapter is None:
            self._window_adapter = self.container.window_adapter()
        return self._window_adapter
    
    @property
    def input_adapter(self) -> IInputAdapter:
        """获取输入适配器"""
        if self._input_adapter is None:
            self._input_adapter = self.container.input_adapter()
        return self._input_adapter
    
    def get_config(self) -> Any:
        """获取配置 - 兼容性方法"""
        return self.config_repository.get_config()
    
    def analyze_frame(self, frame: Any) -> Any:
        """分析帧 - 兼容性方法"""
        return self.game_analyzer_service.analyze_frame(frame)
    
    def start_automation(self) -> bool:
        """启动自动化 - 兼容性方法"""
        return self.automation_service.start_automation()
    
    def stop_automation(self) -> bool:
        """停止自动化 - 兼容性方法"""
        return self.automation_service.stop_automation()
    
    def get_window_list(self) -> list:
        """获取窗口列表 - 兼容性方法"""
        return self.window_adapter.get_window_list()
    
    def get_window_info(self, hwnd: int) -> Any:
        """获取窗口信息 - 兼容性方法"""
        return self.window_adapter.get_window_info(hwnd)
    
    def capture_window(self, hwnd: int) -> Any:
        """捕获窗口 - 兼容性方法"""
        return self.window_adapter.capture_window(hwnd)
    
    def save_state(self, state: Any) -> bool:
        """保存状态 - 兼容性方法"""
        return self.state_manager_service.save_state(state)
    
    def load_state(self, state_id: str) -> Any:
        """加载状态 - 兼容性方法"""
        return self.state_manager_service.load_state(state_id)
    
    def get_templates(self) -> list:
        """获取模板 - 兼容性方法"""
        return self.template_repository.get_templates()
    
    def save_template(self, template: Any) -> bool:
        """保存模板 - 兼容性方法"""
        return self.template_repository.save_template(template)