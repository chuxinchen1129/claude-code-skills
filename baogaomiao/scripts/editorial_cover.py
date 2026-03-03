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

    # 品牌中立化关键词映射（使用短语而非单词，避免误替换）
    BRAND_NEUTRALIZE_PATTERNS = [
        # 品牌/公司相关 - 使用完整短语
        ("龙头地位", "市场地位"),
        ("行业龙头", "行业深度"),
        ("绝对龙头", "市场深度"),
        ("龙头", "核心"),  # 最后才匹配单字
        # 业绩相关
        ("增长密码", "增长动因"),
        ("成功密码", "成功因素"),
        ("逆势增长", "业绩增长"),
        ("增长背后", "增长分析"),
        # 情感词
        ("璀璨", "核心"),
        ("闪耀", "核心"),
        ("辉煌", "重要"),
        ("传奇", "发展"),
        ("神话", "历程"),
    ]

    # 常见词汇（用于避免在词中间断开）
    COMMON_WORDS = set([
        "报告", "研究", "分析", "白皮书", "洞察", "深度", "行业", "市场", "趋势",
        "数据", "经营", "发展", "战略", "布局", "领域", "赛道", "技术", "创新",
        "产品", "品牌", "公司", "业务", "收入", "利润", "增长", "规模", "份额",
        "电池", "芯片", "半导体", "机器人", "化妆品", "母婴", "零售", "连锁",
        "一次性", "碱性", "锂离子", "硅光", "光芯片", "薄膜", "铌酸锂",
        "品类", "品类创新", "市场", "市场地位", "地位", "稳固", "探索", "第二", "第二曲线", "曲线",
    ])
    CATEGORY_KEYWORDS = {
        "一次性电池": ["南孚", "碱性电池", "碱锰电池", "碳性电池", "锌锰电池", "一次性电池", "干电池"],
        "锂离子电池": ["锂电池", "锂离子", "动力电池", "储能电池", "三元锂", "磷酸铁锂"],
        "半导体": ["芯片", "半导体", "集成电路", "IC", "GPU", "CPU", "光芯片", "硅光"],
        "机器人": ["机器人", "自动化", "智能制造", "工控", "机器臂"],
        "化妆品": ["化妆品", "护肤", "彩妆", "珀莱雅", "贝泰尼", "上海家化"],
        "母婴": ["母婴", "童装", "奶粉", "纸尿裤", "玩具", "宝宝"],
        "连锁零售": ["连锁", "零售", "超市", "便利店", "门店"],
        "AI/人工智能": ["AI", "人工智能", "大模型", "ChatGPT", "深度学习"],
        "光通信": ["光通信", "光纤", "光模块", "CPO", "薄膜铌酸锂"],
        "消费电子": ["消费电子", "手机", "耳机", "智能手表", "AR", "VR"],
        "新能源": ["新能源", "光伏", "风电", "储能", "充电桩"],
        "汽车": ["汽车", "整车", "乘用车", "新能源汽车", "电动车"],
        "医疗器械": ["医疗器械", "医疗设备", "影像", "诊断"],
        "医药": ["医药", "药品", "生物药", "创新药", "仿制药"],
        "食品饮料": ["食品", "饮料", "白酒", "乳制品", "调味品"],
        "家电": ["家电", "空调", "冰箱", "洗衣机", "小家电"],
    }

    # 长度限制常量
    MAX_CHINESE_TITLE_LENGTH = 20  # 中文标题总长度最多20字（不含年份前缀）
    MAX_CHINESE_LINES = 2  # 中文标题最多2行（年份占1行，总共3行）
    MAX_CHINESE_CHARS_PER_LINE = 10  # 中文标题每行最多10字
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
                        <i class="fa fa-tag text-xl text-accent mb-2"></i>
                        <h3 class="font-bold text-base mb-1 text-textMain">核心品类</h3>
                        <p class="text-xs text-textMain/80">{category}</p>
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
            'max_chinese_title_length': 25,  # 中文标题总长度最多25字（不含年份前缀）
            'max_chinese_lines': 3,  # 中文标题最多3行
            'max_chinese_chars_per_line': 9,  # 中文标题每行最多9字（3行共25字）
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
                    if 'max_chinese_title_length' in defaults:
                        default_config['max_chinese_title_length'] = defaults['max_chinese_title_length']
                    if 'max_chinese_lines' in defaults:
                        default_config['max_chinese_lines'] = defaults['max_chinese_lines']
                    if 'max_chinese_chars_per_line' in defaults:
                        default_config['max_chinese_chars_per_line'] = defaults['max_chinese_chars_per_line']
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
        self.MAX_CHINESE_TITLE_LENGTH = int(config['max_chinese_title_length'])
        self.MAX_CHINESE_LINES = int(config['max_chinese_lines'])
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
        category: str = "",
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
            category: 核心品类（如：一次性电池、半导体等）
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

            # 处理中文标题：保留年份，去掉emoji，品牌中立化，语义断行
            # 提取年份前缀（如 2026）
            year_prefix = ""
            title_content = chinese_title

            # 匹配年份（带或不带emoji）
            year_match = re.search(r'[🎯🍼📊🚀💡✨🔥💪⭐]?(\d{4})', chinese_title)
            if year_match:
                year_prefix = year_match.group(1)  # 只要年份，不要emoji
                title_content = chinese_title[year_match.end():]  # 剩余部分

            # 品牌中立化处理
            title_content = self._neutralize_brand(title_content)

            # 清理剩余内容：移除emoji和其他符号
            for emoji in ["🎯", "🍼", "📊", "🚀", "💡", "✨", "🔥", "💪", "⭐", "——", "—", " "]:
                title_content = title_content.replace(emoji, "")

            # 截断到最多25字
            if len(title_content) > self.MAX_CHINESE_TITLE_LENGTH:
                title_content = title_content[:self.MAX_CHINESE_TITLE_LENGTH]

            # 使用智能语义断行（避免在词中间断开）
            if '\n' in title_content or '\\n' in title_content:
                # 用户指定了换行位置
                content_lines_html = title_content.replace('\n', '<br>').replace('\\n', '<br>')
            else:
                # 使用语义断行（智能断词）
                content_lines = self._split_title_by_semantics(title_content)
                content_lines_html = "<br>".join(content_lines) if len(content_lines) > 1 else title_content

            # 组合年份 + 内容（年份不带emoji）
            if year_prefix:
                title_lines_html = f"{year_prefix}<br>{content_lines_html}"
            else:
                title_lines_html = content_lines_html

            # 英文标题大写 + 长度限制
            english_upper = english_title.upper()
            if len(english_upper) > self.MAX_ENGLISH_LENGTH:
                english_upper = english_upper[:self.MAX_ENGLISH_LENGTH] + "..."

            # 报告摘要：将梗概和关键词组合成1-2句完整的话
            if not highlight_title and not summary_text:
                # 没有提供任何内容，使用默认值
                summary_text = f"本报告深入分析{chinese_title[:10]}等关键议题。"
            elif highlight_title and summary_text:
                # 有梗概和关键词，组合成1-2句完整的话
                # 格式：梗概。关键词包括A、B、C等。
                if summary_text.endswith('、'):
                    summary_text = summary_text[:-1] + '等'
                summary_text = f"{highlight_title}。{summary_text}。"
                # 确保是完整的句子
                if not summary_text.endswith('。'):
                    summary_text += '。'
            elif highlight_title:
                # 只有梗概，直接使用
                summary_text = highlight_title
                if not summary_text.endswith('。'):
                    summary_text += '。'
            else:
                # 只有关键词，生成句子
                summary_text = f"本报告重点分析{summary_text}等内容。"

            # 摘要长度限制（保留完整句子）
            if len(summary_text) > self.MAX_SUMMARY_TEXT_LENGTH:
                # 截断到最后一个句号
                last_period = summary_text[:self.MAX_SUMMARY_TEXT_LENGTH].rfind('。')
                if last_period > 0:
                    summary_text = summary_text[:last_period + 1]
                else:
                    summary_text = summary_text[:self.MAX_SUMMARY_TEXT_LENGTH] + '...'

            # 自动提取核心品类（如果没有提供）
            if not category:
                # 从标题、摘要、关键词中提取
                extract_text = f"{chinese_title} {highlight_title} {summary_text}"
                category = self._extract_category(extract_text)

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
                category=category,
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

    def _neutralize_brand(self, text: str) -> str:
        """品牌中立化：把带有赞赏色彩的词替换为中性词

        Args:
            text: 原始文本

        Returns:
            中立化后的文本
        """
        result = text
        # 按顺序替换（先匹配长的短语，避免误替换）
        for biased, neutral in self.BRAND_NEUTRALIZE_PATTERNS:
            result = result.replace(biased, neutral)
        return result

    def _split_title_by_semantics(self, text: str) -> list:
        """按语义断句，避免在词中间断开

        Args:
            text: 标题文本

        Returns:
            断句后的行列表
        """
        if not text:
            return []

        # 优先按标点符号断句
        if '——' in text:
            parts = text.split('——')
        elif '——' in text:
            parts = text.split('——')
        elif '，' in text:
            parts = text.split('，')
        elif ' ' in text:
            parts = text.split(' ')
        else:
            parts = [text]

        # 清理每部分
        lines = [p.strip() for p in parts if p.strip()]

        # 如果只有一行且过长，使用智能断词
        if len(lines) == 1 and len(lines[0]) > self.MAX_CHINESE_CHARS_PER_LINE:
            long_text = lines[0]
            lines = []
            start = 0

            while start < len(long_text) and len(lines) < self.MAX_CHINESE_LINES:
                # 计算这行应该到哪里结束
                preferred_end = start + self.MAX_CHINESE_CHARS_PER_LINE
                end = min(preferred_end, len(long_text))

                # 如果还没到结尾且没有到字符串末尾，尝试在词边界断开
                if end < len(long_text):
                    # 优先尝试在常用词结尾断开
                    best_break = end
                    for offset in range(12):  # 向前查找合适的断点（扩大范围）
                        check_pos = end - offset
                        if check_pos <= start + 5:  # 至少保留5个字符
                            break

                        # 检查当前位置是否是常见词的结尾
                        # 检查接下来的字符是否构成常见词
                        found_word_boundary = False
                        for word_len in range(2, 6):  # 检查2-5字的词
                            if check_pos + word_len <= len(long_text):
                                potential_word = long_text[check_pos:check_pos + word_len]
                                if potential_word in self.COMMON_WORDS:
                                    # 这是一个词的开始，应该在这里断开
                                    best_break = check_pos
                                    found_word_boundary = True
                                    break
                        if found_word_boundary:
                            break

                    # 如果找不到词边界，尝试在标点符号处断开
                    if best_break == end:
                        for punctuation in ['，', '。', '、', ';', '；']:
                            punct_pos = long_text.rfind(punctuation, start, end)
                            if punct_pos > start:
                                best_break = punct_pos + 1
                                break

                    end = best_break

                line = long_text[start:end].strip()
                if line:
                    lines.append(line)
                start = end

        # 最多保留3行
        return lines[:self.MAX_CHINESE_LINES]

    def _extract_category(self, text: str) -> str:
        """从文本中提取核心品类

        Args:
            text: 包含关键词的文本（标题、笔记内容等）

        Returns:
            核心品类名称
        """
        if not text:
            return "行业研究"

        # 遍历品类关键词，找到匹配的
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return category

        # 没有匹配到，返回默认值
        return "行业研究"

    def _extract_title_from_note(self, note_text: str) -> tuple:
        """从小红书笔记中提取标题

        Args:
            note_text: 小红书笔记内容

        Returns:
            (中文标题, 英文标题)
        """
        # 提取第一行作为标题
        lines = note_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('🎯'):
                return line, ""

        # 如果没找到，返回默认标题
        return "🎯2026行业深度研究报告", "INDUSTRY DEEP DIVE REPORT"
        """按语义断句，优先在标点符号处断开

        Args:
            text: 标题文本

        Returns:
            断句后的行列表
        """
        if not text:
            return []

        # 优先按标点符号断句：——、——、，、。、；、：
        # 首先尝试长破折号
        if '——' in text:
            parts = text.split('——')
        elif '——' in text:
            parts = text.split('——')
        elif '，' in text:
            parts = text.split('，')
        elif ' ' in text:
            parts = text.split(' ')
        else:
            # 没有标点，按字数切分
            parts = [text]

        # 清理每部分，并过滤空字符串
        lines = [p.strip() for p in parts if p.strip()]

        # 如果只有一行且过长，强制按字数切分
        if len(lines) == 1 and len(lines[0]) > self.MAX_CHINESE_CHARS_PER_LINE:
            long_text = lines[0]
            lines = []
            for i in range(0, len(long_text), self.MAX_CHINESE_CHARS_PER_LINE):
                line = long_text[i:i+self.MAX_CHINESE_CHARS_PER_LINE]
                if line:
                    lines.append(line)

        # 最多保留3行
        return lines[:self.MAX_CHINESE_LINES]

    def _extract_category(self, text: str) -> str:
        """从文本中提取核心品类

        Args:
            text: 包含关键词的文本（标题、笔记内容等）

        Returns:
            核心品类名称
        """
        if not text:
            return "行业研究"

        # 遍历品类关键词，找到匹配的
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return category

        # 没有匹配到，返回默认值
        return "行业研究"


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
    parser.add_argument('--category', help='核心品类（如：一次性电池、半导体等）', default='')
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
        category=args.category,
        number=args.number,
        output_filename=args.output
    )

    print(f"\n{result['message']}")
    if result['success']:
        print(f"  路径: {result['path']}")
        print(f"  提示: 在浏览器中打开该HTML文件查看效果")


if __name__ == '__main__':
    main()
