#!/usr/bin/env python3
"""
飞书配置检查脚本 v3.0
检查 tenant_access_token 配置是否正确
"""

import json
import os
import requests


def check_config():
    """检查配置和 tenant_token"""
    config_path = os.path.expanduser("~/.feishu_user_config.json")

    if not os.path.exists(config_path):
        print("❌ 配置文件不存在")
        print("   请确保 ~/.feishu_user_config.json 存在")
        return False

    with open(config_path, 'r') as f:
        config = json.load(f)

    print("=" * 60)
    print("飞书配置检查 v3.0")
    print("=" * 60)

    # 检查必需字段
    app_id = config.get('app_id')
    app_secret = config.get('app_secret')
    user_open_id = config.get('user_open_id')
    chat_id = config.get('chat_id')
    target_table = config.get('target_table', {})

    print(f"\n✓ 配置文件加载成功")
    print(f"  App ID: {app_id}")
    print(f"  User Open ID: {user_open_id}")
    print(f"  Chat ID: {chat_id}")
    print(f"  Folder Token: {config.get('folder_token', '未设置')}")
    print(f"  目标表格: {target_table.get('name', '未设置')}")

    if target_table:
        print(f"    - App Token: {target_table.get('app_token', '未设置')}")
        print(f"    - Table ID: {target_table.get('table_id', '未设置')}")

    # 检查旧字段是否存在（警告）
    if 'user_access_token' in config or 'refresh_token' in config:
        print("\n⚠️  检测到旧配置字段（user_access_token/refresh_token）")
        print("   这些字段已不再使用，可以安全删除")

    # 测试 tenant_token 获取
    print(f"\n🔧 测试 tenant_access_token 获取...")
    try:
        url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
        payload = {"app_id": app_id, "app_secret": app_secret}
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                token = data.get("app_access_token")
                print(f"✓ Tenant Token 获取成功")
                print(f"  Token: {token[:30]}...")
                print(f"  类型: tenant_access_token (app_access_token/internal)")
                return True
            else:
                print(f"✗ Token 获取失败: {data.get('msg')}")
                return False
        else:
            print(f"✗ 请求失败: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def main():
    """主流程"""
    success = check_config()

    print("\n" + "=" * 60)
    if success:
        print("✅ 配置检查通过，飞书自动化功能可用")
        print("\n使用方法:")
        print("  python3 feishu_user_auto.py test")
        print("  python3 feishu_user_auto.py import-to-target --excel data.xlsx")
    else:
        print("⚠️  配置检查失败，请检查配置文件")
    print("=" * 60)

    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
