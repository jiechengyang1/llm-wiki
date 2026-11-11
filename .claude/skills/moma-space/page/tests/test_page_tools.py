from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PAGE_DIR))

from analyze_page import analyze
from lint_database_sdk_usage import lint as lint_sdk
from lint_page_resources import MAX_HTML_BYTES, lint as lint_resources
from remap_database_ids import remap


class AnalyzePageTests(unittest.TestCase):
    def test_canonical_json_schema_is_valid_json(self) -> None:
        payload = json.loads((PAGE_DIR / "page-analysis.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("output_mode", payload["properties"])

    def test_canonical_json_schema_is_valid_json(self) -> None:
        payload = json.loads((PAGE_DIR / "page-analysis.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("output_mode", payload["properties"])

    def test_static_report_needs_no_database(self) -> None:
        result = analyze("<html><head><title>季度报告</title></head><body><article>结论</article></body></html>", "生成一次性汇报页面", ["intent"])
        self.assertEqual(result["output_mode"], "static")
        self.assertEqual(result["needs_database"]["level"], "none")

    def test_table_without_maintenance_stays_static(self) -> None:
        html = "<table><tr><th>姓名</th><th>成绩</th></tr><tr><td>甲</td><td>90</td></tr></table>"
        result = analyze(html, "展示这份表格", ["table.html"])
        self.assertEqual(result["output_mode"], "static")
        self.assertEqual(result["needs_database"]["level"], "weak")

    def test_persistent_form_is_readwrite(self) -> None:
        html = '<form><input name="姓名"><button type="submit">保存</button></form>'
        result = analyze(html, "提交表单并保存记录", ["form.html", "intent"])
        self.assertEqual(result["output_mode"], "database-readwrite")
        self.assertEqual(result["needs_database"]["level"], "strong")
        self.assertEqual(result["databases"][0]["bindings"]["姓名"]["write_support"], "confirmed")

    def test_current_sdk_extracts_multiple_database_ids(self) -> None:
        html = """<script>
        const db = window.__SPACE_PAGE__.database;
        const PRIMARY_DATABASE_ID = "db_one";
        db.query({ database_id: PRIMARY_DATABASE_ID }).then(page => page.results.map(record => record.fields));
        db.getSchema({ database_id: "db_two" });
        </script>"""
        result = analyze(html, "", ["dynamic.html"])
        self.assertTrue(result["sdk"]["uses_current_sdk"])
        self.assertEqual(result["sdk"]["database_ids"], ["db_one", "db_two"])
        self.assertEqual(result["output_mode"], "database-readonly")


class SdkLintTests(unittest.TestCase):
    def test_legacy_and_camel_case_are_errors(self) -> None:
        findings = lint_sdk("__SMART_PAGE__.database.query({ databaseId: 'old' })")
        codes = {item["code"] for item in findings if item["severity"] == "error"}
        self.assertIn("legacy-global", codes)
        self.assertIn("legacy-key", codes)

    def test_current_crud_and_events_pass_without_errors(self) -> None:
        html = """<script>
        const db = window.__SPACE_PAGE__.database;
        async function run(file) {
          const page = await db.query({ database_id: "db_one", page_size: 100 });
          page.results.forEach(record => console.log(record.record_id, record.fields["姓名"]));
          if (page.has_more) console.log(page.next_cursor);
          const created = await db.addRecord({ database_id: "db_one", record: { "姓名": { text: "甲" } } });
          await db.updateRecord({ database_id: "db_one", record_id: created.id, properties: { "姓名": { text: "乙" } } });
          await db.deleteRecord({ database_id: "db_one", record_id: created.id });
          await db.uploadImage({ file });
          const off = db.onUpdated(event => console.log(event.database_id, event.record_id));
          off();
        }
        </script>"""
        errors = [item for item in lint_sdk(html) if item["severity"] == "error"]
        self.assertEqual(errors, [])

    def test_schema_rejects_unknown_field(self) -> None:
        html = """<script>
        const db = window.__SPACE_PAGE__.database;
        db.getRecord({ database_id: "db_one", record_id: "r1" }).then(record => record.fields["不存在"]);
        </script>"""
        findings = lint_sdk(html, {"姓名"})
        self.assertTrue(any(item["code"] == "unknown-field" for item in findings))


class RemapTests(unittest.TestCase):
    def test_multiple_ids_replace_once_with_boundaries(self) -> None:
        text = 'database_id: "db_one"; const x="db_two"; const untouched="x_db_one_y";'
        output, report = remap(text, {"db_one": "new_one", "db_two": "new_two"})
        self.assertIn('"new_one"', output)
        self.assertIn('"new_two"', output)
        self.assertIn('"x_db_one_y"', output)
        self.assertEqual(report["db_one"]["remaining"], 0)
        self.assertEqual(report["db_two"]["target_added"], 1)


class ResourceLintTests(unittest.TestCase):
    def test_inline_and_uploaded_resources_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "page.html"
            text = '<html><head><style>body{color:#111}</style></head><body><a href="#section">跳转</a><img src="https://assets.example.com/image.png"></body></html>'
            path.write_text(text, encoding="utf-8")
            errors = [item for item in lint_resources(path, text) if item["severity"] == "error"]
            self.assertEqual(errors, [])

    def test_missing_relative_and_local_absolute_are_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "page.html"
            text = '<img src="missing.png"><script src="file:///tmp/app.js"></script>'
            path.write_text(text, encoding="utf-8")
            codes = {item["code"] for item in lint_resources(path, text) if item["severity"] == "error"}
            self.assertIn("missing-relative", codes)
            self.assertIn("file-url", codes)

    def test_floating_remote_version_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "page.html"
            text = '<script src="https://cdn.example.com/pkg@latest/app.js"></script>'
            path.write_text(text, encoding="utf-8")
            self.assertTrue(any(item["code"] == "floating-version" for item in lint_resources(path, text)))

    def test_two_mib_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "page.html"
            text = "x" * (MAX_HTML_BYTES + 1)
            path.write_text(text, encoding="utf-8")
            self.assertTrue(any(item["code"] == "html-size" for item in lint_resources(path, text)))


if __name__ == "__main__":
    unittest.main()
