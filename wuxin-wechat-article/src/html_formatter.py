#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
悟昕公众号文章 HTML 格式化器

将 Markdown 文章转换为符合悟昕品牌规范的 HTML
适用于微信公众号发布

作者: Claude Code
版本: 1.0.0
更新: 2026-02-26
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


class WuxinHTMLFormatter:
    """悟昕HTML格式化器"""

    # 悟昕品牌颜色
    PRIMARY_COLOR = "#7C5DFA"  # 品牌紫
    TEXT_COLOR = "#4A5568"     # 正文色
    BORDER_COLOR = "#E2E8F0"   # 边框色
    BACKGROUND_COLOR = "#FFFFFF"  # 背景色
    MUTED_COLOR = "#A0AEC0"    # 次要文字

    # 字体设置
    FONT_FAMILY = "-apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei UI', 'Microsoft YaHei', Arial, sans-serif"

    # 正文参数
    FONT_SIZE = 15
    LINE_HEIGHT = 1.8
    LETTER_SPACING = 0.8

    def __init__(self):
        self.section_counter = 0

    def format_article(self, markdown_text: str, with_end: bool = True) -> str:
        """
        将 Markdown 转换为悟昕风格 HTML

        Args:
            markdown_text: Markdown 文本
            with_end: 是否包含 END 结尾标识

        Returns:
            HTML 文本
        """
        lines = markdown_text.split('\n')
        html_parts = []
        self.section_counter = 0

        # 容器开始
        html_parts.append(self._container_open())

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 跳过空行
            if not line:
                i += 1
                continue

            # 一级标题 (#) - 转换为醒目标题
            if line.startswith('# '):
                title = line[2:].strip()
                html_parts.append(self._format_main_title(title))

            # 二级标题 (##) - 转换为章节小标题
            elif line.startswith('## '):
                self.section_counter += 1
                title = line[3:].strip()
                html_parts.append(self._format_section_title(self.section_counter, title))

            # 三级标题 (###) - 转换为子标题
            elif line.startswith('### '):
                title = line[4:].strip()
                html_parts.append(self._format_sub_title(title))

            # 无序列表 (- 或 *)
            elif line.startswith(('-', '*')) and len(line) > 1:
                items = self._parse_list_items(lines, i)
                html_parts.append(self._format_bullet_list(items))
                i += len(items) - 1

            # 有序列表
            elif re.match(r'^\d+\.\s', line):
                items = self._parse_list_items(lines, i)
                html_parts.append(self._format_numbered_list(items))
                i += len(items) - 1

            # 引用块 (>)
            elif line.startswith('> '):
                content = line[2:].strip()
                html_parts.append(self._format_quote(content))

            # 普通段落
            else:
                html_parts.append(self._format_paragraph(line))

            i += 1

        # END 结尾标识
        if with_end:
            html_parts.append(self._format_end())

        # 容器结束
        html_parts.append(self._container_close())

        return '\n'.join(html_parts)

    def _container_open(self) -> str:
        """容器开始标签"""
        return f'''<div style="font-family: {self.FONT_FAMILY}; line-height: {self.LINE_HEIGHT}; letter-spacing: {self.LETTER_SPACING}px; padding: 10px 5px; color: {self.TEXT_COLOR}; background-color: {self.BACKGROUND_COLOR};">'''

    def _container_close(self) -> str:
        """容器结束标签"""
        return '</div>'

    def _format_main_title(self, title: str) -> str:
        """一级标题格式"""
        return f'''<h1 style="font-size: 24px; font-weight: bold; color: {self.PRIMARY_COLOR}; text-align: center; margin: 30px 0 20px;">{title}</h1>'''

    def _format_section_title(self, number: int, title: str) -> str:
        """章节小标题格式（悟昕标志性样式）"""
        return f'''
<div style="text-align: center; margin-top: 40px; margin-bottom: 25px;">
    <p style="font-family: Georgia, serif; font-size: 56px; font-style: italic; font-weight: bold; color: {self.PRIMARY_COLOR}; margin: 0; line-height: 1;">{number:02d}</p>
    <div style="display: inline-block; border-top: 1px solid {self.BORDER_COLOR}; border-bottom: 3px solid {self.PRIMARY_COLOR};">
        <h2 style="font-size: 18px; font-weight: bold; color: {self.TEXT_COLOR}; margin: 0; padding: 10px 15px;">{title}</h2>
    </div>
</div>'''

    def _format_sub_title(self, title: str) -> str:
        """三级标题格式"""
        return f'''<h3 style="font-size: 16px; font-weight: bold; color: {self.TEXT_COLOR}; margin: 25px 0 15px; padding-left: 12px; border-left: 4px solid {self.PRIMARY_COLOR};">{title}</h3>'''

    def _format_paragraph(self, text: str) -> str:
        """段落格式"""
        # 处理加粗 **text**
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color: {self.PRIMARY_COLOR}; font-weight: bold;">\1</strong>', text)

        # 处理删除线 ~~text~~
        text = re.sub(r'~~(.+?)~~', r'<span style="text-decoration: line-through;">\1</span>', text)

        # 处理斜体 *text*
        text = re.sub(r'\*(.+?)\*', r'<em style="font-family: Georgia, serif; font-style: italic;">\1</em>', text)

        return f'<p style="font-size: {self.FONT_SIZE}px; margin: 1em 0;">{text}</p>'

    def _format_bullet_list(self, items: List[str]) -> str:
        """无序列表格式"""
        list_items = []
        for item in items:
            # 移除列表符号
            item = re.sub(r'^[-*]\s+', '', item)
            # 处理加粗
            item = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color: {self.PRIMARY_COLOR};">\1</strong>', item)
            list_items.append(f'    <li style="margin-bottom: 8px;"><strong style="color: {self.PRIMARY_COLOR};">-</strong> {item}</li>')

        return f'''<ul style="list-style: none; padding-left: 10px; margin: 1em 0;">
{chr(10).join(list_items)}
</ul>'''

    def _format_numbered_list(self, items: List[str]) -> str:
        """有序列表格式（用于参考文献）"""
        list_items = []
        for idx, item in enumerate(items, 1):
            # 移除序号
            item = re.sub(r'^\d+\.\s+', '', item)
            # 处理加粗
            item = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color: {self.PRIMARY_COLOR};">\1</strong>', item)
            # 处理斜体 *text*
            item = re.sub(r'\*(.+?)\*', r'<em style="font-family: Georgia, serif; font-style: italic;">\1</em>', item)
            list_items.append(f'    <p style="font-size: {self.FONT_SIZE}px; margin: 0.8em 0; padding-left: 10px;"><strong style="color: {self.PRIMARY_COLOR}; font-weight: bold;">{idx}. </strong>{item}</p>')

        return f'''{chr(10).join(list_items)}'''

    def _format_quote(self, text: str) -> str:
        """引用块格式"""
        return f'''<section style="margin-top: 20px; padding: 20px; background-color: #F8F9FA; border-left: 4px solid {self.PRIMARY_COLOR};">
    <p style="font-size: 14px; margin: 0; color: {self.TEXT_COLOR};">{text}</p>
</section>'''

    def _format_end(self) -> str:
        """END 结尾标识"""
        return f'''
<p style="text-align: center; font-weight: bold; font-size: {self.FONT_SIZE}px; color: {self.PRIMARY_COLOR}; margin-top: 40px; margin-bottom: 20px;">END</p>'''

    def _parse_list_items(self, lines: List[str], start_idx: int) -> List[str]:
        """解析列表项"""
        items = []
        i = start_idx

        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            # 检查是否是列表项
            if re.match(r'^[-*]\s+', line) or re.match(r'^\d+\.\s', line):
                items.append(line)
                i += 1
            else:
                break

        return items if items else [lines[start_idx].strip()]


def format_price_section(original_price: str, sale_price: str) -> str:
    """
    格式化价格展示区域

    Args:
        original_price: 原价（如 "2,199 元"）
        sale_price: 现价（如 "1,698 元"）

    Returns:
        HTML 文本
    """
    formatter = WuxinHTMLFormatter()
    return f'''
<p style="font-size: {formatter.FONT_SIZE}px; margin-bottom: 15px; text-align: center;">官方定价 <span style="text-decoration: line-through;">{original_price}</span></p>
<p style="font-size: 20px; font-weight: bold; color: {formatter.PRIMARY_COLOR}; text-align: center; margin-bottom: 15px;">新年首发价：{sale_price}！</p>
'''


def format_faq_section(faqs: List[Tuple[str, str]]) -> str:
    """
    格式化常见问题区域

    Args:
        faqs: Q&A 列表，格式为 [("问题1", "回答1"), ("问题2", "回答2")]

    Returns:
        HTML 文本
    """
    formatter = WuxinHTMLFormatter()

    qa_items = []
    for q, a in faqs:
        qa_items.append(f'    <p style="font-size: 14px; margin-bottom: 10px;"><strong style="color: {formatter.PRIMARY_COLOR};">Q：{q}</strong></p>')
        qa_items.append(f'    <p style="font-size: 14px; margin-bottom: 15px;">A：{a}</p>')

    return f'''
<section style="margin-top: 40px; padding: 20px; background-color: #F8F9FA; border-left: 4px solid {formatter.PRIMARY_COLOR};">
    <h3 style="font-size: 18px; font-weight: bold; color: {formatter.TEXT_COLOR}; margin-bottom: 20px;">常见问题解答</h3>
{chr(10).join(qa_items)}
</section>'''


def format_references_section(references: List[str]) -> str:
    """
    格式化参考文献区域

    Args:
        references: 参考文献列表，每条包含完整的引用信息

    Returns:
        HTML 文本
    """
    formatter = WuxinHTMLFormatter()
    ref_items = []

    for idx, ref in enumerate(references, 1):
        # 处理加粗
        ref = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color: {formatter.PRIMARY_COLOR};">\1</strong>', ref)
        # 处理斜体 *text*
        ref = re.sub(r'\*(.+?)\*', r'<em style="font-family: Georgia, serif; font-style: italic;">\1</em>', ref)
        ref_items.append(f'    <p style="font-size: {formatter.FONT_SIZE}px; margin: 0.8em 0; padding-left: 10px;"><strong style="color: {formatter.PRIMARY_COLOR}; font-weight: bold;">{idx}. </strong>{ref}</p>')

    return f'''
{chr(10).join(ref_items)}'''


# CLI 接口
def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='悟昕公众号文章 HTML 格式化器')
    parser.add_argument('input', help='输入 Markdown 文件路径')
    parser.add_argument('-o', '--output', help='输出 HTML 文件路径')
    parser.add_argument('--no-end', action='store_true', help='不添加 END 结尾标识')

    args = parser.parse_args()

    # 读取输入
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误：文件不存在 - {input_path}")
        return

    markdown_text = input_path.read_text(encoding='utf-8')

    # 格式化
    formatter = WuxinHTMLFormatter()
    html = formatter.format_article(markdown_text, with_end=not args.no_end)

    # 输出
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(html, encoding='utf-8')
        print(f"✅ HTML 已保存到：{output_path}")
    else:
        print(html)


if __name__ == '__main__':
    main()
