from typing import Dict, List, Optional
import json
import os
from pathlib import Path

class StateHistoryModel:
    """状态历史记录模型"""
    
    def __init__(self, max_records: int = 1000):
        self.max_records = max_records
        self.history: List[Dict] = []
        self._init_storage()
        
    def _init_storage(self):
        """初始化存储目录"""
        self.storage_dir = Path("data/history")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
    def add_record(self, state: Dict):
        """添加状态记录"""
        self.history.append(state)
        
        # 保持记录数量在限制范围内
        if len(self.history) > self.max_records:
            self.history = self.history[-self.max_records:]
            
    def get_recent_records(self, count: int = 10) -> List[Dict]:
        """获取最近的记录"""
        return self.history[-count:]
        
    def get_records_by_state(self, state_name: str) -> List[Dict]:
        """获取指定状态的记录"""
        return [
            record for record in self.history
            if state_name in record
        ]
        
    def save_to_file(self, filename: Optional[str] = None):
        """保存历史记录到文件"""
        if filename is None:
            filename = f"state_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        filepath = self.storage_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
            
    def load_from_file(self, filename: str):
        """从文件加载历史记录"""
        filepath = self.storage_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
                
    def clear_history(self):
        """清空历史记录"""
        self.history = []
        
    def get_state_statistics(self, state_name: str) -> Dict:
        """获取状态的统计信息"""
        records = self.get_records_by_state(state_name)
        if not records:
            return {}
            
        values = []
        for record in records:
            try:
                value = float(record[state_name])
                values.append(value)
            except (ValueError, TypeError):
                continue
                
        if not values:
            return {}
            
        return {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "count": len(values)
        } 