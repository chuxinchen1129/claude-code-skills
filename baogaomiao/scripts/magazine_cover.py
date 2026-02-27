#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
杂志封面风生成器

特点：
- 大标题排版
- 留白设计
- 高级感
- 单色背景 + 强调色
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow 未安装，请运行: pip3 install Pillow")
    raise


class MagazineCoverGenerator:
    """杂志封面风生成器"""

    # 封面尺寸
    WIDTH = 1080
    HEIGHT = 1440

    # 配色方案
    COLOR_SCHEMES = {
        "minimal": {
            "bg": (245, 245, 245),       # 浅灰
            "title": (30, 30, 30),       # 深黑
            "accent": (200, 50, 50),     # 强调红
            "meta": (120, 120, 120),     # 灰色
        },
        "elegant": {
            "bg": (250, 248, 245),       # 米白
            "title": (20, 20, 20),       # 黑
            "accent": (124, 93, 250),    # 紫色（悟昕）
            "meta": (100, 100, 100),
        },
        "bold": {
            "bg": (30, 30, 30),          # 深黑
            "title": (255, 255, 255),    # 白
            "accent": (255, 184, 76),    # 金色
            "meta": (180, 180, 180),
        },
        "fresh": {
            "bg": (240, 252, 245),       # 淡绿
            "title": (20, 60, 40),       # 深绿
            "accent": (52, 168, 83),     # 绿色
            "meta": (80, 120, 100),
        },
    }

    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            script_dir = Path(__file__).parent
            output_dir = script_dir / "covers"

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._load_fonts()

    def _load_fonts(self):
        """加载字体"""
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/Arial Unicode.ttf",
        ]

        self.font_title = None
        self.font_subtitle = None
        self.font_meta = None

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    self.font_title = ImageFont.truetype(font_path, 100)
                    self.font_subtitle = ImageFont.truetype(font_path, 48)
                    self.font_meta = ImageFont.truetype(font_path, 36)
                    break
                except Exception:
                    continue

        if self.font_title is None:
            default_font = ImageFont.load_default()
            self.font_title = default_font
            self.font_subtitle = default_font
            self.font_meta = default_font

    def generate_cover(
        self,
        chinese_title: str,
        english_title: str = "",
        source: str = "",
        year: str = "",
        issue: str = "",
        color_scheme: str = "elegant",
        tag: str = "",
        output_filename: Optional[str] = None
    ) -> Dict:
        """生成杂志封面"""
        try:
            colors = self.COLOR_SCHEMES.get(color_scheme, self.COLOR_SCHEMES["elegant"])

            # 创建图片
            img = Image.new('RGB', (self.WIDTH, self.HEIGHT), colors["bg"])
            draw = ImageDraw.Draw(img)

            # 绘制装饰线条
            self._draw_decorations(draw, colors)

            # 顶部标签区域
            if tag or source:
                self._draw_header(draw, tag, source, colors)

            # 主标题区域（居中大）
            self._draw_title(draw, chinese_title, colors)

            # 副标题
            if english_title:
                self._draw_subtitle(draw, english_title, colors)

            # 底部信息
            self._draw_footer(draw, year, issue, colors)

            # 文件名
            if output_filename is None:
                title_slug = self._sanitize_filename(chinese_title[:15])
                output_filename = f"magazine_{title_slug}.png"

            output_path = self.output_dir / output_filename
            img.save(output_path, "PNG", dpi=(300, 300))

            return {
                'success': True,
                'path': output_path,
                'message': f'✓ 杂志封面已生成: {output_filename}'
            }

        except Exception as e:
            return {
                'success': False,
                'path': None,
                'message': f'封面生成失败: {e}'
            }

    def _draw_decorations(self, draw, colors):
        """绘制装饰元素"""
        # 顶部细线
        draw.line([(80, 120), (self.WIDTH - 80, 120)], fill=colors["accent"], width=3)

        # 底部细线
        draw.line([(80, self.HEIGHT - 120), (self.WIDTH - 80, self.HEIGHT - 120)], fill=colors["accent"], width=3)

        # 右上角方块装饰
        size = 60
        draw.rectangle(
            [(self.WIDTH - 80 - size, 80), (self.WIDTH - 80, 80 + size)],
            outline=colors["accent"],
            width=2
        )

    def _draw_header(self, draw, tag, source, colors):
        """绘制头部信息"""
        y = 150

        if tag:
            # 标签
            draw.text((80, y), tag.upper(), fill=colors["accent"], font=self.font_meta)
            y += 50

        if source:
            # 来源
            draw.text((80, y), source, fill=colors["meta"], font=self.font_meta)

    def _draw_title(self, draw, title, colors):
        """绘制主标题"""
        # 移除emoji
        clean_title = title
        for emoji in ["🎯", "🍼", "📊", "🚀", "💡", "✨", "🔥", "💪", "⭐"]:
            clean_title = clean_title.replace(emoji, "")

        # 垂直居中区域
        center_y = self.HEIGHT // 2 - 50

        # 分行
        max_width = self.WIDTH - 160
        lines = self._wrap_text(clean_title, max_width, self.font_title)

        # 计算总高度
        total_height = len(lines) * 130

        # 起始Y坐标（垂直居中）
        start_y = center_y - total_height // 2

        # 绘制每一行
        for i, line in enumerate(lines):
            bbox = self.font_title.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (self.WIDTH - text_width) // 2
            draw.text((x, start_y + i * 130), line, fill=colors["title"], font=self.font_title)

    def _draw_subtitle(self, draw, subtitle, colors):
        """绘制副标题"""
        center_y = self.HEIGHT // 2 + 200

        max_width = self.WIDTH - 200
        lines = self._wrap_text(subtitle, max_width, self.font_subtitle)

        for i, line in enumerate(lines[:2]):
            bbox = self.font_subtitle.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (self.WIDTH - text_width) // 2
            draw.text((x, center_y + i * 70), line, fill=colors["meta"], font=self.font_subtitle)

    def _draw_footer(self, draw, year, issue, colors):
        """绘制底部信息"""
        y = self.HEIGHT - 100
        x = 80

        parts = []
        if year:
            parts.append(f"YEAR {year}")
        if issue:
            parts.append(f"NO.{issue}")

        if parts:
            text = "  |  ".join(parts)
            draw.text((x, y), text, fill=colors["meta"], font=self.font_meta)

        # 页码装饰
        page_num = "01"
        bbox = self.font_meta.getbbox(page_num)
        page_width = bbox[2] - bbox[0]
        draw.text((self.WIDTH - 80 - page_width, y), page_num, fill=colors["accent"], font=self.font_meta)

    def _wrap_text(self, text, max_width, font):
        """文本换行"""
        lines = []
        words = list(text)

        current_line = ""
        for word in words:
            test_line = current_line + word
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def _sanitize_filename(self, text):
        """清理文件名"""
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub('', text)
        return text.replace(' ', '_')[:30]


def main():
    import argparse

    parser = argparse.ArgumentParser(description='杂志封面风生成器')
    parser.add_argument('--chinese-title', required=True, help='中文标题')
    parser.add_argument('--english-title', help='英文标题')
    parser.add_argument('--source', help='来源/机构')
    parser.add_argument('--year', help='年份')
    parser.add_argument('--issue', help='期号')
    parser.add_argument('--color', default='elegant', choices=['minimal', 'elegant', 'bold', 'fresh'], help='配色方案')
    parser.add_argument('--tag', help='顶部标签')
    parser.add_argument('--output', help='输出文件名')

    args = parser.parse_args()

    generator = MagazineCoverGenerator()
    result = generator.generate_cover(
        chinese_title=args.chinese_title,
        english_title=args.english_title or "",
        source=args.source or "",
        year=args.year or "",
        issue=args.issue or "",
        color_scheme=args.color,
        tag=args.tag or "",
        output_filename=args.output
    )

    print(f"\n{result['message']}")
    if result['success']:
        print(f"  路径: {result['path']}")


if __name__ == '__main__':
    main()
