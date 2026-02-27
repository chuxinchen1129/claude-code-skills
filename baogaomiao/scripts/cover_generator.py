#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书封面图生成器

功能：
1. 生成小红书风格的封面图
2. 大标题、醒目配色、吸引眼球
3. 支持多种风格配色
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow 未安装，请运行: pip3 install Pillow")
    raise


class XHSCoverGenerator:
    """小红书封面图生成器"""

    # 封面尺寸（3:4 比例，小红书标准）
    WIDTH = 1080
    HEIGHT = 1440

    # 配色方案（渐变色）
    COLOR_SCHEMES = {
        "warm": {
            "bg_top": (255, 107, 107),    # 珊瑚红
            "bg_bottom": (255, 184, 76),  # 金橙色
            "accent": (255, 255, 255),    # 白色
            "text": (255, 255, 255),      # 白色
        },
        "cool": {
            "bg_top": (66, 165, 245),     # 天蓝色
            "bg_bottom": (114, 159, 255), # 靛蓝色
            "accent": (255, 255, 255),
            "text": (255, 255, 255),
        },
        "purple": {
            "bg_top": (124, 93, 250),     # 紫色（悟昕品牌色）
            "bg_bottom": (168, 153, 255), # 淡紫色
            "accent": (255, 255, 255),
            "text": (255, 255, 255),
        },
        "green": {
            "bg_top": (52, 168, 83),      # 绿色
            "bg_bottom": (102, 205, 137), # 清新绿
            "accent": (255, 255, 255),
            "text": (255, 255, 255),
        },
        "pink": {
            "bg_top": (255, 128, 171),    # 粉色
            "bg_bottom": (255, 182, 213), # 淡粉色
            "accent": (255, 255, 255),
            "text": (255, 255, 255),
        },
    }

    def __init__(self, output_dir: Optional[Path] = None):
        """
        初始化封面图生成器

        Args:
            output_dir: 输出目录（默认为技能目录下的 covers/）
        """
        if output_dir is None:
            script_dir = Path(__file__).parent
            output_dir = script_dir / "covers"

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 加载字体
        self._load_fonts()

    def _load_fonts(self):
        """加载中文字体"""
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/Arial Unicode.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
        ]

        self.font_title = None
        self.font_subtitle = None
        self.font_tag = None

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    self.font_title = ImageFont.truetype(font_path, 120)
                    self.font_subtitle = ImageFont.truetype(font_path, 60)
                    self.font_tag = ImageFont.truetype(font_path, 48)
                    break
                except Exception:
                    continue

        if self.font_title is None:
            default_font = ImageFont.load_default()
            self.font_title = default_font
            self.font_subtitle = default_font
            self.font_tag = default_font

    def generate_cover(
        self,
        chinese_title: str,
        english_title: str = "",
        source: str = "",
        year: str = "",
        color_scheme: str = "purple",
        emoji: str = "🎯",
        tag: str = "",
        output_filename: Optional[str] = None
    ) -> Dict:
        """
        生成小红书封面图

        Args:
            chinese_title: 中文标题（主要）
            english_title: 英文标题（可选）
            source: 来源/机构名称
            year: 年份
            color_scheme: 配色方案（warm/cool/purple/green/pink）
            emoji: 装饰emoji
            tag: 标签（如"报告解读"、"行业分析"）
            output_filename: 输出文件名

        Returns:
            结果字典：{'success': True/False, 'path': Path, 'message': str}
        """
        try:
            # 获取配色
            colors = self.COLOR_SCHEMES.get(color_scheme, self.COLOR_SCHEMES["purple"])

            # 创建图片
            img = Image.new('RGB', (self.WIDTH, self.HEIGHT))
            draw = ImageDraw.Draw(img)

            # 绘制渐变背景
            self._draw_gradient(draw, img, colors["bg_top"], colors["bg_bottom"])

            # 添加装饰图案（几何元素）
            self._draw_decorations(draw, colors)

            # 绘制顶部标签
            if tag:
                self._draw_tag(draw, tag, colors)

            # 绘制emoji（大）
            emoji_y = 200
            # 尝试使用emoji字体，如果失败则跳过
            try:
                emoji_font_path = "/System/Library/Fonts/Apple Color Emoji.ttc"
                if os.path.exists(emoji_font_path):
                    emoji_font = ImageFont.truetype(emoji_font_path, 150)
                    draw.text((self.WIDTH // 2, emoji_y), emoji, font=emoji_font, anchor="mm")
                else:
                    # emoji字体不可用，跳过绘制
                    pass
            except Exception:
                # emoji绘制失败，跳过
                pass

            # 绘制中文标题（大）
            title_y = 500
            self._draw_title(draw, chinese_title, title_y, colors)

            # 绘制英文标题
            if english_title:
                subtitle_y = title_y + 250
                self._draw_subtitle(draw, english_title, subtitle_y, colors)

            # 绘制底部信息
            self._draw_footer(draw, source, year, colors)

            # 生成文件名
            if output_filename is None:
                title_slug = self._sanitize_filename(chinese_title[:15])
                output_filename = f"xhs_cover_{title_slug}.png"

            output_path = self.output_dir / output_filename
            img.save(output_path, "PNG", dpi=(300, 300))

            return {
                'success': True,
                'path': output_path,
                'message': f'✓ 小红书封面已生成: {output_filename}'
            }

        except Exception as e:
            return {
                'success': False,
                'path': None,
                'message': f'封面生成失败: {e}'
            }

    def _draw_gradient(self, draw, img, color_top, color_bottom):
        """绘制渐变背景"""
        for y in range(self.HEIGHT):
            ratio = y / self.HEIGHT
            r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
            g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
            b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
            draw.rectangle([(0, y), (self.WIDTH, y + 1)], fill=(r, g, b))

    def _draw_decorations(self, draw, colors):
        """绘制装饰图案"""
        # 圆形装饰
        draw.ellipse([(-100, -100), (300, 300)], fill=(*colors["accent"], 50))
        draw.ellipse([(self.WIDTH - 300, self.HEIGHT - 300), (self.WIDTH + 100, self.HEIGHT + 100)], fill=(*colors["accent"], 50))

        # 线条装饰
        draw.line([(100, 1500), (300, 1300)], fill=(*colors["accent"], 100), width=5)
        draw.line([(self.WIDTH - 300, 100), (self.WIDTH - 100, 300)], fill=(*colors["accent"], 100), width=5)

    def _draw_tag(self, draw, tag, colors):
        """绘制顶部标签"""
        padding_x = 40
        padding_y = 15

        # 计算标签大小
        bbox = self.font_tag.getbbox(tag)
        tag_width = bbox[2] - bbox[0] + 2 * padding_x

        # 居中
        x = (self.WIDTH - tag_width) // 2
        y = 80

        # 绘制标签背景（圆角矩形）
        draw.rounded_rectangle(
            [(x, y), (x + tag_width, y + bbox[3] - bbox[1] + 2 * padding_y)],
            radius=20,
            fill=(*colors["accent"], 180)
        )

        # 绘制标签文字
        text_x = x + padding_x
        text_y = y + padding_y - 5
        draw.text((text_x, text_y), tag, fill=colors["text"], font=self.font_tag)

    def _draw_title(self, draw, title, y, colors):
        """绘制主标题（自动换行）"""
        # 移除emoji前缀
        clean_title = title
        for emoji in ["🎯", "🍼", "📊", "🚀", "💡", "✨", "🔥", "💪", "⭐"]:
            clean_title = clean_title.replace(emoji, "")

        # 分行处理
        max_width = self.WIDTH - 160
        lines = self._wrap_text(clean_title, max_width, self.font_title)

        # 居中绘制
        for i, line in enumerate(lines):
            bbox = self.font_title.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (self.WIDTH - text_width) // 2
            draw.text((x, y + i * 140), line, fill=colors["text"], font=self.font_title)

    def _draw_subtitle(self, draw, subtitle, y, colors):
        """绘制副标题"""
        max_width = self.WIDTH - 160
        lines = self._wrap_text(subtitle, max_width, self.font_subtitle)

        for i, line in enumerate(lines[:2]):  # 最多2行
            bbox = self.font_subtitle.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (self.WIDTH - text_width) // 2
            draw.text((x, y + i * 80), line, fill=(*colors["text"], 200), font=self.font_subtitle)

    def _draw_footer(self, draw, source, year, colors):
        """绘制底部信息"""
        y = self.HEIGHT - 120

        parts = []
        if source:
            parts.append(f"📊 {source}")
        if year:
            parts.append(f"📅 {year}")

        if parts:
            text = "  ·  ".join(parts)
            bbox = self.font_subtitle.getbbox(text)
            text_width = bbox[2] - bbox[0]
            x = (self.WIDTH - text_width) // 2
            draw.text((x, y), text, fill=(*colors["text"], 180), font=self.font_subtitle)

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
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub('', text)
        return text.replace(' ', '_')[:30]


# ==================== 命令行接口 ====================

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='小红书封面图生成器')
    parser.add_argument('--chinese-title', required=True, help='中文标题')
    parser.add_argument('--english-title', help='英文标题')
    parser.add_argument('--source', help='来源/机构名称')
    parser.add_argument('--year', help='年份')
    parser.add_argument('--color', default='purple', choices=['warm', 'cool', 'purple', 'green', 'pink'], help='配色方案')
    parser.add_argument('--emoji', default='🎯', help='装饰emoji')
    parser.add_argument('--tag', help='顶部标签')
    parser.add_argument('--output', help='输出文件名')

    args = parser.parse_args()

    generator = XHSCoverGenerator()
    result = generator.generate_cover(
        chinese_title=args.chinese_title,
        english_title=args.english_title or "",
        source=args.source or "",
        year=args.year or "",
        color_scheme=args.color,
        emoji=args.emoji,
        tag=args.tag or "",
        output_filename=args.output
    )

    print(f"\n{result['message']}")
    if result['success']:
        print(f"  路径: {result['path']}")


if __name__ == '__main__':
    main()
