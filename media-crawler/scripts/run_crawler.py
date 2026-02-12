#!/usr/bin/env python3
"""
MediaCrawler 采集脚本

功能：
1. 自动环境检查
2. 配置文件备份和恢复
3. 关键词参数化
4. 扫码登录提醒
5. 数据自动转换

改进点：
- 修复虚拟环境路径问题
- 增强扫码登录提示
- 更好的错误处理

作者：大秘书系统
版本：v1.0.0
创建时间：2026-02-11
"""

import json
import os
import shutil
import subprocess
import sys
import re
from datetime import datetime
from pathlib import Path
import argparse


class MediaCrawlerRunner:
    """MediaCrawler 采集器"""

    def __init__(self):
        """初始化采集器"""
        self.mediacrawler_dir = Path.home() / "MediaCrawler"
        self.skill_dir = Path(__file__).parent.parent

        # 虚拟环境 Python 路径
        self.venv_python = self.mediacrawler_dir / ".venv" / "bin" / "python"

        # 配置文件路径
        self.config_file = self.mediacrawler_dir / "config" / "base_config.py"
        self.backup_config_path = self.mediacrawler_dir / "config" / "base_config.py.backup_media_crawler_skill"

        # 数据目录
        self.data_dir = self.mediacrawler_dir / "data"

    def check_environment(self):
        """检查环境"""
        print("=" * 60)
        print("环境检查")
        print("=" * 60)

        # 检查 MediaCrawler 目录
        if not self.mediacrawler_dir.exists():
            print(f"❌ MediaCrawler 目录不存在: {self.mediacrawler_dir}")
            print("\n请先安装 MediaCrawler：")
            print("  cd ~")
            print("  git clone https://github.com/NanmiCoder/MediaCrawler.git")
            return False

        print(f"✅ MediaCrawler 目录存在")

        # 检查虚拟环境
        if not self.venv_python.exists():
            print(f"❌ 虚拟环境不存在: {self.venv_python}")
            print("\n请创建虚拟环境：")
            print(f"  cd {self.mediacrawler_dir}")
            print("  python3.11 -m venv .venv")
            print("  source .venv/bin/activate")
            print("  pip install -r requirements.txt")
            return False

        # 检查虚拟环境 Python 版本
        result = subprocess.run(
            [str(self.venv_python), "--version"],
            capture_output=True,
            text=True
        )
        venv_version = result.stdout.strip()
        print(f"✅ 虚拟环境 Python: {venv_version}")

        if "3.11" not in venv_version:
            print(f"⚠️  虚拟环境版本不是 3.11: {venv_version}")
            return False

        # 检查配置文件
        if not self.config_file.exists():
            print(f"❌ 配置文件不存在: {self.config_file}")
            return False

        print(f"✅ 配置文件存在")

        print("\n✅ 环境检查通过")
        return True

    def backup_config(self):
        """备份配置文件"""
        if not self.backup_config_path.exists():
            shutil.copy2(self.config_file, self.backup_config_path)
            print(f"✓ 配置文件已备份: {self.backup_config_path}")
        else:
            print(f"✓ 配置备份已存在")

    def restore_config(self):
        """恢复配置文件"""
        if self.backup_config_path.exists():
            shutil.copy2(self.backup_config_path, self.config_file)
            print(f"✓ 配置已恢复")
            # 删除备份
            self.backup_config_path.unlink()
        else:
            print(f"⚠️  备份文件不存在，跳过恢复")

    def modify_config(self, platform, keywords, max_count=50):
        """修改配置文件

        Args:
            platform: 平台代码 (xhs, douyin, weibo, bilibili, baidu)
            keywords: 关键词列表
            max_count: 最大采集数量
        """
        # 读取配置
        with open(self.config_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 平台映射
        platform_names = {
            "xhs": "小红书",
            "douyin": "抖音",
            "weibo": "微博",
            "bilibili": "B站",
            "baidu": "百度"
        }

        # 修改关键词
        keywords_str = ",".join(keywords)
        content_new = re.sub(
            r'KEYWORDS = ".*?"',
            f'KEYWORDS = "{keywords_str}"',
            content
        )

        # 设置平台
        content_new = re.sub(
            r'PLATFORM = ".*?"',
            f'PLATFORM = "{platform}"',
            content_new
        )

        # 设置数据保存类型为 json
        content_new = re.sub(
            r'SAVE_DATA_OPTION = ".*?"',
            'SAVE_DATA_OPTION = "json"',
            content_new
        )

        # 确保开启媒体下载
        content_new = re.sub(
            r'ENABLE_GET_MEIDAS = (True|False)',
            'ENABLE_GET_MEIDAS = True',
            content_new
        )

        # 确保开启评论爬取
        content_new = re.sub(
            r'ENABLE_GET_COMMENTS = (True|False)',
            'ENABLE_GET_COMMENTS = True',
            content_new
        )

        # 设置爬取数量
        content_new = re.sub(
            r'CRAWLER_MAX_NOTES_COUNT = \d+',
            f'CRAWLER_MAX_NOTES_COUNT = {max_count}',
            content_new
        )

        # 写回配置
        with open(self.config_file, "w", encoding="utf-8") as f:
            f.write(content_new)

        print(f"✓ 配置已修改:")
        print(f"  - 平台: {platform} ({platform_names.get(platform, platform)})")
        print(f"  - 关键词: {keywords_str}")
        print(f"  - 爬取数量: {max_count}")
        print(f"  - 媒体下载: 已启用")
        print(f"  - 评论爬取: 已启用")

    def show_login_prompt(self, platform):
        """显示登录提示"""
        platform_names = {
            "xhs": "小红书",
            "douyin": "抖音",
            "weibo": "微博",
            "bilibili": "B站"
        }

        print("\n" + "=" * 60)
        print("📱 扫码登录提示")
        print("=" * 60)
        print(f"平台: {platform_names.get(platform, platform)}")
        print()
        print("⚠️  请准备扫码登录...")
        print("1. 浏览器会自动打开")
        print("2. 扫描二维码登录（15秒内有效）")
        print("3. 登录后采集自动开始")
        print("4. 保持浏览器打开，直到采集完成")
        print()
        print("💡 提示:")
        print("  - 首次登录需要扫码")
        print("  - 登录后会保持会话，无需每次扫码")
        print("  - 如果登录超时，重新运行脚本即可")
        print()
        print("=" * 60)

        # 等待用户确认
        input("按 Enter 键继续，准备扫码登录...")

    def run_crawler(self):
        """运行 MediaCrawler

        Returns:
            bool: 是否成功
        """
        print("\n开始运行 MediaCrawler...")
        print("⚠️  浏览器即将打开，请准备扫码登录...")
        print()

        # 切换到 MediaCrawler 目录
        original_dir = os.getcwd()
        os.chdir(self.mediacrawler_dir)

        try:
            # 使用虚拟环境的 Python 运行
            result = subprocess.run(
                [str(self.venv_python), "main.py"],
                capture_output=False,  # 实时显示输出
                text=True,
                timeout=1200  # 20分钟超时
            )

            if result.returncode == 0:
                print("\n✓ MediaCrawler 运行完成")
                return True
            else:
                print(f"\n⚠️  MediaCrawler 运行出错，返回码: {result.returncode}")
                return False

        except subprocess.TimeoutExpired:
            print("\n⚠️  MediaCrawler 运行超时（20分钟）")
            return False
        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断")
            return False
        except Exception as e:
            print(f"\n⚠️  运行失败: {e}")
            return False
        finally:
            os.chdir(original_dir)

    def show_data_summary(self, platform):
        """显示数据汇总"""
        print("\n" + "=" * 60)
        print("数据汇总")
        print("=" * 60)

        # 查找 JSON 文件
        platform_dir = self.data_dir / platform / "json"

        if platform_dir.exists():
            json_files = list(platform_dir.glob("search_contents_*.json"))

            if json_files:
                # 按时间排序，取最新的
                json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                latest_file = json_files[0]

                # 读取数据
                with open(latest_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                print(f"✓ 采集数据: {len(data)} 条")
                print(f"✓ 文件位置: {latest_file}")
                print(f"✓ 采集时间: {datetime.fromtimestamp(latest_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")

                # 计算平均互动量
                if data:
                    total_likes = sum(int(item.get("liked_count", 0).replace(",", "").replace("万", "0000")) if isinstance(item.get("liked_count"), str) else int(item.get("liked_count", 0)) for item in data[:30])

                    # 处理 "万" 字
                    def parse_count(count_str):
                        if isinstance(count_str, str):
                            if "万" in count_str:
                                return float(count_str.replace("万", "")) * 10000
                            return int(count_str.replace(",", ""))
                        return int(count_str) if count_str else 0

                    total_likes = sum(parse_count(item.get("liked_count", 0)) for item in data[:30])
                    total_comments = sum(parse_count(item.get("comment_count", 0)) for item in data[:30])
                    total_collects = sum(parse_count(item.get("collected_count", 0)) for item in data[:30])

                    print(f"✓ TOP30 平均互动:")
                    print(f"    - 平均点赞: {total_likes // min(30, len(data))}")
                    print(f"    - 平均评论: {total_comments // min(30, len(data))}")
                    print(f"    - 平均收藏: {total_collects // min(30, len(data))}")
            else:
                print("⚠️  未找到采集数据")
        else:
            print("⚠️  数据目录不存在")

        print("=" * 60)

    def run(self, platform, keywords, max_count=50, show_login=True):
        """执行采集流程

        Args:
            platform: 平台代码
            keywords: 关键词列表
            max_count: 最大采集数量
            show_login: 是否显示登录提示

        Returns:
            bool: 是否成功
        """
        print("=" * 60)
        print("MediaCrawler 采集")
        print("=" * 60)
        print(f"平台: {platform}")
        print(f"关键词: {', '.join(keywords)}")
        print(f"最大采集数: {max_count}")
        print()

        # 1. 环境检查
        print("[1/5] 环境检查...")
        if not self.check_environment():
            return False

        # 2. 备份配置
        print("\n[2/5] 备份配置...")
        self.backup_config()

        # 3. 修改配置
        print("\n[3/5] 修改配置...")
        self.modify_config(platform, keywords, max_count)

        # 4. 显示登录提示
        if show_login:
            self.show_login_prompt(platform)

        # 5. 运行采集
        print("\n[4/5] 运行采集...")
        success = self.run_crawler()

        # 6. 数据汇总
        print("\n[5/5] 数据汇总...")
        self.show_data_summary(platform)

        # 恢复配置
        print("\n恢复配置...")
        self.restore_config()

        print("\n" + "=" * 60)
        if success:
            print("✓ 采集完成！")
        else:
            print("⚠️  采集可能未完成，请检查数据")
        print("=" * 60)

        return success


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="MediaCrawler 采集脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 采集小红书数据
  python3 run_crawler.py --platform xhs --keywords "睡眠仪"

  # 采集抖音数据
  python3 run_crawler.py --platform douyin --keywords "产品名"

  # 采集微博数据
  python3 run_crawler.py --platform weibo --keywords "话题"

  # 多关键词采集
  python3 run_crawler.py --platform xhs --keywords "睡眠仪" "左点" "助眠"

  # 自定义采集数量
  python3 run_crawler.py --platform xhs --keywords "睡眠仪" --max 100

支持的平台:
  xhs      小红书
  douyin   抖音
  weibo    微博
  bilibili B站
  baidu    百度
        """
    )

    parser.add_argument(
        "--platform",
        choices=["xhs", "douyin", "weibo", "bilibili", "baidu"],
        required=True,
        help="采集平台"
    )

    parser.add_argument(
        "--keywords",
        nargs="+",
        required=True,
        help="采集关键词（多个关键词用空格分隔）"
    )

    parser.add_argument(
        "--max",
        type=int,
        default=50,
        help="最大采集数量（默认 50）"
    )

    parser.add_argument(
        "--no-login-prompt",
        action="store_true",
        help="不显示登录提示（适用于已登录的情况）"
    )

    args = parser.parse_args()

    # 创建采集器
    runner = MediaCrawlerRunner()

    # 运行采集
    success = runner.run(
        platform=args.platform,
        keywords=args.keywords,
        max_count=args.max,
        show_login=not args.no_login_prompt
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
