#!/usr/bin/env python3
"""一键初始化 B站视频总结系统"""
import os
import subprocess
import sys
from pathlib import Path

# DeepSeek API Key (read from environment)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

def main():
    print("🚀 开始初始化 B站视频总结系统...")

    # 1. 设置环境变量到 ~/.zshrc
    print("\n🔑 设置 DeepSeek API Key...")
    zshrc_path = Path.home() / ".zshrc"
    env_line = f'export DEEPSEEK_API_KEY="{DEEPSEEK_API_KEY}"'

    try:
        existing_content = ""
        if zshrc_path.exists():
            existing_content = zshrc_path.read_text()

        # 检查是否已存在
        if "DEEPSEEK_API_KEY" in existing_content:
            print("✅ DEEPSEEK_API_KEY 已存在")
        else:
            with open(zshrc_path, 'a') as f:
                f.write(f'\n# B站视频总结系统\n{env_line}\n')
            print(f"✅ 已添加 DEEPSEEK_API_KEY 到 ~/.zshrc")
            print("   请运行: source ~/.zshrc 或重启终端")

    except Exception as e:
        print(f"⚠️  设置环境变量失败: {e}")
        print("   请手动添加到 ~/.zshrc:")
        print(f"   {env_line}")

    # 2. 安装依赖
    print("\n📦 安装依赖...")
    try:
        subprocess.run(['pip3', 'install', 'openai'], check=True)
        print("✅ 依赖安装成功")
    except subprocess.CalledProcessError:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'openai'], check=True)
            print("✅ 依赖安装成功")
        except:
            print("⚠️  pip install 失败，请手动运行: pip install openai")

    # 3. 创建目录
    print("\n📁 创建必要目录...")
    base_dir = Path(__file__).parent.parent
    for dir_name in ['subtitles', 'logs', 'backup']:
        dir_path = base_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"✅ 创建目录: {dir_path}")

    # 4. 设置定时任务
    print("\n⏰ 设置定时任务...")
    crontab_cmd = f"0 8 * * * cd {base_dir} && /usr/bin/python3 scripts/bilibili_summarizer.py --run >> scripts/logs/summarizer.log 2>&1"

    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        existing = result.stdout if result.returncode == 0 else ''

        if 'bilibili_summarizer' in existing:
            print("✅ 定时任务已存在")
        else:
            new_crontab = existing + '\n' + crontab_cmd + '\n'
            subprocess.run(['crontab', '-'], input=new_crontab, text=True)
            print("✅ 定时任务已设置：每天早上8点执行")

    except Exception as e:
        print(f"⚠️  设置定时任务失败: {e}")
        print("   请手动添加到 crontab:")
        print(f"   {crontab_cmd}")

    # 5. 设置当前环境变量（供当前会话使用）
    os.environ['DEEPSEEK_API_KEY'] = DEEPSEEK_API_KEY

    print("\n" + "=" * 50)
    print("✅ 初始化完成！")
    print("=" * 50)
    print("\n📌 使用方法:")
    print("   立即执行: python scripts/bilibili_summarizer.py --run")
    print("   查看日志: tail -f scripts/logs/summarizer.log")
    print("\n💡 提示: 如果这是首次设置，请运行 source ~/.zshrc")

    # 测试导入
    print("\n🧪 测试 AI 客户端...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        print("✅ AI 客户端测试成功")
    except Exception as e:
        print(f"⚠️  AI 客户端测试失败: {e}")

if __name__ == "__main__":
    main()
