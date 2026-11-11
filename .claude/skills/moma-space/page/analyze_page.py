#!/usr/bin/env python3
"""Analyze page intent and HTML into the Space page canonical schema."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

SDK_METHODS = (
    "query",
    "addRecord",
    "getRecord",
    "updateRecord",
    "deleteRecord",
    "getSchema",
    "uploadImage",
    "onUpdated",
)
WRITE_METHODS = {"addRecord", "updateRecord", "deleteRecord"}
WRITE_INTENT = re.compile(
    r"保存|持久|维护|录入|新增|创建记录|更新|修改记录|删除|增删改|提交.*(?:数据|记录)|"
    r"\b(?:save|persist|maintain|create|add|update|edit|delete)\s+(?:data|record|records)\b",
    re.I,
)
READ_INTENT = re.compile(
    r"持续数据|数据库|筛选|过滤|排序|分页|看板|查询记录|动态数据|"
    r"\b(?:database|filter|sort|pagination|dashboard|query records|dynamic data)\b",
    re.I,
)
STATIC_INTENT = re.compile(r"汇报|报告|总结|专题|叙事|一次性展示|\b(?:report|summary|story)\b", re.I)
ID_VALUE = r"[A-Za-z0-9_-]{1,64}"


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _selector(tag: str, attrs: dict[str, str], index: int) -> str:
    if attrs.get("name"):
        return f'{tag}[name="{attrs["name"]}"]'
    if attrs.get("data-field"):
        return f'{tag}[data-field="{attrs["data-field"]}"]'
    if attrs.get("id"):
        return f'#{attrs["id"]}'
    classes = [part for part in attrs.get("class", "").split() if part]
    if classes:
        return f"{tag}.{classes[0]}"
    return f"{tag}:nth-of-type({index})"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.in_title = False
        self.scripts: list[str] = []
        self._script_parts: list[str] | None = None
        self.forms = 0
        self.submit_controls = 0
        self.tables = 0
        self.table_headers: list[str] = []
        self._in_th = False
        self._th_parts: list[str] = []
        self.fields: list[dict[str, str]] = []
        self.data_fields: list[str] = []
        self.assets: list[dict[str, str]] = []
        self.tag_counts: Counter[str] = Counter()
        # label 文本收集：label_for 存 <label for="id"> 的文本；
        # _in_label/_label_for/_label_parts 跟踪当前 label；
        # _last_label_text 存最近一个已闭合 label 的文本，供兄弟式 <label></label><input> 回退
        self.label_for: dict[str, str] = {}
        self._in_label = False
        self._label_for: str | None = None
        self._label_parts: list[str] = []
        self._last_label_text: str = ""

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        self.tag_counts[tag] += 1
        index = self.tag_counts[tag]
        if tag == "title":
            self.in_title = True
        elif tag == "script":
            src = attrs.get("src")
            if src:
                self.assets.append(_asset(src, "script"))
            self._script_parts = []
        elif tag == "form":
            self.forms += 1
        elif tag == "table":
            self.tables += 1
        elif tag == "th":
            self._in_th = True
            self._th_parts = []
        elif tag == "label":
            self._in_label = True
            self._label_for = attrs.get("for") or None
            self._label_parts = []

        if tag in {"input", "select", "textarea"}:
            # 字段名优先级（对齐 html-analysis.md）：
            #   name > data-field > <label for> 文本 > 包裹式/前导 <label> 文本 > aria-label
            # 不用 DOM id 作为字段名——id 是 JS 钩子（如 f-type、m-amount），不是业务字段名
            # 不用 placeholder——它是提示文案（如"搜索备注"、"0.00"），不是业务字段名
            control_id = attrs.get("id") or ""
            # 包裹式 label：控件在 <label>内部，取当前已累积的 label 文本
            wrapping_label = _clean("".join(self._label_parts)) if self._in_label else ""
            field_name = (
                attrs.get("name")
                or attrs.get("data-field")
                or (self.label_for.get(control_id) if control_id else "")
                or wrapping_label
                or self._last_label_text
                or attrs.get("aria-label")
            )
            input_type = attrs.get("type", "text").lower()
            if field_name and input_type not in {"button", "submit", "reset", "hidden"}:
                self.fields.append(
                    {
                        "name": field_name,
                        "tag": tag,
                        "type": input_type,
                        "selector": _selector(tag, attrs, index),
                    }
                )
            if input_type == "submit":
                self.submit_controls += 1
        elif tag == "button" and attrs.get("type", "submit").lower() == "submit":
            self.submit_controls += 1

        data_field = attrs.get("data-field")
        if data_field:
            self.data_fields.append(data_field)

        if tag in {"img", "source"}:
            if attrs.get("src"):
                self.assets.append(_asset(attrs["src"], "image"))
            if attrs.get("srcset"):
                for item in attrs["srcset"].split(","):
                    url = item.strip().split()[0] if item.strip() else ""
                    if url:
                        self.assets.append(_asset(url, "image"))
        elif tag == "link" and attrs.get("href"):
            rel = attrs.get("rel", "").lower()
            kind = "stylesheet" if "stylesheet" in rel else "font" if "preload" in rel else "other"
            self.assets.append(_asset(attrs["href"], kind))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self._script_parts is not None:
            self.scripts.append("".join(self._script_parts))
            self._script_parts = None
        elif tag == "th":
            value = _clean("".join(self._th_parts))
            if value:
                self.table_headers.append(value)
            self._in_th = False
            self._th_parts = []
        elif tag == "label" and self._in_label:
            value = _clean("".join(self._label_parts))
            if value and self._label_for:
                self.label_for[self._label_for] = value
            if value:
                # 保留最近一个已闭合 label 的文本，供兄弟式 <label></label><input> 回退
                self._last_label_text = value
            self._in_label = False
            self._label_for = None
            self._label_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self._script_parts is not None:
            self._script_parts.append(data)
        if self._in_label:
            self._label_parts.append(data)
        if self._in_th:
            self._th_parts.append(data)


def _asset(source: str, kind: str) -> dict[str, str]:
    if source.startswith("data:"):
        resolution = "inline"
    elif re.match(r"^https?://", source, re.I):
        resolution = "remote"
    else:
        resolution = "unresolved"
    return {"source": source, "kind": kind, "resolution": resolution}


def _extract_sdk(html: str) -> tuple[bool, list[str], list[str]]:
    uses_current = bool(re.search(r"(?:window\s*\.\s*)?__SPACE_PAGE__\s*\.\s*database", html))
    methods = sorted(
        method
        for method in SDK_METHODS
        if re.search(rf"(?:\bdatabase|\bdb|__SPACE_PAGE__\s*\.\s*database)\s*\.\s*{method}\s*\(", html)
    )

    constants: dict[str, str] = {}
    for match in re.finditer(
        rf"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(['\"])(?P<id>{ID_VALUE})\2",
        html,
    ):
        constants[match.group(1)] = match.group("id")

    ids: set[str] = set()
    for match in re.finditer(
        rf"(?:\bdatabase_id\b|['\"]database_id['\"])\s*:\s*(?:(['\"])(?P<literal>{ID_VALUE})\1|(?P<variable>[A-Za-z_$][\w$]*))",
        html,
    ):
        literal = match.group("literal")
        variable = match.group("variable")
        if literal:
            ids.add(literal)
        elif variable in constants:
            ids.add(constants[variable])

    for name, value in constants.items():
        if "DATABASE" in name.upper() and "ID" in name.upper():
            ids.add(value)
    return uses_current, methods, sorted(ids)


def _value_type(field: dict[str, str]) -> str:
    if field["tag"] == "select":
        return "select"
    if field["type"] in {"number", "range"}:
        return "number"
    return "text"


def analyze(html: str, intent: str, source: list[str]) -> dict[str, Any]:
    parser = PageParser()
    parser.feed(html)
    parser.close()
    uses_sdk, methods, database_ids = _extract_sdk(html)
    write_signal = bool(WRITE_METHODS.intersection(methods)) or bool(WRITE_INTENT.search(intent))
    read_signal = uses_sdk or bool(READ_INTENT.search(intent))
    static_signal = bool(STATIC_INTENT.search(intent))
    form_signal = parser.forms > 0 and bool(parser.fields)

    if uses_sdk or write_signal:
        level = "strong"
        reason = "页面使用当前 Database SDK" if uses_sdk else "需求明确要求记录持久化或维护"
    elif read_signal and form_signal:
        level = "medium"
        reason = "结构化表单与持续数据需求同时存在"
    elif read_signal:
        level = "medium"
        reason = "需求包含查询、筛选、分页或持续数据"
    elif form_signal:
        level = "medium"
        reason = "页面包含可提交的结构化表单，但未发现明确持久化要求"
    elif parser.tables or parser.data_fields:
        level = "weak"
        reason = "页面含结构化展示，但没有持续维护证据"
    else:
        level = "none"
        reason = "未发现 Database 需求证据"

    if level == "strong" or (level == "medium" and read_signal):
        output_mode = "database-readwrite" if write_signal else "database-readonly"
    else:
        output_mode = "static"
    if static_signal and not uses_sdk and not write_signal and level in {"none", "weak"}:
        output_mode = "static"

    if form_signal and (parser.tables or parser.data_fields):
        page_type = "mixed"
    elif form_signal:
        page_type = "form"
    else:
        page_type = "display"

    bindings: dict[str, dict[str, str]] = {}
    properties: list[dict[str, Any]] = []
    seen_fields: set[str] = set()
    for field in parser.fields:
        name = field["name"]
        if name in seen_fields:
            continue
        seen_fields.add(name)
        value_type = _value_type(field)
        config: dict[str, Any] = {value_type: "" if value_type == "text" else 0 if value_type == "number" else {}}
        properties.append({"name": name, "config": config})
        bindings[name] = {
            "value_type": value_type,
            "write_support": "confirmed" if value_type in {"text", "number", "select", "multi_select"} else "unknown",
            "form_selector": field["selector"],
        }
    for name in parser.table_headers + parser.data_fields:
        if name in seen_fields:
            if name in bindings and "display_selector" not in bindings[name]:
                bindings[name]["display_selector"] = f'[data-field="{name}"]'
            continue
        seen_fields.add(name)
        properties.append({"name": name, "config": {"text": ""}})
        bindings[name] = {
            "value_type": "text",
            "write_support": "confirmed",
            "display_selector": f'[data-field="{name}"]',
        }

    databases = []
    if output_mode.startswith("database") or database_ids:
        ids_or_none: list[str | None] = database_ids or [None]
        for database_id in ids_or_none:
            entry: dict[str, Any] = {
                "title": _clean("".join(parser.title_parts)) or "未命名 Database",
                "properties": properties,
                "bindings": bindings,
            }
            if database_id:
                entry["source_database_id"] = database_id
            databases.append(entry)

    signals: list[str] = []
    if uses_sdk:
        signals.append("current-sdk")
    if form_signal:
        signals.append("form")
    if parser.tables:
        signals.append("table")
    if write_signal:
        signals.append("record-write")
    if re.search(r"\b(?:fetch|XMLHttpRequest)\s*\(?", html):
        signals.append("external-data")

    evidence_count = sum((bool(intent.strip()), bool(html.strip()), uses_sdk, form_signal, bool(parser.tables)))
    confidence = "high" if uses_sdk or evidence_count >= 3 else "medium" if evidence_count >= 2 else "low"
    assets = list({(item["source"], item["kind"]): item for item in parser.assets}.values())
    return {
        "schema_version": "1.0",
        "title": _clean("".join(parser.title_parts)) or _clean(intent)[:80] or "未命名页面",
        "output_mode": output_mode,
        "page_type": page_type,
        "needs_database": {"level": level, "reason": reason},
        "databases": databases,
        "sdk": {
            "uses_current_sdk": uses_sdk,
            "methods": methods,
            "database_ids": database_ids,
        },
        "assets": assets,
        "signals": signals,
        "source": source,
        "confidence": confidence,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", help="HTML file to analyze")
    parser.add_argument("--intent", default="", help="Original user requirement")
    parser.add_argument("--out", help="Write JSON to this file")
    args = parser.parse_args(argv)
    if not args.html and not args.intent.strip():
        parser.error("at least one of --html or --intent is required")

    html = ""
    source: list[str] = []
    try:
        if args.html:
            path = Path(args.html)
            html = path.read_text(encoding="utf-8")
            source.append(str(path))
        if args.intent.strip():
            source.append("intent")
        result = analyze(html, args.intent, source)
        encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.out:
            Path(args.out).write_text(encoded, encoding="utf-8")
        else:
            sys.stdout.write(encoded)
        return 0
    except (OSError, UnicodeError) as exc:
        sys.stderr.write(json.dumps({"error": str(exc)}, ensure_ascii=False) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
