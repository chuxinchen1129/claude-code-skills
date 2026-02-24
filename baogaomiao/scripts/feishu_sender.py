#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书消息发送工具
用于将生成的小红书笔记自动发送到飞书
"""

import os
import sys
import urllib.request
import urllib.error
import json
from pathlib import Path


class FeishuSender:
    """飞书消息发送器"""

    def __init__(self):
        self.webhook_url = os.environ.get('FEISHU_WEBHOOK_URL', '')
        self.app_id = os.environ.get('FEISHU_APP_ID', '')
        self.app_secret = os.environ.get('FEISHU_APP_SECRET', '')

        # 优先使用 webhook（最简单）
        self.use_webhook = bool(self.webhook_url)

    def send_via_webhook(self, content):
        """通过 Webhook 发送消息

        Args:
            content: 可以是字符串或字符串列表（用于分批发送）
        """
        if not self.webhook_url:
            return {
                'success': False,
                'error': '未设置 FEISHU_WEBHOOK_URL 环境变量'
            }

        try:
            import time

            # 支持单条消息或列表消息（分批发送）
            messages = content if isinstance(content, list) else [content]

            results = []
            for i, msg in enumerate(messages, 1):
                data = {
                    "msg_type": "text",
                    "content": {
                        "text": msg
                    }
                }

                req = urllib.request.Request(
                    self.webhook_url,
                    data=json.dumps(data).encode('utf-8'),
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )

                with urllib.request.urlopen(req, timeout=10) as response:
                    response_data = json.loads(response.read().decode('utf-8'))

                if response_data.get('code') == 0:
                    results.append({'success': True, 'message': f'消息 {i}/3 已发送'})
                else:
                    results.append({'success': False, 'error': f'消息 {i}/3 发送失败: {response_data.get("msg", "未知错误")}'})

                # 每条消息间隔1秒，避免限流
                if i < len(messages):
                    time.sleep(1)

            all_success = all(r['success'] for r in results)
            if all_success:
                return {
                    'success': True,
                    'message': f'{len(messages)}条消息已发送到飞书',
                    'results': results
                }
            else:
                return {
                    'success': False,
                    'error': '部分消息发送失败',
                    'results': results
                }

        except urllib.error.URLError as e:
            return {
                'success': False,
                'error': f'网络错误: {str(e)}'
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'JSON解析错误: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'未知错误: {str(e)}'
            }

    def send_via_bot_notifier(self, content):
        """通过 feishu_bot_notifier.py 发送消息

        Args:
            content: 可以是字符串或字符串列表（用于分批发送）
        """
        # 使用绝对路径解析，避免在工作目录运行时路径错误
        base_dir = Path(__file__).resolve().parent
        script_path = base_dir / 'feishu-universal' / 'scripts' / 'feishu_bot_notifier.py'

        if not script_path.exists():
            # 回退到本地路径
            script_path = Path.home() / '.claude' / 'skills' / 'feishu-universal' / 'scripts' / 'feishu_bot_notifier.py'

        if not script_path.exists():
            return {
                'success': False,
                'error': f'未找到 feishu_bot_notifier.py: {script_path}'
            }

        try:
            import subprocess
            import time

            # 支持单条消息或列表消息（分批发送）
            messages = content if isinstance(content, list) else [content]

            results = []
            for i, msg in enumerate(messages, 1):
                result = subprocess.run(
                    ['python3', str(script_path), '--message', msg],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    results.append({'success': True, 'message': f'消息 {i}/3 已发送'})
                else:
                    results.append({'success': False, 'error': f'消息 {i}/3 发送失败: {result.stderr}'})

                # 每条消息间隔1秒，避免限流
                if i < len(messages):
                    time.sleep(1)

            all_success = all(r['success'] for r in results)
            if all_success:
                return {
                    'success': True,
                    'message': f'{len(messages)}条消息已发送到飞书',
                    'results': results
                }
            else:
                return {
                    'success': False,
                    'error': '部分消息发送失败',
                    'results': results
                }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '发送超时（30秒）'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': '未找到 python3 或脚本'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'未知错误: {str(e)}'
            }

    def send(self, content, auto_send=True):
        """
        发送消息到飞书

        Args:
            content: 要发送的消息内容
            auto_send: 是否自动发送（True）或仅返回内容供用户确认（False）

        Returns:
            dict: 发送结果
        """
        if not auto_send:
            return {
                'success': True,
                'auto_send': False,
                'message': '已生成内容，未自动发送',
                'content': content
            }

        # 优先使用 webhook
        if self.use_webhook:
            return self.send_via_webhook(content)

        # 否则使用 bot_notifier
        return self.send_via_bot_notifier(content)


def format_xhs_note(chinese_title, english_title, xhs_note):
    """格式化小红书笔记内容用于发送

    返回3个独立的消息，分别发送：
    1. 中文标题
    2. 英文标题（带分隔符）
    3. 小红书笔记
    """
    separator = "\n" + "="*50 + "\n"
    return [
        chinese_title,
        separator + english_title,
        separator + xhs_note
    ]


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python feishu_sender.py <内容> [--no-auto]")
        print("选项:")
        print("  --no-auto    不自动发送，仅返回格式化内容")
        print("\n示例:")
        print("  python feishu_sender.py '这是要发送的内容'")
        print("  python feishu_sender.py '这是内容' --no-auto")
        sys.exit(1)

    content = sys.argv[1]
    auto_send = '--no-auto' not in sys.argv

    sender = FeishuSender()
    result = sender.send(content, auto_send=auto_send)

    if result['success']:
        if auto_send:
            print(f"✅ {result.get('message', '发送成功')}")
        else:
            print("✅ 内容已格式化（未自动发送）")
            print("\n--- 内容 ---")
            print(result['content'])
    else:
        print(f"❌ 发送失败: {result.get('error', '未知错误')}")
        if not auto_send:
            print("\n--- 内容 ---")
            print(content)
        sys.exit(1)


if __name__ == '__main__':
    main()
