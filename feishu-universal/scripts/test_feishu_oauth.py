#!/usr/bin/env python3
"""
测试飞书 OAuth 授权流程 - 只生成授权 URL
"""

import requests
import urllib.parse

# 配置
APP_ID = "cli_a9d0ce936278dced"
APP_SECRET = "OSDjdk36qaGZ0xzD7TXmgb5kmuRneuZy"
REDIRECT_URI = "http://localhost:8080/callback"
SCOPE = "contact:user.base:readonly bitable:app drive:drive im:message"

print("=" * 60)
print("飞书 OAuth 授权测试")
print("=" * 60)

# 步骤 1: 获取 app_access_token
print("\n[步骤 1/3] 获取 app_access_token...")

url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
payload = {
    "app_id": APP_ID,
    "app_secret": APP_SECRET
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    data = response.json()
    if data.get("code") == 0:
        app_access_token = data.get("app_access_token")
        print(f"✅ app_access_token: {app_access_token[:20]}...")
    else:
        print(f"❌ 失败: {data.get('msg')}")
        exit(1)
else:
    print(f"❌ 请求失败: {response.status_code}")
    exit(1)

# 步骤 2: 生成授权 URL
print("\n[步骤 2/3] 生成授权 URL...")

params = {
    "app_id": APP_ID,
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "state": "test_oauth_123"
}

auth_url = f"https://open.feishu.cn/open-apis/authen/v1/authorize?{urllib.parse.urlencode(params)}"

print(f"\n授权 URL:")
print("-" * 60)
print(auth_url)
print("-" * 60)

print(f"\n📋 使用说明:")
print(f"1. 复制上面的 URL 到浏览器")
print(f"2. 登录飞书并点击'同意授权'")
print(f"3. 浏览器会跳转到: {REDIRECT_URI}?code=xxxxx")
print(f"4. 复制完整的回调 URL")

# 步骤 3: 手动输入回调 URL
print(f"\n[步骤 3/3] 输入回调 URL...")
print(f"请将回调 URL 粘贴到这里（或按 Ctrl+C 退出）:")

try:
    callback_url = input().strip()

    # 解析 code
    parsed = urllib.parse.urlparse(callback_url)
    params = urllib.parse.parse_qs(parsed.query)

    if "code" in params:
        code = params["code"][0]
        print(f"\n✅ 提取到授权码: {code[:20]}...")

        # 换取 user_access_token
        print("\n正在换取 user_access_token...")

        url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
        headers = {
            "Authorization": f"Bearer {app_access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "app_id": APP_ID,
            "app_secret": APP_SECRET,
            "grant_type": "authorization_code",
            "code": code
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                token_data = data.get("data")

                user_access_token = token_data.get("access_token")
                refresh_token = token_data.get("refresh_token")
                expires_in = token_data.get("expires_in", 7200)

                print(f"✅ user_access_token: {user_access_token[:20]}...")
                print(f"✅ refresh_token: {refresh_token[:20]}...")
                print(f"✅ 有效期: {expires_in} 秒")

                # 获取用户信息
                print("\n正在获取用户信息...")

                url = "https://open.feishu.cn/open-apis/authen/v1/user_info"
                headers = {
                    "Authorization": f"Bearer {user_access_token}",
                    "Content-Type": "application/json"
                }

                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 0:
                        user_info = data.get("data")
                        user_open_id = user_info.get("open_id")
                        user_name = user_info.get("name")

                        print(f"✅ 用户 Open ID: {user_open_id}")
                        print(f"✅ 用户名称: {user_name}")

                        # 保存配置
                        import json
                        import os
                        import time

                        config = {
                            "app_id": APP_ID,
                            "app_secret": APP_SECRET,
                            "user_access_token": user_access_token,
                            "refresh_token": refresh_token,
                            "user_open_id": user_open_id,
                            "expires_at": int(time.time() + expires_in),
                            "auth_time": int(time.time())  # 记录授权时间，用于追踪 refresh_token 过期
                        }

                        config_path = os.path.expanduser("~/.feishu_user_config.json")

                        with open(config_path, "w") as f:
                            json.dump(config, f, indent=2, ensure_ascii=False)

                        print(f"\n✅ 配置已保存到: {config_path}")
                        print(f"\n🎉 OAuth 授权完成！现在可以使用飞书自动化功能了")
                    else:
                        print(f"❌ 获取用户信息失败: {data.get('msg')}")
                else:
                    print(f"❌ 请求失败: {response.status_code}")
            else:
                print(f"❌ 换取 token 失败: {data.get('msg')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    else:
        print(f"❌ 回调 URL 中未找到 code 参数")
except KeyboardInterrupt:
    print(f"\n\n⚠️  用户取消")
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
