#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表格风格封面生成器

参考：用户提供的封面图样式
特点：表格布局、清晰信息、专业报告感
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


class TableCoverGenerator:
    """表格风格封面生成器"""

    # 封面尺寸（宽幅，适合表格展示）
    WIDTH = 1600
    HEIGHT = 900

    # 配色
    COLORS = {
        "bg": (255, 255, 255),           # 白色背景
        "header_bg": (70, 70, 70),        # 深灰表头
        "header_text": (255, 255, 255),  # 白色表头文字
        "row_bg_odd": (245, 245, 245),    # 奇数行浅灰
        "row_bg_even": (255, 255, 255),   # 偶数行白色
        "text": (40, 40, 40),             # 深灰文字
        "border": (200, 200, 200),        # 浅灰边框
        "accent": (124, 93, 250),         # 紫色强调（悟昕品牌）
    }

    # 字体大小
    FONT_HEADER = 32
    FONT_CELL = 28

    # 表格配置
    TABLE_MARGIN_X = 100
    TABLE_MARGIN_Y = 100
    ROW_HEIGHT = 100
    COL_LABEL_WIDTH = 300
    COL_VALUE_WIDTH = 900
    COL_PADDING = 20

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

        self.font_header = None
        self.font_cell = None

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    self.font_header = ImageFont.truetype(font_path, self.FONT_HEADER)
                    self.font_cell = ImageFont.truetype(font_path, self.FONT_CELL)
                    break
                except Exception:
                    continue

        if self.font_header is None:
            default_font = ImageFont.load_default()
            self.font_header = default_font
            self.font_cell = default_font

    def generate_cover(
        self,
        source: str,
        page_count: int,
        chinese_title: str,
        english_title: str,
        year: str,
        number: Optional[str] = None,
        output_filename: Optional[str] = None
    ) -> Dict:
        """
        生成表格风格封面

        Args:
            source: 来源（机构名称）
            page_count: 页数
            chinese_title: 中文标题
            english_title: 英文标题
            year: 年份
            number: 编号（MMDD格式，默认当前日期）
            output_filename: 输出文件名

        Returns:
            结果字典
        """
        try:
            # 生成编号
            if number is None:
                number = datetime.now().strftime("%m%d")

            # 准备表格数据
            data = [
                ("来源", source),
                ("页码", str(page_count)),
                ("中文标题", chinese_title),
                ("英文标题", english_title),
                ("年份", year),
                ("编号", number)
            ]

            # 创建图片
            img = Image.new('RGB', (self.WIDTH, self.HEIGHT), self.COLORS["bg"])
            draw = ImageDraw.Draw(img)

            # 绘制表格
            self._draw_table(draw, data)

            # 生成文件名
            if output_filename is None:
                title_slug = self._sanitize_filename(chinese_title[:15])
                output_filename = f"table_cover_{title_slug}_{number}.png"

            output_path = self.output_dir / output_filename
            img.save(output_path, "PNG", dpi=(300, 300))

            return {
                'success': True,
                'path': output_path,
                'message': f'✓ 表格封面已生成: {output_filename}'
            }

        except Exception as e:
            return {
                'success': False,
                'path': None,
                'message': f'封面生成失败: {e}'
            }

    def _draw_table(self, draw, data):
        """绘制表格"""
        # 计算表格尺寸
        table_width = self.COL_LABEL_WIDTH + self.COL_VALUE_WIDTH
        table_height = len(data) * self.ROW_HEIGHT

        # 表格起始位置（居中）
        table_x = (self.WIDTH - table_width) // 2
        table_y = (self.HEIGHT - table_height) // 2

        # 绘制每一行
        for i, (label, value) in enumerate(data):
            row_y = table_y + i * self.ROW_HEIGHT

            # 行背景
            if i % 2 == 0:
                bg_color = self.COLORS["row_bg_odd"]
            else:
                bg_color = self.COLORS["row_bg_even"]

            draw.rectangle(
                [(table_x, row_y), (table_x + table_width, row_y + self.ROW_HEIGHT)],
                fill=bg_color,
                outline=self.COLORS["border"],
                width=1
            )

            # 标签列（深色背景）
            draw.rectangle(
                [(table_x, row_y), (table_x + self.COL_LABEL_WIDTH, row_y + self.ROW_HEIGHT)],
                fill=self.COLORS["header_bg"],
                outline=self.COLORS["border"],
                width=1
            )

            # 标签文字（白色）
            label_bbox = self.font_cell.getbbox(label)
            label_width = label_bbox[2] - label_bbox[0]
            label_x = table_x + (self.COL_LABEL_WIDTH - label_width) // 2
            label_text_y = row_y + (self.ROW_HEIGHT - self.FONT_CELL) // 2 - 5

            draw.text((label_x, label_text_y), label, fill=self.COLORS["header_text"], font=self.font_cell)

            # 值文字（换行处理）
            value_lines = self._wrap_text(value, self.COL_VALUE_WIDTH - 40, self.font_cell)

            # 计算值的起始Y位置（垂直居中）
            total_text_height = len(value_lines) * (self.FONT_CELL + 8)
            value_text_y = row_y + (self.ROW_HEIGHT - total_text_height) // 2

            for j, line in enumerate(value_lines[:2]):  # 最多2行
                draw.text(
                    (table_x + self.COL_LABEL_WIDTH + 20, value_text_y + j * (self.FONT_CELL + 8)),
                    line,
                    fill=self.COLORS["text"],
                    font=self.font_cell
                )

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

    parser = argparse.ArgumentParser(description='表格风格封面生成器')
    parser.add_argument('--source', required=True, help='来源（机构名称）')
    parser.add_argument('--page-count', type=int, required=True, help='页码')
    parser.add_argument('--chinese-title', required=True, help='中文标题')
    parser.add_argument('--english-title', required=True, help='英文标题')
    parser.add_argument('--year', required=True, help='年份')
    parser.add_argument('--number', help='编号（MMDD格式）')
    parser.add_argument('--output', help='输出文件名')

    args = parser.parse_args()

    generator = TableCoverGenerator()
    result = generator.generate_cover(
        source=args.source,
        page_count=args.page_count,
        chinese_title=args.chinese_title,
        english_title=args.english_title,
        year=args.year,
        number=args.number,
        output_filename=args.output
    )

    print(f"\n{result['message']}")
    if result['success']:
        print(f"  路径: {result['path']}")


if __name__ == '__main__':
    main()
