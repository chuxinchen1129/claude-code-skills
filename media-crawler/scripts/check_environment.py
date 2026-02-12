#!/usr/bin/env python3
"""
MediaCrawler 环境检查脚本

检查：
1. Python 版本（需要 3.11）
2. 虚拟环境（~/MediaCrawler/.venv）
3. MediaCrawler 目录
4. 配置文件完整性

作者：大秘书系统
版本：v1.0.0
创建时间：2026-02-11
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """检查 Python 版本"""
    print("=" * 60)
    print("检查 Python 版本")
    print("=" * 60)

    # 检查系统 Python 版本
    version = sys.version_info
    print(f"系统 Python 版本: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor == 11:
        print("✅ Python 版本正确")
        return True
    else:
        print(f"⚠️  Python 版本不匹配，需要 3.11.x，当前 {version.major}.{version.minor}.{version.micro}")
        print("\n请安装 Python 3.11：")
        print("  brew install python@3.11  # macOS")
        print("  或者下载: https://www.python.org/downloads/")
        return False


def check_mediacrawler_dir():
    """检查 MediaCrawler 目录"""
    print("\n" + "=" * 60)
    print("检查 MediaCrawler 目录")
    print("=" * 60)

    mediacrawler_dir = Path.home() / "MediaCrawler"

    if mediacrawler_dir.exists():
        print(f"✅ MediaCrawler 目录存在: {mediacrawler_dir}")
        return True, mediacrawler_dir
    else:
        print(f"❌ MediaCrawler 目录不存在: {mediacrawler_dir}")
        print("\n请先安装 MediaCrawler：")
        print("  cd ~")
        print("  git clone https://github.com/NanmiCoder/MediaCrawler.git")
        return False, None


def check_virtual_environment(mediacrawler_dir):
    """检查虚拟环境"""
    print("\n" + "=" * 60)
    print("检查虚拟环境")
    print("=" * 60)

    venv_dir = mediacrawler_dir / ".venv"
    venv_python = venv_dir / "bin" / "python"

    if venv_dir.exists():
        print(f"✅ 虚拟环境存在: {venv_dir}")

        if venv_python.exists():
            # 检查虚拟环境的 Python 版本
            result = subprocess.run(
                [str(venv_python), "--version"],
                capture_output=True,
                text=True
            )
            venv_version = result.stdout.strip()
            print(f"✅ 虚拟环境 Python: {venv_version}")

            # 确认是 Python 3.11
            if "3.11" in venv_version:
                print("✅ 虚拟环境版本正确")
                return True, str(venv_python)
            else:
                print(f"⚠️  虚拟环境版本不是 3.11: {venv_version}")
                return False, None
        else:
            print(f"❌ 虚拟环境 Python 不存在: {venv_python}")
            return False, None
    else:
        print(f"❌ 虚拟环境不存在: {venv_dir}")
        print("\n请创建虚拟环境：")
        print(f"  cd {mediacrawler_dir}")
        print("  python3.11 -m venv .venv")
        print("  source .venv/bin/activate")
        print("  pip install -r requirements.txt")
        return False, None


def check_config_files(mediacrawler_dir):
    """检查配置文件"""
    print("\n" + "=" * 60)
    print("检查配置文件")
    print("=" * 60)

    config_dir = mediacrawler_dir / "config"
    base_config = config_dir / "base_config.py"
    env_file = mediacrawler_dir / ".env"

    all_good = True

    # 检查 base_config.py
    if base_config.exists():
        print(f"✅ base_config.py 存在")
    else:
        print(f"❌ base_config.py 不存在")
        all_good = False

    # 检查 .env
    if env_file.exists():
        print(f"✅ .env 存在")
    else:
        print(f"⚠️  .env 不存在（可选）")
        print("   提示: cp .env.example .env")

    # 检查 .env.example
    env_example = mediacrawler_dir / ".env.example"
    if env_example.exists():
        print(f"✅ .env.example 存在")
    else:
        print(f"⚠️  .env.example 不存在")

    return all_good


def check_dependencies(venv_python):
    """检查依赖包"""
    print("\n" + "=" * 60)
    print("检查依赖包")
    print("=" * 60)

    if not venv_python:
        print("❌ 无法检查依赖包（虚拟环境不存在）")
        return False

    # 关键依赖列表
    key_packages = [
        "playwright",
        "pandas",
        "requests",
        "openpyxl",
        "tqdm"
    ]

    all_installed = True

    for package in key_packages:
        result = subprocess.run(
            [venv_python, "-c", f"import {package}"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"✅ {package}")
        else:
            print(f"❌ {package} 未安装")
            all_installed = False

    if not all_installed:
        print("\n请安装依赖：")
        print("  cd ~/MediaCrawler")
        print("  source .venv/bin/activate")
        print("  pip install -r requirements.txt")

    return all_installed


def check_data_dir(mediacrawler_dir):
    """检查数据目录"""
    print("\n" + "=" * 60)
    print("检查数据目录")
    print("=" * 60)

    data_dir = mediacrawler_dir / "data"

    if data_dir.exists():
        print(f"✅ 数据目录存在: {data_dir}")

        # 检查各平台数据目录
        platforms = ["xhs", "douyin", "weibo", "bilibili", "baidu"]
        for platform in platforms:
            platform_dir = data_dir / platform
            if platform_dir.exists():
                json_count = len(list(platform_dir.glob("json/*.json")))
                print(f"  📁 {platform}: {json_count} 个 JSON 文件")

        return True
    else:
        print(f"⚠️  数据目录不存在，首次运行会自动创建")
        return True


def generate_report(results):
    """生成检查报告"""
    print("\n" + "=" * 60)
    print("检查报告")
    print("=" * 60)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    print(f"\n通过: {passed}/{total}")

    for check, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {check}: {status}")

    print("\n" + "=" * 60)

    if passed == total:
        print("✅ 所有检查通过，可以开始采集！")
        return True
    else:
        print("⚠️  部分检查失败，请按照提示修复问题")
        return False


def main():
    """主流程"""
    print("\n🔍 MediaCrawler 环境检查")
    print()

    results = {}
    venv_python = None

    # 1. 检查 Python 版本
    results["Python 版本"] = check_python_version()

    # 2. 检查 MediaCrawler 目录
    dir_exists, mediacrawler_dir = check_mediacrawler_dir()
    results["MediaCrawler 目录"] = dir_exists

    if mediacrawler_dir:
        # 3. 检查虚拟环境
        venv_exists, venv_python = check_virtual_environment(mediacrawler_dir)
        results["虚拟环境"] = venv_exists

        # 4. 检查配置文件
        results["配置文件"] = check_config_files(mediacrawler_dir)

        # 5. 检查依赖包
        if venv_python:
            results["依赖包"] = check_dependencies(venv_python)
        else:
            results["依赖包"] = False

        # 6. 检查数据目录
        check_data_dir(mediacrawler_dir)

    # 生成报告
    success = generate_report(results)

    # 如果检查通过，提示下一步
    if success and venv_python:
        print("\n📌 下一步：")
        print("  运行采集脚本:")
        print("  python3 scripts/run_crawler.py --platform xhs --keywords '关键词'")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
