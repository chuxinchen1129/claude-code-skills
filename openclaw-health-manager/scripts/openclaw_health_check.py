#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


OPENCLAW_HOME = Path("/Users/echo/.openclaw")
CONFIG_PATH = OPENCLAW_HOME / "openclaw.json"
DEFAULT_OUTPUT_DIR = Path("/Users/echo/Desktop/DMS/05_SYSTEM_DOCS/openclaw-health-reports")
SESSION_RESET_BASE = OPENCLAW_HOME / "session-resets"
GATEWAY_LABEL = "ai.openclaw.gateway"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def now_local() -> dt.datetime:
    return dt.datetime.now().astimezone()


def iso_now() -> str:
    return now_local().isoformat(timespec="seconds")


def launchctl_status() -> dict[str, Any]:
    proc = run(["launchctl", "list"])
    listed = False
    pid = None
    status_code = None
    for line in proc.stdout.splitlines():
        if GATEWAY_LABEL not in line:
            continue
        listed = True
        parts = line.split()
        if len(parts) >= 3:
            pid = None if parts[0] == "-" else parts[0]
            status_code = parts[1]
        break
    return {
        "listed": listed,
        "pid": pid,
        "status_code": status_code,
    }


def parse_date_from_name(path: Path) -> dt.date | None:
    if not DATE_RE.match(path.name):
        return None
    try:
        return dt.date.fromisoformat(path.stem)
    except ValueError:
        return None


def agent_memory_state(workspace: Path) -> dict[str, Any]:
    memory_dir = workspace / "memory"
    result: dict[str, Any] = {
        "memory_dir_exists": memory_dir.is_dir(),
        "memory_files": 0,
        "latest_memory_file": None,
        "latest_memory_age_days": None,
        "memory_md_exists": (workspace / "MEMORY.md").exists(),
    }
    if not memory_dir.is_dir():
        return result

    daily_files = []
    for path in memory_dir.iterdir():
        if path.is_file() and parse_date_from_name(path):
            daily_files.append(path)
    daily_files.sort()
    result["memory_files"] = len(daily_files)
    if daily_files:
        latest = daily_files[-1]
        latest_date = parse_date_from_name(latest)
        result["latest_memory_file"] = str(latest)
        if latest_date:
            result["latest_memory_age_days"] = (now_local().date() - latest_date).days
    return result


def agent_session_state(agent_id: str) -> dict[str, Any]:
    sessions_dir = OPENCLAW_HOME / "agents" / agent_id / "sessions"
    sessions_json = sessions_dir / "sessions.json"
    result: dict[str, Any] = {
        "sessions_dir": str(sessions_dir),
        "sessions_json_exists": sessions_json.exists(),
        "indexed_sessions": 0,
        "broken_session_refs": [],
        "orphan_jsonl_files": [],
    }
    if not sessions_json.exists():
        return result

    try:
        data = load_json(sessions_json)
    except Exception as exc:
        result["parse_error"] = str(exc)
        return result

    result["indexed_sessions"] = len(data)
    referenced: set[str] = set()
    for key, value in data.items():
        session_file = value.get("sessionFile")
        if isinstance(session_file, str) and session_file:
            referenced.add(session_file)
            if not Path(session_file).exists():
                result["broken_session_refs"].append({
                    "key": key,
                    "sessionFile": session_file,
                })

    orphan_files = []
    if sessions_dir.exists():
        for file_path in sessions_dir.glob("*.jsonl"):
            if str(file_path) not in referenced:
                orphan_files.append(str(file_path))
    result["orphan_jsonl_files"] = sorted(orphan_files)
    return result


def backup_sessions_json(agent_id: str, source: Path, backup_root: Path) -> None:
    target_dir = backup_root / agent_id
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target_dir / "sessions.json.bak")


def repair_broken_session_refs(agent_id: str, backup_root: Path) -> dict[str, Any]:
    sessions_dir = OPENCLAW_HOME / "agents" / agent_id / "sessions"
    sessions_json = sessions_dir / "sessions.json"
    if not sessions_json.exists():
        return {"agent_id": agent_id, "removed": 0}

    data = load_json(sessions_json)
    broken_keys = []
    for key, value in data.items():
        session_file = value.get("sessionFile")
        if isinstance(session_file, str) and session_file and not Path(session_file).exists():
            broken_keys.append(key)

    if not broken_keys:
        return {"agent_id": agent_id, "removed": 0}

    backup_sessions_json(agent_id, sessions_json, backup_root)
    for key in broken_keys:
        del data[key]

    with sessions_json.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    return {"agent_id": agent_id, "removed": len(broken_keys), "keys": broken_keys}


def build_report() -> dict[str, Any]:
    config = load_json(CONFIG_PATH)
    agents = config.get("agents", {}).get("list", [])
    feishu_accounts = config.get("channels", {}).get("feishu", {}).get("accounts", {})
    bindings = config.get("bindings", [])
    feishu_bindings = [
        b for b in bindings
        if b.get("match", {}).get("channel") == "feishu" and b.get("match", {}).get("accountId")
    ]
    bound_account_ids = {b["match"]["accountId"] for b in feishu_bindings}
    account_ids = set(feishu_accounts.keys())

    report: dict[str, Any] = {
        "timestamp": iso_now(),
        "config_path": str(CONFIG_PATH),
        "gateway": launchctl_status(),
        "config": {
            "dm_scope_ok": config.get("session", {}).get("dmScope") == "per-account-channel-peer",
            "acpx_enabled": config.get("plugins", {}).get("entries", {}).get("acpx", {}).get("enabled") is True,
            "allowed_agents": config.get("acp", {}).get("allowedAgents", []),
            "claude_allowed": "claude" in set(config.get("acp", {}).get("allowedAgents", [])),
            "feishu_accounts": sorted(account_ids),
            "feishu_binding_agent_ids": sorted(b.get("agentId") for b in feishu_bindings),
            "binding_mismatches": sorted(account_ids - bound_account_ids),
        },
        "agents": [],
        "summary": {},
        "repairs": {
            "removed_broken_session_refs": [],
            "backup_dir": None,
        },
    }

    stale_memory_agents = []
    broken_session_agents = []
    missing_memory_agents = []
    total_broken = 0
    total_orphans = 0

    for agent in agents:
        agent_id = agent["id"]
        workspace = Path(agent["workspace"])
        memory_state = agent_memory_state(workspace)
        session_state = agent_session_state(agent_id)
        agent_result = {
            "agent_id": agent_id,
            "workspace": str(workspace),
            "workspace_exists": workspace.exists(),
            **memory_state,
            **session_state,
        }
        report["agents"].append(agent_result)
        if not memory_state["memory_dir_exists"]:
            missing_memory_agents.append(agent_id)
        if memory_state["latest_memory_age_days"] is None or memory_state["latest_memory_age_days"] > 3:
            stale_memory_agents.append(agent_id)
        if session_state["broken_session_refs"]:
            broken_session_agents.append(agent_id)
            total_broken += len(session_state["broken_session_refs"])
        total_orphans += len(session_state["orphan_jsonl_files"])

    report["summary"] = {
        "total_agents": len(agents),
        "agents_with_broken_sessions": broken_session_agents,
        "agents_missing_memory_dir": missing_memory_agents,
        "agents_stale_memory": stale_memory_agents,
        "total_broken_session_refs": total_broken,
        "total_orphan_jsonl_files": total_orphans,
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"# OpenClaw 健康巡检报告")
    lines.append("")
    lines.append(f"- 生成时间: `{report['timestamp']}`")
    lines.append(f"- 配置文件: `{report['config_path']}`")
    lines.append("")
    gateway = report["gateway"]
    lines.append("## 总览")
    lines.append("")
    lines.append(f"- Gateway 已登记: `{gateway['listed']}`")
    lines.append(f"- Gateway PID: `{gateway['pid']}`")
    lines.append(f"- Gateway 状态码: `{gateway['status_code']}`")
    lines.append(f"- dmScope 正确: `{report['config']['dm_scope_ok']}`")
    lines.append(f"- ACPX 启用: `{report['config']['acpx_enabled']}`")
    lines.append(f"- Claude 已放行: `{report['config']['claude_allowed']}`")
    lines.append(f"- 飞书绑定缺口: `{', '.join(report['config']['binding_mismatches']) or '无'}`")
    lines.append("")
    lines.append("## Agent 详情")
    lines.append("")
    for agent in report["agents"]:
        lines.append(f"### {agent['agent_id']}")
        lines.append(f"- workspace 存在: `{agent['workspace_exists']}`")
        lines.append(f"- memory 目录存在: `{agent['memory_dir_exists']}`")
        lines.append(f"- MEMORY.md 存在: `{agent['memory_md_exists']}`")
        lines.append(f"- daily memory 文件数: `{agent['memory_files']}`")
        lines.append(f"- 最近 memory 文件: `{agent['latest_memory_file']}`")
        lines.append(f"- 最近 memory 距今天数: `{agent['latest_memory_age_days']}`")
        lines.append(f"- sessions.json 存在: `{agent['sessions_json_exists']}`")
        lines.append(f"- 已索引 session 数: `{agent['indexed_sessions']}`")
        lines.append(f"- 坏 session 引用数: `{len(agent['broken_session_refs'])}`")
        lines.append(f"- 孤儿 jsonl 数: `{len(agent['orphan_jsonl_files'])}`")
        lines.append("")
    lines.append("## 汇总")
    lines.append("")
    summary = report["summary"]
    lines.append(f"- 总 agent 数: `{summary['total_agents']}`")
    lines.append(f"- 存在坏 session 引用的 agent: `{', '.join(summary['agents_with_broken_sessions']) or '无'}`")
    lines.append(f"- 缺少 memory 目录的 agent: `{', '.join(summary['agents_missing_memory_dir']) or '无'}`")
    lines.append(f"- memory 可能过旧的 agent: `{', '.join(summary['agents_stale_memory']) or '无'}`")
    lines.append(f"- 坏 session 引用总数: `{summary['total_broken_session_refs']}`")
    lines.append(f"- 孤儿 jsonl 总数: `{summary['total_orphan_jsonl_files']}`")
    if report["repairs"]["removed_broken_session_refs"]:
        lines.append("")
        lines.append("## 修复动作")
        lines.append("")
        lines.append(f"- 备份目录: `{report['repairs']['backup_dir']}`")
        for item in report["repairs"]["removed_broken_session_refs"]:
            lines.append(f"- {item['agent_id']}: 删除坏引用 `{item['removed']}` 条")
    return "\n".join(lines) + "\n"


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_outputs(report: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    ensure_output_dir(output_dir)
    stamp = now_local().strftime("%Y%m%d-%H%M%S")
    json_path = output_dir / f"openclaw-health-{stamp}.json"
    md_path = output_dir / f"openclaw-health-{stamp}.md"
    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with md_path.open("w", encoding="utf-8") as fh:
        fh.write(render_markdown(report))
    return json_path, md_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check OpenClaw health and memory/session integrity.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--repair-broken-session-refs", action="store_true")
    parser.add_argument("--json-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not CONFIG_PATH.exists():
        print(json.dumps({"error": f"config not found: {CONFIG_PATH}"}, ensure_ascii=False))
        return 1

    report = build_report()

    if args.repair_broken_session_refs:
        stamp = now_local().strftime("%Y%m%d-%H%M%S")
        backup_dir = SESSION_RESET_BASE / f"{stamp}-health-manager"
        repairs = []
        for agent in report["summary"]["agents_with_broken_sessions"]:
            repairs.append(repair_broken_session_refs(agent, backup_dir))
        report["repairs"]["removed_broken_session_refs"] = [r for r in repairs if r.get("removed")]
        report["repairs"]["backup_dir"] = str(backup_dir) if repairs else None
        report = build_report() | {"repairs": report["repairs"]}

    output_dir = Path(args.output_dir)
    json_path, md_path = write_outputs(report, output_dir)

    if args.json_only:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report))
        print(f"JSON: {json_path}")
        print(f"Markdown: {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
