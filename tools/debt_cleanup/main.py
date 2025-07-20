#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术债务清理主程序

提供命令行界面来执行技术债务分析和清理任务。
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from debt_analyzer import DebtAnalyzer
from cleanup_manager import CleanupManager
from progress_tracker import ProgressTracker


class DebtCleanupCLI:
    """债务清理命令行界面"""
    
    def __init__(self):
        self.analyzer = DebtAnalyzer(".")
        self.manager = CleanupManager(".")
        self.tracker = ProgressTracker()
    
    def analyze(self, output_format: str = "json", output_file: str = None) -> None:
        """分析技术债务"""
        print("🔍 开始分析技术债务...")
        
        # 执行分析
        results = self.analyzer.analyze_project()
        
        if not results:
            print("❌ 分析失败")
            return
        
        # 输出结果
        if output_format == "json":
            output = json.dumps(results, ensure_ascii=False, indent=2)
        else:
            output = self.analyzer.generate_markdown_report(results)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"✅ 分析报告已保存到: {output_file}")
        else:
            print(output)
    
    def plan(self, priority: str = "high", output_file: str = None) -> None:
        """生成清理计划"""
        print("📋 生成清理计划...")
        
        # 先分析债务
        debt_report = self.analyzer.analyze_project()
        if not debt_report:
            print("❌ 无法分析债务，计划生成失败")
            return
        
        # 将DebtReport转换为字典格式
        debt_results = {
            "summary": {
                "total_issues": debt_report.total_issues,
                "critical_issues": debt_report.critical_issues,
                "major_issues": debt_report.major_issues,
                "estimated_hours": debt_report.estimated_total_hours
            },
            "detailed_issues": debt_report.detailed_issues
        }
        
        # 生成计划
        plan = self.manager.create_cleanup_plan(debt_results, priority)
        
        # 输出计划
        plan_json = {
            "plan_id": plan.plan_id,
            "priority": plan.priority,
            "estimated_hours": plan.estimated_hours,
            "tasks": [
                {
                    "task_id": task.id,
                    "name": task.name,
                    "priority": task.priority,
                    "estimated_hours": task.estimated_hours,
                    "description": task.description,
                    "dependencies": task.dependencies,
                    "status": task.status
                }
                for task in plan.tasks
            ],
            "created_at": plan.created_at.isoformat()
        }
        
        output = json.dumps(plan_json, ensure_ascii=False, indent=2)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"✅ 清理计划已保存到: {output_file}")
        else:
            print(output)
    
    def execute(self, plan_file: str = None, task_ids: List[str] = None, dry_run: bool = False) -> None:
        """执行清理任务"""
        if dry_run:
            print("🧪 执行模拟运行...")
        else:
            print("🚀 开始执行清理任务...")
        
        # 加载计划
        if plan_file:
            try:
                with open(plan_file, 'r', encoding='utf-8') as f:
                    plan_data = json.load(f)
                
                # 重建计划对象
                plan = self.manager._rebuild_plan_from_data(plan_data)
                
            except Exception as e:
                print(f"❌ 加载计划文件失败: {e}")
                return
        else:
            # 生成默认计划
            debt_report = self.analyzer.analyze_project()
            if not debt_report:
                print("❌ 无法分析债务，执行失败")
                return
            
            # 将DebtReport转换为字典格式
            debt_results = {
                "summary": {
                    "total_issues": debt_report.total_issues,
                    "critical_issues": debt_report.critical_issues,
                    "major_issues": debt_report.major_issues,
                    "estimated_hours": debt_report.estimated_total_hours
                },
                "detailed_issues": debt_report.detailed_issues
            }
            
            plan = self.manager.create_cleanup_plan(debt_results)
        
        # 过滤任务
        if task_ids:
            plan.tasks = [task for task in plan.tasks if task.id in task_ids]
        
        if not plan.tasks:
            print("❌ 没有找到要执行的任务")
            return
        
        # 开始监控
        self.tracker.start_monitoring()
        
        try:
            # 执行计划
            if dry_run:
                results = self.manager.simulate_execution(plan)
                print("\n📊 模拟执行结果:")
                for task_id, result in results.items():
                    status = "✅ 成功" if result["success"] else "❌ 失败"
                    print(f"  {task_id}: {status} - {result['message']}")
            else:
                results = self.manager.execute_plan(plan)
                print("\n📊 执行结果:")
                for task_id, result in results.items():
                    status = "✅ 成功" if result["success"] else "❌ 失败"
                    print(f"  {task_id}: {status} - {result['message']}")
                    
                    # 更新进度
                    self.tracker.update_task_progress(
                        task_id,
                        "completed" if result["success"] else "failed",
                        100.0 if result["success"] else 0.0,
                        result["message"]
                    )
        
        finally:
            # 停止监控
            self.tracker.stop_monitoring()
    
    def status(self) -> None:
        """显示清理状态"""
        print("📊 获取清理状态...")
        
        # 获取进度摘要
        summary = self.tracker.get_progress_summary()
        
        print("\n📈 任务统计:")
        for status, stats in summary.get("task_statistics", {}).items():
            print(f"  {status}: {stats['count']} 个任务 (平均进度: {stats['avg_progress']:.1f}%)")
        
        # 显示最新指标
        quality = summary.get("latest_quality_metrics")
        if quality:
            print("\n📊 最新质量指标:")
            print(f"  可维护性指数: {quality[10]:.1f}")
            print(f"  测试覆盖率: {quality[7]:.1f}%")
            print(f"  技术债务比率: {quality[9]:.1f}%")
        
        performance = summary.get("latest_performance_metrics")
        if performance:
            print("\n⚡ 最新性能指标:")
            print(f"  启动时间: {performance[2]:.2f}s")
            print(f"  内存使用: {performance[3]:.1f}MB")
            print(f"  构建时间: {performance[5]:.2f}s")
    
    def report(self, days: int = 30, output_file: str = None) -> None:
        """生成趋势报告"""
        print(f"📈 生成最近 {days} 天的趋势报告...")
        
        report = self.tracker.generate_trend_report(days)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ 趋势报告已保存到: {output_file}")
        else:
            print(report)
    
    def export(self, output_file: str) -> None:
        """导出所有数据"""
        print(f"📤 导出数据到 {output_file}...")
        
        self.tracker.export_data(output_file)
        print("✅ 数据导出完成")
    
    def baseline(self) -> None:
        """设置基准指标"""
        print("📏 设置基准指标...")
        
        self.tracker.set_baseline()
        print("✅ 基准指标设置完成")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="技术债务清理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s analyze --format markdown --output debt_report.md
  %(prog)s plan --priority high --output cleanup_plan.json
  %(prog)s execute --plan cleanup_plan.json --dry-run
  %(prog)s execute --tasks task_001,task_002
  %(prog)s status
  %(prog)s report --days 7 --output trend_report.md
  %(prog)s export --output progress_data.json
  %(prog)s baseline
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="分析技术债务")
    analyze_parser.add_argument(
        "--format", 
        choices=["json", "markdown"], 
        default="json",
        help="输出格式 (默认: json)"
    )
    analyze_parser.add_argument(
        "--output", "-o",
        help="输出文件路径"
    )
    
    # plan 命令
    plan_parser = subparsers.add_parser("plan", help="生成清理计划")
    plan_parser.add_argument(
        "--priority",
        choices=["high", "medium", "low"],
        default="high",
        help="优先级过滤 (默认: high)"
    )
    plan_parser.add_argument(
        "--output", "-o",
        help="输出文件路径"
    )
    
    # execute 命令
    execute_parser = subparsers.add_parser("execute", help="执行清理任务")
    execute_parser.add_argument(
        "--plan",
        help="计划文件路径"
    )
    execute_parser.add_argument(
        "--tasks",
        help="要执行的任务ID列表 (逗号分隔)"
    )
    execute_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="模拟执行，不实际修改文件"
    )
    
    # status 命令
    subparsers.add_parser("status", help="显示清理状态")
    
    # report 命令
    report_parser = subparsers.add_parser("report", help="生成趋势报告")
    report_parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="报告天数 (默认: 30)"
    )
    report_parser.add_argument(
        "--output", "-o",
        help="输出文件路径"
    )
    
    # export 命令
    export_parser = subparsers.add_parser("export", help="导出所有数据")
    export_parser.add_argument(
        "--output", "-o",
        required=True,
        help="输出文件路径"
    )
    
    # baseline 命令
    subparsers.add_parser("baseline", help="设置基准指标")
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建CLI实例
    cli = DebtCleanupCLI()
    
    try:
        # 执行命令
        if args.command == "analyze":
            cli.analyze(args.format, args.output)
        
        elif args.command == "plan":
            cli.plan(args.priority, args.output)
        
        elif args.command == "execute":
            task_ids = args.tasks.split(",") if args.tasks else None
            cli.execute(args.plan, task_ids, args.dry_run)
        
        elif args.command == "status":
            cli.status()
        
        elif args.command == "report":
            cli.report(args.days, args.output)
        
        elif args.command == "export":
            cli.export(args.output)
        
        elif args.command == "baseline":
            cli.baseline()
        
    except KeyboardInterrupt:
        print("\n❌ 操作被用户中断")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()