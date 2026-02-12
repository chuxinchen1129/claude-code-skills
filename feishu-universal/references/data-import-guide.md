# 飞书数据导入完整指南

> **适用场景**：Excel/CSV 数据导入到飞书多维表格
> **成功率**：95%+

---

## 目录

1. [快速开始](#快速开始)
2. [完整流程](#完整流程)
3. [数据准备](#数据准备)
4. [导入操作](#导入操作)
5. [常见问题](#常见问题)

---

## 快速开始

### 3 分钟快速导入

```bash
# 1. 检查 OAuth 授权
cat ~/.feishu_user_config.json

# 2. 创建 Base
python3 scripts/feishu_user_auto.py create-base --name "项目名称"

# 3. 导入数据
python3 scripts/feishu_user_auto.py import-data \
  --app-token <APP_TOKEN> \
  --table-id <TABLE_ID> \
  --excel data.xlsx
```

---

## 完整流程

```
数据准备
  ↓
创建 Base
  ↓
获取 table_id
  ↓
数据清洗
  ↓
批量导入
  ↓
发送通知
```

---

## 数据准备

### 1. Excel 格式要求

| 要求 | 说明 | 示例 |
|------|------|------|
| 表头 | 第一行必须是字段名 | 标题、作者、点赞数 |
| 数据类型 | 数字/文本/日期 | 15000、xxx、2026-02-10 |
| 空单元格 | 留空即可 | 会自动转为空字符串 |
| 编码 | UTF-8 | CSV 文件 |

### 2. 常见数据问题

**问题 1：包含 "万" 字**
```python
# 解决方案：转换函数
def convert_wan(val):
    if isinstance(val, str) and '万' in val:
        return float(val.replace('万', '')) * 10000
    return val
```

**问题 2：日期格式不统一**
```python
# 解决方案：统一格式
from datetime import datetime

def standardize_date(val):
    if isinstance(val, str):
        # 尝试解析
        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y']:
            try:
                return datetime.strptime(val, fmt).strftime('%Y-%m-%d')
            except:
                continue
    return val
```

**问题 3：特殊字符**
```python
# 解决方案：清理特殊字符
import re

def clean_text(val):
    if isinstance(val, str):
        # 移除控制字符
        return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', val)
    return val
```

### 3. 数据清洗模板

```python
import pandas as pd

def clean_data(file_path):
    """数据清洗标准流程"""

    # 1. 读取 Excel
    df = pd.read_excel(file_path)

    # 2. ⭐ 填充 NaN（必须！）
    df = df.fillna('')

    # 3. 处理 "万" 字
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(convert_wan)

    # 4. 清理特殊字符
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(clean_text)

    # 5. 保存清洗后的数据
    output_path = file_path.replace('.xlsx', '_cleaned.xlsx')
    df.to_excel(output_path, index=False)

    return output_path
```

---

## 导入操作

### 方案 A：使用脚本（推荐）

```bash
# 完整导入流程
python3 scripts/feishu_user_auto.py import-data \
  --app-token VyekbdajOaDqdqs9e0hcL00Ynjd \
  --table-id tblUt5nzzWM9JHx7 \
  --excel data_cleaned.xlsx
```

**输出示例**：
```
开始导入 199 条记录...
✓ 批次 1: 50 条记录
✓ 批次 2: 50 条记录
✓ 批次 3: 50 条记录
✓ 批次 4: 49 条记录

导入完成: 199 条成功, 0 条失败
✓ 已发送飞书消息通知
```

### 方案 B：手动导入（一次性操作）

**步骤**：
1. 打开飞书多维表格
2. 点击右上角 "..."
3. 选择 "导入数据"
4. 选择 Excel 文件
5. 确认导入

**优点**：快速、简单
**缺点**：无法自动化、不适合重复操作

### 自动获取 table_id

```python
def get_table_id(app_token):
    """自动获取 table_id"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    if data.get("code") == 0:
        tables = data["data"]["items"]
        if tables:
            return tables[0]["table_id"]

    return None
```

---

## 常见问题

### Q1: 导入后表格为空？

**原因**：table_id 格式错误
**解决**：使用 API 自动获取真实的 table_id

```bash
# 检查 table_id 格式
# 正确: tblUt5nzzWM9JHx7
# 错误: tablename
```

### Q2: 部分数据导入失败？

**原因**：
1. NaN 值未处理
2. 数据类型不匹配
3. 字段未创建

**解决**：
```python
# 1. 填充 NaN
df = df.fillna('')

# 2. 检查字段是否存在
# 3. 确认数据类型匹配
```

### Q3: 导入速度慢？

**优化**：
```python
# 调整批次大小
batch_size = 50  # 推荐 50，最大 500

# 添加延迟避免限流
import time
time.sleep(0.5)  # 每批之间延迟 0.5 秒
```

### Q4: 如何批量导入多个文件？

```python
import glob

files = glob.glob("data/*.xlsx")

for file in files:
    print(f"导入: {file}")
    # 调用导入函数
    import_data(file)
```

### Q5: Token 过期怎么办？

**检查**：
```bash
python3 scripts/feishu_token_checker.py
```

**重新授权**：
```bash
python3 scripts/feishu_oauth_setup.py
```

---

## 最佳实践

### 1. 导入前检查清单

- [ ] Excel 格式正确（表头、数据完整）
- [ ] 数据已清洗（NaN、"万"字、特殊字符）
- [ ] OAuth 授权有效
- [ ] 了解预期导入时间

### 2. 导入后验证

```python
# 验证导入数量
expected = len(df)
actual = get_record_count(app_token, table_id)

if expected == actual:
    print("✅ 导入完整")
else:
    print(f"⚠️ 预期 {expected}，实际 {actual}")
```

### 3. 错误处理

```python
try:
    import_data(app_token, table_id, excel_file)
except Exception as e:
    print(f"❌ 导入失败: {e}")

    # 搜索经验文档
    search_troubleshooting(str(e))
```

---

## 进阶技巧

### 1. 增量导入

```python
def incremental_import(new_data):
    """只导入新增数据"""

    # 获取现有数据
    existing = get_existing_records(app_token, table_id)

    # 找出新增
    new_records = [r for r in new_data if r['id'] not in existing]

    # 导入新增
    if new_records:
        import_data(new_records)
```

### 2. 数据更新

```python
def update_records(record_ids, updates):
    """更新现有记录"""

    for record_id, update in zip(record_ids, updates):
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"

        payload = {"fields": update}

        requests.patch(url, json=payload, headers=headers)
```

### 3. 并行导入

```python
from concurrent.futures import ThreadPoolExecutor

def import_parallel(files, workers=3):
    """并行导入多个文件"""

    with ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(import_data, files)
```

---

**记住**：数据导入前先搜索经验，避免重复犯错！
