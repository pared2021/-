"""
任务系统
负责任务调度和执行
"""
import heapq
import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from .resource_manager import ResourceManager


class TaskStatus(Enum):
    """任务状态"""

    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 正在执行
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 执行失败
    SUSPENDED = "suspended"  # 已暂停


class TaskPriority(Enum):
    """任务优先级"""

    CRITICAL = 0  # 紧急任务
    HIGH = 1  # 高优先级
    NORMAL = 2  # 普通优先级
    LOW = 3  # 低优先级
    BACKGROUND = 4  # 后台任务


@dataclass
class TaskCondition:
    """任务条件"""

    type: str
    params: Dict[str, Any]

    def check(self, context: Dict[str, Any]) -> bool:
        """检查条件是否满足"""
        if self.type == "resource":
            # 检查资源条件
            required = self.params.get("required_resources", {})
            available = context.get("resources", {})

            for resource, amount in required.items():
                if resource not in available or available[resource] < amount:
                    return False
            return True

        elif self.type == "time":
            # 检查时间条件
            current_time = datetime.now()
            start_time = self.params.get("start_time")
            end_time = self.params.get("end_time")

            if start_time and current_time < datetime.fromisoformat(start_time):
                return False
            if end_time and current_time > datetime.fromisoformat(end_time):
                return False
            return True

        elif self.type == "dependency":
            # 检查任务依赖
            required_tasks = self.params.get("required_tasks", [])
            completed_tasks = context.get("completed_tasks", set())
            return all(task in completed_tasks for task in required_tasks)

        return False


@dataclass
class Task:
    """任务定义"""

    id: str
    name: str
    priority: TaskPriority
    handler: Callable
    conditions: List[TaskCondition]
    retry_limit: int = 3
    retry_count: int = 0
    status: TaskStatus = TaskStatus.PENDING
    create_time: float = 0.0
    start_time: float = 0.0
    end_time: float = 0.0
    result: Any = None
    error: Optional[Exception] = None

    def __post_init__(self):
        if not self.create_time:
            self.create_time = time.time()

    def __lt__(self, other):
        # 用于优先级队列的比较
        return (self.priority.value, self.create_time) < (
            other.priority.value,
            other.create_time,
        )


class TaskScheduler:
    def __init__(self, resource_manager: ResourceManager):
        self.resource_manager = resource_manager
        self.logger = logging.getLogger("TaskScheduler")
        self.tasks: List[Task] = []  # 优先级队列
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.failed_tasks: Dict[str, Task] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self.context: Dict[str, Any] = {}
        self.lock = threading.Lock()
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None

    def register_handler(self, task_type: str, handler: Callable) -> None:
        """注册任务处理器"""
        self.task_handlers[task_type] = handler

    def add_task(self, task: Task) -> None:
        """添加任务"""
        with self.lock:
            heapq.heappush(self.tasks, task)

    def start(self) -> None:
        """启动任务调度器"""
        if self.running:
            return

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

    def stop(self) -> None:
        """停止任务调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()

    def _scheduler_loop(self) -> None:
        """调度循环"""
        while self.running:
            try:
                # 更新上下文
                self._update_context()

                # 检查并执行任务
                self._check_and_execute_tasks()

                # 检查运行中的任务
                self._check_running_tasks()

                # 清理已完成的任务
                self._cleanup_tasks()

                time.sleep(0.1)  # 避免过度消耗CPU

            except Exception as e:
                self.logger.error(f"任务调度失败: {e}")

    def _update_context(self) -> None:
        """更新上下文"""
        # 更新资源信息
        self.context["resources"] = self.resource_manager.get_resource_stats()

        # 更新已完成任务集合
        self.context["completed_tasks"] = set(self.completed_tasks.keys())

        # 更新时间信息
        self.context["current_time"] = datetime.now().isoformat()

    def _check_and_execute_tasks(self) -> None:
        """检查并执行任务"""
        with self.lock:
            if not self.tasks:
                return

            # 获取但不移除任务
            task = self.tasks[0]

            # 检查条件
            if all(condition.check(self.context) for condition in task.conditions):
                # 移除任务并执行
                heapq.heappop(self.tasks)
                self._execute_task(task)

    def _execute_task(self, task: Task) -> None:
        """执行任务"""
        try:
            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.start_time = time.time()
            self.running_tasks[task.id] = task

            # 在新线程中执行任务
            thread = threading.Thread(target=self._task_worker, args=(task,))
            thread.daemon = True
            thread.start()

        except Exception as e:
            self._handle_task_failure(task, e)

    def _task_worker(self, task: Task) -> None:
        """任务工作器"""
        try:
            # 执行任务
            result = task.handler()

            # 更新任务状态
            with self.lock:
                task.status = TaskStatus.COMPLETED
                task.end_time = time.time()
                task.result = result
                self.completed_tasks[task.id] = task
                del self.running_tasks[task.id]

        except Exception as e:
            self._handle_task_failure(task, e)

    def _handle_task_failure(self, task: Task, error: Exception) -> None:
        """处理任务失败"""
        with self.lock:
            task.error = error
            task.retry_count += 1

            if task.retry_count < task.retry_limit:
                # 重试任务
                task.status = TaskStatus.PENDING
                heapq.heappush(self.tasks, task)
                self.logger.warning(f"任务 {task.name} 失败，准备第 {task.retry_count} 次重试")
            else:
                # 标记为失败
                task.status = TaskStatus.FAILED
                task.end_time = time.time()
                self.failed_tasks[task.id] = task
                self.logger.error(f"任务 {task.name} 失败，已达到重试上限")

            if task.id in self.running_tasks:
                del self.running_tasks[task.id]

    def _check_running_tasks(self) -> None:
        """检查运行中的任务"""
        current_time = time.time()
        with self.lock:
            for task_id, task in list(self.running_tasks.items()):
                # 检查任务是否超时
                if current_time - task.start_time > 3600:  # 1小时超时
                    self._handle_task_failure(
                        task, TimeoutError(f"任务 {task.name} 执行超时")
                    )

    def _cleanup_tasks(self) -> None:
        """清理任务"""
        current_time = time.time()
        with self.lock:
            # 清理过期的已完成任务
            for task_id, task in list(self.completed_tasks.items()):
                if current_time - task.end_time > 86400:  # 24小时后清理
                    del self.completed_tasks[task_id]

            # 清理过期的失败任务
            for task_id, task in list(self.failed_tasks.items()):
                if current_time - task.end_time > 86400:  # 24小时后清理
                    del self.failed_tasks[task_id]

    def get_task_status(self, task_id: str) -> Optional[Task]:
        """获取任务状态"""
        # 按顺序检查各个任务列表
        if task_id in self.running_tasks:
            return self.running_tasks[task_id]
        elif task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
        elif task_id in self.failed_tasks:
            return self.failed_tasks[task_id]

        # 检查待执行任务队列
        with self.lock:
            for task in self.tasks:
                if task.id == task_id:
                    return task

        return None

    def suspend_task(self, task_id: str) -> bool:
        """暂停任务"""
        task = self.get_task_status(task_id)
        if not task:
            return False

        with self.lock:
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.SUSPENDED
                return True

        return False

    def resume_task(self, task_id: str) -> bool:
        """恢复任务"""
        task = self.get_task_status(task_id)
        if not task:
            return False

        with self.lock:
            if task.status == TaskStatus.SUSPENDED:
                task.status = TaskStatus.PENDING
                heapq.heappush(self.tasks, task)
                return True

        return False
