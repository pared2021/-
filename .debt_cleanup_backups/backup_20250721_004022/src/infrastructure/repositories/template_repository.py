"""
模板仓储实现

管理游戏界面模板数据和图像
支持模板的增删改查和图像处理
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import logging
import numpy as np
import cv2
from dependency_injector.wiring import inject, Provide
from typing import TYPE_CHECKING

from src.core.interfaces.repositories import ITemplateRepository, IConfigRepository

if TYPE_CHECKING:
    from src.application.containers.main_container import MainContainer


class TemplateRepository(ITemplateRepository):
    """
    模板仓储实现
    
    管理游戏界面模板的存储、加载和搜索
    """
    
    @inject
    def __init__(self, config_repository: IConfigRepository = Provide['config_repository']):
        self._config_repository = config_repository
        self._logger = logging.getLogger(__name__)
        self._cache = {}
        self._image_cache = {}
        self._base_path = None
        self._cache_size = 100
        self._auto_reload = True
        self._initialized = False
    
    def _ensure_initialized(self) -> bool:
        """确保模板仓储已初始化"""
        if not self._initialized:
            try:
                template_config = self._config_repository.get_config('templates', {})
                self._base_path = Path(template_config.get('base_path', 'templates'))
                self._cache_size = template_config.get('cache_size', 100)
                self._auto_reload = template_config.get('auto_reload', True)
                
                # 确保模板目录存在
                self._base_path.mkdir(parents=True, exist_ok=True)
                
                self._initialized = True
                return True
            except Exception as e:
                self._logger.error(f"Failed to initialize template repository: {str(e)}")
                return False
        return True
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """获取模板"""
        if not self._ensure_initialized():
            return None
        
        try:
            # 检查缓存
            if template_id in self._cache:
                return self._cache[template_id]
            
            # 从文件加载
            template_path = self._base_path / f"{template_id}.json"
            if not template_path.exists():
                return None
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            # 添加到缓存
            self._add_to_cache(template_id, template_data)
            
            return template_data
            
        except Exception as e:
            self._logger.error(f"Failed to get template '{template_id}': {str(e)}")
            return None
    
    def save_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """保存模板"""
        if not self._ensure_initialized():
            return False
        
        try:
            # 验证模板数据
            if not self._validate_template_data(template_data):
                return False
            
            # 保存到文件
            template_path = self._base_path / f"{template_id}.json"
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            
            # 更新缓存
            self._add_to_cache(template_id, template_data)
            
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to save template '{template_id}': {str(e)}")
            return False
    
    def delete_template(self, template_id: str) -> bool:
        """删除模板"""
        if not self._ensure_initialized():
            return False
        
        try:
            # 删除模板文件
            template_path = self._base_path / f"{template_id}.json"
            if template_path.exists():
                template_path.unlink()
            
            # 删除相关的图像文件
            image_path = self._base_path / f"{template_id}.png"
            if image_path.exists():
                image_path.unlink()
            
            # 从缓存中删除
            if template_id in self._cache:
                del self._cache[template_id]
            
            if template_id in self._image_cache:
                del self._image_cache[template_id]
            
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to delete template '{template_id}': {str(e)}")
            return False
    
    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出模板"""
        if not self._ensure_initialized():
            return []
        
        try:
            templates = []
            
            # 扫描模板目录
            for template_file in self._base_path.glob("*.json"):
                template_id = template_file.stem
                template_data = self.get_template(template_id)
                
                if template_data:
                    # 过滤分类
                    if category is None or template_data.get('category') == category:
                        templates.append({
                            'id': template_id,
                            'name': template_data.get('name', template_id),
                            'category': template_data.get('category', 'default'),
                            'description': template_data.get('description', ''),
                            'created_at': template_data.get('created_at', ''),
                            'updated_at': template_data.get('updated_at', '')
                        })
            
            return templates
            
        except Exception as e:
            self._logger.error(f"Failed to list templates: {str(e)}")
            return []
    
    def get_template_image(self, template_id: str) -> Optional[np.ndarray]:
        """获取模板图像"""
        if not self._ensure_initialized():
            return None
        
        try:
            # 检查图像缓存
            if template_id in self._image_cache:
                return self._image_cache[template_id]
            
            # 从文件加载图像
            image_path = self._base_path / f"{template_id}.png"
            if not image_path.exists():
                # 尝试其他格式
                for ext in ['.jpg', '.jpeg', '.bmp']:
                    alt_path = self._base_path / f"{template_id}{ext}"
                    if alt_path.exists():
                        image_path = alt_path
                        break
                else:
                    return None
            
            # 使用OpenCV加载图像
            image = cv2.imread(str(image_path))
            if image is None:
                return None
            
            # 转换为RGB格式
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 添加到缓存
            self._add_image_to_cache(template_id, image)
            
            return image
            
        except Exception as e:
            self._logger.error(f"Failed to get template image '{template_id}': {str(e)}")
            return None
    
    def save_template_image(self, template_id: str, image: np.ndarray) -> bool:
        """保存模板图像"""
        if not self._ensure_initialized():
            return False
        
        try:
            # 转换为BGR格式（OpenCV默认）
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                image_bgr = image
            
            # 保存图像
            image_path = self._base_path / f"{template_id}.png"
            success = cv2.imwrite(str(image_path), image_bgr)
            
            if success:
                # 更新图像缓存
                self._add_image_to_cache(template_id, image)
                return True
            else:
                return False
                
        except Exception as e:
            self._logger.error(f"Failed to save template image '{template_id}': {str(e)}")
            return False
    
    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """搜索模板"""
        if not self._ensure_initialized():
            return []
        
        try:
            all_templates = self.list_templates()
            query_lower = query.lower()
            
            # 搜索匹配的模板
            matching_templates = []
            for template in all_templates:
                # 检查名称、描述和分类
                if (query_lower in template['name'].lower() or
                    query_lower in template['description'].lower() or
                    query_lower in template['category'].lower()):
                    matching_templates.append(template)
            
            return matching_templates
            
        except Exception as e:
            self._logger.error(f"Failed to search templates: {str(e)}")
            return []
    
    def get_template_categories(self) -> List[str]:
        """获取模板分类"""
        if not self._ensure_initialized():
            return []
        
        try:
            categories = set()
            all_templates = self.list_templates()
            
            for template in all_templates:
                categories.add(template['category'])
            
            return sorted(list(categories))
            
        except Exception as e:
            self._logger.error(f"Failed to get template categories: {str(e)}")
            return []
    
    def _validate_template_data(self, template_data: Dict[str, Any]) -> bool:
        """验证模板数据"""
        try:
            # 检查必需字段
            required_fields = ['name', 'category']
            for field in required_fields:
                if field not in template_data:
                    self._logger.error(f"Missing required field: {field}")
                    return False
            
            # 检查数据类型
            if not isinstance(template_data['name'], str):
                self._logger.error("Template name must be a string")
                return False
            
            if not isinstance(template_data['category'], str):
                self._logger.error("Template category must be a string")
                return False
            
            return True
            
        except Exception as e:
            self._logger.error(f"Template validation failed: {str(e)}")
            return False
    
    def _add_to_cache(self, template_id: str, template_data: Dict[str, Any]) -> None:
        """添加到缓存"""
        try:
            # 如果缓存满了，删除最旧的项
            if len(self._cache) >= self._cache_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            
            self._cache[template_id] = template_data
            
        except Exception as e:
            self._logger.error(f"Failed to add to cache: {str(e)}")
    
    def _add_image_to_cache(self, template_id: str, image: np.ndarray) -> None:
        """添加图像到缓存"""
        try:
            # 如果缓存满了，删除最旧的项
            if len(self._image_cache) >= self._cache_size:
                oldest_key = next(iter(self._image_cache))
                del self._image_cache[oldest_key]
            
            self._image_cache[template_id] = image.copy()
            
        except Exception as e:
            self._logger.error(f"Failed to add image to cache: {str(e)}")
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._image_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            'template_cache_size': len(self._cache),
            'image_cache_size': len(self._image_cache),
            'max_cache_size': self._cache_size,
            'cache_hit_rate': 0.0  # 可以添加命中率统计
        }