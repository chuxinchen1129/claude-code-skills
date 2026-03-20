#!/usr/bin/env python3
"""
飞书 OAuth 授权脚本（标准授权码模式）
使用本地 HTTP 服务器接收回调
"""
import json
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
import webbrowser
import threading
from datetime import datetime
import requests

# 飞书应用配置（从环境变量读取）
APP_ID = os.getenv("FEISHU_APP_ID") or os.getenv("LARK_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET") or os.getenv("LARK_APP_SECRET")
REDIRECT_URI = "http://localhost:18080"

# 授权URL（延后在 main 中校验环境变量）
AUTH_URL = None


class CallbackHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 禁用日志输出

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        try:
            with open("/tmp/feishu_auth.log", "a") as f:
                f.write(f"[{datetime.now().isoformat()}] GET {self.path}\n")
        except Exception:
            pass

        # 回调处理
        if parsed.path.startswith('/callback') or 'code' in params:
            if 'code' in params:
                code = params['code'][0]

                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()

                # 用授权码获取 token
                try:
                    url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
                    headers = {'Content-Type': 'application/json; charset=utf-8'}
                    data = {
                        'app_id': APP_ID,
                        'app_secret': APP_SECRET,
                        'grant_type': 'authorization_code',
                        'code': code
                    }

                    response = requests.post(url, headers=headers, json=data, timeout=10)
                    result = response.json()

                    if result.get('code') == 0:
                        try:
                            with open("/tmp/feishu_auth.log", "a") as f:
                                f.write(f"[{datetime.now().isoformat()}] AUTH SUCCESS\n")
                        except Exception:
                            pass
                        # 保存 token
                        config_path = "/Users/echo/.feishu_user_config.json"
                        current_time = int(time.time())

                        new_config = {
                            'app_id': APP_ID,
                            'app_secret': APP_SECRET,
                            'user_access_token': result['data']['access_token'],
                            'refresh_token': result['data']['refresh_token'],
                            'user_open_id': result['data'].get('open_id', ''),
                            'chat_id': result['data'].get('chat_id', ''),
                            'expires_at': current_time + result['data']['expire'],
                            'auth_time': current_time
                        }

                        with open(config_path, 'w') as f:
                            json.dump(new_config, f, indent=2, ensure_ascii=False)

                        expire_hours = result['data']['expire'] // 3600

                        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>授权成功</title>
    <style>
        body {{ font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f5f5f5; }}
        .container {{ text-align: center; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #52c41a; }}
        .info {{ text-align: left; margin: 20px 0; padding: 15px; background: #f6f6f6; border-radius: 4px; }}
        .token {{ font-family: monospace; font-size: 12px; word-break: break-all; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>✅ 授权成功!</h1>
        <div class="info">
            <p><strong>访问令牌:</strong></p>
            <p class="token">{result['data']['access_token'][:50]}...</p>
            <p><strong>有效期:</strong> {expire_hours} 小时</p>
            <p><strong>配置文件:</strong> {config_path}</p>
        </div>
        <p>请关闭此页面并返回终端</p>
    </div>
</body>
</html>
                        """
                        self.wfile.write(html.encode('utf-8'))

                        # 输出到控制台
                        print(f"\n" + "=" * 60)
                        print(f"授权成功!")
                        print(f"=" * 60)
                        print(f"user_access_token: {result['data']['access_token'][:30]}...")
                        print(f"refresh_token: {result['data']['refresh_token'][:30]}...")
                        print(f"有效期: {expire_hours} 小时")
                        print(f"配置已保存到: {config_path}")

                    else:
                        print(f"授权失败: {result}")
                        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>授权失败</title>
</head>
<body>
    <h1>授权失败</h1>
    <p>错误: {result.get('msg')}</p>
</body>
</html>
                        """
                        self.wfile.write(html.encode('utf-8'))

                except Exception as e:
                    print(f"授权异常: {e}")
                    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>授权失败</title>
</head>
<body>
    <h1>授权失败</h1>
    <p>错误: {str(e)}</p>
</body>
</html>
                    """
                    self.wfile.write(html.encode('utf-8'))
                return
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>授权取消</title>
</head>
<body>
    <h1>授权已取消</h1>
    <p>请重新运行脚本进行授权</p>
</body>
</html>
                """
                self.wfile.write(html.encode('utf-8'))
                return

        # 根路径返回说明
        if parsed.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>飞书授权服务</title>
    <style>
        body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f5f5f5; }
        .container { text-align: center; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .btn { display: inline-block; padding: 12px 24px; background: #3370ff; color: white; text-decoration: none; border-radius: 4px; margin: 10px 0; }
        .btn:hover { background: #295ac8; }
    </style>
</head>
<body>
    <div class="container">
        <h1>飞书授权服务</h1>
        <p>点击下方按钮开始授权</p>
        <a href=\"""" + AUTH_URL + """\" class=\"btn\">前往飞书授权</a>
    </div>
</body>
</html>
            """
            self.wfile.write(html.encode('utf-8'))
            return


def main():
    print("=" * 60)
    print("飞书 OAuth 授权")
    print("=" * 60)
    if not APP_ID or not APP_SECRET:
        print("❌ 缺少 FEISHU_APP_ID / FEISHU_APP_SECRET（或 LARK_ 前缀）")
        print("请先在 /Users/echo/.dms.env 中设置，然后再运行授权脚本。")
        return

    global AUTH_URL
    encoded_redirect = quote(REDIRECT_URI, safe="")
    AUTH_URL = f"https://open.feishu.cn/open-apis/authen/v1/authorize?app_id={APP_ID}&redirect_uri={encoded_redirect}&scope=bitable:app&state=feishu_auth"
    print(f"\n应用 ID: {APP_ID}")
    print(f"回调地址: {REDIRECT_URI}")

    # 启动本地服务器
    print("\n正在启动授权服务器...")
    server = HTTPServer(('localhost', 18080), CallbackHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    print(f"✅ 服务器已启动: http://localhost:18080")

    # 自动打开浏览器
    print("\n正在打开浏览器...")
    webbrowser.open("http://localhost:18080")

    print("\n请在浏览器中完成授权...")
    print("提示：如果浏览器没有自动打开，请手动访问: http://localhost:18080")
    print("\n按 Ctrl+C 退出服务器")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n已退出")
        server.shutdown()


if __name__ == "__main__":
    main()
