# 飞书自动化问题排查手册

> **使用场景**：遇到错误时快速查找解决方案
> **更新**：每次解决问题后更新

---

## 目录

1. [常见错误](#常见错误)
2. [诊断流程](#诊断流程)
3. [搜索技巧](#搜索技巧)

---

## 常见错误

### 403 Forbidden

**症状**：
```
{"code": 99991663, "msg": "no permission to operate this resource"}
```

**原因**：使用了应用身份（tenant_access_token）

**解决方案**：
```python
# ✅ 使用用户身份
token = config.get("user_access_token")
```

**验证**：
```python
# 检查所有者
owner = response["data"]["app"]["owner"]
# 应该是: ou_xxx（你）
# 不应该是: app_xxx（应用）
```

---

### 空表（数据导入成功但表格为空）

**症状**：
- 导入显示成功
- 但打开表格为空

**原因**：table_id 格式错误

**解决方案**：
```python
# ✅ 自动获取 table_id
def get_table_id(app_token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables"
    # ... 调用 API
```

**验证**：
```bash
# 检查 table_id 格式
# 正确: tblUt5nzzWM9JHx7
# 错误: tablename
```

---

### 导入失败（部分数据）

**症状**：
```
导入完成: 15 条成功, 5 条失败
```

**原因**：
1. NaN 值未处理
2. 数据类型不匹配
3. 特殊字符

**解决方案**：
```python
# 1. 填充 NaN
df = df.fillna('')

# 2. 检查数据类型
print(df.dtypes)

# 3. 清理特殊字符
import re
df['text'] = df['text'].str.replace(r'[\x00-\x1f]', '', regex=True)
```

---

### Token 过期

**症状**：
```
{"code": 99991404, "msg": "access token expired"}
```

**原因**：user_access_token 有效期 2 小时

**解决方案**：
```bash
# 重新授权
python3 scripts/feishu_oauth_setup.py
```

**预防**：
```bash
# 定期检查
python3 scripts/feishu_token_checker.py
```

---

### 400 Bad Request

**症状**：
```
{"code": 400, "msg": "invalid request"}
```

**原因**：
1. 参数格式错误
2. 字段类型不匹配
3. 缺少必填字段

**解决方案**：
```python
# 检查请求体
print(json.dumps(payload, indent=2, ensure_ascii=False))

# 检查字段类型
field_types = get_field_types(app_token, table_id)
```

---

## 诊断流程

```
遇到错误
  ↓
1. 检查错误码
  ↓
2. 搜索 experience-log.md
  ↓
3. 搜索 core-experiences.md
  ↓
4. 按错误类型处理
  ↓
5. 记录新经验
```

### 按错误码处理

| 错误码 | 类型 | 处理 |
|--------|------|------|
| 403 | 权限 | 检查身份类型 |
| 404 | 资源不存在 | 检查 ID 格式 |
| 400 | 参数错误 | 检查请求体 |
| 99991663 | 无权限 | 使用用户身份 |
| 99991404 | Token 过期 | 重新授权 |

---

## 搜索技巧

### 搜索关键词

| 问题 | 关键词 |
|------|--------|
| 权限 | 403、用户身份、所有者 |
| 空表 | table_id、tablename |
| 导入 | NaN、"万"字、字段 |
| Token | 过期、OAuth、refresh |

### 搜索命令

```bash
# 在 Claude Code 中
Grep "403" references/
Grep "table_id" references/
Grep "NaN" references/
```

---

**记住**：每次解决问题后，更新 experience-log.md！
