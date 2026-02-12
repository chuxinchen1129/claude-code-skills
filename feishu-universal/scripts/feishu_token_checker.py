#!/usr/bin/env python3
"""
飞书 Token 有效期检查和提醒脚本
定期检查 refresh_token 是否即将过期，提前提醒用户

建议：每周运行一次，或添加到 crontab 自动运行
"""

import json
import os
import time
from datetime import datetime, timedelta


def check_token_status():
    """检查 token 状态"""
    config_path = os.path.expanduser("~/.feishu_user_config.json")

    if not os.path.exists(config_path):
        print("❌ 配置文件不存在，请先完成 OAuth 授权")
        print("   运行: python3 test_feishu_oauth.py")
        return False

    with open(config_path, 'r') as f:
        config = json.load(f)

    # 获取过期时间
    expires_at = config.get('expires_at', 0)
    user_open_id = config.get('user_open_id', 'unknown')

    # refresh_token 的有效期是 30 天
    # expires_at 是 user_access_token 的过期时间（2小时）
    # 我们需要追踪 refresh_token 的授权时间

    # 检查是否有授权时间记录
    auth_time = config.get('auth_time', 0)
    if auth_time == 0:
        # 如果没有记录，从当前时间开始
        auth_time = int(time.time())
        config['auth_time'] = auth_time
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    # refresh_token 有效期 30 天
    refresh_expires_at = auth_time + 30 * 24 * 60 * 60
    now = int(time.time())

    # 计算剩余天数
    remaining_days = (refresh_expires_at - now) / (24 * 60 * 60)

    print("=" * 60)
    print("飞书 Token 状态检查")
    print("=" * 60)
    print(f"\n用户 ID: {user_open_id}")
    print(f"授权时间: {datetime.fromtimestamp(auth_time).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"refresh_token 过期时间: {datetime.fromtimestamp(refresh_expires_at).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"剩余天数: {remaining_days:.1f} 天")

    # 状态判断
    if remaining_days < 0:
        print("\n❌ refresh_token 已过期！")
        print("\n请立即重新授权:")
        print("  python3 test_feishu_oauth.py")
        return False

    elif remaining_days < 3:
        print(f"\n⚠️  警告：refresh_token 即将过期（剩余 {remaining_days:.1f} 天）")
        print("\n请在 3 天内重新授权:")
        print("  python3 test_feishu_oauth.py")
        return False

    elif remaining_days < 7:
        print(f"\n⚠️  提醒：refresh_token 将在 {remaining_days:.1f} 天后过期")
        print("\n建议本周内重新授权:")
        print("  python3 test_feishu_oauth.py")
        return True

    else:
        print(f"\n✅ Token 状态良好，剩余 {remaining_days:.1f} 天")
        return True


def main():
    """主流程"""
    is_valid = check_token_status()

    print("\n" + "=" * 60)
    if is_valid:
        print("✅ Token 有效，可以正常使用")
    else:
        print("⚠️  需要重新授权")
    print("=" * 60)

    return is_valid


if __name__ == "__main__":
    import sys
    is_valid = main()
    sys.exit(0 if is_valid else 1)
