#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
封面生成器 - 现代社论风封面生成

统一复用 baogaomiao 的正式封面引擎，避免独立 skill 与自动流程产出不一致。
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, Dict

# 导入图片转换模块
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
BAOGAOMIAO_SCRIPT_DIR = SKILL_DIR.parent / "baogaomiao" / "scripts"

sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(BAOGAOMIAO_SCRIPT_DIR))

from html_to_image import HTMLToImageConverter
from editorial_cover import EditorialCoverGenerator


class CoverGenerator:
    """封面生成器"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化封面生成器

        Args:
            config_path: 配置文件路径（可选）
        """
        self.config_path = config_path or str(SCRIPT_DIR / "cover_config.yaml")
        self.output_dir = SKILL_DIR / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.editorial_generator = EditorialCoverGenerator(output_dir=self.output_dir)
        self.image_converter = HTMLToImageConverter(output_dir=self.output_dir)

    def generate_cover(
        self,
        chinese_title: str,
        english_title: str,
        year: int,
        source: str = "研究报告",
        page_count: Optional[int] = None,
        highlight_title: str = "核心要点",
        summary_text: Optional[str] = None,
        report_type: str = "行业研究报告",
        output: Optional[str] = None,
        variant: Optional[str] = None,
        neutralize_title: bool = False
    ) -> Dict:
        """
        生成社论风封面

        Args:
            chinese_title: 中文标题
            english_title: 英文标题
            year: 年份
            source: 来源机构
            page_count: 报告页数
            highlight_title: 梗概标题
            summary_text: 摘要文本
            report_type: 报告类型
            output: 输出文件名

        Returns:
            结果字典：
            {
                'success': True/False,
                'html_path': 'HTML文件路径',
                'image_path': 'PNG图片路径',
                'message': '执行信息'
            }
        """
        try:
            html_filename = output
            if not html_filename:
                html_filename = self._build_output_filename(chinese_title, year, variant, ".html")

            image_filename = Path(html_filename).with_suffix(".png").name

            # 1. 生成HTML封面
            html_result = self.editorial_generator.generate_cover(
                chinese_title=chinese_title,
                english_title=english_title,
                source=source,
                year=year,
                page_count=page_count or 0,
                highlight_title=highlight_title,
                summary_text=summary_text,
                report_type=report_type,
                output_filename=html_filename,
                neutralize_title=neutralize_title
            )

            if not html_result['success']:
                return html_result

            html_path = str(html_result['path'])

            # 2. 转换为PNG图片
            image_result = self.image_converter.convert_to_xhs_style(
                html_path=html_path,
                output_filename=image_filename
            )

            return {
                'success': image_result['success'],
                'html_path': html_path,
                'image_path': image_result.get('path', ''),
                'message': f"✅ 封面生成成功: {image_result.get('path', '')}"
            }

        except Exception as e:
            return {
                'success': False,
                'html_path': '',
                'image_path': '',
                'message': f"❌ 生成失败: {str(e)}"
            }

    def _build_output_filename(self, chinese_title: str, year: int, variant: Optional[str], suffix: str) -> str:
        safe_title = self.editorial_generator._sanitize_filename(chinese_title[:20])
        variant_suffix = f"_{variant}" if variant else ""
        return f"cover_{year}_{safe_title}{variant_suffix}{suffix}"


# ==================== 命令行接口 ====================

def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(
        description='现代社论风封面生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 使用默认参数
  cover-generator

  # 指定参数
  cover-generator --title "2026新能源汽车行业报告" --year 2026

  # 完整参数
  cover-generator \\
    --title "母婴连锁经营数据报告" \\
    --english "MATERNAL & CHILD CHAIN DATA" \\
    --source "国金证券" \\
    --year 2026 \\
    --highlight "逆势增长密码" \\
    --variant v2 \\
    --output cover_20260316.png
        """
    )

    parser.add_argument('--chinese-title', help='中文标题')
    parser.add_argument('--english-title', help='英文标题')
    parser.add_argument('--year', type=int, help='年份（默认2026）')
    parser.add_argument('--source', help='来源机构（默认"研究报告"）')
    parser.add_argument('--page-count', type=int, help='报告页数')
    parser.add_argument('--highlight', help='梗概标题（默认"核心要点"）')
    parser.add_argument('--summary', help='摘要文本')
    parser.add_argument('--report-type', help='报告类型（默认"行业研究报告"）')
    parser.add_argument('--output', help='输出文件名')
    parser.add_argument('--variant', help='版本后缀，如 v2 / v3')
    parser.add_argument('--neutralize-title', action='store_true', help='封面层对标题做中性化改写（默认关闭）')

    args = parser.parse_args()

    # 如果没有提供必需参数，使用示例
    if not args.chinese_title:
        print("使用示例参数生成封面...\n")
        args.chinese_title = "2026行业趋势研究报告"
        args.english_title = "2026 INDUSTRY TRENDS REPORT"
        args.year = 2026

    generator = CoverGenerator()

    result = generator.generate_cover(
        chinese_title=args.chinese_title,
        english_title=args.english_title or args.chinese_title,
        year=args.year or 2026,
        source=args.source or "研究报告",
        page_count=args.page_count,
        highlight_title=args.highlight or "核心要点",
        summary_text=args.summary,
        report_type=args.report_type or "行业研究报告",
        output=args.output,
        variant=args.variant,
        neutralize_title=args.neutralize_title
    )

    print(f"\n{result['message']}")

    if result['success']:
        print(f"  HTML: {result['html_path']}")
        print(f"  图片: {result['image_path']}")

    return 0 if result['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
