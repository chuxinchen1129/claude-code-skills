#!/usr/bin/env python3
"""
飞书 OAuth 授权脚本 - 使用已配置的 redirect_uri
"""
import json
import time
import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
import webbrowser
import threading
import requests
import sys

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/feishu_auth_final.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 飞书应用配置（从环境变量读取）
APP_ID = os.getenv("FEISHU_APP_ID") or os.getenv("LARK_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET") or os.getenv("LARK_APP_SECRET")

# 使用已配置的 redirect_uri
REDIRECT_URI = "http://localhost:18080"

AUTH_URL = None


class CallbackHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info(f"[HTTP] {format % args}")

    def do_GET(self):
        parsed = urlparse(self.path)
        logger.info(f"收到请求: {parsed.path}")
        params = parse_qs(parsed.query)

        # 根路径返回说明（仅在没有 code 时）
        if parsed.path == '/' and 'code' not in params:
            logger.info("访问根路径，返回授权页面")
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>飞书授权服务</title>
    <style>
        body {{ font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f5f5f5; }}
        .container {{ text-align: center; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
        .btn {{ display: inline-block; padding: 12px 24px; background: #3370ff; color: white; text-decoration: none; border-radius: 4px; margin: 10px 0; }}
        .btn:hover {{ background: #295ac8; }}
        .url {{ font-size: 11px; color: #666; word-break: break-all; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>飞书授权服务</h1>
        <p>点击下方按钮开始授权</p>
        <a href="{AUTH_URL}" class="btn">前往飞书授权</a>
        <p class="url">授权URL: {AUTH_URL}</p>
        <p class="url">redirect_uri: {REDIRECT_URI}</p>
    </div>
</body>
</html>
            """
            self.wfile.write(html.encode('utf-8'))
            return

        # 回调处理（无论是否带 /callback，只要有 code 就处理）
        if 'code' in params:
            code = params['code'][0]
            logger.info(f"收到回调请求，query: {parsed.query}")
            params = parse_qs(parsed.query)
            logger.info(f"解析参数: {params}")

            if 'code' in params:
                code = params['code'][0]
                logger.info(f"✅ 获取到授权码: {code[:20]}...")

                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()

                # 用授权码获取 token
                try:
                    logger.info("正在交换授权码获取 token...")

                    # 首先获取 tenant_access_token
                    tenant_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
                    headers = {'Content-Type': 'application/json; charset=utf-8'}
                    tenant_data = {
                        'app_id': APP_ID,
                        'app_secret': APP_SECRET
                    }

                    tenant_response = requests.post(tenant_url, headers=headers, json=tenant_data, timeout=10)
                    tenant_result = tenant_response.json()

                    if tenant_result.get('code') != 0:
                        raise Exception(f"获取 tenant_access_token 失败: {tenant_result.get('msg')}")

                    tenant_token = tenant_result['tenant_access_token']
                    logger.info(f"✅ tenant_access_token 获取成功")

                    # 使用 tenant_access_token 交换 user_access_token
                    url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
                    headers = {
                        'Content-Type': 'application/json; charset=utf-8',
                        'Authorization': f'Bearer {tenant_token}'
                    }
                    data = {
                        'app_id': APP_ID,
                        'app_secret': APP_SECRET,
                        'grant_type': 'authorization_code',
                        'code': code
                    }

                    response = requests.post(url, headers=headers, json=data, timeout=10)
                    result = response.json()
                    logger.info(f"API 响应: {result}")

                    if result.get('code') == 0:
                        logger.info("✅ Token 获取成功!")
                        # 保存 token
                        config_path = "/Users/echo/.feishu_user_config.json"
                        current_time = int(time.time())

                        expires_in = result['data'].get('expires_in', 7200)  # 默认7200秒（2小时）

                        new_config = {
                            'app_id': APP_ID,
                            'app_secret': APP_SECRET,
                            'user_access_token': result['data']['access_token'],
                            'refresh_token': result['data']['refresh_token'],
                            'user_open_id': result['data'].get('open_id', ''),
                            'chat_id': result['data'].get('chat_id', ''),
                            'expires_at': current_time + expires_in,
                            'auth_time': current_time
                        }

                        with open(config_path, 'w') as f:
                            json.dump(new_config, f, indent=2, ensure_ascii=False)
                        logger.info(f"✅ 配置已保存到: {config_path}")

                        expire_hours = expires_in // 3600

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
            <p><strong>授权时间:</strong> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}</p>
        </div>
        <p>请关闭此页面并返回终端</p>
    </div>
</body>
</html>
                        """
                        self.wfile.write(html.encode('utf-8'))

                        # 输出到控制台
                        print(f"\n" + "=" * 60)
                        print(f"✅ 授权成功!")
                        print(f"=" * 60)
                        print(f"user_access_token: {result['data']['access_token'][:30]}...")
                        print(f"有效期: {expire_hours} 小时")
                        print(f"配置已保存到: {config_path}")
                        print(f"=" * 60)

                    else:
                        logger.error(f"❌ Token 获取失败: {result}")
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
    <p>错误码: {result.get('code')}</p>
</body>
</html>
                        """
                        self.wfile.write(html.encode('utf-8'))

                except Exception as e:
                    logger.exception("Token 交换异常")
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
            else:
                logger.warning("回调中没有 code 参数")
                logger.info(f"完整参数: {params}")
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
        else:
            logger.warning(f"未知路径: {parsed.path}")
            self.send_response(404)
            self.end_headers()


def main():
    logger.info("=" * 60)
    logger.info("飞书 OAuth 授权")
    logger.info("=" * 60)
    if not APP_ID or not APP_SECRET:
        logger.error("缺少 FEISHU_APP_ID / FEISHU_APP_SECRET（或 LARK_ 前缀）")
        logger.error("请先在 /Users/echo/.dms.env 中设置，然后再运行授权脚本。")
        return

    global AUTH_URL
    encoded_redirect = quote(REDIRECT_URI, safe="")
    AUTH_URL = f"https://open.feishu.cn/open-apis/authen/v1/authorize?app_id={APP_ID}&redirect_uri={encoded_redirect}&scope=bitable:app&state=feishu_auth"
    logger.info(f"应用 ID: {APP_ID}")
    logger.info(f"回调地址: {REDIRECT_URI}")
    logger.info(f"授权URL: {AUTH_URL}")

    # 启动本地服务器
    logger.info("正在启动授权服务器...")
    server = HTTPServer(('localhost', 18080), CallbackHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    logger.info(f"✅ 服务器已启动: http://localhost:18080")

    # 自动打开浏览器
    logger.info("正在打开浏览器...")
    webbrowser.open("http://localhost:18080")

    logger.info("请在浏览器中完成授权...")
    logger.info("提示：如果浏览器没有自动打开，请手动访问: http://localhost:18080")
    logger.info("按 Ctrl+C 退出服务器")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("正在关闭服务器...")
        server.shutdown()
        logger.info("服务器已关闭")


if __name__ == "__main__":
    main()
