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

# 导入飞书路径模块
_dms_root = Path(__file__).parent.parent.parent.parent
_feishu_scripts = _dms_root / 'skills' / 'feishu-universal' / 'scripts'
sys.path.insert(0, str(_feishu_scripts))
try:
    from feishu_paths import FeishuPaths
    USE_FEISHU_PATHS = True
except ImportError:
    USE_FEISHU_PATHS = False


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
        # 使用统一的飞书路径管理
        if USE_FEISHU_PATHS:
            script_path = FeishuPaths.BOT_NOTIFIER
        else:
            # 回退到相对路径
            base_dir = Path(__file__).resolve().parent
            script_path = base_dir / 'feishu-universal' / 'scripts' / 'feishu_bot_notifier.py'

            if not script_path.exists():
                # 再回退到 DMS 根目录
                script_path = _dms_root / 'skills' / 'feishu-universal' / 'scripts' / 'feishu_bot_notifier.py'

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

    def send_screenshots(self, screenshot_paths):
        """发送截图列表到飞书

        Args:
            screenshot_paths: 截图文件路径列表

        Returns:
            dict: 发送结果
        """
        if not screenshot_paths:
            return {'success': True, 'message': '没有截图需要发送'}

        try:
            # 导入 FeishuBotNotifier
            import sys
            from pathlib import Path

            # 优先使用 ~/.claude/skills/feishu-universal
            feishu_universal_dir = Path.home() / '.claude' / 'skills' / 'feishu-universal'

            # 如果不存在，尝试相对路径（用于开发环境）
            if not feishu_universal_dir.exists():
                base_dir = Path(__file__).resolve().parent.parent
                feishu_universal_dir = base_dir / 'feishu-universal'

            # 将 feishu-universal 添加到 Python 路径
            if str(feishu_universal_dir) not in sys.path:
                sys.path.insert(0, str(feishu_universal_dir))

            from scripts.feishu_bot_notifier import FeishuBotNotifier

            notifier = FeishuBotNotifier()
            results = notifier.send_image_batch(screenshot_paths, delay=1)

            if results['success'] == results['total']:
                return {
                    'success': True,
                    'message': f"{results['total']} 张截图已发送到飞书",
                    'results': results
                }
            else:
                return {
                    'success': False if results['success'] == 0 else True,  # 部分成功也算成功
                    'message': f"截图发送完成: {results['success']}/{results['total']} 成功",
                    'results': results
                }

        except FileNotFoundError as e:
            return {
                'success': False,
                'error': f'未找到飞书通知模块: {e}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'发送截图失败: {str(e)}'
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


def format_xhs_note(xhs_note):
    """格式化小红书笔记内容用于发送

    只返回小红书笔记（不再包含中英文标题）
    """
    return [xhs_note]


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='飞书消息发送工具')
    parser.add_argument('--content', '-c', type=str, help='要发送的内容')
    parser.add_argument('--no-auto', action='store_true', help='不自动发送，仅返回格式化内容')
    parser.add_argument('--auto-send', action='store_true', help='自动发送（默认行为）')
    parser.add_argument('message', nargs='?', type=str, help='要发送的内容（位置参数）')

    args = parser.parse_args()

    # 优先使用 --content 参数，否则使用位置参数
    content = args.content or args.message

    if not content:
        parser.print_help()
        sys.exit(1)

    auto_send = not args.no_auto

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
        if 'results' in result:
            for r in result['results']:
                if not r['success']:
                    print(f"  - {r.get('error', '未知错误')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
