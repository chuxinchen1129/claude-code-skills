---
name: feishu-universal
description: 飞书全局自动化 - 用户身份版，完整权限管理 + 自动通知 + 经验自动积累。支持 Base 创建、数据导入、文档上传、通知发送。当用户提到"飞书"、"上传到飞书"、"创建 Base"、"导入数据"、"飞书通知"时使用。
version: 3.1.0
created: 2026-02-11
updated: 2026-02-11
---

# 飞书全局自动化 Skill v3.0

> **核心理念**：经验优先 + 自动进化
> 每次操作都自动记录经验，避免重复犯错

---

## 🚀 快速决策树（重要！）

在执行任何飞书操作前，先按以下流程判断：

```
用户请求 → 识别意图 → 搜索经验 → 执行操作 → 自动通知 → 记录经验
```

### 意图识别

| 用户说 | 意图 | 操作 |
|--------|------|------|
| "创建 Base"、"新建表格" | 创建 Base | `create-base` |
| "上传 Excel"、"导入数据" | 数据导入 | `import-data` |
| "上传文档"、"飞书文档" | 文档上传 | `upload-doc` |
| "通知我"、"飞书消息" | 发送通知 | `notify` |

### 经验搜索（关键！）

**每次操作前必须执行**：

1. 搜索 `references/core-experiences.md` - 核心经验
2. 搜索 `references/troubleshooting.md` - 问题排查
3. 搜索 `references/experience-log.md` - 历史经验

**命令示例**：
```bash
# 在 Claude Code 中
Grep "table_id" references/
Grep "403" references/
Grep "NaN" references/
```

---

## 📋 核心脚本

### 1. feishu_user_auto.py - 用户身份自动化

**功能**：
- 创建 Base（用户身份，你是所有者）
- 导入数据（批量，每批 50 条）
- 自动刷新 token
- **一键创建并导入** ⭐ NEW

**使用**：
```bash
# 方式一：一键创建并导入（推荐）⭐
python3 scripts/feishu_user_auto.py create-and-import \
  --name "项目名称" \
  --excel <文件路径>

# 方式二：分步操作
# 1. 创建 Base
python3 scripts/feishu_user_auto.py create-base --name "项目名称"

# 2. 导入数据
python3 scripts/feishu_user_auto.py import-data \
  --app-token <TOKEN> \
  --table-id <TABLE_ID> \
  --excel <文件路径>
```

**一键创建并导入**：自动完成创建 Base → 获取 table_id → 删除默认字段 → 创建字段 → 导入数据

### 2. feishu_bot_notifier.py - 机器人通知

**功能**：
- 发送飞书消息通知
- 确保送达

**使用**：
```bash
python3 scripts/feishu_bot_notifier.py --message "消息内容"
```

### 3. feishu_oauth_setup.py - OAuth 授权

**功能**：
- 首次授权（只需一次）
- 自动获取 user_access_token

**使用**：
```bash
python3 scripts/feishu_oauth_setup.py
```

---

## ⚠️ 5 大核心经验（必读！）

详细内容见 `references/core-experiences.md`

### 经验 1：用户身份 vs 应用身份 ⭐⭐⭐

**原则**：必须使用用户身份创建资源，确保你是所有者

| 身份类型 | 所有者 | 权限 | 推荐 |
|---------|--------|------|------|
| user_access_token | 你 | 完整 | ✅ 使用 |
| tenant_access_token | 飞书应用 | 受限 | ❌ 不用 |

### 经验 2：table_id 格式 ⭐⭐⭐

**正确格式**：`tblxxxxxx`（如 `tblUt5nzzWM9JHx7`）
**错误格式**：`"tablename"`（会导致空表）

**自动获取方法**：
```python
def get_table_id(app_token):
    """从 API 自动获取 table_id"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables"
    # ... 调用 API
```

### 经验 3：NaN 值处理 ⭐⭐⭐

**问题**：pandas 读取 Excel 时，空单元格 → NaN
**解决**：导入前转换为空字符串

```python
df = df.fillna("")  # 或 df.where(pd.notnull(df), "")
```

### 经验 4：字段必须预先创建 ⭐⭐

**原则**：飞书 API 不支持通过导入自动创建字段

**流程**：
1. 先创建字段（API 或手动）
2. 再导入数据

### 经验 5：文档上传用块创建 API ⭐⭐

**端点**：`POST /docx/v1/documents/{doc_id}/blocks/{parent_id}/children`

**要点**：
- 分块处理（每块 1500 字）
- block_type: 2 = 文本块

---

## 🔄 完整工作流

### 场景 1：数据导入

**方式一：一键创建并导入（推荐）⭐**
```
用户："把这个 Excel 上传到飞书"
  ↓
自动执行：
1. 创建 Base
2. 获取 table_id
3. 删除默认字段
4. 从 Excel 列名推断并创建字段
5. 批量导入数据
6. 发送通知
```

**命令**：
```bash
python3 scripts/feishu_user_auto.py create-and-import \
  --name "项目名称" \
  --excel data.xlsx
```

**方式二：分步操作**
```
1. 检查 OAuth 授权
   ↓
2. 创建 Base（用户身份）
   ↓
3. 自动获取 table_id
   ↓
4. 数据清洗（处理 NaN、"万"字等）
   ↓
5. 批量导入（每批 50 条）
   ↓
6. 发送通知
   ↓
7. 记录经验（如有新问题）
```

### 场景 2：文档上传

```
1. 创建文档（用户身份）
   ↓
2. 分块处理（每块 1500 字）
   ↓
3. 块创建 API 上传
   ↓
4. 发送通知
   ↓
5. 记录经验
```

---

## 📚 参考文档

| 文档 | 内容 | 何时查看 |
|------|------|---------|
| `quick-decision-tree.md` | 快速决策流程图 | 每次操作前 |
| `core-experiences.md` | 5 大核心经验（详细） | 遇到问题时 |
| `data-import-guide.md` | 数据导入完整指南 | 导入数据时 |
| `doc-upload-guide.md` | 文档上传完整指南 | 上传文档时 |
| `troubleshooting.md` | 问题排查手册 | 出错时 |
| `experience-log.md` | 自动更新的经验日志 | 持续积累 |

---

## 🎯 最佳实践

### 1. 操作前检查清单

- [ ] 搜索了相关经验文档
- [ ] 确认使用用户身份
- [ ] 检查 OAuth token 是否有效
- [ ] 数据已清洗（NaN 值处理）
- [ ] 了解预期结果

### 2. 错误处理流程

```
遇到错误
  ↓
搜索 troubleshooting.md
  ↓
找到解决方案 → 应用 → 成功 → 记录到 experience-log.md
  ↓
未找到 → 尝试解决 → 成功 → 添加到 experience-log.md
```

### 3. 经验自动积累

**每次操作后**：
1. 判断是否有新经验
2. 如有，更新 `experience-log.md`
3. 标注日期和场景

**格式**：
```markdown
## [YYYY-MM-DD] 经验标题

**场景**：什么情况下遇到的
**问题**：具体问题描述
**解决**：解决方案
**验证**：如何验证有效
```

---

## 🔧 技术细节

### 配置文件

| 文件 | 位置 | 用途 |
|------|------|------|
| OAuth 配置 | `~/.feishu_user_config.json` | Token 存储 |

### Token 管理

| Token 类型 | 有效期 | 刷新方式 |
|-----------|--------|---------|
| user_access_token | 2 小时 | 自动刷新 |
| refresh_token | 30 天 | 需重新授权 |

### API 端点

| 操作 | 端点 | 方法 |
|------|------|------|
| 创建 Base | `/bitable/v1/apps` | POST |
| 获取表格 | `/bitable/v1/apps/{app_token}/tables` | GET |
| 导入数据 | `/bitable/v1/apps/{app_token}/tables/{table_id}/records` | POST |
| 创建文档 | `/docx/v1/documents` | POST |
| 块创建 | `/docx/v1/documents/{doc_id}/blocks/{parent_id}/children` | POST |

---

## 🚨 常见错误速查

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| 403 Forbidden | 用错身份 | 使用 user_access_token |
| 空表 | table_id 错误 | 使用 API 自动获取 |
| 导入失败 | NaN 值 | `df.fillna("")` |
| 400 Bad Request | 参数格式错误 | 检查字段类型映射 |

---

**记住**：这个 Skill 会随着使用不断进化，每次遇到新问题都会自动记录经验！
