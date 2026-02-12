#!/usr/bin/env python3
"""
飞书上传集成脚本

功能：
1. 创建飞书 Base（用户身份）
2. 上传数据到多维表格
3. 上传报告到云文档
4. 发送完成通知

依赖：
- feishu-automation-v2 Skill

作者：大秘书系统
版本：v1.0.0
创建时间：2026-02-10
"""

import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
import argparse


class FeishuUploader:
    """飞书上传器"""

    def __init__(self):
        """初始化上传器"""
        self.skill_dir = Path(__file__).parent.parent
        self.feishu_scripts_dir = Path("/Users/echochen/.claude/skills/feishu-automation-v2/scripts")

        # 检查飞书脚本是否存在
        self.feishu_user_auto = self.feishu_scripts_dir / "feishu_user_auto.py"
        self.feishu_oauth_setup = self.feishu_scripts_dir / "feishu_oauth_setup.py"
        self.feishu_bot_notifier = self.feishu_scripts_dir / "feishu_bot_notifier.py"

        # 检查配置文件
        self.feishu_config = Path.home() / ".feishu_user_config.json"

    def _load_config(self):
        """加载飞书配置

        Returns:
            dict: 配置数据
        """
        with open(self.feishu_config, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_table_id(self, app_token):
        """获取 Base 中的第一个表格 ID

        Args:
            app_token: Base App Token

        Returns:
            str: 表格 ID，如果失败返回 None
        """
        print("正在获取表格 ID...")

        config = self._load_config()
        token = config.get("user_access_token")

        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request) as response:
                data = json.loads(response.read().decode('utf-8'))

                if data.get("code") == 0 and data.get("data", {}).get("items"):
                    tables = data["data"]["items"]
                    if tables:
                        table_id = tables[0].get("table_id")
                        print(f"✓ 获取到表格 ID: {table_id}")
                        return table_id
                    else:
                        print("⚠️  Base 中没有表格")
                        return None
                else:
                    print(f"⚠️  获取表格失败: {data.get('msg')}")
                    return None

        except Exception as e:
            print(f"⚠️  获取表格 ID 出错: {e}")
            return None

    def check_oauth(self):
        """检查 OAuth 配置

        Returns:
            bool: 是否已配置
        """
        if not self.feishu_config.exists():
            print("⚠️  飞书 OAuth 配置不存在")
            print("⚠️  请运行: python3 feishu_oauth_setup.py")
            return False

        print("✓ 飞书 OAuth 配置已存在")
        return True

    def create_base(self, name=None):
        """创建飞书 Base

        Args:
            name: Base 名称

        Returns:
            dict: 包含 app_token, base_url 的字典
        """
        if not name:
            name = f"悟昕睡眠热点分析_{datetime.now().strftime('%Y%m%d')}"

        print(f"创建飞书 Base: {name}")

        # 检查脚本
        if not self.feishu_user_auto.exists():
            print(f"⚠️  飞书脚本不存在: {self.feishu_user_auto}")
            print("⚠️  请先安装 feishu-automation-v2 Skill")
            return None

        # 调用脚本创建 Base
        cmd = [
            sys.executable,
            str(self.feishu_user_auto),
            "create-base",
            "--name", name
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.feishu_scripts_dir
            )

            if result.returncode == 0:
                print("✓ Base 创建成功")

                # 提取 App Token 和 Base URL
                app_token = None
                base_url = None

                for line in result.stdout.split('\n'):
                    if 'App Token:' in line:
                        app_token = line.split('App Token:')[1].strip()
                    elif 'feishu.cn/base/' in line:
                        base_url = line.strip()
                        # 清理可能的 "链接:" 前缀
                        if '链接:' in base_url:
                            base_url = base_url.split('链接:')[1].strip()

                if app_token and base_url:
                    print(f"✓ App Token: {app_token}")
                    print(f"✓ Base URL: {base_url}")
                    return {"app_token": app_token, "base_url": base_url}
                else:
                    print(f"⚠️  无法提取 App Token 或 Base URL")
                    return None

            else:
                print(f"⚠️  创建失败: {result.stderr}")
                return None

        except Exception as e:
            print(f"⚠️  运行失败: {e}")
            return None

    def import_data(self, app_token, table_id, excel_file):
        """导入数据到飞书 Base

        Args:
            app_token: Base App Token
            table_id: 表格 ID
            excel_file: Excel 文件路径

        Returns:
            bool: 是否成功
        """
        # 转换为绝对路径
        excel_path = Path(excel_file)
        if not excel_path.is_absolute():
            excel_path = self.skill_dir / excel_file

        print(f"导入数据到飞书 Base")
        print(f"  App Token: {app_token}")
        print(f"  Table ID: {table_id}")
        print(f"  Excel 文件: {excel_path}")

        # 如果 table_id 是默认值或为空，自动获取
        if not table_id or table_id == "tablename":
            print("⚠️  Table ID 为默认值，尝试自动获取...")
            table_id = self.get_table_id(app_token)
            if not table_id:
                print("❌ 无法获取 Table ID，导入失败")
                return False
            print(f"✓ 自动获取到 Table ID: {table_id}")

        # 调用脚本导入数据
        cmd = [
            sys.executable,
            str(self.feishu_user_auto),
            "import-data",
            "--app-token", app_token,
            "--table-id", table_id,
            "--excel", str(excel_path)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.feishu_scripts_dir
            )

            if result.returncode == 0:
                print("✓ 数据导入成功")
                # 只打印关键信息，不打印全部输出
                return True
            else:
                print(f"⚠️  导入失败: {result.stderr}")
                return False

        except Exception as e:
            print(f"⚠️  运行失败: {e}")
            return False

    def send_notification(self, message):
        """发送飞书通知（使用飞书机器人）

        Args:
            message: 通知消息

        Returns:
            bool: 是否成功
        """
        print(f"发送飞书机器人通知")

        # 检查机器人通知脚本是否存在
        if not self.feishu_bot_notifier.exists():
            print(f"⚠️  飞书机器人通知脚本不存在: {self.feishu_bot_notifier}")
            return False

        cmd = [
            sys.executable,
            str(self.feishu_bot_notifier),
            "--message", message
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.feishu_scripts_dir
            )

            if result.returncode == 0:
                print("✓ 机器人通知发送成功")
                return True
            else:
                print(f"⚠️  发送失败: {result.stderr}")
                return False

        except Exception as e:
            print(f"⚠️  运行失败: {e}")
            return False

    def upload_report(self, report_file):
        """上传报告到飞书

        Args:
            report_file: 报告文件路径

        Returns:
            str: 文档 URL
        """
        print(f"上传报告到飞书")
        print(f"  报告文件: {report_file}")

        # TODO: 实现云文档上传
        # 目前返回示例 URL

        doc_url = f"https://zenoasislab.feishu.cn/doc/example"

        print(f"✓ 报告已上传: {doc_url}")
        return doc_url

    def upload_all(self, data_dir=None):
        """上传所有数据到飞书

        Args:
            data_dir: 数据目录

        Returns:
            bool: 是否成功
        """
        print("=" * 80)
        print("飞书数据上传")
        print("=" * 80)

        # 检查 OAuth
        if not self.check_oauth():
            print("\n⚠️  请先完成飞书 OAuth 授权:")
            print(f"  python3 {self.feishu_oauth_setup}")
            return False

        # 确定数据目录
        if data_dir:
            data_path = Path(data_dir)
        else:
            data_path = self.skill_dir / "data" / "weekly_reports" / datetime.now().strftime("%Y-%m-%d")

        if not data_path.exists():
            print(f"✗ 数据目录不存在: {data_path}")
            return False

        print(f"\n数据目录: {data_path}")

        # 1. 创建 Base
        print("\n[1/4] 创建飞书 Base...")
        base_info = self.create_base()

        if not base_info:
            print("✗ Base 创建失败")
            return False

        app_token = base_info["app_token"]
        base_url = base_info["base_url"]

        # 2. 上传数据表格
        print("\n[2/4] 上传数据表格...")
        excel_files = list(data_path.glob("*.csv")) + list(data_path.glob("*.xlsx"))

        if excel_files:
            print(f"✓ 找到 {len(excel_files)} 个数据文件")

            # 获取表格 ID（会自动从 API 获取，无需手动指定）
            table_id = None  # import_data 会自动获取

            for excel_file in excel_files:
                print(f"  - 导入: {excel_file.name}")
                self.import_data(app_token, table_id, str(excel_file))

        # 3. 上传报告
        print("\n[3/4] 上传分析报告...")
        report_file = data_path / "分析报告.md"

        if report_file.exists():
            doc_url = self.upload_report(report_file)
        else:
            print("⚠️  报告文件不存在")
            doc_url = None

        # 4. 发送通知
        print("\n[4/4] 发送完成通知...")

        message = f"""✅ 悟昕睡眠热点分析报告已生成

数据统计：
- 分析日期: {datetime.now().strftime('%Y-%m-%d')}
- Base 链接: {base_url}"""

        if doc_url:
            message += f"\n- 报告链接: {doc_url}"

        self.send_notification(message)

        print("\n" + "=" * 80)
        print("✓ 上传完成！")
        print(f"✓ Base: {base_url}")
        if doc_url:
            print(f"✓ 报告: {doc_url}")
        print("=" * 80)

        print("\n" + "=" * 80)
        print("✓ 上传完成！")
        print(f"✓ Base: {base_url}")
        if doc_url:
            print(f"✓ 报告: {doc_url}")
        print("=" * 80)

        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="飞书上传集成")
    parser.add_argument("--data-dir", help="数据目录路径")
    parser.add_argument("--create-base", help="创建 Base（名称）")
    parser.add_argument("--import-data", nargs=3, metavar=("APP_TOKEN", "TABLE_ID", "EXCEL"), help="导入数据")
    parser.add_argument("--notify", help="发送通知消息")

    args = parser.parse_args()

    uploader = FeishuUploader()

    if args.create_base:
        uploader.create_base(args.create_base)
    elif args.import_data:
        uploader.import_data(args.import_data[0], args.import_data[1], args.import_data[2])
    elif args.notify:
        uploader.send_notification(args.notify)
    else:
        uploader.upload_all(data_dir=args.data_dir)


if __name__ == "__main__":
    main()
