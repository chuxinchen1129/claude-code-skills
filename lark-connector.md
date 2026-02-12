---
name: lark-connector
description: This skill should be used when the user asks to "connect to Feishu", "connect to Lark", "setup lark-mcp", "fix lark connection", mentions "飞书连接", "飞书", "lark-mcp", or discusses Feishu/Lark API integration and connection issues.
version: 2.0.0
---

# 飞书/Lark 连接器 Skill

这个 Skill 提供了完整的飞书/Lark MCP 服务器连接、配置和故障排除指南。

**最新更新**: 添加了经过测试的 OAuth 授权流程，支持文档读写、多维表格操作等完整功能。

## 快速开始

### 检查连接状态

```bash
# 查看当前登录状态
lark-mcp whoami
```

### 连接飞书的三种方法

#### 方法 1: OAuth 登录（推荐）

```bash
# 使用 App ID 和 Secret 登录
lark-mcp login -a <APP_ID> -s <APP_SECRET>
```

**注意**: 需要确保应用的重定向 URL 配置为 `http://localhost:3000/callback`
配置地址: https://open.feishu.cn/app/<APP_ID>/safe

#### 方法 2: 重新连接 MCP 服务器

```bash
# 如果已经配置过，直接重新连接
/mcp reconnect lark-mcp
```

#### 方法 3: 完整配置流程

如果之前没有配置过，需要：

1. **安装 lark-mcp 包**
```bash
npm install -g @larksuiteoapi/lark-mcp
```

2. **登录飞书**
```bash
lark-mcp login -a <APP_ID> -s <APP_SECRET>
```

3. **更新 Claude 配置**

编辑 `~/.claude.json`，找到 `mcpServers` 部分：

```json
"mcpServers": {
  "lark-mcp": {
    "command": "/path/to/lark-mcp",
    "args": [
      "mcp",
      "-a",
      "<APP_ID>",
      "-s",
      "<APP_SECRET>",
      "--oauth"
    ],
    "timeout": 30000
  }
}
```

4. **重新连接**
```bash
/mcp reconnect lark-mcp
```

## 获取凭证

### 获取 App ID 和 App Secret

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建应用或选择现有应用
3. 在应用详情页获取：
   - **App ID**: `cli_` 开头的字符串
   - **App Secret**: 点击查看或生成

### 配置权限

确保你的应用有以下权限：

**基础权限**：
- `contact:user.base:readonly` - 获取用户基础信息

**文档操作权限**（必须）：
- `docx:document` - 文档读写操作
- `docs:doc` - 旧版文档操作

**多维表格权限**（如需操作表格）：
- `bitable:app` - 多维表格应用

**消息权限**（如需发送消息）：
- `im:message` - 发送消息
- `im:message:send_as_bot` - 机器人发送消息

**权限配置地址**：
https://open.feishu.cn/app/<APP_ID>/scope

## 常见问题排查

### 问题 1: "Failed to reconnect to lark-mcp"

**原因分析**:
- npm 访问令牌过期
- lark-mcp 包未正确安装
- 配置文件中的命令路径错误
- OAuth token 过期

**解决方案**:

```bash
# 1. 检查 lark-mcp 是否安装
which lark-mcp

# 2. 如果未安装，全局安装
npm install -g @larksuiteoapi/lark-mcp

# 3. 检查登录状态
lark-mcp whoami

# 4. 如果未登录或 token 过期，重新登录
lark-mcp login -a <APP_ID> -s <APP_SECRET>

# 5. 重新连接 MCP
/mcp reconnect lark-mcp
```

### 问题 2: "No active login sessions found"

**解决方案**:
```bash
lark-mcp login -a <APP_ID> -s <APP_SECRET>
```

### 问题 3: "Cannot find module 'debug'"

**原因**: npx 缓存损坏或依赖缺失

**解决方案**:
```bash
# 全局安装而不是使用 npx
npm install -g @larksuiteoapi/lark-mcp

# 更新配置文件，使用直接命令而不是 npx
# 将 ~/.claude.json 中的 command 从 npx 改为 lark-mcp 的完整路径
```

### 问题 4: 重定向 URL 未配置

**解决方案**:
1. 访问 https://open.feishu.cn/app/<APP_ID>/safe
2. 添加重定向 URL: `http://localhost:3000/callback` 或 `http://localhost:8080/callback`
3. 保存后重新执行登录命令

## 手动 OAuth 授权流程（已验证可用）

如果 `lark-mcp login` 遇到问题，可以手动完成 OAuth 授权流程：

### 步骤 1: 获取应用访问令牌

```bash
curl -X POST "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "cli_a9d0ce936278dced",
    "app_secret": "OSDjdk36qaGZ0xzD7TXmgb5kmuRneuZy"
  }'
```

响应示例：
```json
{
  "app_access_token": "t-g1041lmq57QW623QDL6PV5D322YKQUHGYNGUCA4O",
  "code": 0,
  "expire": 5997
}
```

### 步骤 2: 生成授权 URL

在浏览器中打开以下 URL（替换你的 APP_ID）：

```
https://open.feishu.cn/open-apis/authen/v1/authorize?app_id=cli_a9d0ce936278dced&redirect_uri=http://localhost:8080/callback&scope=contact:user.base:readonly%20docs:doc%20docx:document&state=random_state_123
```

**参数说明**：
- `app_id`: 你的应用 ID
- `redirect_uri`: 必须与飞书开放平台配置的完全一致
- `scope`: 权限范围，用 `%20`（空格的 URL 编码）分隔多个权限

**常用权限组合**：
- 只读文档: `contact:user.base:readonly docs:doc`
- 编辑文档: `contact:user.base:readonly docs:doc docx:document`
- 完整权限: `contact:user.base:readonly docs:doc docx:document drive:drive`

### 步骤 3: 完成授权并获取授权码

1. 访问步骤 2 中的授权 URL
2. 登录飞书账号
3. 点击"同意授权"
4. 浏览器会跳转到 `http://localhost:8080/callback?code=xxxxx&state=random_state_123`
5. **复制完整的回调 URL**（即使显示"无法连接"也没关系）

### 步骤 4: 用授权码换取用户访问令牌

```bash
curl -X POST "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer t-g1041lmq57QW623QDL6PV5D322YKQUHGYNGUCA4O" \
  -d '{
    "app_id": "cli_a9d0ce936278dced",
    "app_secret": "OSDjdk36qaGZ0xzD7TXmgb5kmuRneuZy",
    "grant_type": "authorization_code",
    "code": "cwyqDbeH5FDL421cGKL99CzwzAFEbFe7"
  }'
```

响应示例：
```json
{
  "code": 0,
  "data": {
    "access_token": "u-7lNhiJqwRbwVL2ZOPZcoYf5lmYdM1kijhw8aFB000y8o",
    "refresh_token": "ur-61jV89nWZeaEfi3HnBsUD65lkkDg1kqjX08aZB000zdc",
    "token_type": "Bearer",
    "expires_in": 7200,
    "scope": "auth:user.id:read contact:user.base:readonly docs:doc docx:document drive:drive"
  }
}
```

### 步骤 5: 使用访问令牌

现在你可以使用 `access_token` 来调用飞书 API：

```bash
# 读取文档内容
curl -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/FT2WdXjEeomwQwx41cvcsDDUnRh/blocks/FT2WdXjEeomwQwx41cvcsDDUnRh/children" \
  -H "Authorization: Bearer u-7lNhiJqwRbwVL2ZOPZcoYf5lmYdM1kijhw8aFB000y8o"
```

### 令牌刷新

访问令牌有效期为 2 小时，过期后可以使用 `refresh_token` 刷新：

```bash
curl -X POST "https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <app_access_token>" \
  -d '{
    "grant_type": "refresh_token",
    "refresh_token": "ur-61jV89nWZeaEfi3HnBsUD65lkkDg1kqjX08aZB000zdc"
  }'
```

## 可用的飞书 MCP 工具

连接成功后，可以使用以下功能：

### 文档操作

#### 使用 MCP 工具（推荐）
- **读取文档内容**: 使用 `docx_v1_document_rawContent` 获取飞书文档的纯文本
- **获取文档块**: 使用 `bitable_v1_appTableField_list` 或相关工具获取文档结构
- **创建文档**: 使用 `docx_builtin_import` 导入 Markdown 创建新文档
- **搜索文档**: 使用 `docx_builtin_search` 按关键词搜索云文档

#### 使用 API 直接操作（需要 access_token）

**读取文档内容**：
```bash
curl -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/<document_id>/blocks/<block_id>/children" \
  -H "Authorization: Bearer <access_token>"
```

**获取文档块结构**：
```bash
# 获取文档的顶层块
curl -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/<document_id>/blocks/<document_id>/children" \
  -H "Authorization: Bearer <access_token>"
```

**创建新文档**：
```bash
curl -X POST "https://open.feishu.cn/open-apis/docx/v1/documents" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "文档标题",
    "folder_token": ""
  }'
```

### 多维表格 (Bitable)
- **获取表格列表**: 列出所有数据表
- **读取记录**: 查询表格数据
- **创建记录**: 添加新数据
- **更新记录**: 修改现有数据

### 消息发送
- **发送消息**: 向用户或群组发送消息
- **获取消息历史**: 读取聊天记录

### 权限管理
- **添加协作者**: 邀请用户协作

## 使用示例

### 读取飞书文档

```python
# 通过 MCP 工具读取文档
document_id = "FT2WdXjEeomwQwx41cvcsDDUnRh"
# 工具会自动调用 lark-mcp 获取文档内容
```

### 创建多维表格记录

```python
# 向表格添加新记录
app_token = "your_app_token"
table_id = "your_table_id"
# 使用 bitable_v1_appTableRecord_create 工具
```

### 发送飞书消息

```python
# 向用户发送消息
receive_id = "user_open_id"
msg_type = "text"
content = "Hello from Lark!"
# 使用 im_v1_message_create 工具
```

## 维护命令

```bash
# 查看登录状态
lark-mcp whoami

# 登出
lark-mcp logout

# 查看版本
lark-mcp --version

# 查看帮助
lark-mcp --help

# 查看 MCP 命令帮助
lark-mcp mcp --help
```

## 最佳实践

1. **定期检查 Token 状态**: OAuth token 有效期为 2 小时，refresh_token 有效期为 30 天
2. **使用全局安装**: 避免使用 npx，直接全局安装 lark-mcp
3. **配置正确的重定向 URL**: 确保 OAuth 回调地址与飞书开放平台配置完全一致
4. **权限最小化**: 只申请必要的 API 权限
5. **错误日志**: 如遇问题，查看 `~/.claude/debug/` 目录下的日志

## 常见 OAuth 授权错误

### 错误码 20043: scope 参数有误

**错误信息**: `docs:doc:docs docs:doc:write 有误`

**原因**: scope 格式不正确或权限名称错误

**解决方案**:
1. 检查 scope 参数格式，确保使用正确的权限名称
2. 权限之间用 `%20`（URL 编码的空格）分隔，而不是冒号或其它符号
3. 正确的权限示例：
   ```
   contact:user.base:readonly docs:doc docx:document
   ```

### 错误码 99991679: 缺少权限

**错误信息**: `Unauthorized. required one of these privileges: [docx:document, docx:document:write_only]`

**原因**: 应用未获得所需的用户授权

**解决方案**:
1. 确保在飞书开放平台开通了相应权限
2. 在授权 URL 的 scope 参数中包含所需权限
3. 重新完成授权流程

### 错误码 99991403: 应用未发布

**错误信息**: `app not found or not published`

**原因**: 应用状态为开发中，未发布

**解决方案**:
1. 访问 https://open.feishu.cn/app/<APP_ID>/app/publish
2. 将应用状态改为"已发布"
3. 重新进行授权

## 完整示例：从零开始编辑飞书文档

```bash
# 1. 获取 app_access_token
curl -X POST "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "cli_a9d0ce936278dced",
    "app_secret": "OSDjdk36qaGZ0xzD7TXmgb5kmuRneuZy"
  }'

# 2. 浏览器访问授权 URL（替换 YOUR_APP_ID）
# https://open.feishu.cn/open-apis/authen/v1/authorize?app_id=YOUR_APP_ID&redirect_uri=http://localhost:8080/callback&scope=contact:user.base:readonly%20docs:doc%20docx:document&state=random_state_123

# 3. 从浏览器回调 URL 复制 code 参数

# 4. 用 code 换取 user_access_token
curl -X POST "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <app_access_token>" \
  -d '{
    "app_id": "cli_a9d0ce936278dced",
    "app_secret": "OSDjdk36qaGZ0xzD7TXmgb5kmuRneuZy",
    "grant_type": "authorization_code",
    "code": "<从回调URL复制的code>"
  }'

# 5. 读取文档内容
curl -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/<document_id>/blocks/<document_id>/children" \
  -H "Authorization: Bearer <user_access_token>"

# 6. 获取纯文本内容
curl -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/<document_id>/rawContent" \
  -H "Authorization: Bearer <user_access_token>"
```

## 相关资源

- [飞书开放平台文档](https://open.feishu.cn/document/)
- [Lark MCP GitHub](https://github.com/larksuite/lark-openapi-mcp)
- [MCP 集成指南](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/mcp_integration/mcp_introduction)
- [npm 包地址](https://www.npmjs.com/package/@larksuiteoapi/lark-mcp)
