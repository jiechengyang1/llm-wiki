#!/usr/bin/env python3
"""Remap multiple Database IDs in HTML without chained replacements."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ID_CHAR = r"A-Za-z0-9_-"


def _load_mapping(value: str) -> dict[str, str]:
    if value.startswith("@"):
        payload = json.loads(Path(value[1:]).read_text(encoding="utf-8"))
    else:
        payload = json.loads(value)
    if not isinstance(payload, dict) or not payload:
        raise ValueError("mapping must be a non-empty JSON object")
    mapping: dict[str, str] = {}
    for old, new in payload.items():
        if not isinstance(old, str) or not isinstance(new, str) or not old or not new:
            raise ValueError("mapping keys and values must be non-empty strings")
        if not re.fullmatch(rf"[{ID_CHAR}]{{1,64}}", old) or not re.fullmatch(rf"[{ID_CHAR}]{{1,64}}", new):
            raise ValueError(f"invalid Database ID mapping: {old!r} -> {new!r}")
        if old == new:
            raise ValueError(f"source and target IDs are equal: {old}")
        mapping[old] = new
    if set(mapping).intersection(mapping.values()):
        raise ValueError("source IDs and target IDs must not overlap; chained mappings are ambiguous")
    if len(set(mapping.values())) != len(mapping):
        raise ValueError("each source Database ID must map to a unique target ID")
    return mapping


def remap(text: str, mapping: dict[str, str]) -> tuple[str, dict[str, dict[str, int]]]:
    alternatives = "|".join(re.escape(item) for item in sorted(mapping, key=len, reverse=True))
    pattern = re.compile(rf"(?<![{ID_CHAR}])(?:{alternatives})(?![{ID_CHAR}])")
    before = {old: len(re.findall(rf"(?<![{ID_CHAR}]){re.escape(old)}(?![{ID_CHAR}])", text)) for old in mapping}
    output = pattern.sub(lambda match: mapping[match.group(0)], text)
    report: dict[str, dict[str, int]] = {}
    for old, new in mapping.items():
        remaining = len(re.findall(rf"(?<![{ID_CHAR}]){re.escape(old)}(?![{ID_CHAR}])", output))
        added = len(re.findall(rf"(?<![{ID_CHAR}]){re.escape(new)}(?![{ID_CHAR}])", output)) - len(
            re.findall(rf"(?<![{ID_CHAR}]){re.escape(new)}(?![{ID_CHAR}])", text)
        )
        report[old] = {"source_occurrences": before[old], "remaining": remaining, "target_added": added}
        if before[old] == 0:
            raise ValueError(f"source Database ID not found: {old}")
        if remaining:
            raise ValueError(f"source Database ID remains after remap: {old}")
        if added != before[old]:
            raise ValueError(f"replacement count mismatch for {old}: expected {before[old]}, got {added}")
    return output, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", required=True, help="Source HTML")
    parser.add_argument("--mapping", required=True, help="JSON object or @mapping.json")
    parser.add_argument("--out", help="Output HTML; default replaces source")
    args = parser.parse_args(argv)
    try:
        source = Path(args.html)
        text = source.read_text(encoding="utf-8")
        mapping = _load_mapping(args.mapping)
        output, report = remap(text, mapping)
        target = Path(args.out) if args.out else source
        target.write_text(output, encoding="utf-8")
        print(json.dumps({"ok": True, "output": str(target), "mapping": mapping, "counts": report}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        sys.stderr.write(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
