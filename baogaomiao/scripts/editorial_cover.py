#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代社论风HTML封面生成器

紧凑社论风格，高密度、高对比、报纸头版质感
输出单文件HTML5，可直接在浏览器打开
"""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict


class EditorialCoverGenerator:
    """现代社论风HTML封面生成器"""

    # 长度限制常量
    MAX_CHINESE_CHARS_PER_LINE = 8  # 中文标题每行最多8字
    MAX_ENGLISH_LENGTH = 25  # 英文标题最多25个字符
    MAX_HIGHLIGHT_TITLE_LENGTH = 60  # 摘要标题最多60字（3句话完整显示）
    MAX_SUMMARY_TEXT_LENGTH = 80  # 摘要内容最多80字

    # HTML模板（固定3:4比例的紧凑社论风）
    HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | 紧凑社论风</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@900&family=Oswald:wght@700&family=Noto+Sans+SC:wght@400;700&display=swap" rel="stylesheet">
    <style type="text/tailwindcss">
        @layer utilities {{
            .text-shadow-sm {{
                text-shadow: 0 1px 2px rgba(0,0,0,0.05);
            }}
            .paper-noise {{
                position: relative;
            }}
            .paper-noise::before {{
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                opacity: 0.05;
                pointer-events: none;
                background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
                z-index: 1;
            }}
            .content-wrapper {{
                position: relative;
                z-index: 2;
            }}
        }}
    </style>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        bgBase: '#FB0151',
                        textMain: '#000000',
                        accent: '#000000',
                        borderLine: '#1a110d',
                        bgLight: '#fb5a7b',
                        bgDark: '#1a110d'
                    }},
                    fontFamily: {{
                        'noto-serif': ['Noto Serif SC', 'serif'],
                        'oswald': ['Oswald', 'sans-serif'],
                        'noto-sans': ['Noto Sans SC', 'sans-serif']
                    }},
                    boxShadow: {{
                        'editorial': '0 20px 40px -10px rgba(60,48,32,0.15)'
                    }}
                }}
            }}
        }}
    </script>
</head>
<body class="bg-bgBase flex items-center justify-center p-8 font-noto-sans text-textMain" style="min-height: 100vh;">
    <div id="editorial-card-container" class="rounded-xl overflow-hidden shadow-editorial paper-noise bg-bgBase" style="width: 640px; height: 900px;">
        <div class="content-wrapper p-10 flex flex-col" style="height: 100%; display: flex; flex-direction: column;">
            <!-- Header -->
            <header class="pb-6 border-b-3 border-textMain" style="flex-shrink: 0;">
                <h1 class="font-noto-serif font-black text-[3.6rem] leading-tight text-textMain mb-0">
                    {title_lines}
                </h1>
                <div class="flex justify-between items-baseline">
                    <p class="text-lg text-accent font-bold tracking-wider">{english_upper}</p>
                    <p class="font-oswald text-xl text-textMain/80">INDUSTRY REPORT</p>
                </div>
            </header>

            <!-- Body -->
            <main class="flex-1 flex flex-col" style="min-height: 0;">
                <!-- 摘要区 -->
                <div class="bg-bgLight p-5 mb-8 rounded-lg border-l-4 border-accent" style="flex-shrink: 0;">
                    <h2 class="font-noto-serif font-bold text-xl mb-2 text-textMain">报告摘要</h2>
                    <p class="text-textMain/90 leading-relaxed text-sm">{summary_text}</p>
                </div>

                <!-- 网格区 -->
                <div class="grid grid-cols-3 gap-4" style="flex-shrink: 0;">
                    <div class="bg-white/80 backdrop-blur-sm p-4 rounded-lg shadow-sm">
                        <i class="fa fa-file-text-o text-xl text-accent mb-2"></i>
                        <h3 class="font-bold text-base mb-1 text-textMain">报告类型</h3>
                        <p class="text-xs text-textMain/80">{report_type}</p>
                    </div>
                    <div class="bg-white/80 backdrop-blur-sm p-4 rounded-lg shadow-sm">
                        <i class="fa fa-calendar text-xl text-accent mb-2"></i>
                        <h3 class="font-bold text-base mb-1 text-textMain">发布年份</h3>
                        <p class="text-xs text-textMain/80">{year}</p>
                    </div>
                    <div class="bg-white/80 backdrop-blur-sm p-4 rounded-lg shadow-sm">
                        <i class="fa fa-barcode text-xl text-accent mb-2"></i>
                        <h3 class="font-bold text-base mb-1 text-textMain">报告编号</h3>
                        <p class="text-xs text-textMain/80">NO.{number}</p>
                    </div>
                </div>
            </main>

            <!-- Footer -->
            <footer class="bg-bgDark text-white rounded-xl p-6 mt-4" style="flex-shrink: 0;">
                <div class="flex justify-between items-center">
                    <div>
                        <p class="font-noto-sans text-base mb-1">来源：{source}</p>
                        <p class="text-white/80 text-xs">{date_full} | {pages} PAGES</p>
                    </div>
                    <div class="text-center">
                        <span class="font-oswald text-[5rem] font-bold text-white leading-none">{pages}</span>
                        <p class="font-noto-sans text-white/90 text-xs">PAGES</p>
                    </div>
                </div>
            </footer>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const elements = [
                'header', 'main > div:first-child',
                'main .grid > div:nth-child(1)',
                'main .grid > div:nth-child(2)',
                'main .grid > div:nth-child(3)',
                'footer'
            ];

            elements.forEach((selector, index) => {{
                const el = document.querySelector(selector);
                if (el) {{
                    el.style.opacity = '0';
                    el.style.transform = 'translateY(20px)';
                    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    el.style.transitionDelay = `${{index * 0.15}}s`;

                    setTimeout(() => {{
                        el.style.opacity = '1';
                        el.style.transform = 'translateY(0)';
                    }}, 100);
                }}
            }});
        }});
    </script>
</body>
</html>"""

    def _load_config(self) -> Dict:
        """加载配置文件

        Returns:
            配置字典
        """
        config_file = Path(__file__).parent / "editorial_cover_config.yaml"

        # 默认配置
        default_config = {
            'max_chinese_chars_per_line': 8,
            'max_english_length': 25,
            'max_highlight_title_length': 60,
            'max_summary_text_length': 80,
            'container_width': 800,
            'container_height': 1066,
            'page_num_font_scale': 2.0,
            'title_font_scale': 1.0,
            'default_output_dir': Path(__file__).parent / "covers"
        }

        # 如果配置文件存在，则加载
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)

                # 合并配置（用户配置覆盖默认值）
                if user_config and 'defaults' in user_config:
                    defaults = user_config['defaults']

                    # 更新长度限制
                    if 'highlight_title_max_length' in defaults:
                        default_config['max_highlight_title_length'] = defaults['highlight_title_max_length']
                    if 'summary_max_length' in defaults:
                        default_config['max_summary_text_length'] = defaults['summary_max_length']

                    # 更新容器尺寸
                    if 'container_width' in defaults:
                        default_config['container_width'] = defaults['container_width']
                    if 'container_height' in defaults:
                        default_config['container_height'] = defaults['container_height']

                    # 更新字号缩放
                    if 'page_num_font_scale' in defaults:
                        default_config['page_num_font_scale'] = defaults['page_num_font_scale']
                    if 'title_font_scale' in defaults:
                        default_config['title_font_scale'] = defaults['title_font_scale']

                    # 更新输出目录
                    if 'default_output_dir' in defaults:
                        default_config['default_output_dir'] = Path(defaults['default_output_dir']).expanduser()

                    print(f"✓ 已加载配置文件: {config_file}")

            except Exception as e:
                print(f"⚠️ 配置文件加载失败，使用默认值: {e}")

        return default_config

    def __init__(self, output_dir: Optional[Path] = None):
        # 加载配置
        config = self._load_config()

        # 应用配置到类常量（确保类型正确）
        self.MAX_CHINESE_CHARS_PER_LINE = int(config['max_chinese_chars_per_line'])
        self.MAX_ENGLISH_LENGTH = int(config['max_english_length'])
        self.MAX_HIGHLIGHT_TITLE_LENGTH = int(config['max_highlight_title_length'])
        self.MAX_SUMMARY_TEXT_LENGTH = int(config['max_summary_text_length'])
        self.container_width = int(config['container_width'])
        self.container_height = int(config['container_height'])
        self.page_num_font_scale = float(config['page_num_font_scale'])
        self.title_font_scale = float(config['title_font_scale'])

        # 设置输出目录
        if output_dir is None:
            output_dir = config['default_output_dir']

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_cover(
        self,
        source: str,
        page_count: int,
        chinese_title: str,
        english_title: str,
        year: str,
        highlight_title: str = "",
        summary_text: str = "",
        report_type: str = "行业研究报告",
        number: Optional[str] = None,
        output_filename: Optional[str] = None
    ) -> Dict:
        """
        生成现代社论风HTML封面

        Args:
            source: 来源（机构名称）
            page_count: 页数
            chinese_title: 中文标题
            english_title: 英文标题
            year: 年份
            highlight_title: 摘要区标题
            summary_text: 摘要区内容
            report_type: 报告类型
            number: 编号（MMDD格式）
            output_filename: 输出文件名

        Returns:
            结果字典
        """
        try:
            # 生成编号和日期
            if number is None:
                number = datetime.now().strftime("%m%d")

            now = datetime.now()
            date_full = now.strftime("%Y.%m.%d")
            day = now.strftime("%d")

            # 处理标题换行（优先使用\n，否则按8字一行切分）
            # 检测真正的\n或转义后的\\n
            if '\n' in chinese_title or '\\n' in chinese_title:
                # 用户指定了换行位置，使用<br>实现真正的HTML换行
                title_lines_html = chinese_title.replace('\n', '<br>').replace('\\n', '<br>')
            else:
                # 按字符数自动切分（8字一行）
                title_clean = chinese_title
                # 移除emoji
                for emoji in ["🎯", "🍼", "📊", "🚀", "💡", "✨", "🔥", "💪", "⭐"]:
                    title_clean = title_clean.replace(emoji, "")
                title_chars = list(title_clean)
                title_lines = []
                for i in range(0, len(title_chars), self.MAX_CHINESE_CHARS_PER_LINE):
                    title_lines.append("".join(title_chars[i:i+self.MAX_CHINESE_CHARS_PER_LINE]))
                title_lines_html = "<br>".join(title_lines) if len(title_lines) > 1 else chinese_title

            # 英文标题大写 + 长度限制
            english_upper = english_title.upper()
            if len(english_upper) > self.MAX_ENGLISH_LENGTH:
                english_upper = english_upper[:self.MAX_ENGLISH_LENGTH] + "..."

            # 摘要区和关键词长度限制
            if not highlight_title:
                highlight_title = "核心要点"
            if len(highlight_title) > self.MAX_HIGHLIGHT_TITLE_LENGTH:
                highlight_title = highlight_title[:self.MAX_HIGHLIGHT_TITLE_LENGTH]
            if not summary_text:
                summary_text = f"本报告深入分析{chinese_title[:10]}等关键议题，"
            if len(summary_text) > self.MAX_SUMMARY_TEXT_LENGTH:
                summary_text = summary_text[:self.MAX_SUMMARY_TEXT_LENGTH]

            # 计算动态值
            page_num_font_size = f"{3.35 * self.page_num_font_scale:.2f}"

            # 动态替换模板中的固定值
            html_template = self.HTML_TEMPLATE
            html_template = html_template.replace("width: 640px;", f"width: {self.container_width}px;")
            html_template = html_template.replace("height: 853px;", f"height: {self.container_height}px;")
            html_template = html_template.replace("text-[5rem]", f"text-[{page_num_font_size}rem]")

            # 生成HTML
            html_content = html_template.format(
                title=chinese_title,
                title_lines=title_lines_html,
                english_upper=english_upper,
                highlight_title=highlight_title,
                summary_text=summary_text,
                report_type=report_type,
                year=year,
                number=number,
                source=source,
                date_full=date_full,
                day=day,
                pages=page_count
            )

            # 生成文件名
            if output_filename is None:
                title_slug = self._sanitize_filename(chinese_title[:15])
                output_filename = f"editorial_{title_slug}_{number}.html"

            output_path = self.output_dir / output_filename

            # 保存HTML
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            return {
                'success': True,
                'path': output_path,
                'message': f'✓ 现代社论风HTML封面已生成: {output_filename}'
            }

        except Exception as e:
            return {
                'success': False,
                'path': None,
                'message': f'封面生成失败: {e}'
            }

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

    parser = argparse.ArgumentParser(description='现代社论风HTML封面生成器')
    parser.add_argument('--source', required=True, help='来源（机构名称）')
    parser.add_argument('--page-count', type=int, required=True, help='页码')
    parser.add_argument('--chinese-title', required=True, help='中文标题')
    parser.add_argument('--english-title', required=True, help='英文标题')
    parser.add_argument('--year', required=True, help='年份')
    parser.add_argument('--highlight-title', help='摘要区标题', default='')
    parser.add_argument('--summary-text', help='摘要区内容', default='')
    parser.add_argument('--report-type', help='报告类型', default='行业研究报告')
    parser.add_argument('--number', help='编号（MMDD格式）')
    parser.add_argument('--output', help='输出文件名')

    args = parser.parse_args()

    generator = EditorialCoverGenerator()
    result = generator.generate_cover(
        source=args.source,
        page_count=args.page_count,
        chinese_title=args.chinese_title,
        english_title=args.english_title,
        year=args.year,
        highlight_title=args.highlight_title,
        summary_text=args.summary_text,
        report_type=args.report_type,
        number=args.number,
        output_filename=args.output
    )

    print(f"\n{result['message']}")
    if result['success']:
        print(f"  路径: {result['path']}")
        print(f"  提示: 在浏览器中打开该HTML文件查看效果")


if __name__ == '__main__':
    main()
