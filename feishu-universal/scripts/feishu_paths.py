#!/usr/bin/env python3
"""
飞书自动化 - 统一路径管理模块
解决飞书相关脚本的路径配置不一致问题
"""

from pathlib import Path


class FeishuPaths:
    """飞书路径统一管理"""

    # DMS 根目录
    DMS_ROOT = Path.home() / 'Desktop' / 'DMS'

    # feishu-universal 位置
    FEISHU_UNIVERSAL = DMS_ROOT / 'skills' / 'feishu-universal'
    SCRIPTS = FEISHU_UNIVERSAL / 'scripts'

    # 核心脚本
    USER_AUTO = SCRIPTS / 'feishu_user_auto.py'
    BOT_NOTIFIER = SCRIPTS / 'feishu_bot_notifier.py'
    OAUTH_SETUP = SCRIPTS / 'feishu_oauth_setup.py'
    TOKEN_CHECKER = SCRIPTS / 'feishu_token_checker.py'

    # 全局配置
    USER_CONFIG = Path.home() / '.feishu_user_config.json'

    @classmethod
    def verify(cls):
        """验证路径配置是否正确"""
        issues = []

        if not cls.DMS_ROOT.exists():
            issues.append(f"DMS_ROOT 不存在: {cls.DMS_ROOT}")

        if not cls.FEISHU_UNIVERSAL.exists():
            issues.append(f"FEISHU_UNIVERSAL 不存在: {cls.FEISHU_UNIVERSAL}")

        if not cls.SCRIPTS.exists():
            issues.append(f"SCRIPTS 不存在: {cls.SCRIPTS}")

        if not cls.BOT_NOTIFIER.exists():
            issues.append(f"BOT_NOTIFIER 不存在: {cls.BOT_NOTIFIER}")

        if not cls.USER_CONFIG.exists():
            issues.append(f"USER_CONFIG 不存在: {cls.USER_CONFIG} (请先执行 OAuth 授权)")

        return issues


# 便捷函数
def get_feishu_script(script_name: str) -> Path:
    """获取飞书脚本路径"""
    return FeishuPaths.SCRIPTS / script_name


def get_bot_notifier() -> Path:
    """获取飞书通知工具路径"""
    return FeishuPaths.BOT_NOTIFIER


def get_user_config() -> Path:
    """获取用户配置文件路径"""
    return FeishuPaths.USER_CONFIG


if __name__ == "__main__":
    # 验证路径配置
    print("=" * 60)
    print("飞书路径配置验证")
    print("=" * 60)

    issues = FeishuPaths.verify()

    if issues:
        print("\n❌ 发现问题:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ 所有路径配置正确")

    print("\n路径配置:")
    print(f"  DMS_ROOT:          {FeishuPaths.DMS_ROOT}")
    print(f"  FEISHU_UNIVERSAL:  {FeishuPaths.FEISHU_UNIVERSAL}")
    print(f"  SCRIPTS:           {FeishuPaths.SCRIPTS}")
    print(f"  BOT_NOTIFIER:      {FeishuPaths.BOT_NOTIFIER}")
    print(f"  USER_CONFIG:       {FeishuPaths.USER_CONFIG}")
