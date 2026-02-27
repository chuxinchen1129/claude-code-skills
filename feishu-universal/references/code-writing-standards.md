# 飞书代码写作规范

> **版本**: v1.0
> **创建时间**: 2026-02-27
> **目的**: 统一飞书相关代码的编写风格，提高代码可维护性和复用性

---

## 1. 命名规范

### 1.1 类名（PascalCase）

```python
# ✅ 正确
class FeishuSender:
    pass

class FeishuBotNotifier:
    pass

class FeishuUserClient:
    pass

# ❌ 错误
class feishu_sender:
    pass

class Feishu_Sender:
    pass
```

### 1.2 函数名（snake_case）

```python
# ✅ 正确
def send_message():
    pass

def send_via_webhook():
    pass

def create_base():
    pass

# ❌ 错误
def SendMessage():
    pass

def sendMessage():
    pass
```

### 1.3 文件名（snake_case）

```python
# ✅ 正确
feishu_sender.py
send_image_to_feishu.py
feishu_bot_notifier.py

# ❌ 错误
FeishuSender.py
send-image-to-feishu.py
```

### 1.4 常量（UPPER_SNAKE_CASE）

```python
# ✅ 正确
USE_FEISHU_PATHS = True
API_TIMEOUT = 30
MAX_BATCH_SIZE = 50

# ❌ 错误
use_feishu_paths = True
ApiTimeout = 30
```

---

## 2. 文件结构规范

### 2.1 标准文件头

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书消息发送工具
用于将生成的内容自动发送到飞书
"""

import os
import sys
from pathlib import Path
```

### 2.2 导入顺序

1. 标准库
2. 第三方库
3. 本地模块
4. 项目内部模块

```python
# 1. 标准库
import os
import sys
import json
import time

# 2. 第三方库
import requests
import pandas as pd

# 3. 本地模块
from pathlib import Path

# 4. 项目内部模块
from feishu_paths import FeishuPaths
from dms_paths import DMSCheck
```

### 2.3 模块导入规范

**关键原则**: 使用 `sys.path.insert` 而非 `scripts.` 前缀

```python
# ✅ 正确：直接导入
sys.path.insert(0, str(feishu_scripts))
from feishu_bot_notifier import FeishuBotNotifier

# ❌ 错误：使用 scripts. 前缀会导致 "No module named 'scripts'"
from scripts.feishu_bot_notifier import FeishuBotNotifier
```

---

## 3. 函数规范

### 3.1 文档字符串（Docstring）

```python
def send_via_webhook(self, content):
    """通过 Webhook 发送消息

    Args:
        content: 可以是字符串或字符串列表（用于分批发送）

    Returns:
        dict: 发送结果
            - success (bool): 是否成功
            - message (str): 结果消息
            - results (list): 详细结果列表（可选）
            - error (str): 错误信息（失败时）
    """
```

### 3.2 参数类型注解（推荐）

```python
def send_via_webhook(
    self,
    content: str | list[str],
    timeout: int = 10
) -> dict:
    pass
```

---

## 4. 返回值格式规范

### 4.1 统一返回字典格式

```python
# 成功
{
    'success': True,
    'message': '消息已发送',
    'results': [...]  # 可选
}

# 失败
{
    'success': False,
    'error': '发送失败: 网络错误'
}
```

### 4.2 返回值示例

```python
def send_via_webhook(self, content):
    try:
        # 业务逻辑
        return {
            'success': True,
            'message': f'{len(messages)}条消息已发送到飞书',
            'results': results
        }
    except urllib.error.URLError as e:
        return {
            'success': False,
            'error': f'网络错误: {str(e)}'
        }
```

---

## 5. 错误处理规范

### 5.1 异常捕获顺序

```python
try:
    # 业务逻辑
    pass
except SpecificException as e:
    # 特定异常处理
    return {'success': False, 'error': f'具体错误: {str(e)}'}
except json.JSONDecodeError as e:
    # JSON 解析错误
    return {'success': False, 'error': f'JSON解析错误: {str(e)}'}
except Exception as e:
    # 通用异常处理
    return {'success': False, 'error': f'未知错误: {str(e)}'}
```

### 5.2 资源清理（使用 with）

```python
# ✅ 正确
with open('file.txt', 'r') as f:
    content = f.read()

# ❌ 错误
f = open('file.txt', 'r')
content = f.read()
f.close()
```

---

## 6. 路径管理规范

### 6.1 使用 pathlib 而非字符串

```python
# ✅ 正确
from pathlib import Path

config_path = Path(__file__).parent / 'config.yaml'
output_dir = Path.home() / 'Desktop' / 'output'

# ❌ 错误
config_path = __file__ + '/config.yaml'
output_dir = os.path.expanduser('~/Desktop/output')
```

### 6.2 路径计算规范

```python
# ✅ 正确：使用相对路径
_dms_root = Path(__file__).parent.parent.parent.parent
feishu_scripts = _dms_root / 'skills' / 'feishu-universal' / 'scripts'

# ❌ 错误：使用绝对路径
feishu_scripts = '/Users/echochen/Desktop/DMS/skills/feishu-universal/scripts'
```

### 6.3 统一路径管理（推荐）

```python
# 使用 dms_paths.py 统一管理
from dms_paths import DMSCheck

# 获取飞书脚本目录
feishu_scripts = DMSCheck.get_feishu_scripts_dir()

# 添加到 Python 路径
sys.path.insert(0, str(feishu_scripts))
```

---

## 7. 批量发送规范

### 7.1 支持单条或列表

```python
def send(self, content):
    """
    发送消息到飞书

    Args:
        content: 可以是字符串或字符串列表
    """
    # 支持单条消息或列表消息（分批发送）
    messages = content if isinstance(content, list) else [content]

    for i, msg in enumerate(messages, 1):
        # 发送逻辑
        pass

        # 每条消息间隔1秒，避免限流
        if i < len(messages):
            time.sleep(1)
```

### 7.2 批量上传规范

```python
def batch_create_records(self, records, batch_size=50):
    """批量创建记录

    Args:
        records: 记录列表
        batch_size: 每批数量（最大500，推荐50）
    """
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]

        # 批量创建逻辑
        self._create_batch(batch)

        # 批次间延迟，避免API限流
        if i + batch_size < len(records):
            time.sleep(0.5)
```

---

## 8. 环境变量规范

### 8.1 使用 os.getenv 获取

```python
# ✅ 正确
webhook_url = os.getenv('FEISHU_WEBHOOK_URL', '')
app_id = os.getenv('FEISHU_APP_ID', '')

# ❌ 错误
webhook_url = os.environ['FEISHU_WEBHOOK_URL']  # 会抛出 KeyError
```

### 8.2 提供默认值

```python
# ✅ 正确：提供默认值
webhook_url = os.getenv('FEISHU_WEBHOOK_URL', '')
api_timeout = int(os.getenv('API_TIMEOUT', '30'))

# ❌ 错误：不提供默认值
webhook_url = os.getenv('FEISHU_WEBHOOK_URL')  # 返回 None
```

---

## 9. 日志规范

### 9.1 使用 print（简单场景）

```python
print(f"✅ 消息已发送")
print(f"❌ 发送失败: {error}")
print(f"⏳ 正在处理 {i}/{total}...")
```

### 9.2 使用 logging（复杂场景）

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

logger.info("开始发送消息")
logger.error(f"发送失败: {error}")
```

---

## 10. 命令行接口规范

### 10.1 使用 argparse

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description='飞书消息发送工具')
    parser.add_argument('--content', '-c', type=str, help='要发送的内容')
    parser.add_argument('--no-auto', action='store_true', help='不自动发送')
    parser.add_argument('message', nargs='?', type=str, help='要发送的内容')

    args = parser.parse_args()

    # 处理逻辑
    pass

if __name__ == '__main__':
    main()
```

### 10.2 退出码规范

```python
import sys

# 成功
sys.exit(0)

# 失败
sys.exit(1)
```

---

## 11. 类设计规范

### 11.1 初始化方法

```python
class FeishuSender:
    """飞书消息发送器"""

    def __init__(self):
        """初始化发送器"""
        # 读取环境变量
        self.webhook_url = os.environ.get('FEISHU_WEBHOOK_URL', '')
        self.app_id = os.environ.get('FEISHU_APP_ID', '')
        self.app_secret = os.environ.get('FEISHU_APP_SECRET', '')

        # 优先使用 webhook
        self.use_webhook = bool(self.webhook_url)
```

### 11.2 私有方法

```python
class FeishuSender:
    def send_via_webhook(self, content):
        # 公开方法
        pass

    def _create_batch(self, batch):
        # 私有方法（单下划线）
        pass

    def __internal_method(self):
        # 强私有方法（双下划线）
        pass
```

---

## 12. 代码注释规范

### 12.1 行内注释

```python
# 每条消息间隔1秒，避免限流
time.sleep(1)
```

### 12.2 代码块注释

```python
# ========== 数据清洗 ==========
# 1. 填充 NaN 值
df = df.fillna('')

# 2. 处理 "万" 字
df['value'] = df['value'].apply(convert_wan)

# ========== 数据导入 ==========
```

---

## 13. 常见反模式

### 13.1 不要硬编码路径

```python
# ❌ 错误
config_path = '/Users/echochen/Desktop/DMS/config.yaml'

# ✅ 正确
_dms_root = Path(__file__).parent.parent.parent.parent
config_path = _dms_root / 'config.yaml'
```

### 13.2 不要使用 scripts. 前缀导入

```python
# ❌ 错误：会导致 "No module named 'scripts'"
from scripts.feishu_bot_notifier import FeishuBotNotifier

# ✅ 正确
sys.path.insert(0, str(feishu_scripts))
from feishu_bot_notifier import FeishuBotNotifier
```

### 13.3 不要忽略 NaN 值

```python
# ❌ 错误：NaN 无法被 JSON 序列化
df = pd.read_excel('data.xlsx')
records = df.to_dict('records')  # 包含 NaN

# ✅ 正确：立即填充 NaN
df = pd.read_excel('data.xlsx')
df = df.fillna('')
records = df.to_dict('records')
```

---

## 14. 最佳实践总结

### 14.1 复用优先

```python
# ✅ 正确：复用现有类
from feishu_sender import FeishuSender

sender = FeishuSender()
result = sender.send("消息内容")

# ❌ 错误：重复实现
# 不要在每个技能中重新实现发送逻辑
```

### 14.2 统一路径管理

```python
# ✅ 正确：使用 dms_paths.py
from dms_paths import DMSCheck

feishu_scripts = DMSCheck.get_feishu_scripts_dir()

# ❌ 错误：每个脚本独立计算路径
feishu_scripts = Path(__file__).parent.parent.parent.parent / 'skills' / 'feishu-universal' / 'scripts'
```

### 14.3 错误处理完善

```python
# ✅ 正确：分层次的异常处理
try:
    # 业务逻辑
    pass
except urllib.error.URLError as e:
    return {'success': False, 'error': f'网络错误: {str(e)}'}
except json.JSONDecodeError as e:
    return {'success': False, 'error': f'JSON解析错误: {str(e)}'}
except Exception as e:
    return {'success': False, 'error': f'未知错误: {str(e)}'}

# ❌ 错误：通用异常处理
try:
    pass
except Exception as e:
    return {'success': False, 'error': str(e)}
```

---

## 15. 检查清单

编写飞书相关代码时，请检查：

- [ ] 类名使用 PascalCase
- [ ] 函数名使用 snake_case
- [ ] 文件名使用 snake_case
- [ ] 常量使用 UPPER_SNAKE_CASE
- [ ] 导入顺序：标准库 → 第三方库 → 本地模块 → 项目内部模块
- [ ] 不使用 `scripts.` 前缀导入
- [ ] 使用 `sys.path.insert` 处理路径
- [ ] 使用 `pathlib` 处理文件路径
- [ ] 不硬编码绝对路径
- [ ] 返回值使用统一的字典格式
- [ ] 提供文档字符串
- [ ] 使用 `with` 语句管理资源
- [ ] 批量操作时控制批次大小和延迟
- [ ] 处理 NaN 值（数据导入时）
- [ ] 提供环境变量默认值

---

**文档维护**: DMS
**最后更新**: 2026-02-27
**版本**: v1.0
