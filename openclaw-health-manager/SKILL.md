---
name: openclaw-health-manager
description: "巡检和维护 OpenClaw 多 agent 环境的健康度。适用于每日自动检查 OpenClaw gateway、ACP、Feishu 多账号绑定、session 坏引用、agent memory 目录与长期记忆状态，并可选地安全修复坏 session 索引。用户提到 OpenClaw 健康检查、daily health check、session 修复、memory 管理、agent 记忆巡检、飞书绑定巡检时使用。"
---

# OpenClaw Health Manager

用于你这套 OpenClaw 多 agent 环境的日常健康巡检和轻量维护。

默认策略：

- **先检查，后修复**
- **默认只读**
- **只做可逆修复**
- **修复前自动备份**

## 适用场景

- 每日自动检查 OpenClaw 是否健康
- 检查 gateway / ACP / Feishu 绑定是否异常
- 检查各 agent 的 `sessions.json` 是否有坏引用
- 检查各 agent 的 `memory/` 是否缺失、过旧或空转
- 生成一份统一的巡检报告
- 在确认安全时，自动删除指向不存在 `.jsonl` 的坏 session 索引

## 最常用命令

```bash
# 1) 每日健康检查（推荐默认）
python3 skills/openclaw-health-manager/scripts/openclaw_health_check.py

# 2) 输出到指定目录
python3 skills/openclaw-health-manager/scripts/openclaw_health_check.py \
  --output-dir /Users/echo/Desktop/DMS/05_SYSTEM_DOCS/openclaw-health-reports

# 3) 附带安全修复坏 session 引用
python3 skills/openclaw-health-manager/scripts/openclaw_health_check.py \
  --repair-broken-session-refs

# 4) 只看 JSON 结果，方便自动化消费
python3 skills/openclaw-health-manager/scripts/openclaw_health_check.py \
  --json-only
```

## 检查内容

脚本会检查：

1. `ai.openclaw.gateway` 是否存在、是否在运行
2. 主配置 `/Users/echo/.openclaw/openclaw.json` 是否可读
3. `session.dmScope` 是否为 `per-account-channel-peer`
4. ACP 是否启用，`acp.allowedAgents` 是否包含 `claude`
5. `channels.feishu.accounts` 和 `bindings` 是否一致
6. 每个 agent 的：
   - `workspace` 是否存在
   - `sessions/sessions.json` 是否存在且可解析
   - `sessions.json` 中的 `sessionFile` 是否存在
   - 是否存在未被索引引用的孤儿 `.jsonl`
   - `memory/` 是否存在
   - 最近的 `memory/YYYY-MM-DD.md` 是否过旧
   - `MEMORY.md` 是否存在

## 修复策略

仅在显式传入：

```bash
--repair-broken-session-refs
```

时，脚本才会做修复。

当前仅做一种安全修复：

- 删除 `sessions.json` 中指向不存在 `sessionFile` 的坏引用

修复前会自动备份原始 `sessions.json` 到：

```text
/Users/echo/.openclaw/session-resets/<timestamp>-health-manager/
```

不会做的事：

- 不会删除真实存在的 `.jsonl`
- 不会删除 `memory/` 内容
- 不会改 Feishu appId / secret
- 不会改 agent workspace
- 不会重启 gateway

## 每日自动化建议

如果做每日自动任务，推荐先跑只读模式：

```bash
python3 skills/openclaw-health-manager/scripts/openclaw_health_check.py \
  --output-dir /Users/echo/Desktop/DMS/05_SYSTEM_DOCS/openclaw-health-reports
```

只有当你确认这套环境已经稳定后，再考虑把：

```bash
--repair-broken-session-refs
```

加进去。

## 推荐执行 Agent

这个 skill 的推荐日常执行 Agent 是：

- `kou_zi`

原因：

- `kou_zi` 已经承担系统检查类定时任务
- `kou_zi` 更适合处理 session、脚本、配置、修复建议
- 这类任务不需要 `Mini` 长期占住主会话

推荐的 cron 设计：

- `agentId`: `kou_zi`
- `sessionTarget`: `isolated`
- `wakeMode`: `now`
- `delivery.mode`: `announce` 或 `none`

推荐 payload：

```text
运行 openclaw-health-manager 技能，对当前 OpenClaw 环境做每日巡检。

步骤：
1. 执行：
   python3 /Users/echo/Desktop/DMS/skills/openclaw-health-manager/scripts/openclaw_health_check.py --output-dir /Users/echo/Desktop/DMS/05_SYSTEM_DOCS/openclaw-health-reports
2. 读取最新报告
3. 如果发现 broken_session_refs > 0，只汇报，不自动修复
4. 如果发现 gateway / ACP / Feishu bindings 异常，明确列出问题
5. 输出简要总结：正常项 / 风险项 / 是否需要人工处理
```

如果后续你要升级成“半自动修复版”，建议单独再建第二个 cron job，不要直接覆盖每日巡检任务。

## memory 管理建议

这个 skill 的 memory 管理是“巡检 + 报告”，不是激进清理。

它会重点给出：

- 哪个 agent 没有 `memory/`
- 哪个 agent 最近几天没有新增 daily memory
- 哪个 agent 缺少 `MEMORY.md`
- 哪个 agent 的 session 数量异常多、但 memory 长期没更新

如果用户要进一步“整理 memory 内容”，再单独做人工或 agent 级整理，不建议放到每日自动修复里。

## 报告输出

默认会输出：

- 终端摘要
- 一份 JSON 报告
- 一份 Markdown 报告

字段说明见：

- `references/report-fields.md`

## 使用原则

- 先跑只读检查
- 看到 `broken_session_refs` 再决定是否修复
- 如果是 Feishu 收不到消息，优先看主日志，不要先删 memory
- 如果是 agent 不回消息，优先分辨是：
  - 没收到消息
  - 收到后没 dispatch
  - dispatch 后 `replies=0`
  - session 坏引用

## 和 ACP / Claude Code 的关系

这个 skill 本身不直接调 Claude Code。

它负责维护的是：

- OpenClaw 主运行环境
- 多 agent 绑定健康度
- ACP 配置完整性
- memory / session 可用性

如果用户要“发现异常后自动交给 Claude Code 修”，应由上层 agent 先运行本 skill，拿到报告后，再用 ACP 调 `agentId: "claude"` 做进一步修复。
