"""几何类型定义"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Point:
    """点坐标"""
    x: int
    y: int
    
    def to_tuple(self) -> Tuple[int, int]:
        """转换为元组格式"""
        return (self.x, self.y)
    
    @classmethod
    def from_tuple(cls, point: Tuple[int, int]) -> 'Point':
        """从元组创建点"""
        return cls(x=point[0], y=point[1])


@dataclass
class Rectangle:
    """矩形区域"""
    x: int
    y: int
    width: int
    height: int
    
    @property
    def left(self) -> int:
        return self.x
    
    @property
    def top(self) -> int:
        return self.y
    
    @property
    def right(self) -> int:
        return self.x + self.width
    
    @property
    def bottom(self) -> int:
        return self.y + self.height
    
    @property
    def center(self) -> Point:
        """获取矩形中心点"""
        return Point(
            x=self.x + self.width // 2,
            y=self.y + self.height // 2
        )
    
    def contains(self, point: Point) -> bool:
        """检查点是否在矩形内"""
        return (self.left <= point.x <= self.right and 
                self.top <= point.y <= self.bottom)
    
    def to_tuple(self) -> Tuple[int, int, int, int]:
        """转换为元组格式 (x, y, width, height)"""
        return (self.x, self.y, self.width, self.height)
    
    @classmethod
    def from_tuple(cls, rect: Tuple[int, int, int, int]) -> 'Rectangle':
        """从元组创建矩形"""
        return cls(x=rect[0], y=rect[1], width=rect[2], height=rect[3])