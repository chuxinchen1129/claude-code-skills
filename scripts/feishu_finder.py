#!/usr/bin/env python3
"""
飞书路径查找工具 v3.0 - 统一入口
自动定位 feishu_bot_notifier.py 和相关脚本的实际路径
"""

import os
from pathlib import Path
import sys

# ==================== 可能的位置 ====================
# 按优先级排序（最可能在前）
POSSIBLE_PATHS = [
    Path("/Users/echochen/Desktop/DMS/skills/feishu-universal/scripts"),
    Path.home() / 'Desktop' / 'DMS' / 'skills' / 'feishu-universal' / 'scripts',
    Path.home() / '.claude' / 'skills' / 'feishu-universal',
    Path("/Users/echochen/claude-code-skills/DaMiShuSystem/skills"),
    Path("/Users/echochen/.claude/skills_backup/feishu-automation-v2_20260211_122046/scripts"),
]

# 要查找的文件
TARGET_FILES = {
    'feishu_bot_notifier.py': '飞书机器人通知器',
    'feishu_paths.py': '飞书路径管理',
    'feishu_user_auto.py': '飞书用户客户端',
}


class FeishuFinder:
    """飞书路径查找器"""

    def __init__(self):
        self.scripts_dir = None
        self.paths = {}
        self._find_all()

    def _find_all(self):
        """查找所有脚本文件"""
        for scripts_dir in POSSIBLE_PATHS:
            if scripts_dir.exists():
                self.scripts_dir = scripts_dir
                break

        if not self.scripts_dir:
            return

        # 查找每个目标文件
        for filename, description in TARGET_FILES.items():
            file_path = self.scripts_dir / filename
            if file_path.exists():
                self.paths[filename] = file_path
            else:
                # 尝试在其他位置查找
                for alt_dir in POSSIBLE_PATHS:
                    alt_path = alt_dir / filename
                    if alt_path.exists():
                        self.paths[filename] = alt_path
                        break

    def get_scripts_dir(self):
        """获取 feishu-universal 脚本目录"""
        return self.scripts_dir

    def get_path(self, filename):
        """获取指定文件的路径

        Args:
            filename: 文件名（如 'feishu_bot_notifier.py'）

        Returns:
            Path: 文件的绝对路径，如果未找到返回 None
        """
        return self.paths.get(filename)

    def get_notifier_path(self):
        """获取 feishu_bot_notifier.py 的路径"""
        return self.get_path('feishu_bot_notifier.py')

    def get_paths(self):
        """返回所有找到的路径"""
        return self.paths

    def is_valid(self):
        """检查是否找到所有必要的文件"""
        required = ['feishu_bot_notifier.py']
        return all(self.get_path(f) for f in required)

    def print_status(self):
        """打印查找状态"""
        print("=" * 60)
        print("飞书路径检查 v3.0")
        print("=" * 60)

        if self.scripts_dir:
            print(f"\n✅ 找到脚本目录: {self.scripts_dir}")
        else:
            print(f"\n❌ 未找到 feishu-universal 脚本目录")
            print("\n尝试过的路径:")
            for path in POSSIBLE_PATHS:
                exists = path.exists()
                status = "✓" if exists else "✗"
                print(f"  {status} {path}")
            return

        print(f"\n找到的文件:")
        for filename, description in TARGET_FILES.items():
            path = self.get_path(filename)
            if path:
                print(f"  ✓ {filename:25s} → {path}")
            else:
                print(f"  ✗ {filename:25s} → 未找到")

        print(f"\n完整路径示例:")
        notifier = self.get_notifier_path()
        if notifier:
            print(f"  feishu_bot_notifier.py: {notifier}")
        else:
            print(f"  ❌ feishu_bot_notifier.py: 未找到")


def find_feishu_scripts():
    """查找 feishu_universal 脚本目录（向后兼容函数）

    Returns:
        Path: 脚本目录路径，未找到返回 None
    """
    finder = FeishuFinder()
    return finder.get_scripts_dir()


def get_notifier_path():
    """获取 feishu_bot_notifier.py 的路径（向后兼容函数）

    Returns:
        Path: 文件路径，未找到返回 None
    """
    finder = FeishuFinder()
    return finder.get_notifier_path()


def get_feishu_import_path():
    """获取用于 sys.path 的路径

    Returns:
        str: 路径字符串，未找到返回 None
    """
    scripts_dir = find_feishu_scripts()
    if scripts_dir:
        return str(scripts_dir)
    return None


# ==================== 快捷函数 ====================

def check_feishu_setup():
    """检查飞书设置是否正确（用于调试）"""
    finder = FeishuFinder()
    finder.print_status()

    if finder.is_valid():
        print("\n✅ 所有必要文件已找到，飞书功能可用")
        return True
    else:
        print("\n⚠️  部分文件缺失，可能需要重新安装")
        return False


def get_notifier_command():
    """获取直接调用 feishu_bot_notifier.py 的命令

    Returns:
        list: 命令行参数列表，可直接用于 subprocess.run()
    """
    import sys
    python_path = sys.executable or 'python3'

    finder = FeishuFinder()
    notifier_path = finder.get_notifier_path()

    if notifier_path:
        return [python_path, str(notifier_path)]
    else:
        return None


def import_feishu_modules():
    """将 feishu-universal 添加到 Python 路径

    Returns:
        bool: 是否成功添加
    """
    import_path = get_feishu_import_path()
    if import_path and import_path not in sys.path:
        sys.path.insert(0, import_path)
        return True
    return False


# ==================== 命令行接口 ====================

def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='飞书路径查找工具 v3.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:

  # 检查飞书设置
  python3 feishu_finder.py

  # 获取 notifier 路径
  python3 feishu_finder.py --notifier

  # 获取所有路径（JSON格式）
  python3 feishu_finder.py --json

  # 添加到 sys.path
  python3 feishu_finder.py --import-mode
        """
    )

    parser.add_argument(
        '--check', '-c',
        action='store_true',
        help='检查飞书设置并打印状态'
    )

    parser.add_argument(
        '--notifier', '-n',
        action='store_true',
        help='只获取 feishu_bot_notifier.py 的路径'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='以 JSON 格式输出所有路径'
    )

    parser.add_argument(
        '--import-mode',
        '-i',
        action='store_true',
        help='将 feishu-universal 添加到 sys.path（用于Python脚本）'
    )

    parser.add_argument(
        '--command',
        action='store_true',
        help='获取调用 feishu_bot_notifier.py 的命令行参数'
    )

    args = parser.parse_args()

    finder = FeishuFinder()

    if args.check:
        finder.print_status()
        return 0 if finder.is_valid() else 1

    if args.notifier:
        path = finder.get_notifier_path()
        if path:
            print(path)
            return 0
        else:
            print("未找到 feishu_bot_notifier.py", file=sys.stderr)
            return 1

    if args.json:
        import json
        output = {
            'scripts_dir': str(finder.get_scripts_dir()) if finder.get_scripts_dir() else None,
            'paths': {k: str(v) for k, v in finder.get_paths().items()}
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return 0

    if args.import_mode:
        if import_feishu_modules():
            print(f"已添加到 sys.path: {get_feishu_import_path()}")
            return 0
        else:
            print("未找到 feishu-universal 脚本目录", file=sys.stderr)
            return 1

    if args.command:
        cmd = get_notifier_command()
        if cmd:
            print(' '.join(cmd))
            return 0
        else:
            print("未找到 feishu_bot_notifier.py", file=sys.stderr)
            return 1

    # 默认：检查状态
    finder.print_status()
    return 0 if finder.is_valid() else 1


if __name__ == "__main__":
    sys.exit(main())
