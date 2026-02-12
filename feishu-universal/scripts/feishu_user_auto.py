#!/usr/bin/env python3
"""
飞书自动化工具 v2.0 - 用户身份版
使用 user_access_token 创建资源，确保用户拥有完整权限

核心改进：
- 使用 user_access_token 而不是 app_access_token
- 创建的资源，用户自动成为所有者
- 支持自动刷新 token
- 使用机器人身份发送通知（混合模式）
"""

import requests
import json
import pandas as pd
import time
import os
from datetime import datetime, timedelta
from pathlib import Path


class FeishuBotNotifier:
    """飞书机器人通知器（使用应用身份发送消息）"""

    def __init__(self, app_id, app_secret, user_open_id):
        """初始化机器人通知器"""
        self.app_id = app_id
        self.app_secret = app_secret
        self.user_open_id = user_open_id
        self.app_access_token = None
        self.base_url = "https://open.feishu.cn/open-apis"
        self._get_app_token()

    def _get_app_token(self):
        """获取 app_access_token"""
        url = f"{self.base_url}/auth/v3/app_access_token/internal"
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                self.app_access_token = data.get("app_access_token")

    def send_notification(self, content):
        """发送通知消息"""
        url = f"{self.base_url}/im/v1/messages?receive_id_type=open_id"
        headers = {
            "Authorization": f"Bearer {self.app_access_token}",
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


class FeishuUserClient:
    """飞书用户身份客户端"""

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
            raise FileNotFoundError(f"配置文件不存在: {config_path}\n请先完成 OAuth 授权流程")

        self.app_id = self.config.get('app_id')
        self.app_secret = self.config.get('app_secret')
        self.user_access_token = self.config.get('user_access_token')
        self.refresh_token = self.config.get('refresh_token')
        self.user_open_id = self.config.get('user_open_id')
        self.expires_at = self.config.get('expires_at', 0)
        self.auth_time = self.config.get('auth_time', int(time.time()))  # 授权时间

        self.app_access_token = None
        self.base_url = "https://open.feishu.cn/open-apis"

        # 检查 refresh_token 是否即将过期（30天有效期）
        self._check_refresh_token_expiry()

        # 检查并刷新 token
        self._ensure_valid_token()

    def _check_refresh_token_expiry(self):
        """检查 refresh_token 是否即将过期，提前提醒"""
        now = int(time.time())
        # refresh_token 有效期 30 天
        refresh_expires_at = self.auth_time + 30 * 24 * 60 * 60
        remaining_days = (refresh_expires_at - now) / (24 * 60 * 60)

        # 创建机器人通知器
        notifier = FeishuBotNotifier(self.app_id, self.app_secret, self.user_open_id)

        if remaining_days < 3:
            print(f"\n{'='*60}")
            print(f"⚠️  警告：refresh_token 即将过期（剩余 {remaining_days:.1f} 天）")
            print(f"{'='*60}")
            print(f"为了避免影响使用，建议尽快重新授权：")
            print(f"  python3 test_feishu_oauth.py")
            print(f"或运行自动版：")
            print(f"  python3 feishu_oauth_setup.py")
            print(f"{'='*60}\n")

            # 发送飞书消息通知（使用机器人身份）
            try:
                expire_date = datetime.fromtimestamp(refresh_expires_at).strftime('%Y-%m-%d')
                message = f"""⚠️ 飞书 Token 即将过期提醒

你的飞书 refresh_token 即将过期：
- 剩余天数：{remaining_days:.1f} 天
- 过期时间：{expire_date}

建议尽快重新授权：
  python3 feishu_oauth_setup.py

避免影响飞书自动化功能的使用。"""
                if notifier.send_notification(message):
                    print("✓ 已发送飞书消息提醒")
            except Exception as e:
                print(f"⚠️  发送飞书消息失败: {e}")

        elif remaining_days < 7:
            print(f"💡 提醒：refresh_token 将在 {remaining_days:.1f} 天后过期")

            # 发送飞书消息提醒（使用机器人身份）
            try:
                expire_date = datetime.fromtimestamp(refresh_expires_at).strftime('%Y-%m-%d')
                message = f"""💡 飞书 Token 过期提醒

你的飞书 refresh_token 将在 {remaining_days:.1f} 天后过期：
- 过期时间：{expire_date}

建议本周内重新授权：
  python3 feishu_oauth_setup.py"""
                if notifier.send_notification(message):
                    print("✓ 已发送飞书消息提醒")
            except Exception as e:
                print(f"⚠️  发送飞书消息失败: {e}")

    def get_app_access_token(self):
        """获取 app_access_token（用于刷新 user_access_token）"""
        url = f"{self.base_url}/auth/v3/app_access_token/internal"

        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                self.app_access_token = data.get("app_access_token")
                return self.app_access_token
            else:
                raise Exception(f"获取 app_access_token 失败: {data.get('msg')}")
        else:
            raise Exception(f"请求失败: {response.status_code}")

    def _ensure_valid_token(self):
        """确保 user_access_token 有效"""
        now = time.time()

        # 如果 token 还有 5 分钟过期，提前刷新
        if self.expires_at - now < 300:
            print("⚠️  user_access_token 即将过期，正在刷新...")
            self.refresh_user_token()

    def refresh_user_token(self):
        """刷新 user_access_token"""
        if not self.refresh_token:
            raise Exception("没有 refresh_token，无法刷新。请重新执行 OAuth 授权")

        # 先获取 app_access_token
        if not self.app_access_token:
            self.get_app_access_token()

        url = f"{self.base_url}/authen/v1/oidc/refresh_access_token"

        headers = {
            "Authorization": f"Bearer {self.app_access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                token_data = data.get("data")

                # 更新 token
                self.user_access_token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token")
                self.expires_at = time.time() + token_data.get("expires_in", 7200)

                # 保存到配置文件
                self._save_config()

                print(f"✓ Token 刷新成功，有效期至: {datetime.fromtimestamp(self.expires_at)}")
            else:
                raise Exception(f"刷新 token 失败: {data.get('msg')}")
        else:
            raise Exception(f"请求失败: {response.status_code}")

    def _save_config(self):
        """保存配置到文件"""
        config_path = os.path.expanduser("~/.feishu_user_config.json")

        self.config['user_access_token'] = self.user_access_token
        self.config['refresh_token'] = self.refresh_token
        self.config['expires_at'] = self.expires_at

        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def create_base(self, name, folder_token=""):
        """创建多维表格 Base（以用户身份）

        Args:
            name: Base 名称
            folder_token: 父文件夹 token（可选）

        Returns:
            dict: Base 信息
        """
        self._ensure_valid_token()

        url = f"{self.base_url}/bitable/v1/apps"

        headers = {
            "Authorization": f"Bearer {self.user_access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "name": name,
            "folder_token": folder_token
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                app = data.get("data", {}).get("app")
                print(f"✓ 成功创建 Base: {name}")
                print(f"  App Token: {app.get('app_token')}")
                print(f"  所有者: {self.user_open_id}（你）")
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
        self._ensure_valid_token()

        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables"

        headers = {
            "Authorization": f"Bearer {self.user_access_token}",
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

    def get_table_fields(self, app_token, table_id):
        """获取表格字段信息

        Args:
            app_token: Base token
            table_id: 表格 ID

        Returns:
            list: 字段列表
        """
        self._ensure_valid_token()

        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"

        headers = {
            "Authorization": f"Bearer {self.user_access_token}",
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

    def delete_default_fields(self, app_token, table_id, keep_first=True):
        """删除表格的默认字段

        Args:
            app_token: Base token
            table_id: 表格 ID
            keep_first: 是否保留第一个字段（主键字段无法删除）

        Returns:
            int: 删除的字段数量
        """
        self._ensure_valid_token()

        fields = self.get_table_fields(app_token, table_id)
        deleted_count = 0

        # 默认字段名称（飞书新建表格时的默认字段）
        default_field_names = ["文本", "单选", "日期", "附件"]

        for field in fields:
            if field is None:
                continue
            field_name = field.get("field_name", "")
            field_id = field.get("field_id")
            property_data = field.get("property")
            is_primary = property_data.get("primary", False) if property_data else False

            # 跳过主键字段
            if is_primary or (keep_first and deleted_count == 0 and field_name in default_field_names):
                continue

            # 只删除默认字段
            if field_name in default_field_names:
                url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}"

                headers = {
                    "Authorization": f"Bearer {self.user_access_token}",
                    "Content-Type": "application/json"
                }

                response = requests.delete(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 0:
                        deleted_count += 1
                        print(f"✓ 已删除默认字段: {field_name}")
                    else:
                        print(f"⚠️  删除字段失败 {field_name}: {data.get('msg')}")
                else:
                    print(f"⚠️  删除字段请求失败: {response.status_code}")

        return deleted_count

    def create_fields_from_excel(self, app_token, table_id, excel_path):
        """从 Excel 列名推断并创建字段

        Args:
            app_token: Base token
            table_id: 表格 ID
            excel_path: Excel 文件路径

        Returns:
            list: 创建的字段列表
        """
        import pandas as pd

        # 读取 Excel 列名
        df = pd.read_excel(excel_path, nrows=0)
        columns = list(df.columns)

        print(f"从 Excel 推断字段: {columns}")

        # 推断字段类型
        created_fields = []
        for col in columns:
            # 根据列名推断类型
            col_lower = str(col).lower()

            if any(keyword in col_lower for keyword in ["链接", "url", "链接", "网址", "http"]):
                field_type = 1  # 文本（URL 字段在 API 中有限制）
            elif any(keyword in col_lower for keyword in ["序号", "id", "编号"]):
                field_type = 2  # 数字
            elif any(keyword in col_lower for keyword in ["时间", "日期", "time", "date"]):
                field_type = 5  # 日期
            elif any(keyword in col_lower for keyword in ["是", "否", "是否", "true", "false"]):
                field_type = 3  # 单选
            else:
                # 尝试读取一些数据来推断类型
                sample_df = pd.read_excel(excel_path, usecols=[col])
                sample_values = sample_df[col].dropna().head(10)

                if sample_values.empty:
                    field_type = 1  # 默认文本
                elif all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in sample_values):
                    field_type = 2  # 数字
                else:
                    field_type = 1  # 文本

            # 创建字段
            url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"

            headers = {
                "Authorization": f"Bearer {self.user_access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "field_name": str(col),
                "type": field_type
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    created_fields.append(str(col))
                    print(f"✓ 创建字段: {str(col)} (类型: {field_type})")
                else:
                    print(f"⚠️  创建字段失败 {str(col)}: {data.get('msg')}")
            else:
                print(f"⚠️  创建字段请求失败: {response.status_code}")

        return created_fields

    def list_table_rows(self, app_token, table_id, page_size=100):
        """获取表格数据

        Args:
            app_token: Base token
            table_id: 表格 ID
            page_size: 每页数据量

        Returns:
            list: 表格数据列表
        """
        self._ensure_valid_token()

        all_rows = []
        page_token = None

        while True:
            url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"

            headers = {
                "Authorization": f"Bearer {self.user_access_token}",
                "Content-Type": "application/json"
            }

            params = {
                "page_size": page_size
            }
            if page_token:
                params["page_token"] = page_token

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    items = data.get("data", {}).get("items", [])
                    all_rows.extend(items)

                    # 检查是否还有更多数据
                    has_more = data.get("data", {}).get("has_more", False)
                    if has_more:
                        page_token = data.get("data", {}).get("page_token")
                    else:
                        break
                else:
                    raise Exception(f"查询失败: {data.get('code')} - {data.get('msg')}")
            else:
                raise Exception(f"请求失败: {response.status_code}")

        return all_rows

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
        self._ensure_valid_token()

        total = len(records)
        created = 0
        failed = 0

        print(f"开始导入 {total} 条记录...")

        # 分批处理
        for i in range(0, total, batch_size):
            batch = records[i:i + batch_size]

            url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"

            headers = {
                "Authorization": f"Bearer {self.user_access_token}",
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

        # 发送飞书消息通知（使用机器人身份）
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
                notifier = FeishuBotNotifier(self.app_id, self.app_secret, self.user_open_id)
                if notifier.send_notification(message):
                    print("✓ 已发送飞书消息通知")
        except Exception as e:
            print(f"⚠️  发送飞书消息失败: {e}")

        return created

    def send_message(self, receive_id, content, msg_type="text", receive_id_type="open_id"):
        """发送消息到用户或群组

        Args:
            receive_id: 接收者 ID
            content: 消息内容
            msg_type: 消息类型（text, post, interactive）
            receive_id_type: 接收者 ID 类型（open_id, user_id, union_id, chat_id）

        Returns:
            dict: 消息信息
        """
        self._ensure_valid_token()

        # receive_id_type 是 URL 参数
        url = f"{self.base_url}/im/v1/messages?receive_id_type={receive_id_type}"

        headers = {
            "Authorization": f"Bearer {self.user_access_token}",
            "Content-Type": "application/json"
        }

        if msg_type == "text":
            payload_content = json.dumps({"text": content})
        else:
            payload_content = content

        payload = {
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": payload_content
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                return data.get("data")
            else:
                raise Exception(f"发送消息失败: {data.get('msg')}")
        else:
            raise Exception(f"请求失败: {response.status_code}")

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
            # 处理 NaN 值
            record = {}
            for col, val in row.items():
                if pd.notna(val):
                    # 处理特殊类型
                    if hasattr(pd, 'datetime64') and isinstance(val, (pd.Timestamp, pd.datetime64)):
                        record[str(col)] = val.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(val, pd.Timestamp):
                        record[str(col)] = val.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(val, (int, float)):
                        # 检查是否为 NaN
                        if not pd.isna(val):
                            record[str(col)] = float(val) if isinstance(val, float) else int(val)
                    else:
                        record[str(col)] = str(val)

            if record:  # 只添加非空记录
                records.append({"fields": record})

        print(f"转换为飞书格式: {len(records)} 条有效记录")

        # 批量导入
        return self.batch_create_records(app_token, table_id, records)

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

        # 3. 删除默认字段（如果需要）
        if clean_defaults:
            print(f"\n3️⃣  清理默认字段...")
            deleted = self.delete_default_fields(app_token, table_id)
            print(f"✓ 已删除 {deleted} 个默认字段")

        # 4. 从 Excel 创建字段
        print(f"\n4️⃣  创建自定义字段...")
        created_fields = self.create_fields_from_excel(app_token, table_id, excel_path)
        print(f"✓ 已创建 {len(created_fields)} 个字段")

        # 5. 导入数据
        print(f"\n5️⃣  导入数据...")
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

    parser = argparse.ArgumentParser(description="飞书自动化工具 - 用户身份版")
    parser.add_argument("action", choices=["create-base", "import-data", "notify", "create-and-import"],
                        help="操作类型")
    parser.add_argument("--name", help="Base 名称")
    parser.add_argument("--app-token", help="Base token")
    parser.add_argument("--table-id", help="表格 ID")
    parser.add_argument("--excel", help="Excel 文件路径")
    parser.add_argument("--message", help="消息内容")
    parser.add_argument("--keep-defaults", action="store_true",
                        help="保留默认字段（不删除）")

    args = parser.parse_args()

    try:
        client = FeishuUserClient()

        if args.action == "create-base":
            if not args.name:
                print("错误: 请提供 --name 参数")
                return

            result = client.create_base(args.name)
            print(f"\n✅ Base 创建成功！")
            print(f"链接: https://zenoasislab.feishu.cn/base/{result.get('app_token')}")
            print(f"所有者: {client.user_open_id}（你）")

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

        elif args.action == "create-and-import":
            if not args.name or not args.excel:
                print("错误: 请提供 --name 和 --excel 参数")
                return

            result = client.create_and_import(
                args.name,
                args.excel,
                clean_defaults=not args.keep_defaults
            )
            print(f"\n✅ 一键完成！")
            print(f"   Base: {args.name}")
            print(f"   链接: https://zenoasislab.feishu.cn/base/{result['app_token']}")
            print(f"   记录: {result['count']} 条")

        elif args.action == "notify":
            if not args.message:
                print("错误: 请提供 --message 参数")
                return

            # 发送给自己
            client.send_message(client.user_open_id, args.message)
            print(f"\n✅ 通知发送成功！")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
