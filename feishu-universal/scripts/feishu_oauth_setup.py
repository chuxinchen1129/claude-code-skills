#!/usr/bin/env python3
"""
飞书 OAuth 授权辅助脚本
帮助用户获取 user_access_token 并保存到配置文件

使用方法：
1. 运行脚本：python3 feishu_oauth_setup.py
2. 在浏览器中打开授权 URL
3. 复制回调 URL 中的 code 参数
4. 粘贴到脚本中，完成授权
"""

import requests
import json
import os
import time
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import webbrowser


# 配置信息
APP_ID = "cli_a9d0ce936278dced"
APP_SECRET = "OSDjdk36qaGZ0xzD7TXmgb5kmuRneuZy"
REDIRECT_URI = "http://localhost:8080/callback"

# 权限范围
SCOPE = "contact:user.base:readonly bitable:app drive:drive im:message"


class CallbackHandler(BaseHTTPRequestHandler):
    """OAuth 回调处理"""

    def do_GET(self):
        if self.path.startswith("/callback"):
            # 解析参数
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)

            if "code" in params:
                code = params["code"][0]

                # 返回成功页面
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()

                html = f"""
                <html>
                <head><title>授权成功</title></head>
                <body>
                    <h1>✅ 授权成功！</h1>
                    <p>授权码: <strong>{code}</strong></p>
                    <p>请复制这个授权码，返回终端继续操作</p>
                    <p>你可以关闭这个页面了</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode("utf-8"))

                # 保存 code 到文件
                with open("/tmp/feishu_oauth_code.txt", "w") as f:
                    f.write(code)

                print(f"\n✅ 收到授权码: {code}")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing code parameter")


def start_callback_server():
    """启动本地回调服务器"""
    server = HTTPServer(("localhost", 8080), CallbackHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print("✓ 本地回调服务器已启动: http://localhost:8080")


def get_app_access_token():
    """获取 app_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"

    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 0:
            return data.get("app_access_token")
        else:
            raise Exception(f"获取 app_access_token 失败: {data.get('msg')}")
    else:
        raise Exception(f"请求失败: {response.status_code}")


def get_user_access_token(app_access_token, code):
    """用授权码换取 user_access_token"""
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
            return data.get("data")
        else:
            raise Exception(f"获取 user_access_token 失败: {data.get('msg')}")
    else:
        raise Exception(f"请求失败: {response.status_code}")


def get_user_info(user_access_token):
    """获取用户信息"""
    url = "https://open.feishu.cn/open-apis/authen/v1/user_info"

    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 0:
            return data.get("data")
        else:
            raise Exception(f"获取用户信息失败: {data.get('msg')}")
    else:
        raise Exception(f"请求失败: {response.status_code}")


def save_config(user_access_token, refresh_token, user_open_id, expires_in):
    """保存配置到文件"""
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


def main():
    """主流程"""
    print("=" * 60)
    print("飞书 OAuth 授权流程")
    print("=" * 60)

    # 步骤 1: 获取 app_access_token
    print("\n[步骤 1/5] 获取 app_access_token...")
    app_access_token = get_app_access_token()
    print(f"✓ app_access_token: {app_access_token[:20]}...")

    # 步骤 2: 生成授权 URL
    print("\n[步骤 2/5] 生成授权 URL...")

    params = {
        "app_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "state": "feishu_oauth_" + str(int(time.time()))
    }

    auth_url = f"https://open.feishu.cn/open-apis/authen/v1/authorize?{urllib.parse.urlencode(params)}"

    print(f"\n授权 URL:")
    print(f"-" * 60)
    print(auth_url)
    print(f"-" * 60)

    # 步骤 3: 启动本地服务器
    print("\n[步骤 3/5] 启动本地回调服务器...")
    start_callback_server()

    # 步骤 4: 打开浏览器
    print("\n[步骤 4/5] 打开浏览器完成授权...")
    print("正在打开浏览器...")

    try:
        webbrowser.open(auth_url)
        print("✓ 浏览器已打开")
    except:
        print("⚠️  无法自动打开浏览器，请手动复制上面的 URL 到浏览器")

    print("\n请在浏览器中：")
    print("1. 登录飞书账号")
    print("2. 点击'同意授权'")
    print("3. 等待跳转到回调页面")

    # 步骤 5: 等待授权码
    print("\n[步骤 5/5] 等待授权码...")

    max_wait = 300  # 最多等待 5 分钟
    start_time = time.time()

    code_file = "/tmp/feishu_oauth_code.txt"

    while time.time() - start_time < max_wait:
        if os.path.exists(code_file):
            with open(code_file, "r") as f:
                code = f.read().strip()
            os.remove(code_file)
            break
        time.sleep(1)
        print(".", end="", flush=True)
    else:
        print("\n❌ 等待超时，请重试")
        return

    print(f"\n✓ 收到授权码: {code[:20]}...")

    # 换取 user_access_token
    print("\n正在换取 user_access_token...")
    token_data = get_user_access_token(app_access_token, code)

    user_access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 7200)

    print(f"✓ user_access_token: {user_access_token[:20]}...")
    print(f"✓ refresh_token: {refresh_token[:20]}...")
    print(f"✓ 有效期: {expires_in} 秒")

    # 获取用户信息
    print("\n正在获取用户信息...")
    user_info = get_user_info(user_access_token)

    user_open_id = user_info.get("open_id")
    user_name = user_info.get("name")

    print(f"✓ 用户 Open ID: {user_open_id}")
    print(f"✓ 用户名称: {user_name}")

    # 保存配置
    save_config(user_access_token, refresh_token, user_open_id, expires_in)

    # 完成
    print("\n" + "=" * 60)
    print("✅ OAuth 授权完成！")
    print("=" * 60)
    print(f"\n用户: {user_name}")
    print(f"Open ID: {user_open_id}")
    print(f"\n现在可以使用以下命令:")
    print(f"  python3 feishu_user_auto.py create-base --name \"我的Base\"")
    print(f"  python3 feishu_user_auto.py import-data --app-token <TOKEN> --table-id <ID> --excel data.xlsx")
    print(f"  python3 feishu_user_auto.py notify --message \"数据导入完成\"")


if __name__ == "__main__":
    main()
