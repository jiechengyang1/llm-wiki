#!/usr/bin/env python3
"""Lint final page resource references and the 2 MiB HTML limit."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

MAX_HTML_BYTES = 2 * 1024 * 1024
PINNED_VERSION = re.compile(r"(?:@|/)(?:v?\d+\.\d+(?:\.\d+)?)(?:[/?#.-]|$)", re.I)


def _finding(severity: str, code: str, message: str, source: str = "") -> dict[str, str]:
    result = {"severity": severity, "code": code, "message": message}
    if source:
        result["source"] = source
    return result


class ResourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, str]] = []
        self.inline_blocks: list[str] = []
        self._capture: list[str] | None = None
        self.base_hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        if tag in {"style", "script"} and not attrs.get("src"):
            self._capture = []
        if tag == "base" and attrs.get("href"):
            self.base_hrefs.append(attrs["href"])
        resource_attrs = {
            "img": ("src",),
            "source": ("src",),
            "script": ("src",),
            "link": ("href",),
            "video": ("src", "poster"),
            "audio": ("src",),
            "iframe": ("src",),
            "object": ("data",),
        }
        for attr in resource_attrs.get(tag, ()):
            if attrs.get(attr):
                kind = "script" if tag == "script" else "stylesheet" if tag == "link" else "html"
                self.refs.append((attrs[attr], kind))
        if attrs.get("srcset"):
            for item in attrs["srcset"].split(","):
                value = item.strip().split()[0] if item.strip() else ""
                if value:
                    self.refs.append((value, "html"))

    def handle_endtag(self, tag: str) -> None:
        if tag in {"style", "script"} and self._capture is not None:
            self.inline_blocks.append("".join(self._capture))
            self._capture = None

    def handle_data(self, data: str) -> None:
        if self._capture is not None:
            self._capture.append(data)


def _embedded_refs(text: str) -> list[str]:
    refs = re.findall(r"url\(\s*['\"]?([^)'\"\s]+)", text, re.I)
    refs += re.findall(r"@import\s+(?:url\()?\s*['\"]([^'\"]+)", text, re.I)
    refs += re.findall(r"\bimport\s*(?:\([^'\"]*|[^;]*?\bfrom\s*)['\"]([^'\"]+)['\"]", text)
    return refs


def lint(path: Path, text: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    size = len(text.encode("utf-8"))
    if size > MAX_HTML_BYTES:
        findings.append(_finding("error", "html-size", f"HTML 为 {size} bytes，超过 2 MiB"))
    parser = ResourceParser()
    parser.feed(text)
    parser.close()
    for href in parser.base_hrefs:
        findings.append(_finding("error", "source-base", "最终 HTML 不应保留来源 <base>", href))

    refs = parser.refs[:]
    refs.extend((ref, "embedded") for block in parser.inline_blocks for ref in _embedded_refs(block))
    seen: set[str] = set()
    for source, kind in refs:
        source = source.strip()
        if not source or source in seen:
            continue
        seen.add(source)
        lower = source.lower()
        if lower.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        if lower.startswith("data:"):
            continue
        if lower.startswith("file://"):
            findings.append(_finding("error", "file-url", "禁止 file:// 资源", source))
            continue
        if re.match(r"^(?:/[A-Za-z]|[A-Za-z]:[\\/])", source):
            findings.append(_finding("error", "absolute-local-path", "禁止开发机绝对路径", source))
            continue
        parsed = urlparse(source)
        if parsed.scheme in {"http", "https"}:
            if parsed.scheme != "https":
                findings.append(_finding("warning", "insecure-remote", "远程资源应使用 HTTPS", source))
            if parsed.hostname in {"localhost", "127.0.0.1", "0.0.0.0"}:
                findings.append(_finding("error", "localhost", "发布页不能依赖 localhost", source))
            if re.search(r"(?:@|/)(?:latest|next)(?:[/?#.-]|$)", source, re.I):
                findings.append(_finding("error", "floating-version", "远程依赖不能使用 latest/next", source))
            elif kind in {"script", "stylesheet", "embedded"} and not PINNED_VERSION.search(source):
                findings.append(_finding("warning", "unpinned-remote", "远程代码/样式未发现固定版本", source))
            continue
        if parsed.scheme:
            findings.append(_finding("warning", "unknown-scheme", "无法确认资源协议", source))
            continue
        clean_path = source.split("?", 1)[0].split("#", 1)[0]
        candidate = (path.parent / clean_path).resolve()
        try:
            candidate.relative_to(path.parent.resolve())
        except ValueError:
            findings.append(_finding("error", "path-traversal", "资源越出页面工作目录", source))
            continue
        if not candidate.exists():
            findings.append(_finding("error", "missing-relative", "相对资源不存在或尚未上传/内联", source))
        else:
            findings.append(_finding("error", "unresolved-relative", "最终 HTML 仍依赖本地相对资源，需内联或上传改写", source))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", help="Final HTML file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        path = Path(args.html)
        text = path.read_text(encoding="utf-8")
        findings = lint(path, text)
    except (OSError, UnicodeError) as exc:
        sys.stderr.write(f"resource lint failed: {exc}\n")
        return 2
    errors = sum(item["severity"] == "error" for item in findings)
    warnings = sum(item["severity"] == "warning" for item in findings)
    if args.json:
        print(json.dumps({"ok": errors == 0, "errors": errors, "warnings": warnings, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        for item in findings:
            suffix = f" ({item['source']})" if item.get("source") else ""
            print(f"{item['severity'].upper()} [{item['code']}] {item['message']}{suffix}")
        print(f"errors={errors} warnings={warnings}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
