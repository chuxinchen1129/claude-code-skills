#!/usr/bin/env python3
"""
飞书自动化工具 v3.0 - 统一 tenant_access_token 版本

核心改进：
- 统一使用 tenant_access_token (app_access_token/internal)
- 删除 OAuth 流程，无需人工授权
- 支持创建新 Base
- 支持直接导入到目标表格
- 字段自动创建
"""

import requests
import json
import pandas as pd
import time
import os
from datetime import datetime
from pathlib import Path


class FeishuBotNotifier:
    """飞书机器人通知器（使用应用身份发送消息）"""

    def __init__(self, app_id, app_secret, user_open_id):
        """初始化机器人通知器"""
        self.app_id = app_id
        self.app_secret = app_secret
        self.user_open_id = user_open_id
        self.tenant_access_token = None
        self.base_url = "https://open.feishu.cn/open-apis"
        self._get_tenant_token()

    def _get_tenant_token(self):
        """获取 tenant_access_token"""
        url = f"{self.base_url}/auth/v3/app_access_token/internal"
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                self.tenant_access_token = data.get("app_access_token")
                return
        raise Exception(f"获取 tenant_access_token 失败")

    def send_notification(self, content):
        """发送通知消息"""
        # 确保token有效
        if not self.tenant_access_token:
            self._get_tenant_token()

        url = f"{self.base_url}/im/v1/messages?receive_id_type=open_id"
        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "receive_id": self.user_open_id,
            "msg_type": "text",
            "content": json.dumps({"text": content})
        }
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                return True
        return False


class FeishuTenantClient:
    """飞书 tenant_access_token 客户端"""

    def __init__(self, config_path="~/.feishu_user_config.json"):
        """初始化客户端

        Args:
            config_path: 配置文件路径
        """
        config_path = os.path.expanduser(config_path)

        # 加载配置
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        self.app_id = self.config.get('app_id')
        self.app_secret = self.config.get('app_secret')
        self.user_open_id = self.config.get('user_open_id')
        self.chat_id = self.config.get('chat_id', self.user_open_id)  # 兼容旧配置
        self.folder_token = self.config.get('folder_token', '')
        self.target_table = self.config.get('target_table', {})

        self.tenant_access_token = None
        self.base_url = "https://open.feishu.cn/open-apis"

        # 初始化时获取 token
        self._get_tenant_token()

        # 创建通知器
        self.notifier = FeishuBotNotifier(self.app_id, self.app_secret, self.user_open_id)

    def _get_tenant_token(self):
        """获取 tenant_access_token"""
        url = f"{self.base_url}/auth/v3/app_access_token/internal"

        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                self.tenant_access_token = data.get("app_access_token")
                return
            else:
                raise Exception(f"获取 tenant_access_token 失败: {data.get('msg')}")
        else:
            raise Exception(f"请求失败: {response.status_code}")

    def _ensure_token(self):
        """确保 token 有效（tenant_token 2小时有效，可以重新获取）"""
        if not self.tenant_access_token:
            self._get_tenant_token()

    # ==================== Base 操作 ====================

    def create_base(self, name, folder_token=""):
        """创建多维表格 Base（使用应用身份）

        Args:
            name: Base 名称
            folder_token: 父文件夹 token（可选）

        Returns:
            dict: Base 信息
        """
        self._ensure_token()

        url = f"{self.base_url}/bitable/v1/apps"

        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "name": name,
        }

        # 如果指定了 folder_token，添加到 payload
        if folder_token:
            payload["folder_token"] = folder_token
        elif self.folder_token:
            payload["folder_token"] = self.folder_token

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                app = data.get("data", {}).get("app")
                print(f"✓ 成功创建 Base: {name}")
                print(f"  App Token: {app.get('app_token')}")
                print(f"  所有者: 应用（使用 tenant_access_token）")
                return app
            else:
                raise Exception(f"创建 Base 失败: {data.get('msg')}")
        else:
            raise Exception(f"请求失败: {response.status_code}")

    def get_base_tables(self, app_token):
        """获取 Base 中的所有表格

        Args:
            app_token: Base token

        Returns:
            list: 表格列表
        """
        self._ensure_token()

        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables"

        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                tables = data.get("data", {}).get("items", [])
                return tables
            else:
                raise Exception(f"获取表格列表失败: {data.get('msg')}")
        else:
            raise Exception(f"请求失败: {response.status_code}")

    # ==================== 字段操作 ====================

    def get_table_fields(self, app_token, table_id):
        """获取表格字段信息

        Args:
            app_token: Base token
            table_id: 表格 ID

        Returns:
            list: 字段列表
        """
        self._ensure_token()

        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"

        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                fields = data.get("data", {}).get("items", [])
                return fields
            else:
                raise Exception(f"获取字段信息失败: {data.get('msg')}")
        else:
            raise Exception(f"请求失败: {response.status_code}")

    def create_field(self, app_token, table_id, field_name, field_type=1):
        """创建字段

        Args:
            app_token: Base token
            table_id: 表格 ID
            field_name: 字段名称
            field_type: 字段类型 (1=文本, 2=数字, 3=单选, 4=多选, 5=日期, 17=附件)

        Returns:
            dict: 创建的字段信息
        """
        self._ensure_token()

        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"

        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "field_name": field_name,
            "type": field_type
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                field = data.get("data", {}).get("field")
                return field
            else:
                raise Exception(f"创建字段失败: {data.get('msg')}")
        else:
            raise Exception(f"请求失败: {response.status_code}")

    def create_fields_from_excel(self, app_token, table_id, excel_path):
        """从 Excel 列名推断并创建字段

        Args:
            app_token: Base token
            table_id: 表格 ID
            excel_path: Excel 文件路径

        Returns:
            list: 创建的字段列表
        """
        # 读取 Excel 列名
        df = pd.read_excel(excel_path, nrows=0)
        columns = list(df.columns)

        # 获取现有字段
        existing_fields = self.get_table_fields(app_token, table_id)
        existing_field_names = {f.get("field_name") for f in existing_fields}

        print(f"从 Excel 推断字段: {columns}")
        print(f"现有字段: {existing_field_names}")

        # 推断字段类型
        created_fields = []
        for col in columns:
            col_str = str(col)

            # 跳过已存在的字段
            if col_str in existing_field_names:
                print(f"⊙ 字段已存在，跳过: {col_str}")
                continue

            # 根据列名推断类型
            col_lower = col_str.lower()

            if any(keyword in col_lower for keyword in ["链接", "url", "网址", "http"]):
                field_type = 1  # 文本
            elif any(keyword in col_lower for keyword in ["序号", "id", "编号"]):
                field_type = 2  # 数字
            elif any(keyword in col_lower for keyword in ["时间", "日期", "time", "date"]):
                field_type = 5  # 日期
            elif any(keyword in col_lower for keyword in ["是", "否", "是否"]):
                field_type = 3  # 单选
            elif any(keyword in col_lower for keyword in ["封面", "图片", "附件", "file", "image"]):
                field_type = 17  # 附件
            else:
                # 尝试读取一些数据来推断类型
                try:
                    sample_df = pd.read_excel(excel_path, usecols=[col])
                    sample_values = sample_df[col].dropna().head(10)

                    if sample_values.empty:
                        field_type = 1  # 默认文本
                    elif all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in sample_values):
                        field_type = 2  # 数字
                    else:
                        field_type = 1  # 文本
                except:
                    field_type = 1  # 默认文本

            # 创建字段
            try:
                field = self.create_field(app_token, table_id, col_str, field_type)
                created_fields.append(col_str)
                print(f"✓ 创建字段: {col_str} (类型: {field_type})")
            except Exception as e:
                print(f"⚠️  创建字段失败 {col_str}: {e}")

        return created_fields

    # ==================== 数据操作 ====================

    def batch_create_records(self, app_token, table_id, records, batch_size=50):
        """批量创建记录

        Args:
            app_token: Base token
            table_id: 表格 ID
            records: 记录列表 [{"fields": {...}}, ...]
            batch_size: 每批数量（最大 500）

        Returns:
            int: 成功创建的记录数
        """
        self._ensure_token()

        total = len(records)
        created = 0
        failed = 0

        print(f"开始导入 {total} 条记录...")

        # 分批处理
        for i in range(0, total, batch_size):
            batch = records[i:i + batch_size]

            url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"

            headers = {
                "Authorization": f"Bearer {self.tenant_access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "records": batch
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    batch_created = len(data.get("data", {}).get("records", []))
                    created += batch_created
                    print(f"✓ 批次 {i//batch_size + 1}: {batch_created} 条记录")
                else:
                    print(f"✗ 批次 {i//batch_size + 1} 失败: {data.get('msg')}")
                    failed += len(batch)
            else:
                print(f"✗ 批次 {i//batch_size + 1} 请求失败: {response.status_code}")
                failed += len(batch)

            # 延迟避免超限
            time.sleep(0.5)

        print(f"\n导入完成: {created} 条成功, {failed} 条失败")

        # 发送飞书消息通知
        try:
            completion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"""✅ 飞书数据导入完成

导入统计：
- 成功：{created} 条
- 失败：{failed} 条
- 完成时间：{completion_time}

Base 链接：
https://zenoasislab.feishu.cn/base/{app_token}"""

            if created > 0:
                if self.notifier.send_notification(message):
                    print("✓ 已发送飞书消息通知")
        except Exception as e:
            print(f"⚠️  发送飞书消息失败: {e}")

        return created

    def import_excel_to_feishu(self, app_token, table_id, excel_path):
        """从 Excel 导入数据到飞书

        Args:
            app_token: Base token
            table_id: 表格 ID
            excel_path: Excel 文件路径

        Returns:
            int: 导入的记录数
        """
        # 读取 Excel
        print(f"正在读取 Excel 文件: {excel_path}")
        df = pd.read_excel(excel_path)

        print(f"Excel 数据: {len(df)} 行, {len(df.columns)} 列")
        print(f"列名: {list(df.columns)}")

        # 转换为飞书格式
        records = []
        for _, row in df.iterrows():
            record = {}
            for col, val in row.items():
                if pd.notna(val):
                    # 处理特殊类型
                    if isinstance(val, pd.Timestamp):
                        record[str(col)] = val.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(val, (int, float)):
                        record[str(col)] = float(val) if isinstance(val, float) and not val.is_integer() else int(val) if isinstance(val, (int, float)) else str(val)
                    else:
                        record[str(col)] = str(val)

            if record:  # 只添加非空记录
                records.append({"fields": record})

        print(f"转换为飞书格式: {len(records)} 条有效记录")

        # 批量导入
        return self.batch_create_records(app_token, table_id, records)

    # ==================== 目标表格操作 ====================

    def import_to_target_table(self, excel_path, create_fields=True):
        """直接导入到配置的目标表格

        Args:
            excel_path: Excel 文件路径
            create_fields: 是否自动创建字段

        Returns:
            int: 导入的记录数
        """
        if not self.target_table:
            raise Exception("未配置 target_table，请在配置文件中设置")

        app_token = self.target_table.get('app_token')
        table_id = self.target_table.get('table_id')
        table_name = self.target_table.get('name', '目标表格')

        print(f"📋 导入到目标表格: {table_name}")
        print(f"   App Token: {app_token}")
        print(f"   Table ID: {table_id}")

        # 自动创建字段
        if create_fields:
            print(f"\n🔧 检查并创建字段...")
            created_fields = self.create_fields_from_excel(app_token, table_id, excel_path)
            print(f"✓ 新增 {len(created_fields)} 个字段")

        # 导入数据
        print(f"\n📊 导入数据...")
        count = self.import_excel_to_feishu(app_token, table_id, excel_path)

        return count

    # ==================== 一键操作 ====================

    def create_and_import(self, base_name, excel_path, clean_defaults=True):
        """一键创建 Base 并导入数据

        Args:
            base_name: Base 名称
            excel_path: Excel 文件路径
            clean_defaults: 是否删除默认字段

        Returns:
            dict: 包含 app_token, table_id, count 的结果字典
        """
        print(f"🚀 开始一键创建并导入流程")
        print(f"   Base 名称: {base_name}")
        print(f"   Excel 文件: {excel_path}")

        # 1. 创建 Base
        print(f"\n1️⃣  创建 Base...")
        app = self.create_base(base_name)
        app_token = app.get('app_token')
        print(f"✓ Base 已创建")

        # 2. 获取表格列表
        print(f"\n2️⃣  获取表格信息...")
        tables = self.get_base_tables(app_token)
        if not tables:
            raise Exception("Base 中没有表格")

        table_id = tables[0].get('table_id')
        print(f"✓ 表格 ID: {table_id}")

        # 3. 从 Excel 创建字段
        print(f"\n3️⃣  创建字段...")
        created_fields = self.create_fields_from_excel(app_token, table_id, excel_path)
        print(f"✓ 已创建 {len(created_fields)} 个字段")

        # 4. 导入数据
        print(f"\n4️⃣  导入数据...")
        count = self.import_excel_to_feishu(app_token, table_id, excel_path)

        print(f"\n✅ 一键创建并导入完成！")
        print(f"   Base 链接: https://zenoasislab.feishu.cn/base/{app_token}")
        print(f"   导入记录: {count} 条")

        return {
            "app_token": app_token,
            "table_id": table_id,
            "count": count
        }


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="飞书自动化工具 v3.0 - tenant_access_token 版本")
    parser.add_argument("action", choices=["create-base", "import-data", "import-to-target", "create-and-import", "test"],
                        help="操作类型")
    parser.add_argument("--name", help="Base 名称")
    parser.add_argument("--app-token", help="Base token")
    parser.add_argument("--table-id", help="表格 ID")
    parser.add_argument("--excel", help="Excel 文件路径")
    parser.add_argument("--no-create-fields", action="store_true",
                        help="不自动创建字段")

    args = parser.parse_args()

    try:
        client = FeishuTenantClient()

        if args.action == "test":
            print("=" * 60)
            print("飞书配置测试")
            print("=" * 60)
            print(f"✓ 配置文件加载成功")
            print(f"  App ID: {client.app_id}")
            print(f"  User Open ID: {client.user_open_id}")
            print(f"  Chat ID: {client.chat_id}")
            print(f"  Folder Token: {client.folder_token or '未设置'}")
            print(f"  目标表格: {client.target_table.get('name', '未设置')}")
            print(f"\n✓ Tenant Token 获取成功: {client.tenant_access_token[:20]}...")
            print("=" * 60)

        elif args.action == "create-base":
            if not args.name:
                print("错误: 请提供 --name 参数")
                return

            result = client.create_base(args.name)
            print(f"\n✅ Base 创建成功！")
            print(f"链接: https://zenoasislab.feishu.cn/base/{result.get('app_token')}")
            print(f"所有者: 应用（使用 tenant_access_token）")

        elif args.action == "import-data":
            if not args.app_token or not args.table_id or not args.excel:
                print("错误: 请提供 --app-token, --table-id, --excel 参数")
                return

            count = client.import_excel_to_feishu(
                args.app_token,
                args.table_id,
                args.excel
            )
            print(f"\n✅ 数据导入完成！共导入 {count} 条记录")

        elif args.action == "import-to-target":
            if not args.excel:
                print("错误: 请提供 --excel 参数")
                return

            count = client.import_to_target_table(
                args.excel,
                create_fields=not args.no_create_fields
            )
            print(f"\n✅ 导入到目标表格完成！共导入 {count} 条记录")

        elif args.action == "create-and-import":
            if not args.name or not args.excel:
                print("错误: 请提供 --name 和 --excel 参数")
                return

            result = client.create_and_import(args.name, args.excel)
            print(f"\n✅ 一键完成！")
            print(f"   Base: {args.name}")
            print(f"   链接: https://zenoasislab.feishu.cn/base/{result['app_token']}")
            print(f"   记录: {result['count']} 条")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
