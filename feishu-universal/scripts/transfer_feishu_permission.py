#!/usr/bin/env python3
"""
飞书多维表格权限转移工具
用于将飞书 Base 的所有权从机器人转移到用户
"""

import requests
import json
import sys


class FeishuPermissionTransfer:
    def __init__(self, app_id, app_secret):
        """初始化飞书权限转移客户端

        Args:
            app_id: 飞书应用的 App ID
            app_secret: 飞书应用的 App Secret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.tenant_access_token = None
        self.base_url = "https://open.feishu.cn/open-apis"

    def get_tenant_access_token(self):
        """获取 tenant_access_token"""
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"

        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                self.tenant_access_token = data.get("tenant_access_token")
                print(f"✓ 成功获取 tenant_access_token")
                return self.tenant_access_token
            else:
                print(f"✗ 获取 token 失败: {data.get('code')} - {data.get('msg')}")
                return None
        else:
            print(f"✗ 请求失败: {response.status_code}")
            return None

    def get_base_info(self, app_token):
        """获取 Base 信息

        Args:
            app_token: 多维表格的 app_token

        Returns:
            dict: Base 信息
        """
        if not self.tenant_access_token:
            self.get_tenant_access_token()

        url = f"{self.base_url}/bitable/v1/apps/{app_token}"

        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                return data.get("data")
            else:
                print(f"✗ 获取 Base 信息失败: {data.get('code')} - {data.get('msg')}")
                return None
        else:
            print(f"✗ 请求失败: {response.status_code}")
            return None

    def get_base_permission(self, app_token):
        """获取 Base 权限信息

        Args:
            app_token: 多维表格的 app_token

        Returns:
            dict: 权限信息
        """
        if not self.tenant_access_token:
            self.get_tenant_access_token()

        url = f"{self.base_url}/bitable/v1/apps/{app_token}/permission"

        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                return data.get("data")
            else:
                print(f"✗ 获取权限信息失败: {data.get('code')} - {data.get('msg')}")
                return None
        else:
            print(f"✗ 请求失败: {response.status_code}")
            return None

    def add_base_owner(self, app_token, user_open_id):
        """添加用户为 Base 所有者

        Args:
            app_token: 多维表格的 app_token
            user_open_id: 用户的 Open ID

        Returns:
            dict: 操作结果
        """
        if not self.tenant_access_token:
            self.get_tenant_access_token()

        url = f"{self.base_url}/bitable/v1/apps/{app_token}/permission/role"

        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "member_type": "user",
            "member_id": user_open_id,
            "perm": "view",  # 先给予查看权限
            "type": "base"
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print(f"✓ 成功添加用户权限")
                return data.get("data")
            else:
                print(f"✗ 添加用户权限失败: {data.get('code')} - {data.get('msg')}")
                return None
        else:
            print(f"✗ 请求失败: {response.status_code}")
            return None

    def transfer_base_ownership(self, app_token, user_open_id):
        """转移 Base 所有权给用户

        注意：飞书 API 可能不支持直接转移所有权，需要通过管理后台操作

        Args:
            app_token: 多维表格的 app_token
            user_open_id: 用户的 Open ID

        Returns:
            dict: 操作结果
        """
        # 先获取当前权限信息
        print(f"\n=== 获取当前权限信息 ===")
        perm_info = self.get_base_permission(app_token)
        if perm_info:
            print(f"当前权限信息: {json.dumps(perm_info, indent=2, ensure_ascii=False)}")

        # 添加用户为协作者
        print(f"\n=== 添加用户为协作者 ===")
        result = self.add_base_owner(app_token, user_open_id)

        return result


def main():
    # 配置信息
    APP_ID = "cli_a9d0ce936278dced"
    APP_SECRET = "OSDjdk36qaGZ0xzD7TXmgb5kmuRneuZy"

    # 从 URL 中提取: https://zenoasislab.feishu.cn/base/XAxgb6iynaf3husBMDscm8a2nIe
    APP_TOKEN = "XAxgb6iynaf3husBMDscm8a2nIe"

    # 用户的 Open ID
    USER_OPEN_ID = "ou_55a1ea53df8c6fe203ecb456d0a4db54"

    print("=" * 60)
    print("飞书多维表格权限转移工具")
    print("=" * 60)

    # 创建客户端
    client = FeishuPermissionTransfer(APP_ID, APP_SECRET)

    # 获取 Base 信息
    print(f"\n=== 获取 Base 信息 ===")
    base_info = client.get_base_info(APP_TOKEN)
    if base_info:
        print(f"Base 名称: {base_info.get('name')}")
        print(f"Base Token: {APP_TOKEN}")

    # 转移权限
    print(f"\n=== 转移权限 ===")
    print(f"目标用户 Open ID: {USER_OPEN_ID}")
    result = client.transfer_base_ownership(APP_TOKEN, USER_OPEN_ID)

    if result:
        print(f"\n✓ 权限转移操作完成！")
        print(f"\n⚠️  注意:")
        print(f"1. 用户已被添加为 Base 协作者")
        print(f"2. 如需完全转移所有权，请在飞书管理后台操作")
        print(f"3. 或者直接在飞书客户端中修改权限设置")
    else:
        print(f"\n✗ 权限转移失败")
        print(f"\n💡 建议:")
        print(f"1. 在飞书客户端中打开 Base:")
        print(f"   https://zenoasislab.feishu.cn/base/{APP_TOKEN}")
        print(f"2. 点击右上角 '权限' 或 '分享'")
        print(f"3. 添加用户并设置为 '所有者'")


if __name__ == "__main__":
    main()
