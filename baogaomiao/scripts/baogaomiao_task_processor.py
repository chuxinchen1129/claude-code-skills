#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
baogaomiao 任务处理器

负责处理从bot_server创建的任务文件，自动完成PDF→XHS笔记→飞书的完整流程。

功能：
1. 检测新的pending任务文件
2. 读取PDF内容
3. 生成小红书笔记（3步输出）
4. 发送到飞书（使用feishu_sender.py）
5. 更新任务状态为completed
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# 添加baogaomiao scripts目录到路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# 导入baogaomiao组件
from pdf_extractor import PDFExtractor
from feishu_sender import FeishuSender, format_xhs_note

# 配置
TASK_DIR = Path.home() / ".claude" / "skills" / "feishu-bot" / "data" / "baogaomiao_tasks"
TASK_DIR.mkdir(parents=True, exist_ok=True)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BaogaomiaoTaskProcessor:
    """baogaomiao任务处理器"""

    def __init__(self):
        self.task_dir = TASK_DIR

    def check_new_tasks(self):
        """检查是否有新的pending任务"""
        try:
            task_files = sorted(self.task_dir.glob("task_*.json"),
                                key=lambda p: p.stat().st_mtime)
            pending_tasks = [f for f in task_files
                             if self._is_pending(f)]

            if pending_tasks:
                logger.info(f"✓ 发现 {len(pending_tasks)} 个待处理任务")
                return pending_tasks
            return []
        except Exception as e:
            logger.error(f"检查任务失败: {e}")
            return []

    def _is_pending(self, task_file):
        """检查任务文件是否为pending状态"""
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            return task_data.get('status') == 'pending'
        except Exception as e:
            logger.error(f"读取任务失败 {task_file}: {e}")
            return False

    def process_task(self, task_file):
        """处理单个任务"""
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)

            task_id = task_data.get('task_id', 'unknown')
            pdf_path = task_data.get('pdf_path', '')
            created_at = task_data.get('created_at', '')

            logger.info(f"开始处理任务 {task_id}")
            logger.info(f"  PDF路径: {pdf_path}")

            # 步骤1：提取PDF内容
            if not pdf_path or not os.path.exists(pdf_path):
                self._update_task_status(task_file, 'failed',
                                      error='PDF文件不存在')
                return

            pdf_extractor = PDFExtractor(pdf_path)
            extract_result = pdf_extractor.extract(max_pages=5)

            if not extract_result['success']:
                self._update_task_status(task_file, 'failed',
                                      error=f'PDF提取失败: {extract_result.get("error", "未知")}')
                return

            pdf_text = extract_result.get('text', '')
            logger.info(f"  ✓ PDF提取成功，共 {len(pdf_text)} 字符")

            # 步骤2：生成小红书笔记（3步输出）
            # 这里调用实际的baogaomiao skill逻辑来生成笔记
            # 由于是独立脚本，需要模拟完整工作流

            # 步骤2.1：生成中文标题
            chinese_title = self._generate_chinese_title(pdf_text)

            # 步骤2.2：生成英文标题
            english_title = self._generate_english_title(chinese_title)

            # 步骤2.3：生成小红书笔记
            xhs_note = self._generate_xhs_note(pdf_text)

            # 格式化完整笔记
            full_note = format_xhs_note(chinese_title, english_title, xhs_note)

            # 步骤3：发送到飞书
            sender = FeishuSender()
            send_result = sender.send(full_note, auto_send=True)

            if send_result['success']:
                logger.info(f"  ✓ 飞书发送成功")

                # 保存处理结果到任务文件
                result_data = {
                    'status': 'completed',
                    'chinese_title': chinese_title,
                    'english_title': english_title,
                    'xhs_note': xhs_note,
                    'completed_at': datetime.now().isoformat(),
                    'sent_to_feishu': True
                }

                self._update_task_status(task_file, 'completed', result=result_data)
                logger.info(f"✓ 任务 {task_id} 处理完成")

                return {
                    'success': True,
                    'task_id': task_id,
                    'chinese_title': chinese_title,
                    'english_title': english_title
                }
            else:
                error_msg = send_result.get('error', '飞书发送失败')
                self._update_task_status(task_file, 'failed', error=error_msg)
                logger.error(f"  飞书发送失败: {error_msg}")

                return {
                    'success': False,
                    'task_id': task_id,
                    'error': error_msg
                }

        except Exception as e:
            logger.error(f"处理任务异常 {task_file}: {e}")
            self._update_task_status(task_file, 'failed', error=str(e))
            return {
                'success': False,
                'task_id': task_id,
                'error': str(e)
            }

    def _generate_chinese_title(self, pdf_text):
        """生成中文标题（🎯2026开头）"""
        # 简化版本：从PDF文本中提取核心内容
        # 实际应用中应由Claude Code执行完整分析

        # 这里生成一个基础的标题
        return f"🎯2026 PDF内容总结"

    def _generate_english_title(self, chinese_title):
        """生成英文标题"""
        return "PDF Summary"

    def _generate_xhs_note(self, pdf_text):
        """生成小红书笔记"""
        # 简化版本：返回提取的文本
        # 实际应用中应由Claude Code执行完整分析和生成

        return f"""
【PDF内容摘要】

{pdf_text[:500]}...

（完整笔记需要通过Claude Code的完整baogaomiao skill生成）
"""

    def _update_task_status(self, task_file, status, result=None, error=None):
        """更新任务状态"""
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)

            task_data['status'] = status
            task_data['updated_at'] = datetime.now().isoformat()

            if result is not None:
                task_data['result'] = result
            if error is not None:
                task_data['error'] = error

            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, ensure_ascii=False, indent=2)

            logger.info(f"  ✓ 更新任务状态: {status}")

        except Exception as e:
            logger.error(f"更新任务状态失败: {e}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='baogaomiao任务处理器'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='检查新任务'
    )
    parser.add_argument(
        '--process',
        type=str,
        metavar='TASK_FILE',
        help='处理指定任务文件'
    )
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='守护进程模式，持续检查和处理任务'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='检查间隔（秒），默认60秒'
    )

    args = parser.parse_args()

    processor = BaogaomiaoTaskProcessor()

    if args.check:
        # 检查新任务
        tasks = processor.check_new_tasks()
        if tasks:
            logger.info(f"\n发现 {len(tasks)} 个待处理任务：")
            for task_file in tasks:
                with open(task_file, 'r') as f:
                    task_data = json.load(f)
                    logger.info(f"  • {task_data.get('task_id')} - {task_data.get('pdf_path', '')}")
        else:
            logger.info("\n没有待处理任务")

    elif args.process:
        # 处理指定任务
        logger.info(f"\n处理任务: {args.process}")
        result = processor.process_task(args.process)
        if result['success']:
            logger.info(f"\n✓ 任务 {result['task_id']} 处理完成")
            logger.info(f"  中文标题: {result.get('chinese_title', '')}")
        else:
            logger.error(f"\n✗ 任务处理失败: {result.get('error', '未知')}")

    elif args.daemon:
        # 守护进程模式
        logger.info(f"\n启动守护进程（检查间隔: {args.interval}秒）...")

        import time
        try:
            while True:
                tasks = processor.check_new_tasks()

                for task_file in tasks:
                    result = processor.process_task(task_file)

                if result['success']:
                    logger.info(f"  ✓ 任务 {result['task_id']} 完成")
                else:
                    logger.error(f"  ✗ 任务 {result.get('task_id')} 失败: {result.get('error', '')}")

                time.sleep(args.interval)

        except KeyboardInterrupt:
            logger.info("\n守护进程已停止")
        except Exception as e:
            logger.error(f"\n守护进程异常: {e}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
