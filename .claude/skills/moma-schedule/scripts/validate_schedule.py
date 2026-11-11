#!/usr/bin/env python3
"""离线校验云端创建参数；不调用 API，不修改 payload。"""

import argparse
from datetime import datetime
import json
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def validate_execution_context(context):
    """普通任务仅需 text；使用 skill 时校验 skills 与 mention.skill。"""
    if not isinstance(context, dict):
        raise ValueError("execution_context 必须为对象")
    user_input = context.get("user_input")
    if not isinstance(user_input, dict):
        raise ValueError("execution_context.user_input 必须为对象")
    text = user_input.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("execution_context.user_input.text 必须为非空字符串")
    for field in ("skills", "attachments", "html_snippets"):
        if field in user_input and not isinstance(user_input[field], list):
            raise ValueError(f"execution_context.user_input.{field} 必须为数组")
    skills = user_input.get("skills", [])
    mention = user_input.get("mention", {})
    if not isinstance(mention, dict):
        raise ValueError("execution_context.user_input.mention 必须为对象，不能为数组")
    if "skills" in mention:
        raise ValueError("skill 引用字段为 mention.skill，不是 mention.skills")
    mentioned = mention.get("skill", [])
    if not isinstance(mentioned, list):
        raise ValueError("execution_context.user_input.mention.skill 必须为数组")
    for field, entries in (("skills", skills), ("mention.skill", mentioned)):
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError(f"{field} 的每一项必须为 skill 对象")
            skill_id = entry.get("skill_id")
            if isinstance(skill_id, bool) or not isinstance(skill_id, (str, int)) or not str(skill_id).strip():
                raise ValueError(f"{field} 的每一项必须含有效的 skill_id")
    if [str(item["skill_id"]) for item in skills] != [str(item["skill_id"]) for item in mentioned]:
        raise ValueError("skills 与 mention.skill 必须按相同顺序引用相同的 skill")


def validate_schedule(payload):
    """校验当前支持的创建参数，失败时抛出 ValueError。"""
    if not isinstance(payload, dict):
        raise ValueError("payload 必须为 JSON 对象")
    for key in ("name", "description"):
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            raise ValueError(f"{key} 必须为非空字符串")
    if len(payload["name"]) > 200:
        raise ValueError("name 最长 200 字符")
    trigger_type = payload.get("trigger_type")
    if trigger_type not in ("cron", "date"):
        raise ValueError("trigger_type 仅支持 cron/date，不支持 interval/once")
    config = payload.get("trigger_config")
    if not isinstance(config, dict):
        raise ValueError("trigger_config 必须为对象")
    allowed = {"timezone", "cron_expression" if trigger_type == "cron" else "run_date"}
    if set(config) - allowed:
        raise ValueError("trigger_config 含当前触发类型不支持的字段")
    if trigger_type == "cron":
        expression = config.get("cron_expression")
        if not isinstance(expression, str) or len(expression.split()) != 5:
            raise ValueError("cron_expression 必须为标准 5 字段 cron 表达式")
        minute = expression.split()[0]
        if not minute.isascii() or not minute.isdigit() or not 0 <= int(minute) <= 59:
            raise ValueError("计划创建最小粒度为小时级；cron 分钟字段必须为 0–59 的单个固定值，不支持分钟级通配、步长、列表或范围")
    else:
        value = config.get("run_date")
        try:
            if not isinstance(value, str):
                raise ValueError()
            parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            if parsed.strftime("%Y-%m-%d %H:%M:%S") != value:
                raise ValueError()
        except ValueError:
            raise ValueError("run_date 必须为有效的 YYYY-MM-DD HH:mm:ss 时间") from None
    if "timezone" in config:
        try:
            if not isinstance(config["timezone"], str) or not config["timezone"]:
                raise ValueError()
            ZoneInfo(config["timezone"])
        except (ValueError, ZoneInfoNotFoundError):
            raise ValueError("timezone 必须为有效的 IANA 时区，如 Asia/Shanghai") from None
    if payload.get("output_format") not in ("message", "report", "table", "alert"):
        raise ValueError("output_format 仅支持 message/report/table/alert")
    delivery = payload.get("delivery_config")
    if not isinstance(delivery, list) or not delivery:
        raise ValueError("delivery_config 必须为非空数组")
    for channel in delivery:
        if not isinstance(channel, dict) or channel.get("type") not in ("message", "wechat"):
            raise ValueError("推送渠道 type 仅支持 message/wechat")
        if not isinstance(channel.get("config"), dict):
            raise ValueError("推送渠道 config 必须为对象")
    validate_execution_context(payload.get("execution_context"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--payload", help="直接传入完整 JSON 字符串")
    inputs.add_argument("--payload-file", help="从 JSON 文件读取")
    parser.epilog = "未指定输入参数时从标准输入读取 JSON，无需生成文件。"
    args = parser.parse_args()
    try:
        if args.payload is not None:
            payload = json.loads(args.payload)
        elif args.payload_file is not None:
            with open(args.payload_file, encoding="utf-8") as stream:
                payload = json.load(stream)
        else:
            if sys.stdin.isatty():
                parser.error("请使用 --payload、--payload-file 或通过标准输入提供 JSON")
            payload = json.load(sys.stdin)
        validate_schedule(payload)
    except (ValueError, OSError) as exc:
        print(f"参数校验失败: {exc}", file=sys.stderr)
        return 1
    print("参数校验通过；仍须执行 CLI dry-run 和审批流程。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
