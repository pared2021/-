#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
债务清理管理器

协调和执行技术债务清理任务，包括：
- 清理任务规划和调度
- 自动化重构工具
- 进度跟踪和报告
- 回滚和恢复机制
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

from debt_analyzer import DebtAnalyzer, DebtIssue, DebtReport
from progress_tracker import ProgressTracker


@dataclass
class CleanupTask:
    """清理任务"""
    id: str
    name: str
    description: str
    priority: int  # 1-10, 10最高
    estimated_hours: float
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, failed
    assigned_issues: List[DebtIssue] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: str = ""


@dataclass
class CleanupPlan:
    """清理计划"""
    plan_id: str
    name: str
    description: str
    priority: str
    tasks: List[CleanupTask]
    estimated_hours: float
    created_at: datetime
    target_completion: Optional[datetime] = None


class CleanupManager:
    """债务清理管理器"""
    
    def __init__(self, project_root: str, backup_dir: str = None):
        self.project_root = Path(project_root)
        self.backup_dir = Path(backup_dir) if backup_dir else self.project_root / ".debt_cleanup_backups"
        self.analyzer = DebtAnalyzer(project_root)
        self.tracker = ProgressTracker()
        
        # 确保备份目录存在
        self.backup_dir.mkdir(exist_ok=True)
        
        # 设置日志
        self.logger = self._setup_logger()
        
        # 预定义清理任务模板
        self.task_templates = self._load_task_templates()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("CleanupManager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler(self.project_root / "debt_cleanup.log")
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_task_templates(self) -> Dict[str, Dict]:
        """加载清理任务模板"""
        return {
            "hardcoded_imports": {
                "name": "硬编码导入清理",
                "description": "将硬编码的src导入转换为相对导入",
                "priority": 9,
                "auto_fixable": True
            },
            "service_locator_refactor": {
                "name": "服务定位器重构",
                "description": "将服务定位器模式重构为依赖注入",
                "priority": 10,
                "auto_fixable": False
            },
            "async_conversion": {
                "name": "异步化改造",
                "description": "将同步代码转换为异步代码",
                "priority": 8,
                "auto_fixable": False
            },
            "interface_extraction": {
                "name": "接口抽象提取",
                "description": "为服务类提取接口抽象",
                "priority": 7,
                "auto_fixable": False
            },
            "duplicate_code_removal": {
                "name": "重复代码消除",
                "description": "识别并消除重复代码",
                "priority": 5,
                "auto_fixable": True
            },
            "error_handling_standardization": {
                "name": "错误处理标准化",
                "description": "统一错误处理策略和异常体系",
                "priority": 6,
                "auto_fixable": False
            }
        }
    
    def create_cleanup_plan(self, debt_results: Dict, priority: str = "high") -> CleanupPlan:
        """根据债务分析结果创建清理计划"""
        self.logger.info(f"创建清理计划，优先级：{priority}")
        
        # 根据分析结果生成清理任务
        tasks = self._generate_cleanup_tasks_from_results(debt_results, priority)
        
        # 计算总预估时间
        total_hours = sum(task.estimated_hours for task in tasks)
        
        # 创建清理计划
        plan = CleanupPlan(
            plan_id=f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name="技术债务清理计划",
            description=f"基于 {debt_results.get('summary', {}).get('total_issues', 0)} 个问题的系统性清理计划",
            priority=priority,
            tasks=tasks,
            estimated_hours=total_hours,
            created_at=datetime.now()
        )
        
        self.logger.info(f"生成清理计划：{len(tasks)} 个任务，预估 {total_hours:.1f} 小时")
        return plan
    
    def _generate_cleanup_tasks_from_results(self, debt_results: Dict, priority: str) -> List[CleanupTask]:
        """根据债务分析结果生成清理任务"""
        tasks = []
        task_counter = 1
        
        # 获取问题详情
        issues = debt_results.get('detailed_issues', [])
        
        # 按问题类型分组
        issues_by_type = {}
        for issue in issues:
            issue_type = getattr(issue, 'type', 'unknown')
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
        
        # 为每种问题类型创建清理任务
        for issue_type, type_issues in issues_by_type.items():
            template = self._get_task_template(issue_type)
            if template:
                # 根据优先级过滤
                if priority == "high" and template["priority"] < 8:
                    continue
                elif priority == "medium" and template["priority"] < 5:
                    continue
                
                # 创建任务
                task = CleanupTask(
                    id=f"task_{task_counter:03d}",
                    name=f"{template['description']}",
                    description=f"{template['description']} ({len(type_issues)} 个问题)",
                    priority=template["priority"],
                    estimated_hours=len(type_issues) * 0.5,  # 每个问题预估0.5小时
                    dependencies=[],
                    assigned_issues=type_issues
                )
                tasks.append(task)
                task_counter += 1
        
        # 按优先级排序
        tasks.sort(key=lambda t: t.priority, reverse=True)
        
        return tasks
    
    def _get_task_template(self, issue_type: str) -> Dict:
        """获取问题类型对应的任务模板"""
        templates = {
            "hardcoded_import": {
                "description": "修复硬编码导入",
                "priority": 9,
                "automation_level": "high"
            },
            "service_locator_antipattern": {
                "description": "重构服务定位器反模式",
                "priority": 8,
                "automation_level": "medium"
            },
            "god_class": {
                "description": "拆分上帝类",
                "priority": 7,
                "automation_level": "low"
            },
            "long_method": {
                "description": "重构长方法",
                "priority": 6,
                "automation_level": "medium"
            },
            "code_duplication": {
                "description": "消除代码重复",
                "priority": 5,
                "automation_level": "medium"
            }
        }
        return templates.get(issue_type)
    
    def analyze_and_plan(self) -> CleanupPlan:
        """分析项目并生成清理计划"""
        self.logger.info("开始分析项目技术债务...")
        
        # 分析技术债务
        debt_report = self.analyzer.analyze_project()
        
        # 根据分析结果生成清理任务
        tasks = self._generate_cleanup_tasks(debt_report)
        
        # 计算总预估时间
        total_hours = sum(task.estimated_hours for task in tasks)
        
        # 创建清理计划
        plan = CleanupPlan(
            plan_id=f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name="技术债务清理计划",
            description=f"基于 {debt_report.total_issues} 个问题的系统性清理计划",
            priority="medium",
            tasks=tasks,
            estimated_hours=total_hours,
            created_at=datetime.now()
        )
        
        self.logger.info(f"生成清理计划：{len(tasks)} 个任务，预估 {total_hours:.1f} 小时")
        return plan
    
    def _generate_cleanup_tasks(self, debt_report: DebtReport) -> List[CleanupTask]:
        """根据债务报告生成清理任务"""
        tasks = []
        task_counter = 1
        
        # 按问题类型分组
        issues_by_type = {}
        for issue in debt_report.detailed_issues:
            if issue.type not in issues_by_type:
                issues_by_type[issue.type] = []
            issues_by_type[issue.type].append(issue)
        
        # 为每种问题类型创建清理任务
        for issue_type, issues in issues_by_type.items():
            template = self._get_task_template(issue_type)
            if template:
                task = CleanupTask(
                    id=f"task_{task_counter:03d}",
                    name=template["name"],
                    description=f"{template['description']} ({len(issues)} 个问题)",
                    priority=template["priority"],
                    estimated_hours=sum(issue.estimated_hours for issue in issues),
                    assigned_issues=issues
                )
                tasks.append(task)
                task_counter += 1
        
        # 按优先级排序
        tasks.sort(key=lambda t: t.priority, reverse=True)
        
        # 设置依赖关系
        self._set_task_dependencies(tasks)
        
        return tasks
    
    def _get_task_template(self, issue_type: str) -> Optional[Dict]:
        """获取问题类型对应的任务模板"""
        # 映射问题类型到任务模板
        type_mapping = {
            "hardcoded_import": "hardcoded_imports",
            "service_locator_antipattern": "service_locator_refactor",
            "god_class": "interface_extraction",
            "long_method": "duplicate_code_removal"
        }
        
        template_key = type_mapping.get(issue_type)
        return self.task_templates.get(template_key) if template_key else None
    
    def _set_task_dependencies(self, tasks: List[CleanupTask]) -> None:
        """设置任务依赖关系"""
        # 简单的依赖规则：高优先级任务先执行
        for i, task in enumerate(tasks):
            if i > 0 and task.priority < tasks[i-1].priority:
                task.dependencies.append(tasks[i-1].id)
    
    def execute_plan(self, plan: CleanupPlan, auto_mode: bool = False) -> Dict[str, Dict[str, Any]]:
        """执行清理计划"""
        self.logger.info(f"开始执行清理计划：{plan.name}")
        results = {}
        
        # 创建备份
        backup_path = self._create_backup()
        self.logger.info(f"创建备份：{backup_path}")
        
        try:
            for task in plan.tasks:
                if not self._can_execute_task(task, plan.tasks):
                    self.logger.warning(f"任务 {task.id} 依赖未满足，跳过")
                    results[task.id] = {
                        "success": False,
                        "message": "依赖未满足"
                    }
                    continue
                
                success = self._execute_task(task, auto_mode)
                results[task.id] = {
                    "success": success,
                    "message": "执行成功" if success else "执行失败"
                }
                
                if not success:
                    self.logger.error(f"任务 {task.id} 执行失败")
                    if not auto_mode:
                        user_choice = input("是否继续执行其他任务？(y/n): ")
                        if user_choice.lower() != 'y':
                            break
                
                # 更新进度
                self.tracker.update_task_progress(task.id, task.status)
            
            self.logger.info("清理计划执行完成")
            return results
            
        except Exception as e:
            self.logger.error(f"执行清理计划时发生错误：{e}")
            if not auto_mode:
                restore_choice = input("是否恢复备份？(y/n): ")
                if restore_choice.lower() == 'y':
                    self._restore_backup(backup_path)
            for task in plan.tasks:
                if task.id not in results:
                    results[task.id] = {
                        "success": False,
                        "message": f"执行异常：{str(e)}"
                    }
            return results
    
    def simulate_execution(self, plan: CleanupPlan) -> Dict[str, Dict[str, Any]]:
        """模拟执行清理计划"""
        self.logger.info(f"模拟执行清理计划：{plan.name}")
        results = {}
        
        for task in plan.tasks:
            if not self._can_execute_task(task, plan.tasks):
                results[task.id] = {
                    "success": False,
                    "message": "依赖未满足"
                }
                continue
            
            # 模拟执行逻辑
            if "硬编码导入" in task.name:
                results[task.id] = {
                    "success": True,
                    "message": f"将修复 {len(task.assigned_issues)} 个硬编码导入问题"
                }
            elif "服务定位器" in task.name:
                results[task.id] = {
                    "success": True,
                    "message": f"将重构 {len(task.assigned_issues)} 个服务定位器反模式"
                }
            else:
                results[task.id] = {
                    "success": True,
                    "message": f"将处理 {len(task.assigned_issues)} 个问题"
                }
        
        return results
    
    def _can_execute_task(self, task: CleanupTask, all_tasks: List[CleanupTask]) -> bool:
        """检查任务是否可以执行（依赖是否满足）"""
        if not task.dependencies:
            return True
        
        task_dict = {t.id: t for t in all_tasks}
        for dep_id in task.dependencies:
            if dep_id in task_dict and task_dict[dep_id].status != "completed":
                return False
        
        return True
    
    def _execute_task(self, task: CleanupTask, auto_mode: bool) -> bool:
        """执行单个清理任务"""
        self.logger.info(f"执行任务：{task.name}")
        task.status = "in_progress"
        task.start_time = datetime.now()
        
        try:
            # 根据任务类型执行相应的清理操作
            if "硬编码导入" in task.name:
                success = self._fix_hardcoded_imports(task)
            elif "重复代码" in task.name:
                success = self._remove_duplicate_code(task)
            else:
                # 对于复杂任务，需要手动处理
                success = self._handle_manual_task(task, auto_mode)
            
            task.status = "completed" if success else "failed"
            task.end_time = datetime.now()
            
            return success
            
        except Exception as e:
            self.logger.error(f"任务执行失败：{e}")
            task.status = "failed"
            task.end_time = datetime.now()
            task.notes = str(e)
            return False
    
    def _fix_hardcoded_imports(self, task: CleanupTask) -> bool:
        """修复硬编码导入"""
        fixed_count = 0
        
        for issue in task.assigned_issues:
            if issue.type == "hardcoded_import":
                success = self._fix_single_import(issue)
                if success:
                    fixed_count += 1
        
        self.logger.info(f"修复了 {fixed_count}/{len(task.assigned_issues)} 个硬编码导入")
        return fixed_count > 0
    
    def _fix_single_import(self, issue: DebtIssue) -> bool:
        """修复单个硬编码导入"""
        try:
            file_path = Path(issue.file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 修复导入语句
            line_index = issue.line_number - 1
            original_line = lines[line_index]
            fixed_line = self._convert_import_to_relative(original_line, file_path)
            
            if fixed_line != original_line:
                lines[line_index] = fixed_line
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                self.logger.info(f"修复导入：{file_path}:{issue.line_number}")
                return True
            
        except Exception as e:
            self.logger.error(f"修复导入失败：{e}")
        
        return False
    
    def _convert_import_to_relative(self, import_line: str, file_path: Path) -> str:
        """将硬编码导入转换为相对导入"""
        # 简单的转换逻辑，实际实现需要更复杂的路径计算
        if "from src." in import_line:
            # 计算相对路径
            src_path = self.project_root / "src"
            current_dir = file_path.parent
            relative_path = os.path.relpath(src_path, current_dir)
            
            # 替换导入路径
            import_line = import_line.replace("from src.", f"from {relative_path}.")
            import_line = import_line.replace("/", ".")
        
        return import_line
    
    def _remove_duplicate_code(self, task: CleanupTask) -> bool:
        """移除重复代码（简化实现）"""
        # 这里只是示例，实际需要复杂的代码相似性分析
        self.logger.info("重复代码移除需要手动处理")
        return False
    
    def _handle_manual_task(self, task: CleanupTask, auto_mode: bool) -> bool:
        """处理需要手动操作的任务"""
        if auto_mode:
            self.logger.warning(f"任务 {task.name} 需要手动处理，自动模式下跳过")
            return False
        
        print(f"\n任务：{task.name}")
        print(f"描述：{task.description}")
        print(f"相关问题数：{len(task.assigned_issues)}")
        
        # 显示相关问题
        for i, issue in enumerate(task.assigned_issues[:5], 1):
            print(f"  {i}. {issue.file_path}:{issue.line_number} - {issue.description}")
        
        if len(task.assigned_issues) > 5:
            print(f"  ... 还有 {len(task.assigned_issues) - 5} 个问题")
        
        choice = input("\n请选择操作：(s)跳过 (c)标记完成 (f)标记失败: ")
        
        if choice.lower() == 'c':
            return True
        elif choice.lower() == 'f':
            return False
        else:
            task.status = "pending"
            return False
    
    def _create_backup(self) -> Path:
        """创建项目备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        
        # 只备份src目录
        src_backup = backup_path / "src"
        shutil.copytree(self.project_root / "src", src_backup)
        
        return backup_path
    
    def _restore_backup(self, backup_path: Path) -> None:
        """恢复备份"""
        if backup_path.exists():
            # 删除当前src目录
            shutil.rmtree(self.project_root / "src")
            # 恢复备份
            shutil.copytree(backup_path / "src", self.project_root / "src")
            self.logger.info(f"已恢复备份：{backup_path}")
    
    def generate_progress_report(self, plan: CleanupPlan) -> str:
        """生成进度报告"""
        completed_tasks = [t for t in plan.tasks if t.status == "completed"]
        failed_tasks = [t for t in plan.tasks if t.status == "failed"]
        pending_tasks = [t for t in plan.tasks if t.status == "pending"]
        
        completed_hours = sum(t.estimated_hours for t in completed_tasks)
        total_hours = plan.total_estimated_hours
        
        progress_percent = (completed_hours / total_hours * 100) if total_hours > 0 else 0
        
        report = []
        report.append("# 🚀 债务清理进度报告")
        report.append("")
        report.append(f"**计划名称**: {plan.name}")
        report.append(f"**创建时间**: {plan.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**总体进度**: {progress_percent:.1f}% ({completed_hours:.1f}/{total_hours:.1f} 小时)")
        report.append("")
        
        report.append("## 📊 任务统计")
        report.append("")
        report.append(f"- ✅ **已完成**: {len(completed_tasks)}")
        report.append(f"- ❌ **失败**: {len(failed_tasks)}")
        report.append(f"- ⏳ **待处理**: {len(pending_tasks)}")
        report.append("")
        
        if completed_tasks:
            report.append("## ✅ 已完成任务")
            report.append("")
            for task in completed_tasks:
                duration = ""
                if task.start_time and task.end_time:
                    duration = f" (耗时: {(task.end_time - task.start_time).total_seconds() / 3600:.1f}h)"
                report.append(f"- **{task.name}**{duration}")
            report.append("")
        
        if failed_tasks:
            report.append("## ❌ 失败任务")
            report.append("")
            for task in failed_tasks:
                report.append(f"- **{task.name}**: {task.notes}")
            report.append("")
        
        return "\n".join(report)
    
    def load_plan(self, file_path: str) -> CleanupPlan:
        """从文件加载清理计划"""
        with open(file_path, 'r', encoding='utf-8') as f:
            plan_data = json.load(f)
        
        return self._rebuild_plan_from_data(plan_data)
    
    def _rebuild_plan_from_data(self, plan_data: dict) -> CleanupPlan:
        """从字典数据重建CleanupPlan对象"""
        tasks = []
        for task_data in plan_data.get('tasks', []):
            task = CleanupTask(
                id=task_data['task_id'],
                name=task_data['name'],
                description=task_data['description'],
                priority=task_data['priority'],
                estimated_hours=task_data['estimated_hours'],
                dependencies=task_data.get('dependencies', []),
                status=task_data.get('status', 'pending'),
                assigned_issues=[]
            )
            if task_data.get('start_time'):
                task.start_time = datetime.fromisoformat(task_data['start_time'])
            if task_data.get('end_time'):
                task.end_time = datetime.fromisoformat(task_data['end_time'])
            task.notes = task_data.get('notes', '')
            tasks.append(task)
        
        return CleanupPlan(
            plan_id=plan_data.get('plan_id', f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            name=plan_data.get('name', '技术债务清理计划'),
            description=plan_data.get('description', '自动生成的清理计划'),
            priority=plan_data.get('priority', 'medium'),
            tasks=tasks,
            estimated_hours=plan_data.get('estimated_hours', 0),
            created_at=datetime.fromisoformat(plan_data['created_at']) if isinstance(plan_data['created_at'], str) else datetime.now(),
            target_completion=datetime.fromisoformat(plan_data['target_completion']) if plan_data.get('target_completion') else None
        )
    
    def save_plan(self, plan: CleanupPlan, file_path: str) -> None:
        """保存清理计划到文件"""
        plan_data = {
            "name": plan.name,
            "description": plan.description,
            "total_estimated_hours": plan.total_estimated_hours,
            "created_at": plan.created_at.isoformat(),
            "target_completion": plan.target_completion.isoformat() if plan.target_completion else None,
            "tasks": [
                {
                    "id": task.id,
                    "name": task.name,
                    "description": task.description,
                    "priority": task.priority,
                    "estimated_hours": task.estimated_hours,
                    "dependencies": task.dependencies,
                    "status": task.status,
                    "start_time": task.start_time.isoformat() if task.start_time else None,
                    "end_time": task.end_time.isoformat() if task.end_time else None,
                    "notes": task.notes,
                    "assigned_issues_count": len(task.assigned_issues)
                }
                for task in plan.tasks
            ]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(plan_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 示例用法
    manager = CleanupManager(".")
    
    # 分析并生成计划
    plan = manager.analyze_and_plan()
    
    # 保存计划
    manager.save_plan(plan, "cleanup_plan.json")
    
    # 生成进度报告
    report = manager.generate_progress_report(plan)
    with open("cleanup_progress.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"生成清理计划：{len(plan.tasks)} 个任务")