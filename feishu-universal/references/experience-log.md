# 飞书自动化经验日志

> **用途**：持续记录遇到的问题和解决方案
> **更新**：每次操作后更新

---

## [2026-02-11] 自动获取 table_id 功能

**场景**：睡眠热点采集项目数据导入

**问题**：
- 使用 `table_id = "tablename"` 导致空表
- 手动查找 table_id 效率低

**尝试**：
1. 手动在浏览器 URL 中查找 → 成功但繁琐
2. 使用默认值 "tablename" → 表格为空

**解决**：
```python
def get_table_id(app_token):
    """自动从 API 获取 table_id"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables"
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if data.get("code") == 0:
        tables = data["data"]["items"]
        if tables:
            return tables[0]["table_id"]
    
    return None
```

**验证**：
- ✅ 3 个 CSV 文件成功导入
- ✅ table_id: tblUt5nzzWM9JHx7

**相关**：
- 核心经验 2：table_id 格式
- 问题排查：空表问题

---

## [2026-02-02] 文档上传块创建 API

**场景**：悟昕创始人专访上传

**问题**：
- 浏览器自动化上传后刷新丢失
- 剪贴板粘贴无内容

**尝试**：
1. 浏览器自动化 - DOM 修改 → 刷新后丢失 ❌
2. 剪贴板粘贴 → 无内容 ❌
3. docx_builtin_import → 404 ❌
4. 块创建 API → 成功 ✅

**解决**：
```python
# 使用块创建 API
POST /docx/v1/documents/{doc_id}/blocks/{parent_id}/children

# 分块处理（每块 1500 字）
chunk_size = 1500
for i in range(0, len(content), chunk_size):
    chunk = content[i:i+chunk_size]
    add_block(doc_id, chunk)
```

**验证**：
- ✅ 文档内容完整保存
- ✅ 刷新后不丢失

**相关**：
- 核心经验 5：文档上传
- 文档上传指南

---

## [2026-02-01] NaN 值处理

**场景**：左点睡眠仪数据导入

**问题**：
- 第 10-20 行导入失败
- 错误：JSON 序列化失败

**原因**：
```python
# NaN 无法被 JSON 序列化
record = {"IP地址": NaN}  # 错误！
```

**解决**：
```python
# 读取后立即填充 NaN
df = pd.read_excel("data.xlsx")
df = df.fillna('')  # 必须！
```

**验证**：
- ✅ 成功率从 45% → 100%

**相关**：
- 核心经验 3：NaN 值处理
- 数据导入指南

---

## [2026-01-29] 用户身份权限问题

**场景**：左点睡眠仪项目首次导入

**问题**：
- 403 Forbidden 错误
- 无法导入数据

**原因**：使用了应用身份（tenant_access_token）

**解决**：
```python
# 切换到用户身份
token = config.get("user_access_token")
headers = {"Authorization": f"Bearer {token}"}
```

**验证**：
- ✅ 成功导入 20 条数据
- ✅ 你是所有者（完整权限）

**相关**：
- 核心经验 1：用户身份 vs 应用身份

---

## [2026-02-11] 一键创建并导入功能 ⭐

**场景**：悟昕睡眠仪小红书数据导入

**问题**：
- 多步骤操作繁琐（创建 Base → 获取 table_id → 删除默认字段 → 创建字段 → 导入）
- 列偏移问题（默认字段导致数据不从第一列开始）
- 字段类型需要手动指定

**尝试**：
1. 分步操作 - 成功但繁琐 ❌
2. 自动获取 table_id - 部分解决 ⚠️
3. 添加 `--clean-defaults` 参数 - 需手动指定 ⚠️

**解决**：`create-and-import` 命令
```bash
python3 feishu_user_auto.py create-and-import \
  --name "数据名称" \
  --excel data.xlsx
```

**自动化流程**：
1. 创建 Base（用户身份）
2. 自动获取 table_id
3. 删除默认字段（避免列偏移）
4. 从 Excel 列名推断字段类型
5. 批量导入数据
6. 发送飞书通知

**字段类型推断规则**：
```python
# 根据列名推断
- "链接"/"url"/"网址" → type 1 (文本)
- "序号"/"id"/"编号" → type 2 (数字)
- "时间"/"日期"/"time" → type 5 (日期)

# 根据数据推断
- 全是数字 → type 2 (数字)
- 其他 → type 1 (文本)
```

**验证**：
- ✅ 1 个命令完成全流程
- ✅ 20 条数据成功导入
- ✅ 数据从第一列开始显示
- ✅ 字段类型自动匹配

**相关**：
- 核心经验 2：table_id 格式（自动获取）
- 核心经验 3：NaN 值处理
- 核心经验 4：字段必须预先创建（自动推断）

---

**格式模板**：

```markdown
## [YYYY-MM-DD] 经验标题

**场景**：什么情况下遇到的
**问题**：具体问题描述
**尝试**：尝试过的方案
**解决**：最终解决方案
**验证**：如何验证有效
**相关**：相关经验或文档
```
