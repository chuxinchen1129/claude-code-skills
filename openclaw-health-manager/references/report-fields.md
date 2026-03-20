# OpenClaw Health Report Fields

## 顶层字段

- `timestamp`: 报告生成时间
- `config_path`: 主配置路径
- `gateway`: gateway 状态
- `config`: 主配置检查结果
- `agents`: 各 agent 巡检结果
- `summary`: 汇总统计
- `repairs`: 本次实际执行的修复动作

## gateway

- `listed`: `launchctl list` 是否能看到 `ai.openclaw.gateway`
- `pid`: 当前 PID
- `status_code`: `launchctl` 状态码

## config

- `dm_scope_ok`: 是否为 `per-account-channel-peer`
- `acpx_enabled`: ACPX 插件是否启用
- `allowed_agents`: `acp.allowedAgents`
- `claude_allowed`: 是否允许 `claude`
- `feishu_accounts`: 飞书账号列表
- `feishu_binding_agent_ids`: 飞书绑定到的 agent 列表
- `binding_mismatches`: 没有正确绑定的账号

## agents[*]

- `agent_id`
- `workspace`
- `workspace_exists`
- `memory_dir_exists`
- `memory_files`
- `latest_memory_file`
- `latest_memory_age_days`
- `memory_md_exists`
- `sessions_json_exists`
- `indexed_sessions`
- `broken_session_refs`
- `orphan_jsonl_files`

## summary

- `total_agents`
- `agents_with_broken_sessions`
- `agents_missing_memory_dir`
- `agents_stale_memory`
- `total_broken_session_refs`
- `total_orphan_jsonl_files`

## repairs

- `removed_broken_session_refs`
- `backup_dir`

