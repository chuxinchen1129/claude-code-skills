#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""现代社论风HTML封面生成器
紧凑社论风格，高密度、高对比、报纸头版质感
输出单文件HTML5，可直接在浏览器打开
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict


class EditorialCoverGenerator:
    """现代社论风HTML封面生成器"""

    # 长度限制常量
    MAX_CHINESE_CHARS_PER_LINE = 8  # 中文标题每行最多8字
    MAX_ENGLISH_LENGTH = 25  # 英文标题最多25个字符
    MAX_HIGHLIGHT_TITLE_LENGTH = 25  # 摘要标题最多25字
    MAX_SUMMARY_TEXT_LENGTH = 60  # 摘要内容最多60字

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
                        borderLine: '#2c241b',
                        bgLight: '#fc3d6d',
                        bgDark: '#2c241b'
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
    <div id="editorial-card-container" class="rounded-xl overflow-hidden shadow-editorial paper-noise bg-bgBase" style="width: 640px; height: 853px;">
        <div class="content-wrapper p-10 flex flex-col" style="height: 100%; display: flex; flex-direction: column;">
            <!-- Header -->
            <header class="pb-6 border-b-3 border-textMain" style="flex-shrink: 0;">
                <h1 class="font-noto-serif font-black text-[3.6rem] leading-[1.1] text-textMain mb-2" style="word-break: keep-all; overflow-wrap: break-word;">
                    {title_lines}
                </h1>
                <div class="flex justify-between items-baseline">
                    <p class="text-lg text-accent font-bold tracking-wider" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{english_upper}</p>
                    <p class="font-oswald text-xl text-textMain/80">INDUSTRY REPORT</p>
                </div>
            </header>

            <!-- Body -->
            <main class="flex-1 flex flex-col" style="min-height: 0;">
                <!-- 摘要区 -->
                <div class="bg-bgLight p-5 mb-5 rounded-lg border-l-4 border-accent" style="flex-shrink: 0;">
                    <h2 class="font-noto-serif font-bold text-xl mb-2 text-textMain" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{highlight_title}</h2>
                    <p class="text-textMain/90 leading-relaxed text-sm" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{summary_text}</p>
                </div>

                <!-- 网格区 -->
                <div class="grid grid-cols-3 gap-4" style="flex-shrink: 0;">
                    <div class="bg-white/80 backdrop-blur-sm p-4 rounded-lg shadow-sm">
                        <i class="fa fa-file-text-o text-xl text-accent mb-2"></i>
                        <h3 class="font-bold text-base mb-1 text-textMain">报告类型</h3>
                        <p class="text-xs text-textMain/80" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{report_type}</p>
                    </div>
                    <div class="bg-white/80 backdrop-blur-sm p-4 rounded-lg shadow-sm">
                        <i class="fa fa-tag text-xl text-accent mb-2"></i>
                        <h3 class="font-bold text-base mb-1 text-textMain">核心品类</h3>
                        <p class="text-xs text-textMain/80" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{categories}</p>
                    </div>
                    <div class="bg-white/80 backdrop-blur-sm p-4 rounded-lg shadow-sm">
                        <i class="fa fa-barcode text-xl text-accent mb-2"></i>
                        <h3 class="font-bold text-base mb-1 text-textMain">报告编号</h3>
                        <p class="text-xs text-textMain/80">NO.{number}</p>
                    </div>
                </div>
            </main>

            <!-- Footer -->
            <footer class="bg-bgDark text-white rounded-xl p-6" style="flex-shrink: 0;">
                <div class="flex justify-between items-center">
                    <div class="flex-1 min-w-0">
                        <p class="font-noto-sans text-base mb-1" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">来源：{source}</p>
                        <p class="text-white/80 text-xs">{date_full} | PAGES: {page_count}</p>
                    </div>
                    <div class="text-center flex-shrink-0 ml-4">
                        <span class="font-oswald text-[4rem] font-bold text-white leading-none">{page_count}</span>
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

    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            script_dir = Path(__file__).parent
            output_dir = script_dir / "covers"
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
        categories: str = "",
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
            categories: 核心品类（用于网格区中间位置）
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

            # 保留用户自定义换行，按\n分割成多行
            user_lines = chinese_title.split('\n') if '\n' in chinese_title else []

            if len(user_lines) >= 3:
                # 用户提供了完整的三行，直接使用，跳过自动生成
                title_lines = [line.strip() for line in user_lines[:3]]
            else:
                # 回退到自动生成逻辑
                # 第一行始终是年份（固定）
                year_match = re.search(r'(20\d{2})', year or chinese_title)
                year_line = year_match.group(1) if year_match else "2026"

                # 清理标题内容，用于提取关键词
                title_clean = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', chinese_title)
                # 移除开头的年份
                title_clean = re.sub(r'^20\d{2}', '', title_clean)

                # 放宽关键词匹配规则：从标题中智能提取核心信息（最多8字）
                # 优先级：1. 用户传入的标题前8字 2. 常见行业关键词 3. 通用后缀
                second_line = ""

                # 提取标题中的品牌/品类信息（取前8个字作为第二行）
                if title_clean:
                    # 移除常见的报告后缀
                    suffixes = ["研究报告", "报告", "分析", "洞察", "白皮书", "行业", "产业"]
                    for suffix in suffixes:
                        if title_clean.endswith(suffix):
                            title_clean = title_clean[:-len(suffix)]
                            break

                    # 取前8个字作为第二行（核心品牌/品类）
                    second_line = title_clean[:8].strip()

                # 如果提取为空，使用通用后缀
                if not second_line:
                    second_line = "行业研究"

                # 第三行：智能生成报告类型
                third_line = "研究报告"  # 默认最简洁

                # 根据标题中的关键词优化报告类型
                if any(kw in chinese_title for kw in ["复兴", "改革", "转型", "焕新"]):
                    third_line = "复兴报告"
                elif any(kw in chinese_title for kw in ["趋势", "展望", "预测", "增长"]):
                    third_line = "趋势报告"
                elif any(kw in chinese_title for kw in ["竞争", "格局", "排名"]):
                    third_line = "竞争报告"
                elif any(kw in chinese_title for kw in ["白皮书"]):
                    third_line = "白皮书"
                elif any(kw in chinese_title for kw in ["洞察", "分析"]):
                    third_line = "洞察报告"

                # 统一组合标题行
                title_lines = [year_line, second_line, third_line]
            # 规则：第3行标题长度不超过9个字
            if len(title_lines) >= 3 and len(title_lines[2]) > 9:
                title_lines[2] = title_lines[2][:9]

            title_lines_html = "<br>".join(title_lines)

            # 英文标题转大写
            english_upper = english_title.upper()[:self.MAX_ENGLISH_LENGTH]

            # 验证长度
            if len(highlight_title) > self.MAX_HIGHLIGHT_TITLE_LENGTH:
                highlight_title = highlight_title[:self.MAX_HIGHLIGHT_TITLE_LENGTH]
            if len(summary_text) > self.MAX_SUMMARY_TEXT_LENGTH:
                summary_text = summary_text[:self.MAX_SUMMARY_TEXT_LENGTH]

            # 填充HTML模板
            html_content = self.HTML_TEMPLATE.format(
                title=chinese_title[:30],
                title_lines=title_lines_html,
                english_upper=english_upper,
                highlight_title=highlight_title or "核心要点",
                summary_text=summary_text or "简要概述",
                source=source or "研究报告",
                page_count=page_count,
                date_full=date_full,
                report_type=report_type or "行业研究报告",
                categories=categories or "-",
                number=number
            )

            # 生成输出文件名
            if output_filename is None:
                safe_title = re.sub(r'[^\w\-]', '_', chinese_title[:20])
                output_filename = f"cover_{safe_title}_{number}.html"

            output_path = self.output_dir / output_filename

            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            return {
                'success': True,
                'path': str(output_path),
                'title_lines': title_lines,
                'english_upper': english_upper,
                'page_count': page_count,
                'number': number,
                'html_content': html_content
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'path': None
            }


def main():
    """测试函数"""
    generator = EditorialCoverGenerator()

    # 测试用例：海菲曼电声行业报告
    result = generator.generate_cover(
        source="海菲曼研究",
        page_count=22,
        chinese_title="海菲曼电声高端品牌商研究报告",
        english_title="HIFIMAN Audio Industry Report",
        year="2026",
        highlight_title="从高端音频品牌到行业领导者",
        summary_text="电声行业竞争格局与市场机会分析",
        report_type="行业研究报告",
        categories="耳机、播放器、解码器",
        number="0304"
    )

    if result['success']:
        print(f"✅ 封面生成成功")
        print(f"   文件路径: {result['path']}")
        print(f"   标题行: {' | '.join(result['title_lines'])}")
        print(f"   英文标题: {result['english_upper']}")
        print(f"   页数: {result['page_count']}")
    else:
        print(f"❌ 封面生成失败: {result['error']}")


if __name__ == "__main__":
    main()
