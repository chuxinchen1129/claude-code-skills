#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送图片到飞书

简单的工具，直接使用 feishu_sender.py 的 send_screenshots() 方法
"""

import sys
from pathlib import Path

# 导入 feishu_sender
_dms_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_dms_root / 'skills' / 'feishu-universal' / 'scripts'))
from feishu_sender import FeishuSender

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='发送图片到飞书')
    parser.add_argument('image', help='图片文件路径')
    
    args = parser.parse_args()
    
    if not args.image:
        parser.print_help()
        sys.exit(1)
    
    image_path = Path(args.image)
    
    if not image_path.exists():
        print(f"❌ 图片不存在: {image_path}")
        sys.exit(1)
    
    # 使用 FeishuSender 的 send_screenshots 方法
    sender = FeishuSender()
    result = sender.send_screenshots([str(image_path)])
    
    if result['success']:
        print(f"✅ 图片已发送到飞书")
        print(f"   文件: {image_path.name}")
    else:
        print(f"❌ 发送失败: {result.get('error', '未知')}")
        sys.exit(1)

if __name__ == '__main__':
    main()
