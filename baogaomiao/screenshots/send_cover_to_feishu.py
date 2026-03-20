#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发送封面到飞书"""

import sys
from pathlib import Path

# 添加脚本目录到路径
script_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(script_dir))

from feishu_sender import FeishuSender

cover_path = "/Users/echo/DMS/skills/baogaomiao/screenshots/editorial_AI短剧_完整版_0320.png"

print(f"发送封面: {cover_path}")

sender = FeishuSender()
result = sender.send_screenshots([cover_path])

if result['success']:
    print(f"✅ {result['message']}")
else:
    print(f"❌ 发送失败: {result.get('error', '未知')}")
    sys.exit(1)