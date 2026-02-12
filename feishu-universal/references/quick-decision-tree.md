# 飞书操作快速决策树

> **使用场景**：每次执行飞书操作前，先按此流程判断
> **目标**：避免重复犯错，选择正确方案

---

## 🚀 完整决策流程

```
用户请求
  ↓
[1] 识别意图
  ↓
[2] 搜索经验（必须！）
  ↓
[3] 选择方案
  ↓
[4] 执行操作
  ↓
[5] 自动通知
  ↓
[6] 记录经验
```

---

## [1] 意图识别

### 用户说什么 → 做什么

| 用户关键词 | 意图 | 操作 | 脚本 |
|-----------|------|------|------|
| "创建 Base"、"新建表格"、"飞书表格" | 创建 Base | `create-base` | feishu_user_auto.py |
| "上传 Excel"、"导入数据"、"数据到飞书" | 数据导入 | `import-data` | feishu_user_auto.py |
| "上传文档"、"飞书文档"、"文章上传" | 文档上传 | `upload-doc` | upload_wuxin_article_to_feishu.py |
| "通知我"、"飞书消息"、"发送通知" | 发送通知 | `notify` | feishu_bot_notifier.py |
| "自动化"、"完整流程" | 全流程 | `full-workflow` | 主脚本 |

---

## [2] 经验搜索（关键步骤！）

**每次操作前必须执行**：

### 搜索优先级

1. **核心经验** → `core-experiences.md`
2. **问题排查** → `troubleshooting.md`
3. **历史经验** → `experience-log.md`

### 搜索关键词

| 场景 | 搜索关键词 |
|------|-----------|
| 创建 Base | "用户身份"、"所有者"、"权限" |
| 数据导入 | "table_id"、"NaN"、"字段"、"批量" |
| 文档上传 | "块创建"、"1500字"、"block_type" |
| 错误处理 | "403"、"400"、"空表"、"失败" |

### 搜索命令示例

```bash
# 在 Claude Code 中
Grep "用户身份" references/
Grep "table_id" references/
Grep "NaN" references/
```

---

## [3] 方案选择

### 场景 A：创建 Base

```
判断：需要 Base 吗？
  ├─ 是 → 选择创建方式
  │    ├─ 一次性操作 → 方案 A1：手动创建（最快）
  │    ├─ 需要自动化 → 方案 A2：脚本创建
  │    └─ 需要权限 → 方案 A3：用户身份创建（推荐）
  └─ 否 → 使用现有 Base
```

### 场景 B：数据导入

```
判断：数据来源？
  ├─ Excel 文件 → 检查格式
  │    ├─ 标准 Excel → 方案 B1：直接导入
  │    ├─ 有 NaN 值 → 方案 B2：先清洗后导入
  │    └─ 有 "万" 字 → 方案 B3：转换后导入
  ├─ CSV 文件 → 检查编码
  └─ 其他格式 → 先转换为 Excel
```

### 场景 C：文档上传

```
判断：文档类型？
  ├─ Markdown → 方案 C1：块创建 API
  ├─ Word/PDF → 方案 C2：先转换为 Markdown
  └─ 纯文本 → 方案 C3：块创建 API
```

---

## [4] 执行操作

### 执行前检查清单

- [ ] 搜索了相关经验
- [ ] 确认使用用户身份
- [ ] 检查 OAuth token 有效性
- [ ] 数据已清洗（如需要）
- [ ] 了解预期结果

### 执行中监控

| 阶段 | 检查点 | 正常指标 |
|------|--------|---------|
| OAuth 授权 | Token 获取 | 200 OK |
| Base 创建 | 所有者检查 | 你（ou_xxx） |
| table_id 获取 | 格式验证 | tblxxxxxx |
| 数据导入 | 批次进度 | 50条/批 |
| 通知发送 | 消息送达 | 成功 |

---

## [5] 自动通知

### 通知触发条件

- ✅ Base 创建完成
- ✅ 数据导入完成
- ✅ 文档上传完成
- ⚠️ Token 即将过期（<3天）
- ❌ 操作失败

### 通知内容模板

```
✅ [操作类型] 已完成

详情：
- Base: https://feishu.cn/base/xxx
- 数据: XX 条记录
- 时间: YYYY-MM-DD HH:MM
```

---

## [6] 记录经验

### 何时记录

- ✅ 遇到新问题
- ✅ 发现更好的方案
- ✅ 验证了某个经验
- ✅ 用户反馈有改进

### 记录格式

```markdown
## [YYYY-MM-DD] 经验标题

**场景**：什么情况下遇到的
**问题**：具体问题描述
**尝试**：尝试过的方案
**解决**：最终解决方案
**验证**：如何验证有效
**相关**：相关 issue 或文档
```

### 记录位置

- 新经验 → `experience-log.md`
- 验证经验 → 在原经验添加"已验证"标记
- 改进经验 → 更新原经验，添加"改进历史"

---

## 🚨 常见错误快速处理

| 错误 | 立即检查 | 快速解决 |
|------|---------|---------|
| 403 Forbidden | 是否用用户身份？ | 切换到 user_access_token |
| 空表 | table_id 格式？ | 使用 API 自动获取 |
| 导入失败 | 有 NaN 值？ | `df.fillna("")` |
| 400 Bad Request | 字段类型匹配？ | 检查字段映射 |
| Token 过期 | refresh 有效期？ | 重新 OAuth 授权 |

---

## 💡 效率提升技巧

### 1. 批量操作

```python
# 批量导入：每批 50 条
for i in range(0, total, 50):
    batch = data[i:i+50]
    import_batch(batch)
```

### 2. 并行处理

```python
# 多文件并行上传
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(upload_file, files)
```

### 3. 缓存复用

```python
# 缓存 table_id，避免重复获取
table_id_cache = {}
def get_table_id(app_token):
    if app_token not in table_id_cache:
        table_id_cache[app_token] = fetch_table_id(app_token)
    return table_id_cache[app_token]
```

---

**记住**：这个决策树会随着经验积累不断优化！
