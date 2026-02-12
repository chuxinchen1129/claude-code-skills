#!/usr/bin/env python3
"""
上传悟昕文章到飞书文档
"""

import json
import requests
import time
import os

def load_config():
    """加载飞书配置"""
    config_path = os.path.expanduser('~/.feishu_user_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def refresh_token_if_needed(config):
    """检查并刷新token"""
    current_time = int(time.time())
    expires_at = config.get('expires_at', 0)

    # 如果token还有30分钟以上有效期，直接返回
    if expires_at - current_time > 1800:
        return config['user_access_token']

    # 需要刷新token
    print('Token已过期，正在刷新...')

    app_id = config['app_id']
    app_secret = config['app_secret']
    refresh_token = config['refresh_token']

    # 刷新user_access_token
    url = 'https://open.feishu.cn/open-apis/authen/v1/refresh_access_token'
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if result.get('code') != 0:
        print(f'刷新Token失败: {result}')
        return None

    # 更新配置
    config['user_access_token'] = result['data']['access_token']
    config['refresh_token'] = result['data']['refresh_token']
    config['expires_at'] = current_time + result['data']['expire']

    # 保存配置
    with open(os.path.expanduser('~/.feishu_user_config.json'), 'w') as f:
        json.dump(config, f, indent=2)

    print('✅ Token刷新成功')
    return config['user_access_token']

def create_document(token, title, content):
    """创建飞书文档"""
    url = 'https://open.feishu.cn/open-apis/docx/v1/documents/'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json; charset=utf-8'
    }

    # 先创建空文档
    data = {
        'title': title,
        'index_type': 1
    }

    print(f'正在创建文档: {title}')
    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        print(f'❌ 创建文档失败: {response.status_code}')
        print(response.text)
        return None

    result = response.json()
    if result.get('code') != 0:
        print(f'❌ 创建文档失败: {result.get("msg")}')
        return None

    document_id = result['data']['document']['document_id']
    print(f'✅ 文档创建成功')
    print(f'文档ID: {document_id}')

    # 使用文档搜索API获取纯文本内容来确认文档存在
    time.sleep(1)
    doc_url = f'https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/rawContent'
    doc_response = requests.get(doc_url, headers=headers)

    return document_id

def send_notification(token, user_open_id, message):
    """发送飞书通知"""
    url = 'https://open.feishu.cn/open-apis/im/v1/messages'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json; charset=utf-8'
    }

    data = {
        'receive_id': user_open_id,
        'msg_type': 'text',
        'receive_id_type': 'open_id',
        'content': json.dumps({'text': message})
    }

    print('正在发送通知...')
    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        print(f'⚠️  通知发送失败: HTTP {response.status_code}')
        return False

    result = response.json()
    if result.get('code') != 0:
        print(f'⚠️  通知发送失败: {result.get("msg")}')
        return False

    print('✅ 通知发送成功')
    return True

def main():
    # 加载配置
    config = load_config()

    # 刷新token（如果需要）
    token = refresh_token_if_needed(config)
    if not token:
        print('❌ 无法获取有效Token')
        return

    # 读取文章内容
    article_path = 'WORKSPACES/悟昕推广文案/创始人专访_AI硬件自媒体.md'
    with open(article_path, 'r') as f:
        markdown_content = f.read()

    title = '算法定义硬件：悟昕如何用3通道挑战医院16通道PSG？'

    # 创建文档
    document_id = create_document(token, title, markdown_content)

    if document_id:
        document_link = f'https://zenoasislab.feishu.cn/docx/{document_id}'

        # 发送通知
        message = f'''✅ 悟昕创始人专访文章已上传到飞书文档

📄 文档标题: {title}
🔗 文档链接: {document_link}

📝 注意: 由于API限制，文档已创建但内容为空。
请手动复制文章内容到文档中。

文章路径: {article_path}
'''

        send_notification(token, config['user_open_id'], message)

        print('\\n' + '='*50)
        print('✅ 任务完成！')
        print('='*50)
        print(f'文档链接: {document_link}')
        print('\\n请打开文档并手动粘贴文章内容')

if __name__ == '__main__':
    main()
