#!/usr/bin/env python3
"""
MCP工具桥接器

功能：
1. 管理需要MCP工具的任务队列
2. 提供任务状态查询
3. 支持手动触发任务处理

MCP工具说明：
- web_reader: 需要在Claude Code上下文中调用
- 此模块提供队列机制，将URL放入队列供后续处理

作者：大秘书系统
版本：v1.0
创建时间：2026-02-12
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class MCPBridge:
    """MCP工具桥接器 - 管理需要MCP工具的任务队列"""

    def __init__(self, queue_dir=None):
        """
        初始化桥接器

        Args:
            queue_dir: 队列目录
        """
        if queue_dir is None:
            queue_dir = Path(__file__).parent.parent / "data" / "mcp_queue"
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)

        # 任务状态文件
        self.status_file = self.queue_dir / "processing_status.json"

        logger.info(f"MCPBridge initialized: {self.queue_dir}")

    def add_task(self, task_type, url, metadata=None):
        """
        添加任务到队列

        Args:
            task_type: 任务类型 (wechat_article, web_reader, etc.)
            url: 目标URL
            metadata: 附加元数据

        Returns:
            dict: 添加结果
        """
        timestamp = datetime.now().isoformat()
        task = {
            'type': task_type,
            'url': url,
            'timestamp': timestamp,
            'status': 'queued',
            'metadata': metadata or {}
        }

        # 按日期组织队列文件
        date_str = datetime.now().strftime('%Y%m%d')
        queue_file = self.queue_dir / f"queue_{date_str}.jsonl"

        with open(queue_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(task, ensure_ascii=False) + '\n')

        logger.info(f"Task added to queue: {task_type} - {url[:80]}")

        return {
            'success': True,
            'task_id': f"{date_str}_{len(list(self.get_tasks()))}",
            'queue_file': str(queue_file)
        }

    def get_tasks(self, task_type=None, status=None):
        """
        获取队列中的任务

        Args:
            task_type: 筛选任务类型（None表示全部）
            status: 筛选状态（None表示全部）

        Returns:
            list: 任务列表
        """
        tasks = self._load_all_tasks()

        # 筛选
        if task_type:
            tasks = [t for t in tasks if t.get('type') == task_type]
        if status:
            tasks = [t for t in tasks if t.get('status') == status]

        return tasks

    def _load_all_tasks(self):
        """
        从所有队列文件加载任务

        Returns:
            list: 所有任务
        """
        tasks = []
        for queue_file in sorted(self.queue_dir.glob('queue_*.jsonl'), reverse=True):
            try:
                with open(queue_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                task = json.loads(line)
                                tasks.append(task)
                            except json.JSONDecodeError:
                                logger.warning(f"Invalid JSON: {line[:100]}")
            except Exception as e:
                logger.error(f"Error reading queue {queue_file.name}: {e}")

        return tasks

    def update_task_status(self, task_id, status, result=None):
        """
        更新任务状态

        Args:
            task_id: 任务ID
            status: 新状态 (processing, completed, failed)
            result: 处理结果

        Returns:
            dict: 更新结果
        """
        # 加载所有任务
        tasks = self._load_all_tasks()

        # 查找并更新任务
        updated = False
        for task in tasks:
            if task.get('task_id') == task_id or task.get('id') == task_id:
                task['status'] = status
                task['updated_at'] = datetime.now().isoformat()
                if result is not None:
                    task['result'] = result
                updated = True
                break

        if updated:
            # 保存更新后的状态
            self._save_status(tasks)
            return {'success': True, 'task_id': task_id, 'status': status}
        else:
            return {'success': False, 'error': 'Task not found'}

    def _save_status(self, tasks):
        """
        保存任务状态到文件
        """
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)

    def clear_completed(self):
        """
        清除已完成的任务

        Returns:
            dict: 清除结果
        """
        tasks = self.get_tasks()
        before_count = len(tasks)

        # 保留未完成的任务
        incomplete_tasks = [t for t in tasks if t.get('status') != 'completed']

        # 更新队列文件（只保留未完成的）
        date_str = datetime.now().strftime('%Y%m%d')
        queue_file = self.queue_dir / f"queue_{date_str}.jsonl"

        if incomplete_tasks:
            with open(queue_file, 'w', encoding='utf-8') as f:
                for task in incomplete_tasks:
                    f.write(json.dumps(task, ensure_ascii=False) + '\n')

        # 删除旧的队列文件
        for qf in self.queue_dir.glob('queue_*.jsonl'):
            if qf != queue_file:
                try:
                    qf.unlink()
                except:
                    pass

        after_count = len(incomplete_tasks)

        logger.info(f"Cleared {before_count - after_count} completed tasks")

        return {
            'success': True,
            'cleared': before_count - after_count,
            'remaining': after_count
        }

    def get_status_summary(self):
        """
        获取队列状态摘要

        Returns:
            dict: 状态摘要
        """
        tasks = self.get_tasks()

        # 按类型和状态统计
        by_type = {}
        by_status = {}

        for task in tasks:
            task_type = task.get('type', 'unknown')
            status = task.get('status', 'unknown')

            by_type[task_type] = by_type.get(task_type, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1

        return {
            'total': len(tasks),
            'by_type': by_type,
            'by_status': by_status,
            'queue_dir': str(self.queue_dir)
        }


# 便捷函数
def create_bridge(queue_dir=None):
    """创建MCPBridge实例"""
    return MCPBridge(queue_dir)


# 命令行接口
if __name__ == '__main__':
    import sys

    bridge = MCPBridge()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python mcp_bridge.py add <type> <url>      # Add task to queue")
        print("  python mcp_bridge.py list [type]            # List tasks (optional filter by type)")
        print("  python mcp_bridge.py status                  # Get status summary")
        print("  python mcp_bridge.py clear                  # Clear completed tasks")
        print()
        print("Examples:")
        print("  python mcp_bridge.py add wechat_article https://mp.weixin.qq.com/s/xxx")
        print("  python mcp_bridge.py list wechat_article")
        print("  python mcp_bridge.py status")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'add':
        if len(sys.argv) < 4:
            print("Error: add command requires <type> and <url>")
            sys.exit(1)
        task_type = sys.argv[2]
        url = sys.argv[3]
        result = bridge.add_task(task_type, url)
        print(f"Added: {result}")

    elif command == 'list':
        task_type = sys.argv[2] if len(sys.argv) > 2 else None
        tasks = bridge.get_tasks(task_type)
        print(f"Tasks ({task_type or 'all'}): {len(tasks)}")
        for task in tasks[:20]:
            print(f"  [{task.get('status', 'queued')}] {task.get('url', 'N/A')[:80]}")

    elif command == 'status':
        summary = bridge.get_status_summary()
        print(f"Queue Status:")
        print(f"Total: {summary['total']}")
        print(f"\nBy Type:")
        for task_type, count in summary['by_type'].items():
            print(f"  {task_type}: {count}")
        print(f"\nBy Status:")
        for status, count in summary['by_status'].items():
            print(f"  {status}: {count}")

    elif command == 'clear':
        result = bridge.clear_completed()
        print(f"Cleared {result['cleared']} completed tasks, {result['remaining']} remaining")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
