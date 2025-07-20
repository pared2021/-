"""统一游戏状态定义"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from .geometry import Rectangle


@dataclass
class UnifiedGameState:
    """统一的游戏状态数据结构
    
    整合了原有的三个GameState定义：
    - 游戏状态管理服务的状态信息
    - 视觉识别的状态数据
    - 游戏适配器的状态表示
    """
    
    # 基础信息
    scene: str = "unknown"
    timestamp: float = 0.0
    confidence: float = 0.0
    
    # 视觉识别信息（来自 state_recognizer.py）
    name: str = ""
    features: Dict[str, Any] = field(default_factory=dict)
    region: Optional[Rectangle] = None
    template_matches: List[Any] = field(default_factory=list)  # 避免循环导入，暂时使用Any
    
    # 游戏变量（来自 game_adapter.py）
    ui_elements: Dict[str, Any] = field(default_factory=dict)
    game_variables: Dict[str, Any] = field(default_factory=dict)
    
    # 状态管理信息（来自 game_state.py 服务）
    state_id: Optional[str] = None
    previous_state: Optional[str] = None
    state_duration: float = 0.0
    
    # 扩展信息
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.name and self.scene:
            self.name = self.scene
    
    def is_valid(self) -> bool:
        """检查状态是否有效"""
        return self.confidence > 0 and bool(self.scene or self.name)
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return self.name or self.scene or "Unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            'scene': self.scene,
            'name': self.name,
            'timestamp': self.timestamp,
            'confidence': self.confidence,
            'features': self.features,
            'ui_elements': self.ui_elements,
            'game_variables': self.game_variables,
            'state_id': self.state_id,
            'previous_state': self.previous_state,
            'state_duration': self.state_duration,
            'metadata': self.metadata
        }
        
        if self.region:
            result['region'] = self.region.to_tuple()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedGameState':
        """从字典创建状态对象"""
        region = None
        if 'region' in data and data['region']:
            region = Rectangle.from_tuple(data['region'])
        
        return cls(
            scene=data.get('scene', 'unknown'),
            name=data.get('name', ''),
            timestamp=data.get('timestamp', 0.0),
            confidence=data.get('confidence', 0.0),
            features=data.get('features', {}),
            region=region,
            template_matches=data.get('template_matches', []),
            ui_elements=data.get('ui_elements', {}),
            game_variables=data.get('game_variables', {}),
            state_id=data.get('state_id'),
            previous_state=data.get('previous_state'),
            state_duration=data.get('state_duration', 0.0),
            metadata=data.get('metadata', {})
        )
    
    def merge_with(self, other: 'UnifiedGameState') -> 'UnifiedGameState':
        """与另一个状态合并"""
        merged_features = {**self.features, **other.features}
        merged_ui_elements = {**self.ui_elements, **other.ui_elements}
        merged_game_variables = {**self.game_variables, **other.game_variables}
        merged_metadata = {**self.metadata, **other.metadata}
        
        return UnifiedGameState(
            scene=other.scene or self.scene,
            name=other.name or self.name,
            timestamp=max(self.timestamp, other.timestamp),
            confidence=max(self.confidence, other.confidence),
            features=merged_features,
            region=other.region or self.region,
            template_matches=other.template_matches or self.template_matches,
            ui_elements=merged_ui_elements,
            game_variables=merged_game_variables,
            state_id=other.state_id or self.state_id,
            previous_state=self.scene if other.scene != self.scene else self.previous_state,
            state_duration=other.state_duration,
            metadata=merged_metadata
        )