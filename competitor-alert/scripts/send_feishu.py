#!/usr/bin/env python3
"""
飞书通知脚本
发送竞品预警消息到飞书
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path


class FeishuNotifier:
    """飞书通知器"""

    def __init__(self, config_path=None):
        """
        初始化通知器

        Args:
            config_path: 配置文件路径
        """
        # 优先使用全局飞书配置
        global_config = Path.home() / '.feishu_user_config.json'
        if global_config.exists():
            self._load_config(global_config)
            self.base_url = "https://open.feishu.cn/open-apis"
            self._get_app_token()
            return

        # 从环境变量或配置文件读取飞书凭据
        self.app_id = os.getenv('FEISHU_APP_ID', '')
        self.app_secret = os.getenv('FEISHU_APP_SECRET', '')
        self.webhook_url = os.getenv('FEISHU_BOT_WEBHOOK', '')
        self.user_open_id = None
        self.base_url = "https://open.feishu.cn/open-apis"

        # 如果环境变量为空，尝试从配置文件读取
        if not self.app_id or not self.app_secret:
            self._load_config(config_path)

        self.app_access_token = None
        self.access_token = None
        self.token_expire_time = 0

    def _load_config(self, config_path):
        """从配置文件加载飞书凭据"""
        if config_path is None:
            # 尝试多个可能的配置文件位置
            possible_paths = [
                Path(__file__).parent / 'config.py',
                Path(__file__).parent.parent / 'config' / 'feishu.json',
            ]

            for path in possible_paths:
                if path.exists():
                    config_path = path
                    break

        if config_path and Path(config_path).exists():
            if config_path.suffix == '.py':
                # 从 Python 文件导入配置
                import importlib.util
                spec = importlib.util.spec_from_file_location("config", config_path)
                config = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config)

                self.app_id = getattr(config, 'FEISHU_APP_ID', '')
                self.app_secret = getattr(config, 'FEISHU_APP_SECRET', '')
                self.webhook_url = getattr(config, 'FEISHU_BOT_WEBHOOK', '')
                self.user_open_id = getattr(config, 'user_open_id', None)
            else:
                # 从 JSON 文件读取配置
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.app_id = config.get('app_id', '')
                    self.app_secret = config.get('app_secret', '')
                    self.webhook_url = config.get('webhook_url', '')
                    self.user_open_id = config.get('user_open_id', None)

    def _get_app_token(self):
        """获取 app_access_token"""
        url = f"{self.base_url}/auth/v3/app_access_token/internal"

        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    self.app_access_token = data.get("app_access_token")
                else:
                    print(f"获取 token 失败: {data.get('msg')}")
            else:
                print(f"请求失败: {response.status_code}")
        except Exception as e:
            print(f"请求 token 出错: {e}")

    def get_access_token(self):
        """
        获取飞书访问令牌

        Returns:
            str: 访问令牌
        """
        # 如果有 webhook URL，直接使用
        if self.webhook_url:
            return None  # Webhook 不需要 token

        # 检查 token 是否过期
        if self.access_token and datetime.now().timestamp() < self.token_expire_time:
            return self.access_token

        # 获取新的 token
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        try:
            response = requests.post(url, json=payload)
            data = response.json()

            if data.get('code') == 0:
                self.access_token = data['tenant_access_token']
                # token 有效期 2 小时，提前 5 分钟刷新
                self.token_expire_time = datetime.now().timestamp() + 7200 - 300
                return self.access_token
            else:
                print(f"获取 token 失败: {data}")
                return None
        except Exception as e:
            print(f"请求 token 出错: {e}")
            return None

    def send_alert(self, scan_result):
        """
        发送竞品预警消息（整合版）

        Args:
            scan_result: 完整的扫描结果

        Returns:
            bool: 发送是否成功
        """
        # 生成整合的消息
        message = self._create_integrated_alert(scan_result)

        # 优先使用 webhook
        if self.webhook_url:
            card = self._create_integrated_card(scan_result)
            return self._send_via_webhook(card)

        # 使用 app_access_token 发送文本消息
        return self._send_text(message)

    def send_summary(self, scan_result):
        """
        发送扫描总结

        Args:
            scan_result: 扫描结果

        Returns:
            bool: 发送是否成功
        """
        if self.webhook_url:
            card = self._create_summary_card(scan_result)
            return self._send_via_webhook(card)

        # 生成文本总结
        summary = self._create_text_summary(scan_result)
        return self._send_text(summary)

    def _send_text(self, content):
        """发送文本消息"""
        if not self.app_access_token or not self.user_open_id:
            print("⚠️  缺少 app_access_token 或 user_open_id")
            return False

        url = f"{self.base_url}/im/v1/messages?receive_id_type=open_id"
        headers = {
            "Authorization": f"Bearer {self.app_access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "receive_id": self.user_open_id,
            "msg_type": "text",
            "content": json.dumps({"text": content})
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    print("✅ 飞书通知已发送")
                    return True
                else:
                    print(f"⚠️  发送失败: {data.get('msg')}")
                    return False
            else:
                print(f"⚠️  请求失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠️  发送出错: {e}")
            return False

    def _send_via_api(self, mention_data):
        """通过 API 发送卡片消息"""
        if not self.app_access_token or not self.user_open_id:
            return False

        # 生成文本消息（简化版）
        brand = mention_data['brand']
        note_title = mention_data['note_title']
        note_url = mention_data['note_url']
        content = mention_data['comment'].get('content', '')

        text = f"""🚨 竞品评论预警

品牌: {brand}
笔记: {note_title}
链接: {note_url}

评论: {content[:100]}...
"""

        return self._send_text(text)

    def _create_text_summary(self, result):
        """创建文本总结"""
        total_notes = result['total_notes_scanned']
        total_comments = result['total_comments_scanned']
        competitors = result['competitors_found']

        competitors_text = "\n".join([
            f"- {brand}: {count} 条" for brand, count in competitors.items()
        ]) if competitors else "未发现竞品评论"

        return f"""📊 竞品扫描总结

扫描范围: {total_notes} 条笔记, {total_comments} 条评论

发现竞品评论:
{competitors_text}

扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    def _create_integrated_alert(self, result):
        """创建整合的预警消息"""
        total_notes = result['total_notes_scanned']
        total_comments = result['total_comments_scanned']
        competitors = result['competitors_found']
        mentions = result['competitor_mentions']

        # 按品牌分组
        brand_groups = {}
        for m in mentions:
            brand = m['brand']
            if brand not in brand_groups:
                brand_groups[brand] = []
            brand_groups[brand].append(m)

        # 构建消息
        lines = [
            "🚨 竞品评论预警",
            "",
            f"📊 扫描概况",
            f"扫描范围: {total_notes} 条笔记, {total_comments} 条评论",
            f"发现竞品评论: {sum(competitors.values())} 条",
            ""
        ]

        # 按品牌展示详情
        for brand, items in brand_groups.items():
            lines.append(f"【{brand}】共 {len(items)} 条")
            for item in items[:3]:  # 每个品牌最多显示3条
                note_title = item['note_title']
                note_url = item['note_url']
                content = item['comment'].get('content', '')
                user = item['comment'].get('user', '匿名')

                lines.append(f"  📝 {note_title}")
                lines.append(f"     👤 {user}: {content[:50]}...")
                lines.append(f"     🔗 {note_url}")

            if len(items) > 3:
                lines.append(f"  ... 还有 {len(items) - 3} 条评论")
            lines.append("")

        lines.append(f"⏰ 扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(lines)

    def _create_integrated_card(self, result):
        """创建整合的预警卡片（用于 webhook）"""
        total_notes = result['total_notes_scanned']
        total_comments = result['total_comments_scanned']
        competitors = result['competitors_found']
        mentions = result['competitor_mentions']

        # 按品牌分组
        brand_groups = {}
        for m in mentions:
            brand = m['brand']
            if brand not in brand_groups:
                brand_groups[brand] = []
            brand_groups[brand].append(m)

        # 构建竞品统计文本
        competitors_text = "\n".join([
            f"- {brand}: {count} 条" for brand, count in competitors.items()
        ])

        # 构建详情列表
        details_elements = []
        for brand, items in brand_groups.items():
            for item in items[:3]:
                note_title = item['note_title']
                note_url = item['note_url']
                content = item['comment'].get('content', '')[:80]

                details_elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**【{brand}】** [{note_title}]({note_url})\n{content}..."
                    }
                })
                details_elements.append({"tag": "hr"})

        return {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "🚨 竞品评论预警"
                    },
                    "template": "red"
                },
                "elements": [
                    {
                        "tag": "div",
                        "fields": [
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**扫描笔记**\n{total_notes}"
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**竞品评论**\n{sum(competitors.values())}"
                                }
                            }
                        ]
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**品牌分布**\n{competitors_text}"
                        }
                    },
                    {
                        "tag": "hr"
                    }
                ] + details_elements[:10]  # 限制卡片元素数量
            }
        }

    def _create_alert_card(self, mention):
        """
        创建预警消息卡片

        Args:
            mention: 竞品提及数据

        Returns:
            dict: 消息卡片内容
        """
        brand = mention['brand']
        note_title = mention['note_title']
        note_url = mention['note_url']
        comment = mention['comment']
        content = comment.get('content', '')
        user = comment.get('user', '匿名用户')
        time = comment.get('time', '未知')

        return {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "🚨 竞品评论预警"
                    },
                    "template": "red"
                },
                "elements": [
                    {
                        "tag": "div",
                        "fields": [
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**品牌**\n{brand}"
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**时间**\n{datetime.now().strftime('%Y-%m-%d %H:%M')}"
                                }
                            }
                        ]
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**来源笔记**\n[{note_title}]({note_url})"
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**评论摘要**\n用户: {user}\n\n{content[:200]}..."
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "action",
                        "actions": [
                            {
                                "tag": "button",
                                "text": {
                                    "tag": "plain_text",
                                    "content": "查看笔记"
                                },
                                "url": note_url,
                                "type": "default"
                            }
                        ]
                    }
                ]
            }
        }

    def _create_summary_card(self, result):
        """
        创建扫描总结卡片

        Args:
            result: 扫描结果

        Returns:
            dict: 消息卡片内容
        """
        total_notes = result['total_notes_scanned']
        total_comments = result['total_comments_scanned']
        competitors = result['competitors_found']
        mentions = result['competitor_mentions']

        # 构建竞品统计
        competitors_text = "\n".join([
            f"- {brand}: {count} 条" for brand, count in competitors.items()
        ]) if competitors else "未发现竞品评论"

        # 构建相关笔记列表
        notes_text = ""
        if mentions:
            note_groups = {}
            for m in mentions:
                title = m['note_title']
                if title not in note_groups:
                    note_groups[title] = {'brands': set(), 'url': m['note_url']}

                note_groups[title]['brands'].add(m['brand'])

            notes_text = "\n\n**相关笔记**\n"
            for title, info in list(note_groups.items())[:5]:
                brands = ", ".join(info['brands'])
                notes_text += f"- [{title}]({info['url']}) - {brands}\n"

        return {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "📊 竞品扫描总结"
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**扫描时间**\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                                      f"**扫描范围**\n- 笔记数: {total_notes}\n"
                                      f"- 评论数: {total_comments}\n\n"
                                      f"**发现竞品评论**\n{competitors_text}"
                        }
                    },
                    {
                        "tag": "hr"
                    }
                ]
            }
        }

    def _send_via_webhook(self, card):
        """
        通过 Webhook 发送消息

        Args:
            card: 消息卡片

        Returns:
            bool: 发送是否成功
        """
        try:
            response = requests.post(self.webhook_url, json=card)
            result = response.json()

            if result.get('StatusCode', -1) == 0 or result.get('code', -1) == 0:
                print("✅ 飞书消息发送成功")
                return True
            else:
                print(f"⚠️  飞书消息发送失败: {result}")
                return False
        except Exception as e:
            print(f"⚠️  发送飞书消息出错: {e}")
            return False


def main():
    """主函数 - 用于测试"""
    import argparse

    parser = argparse.ArgumentParser(description='飞书通知测试')
    parser.add_argument('--test-alert', action='store_true', help='发送测试预警')
    parser.add_argument('--test-summary', action='store_true', help='发送测试总结')

    args = parser.parse_args()

    notifier = FeishuNotifier()

    if args.test_alert:
        test_mention = {
            'brand': '强脑',
            'note_title': '睡眠仪真实测评',
            'note_url': 'https://www.xiaohongshu.com/explore/12345',
            'comment': {
                'content': '我觉得强脑的更有效',
                'user': '测试用户',
                'time': '2小时前'
            }
        }
        notifier.send_alert(test_mention)

    elif args.test_summary:
        test_result = {
            'total_notes_scanned': 10,
            'total_comments_scanned': 500,
            'competitors_found': {'强脑': 2, '左点': 1},
            'competitor_mentions': []
        }
        notifier.send_summary(test_result)

    else:
        print("请使用 --test-alert 或 --test-summary 测试")


if __name__ == '__main__':
    main()
