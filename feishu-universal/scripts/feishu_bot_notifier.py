#!/usr/bin/env python3
"""
飞书机器人通知工具
使用应用身份（app_access_token）发送消息，不受用户身份限制
"""

import requests
import json
import os


class FeishuBotNotifier:
    """飞书机器人通知器（使用应用身份）"""

    def __init__(self):
        """初始化机器人通知器"""
        # 从用户配置中读取 app_id 和 app_secret
        config_path = os.path.expanduser("~/.feishu_user_config.json")

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, 'r') as f:
            config = json.load(f)

        self.app_id = config.get('app_id')
        self.app_secret = config.get('app_secret')
        self.user_open_id = config.get('user_open_id')

        self.app_access_token = None
        self.base_url = "https://open.feishu.cn/open-apis"

        # 获取 app_access_token
        self._get_app_token()

    def _get_app_token(self):
        """获取 app_access_token"""
        url = f"{self.base_url}/auth/v3/app_access_token/internal"

        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                self.app_access_token = data.get("app_access_token")
            else:
                raise Exception(f"获取 token 失败: {data.get('msg')}")
        else:
            raise Exception(f"请求失败: {response.status_code}")

    def send_message(self, content):
        """发送消息到用户

        Args:
            content: 消息内容
        """
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

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print("✓ 通知已发送到飞书")
                return True
            else:
                print(f"✗ 发送失败: {data.get('msg')}")
                return False
        else:
            print(f"✗ 请求失败: {response.status_code}")
            return False


def test_notification():
    """测试通知功能"""
    from datetime import datetime

    print("=" * 60)
    print("飞书机器人通知测试")
    print("=" * 60)

    try:
        notifier = FeishuBotNotifier()

        test_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"""🎉 飞书机器人通知测试成功！

你好！这是飞书机器人的测试消息。

✅ 通知功能已启用：
  • 数据导入完成通知
  • Token 即将过期提醒（< 7 天 / < 3 天）

📱 你会收到此消息说明通知功能正常！

测试信息：
• 测试时间：{test_time}
• 通知方式：飞书机器人（app_access_token）

现在使用飞书自动化，你会收到自动通知！"""

        print("\n发送测试消息...")
        success = notifier.send_message(message)

        if success:
            print("\n✅ 测试成功！请检查你的飞书")
        else:
            print("\n❌ 测试失败")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_notification()
