#!/usr/bin/env python3
"""
飞书 OAuth 授权脚本 - 尝试多种 redirect_uri
"""
import json
import time
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser
import threading
import requests
import sys

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/feishu_auth_oob.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 飞书应用配置
APP_ID = "cli_a90451f26538dcd6"
APP_SECRET = "3tEvbQEsIzQbkW4oBZEgsTj7PwcpeDve"

# 尝试多种 redirect_uri
REDIRECT_OPTIONS = [
    "http://localhost:18080/callback",
    "http://127.0.0.1:18080/callback",
    "http://localhost:18080",
    "http://127.0.0.1:18080",
]

AUTH_URLS = [
    f"https://open.feishu.cn/open-apis/authen/v1/authorize?app_id={APP_ID}&redirect_uri={uri}&scope=bitable:app&state=feishu_auth"
    for uri in REDIRECT_OPTIONS
]


class ManualCodeHandler(BaseHTTPRequestHandler):
    """手动输入授权码的处理器"""

    def log_message(self, format, *args):
        logger.info(f"[HTTP] {format % args}")

    def do_GET(self):
        parsed = urlparse(self.path)
        logger.info(f"收到请求: {parsed.path}")

        if parsed.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>飞书授权 - 手动输入授权码</title>
    <style>
        body {{ font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f5f5f5; }}
        .container {{ text-align: center; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 600px; }}
        h1 {{ color: #333; }}
        .step {{ margin: 20px 0; padding: 15px; background: #f6f6f6; border-radius: 4px; text-align: left; }}
        .url {{ font-size: 11px; color: #666; word-break: break-all; margin: 10px 0; }}
        .btn {{ display: inline-block; padding: 12px 24px; background: #3370ff; color: white; text-decoration: none; border-radius: 4px; margin: 5px; }}
        .btn:hover {{ background: #295ac8; }}
        input {{ padding: 10px; width: 80%; font-size: 14px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>飞书授权 - 多种方式</h1>

        <div class="step">
            <p><strong>方法1: 点击下方链接授权</strong></p>
            {"".join([f'<a href="{url}" class="btn" target="_blank">选项{i+1}: {uri}</a><br>'
                for i, (url, uri) in enumerate(zip(AUTH_URLS, REDIRECT_OPTIONS))])}
        </div>

        <div class="step">
            <p><strong>方法2: 手动输入授权码</strong></p>
            <p>如果上面链接都失败，请：</p>
            <ol>
                <li>手动访问任一授权链接</li>
                <li>完成授权后，从浏览器地址栏复制授权码</li>
                <li>访问: <a href="http://localhost:18081/input">http://localhost:18081/input</a></li>
                <li>粘贴授权码并提交</li>
            </ol>
        </div>

        <div class="step">
            <p><strong>授权链接（手动复制）:</strong></p>
            <div class="url">{AUTH_URLS[0]}</div>
        </div>
    </div>
</body>
</html>
            """
            self.wfile.write(html.encode('utf-8'))
            return


class CodeInputHandler(BaseHTTPRequestHandler):
    """接收手动输入的授权码"""

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/input':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>输入授权码</title>
    <style>
        body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f5f5f5; }
        .container { text-align: center; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input { padding: 10px; width: 300px; font-size: 14px; margin: 10px 0; }
        button { padding: 12px 24px; background: #3370ff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #295ac8; }
    </style>
</head>
<body>
    <div class="container">
        <h1>输入授权码</h1>
        <form method="POST" action="/input">
            <input type="text" name="code" placeholder="粘贴授权码到这里" required>
            <br>
            <button type="submit">提交</button>
        </form>
    </div>
</body>
</html>
            """
            self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        if parsed.path.startswith('/input'):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)

            if 'code' in params:
                code = params['code'][0]
                logger.info(f"收到手动输入的授权码: {code[:20]}...")

                # 交换 token
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
                    logger.info(f"Token响应: {result}")

                    if result.get('code') == 0:
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

                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>授权成功</title>
</head>
<body>
    <h1>✅ 授权成功!</h1>
    <p>Token已保存到: {config_path}</p>
    <p>有效期: {result['data']['expire']//3600} 小时</p>
    <p>请关闭此页面</p>
</body>
</html>
                        """
                        self.wfile.write(html.encode('utf-8'))
                        logger.info("✅ Token保存成功")
                    else:
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html; charset=utf-8')
                        self.end_headers()
                        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>授权失败</title>
</head>
<body>
    <h1>授权失败</h1>
    <p>错误: {result.get('msg')}</p>
    <p>错误码: {result.get('code')}</p>
</body>
</html>
                        """
                        self.wfile.write(html.encode('utf-8'))
                except Exception as e:
                    logger.exception("Token交换异常")
                    self.send_response(500)
                    self.end_headers()


def main():
    logger.info("=" * 60)
    logger.info("飞书 OAuth 授权 - 多方式尝试")
    logger.info("=" * 60)
    logger.info(f"应用 ID: {APP_ID}")
    logger.info(f"尝试 {len(REDIRECT_OPTIONS)} 种 redirect_uri:")

    for i, uri in enumerate(REDIRECT_OPTIONS):
        logger.info(f"  {i+1}. {uri}")

    # 启动服务器
    server1 = HTTPServer(('localhost', 18080), ManualCodeHandler)
    thread1 = threading.Thread(target=server1.serve_forever)
    thread1.daemon = True
    thread1.start()

    server2 = HTTPServer(('localhost', 18081), CodeInputHandler)
    thread2 = threading.Thread(target=server2.serve_forever)
    thread2.daemon = True
    thread2.start()

    logger.info(f"✅ 服务器已启动:")
    logger.info(f"   - 主页: http://localhost:18080")
    logger.info(f"   - 授权码输入: http://localhost:18081/input")

    webbrowser.open("http://localhost:18080")

    logger.info("请在浏览器中选择授权方式")
    logger.info("按 Ctrl+C 退出")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("正在关闭服务器...")
        server1.shutdown()
        server2.shutdown()
        logger.info("服务器已关闭")


if __name__ == "__main__":
    main()
