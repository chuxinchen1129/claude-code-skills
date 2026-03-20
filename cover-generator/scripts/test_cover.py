#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版封面生成器 - 用于测试
"""

import sys
from pathlib import Path

# 测试封面生成功能
def test_cover_generation():
    """测试封面生成"""

    # 参数
    chinese_title = "2026智驾未来AI重塑汽车消费"
    english_title = "AI RESHAPING AUTOMOTIVE CONSUMPTION"
    year = 2026
    source = "艺恩"

    # 生成HTML
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{chinese_title}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #f5f5f5;
        }}
        .cover {{
            width: 540px;
            height: 720px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            color: white;
            border: 4px solid #1a1a1a;
        }}
        .year {{
            font-size: 32px;
            font-weight: 900;
            letter-spacing: 8px;
            margin-bottom: 20px;
        }}
        .title {{
            font-size: 48px;
            font-weight: 900;
            line-height: 1.2;
            margin-bottom: 40px;
        }}
        .english {{
            font-size: 20px;
            font-weight: 600;
            letter-spacing: 4px;
            text-transform: uppercase;
            margin-top: auto;
        }}
        .footer {{
            font-size: 16px;
            text-align: center;
            border-top: 2px solid white;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="cover">
        <div class="year">{year}</div>
        <div class="title">{chinese_title}</div>
        <div class="english">{english_title}</div>
        <div class="footer">
            {source} | 行业趋势报告
        </div>
    </div>
</body>
</html>"""

    # 保存HTML
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    html_path = output_dir / "test_cover.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ 测试封面已生成: {html_path}")
    print(f"\n💡 提示: 在浏览器中打开查看效果")
    print(f"   file://{html_path.absolute()}")

    return True


if __name__ == '__main__':
    test_cover_generation()
