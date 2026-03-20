#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能断词工具

功能：
1. 在语义边界处断开标题
2. 避免在词中间断开
3. 支持自定义词库
"""

import re
from typing import List


class TitleSplitter:
    """标题断词器"""

    # 常见词汇库（避免在这些词中间断开）
    COMMON_WORDS = [
        # 科技类
        "智能", "驾驶", "汽车", "消费", "报告", "研究", "分析", "技术", "数据",
        "平台", "系统", "应用", "服务", "模型", "算法", "网络", "云端",
        # 商业类
        "行业", "市场", "用户", "产品", "品牌", "营销", "销售", "渠道", "客户",
        "增长", "趋势", "策略", "竞争", "发展", "管理", "运营", "投资",
        # 描述类
        "深度", "全面", "详细", "专业", "最新", "年度", "季度", "月度",
        "白皮书", "洞察", "蓝皮书", "调查", "分析", "预测", "展望"
    ]

    # 不能单独成字的字符
    SINGLE_CHARS = ["的", "与", "和", "或", "及", "与", "等", "中", "在", "上"]

    def __init__(self, custom_words: List[str] = None):
        """
        初始化断词器

        Args:
            custom_words: 自定义词库
        """
        self.word_set = set(self.COMMON_WORDS)
        if custom_words:
            self.word_set.update(custom_words)

    def split_title(self, title: str, max_lines: int = 2, max_chars: int = 10) -> List[str]:
        """
        智能断开标题

        Args:
            title: 标题文本
            max_lines: 最大行数
            max_chars: 每行最大字符数

        Returns:
            断开后的标题行列表
        """
        # 移除emoji和特殊字符
        clean_title = self._clean_title(title)

        # 如果标题足够短，不需要断开
        if len(clean_title) <= max_chars:
            return [clean_title]

        # 智能断开
        lines = self._split_by_semantics(clean_title, max_lines, max_chars)

        return lines

    def _clean_title(self, title: str) -> str:
        """清理标题，移除emoji和特殊字符"""
        # 移除emoji
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        title = emoji_pattern.sub('', title)

        # 移除其他特殊字符
        title = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\(\)（）\-—]', '', title)

        return title.strip()

    def _split_by_semantics(self, title: str, max_lines: int, max_chars: int) -> List[str]:
        """按语义断开标题"""
        lines = []
        current_line = ""
        words = list(title)  # 按字符分割

        i = 0
        while i < len(words) and len(lines) < max_lines:
            char = words[i]

            # 如果当前行满了
            if len(current_line) >= max_chars:
                # 尝试在语义边界断开
                break_pos = self._find_break_position(current_line)
                lines.append(current_line[:break_pos])
                current_line = current_line[break_pos:] + char
                i += 1
                continue

            # 检查是否应该在这里断开
            if i < len(words) - 1:
                next_char = words[i + 1]
                # 如果下一个字符会导致超长，且当前位置是合适的断点
                if (len(current_line) + 1 >= max_chars and
                    self._is_break_position(char, next_char)):
                    lines.append(current_line)
                    current_line = ""
                    i += 1
                    continue

            current_line += char
            i += 1

        # 添加最后一行
        if current_line and len(lines) < max_lines:
            lines.append(current_line)

        return lines

    def _find_break_position(self, text: str) -> int:
        """找到合适的断开位置"""
        if len(text) <= 5:
            return len(text)

        # 从后往前找断点
        for i in range(len(text) - 1, 0, -1):
            # 如果是标点符号，可以断开
            if text[i] in '，。、；：!?！？':
                return i + 1

            # 如果是空格，可以断开
            if text[i].isspace():
                return i + 1

        # 如果没有找到，就在中间断开
        return len(text) // 2

    def _is_break_position(self, char: str, next_char: str) -> bool:
        """判断是否是合适的断开位置"""
        # 如果是标点符号，可以断开
        if char in '，。、；：!?！？':
            return True

        # 如果是空格，可以断开
        if char.isspace():
            return True

        # 如果下一个字符会导致词被拆开，不能断开
        two_char = char + next_char
        if two_char in self.word_set:
            return False

        return True


# ==================== 测试代码 ====================

if __name__ == '__main__':
    splitter = TitleSplitter()

    test_titles = [
        "2026智驾未来AI重塑汽车消费新纪元",
        "母婴连锁经营数据报告逆势增长密码",
        "OpenClaw高级玩法之工作区优化与三大Agent深度解析",
        "中国移动互联网流量年度报告"
    ]

    print("智能断词测试：\n")
    for title in test_titles:
        lines = splitter.split_title(title, max_lines=2, max_chars=10)
        print(f"原标题: {title}")
        print(f"断开: {' | '.join(lines)}")
        print()
