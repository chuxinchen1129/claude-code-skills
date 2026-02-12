#!/usr/bin/env python3
"""
微信文章处理器

功能：
1. 使用web_reader MCP工具将微信文章转换为Markdown
2. 提取文章元数据（标题、作者、日期等）
3. 保存到对标参考文件夹

作者：大秘书系统
版本：v1.0
创建时间：2026-02-12

注意：MCP工具需要在Claude Code上下文中调用
此模块提供任务队列机制，将URL放入队列，稍后处理
"""

import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class WeChatProcessor:
    """微信文章处理器 - 将微信文章URL转换为Markdown并组织"""

    def __init__(self, material_base_path=None, queue_dir=None):
        """
        初始化处理器

        Args:
            material_base_path: 材料存储基础路径
            queue_dir: MCP任务队列目录
        """
        if material_base_path is None:
            material_base_path = Path.home() / "Desktop" / "DaMiShuSystem-main-backup" / "工作空间" / "对标参考"
        self.material_base = Path(material_base_path)

        # 队列目录
        if queue_dir is None:
            queue_dir = Path(__file__).parent.parent / "data" / "mcp_queue"
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)

        # 微信文章输出目录
        self.output_dir = self.material_base / "微信文章"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"WeChatProcessor initialized: {self.material_base}")

    def queue_wechat_task(self, url, metadata=None):
        """
        将微信文章URL放入任务队列

        Args:
            url: 微信文章URL
            metadata: 附加元数据

        Returns:
            dict: 队列结果
        """
        timestamp = datetime.now().isoformat()
        task = {
            'type': 'wechat_article',
            'url': url,
            'timestamp': timestamp,
            'metadata': metadata or {}
        }

        # 生成任务文件名（按时间）
        time_str = datetime.now().strftime('%Y%m%d')
        queue_file = self.queue_dir / f"queue_{time_str}.jsonl"

        # 追加到队列文件
        with open(queue_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(task, ensure_ascii=False) + '\n')

        logger.info(f"WeChat article queued: {url[:80]}... -> {queue_file.name}")

        return {
            'success': True,
            'queued': True,
            'queue_file': str(queue_file),
            'task': task
        }

    def process_queue(self):
        """
        获取队列中的所有任务

        Returns:
            list: 任务列表
        """
        tasks = []

        # 读取所有队列文件
        for queue_file in sorted(self.queue_dir.glob('queue_*.jsonl'), reverse=True):
            try:
                with open(queue_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                tasks.append(json.loads(line))
                            except json.JSONDecodeError:
                                logger.warning(f"Invalid JSON in queue: {line[:100]}")
            except Exception as e:
                logger.error(f"Error reading queue file {queue_file.name}: {e}")

        logger.info(f"Found {len(tasks)} tasks in queue")
        return tasks

    def clear_queue(self, queue_file=None):
        """
        清空队列文件

        Args:
            queue_file: 队列文件路径（如果为None则清空所有）
        """
        if queue_file:
            try:
                queue_file.unlink()
                logger.info(f"Cleared queue file: {queue_file.name}")
            except Exception as e:
                logger.error(f"Error clearing queue {queue_file.name}: {e}")
        else:
            # 清空所有队列文件
            for qf in self.queue_dir.glob('queue_*.jsonl'):
                try:
                    qf.unlink()
                except Exception as e:
                    logger.error(f"Error clearing queue {qf.name}: {e}")

    def extract_article_metadata(self, url, html_content=None):
        """
        从URL或HTML内容提取文章元数据

        Args:
            url: 文章URL
            html_content: HTML内容（如果有）

        Returns:
            dict: 提取的元数据
        """
        metadata = {
            'url': url,
            'original_url': url,
            'type': 'wechat_article'
        }

        if html_content:
            # 从HTML提取元数据
            # 尝试提取标题
            title_match = re.search(r'<title>([^<]+)</title>', html_content, re.IGNORECASE)
            if title_match:
                metadata['title'] = title_match.group(1).strip()

            # 尝试提取作者（微信文章通常在 meta 标签中）
            author_match = re.search(r'<meta[^>]*name=["\']author["\'][^>]*content=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
            if author_match:
                metadata['author'] = author_match.group(1)

            # 尝试提取发布时间
            date_match = re.search(r'<meta[^>]*name=["\']article:published_time["\'][^>]*content=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
            if date_match:
                metadata['date'] = date_match.group(1)

        return metadata

    def save_markdown_direct(self, url, markdown_content, metadata=None):
        """
        直接保存Markdown内容（绕过MCP，用于已获取的内容）

        Args:
            url: 文章URL
            markdown_content: Markdown内容
            metadata: 元数据

        Returns:
            dict: 保存结果
        """
        if metadata is None:
            metadata = self.extract_article_metadata(url)

        # 生成文件夹名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        title_clean = re.sub(r'[<>:"/\\|?*]', '_', metadata.get('title', '未命名'))[:30]
        folder_name = f"{timestamp}_{title_clean}"
        folder_path = self.output_dir / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        # 保存元数据
        metadata_file = folder_path / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # 保存Markdown文章
        article_file = folder_path / "article.md"
        with open(article_file, 'w', encoding='utf-8') as f:
            # 添加YAML front matter
            f.write("---\n")
            f.write(f"title: {metadata.get('title', '')}\n")
            f.write(f"author: {metadata.get('author', '')}\n")
            f.write(f"date: {metadata.get('date', '')}\n")
            f.write(f"url: {url}\n")
            f.write("---\n\n")
            # 写入正文内容
            f.write(markdown_content)

        logger.info(f"WeChat article saved: {folder_path}")

        return {
            'success': True,
            'folder_path': str(folder_path),
            'folder_name': folder_name,
            'article_file': str(article_file),
            'metadata': metadata
        }

    def get_queue_summary(self):
        """
        获取队列摘要

        Returns:
            dict: 队列摘要
        """
        tasks = self.process_queue()
        return {
            'total': len(tasks),
            'tasks': tasks[:10],  # 只返回前10个
            'queue_file': str(self.queue_dir)
        }


# 便捷函数
def create_processor(material_base_path=None, queue_dir=None):
    """创建WeChatProcessor实例"""
    return WeChatProcessor(material_base_path, queue_dir)


if __name__ == '__main__':
    import sys

    processor = WeChatProcessor()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python wechat_processor.py queue <url>      # Add URL to queue")
        print("  python wechat_processor.py list               # List queued tasks")
        print("  python wechat_processor.py clear             # Clear queue")
        sys.exit(1)

    command = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else None

    if command == 'queue' and url:
        result = processor.queue_wechat_task(url)
        print(f"Queued: {result}")

    elif command == 'list':
        summary = processor.get_queue_summary()
        print(f"Queue Summary:")
        print(f"Total tasks: {summary['total']}")
        for task in summary['tasks']:
            print(f"  - {task['url'][:80]}")

    elif command == 'clear':
        processor.clear_queue()
        print("Queue cleared")
