#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速发送图片到飞书
"""

import os
from pathlib import Path

# 动态获取用户目录
USER_HOME = str(Path.home())

# 切换到正确的目录
os.chdir(f'{USER_HOME}/Desktop/DMS/skills/baogaomiao/scripts')

# 添加 feishu-universal 路径
sys.path.insert(0, f'{USER_HOME}/Desktop/DMS/skills/feishu-universal/scripts')

# 导入 FeishuBotNotifier
from feishu_bot_notifier import FeishuBotNotifier

def send_image(image_path):
    """发送单张图片到飞书"""
    notifier = FeishuBotNotifier()
    image_key = notifier.upload_image(image_path, max_retries=3)
    if image_key:
        print(f"✅ 图片已发送到飞书")
        print(f"   image_key: {image_key}")
        return True
    else:
        print(f"❌ 图片发送失败")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 quick_send.py <图片路径>")
        sys.exit(1)

    image_path = sys.argv[1]
    send_image(image_path)
