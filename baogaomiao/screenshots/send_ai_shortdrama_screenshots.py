#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发送AI短剧报告6张截图到飞书"""

import sys
import glob
from pathlib import Path

# 添加脚本目录到路径
script_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(script_dir))

from feishu_sender import FeishuSender

# 获取最新的6张AI短剧报告截图
screenshots_dir = Path("/Users/echo/DMS/skills/baogaomiao/screenshots")
screenshot_files = sorted(screenshots_dir.glob("0320-2026PDF内容总结*.png"))

# 取最新的6张
latest_screenshots = screenshot_files[-6:] if len(screenshot_files) >= 6 else screenshot_files

print(f"准备发送 {len(latest_screenshots)} 张AI短剧报告截图")

# 发送到飞书
sender = FeishuSender()
result = sender.send_screenshots([str(f) for f in latest_screenshots])

if result['success']:
    print(f"✅ {result['message']}")
else:
    print(f"❌ 发送失败: {result.get('error', '未知')}")
    sys.exit(1)