#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DMS 系统统一路径管理模块

提供统一的路径管理，避免每个脚本重复计算路径
"""

from pathlib import Path
from typing import Optional

# DMS 根目录
DMS_ROOT = Path.home() / 'Desktop' / 'DMS'

# 各技能目录
SKILLS_DIR = DMS_ROOT / 'skills'

# 具体技能路径
BAOGAOMIAO_SCRIPTS = SKILLS_DIR / 'baogaomiao' / 'scripts'
BAOGAOMIAO_COVERS = BAOGAOMIAO_SCRIPTS / 'covers'

FEISHU_UNIVERSAL_SCRIPTS = SKILLS_DIR / 'feishu-universal' / 'scripts'
FEISHU_UNIVERSAL_DIR = Path.home() / '.claude' / 'skills' / 'feishu-universal'


class DMSCheck:
    """DMS 系统路径检查工具"""

    @staticmethod
    def verify_feishu_env():
        """验证飞书环境配置"""
        # 检查用户配置文件是否存在
        user_config = Path.home() / '.feishu_user_config.json'
        return user_config.exists()

    @staticmethod
    def get_feishu_scripts_dir() -> Path:
        """获取飞书脚本目录，自动处理环境差异"""
        # 优先：~/.claude/skills/feishu-universal/
        primary = FEISHU_UNIVERSAL_DIR

        # 如果不存在，回退到 DMS
        if not primary.exists():
            primary = FEISHU_UNIVERSAL_SCRIPTS

        return primary

    @staticmethod
    def get_baogaomiao_scripts_dir() -> Path:
        """获取报告喵脚本目录"""
        return BAOGAOMIAO_SCRIPTS

    @staticmethod
    def get_baogaomiao_covers_dir() -> Path:
        """获取报告喵封面输出目录"""
        return BAOGAOMIAO_COVERS


# 使用示例
if __name__ == '__main__':
    print(f"DMS_ROOT: {DMS_ROOT}")
    print(f"BAOGAOMIAO_SCRIPTS: {BAOGAOMIAO_SCRIPTS}")
    print(f"FEISHU_SCRIPTS: {DMSCheck.get_feishu_scripts_dir()}")
