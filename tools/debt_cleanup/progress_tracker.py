#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
债务清理进度跟踪器

跟踪和监控技术债务清理的进度，包括：
- 任务进度跟踪
- 质量指标监控
- 性能基准测试
- 清理效果评估
"""

import time
import psutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import sqlite3
import threading


@dataclass
class QualityMetrics:
    """质量指标"""
    timestamp: datetime
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    cyclomatic_complexity: float
    test_coverage: float
    duplicate_code_ratio: float
    technical_debt_ratio: float
    maintainability_index: float


@dataclass
class PerformanceMetrics:
    """性能指标"""
    timestamp: datetime
    startup_time: float  # 启动时间（秒）
    memory_usage: float  # 内存使用（MB）
    cpu_usage: float     # CPU使用率（%）
    build_time: float    # 构建时间（秒）
    test_execution_time: float  # 测试执行时间（秒）


@dataclass
class TaskProgress:
    """任务进度"""
    task_id: str
    status: str
    progress_percent: float
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    actual_hours: float = 0.0
    estimated_hours: float = 0.0
    notes: str = ""


class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self, db_path: str = "debt_cleanup_progress.db"):
        self.db_path = db_path
        self.project_root = Path(".")
        
        # 初始化数据库
        self._init_database()
        
        # 监控线程
        self._monitoring = False
        self._monitor_thread = None
        
        # 基准指标
        self.baseline_metrics = None
    
    def _init_database(self) -> None:
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_lines INTEGER,
                code_lines INTEGER,
                comment_lines INTEGER,
                blank_lines INTEGER,
                cyclomatic_complexity REAL,
                test_coverage REAL,
                duplicate_code_ratio REAL,
                technical_debt_ratio REAL,
                maintainability_index REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                startup_time REAL,
                memory_usage REAL,
                cpu_usage REAL,
                build_time REAL,
                test_execution_time REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_progress (
                task_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                progress_percent REAL,
                start_time TEXT,
                end_time TEXT,
                estimated_completion TEXT,
                actual_hours REAL,
                estimated_hours REAL,
                notes TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def start_monitoring(self, interval: int = 300) -> None:
        """开始监控（每5分钟收集一次指标）"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """停止监控"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join()
    
    def _monitor_loop(self, interval: int) -> None:
        """监控循环"""
        while self._monitoring:
            try:
                # 收集质量指标
                quality_metrics = self._collect_quality_metrics()
                if quality_metrics:
                    self._save_quality_metrics(quality_metrics)
                
                # 收集性能指标
                performance_metrics = self._collect_performance_metrics()
                if performance_metrics:
                    self._save_performance_metrics(performance_metrics)
                
            except Exception as e:
                print(f"监控过程中发生错误：{e}")
            
            time.sleep(interval)
    
    def _collect_quality_metrics(self) -> Optional[QualityMetrics]:
        """收集质量指标"""
        try:
            # 统计代码行数
            total_lines, code_lines, comment_lines, blank_lines = self._count_lines()
            
            # 计算圈复杂度（简化版）
            complexity = self._calculate_complexity()
            
            # 获取测试覆盖率
            coverage = self._get_test_coverage()
            
            # 计算重复代码比率（简化版）
            duplicate_ratio = self._calculate_duplicate_ratio()
            
            # 计算技术债务比率
            debt_ratio = self._calculate_debt_ratio()
            
            # 计算可维护性指数
            maintainability = self._calculate_maintainability_index(
                complexity, coverage, duplicate_ratio
            )
            
            return QualityMetrics(
                timestamp=datetime.now(),
                total_lines=total_lines,
                code_lines=code_lines,
                comment_lines=comment_lines,
                blank_lines=blank_lines,
                cyclomatic_complexity=complexity,
                test_coverage=coverage,
                duplicate_code_ratio=duplicate_ratio,
                technical_debt_ratio=debt_ratio,
                maintainability_index=maintainability
            )
            
        except Exception as e:
            print(f"收集质量指标失败：{e}")
            return None
    
    def _collect_performance_metrics(self) -> Optional[PerformanceMetrics]:
        """收集性能指标"""
        try:
            # 测量启动时间
            startup_time = self._measure_startup_time()
            
            # 获取当前内存使用
            memory_usage = psutil.virtual_memory().used / 1024 / 1024  # MB
            
            # 获取当前CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 测量构建时间
            build_time = self._measure_build_time()
            
            # 测量测试执行时间
            test_time = self._measure_test_time()
            
            return PerformanceMetrics(
                timestamp=datetime.now(),
                startup_time=startup_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                build_time=build_time,
                test_execution_time=test_time
            )
            
        except Exception as e:
            print(f"收集性能指标失败：{e}")
            return None
    
    def _count_lines(self) -> tuple:
        """统计代码行数"""
        total_lines = 0
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        for py_file in self.project_root.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".venv" in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line in lines:
                    total_lines += 1
                    stripped = line.strip()
                    
                    if not stripped:
                        blank_lines += 1
                    elif stripped.startswith('#'):
                        comment_lines += 1
                    else:
                        code_lines += 1
                        
            except Exception:
                continue
        
        return total_lines, code_lines, comment_lines, blank_lines
    
    def _calculate_complexity(self) -> float:
        """计算平均圈复杂度（简化版）"""
        try:
            # 使用radon工具计算复杂度
            result = subprocess.run(
                ["python", "-m", "radon", "cc", "src", "--average"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 解析输出获取平均复杂度
                output = result.stdout
                # 简化解析，实际需要更复杂的逻辑
                return 2.5  # 默认值
            
        except Exception:
            pass
        
        return 2.5  # 默认复杂度
    
    def _get_test_coverage(self) -> float:
        """获取测试覆盖率"""
        try:
            # 运行coverage工具
            result = subprocess.run(
                ["python", "-m", "coverage", "report", "--format=json"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                coverage_data = json.loads(result.stdout)
                return coverage_data.get("totals", {}).get("percent_covered", 0.0)
            
        except Exception:
            pass
        
        return 0.0  # 默认覆盖率
    
    def _calculate_duplicate_ratio(self) -> float:
        """计算重复代码比率（简化版）"""
        # 这里需要实现代码重复检测算法
        # 简化实现，返回估算值
        return 15.0  # 15%重复率
    
    def _calculate_debt_ratio(self) -> float:
        """计算技术债务比率"""
        # 基于已知问题数量计算债务比率
        # 这里可以集成debt_analyzer的结果
        return 25.0  # 25%债务比率
    
    def _calculate_maintainability_index(self, complexity: float, coverage: float, duplicate_ratio: float) -> float:
        """计算可维护性指数"""
        # 简化的可维护性指数计算
        # 实际公式更复杂，考虑多个因素
        base_score = 100
        complexity_penalty = complexity * 5
        coverage_bonus = coverage * 0.3
        duplicate_penalty = duplicate_ratio * 2
        
        score = base_score - complexity_penalty + coverage_bonus - duplicate_penalty
        return max(0, min(100, score))
    
    def _measure_startup_time(self) -> float:
        """测量应用启动时间"""
        try:
            start_time = time.time()
            result = subprocess.run(
                ["python", "main.py", "--version"],
                capture_output=True,
                timeout=30
            )
            end_time = time.time()
            
            if result.returncode == 0:
                return end_time - start_time
            
        except Exception:
            pass
        
        return 0.0
    
    def _measure_build_time(self) -> float:
        """测量构建时间"""
        try:
            start_time = time.time()
            result = subprocess.run(
                ["python", "-m", "py_compile", "src/main.py"],
                capture_output=True,
                timeout=60
            )
            end_time = time.time()
            
            if result.returncode == 0:
                return end_time - start_time
            
        except Exception:
            pass
        
        return 0.0
    
    def _measure_test_time(self) -> float:
        """测量测试执行时间"""
        try:
            start_time = time.time()
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v"],
                capture_output=True,
                timeout=300
            )
            end_time = time.time()
            
            return end_time - start_time
            
        except Exception:
            pass
        
        return 0.0
    
    def _save_quality_metrics(self, metrics: QualityMetrics) -> None:
        """保存质量指标"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO quality_metrics (
                timestamp, total_lines, code_lines, comment_lines, blank_lines,
                cyclomatic_complexity, test_coverage, duplicate_code_ratio,
                technical_debt_ratio, maintainability_index
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metrics.timestamp.isoformat(),
            metrics.total_lines,
            metrics.code_lines,
            metrics.comment_lines,
            metrics.blank_lines,
            metrics.cyclomatic_complexity,
            metrics.test_coverage,
            metrics.duplicate_code_ratio,
            metrics.technical_debt_ratio,
            metrics.maintainability_index
        ))
        
        conn.commit()
        conn.close()
    
    def _save_performance_metrics(self, metrics: PerformanceMetrics) -> None:
        """保存性能指标"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO performance_metrics (
                timestamp, startup_time, memory_usage, cpu_usage,
                build_time, test_execution_time
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            metrics.timestamp.isoformat(),
            metrics.startup_time,
            metrics.memory_usage,
            metrics.cpu_usage,
            metrics.build_time,
            metrics.test_execution_time
        ))
        
        conn.commit()
        conn.close()
    
    def update_task_progress(self, task_id: str, status: str, progress_percent: float = None, notes: str = "") -> None:
        """更新任务进度"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取现有记录
        cursor.execute("SELECT * FROM task_progress WHERE task_id = ?", (task_id,))
        existing = cursor.fetchone()
        
        now = datetime.now().isoformat()
        
        if existing:
            # 更新现有记录
            update_fields = ["status = ?", "notes = ?", "end_time = ?"]
            update_values = [status, notes, now if status in ["completed", "failed"] else None]
            
            if progress_percent is not None:
                update_fields.append("progress_percent = ?")
                update_values.append(progress_percent)
            
            update_values.append(task_id)
            
            cursor.execute(
                f"UPDATE task_progress SET {', '.join(update_fields)} WHERE task_id = ?",
                update_values
            )
        else:
            # 创建新记录
            cursor.execute("""
                INSERT INTO task_progress (
                    task_id, status, progress_percent, start_time, notes
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                task_id,
                status,
                progress_percent or 0.0,
                now,
                notes
            ))
        
        conn.commit()
        conn.close()
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """获取进度摘要"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 任务统计
        cursor.execute("""
            SELECT status, COUNT(*), AVG(progress_percent)
            FROM task_progress
            GROUP BY status
        """)
        task_stats = {row[0]: {"count": row[1], "avg_progress": row[2]} for row in cursor.fetchall()}
        
        # 最新质量指标
        cursor.execute("""
            SELECT * FROM quality_metrics
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        latest_quality = cursor.fetchone()
        
        # 最新性能指标
        cursor.execute("""
            SELECT * FROM performance_metrics
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        latest_performance = cursor.fetchone()
        
        conn.close()
        
        return {
            "task_statistics": task_stats,
            "latest_quality_metrics": latest_quality,
            "latest_performance_metrics": latest_performance,
            "last_updated": datetime.now().isoformat()
        }
    
    def generate_trend_report(self, days: int = 30) -> str:
        """生成趋势报告"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取指定天数内的数据
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # 质量趋势
        cursor.execute("""
            SELECT timestamp, maintainability_index, test_coverage, technical_debt_ratio
            FROM quality_metrics
            WHERE timestamp >= ?
            ORDER BY timestamp
        """, (since_date,))
        quality_data = cursor.fetchall()
        
        # 性能趋势
        cursor.execute("""
            SELECT timestamp, startup_time, memory_usage, build_time
            FROM performance_metrics
            WHERE timestamp >= ?
            ORDER BY timestamp
        """, (since_date,))
        performance_data = cursor.fetchall()
        
        conn.close()
        
        # 生成报告
        report = []
        report.append("# 📈 债务清理趋势报告")
        report.append("")
        report.append(f"**报告周期**: 最近 {days} 天")
        report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        if quality_data:
            first_quality = quality_data[0]
            last_quality = quality_data[-1]
            
            report.append("## 📊 质量指标趋势")
            report.append("")
            report.append(f"- **可维护性指数**: {first_quality[1]:.1f} → {last_quality[1]:.1f} ({last_quality[1] - first_quality[1]:+.1f})")
            report.append(f"- **测试覆盖率**: {first_quality[2]:.1f}% → {last_quality[2]:.1f}% ({last_quality[2] - first_quality[2]:+.1f}%)")
            report.append(f"- **技术债务比率**: {first_quality[3]:.1f}% → {last_quality[3]:.1f}% ({last_quality[3] - first_quality[3]:+.1f}%)")
            report.append("")
        
        if performance_data:
            first_perf = performance_data[0]
            last_perf = performance_data[-1]
            
            report.append("## ⚡ 性能指标趋势")
            report.append("")
            report.append(f"- **启动时间**: {first_perf[1]:.2f}s → {last_perf[1]:.2f}s ({last_perf[1] - first_perf[1]:+.2f}s)")
            report.append(f"- **内存使用**: {first_perf[2]:.1f}MB → {last_perf[2]:.1f}MB ({last_perf[2] - first_perf[2]:+.1f}MB)")
            report.append(f"- **构建时间**: {first_perf[3]:.2f}s → {last_perf[3]:.2f}s ({last_perf[3] - first_perf[3]:+.2f}s)")
            report.append("")
        
        # 改进建议
        report.append("## 💡 改进建议")
        report.append("")
        
        if quality_data and len(quality_data) >= 2:
            latest = quality_data[-1]
            if latest[1] < 60:  # 可维护性指数低于60
                report.append("- 🔴 **可维护性指数偏低**，建议优先处理代码重构任务")
            if latest[2] < 80:  # 测试覆盖率低于80%
                report.append("- 🟡 **测试覆盖率不足**，建议增加单元测试")
            if latest[3] > 20:  # 技术债务比率高于20%
                report.append("- 🔴 **技术债务比率过高**，建议加快债务清理进度")
        
        return "\n".join(report)
    
    def set_baseline(self) -> None:
        """设置基准指标"""
        quality_metrics = self._collect_quality_metrics()
        performance_metrics = self._collect_performance_metrics()
        
        self.baseline_metrics = {
            "quality": quality_metrics,
            "performance": performance_metrics,
            "timestamp": datetime.now()
        }
        
        # 保存基准指标
        if quality_metrics:
            self._save_quality_metrics(quality_metrics)
        if performance_metrics:
            self._save_performance_metrics(performance_metrics)
    
    def export_data(self, output_path: str) -> None:
        """导出所有数据"""
        conn = sqlite3.connect(self.db_path)
        
        # 导出为JSON格式
        data = {
            "quality_metrics": [],
            "performance_metrics": [],
            "task_progress": []
        }
        
        # 质量指标
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quality_metrics ORDER BY timestamp")
        for row in cursor.fetchall():
            data["quality_metrics"].append({
                "timestamp": row[1],
                "total_lines": row[2],
                "code_lines": row[3],
                "comment_lines": row[4],
                "blank_lines": row[5],
                "cyclomatic_complexity": row[6],
                "test_coverage": row[7],
                "duplicate_code_ratio": row[8],
                "technical_debt_ratio": row[9],
                "maintainability_index": row[10]
            })
        
        # 性能指标
        cursor.execute("SELECT * FROM performance_metrics ORDER BY timestamp")
        for row in cursor.fetchall():
            data["performance_metrics"].append({
                "timestamp": row[1],
                "startup_time": row[2],
                "memory_usage": row[3],
                "cpu_usage": row[4],
                "build_time": row[5],
                "test_execution_time": row[6]
            })
        
        # 任务进度
        cursor.execute("SELECT * FROM task_progress")
        for row in cursor.fetchall():
            data["task_progress"].append({
                "task_id": row[0],
                "status": row[1],
                "progress_percent": row[2],
                "start_time": row[3],
                "end_time": row[4],
                "estimated_completion": row[5],
                "actual_hours": row[6],
                "estimated_hours": row[7],
                "notes": row[8]
            })
        
        conn.close()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 示例用法
    tracker = ProgressTracker()
    
    # 设置基准
    tracker.set_baseline()
    
    # 开始监控
    tracker.start_monitoring(interval=60)  # 每分钟收集一次
    
    # 模拟任务进度更新
    tracker.update_task_progress("task_001", "in_progress", 50.0, "开始处理硬编码导入")
    
    # 生成报告
    summary = tracker.get_progress_summary()
    print(f"进度摘要：{summary}")
    
    # 生成趋势报告
    trend_report = tracker.generate_trend_report(7)  # 最近7天
    with open("trend_report.md", "w", encoding="utf-8") as f:
        f.write(trend_report)
    
    # 导出数据
    tracker.export_data("progress_data.json")
    
    # 停止监控
    time.sleep(5)
    tracker.stop_monitoring()