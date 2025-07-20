"""统一模板匹配结果定义"""

from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Any
from .geometry import Point, Rectangle


@dataclass
class UnifiedTemplateMatchResult:
    """统一的模板匹配结果数据结构
    
    整合了原有的两个TemplateMatchResult定义：
    - 服务接口层的标准化匹配结果（core/interfaces/services.py）
    - 图像处理服务的模板特定结果（services/image_processor.py）
    """
    
    # 基础匹配信息（两个版本共有）
    found: bool = False
    confidence: float = 0.0
    
    # 位置信息（整合两种格式）
    location: Optional[Point] = None  # 来自 image_processor.py 的 Tuple[int, int]
    bounding_box: Optional[Rectangle] = None  # 来自 services.py
    
    # 模板信息（来自 image_processor.py）
    template_name: str = ""
    template_size: Optional[Tuple[int, int]] = None
    
    # 扩展信息
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        # 如果有位置但没有边界框，根据模板大小创建边界框
        if self.location and not self.bounding_box and self.template_size:
            self.bounding_box = Rectangle(
                x=self.location.x,
                y=self.location.y,
                width=self.template_size[0],
                height=self.template_size[1]
            )
        
        # 如果有边界框但没有位置，从边界框提取位置
        elif self.bounding_box and not self.location:
            self.location = Point(x=self.bounding_box.x, y=self.bounding_box.y)
        
        # 如果有边界框但没有模板大小，从边界框提取大小
        if self.bounding_box and not self.template_size:
            self.template_size = (self.bounding_box.width, self.bounding_box.height)
    
    def is_valid(self) -> bool:
        """检查匹配结果是否有效"""
        return (
            self.found and 
            self.confidence > 0 and 
            self.location is not None
        )
    
    def get_center_point(self) -> Optional[Point]:
        """获取匹配区域的中心点"""
        if self.bounding_box:
            return self.bounding_box.center
        elif self.location and self.template_size:
            return Point(
                x=self.location.x + self.template_size[0] // 2,
                y=self.location.y + self.template_size[1] // 2
            )
        return self.location
    
    def get_location_tuple(self) -> Optional[Tuple[int, int]]:
        """获取位置的元组格式（兼容原 image_processor.py）"""
        return self.location.to_tuple() if self.location else None
    
    def get_bounding_box_tuple(self) -> Optional[Tuple[int, int, int, int]]:
        """获取边界框的元组格式"""
        return self.bounding_box.to_tuple() if self.bounding_box else None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            'found': self.found,
            'confidence': self.confidence,
            'template_name': self.template_name,
            'metadata': self.metadata
        }
        
        if self.location:
            result['location'] = self.location.to_tuple()
        
        if self.bounding_box:
            result['bounding_box'] = self.bounding_box.to_tuple()
        
        if self.template_size:
            result['template_size'] = self.template_size
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedTemplateMatchResult':
        """从字典创建匹配结果对象"""
        location = None
        if 'location' in data and data['location']:
            location = Point.from_tuple(data['location'])
        
        bounding_box = None
        if 'bounding_box' in data and data['bounding_box']:
            bounding_box = Rectangle.from_tuple(data['bounding_box'])
        
        return cls(
            found=data.get('found', False),
            confidence=data.get('confidence', 0.0),
            location=location,
            bounding_box=bounding_box,
            template_name=data.get('template_name', ''),
            template_size=data.get('template_size'),
            metadata=data.get('metadata', {})
        )
    
    @classmethod
    def from_legacy_services(cls, found: bool, confidence: float, 
                            location: Optional[Point] = None,
                            bounding_box: Optional[Rectangle] = None) -> 'UnifiedTemplateMatchResult':
        """从原 services.py 的TemplateMatchResult创建（兼容格式）"""
        return cls(
            found=found,
            confidence=confidence,
            location=location,
            bounding_box=bounding_box
        )
    
    @classmethod
    def from_legacy_image_processor(cls, location: Tuple[int, int], confidence: float,
                                   template_name: str, template_size: Tuple[int, int]) -> 'UnifiedTemplateMatchResult':
        """从原 image_processor.py 的TemplateMatchResult创建（兼容格式）"""
        return cls(
            found=True,  # 原版本没有found字段，有结果就表示找到了
            confidence=confidence,
            location=Point.from_tuple(location),
            template_name=template_name,
            template_size=template_size
        )
    
    def to_legacy_services(self) -> Dict[str, Any]:
        """转换为原 services.py 兼容的格式"""
        return {
            'found': self.found,
            'confidence': self.confidence,
            'location': self.location,
            'bounding_box': self.bounding_box
        }
    
    def to_legacy_image_processor(self) -> Dict[str, Any]:
        """转换为原 image_processor.py 兼容的格式"""
        result = {
            'confidence': self.confidence,
            'template_name': self.template_name
        }
        
        if self.location:
            result['location'] = self.location.to_tuple()
        
        if self.template_size:
            result['template_size'] = self.template_size
        
        return result
    
    def merge_with(self, other: 'UnifiedTemplateMatchResult') -> 'UnifiedTemplateMatchResult':
        """与另一个匹配结果合并（取置信度更高的为主）"""
        if other.confidence > self.confidence:
            primary, secondary = other, self
        else:
            primary, secondary = self, other
        
        merged_metadata = {**secondary.metadata, **primary.metadata}
        
        return UnifiedTemplateMatchResult(
            found=primary.found or secondary.found,
            confidence=primary.confidence,
            location=primary.location or secondary.location,
            bounding_box=primary.bounding_box or secondary.bounding_box,
            template_name=primary.template_name or secondary.template_name,
            template_size=primary.template_size or secondary.template_size,
            metadata=merged_metadata
        )
    
    def __str__(self) -> str:
        """字符串表示"""
        if not self.found:
            return f"TemplateMatch(not found, template='{self.template_name}')"
        
        location_str = f"({self.location.x}, {self.location.y})" if self.location else "unknown"
        return f"TemplateMatch(found=True, confidence={self.confidence:.3f}, location={location_str}, template='{self.template_name}')"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"UnifiedTemplateMatchResult(found={self.found}, confidence={self.confidence}, "
                f"location={self.location}, bounding_box={self.bounding_box}, "
                f"template_name='{self.template_name}', template_size={self.template_size})")