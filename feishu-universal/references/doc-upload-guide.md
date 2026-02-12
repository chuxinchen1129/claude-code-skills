# 飞书文档上传完整指南

> **适用场景**：Markdown/Word/文章上传到飞书云文档
> **成功率**：90%+

---

## 核心原则

> **必须使用块创建 API，不能用浏览器自动化或剪贴板粘贴**

---

## 正确的 API 端点

```
POST /docx/v1/documents/{document_id}/blocks/{parent_block_id}/children
```

### 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| document_id | 文档 ID | 从创建文档响应获取 |
| parent_block_id | 父块 ID | 根块 = document_id |
| block_type | 块类型 | 2 = 文本块, 1 = 标题块 |

---

## 完整流程

```
创建文档
  ↓
分块处理（1500字/块）
  ↓
块创建 API 上传
  ↓
发送通知
```

---

## 代码示例

### 上传文档

```python
import requests

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
                            "content": chunk
                        }
                    }]
                }
            }]
        }

        response = requests.post(block_url, json=block_data, headers=headers)

    return f"https://zenoasislab.feishu.cn/docx/{document_id}"
```

---

## 常见问题

### Q: 上传后内容丢失？

**原因**：使用了浏览器自动化
**解决**：使用块创建 API

### Q: 无法分段落？

**解决**：使用标题块（block_type = 1）

```python
# 标题块
{
    "block_type": 1,
    "heading": {
        "elements": [{
            "text_run": {
                "content": "章节标题"
            }
        }]
    }
}
```

---

## 失败方案（不要用）

### ❌ 浏览器自动化
- 内容刷新后丢失
- 无法触发数据绑定

### ❌ 剪贴板粘贴
- 浏览器安全限制
- 无法程序化操作

### ❌ 废弃的 API 端点
- `/docx/v1/documents/import` - 404
- `/docx/v1/documents/import_templates` - 404

---

**记住**：文档上传，只用块创建 API！
