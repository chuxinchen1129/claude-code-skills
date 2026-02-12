# 飞书自动化 - 5 大核心经验

> **来源**：实战验证 + 历史复盘文档整合
> **更新**：2026-02-11
> **状态**：✅ 已验证可用

---

## 目录

1. [用户身份 vs 应用身份](#经验1用户身份-vs-应用身份-⭐⭐⭐)
2. [table_id 格式](#经验2table_id-格式-⭐⭐⭐)
3. [NaN 值处理](#经验3nan-值必须预处理-⭐⭐⭐)
4. [字段必须预先创建](#经验4字段必须预先创建-⭐⭐)
5. [文档上传用块创建 API](#经验5文档上传用块创建-api-⭐⭐)

---

## 经验1：用户身份 vs 应用身份 ⭐⭐⭐

### 关键原则

> **必须使用用户身份（user_access_token）创建资源，确保你是所有者**

### 对比表格

| 身份类型 | Token | 所有者 | 权限 | 推荐 |
|---------|-------|--------|------|------|
| **用户身份** | user_access_token | **你** | 完整控制 | ✅ **使用** |
| 应用身份 | tenant_access_token | 飞书应用 | 受限 | ❌ 不用 |

### 错误做法

```python
# ❌ 使用 tenant_access_token（应用身份）
client = FeishuBitableClient(app_id, app_secret)
# → 飞书应用是所有者
# → 你没有完整权限
# → 无法修改权限设置
# → 403 Forbidden 错误
```

### 正确做法

```python
# ✅ 使用 user_access_token（用户身份）
import requests

token = config.get("user_access_token")
headers = {"Authorization": f"Bearer {token}"}

# → 你是所有者
# → 完整权限控制
# → 可以自由管理
```

### 实战案例

**左点睡眠仪项目** (2026-01-29)：
- ❌ 首次使用应用身份 → 403权限错误
- ✅ 修正后使用用户身份 → 成功导入20条数据

**悟昕睡眠热点采集** (2026-02-11)：
- ✅ 使用用户身份创建 Base
- ✅ 自动成为所有者
- ✅ 完整权限控制

---

## 经验2：table_id 格式 ⭐⭐⭐

### 关键原则

> **table_id 必须是真实格式，不能使用默认值**

### 格式对比

| 格式 | 示例 | 状态 | 说明 |
|------|------|------|------|
| 正确格式 | `tblUt5nzzWM9JHx7` | ✅ 有效 | 从 API 获取 |
| 错误格式 | `"tablename"` | ❌ 无效 | 默认值，导致空表 |
| 错误格式 | `table123` | ❌ 无效 | 不符合格式 |

### 自动获取方法

```python
def get_table_id(app_token):
    """从 API 自动获取 table_id"""
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
            return tables[0]["table_id"]  # 返回第一个表格的 ID

    return None
```

### 实战案例

**空表问题修复** (2026-02-11)：
- ❌ 使用 `table_id = "tablename"` → 表格为空
- ✅ 实现 `get_table_id()` 自动获取 → 成功导入数据

---

## 经验3：NaN 值必须预处理 ⭐⭐⭐

### 关键原则

> **pandas 读取 Excel 时，空单元格会被解析为 NaN，必须在使用前转换为空字符串**

### 为什么必须这样做？

1. **NaN 是特殊类型**：
   - `NaN != NaN`（NaN 不等于任何值，包括它自己）
   - `type(NaN)` 是 `float`（不是 str，不是 None）
   - 无法被 JSON 序列化

2. **飞书 API 无法处理 NaN**：
   ```python
   # ❌ 错误：NaN 无法序列化
   record = {
       "标题": "xxx",
       "IP地址": NaN  # JSON 序列化失败
   }
   ```

### 正确做法

```python
import pandas as pd

# 读取 Excel
df = pd.read_excel("data.xlsx")

# ⭐ 关键第一步：立即填充所有 NaN 为空字符串
df = df.fillna('')  # 必须放在最前面！

# 然后再进行数据转换
for idx, row in df.iterrows():
    record = {}
    for col, val in row.items():
        if val != '':  # 检查空字符串（而不是检查 NaN）
            record[str(col)] = val
```

### 数据清洗进阶

**1. "万"字处理**
```python
# 原始数据: "1.5万"
# 需要转换为: 15000

def convert_wan(val):
    if isinstance(val, str) and '万' in val:
        return float(val.replace('万', '')) * 10000
    return val

df['点赞数'] = df['点赞数'].apply(convert_wan)
```

**2. 数字类型转换**
```python
if isinstance(val, float):
    # 检查是否为整数
    if val == int(val):
        record[col] = int(val)  # 15000.0 → 15000
    else:
        record[col] = val
```

**3. 完整数据清洗流程**
```python
# 1. 读取 Excel
df = pd.read_excel("data.xlsx")

# 2. ⭐ 填充 NaN（必须！）
df = df.fillna('')

# 3. 处理 "万" 字
for col in ['赞', '收藏', '评论']:
    if col in df.columns:
        df[col] = df[col].apply(convert_wan)

# 4. 构建记录
for idx, row in df.iterrows():
    record = {}
    for col, val in row.items():
        if val != '':  # 检查空字符串
            record[str(col)] = val
```

### 实战案例

**NaN 值修复** (2026-02-01)：
- ❌ 第 10-20 行的 IP 地址为空（NaN）→ 导入失败
- ✅ 添加 `df.fillna('')` → 成功率从 45% 提升到 100%

---

## 经验4：字段必须预先创建 ⭐⭐

### 关键发现

> **飞书 API 支持批量创建记录，但不支持通过批量导入自动创建字段**

### 流程

```
1. 创建字段（使用 API 或手动）
    ↓
2. 导入数据（批量创建记录）
```

### 字段类型映射

```python
FIELD_TYPES = {
    "文本": 1,      # text
    "数字": 2,      # number
    "单选": 3,      # singleSelect
    "多选": 4,      # multiSelect
    "日期": 5,      # date
    "附件": 17,     # attachment
    "电话": 11,     # phone
    "邮箱": 13,     # email
    "URL": 15,      # url
}
```

### 创建字段示例

```python
def create_field(app_token, table_id, field_name, field_type):
    """创建字段"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"

    payload = {
        "field_name": field_name,
        "type": field_type
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

### 实战案例

**左点睡眠仪项目** (2026-01-29)：
- ✅ 手动创建字段 → 导入成功
- ⚠️ 尝试通过 API 创建字段 → 字段类型复杂，建议手动创建

---

## 经验5：文档上传用块创建 API ⭐⭐

### 关键原则

> **上传内容到飞书文档，必须使用块创建 API，不能用浏览器自动化**

### 正确的 API 端点

```
POST /docx/v1/documents/{document_id}/blocks/{parent_block_id}/children
```

### 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| document_id | 文档 ID | 从创建文档响应获取 |
| parent_block_id | 父块 ID | 根块 = document_id |
| block_type | 块类型 | 2 = 文本块 |

### 分块处理

**为什么需要分块？**
1. API 对单个块的大小有限制
2. 大文本需要分成多个块
3. 每块建议 1500 字以内

### 完整代码示例

```python
def upload_document(title, content):
    """上传文档到飞书"""

    # 1. 创建文档
    doc_url = "https://open.feishu.cn/open-apis/docx/v1/documents"
    payload = {"title": title}
    response = requests.post(doc_url, json=payload, headers=headers)

    document_id = response.json()["data"]["document"]["document_id"]

    # 2. 分块处理（每块 1500 字）
    chunk_size = 1500
    for i in range(0, len(content), chunk_size):
        chunk = content[i:i+chunk_size]

        # 3. 使用块创建 API
        block_url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/children"

        block_data = {
            "children": [{
                "block_type": 2,  # 文本块
                "text": {
                    "elements": [{
                        "text_run": {
                            "content": chunk,
                            "text_element_style": {}
                        }
                    }]
                }
            }]
        }

        response = requests.post(block_url, json=block_data, headers=headers)
        print(f"块 {i//chunk_size + 1}: {response.status_code}")

    return f"https://zenoasislab.feishu.cn/docx/{document_id}"
```

### 失败方案及原因

**❌ 方案 1：浏览器自动化 - DOM 修改**
- 现象：内容显示在页面上，刷新后消失
- 原因：飞书使用虚拟 DOM，直接修改 innerHTML 不会触发数据绑定

**❌ 方案 2：剪贴板粘贴**
- 现象：无内容
- 原因：浏览器安全策略限制程序化粘贴

**❌ 方案 3：各种 404 的 API 端点**
- 尝试的端点：
  - `/docx/v1/documents/import` - 404
  - `/docx/v1/documents/import_templates` - 404
  - `/docx/v1/documents/{id}/blocks/batch_create` - 404

### 实战案例

**悟昕创始人专访上传** (2026-02-02)：
- ❌ 浏览器自动化 → 刷新后丢失
- ❌ 剪贴板粘贴 → 无内容
- ✅ 块创建 API → 成功

---

## 📌 总结

| 经验 | 重要性 | 影响范围 |
|------|--------|---------|
| 用户身份 | ⭐⭐⭐ | 所有操作 |
| table_id 格式 | ⭐⭐⭐ | 数据导入 |
| NaN 值处理 | ⭐⭐⭐ | 数据导入 |
| 字段创建 | ⭐⭐ | 数据导入 |
| 块创建 API | ⭐⭐ | 文档上传 |

**记住**：每次操作前，先搜索相关经验！
