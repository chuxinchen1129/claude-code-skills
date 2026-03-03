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
        self.chat_id = config.get('chat_id', self.user_open_id)  # 优先使用 chat_id

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
                print(f"✓ app_access_token 获取成功: {self.app_access_token[:20] if self.app_access_token else 'None'}")
            else:
                error_code = data.get('code')
                error_msg = data.get('msg', '未知错误')
                raise Exception(f"获取 token 失败: [{error_code}] {error_msg}")
        else:
            raise Exception(f"请求失败: HTTP {response.status_code}")

    def send_message(self, content, max_retries=3, retry_delay=1):
        """发送消息到用户

        Args:
            content: 消息内容
            max_retries: 最大重试次数（默认3次）
            retry_delay: 重试延迟秒数（默认1秒）

        Returns:
            bool: 发送是否成功
        """
        import time

        # 优先使用 chat_id，确保消息和监听在同一聊天中
        if self.chat_id and self.chat_id != self.user_open_id:
            # 使用 chat_id 发送消息
            url = f"{self.base_url}/im/v1/messages?receive_id_type=chat_id"
            receive_id = self.chat_id
        else:
            # 回退到 user_open_id
            url = f"{self.base_url}/im/v1/messages?receive_id_type=open_id"
            receive_id = self.user_open_id

        headers = {
            "Authorization": f"Bearer {self.app_access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "receive_id": receive_id,
            "msg_type": "text",
            "content": json.dumps({"text": content})
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=10  # 10秒超时
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 0:
                        print("✓ 通知已发送到飞书")
                        return True
                    else:
                        # API 返回错误，检查是否可重试
                        error_code = data.get("code")
                        error_msg = data.get("msg", "未知错误")

                        # 限流错误 (99991663) 和某些临时错误可重试
                        retryable_codes = [99991663, 99991400, 99991398]
                        if error_code in retryable_codes and attempt < max_retries - 1:
                            print(f"⚠️ API限流/临时错误 ({error_code})，{retry_delay}秒后重试...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            print(f"✗ 发送失败: [{error_code}] {error_msg}")
                            return False
                else:
                    # HTTP 错误
                    if attempt < max_retries - 1:
                        print(f"⚠️ HTTP {response.status_code}，{retry_delay}秒后重试...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"✗ 请求失败: HTTP {response.status_code}")
                        return False

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"⚠️ 请求超时，{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print("✗ 请求超时")
                    return False

            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ 网络连接错误，{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"✗ 网络连接错误: {e}")
                    return False

            except Exception as e:
                print(f"✗ 未知错误: {e}")
                return False

        return False

    def upload_image(self, image_path, max_retries=3, retry_delay=1):
        """上传图片到飞书，返回 image_key

        Args:
            image_path: 图片文件路径
            max_retries: 最大重试次数（默认3次）
            retry_delay: 重试延迟秒数（默认1秒）

        Returns:
            str: image_key，失败返回 None
        """
        import time

        if not os.path.exists(image_path):
            print(f"✗ 图片文件不存在: {image_path}")
            return None

        url = f"{self.base_url}/im/v1/images"

        for attempt in range(max_retries):
            try:
                # 使用 requests_toolbell 的 MultipartEncoder 确保正确的编码
                try:
                    from requests_toolbelt import MultipartEncoder

                    form = {
                        'image_type': 'message',
                        'image': (os.path.basename(image_path), open(image_path, 'rb'), 'image/png')
                    }
                    multi_form = MultipartEncoder(form)
                    headers = {
                        "Authorization": f"Bearer {self.app_access_token}",
                        "Content-Type": multi_form.content_type
                    }
                    response = requests.post(url, headers=headers, data=multi_form, timeout=30)

                except ImportError:
                    # 回退到标准 requests 格式（使用 'image' 字段名）
                    headers = {
                        "Authorization": f"Bearer {self.app_access_token}"
                    }
                    with open(image_path, 'rb') as f:
                        files = {
                            'image_type': (None, 'message'),
                            'image': (os.path.basename(image_path), f, 'image/png')
                        }
                        response = requests.post(url, headers=headers, files=files, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 0:
                        image_key = data.get("data", {}).get("image_key")
                        if image_key:
                            print(f"✓ 图片上传成功: {os.path.basename(image_path)}")
                            return image_key
                        else:
                            print(f"✗ 上传响应中没有 image_key")
                            return None
                    else:
                        # API 返回错误，检查是否可重试
                        error_code = data.get("code")
                        error_msg = data.get("msg", "未知错误")

                        retryable_codes = [99991663, 99991400, 99991398]
                        if error_code in retryable_codes and attempt < max_retries - 1:
                            print(f"⚠️ 图片上传限流 ({error_code})，{retry_delay}秒后重试...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            print(f"✗ 图片上传失败: [{error_code}] {error_msg}")
                            return None
                else:
                    # HTTP 错误
                    if attempt < max_retries - 1:
                        print(f"⚠️ 图片上传 HTTP {response.status_code}，{retry_delay}秒后重试...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"✗ 图片上传请求失败: HTTP {response.status_code}")
                        return None

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"⚠️ 图片上传超时，{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print("✗ 图片上传超时")
                    return None

            except Exception as e:
                print(f"✗ 图片上传异常: {e}")
                return None

        return None

    def send_image_message(self, image_path_or_key, max_retries=3, retry_delay=1):
        """发送单张图片消息

        Args:
            image_path_or_key: 图片路径或 image_key
            max_retries: 最大重试次数（默认3次）
            retry_delay: 重试延迟秒数（默认1秒）

        Returns:
            bool: 发送是否成功
        """
        import time

        # 如果是路径，先上传获取 key
        if isinstance(image_path_or_key, str) and os.path.exists(image_path_or_key):
            image_key = self.upload_image(image_path_or_key, max_retries, retry_delay)
            if not image_key:
                return False
        else:
            image_key = image_path_or_key

        url = f"{self.base_url}/im/v1/messages?receive_id_type=open_id"

        headers = {
            "Authorization": f"Bearer {self.app_access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "receive_id": self.user_open_id,
            "msg_type": "image",
            "content": json.dumps({"image_key": image_key})
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 0:
                        print("✓ 图片消息已发送到飞书")
                        return True
                    else:
                        error_code = data.get("code")
                        error_msg = data.get("msg", "未知错误")

                        retryable_codes = [99991663, 99991400, 99991398]
                        if error_code in retryable_codes and attempt < max_retries - 1:
                            print(f"⚠️ 发送限流 ({error_code})，{retry_delay}秒后重试...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            print(f"✗ 发送失败: [{error_code}] {error_msg}")
                            return False
                else:
                    if attempt < max_retries - 1:
                        print(f"⚠️ HTTP {response.status_code}，{retry_delay}秒后重试...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"✗ 请求失败: HTTP {response.status_code}")
                        return False

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"⚠️ 请求超时，{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print("✗ 请求超时")
                    return False

            except Exception as e:
                print(f"✗ 发送异常: {e}")
                return False

        return False

    def send_image_batch(self, image_paths, delay=1):
        """批量发送多张图片

        Args:
            image_paths: 图片文件路径列表
            delay: 每张图片之间的间隔秒数（默认1秒）

        Returns:
            dict: 发送结果统计
        """
        import time

        results = {
            'success': 0,
            'failed': 0,
            'total': len(image_paths),
            'details': []
        }

        for i, image_path in enumerate(image_paths, 1):
            print(f"\n发送图片 {i}/{len(image_paths)}: {os.path.basename(image_path)}")

            success = self.send_image_message(image_path)

            if success:
                results['success'] += 1
                results['details'].append({'path': image_path, 'status': 'success'})
            else:
                results['failed'] += 1
                results['details'].append({'path': image_path, 'status': 'failed'})

            # 间隔 delay 秒，避免限流
            if i < len(image_paths):
                time.sleep(delay)

        print(f"\n✓ 图片发送完成: 成功 {results['success']}/{results['total']}")

        return results


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
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='飞书机器人通知工具')
    parser.add_argument('--message', '-m', help='要发送的消息内容')
    parser.add_argument('--test', '-t', action='store_true', help='发送测试消息')

    args = parser.parse_args()

    if args.message:
        # 发送指定消息
        try:
            notifier = FeishuBotNotifier()
            success = notifier.send_message(args.message)
            if success:
                print("✅ 消息已发送")
                sys.exit(0)
            else:
                print("❌ 消息发送失败")
                sys.exit(1)
        except Exception as e:
            print(f"❌ 错误: {e}")
            sys.exit(1)
    else:
        # 默认发送测试消息
        test_notification()
