#!/usr/bin/env python3
"""Lint HTML for the current MSpace page Database SDK contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

CURRENT_METHODS = {
    "query",
    "addRecord",
    "getRecord",
    "updateRecord",
    "deleteRecord",
    "getSchema",
    "uploadImage",
    "onUpdated",
}
DYNAMIC_METHODS = CURRENT_METHODS - {"uploadImage", "onUpdated"}
LEGACY_KEYS = (
    "databaseId",
    "recordId",
    "pageSize",
    "startCursor",
    "nextCursor",
    "hasMore",
)


def _finding(severity: str, code: str, message: str) -> dict[str, str]:
    return {"severity": severity, "code": code, "message": message}


def _sdk_receivers(text: str) -> str:
    aliases = set(
        re.findall(
            r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:window\s*\.\s*)?__SPACE_PAGE__\s*\.\s*database",
            text,
        )
    )
    receivers = [r"(?:window\s*\.\s*)?__SPACE_PAGE__\s*\.\s*database"]
    receivers.extend(rf"\b{re.escape(alias)}" for alias in sorted(aliases))
    return "(?:" + "|".join(receivers) + ")"


def _method_pattern(text: str, method: str, suffix: str = "") -> re.Pattern[str]:
    return re.compile(rf"{_sdk_receivers(text)}\s*\.\s*{re.escape(method)}\s*\({suffix}", re.S)


def _object_calls(text: str, method: str) -> list[str]:
    calls: list[str] = []
    pattern = _method_pattern(text, method, r"\s*\{")
    for match in pattern.finditer(text):
        start = match.end() - 1
        depth = 0
        quote = ""
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = ""
                continue
            if char in {"'", '"', "`"}:
                quote = char
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    calls.append(text[start + 1:index])
                    break
    return calls


def _has_key(body: str, key: str) -> bool:
    named = rf"(?:['\"]{re.escape(key)}['\"]|{re.escape(key)})"
    return bool(
        re.search(rf"(?:^|[,\s]){named}\s*:", body)
        or re.search(rf"(?:^|,)\s*{re.escape(key)}\s*(?:,|$)", body)
    )


def _load_schema(path: str | None) -> set[str] | None:
    if not path:
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
        payload = payload["data"]
    properties = payload.get("properties") if isinstance(payload, dict) else None
    if not isinstance(properties, list):
        raise ValueError("schema must contain a properties array")
    names = {
        item["name"]
        for item in properties
        if isinstance(item, dict) and isinstance(item.get("name"), str) and item["name"].strip()
    }
    return names


def lint(text: str, schema_fields: set[str] | None = None) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    uses_current = bool(re.search(r"(?:window\s*\.\s*)?__SPACE_PAGE__\s*\.\s*database", text))
    methods = {
        method
        for method in CURRENT_METHODS
        if _method_pattern(text, method).search(text)
    }
    if "__SMART_PAGE__" in text:
        findings.append(_finding("error", "legacy-global", "检测到已废弃页面 SDK 全局；只使用 window.__SPACE_PAGE__.database"))
    for key in LEGACY_KEYS:
        if re.search(rf"\b{key}\b", text):
            findings.append(_finding("error", "legacy-key", f"禁止 camelCase 字段 {key}"))
    if methods.intersection(DYNAMIC_METHODS) and not uses_current:
        findings.append(_finding("error", "missing-current-global", "Database 动态调用必须来自 window.__SPACE_PAGE__.database"))

    if re.search(r"(?:fetch\s*\(|new\s+XMLHttpRequest\s*\(|axios\s*\.)[^\n]*(?:/api/v1/tools|query-database|storage_table)", text, re.I):
        findings.append(_finding("error", "browser-gateway-call", "页面运行期不得直接调用 Gateway Database API"))

    required_keys = {
        "query": ("database_id",),
        "addRecord": ("database_id", "record"),
        "getRecord": ("database_id", "record_id"),
        "updateRecord": ("database_id", "record_id", "properties"),
        "deleteRecord": ("database_id", "record_id"),
        "getSchema": ("database_id",),
        "uploadImage": ("file",),
    }
    for method, keys in required_keys.items():
        literal_calls = _object_calls(text, method)
        method_count = len(_method_pattern(text, method).findall(text))
        for body in literal_calls:
            for key in keys:
                if not _has_key(body, key):
                    findings.append(_finding("error", "missing-param", f"{method} 缺少参数 {key}"))
            if method == "addRecord" and _has_key(body, "properties"):
                findings.append(_finding("error", "add-record-shape", "addRecord 使用 record，不使用 properties"))
            if method == "uploadImage":
                for unsupported in ("data", "contentType", "fileName"):
                    if _has_key(body, unsupported):
                        findings.append(_finding("error", "upload-image-shape", f"uploadImage 不接受 {unsupported}"))
        if method_count and not literal_calls:
            findings.append(_finding("warning", "dynamic-params", f"无法静态展开 {method} 参数；运行前按当前 schema 人工核对"))

    if "query" in methods:
        if not re.search(r"\.\s*results\b|\[\s*['\"]results['\"]\s*\]", text):
            findings.append(_finding("warning", "query-result", "query 结果未发现 results 读取"))
        for key in ("next_cursor", "has_more"):
            if re.search(r"\b(?:cursor|page_size)\b", text) and not re.search(rf"\b{key}\b", text):
                findings.append(_finding("warning", "query-pagination", f"分页逻辑未发现 {key}"))
    if methods.intersection({"query", "getRecord"}):
        if not re.search(r"\.\s*fields\b|\[\s*['\"]fields['\"]\s*\]", text):
            findings.append(_finding("warning", "record-shape", "记录读取未发现 record.fields"))
        if re.search(r"\.\s*_id\b|\[\s*['\"]_id['\"]\s*\]", text):
            findings.append(_finding("error", "record-id-shape", "记录没有 _id 合同；使用 record.record_id"))
    if methods.intersection({"addRecord", "updateRecord", "deleteRecord"}) and re.search(
        r"(?:created|updated|deleted|result)\s*\.\s*record_id\b", text
    ):
        findings.append(_finding("error", "write-result-id", "写操作结果 ID 字段是 id，不是 record_id"))
    if "onUpdated" in methods:
        if re.search(r"event\s*\.\s*(?:databaseId|recordId)\b", text):
            findings.append(_finding("error", "updated-event-shape", "onUpdated 事件使用 database_id/record_id"))
        if re.search(r"(?:其他用户|跨标签页|全局实时|realtime subscription|real-time subscription)", text, re.I):
            findings.append(_finding("error", "updated-event-scope", "onUpdated 不是跨客户端实时订阅"))

    if schema_fields is not None:
        references: set[str] = set()
        patterns = (
            r"\.fields\s*\[\s*['\"]([^'\"]+)['\"]\s*\]",
            r"\bproperty\s*:\s*['\"]([^'\"]+)['\"]",
        )
        for pattern in patterns:
            references.update(re.findall(pattern, text))
        for body in _object_calls(text, "addRecord") + _object_calls(text, "updateRecord"):
            nested = re.search(r"\b(?:record|properties)\s*:\s*\{(.*)\}\s*$", body, re.S)
            if nested:
                references.update(re.findall(r"['\"]([^'\"]+)['\"]\s*:", nested.group(1)))
        for name in sorted(references - schema_fields):
            findings.append(_finding("error", "unknown-field", f"真实 schema 中不存在字段：{name}"))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", help="HTML file to lint")
    parser.add_argument("--schema", help="getSchema response JSON")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result")
    args = parser.parse_args(argv)
    try:
        text = Path(args.html).read_text(encoding="utf-8")
        findings = lint(text, _load_schema(args.schema))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        sys.stderr.write(f"lint failed: {exc}\n")
        return 2
    errors = sum(item["severity"] == "error" for item in findings)
    warnings = sum(item["severity"] == "warning" for item in findings)
    if args.json:
        print(json.dumps({"ok": errors == 0, "errors": errors, "warnings": warnings, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        for item in findings:
            print(f"{item['severity'].upper()} [{item['code']}] {item['message']}")
        print(f"errors={errors} warnings={warnings}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
