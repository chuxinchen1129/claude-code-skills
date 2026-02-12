# 飞书交互机器人配置指南

## 当前进度

✅ 步骤 1: 安装 Flask 依赖 - **已完成**
✅ 步骤 2: 安装 cloudflared - **已完成**
✅ 步骤 3: 启动机器人服务 - **已完成** (运行在 localhost:5001)
✅ 步骤 4: 启动 Cloudflare 隧道 - **已完成**
⏳ 步骤 5: 创建飞书应用 - **进行中**
⏳ 步骤 6: 配置事件订阅 - **待完成**
⏳ 步骤 7: 测试飞书机器人 - **待完成**

---

## 公网地址信息

**Webhook URL** (复制到飞书事件订阅):
```
https://distance-occur-databases-align.trycloudflare.com/webhook
```

⚠️ **重要提示**:
- 这个地址只在 Cloudflare 隧道运行时有效
- 重启隧道后会生成新地址，需要重新配置
- 机器人服务运行在 `localhost:5001`

---

## 飞书应用配置步骤

### 1. 创建应用

访问: https://open.feishu.cn/app

1. 点击 "创建企业自建应用"
2. 填写应用信息:
   - 应用名称: `飞书交互机器人`
   - 应用描述: `接收用户消息并执行操作，支持链接采集、数据上传等功能`
3. 选择你的企业/个人

### 2. 配置权限

在 "权限管理" 页面，启用以下权限:

| 权限名称 | 权限ID | 说明 |
|---------|--------|------|
| 获取与发送单聊、群组消息 | `im:message` | ✅ 必需 |
| 发送消息 | `im:chat` | ✅ 必需 |
| 群@权限 | `im:message:group_at` | 可选 |

### 3. 配置事件订阅

在 "事件订阅" 页面:

1. 选择 "添加事件"
2. 搜索并选择: `im.message.receive_v1` (接收消息事件)
3. 设置 Request URL:
   ```
   https://distance-occur-databases-align.trycloudflare.com/webhook
   ```
4. 点击 "验证" - 如果隧道正常运行，验证会成功

### 4. 获取凭证

在 "凭证与基础信息" 页面:

- 复制 **App ID**
- 复制 **App Secret**

### 5. 发布应用

在 "版本管理与发布" 页面:

1. 创建新版本
2. 填写版本说明
3. 点击 "申请发布" (企业自建应用通常自动通过)

---

## 配置机器人

完成飞书应用配置后，请提供:

1. **App ID**: 格式如 `cli_xxxxxxxxxxxxx`
2. **App Secret**: 格式如 `xxxxxxxxxxxxxxxxxxxxx`

我会帮你配置到机器人中。

---

## 支持的命令

配置完成后，你可以在飞书中向机器人发送:

| 命令 | 功能 | 示例 |
|------|------|------|
| 链接采集 | 发送小红书/微信链接 | `https://xhs.com/...` |
| 关键词采集 | 触发 MediaCrawler | `采集：睡眠仪 50` |
| 数据上传 | 上传到飞书表格 | `上传到飞书` |
| 状态查询 | 查看采集状态 | `查看状态` |
| 帮助 | 显示命令列表 | `help` |

---

## 故障排查

### 隧道断开

如果隧道断开，重新启动:

```bash
# 停止旧隧道
pkill cloudflared

# 启动新隧道
cloudflared tunnel --url http://localhost:5001
```

### 机器人服务停止

如果机器人服务停止，重新启动:

```bash
cd ~/.claude/skills/feishu-bot/scripts
python3 bot_server.py
```

---

**创建时间**: 2026-02-11
**版本**: v1.0.0
