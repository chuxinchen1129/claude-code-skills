#!/usr/bin/env python3
"""
悟昕睡眠热点采集分析系统 - 主脚本

功能：协调所有采集、分析、上传功能

使用方法：
    # 完整流程
    python3 main.py --full

    # 仅采集
    python3 main.py --collect

    # 仅分析
    python3 main.py --analyze

    # 仅上传
    python3 main.py --upload

作者：大秘书系统
版本：v1.0.0
创建时间：2026-02-10
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class WuxinSleepAnalyzer:
    """悟昕睡眠热点分析器"""

    def __init__(self):
        """初始化"""
        self.script_dir = Path(__file__).parent
        self.skill_dir = self.script_dir.parent

    def run_script(self, script_name, args=None):
        """运行脚本

        Args:
            script_name: 脚本名称
            args: 参数列表

        Returns:
            bool: 是否成功
        """
        script_path = self.script_dir / script_name

        if not script_path.exists():
            print(f"✗ 脚本不存在: {script_path}")
            return False

        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)

        print(f"\n运行: {script_name}")
        print("-" * 80)

        try:
            result = subprocess.run(cmd, cwd=self.skill_dir)
            return result.returncode == 0
        except Exception as e:
            print(f"✗ 运行失败: {e}")
            return False

    def collect(self, keywords=None):
        """采集数据

        Args:
            keywords: 关键词列表
        """
        print("\n" + "=" * 80)
        print("步骤 1: 数据采集")
        print("=" * 80)

        args = []
        if keywords:
            args.extend(["--keywords"] + keywords)

        return self.run_script("mediecrawler_integration.py", args)

    def analyze(self):
        """分析数据"""
        print("\n" + "=" * 80)
        print("步骤 2: 数据分析")
        print("=" * 80)

        # 运行每周分析器
        success1 = self.run_script("weekly_analyzer.py")

        # 生成 Excel 报告
        success2 = self.run_script("excel_generator.py")

        return success1 and success2

    def transcribe(self):
        """视频转文字"""
        print("\n" + "=" * 80)
        print("步骤 3: 视频转文字")
        print("=" * 80)

        return self.run_script("video_transcriber_integration.py")

    def upload(self):
        """上传到飞书"""
        print("\n" + "=" * 80)
        print("步骤 4: 飞书上传")
        print("=" * 80)

        return self.run_script("feishu_uploader.py")

    def full_workflow(self, keywords=None):
        """完整工作流

        Args:
            keywords: 关键词列表
        """
        print("\n" + "=" * 80)
        print("悟昕睡眠热点采集分析系统")
        print("=" * 80)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. 采集数据
        if not self.collect(keywords):
            print("\n⚠️  采集失败，但继续分析...")

        # 2. 分析数据
        if not self.analyze():
            print("\n✗ 分析失败")
            return False

        # 3. 视频转文字（可选）
        # self.transcribe()

        # 4. 上传飞书
        if not self.upload():
            print("\n⚠️  上传失败，但数据已保存")

        print("\n" + "=" * 80)
        print("✓ 工作流完成！")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="悟昕睡眠热点采集分析系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  # 完整流程（采集 + 分析 + 上传）
  python3 main.py --full

  # 指定关键词采集
  python3 main.py --full --keywords 睡眠仪 左点

  # 仅采集数据
  python3 main.py --collect

  # 仅分析已有数据
  python3 main.py --analyze

  # 仅上传到飞书
  python3 main.py --upload
        """
    )

    parser.add_argument("--full", action="store_true", help="运行完整工作流")
    parser.add_argument("--collect", action="store_true", help="仅采集数据")
    parser.add_argument("--analyze", action="store_true", help="仅分析数据")
    parser.add_argument("--transcribe", action="store_true", help="仅视频转文字")
    parser.add_argument("--upload", action="store_true", help="仅上传到飞书")
    parser.add_argument("--keywords", nargs="+", help="采集关键词")

    args = parser.parse_args()

    analyzer = WuxinSleepAnalyzer()

    # 根据参数执行相应功能
    if args.full:
        analyzer.full_workflow(args.keywords)
    elif args.collect:
        analyzer.collect(args.keywords)
    elif args.analyze:
        analyzer.analyze()
    elif args.transcribe:
        analyzer.transcribe()
    elif args.upload:
        analyzer.upload()
    else:
        # 默认运行完整流程
        parser.print_help()


if __name__ == "__main__":
    main()
