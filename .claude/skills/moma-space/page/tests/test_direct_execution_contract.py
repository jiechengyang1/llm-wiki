from __future__ import annotations

import re
import unittest
from pathlib import Path


PAGE_DIR = Path(__file__).resolve().parents[1]
SPACE_SKILL = PAGE_DIR.parent / "SKILL.md"
SHARED_SKILL = PAGE_DIR.parents[1] / "moma-shared" / "SKILL.md"
LIST_USER_SPACES_REFERENCE = (
    PAGE_DIR.parent / "references" / "moma-space-list_user_spaces.md"
)

SPACE_LIST_API = "GET_api_v1_tools_storage_space_list-user-spaces"
SPACE_LIST_COMMAND = """moma moma-space api GET_api_v1_tools_storage_space_list-user-spaces \\
  --query 'pageQuery={"page_no":1,"page_size":100}' --json"""
NEW_PAGE_FLOW_DOCS = (
    "entry.md",
    "page-manage.md",
    "static-page-flow.md",
    "data-page-flow.md",
    "import-clone-flow.md",
    "source-to-page-flow.md",
    "artifact-contract.md",
)

WRITE_APIS = {
    "POST_api_v1_tools_storage_file_create-folder",
    "POST_api_v1_tools_storage_file_upload-node",
    "POST_api_v1_tools_storage_file_publish-page",
    "POST_api_v1_tools_write_file",
    "POST_api_v1_tools_storage_table_create-database",
    "POST_api_v1_tools_storage_table_delete-database",
    "POST_api_v1_tools_storage_table_add-field",
    "POST_api_v1_tools_storage_table_update-field",
    "POST_api_v1_tools_storage_table_delete-field",
    "POST_api_v1_tools_storage_table_batch-add-records",
    "POST_api_v1_tools_storage_table_batch-update-records",
    "POST_api_v1_tools_storage_table_batch-delete-records",
    "POST_api_v1_tools_storage_file_attachment-upload",
    "POST_api_v1_tools_storage_file_upload-image",
}


def page_markdown_files() -> list[Path]:
    return sorted(PAGE_DIR.rglob("*.md"))


class DirectExecutionContractTests(unittest.TestCase):
    def test_page_docs_do_not_restore_approval_flow(self) -> None:
        forbidden = ("审批", "确认", "--dry-run", "--no")
        for path in page_markdown_files():
            text = path.read_text(encoding="utf-8")
            for marker in forbidden:
                with self.subTest(path=path.relative_to(PAGE_DIR), marker=marker):
                    self.assertNotIn(marker, text)

    def test_entry_defines_direct_execution(self) -> None:
        text = (PAGE_DIR / "entry.md").read_text(encoding="utf-8")
        self.assertIn("## 1. 直接执行规则", text)
        self.assertIn("写调用第一次执行就追加 `--yes`", text)
        self.assertIn("也不等待额外交互", text)
        self.assertIn("保持相同 API 名和全部业务参数", text)

    def test_database_contract_uses_returned_database_name(self) -> None:
        docs = [*page_markdown_files(), SPACE_SKILL]
        for path in docs:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertNotRegex(text, r"database-<[^>]+>\.csv")
        database_text = (PAGE_DIR / "database" / "page-database.md").read_text(encoding="utf-8")
        self.assertIn("database_id, database_name, space_id", database_text)
        self.assertIn("`database_name` 是创建后的真实 Database 名", database_text)

    def test_parent_skills_preserve_page_exception(self) -> None:
        space_text = SPACE_SKILL.read_text(encoding="utf-8")
        shared_text = SHARED_SKILL.read_text(encoding="utf-8")
        self.assertIn("version: 1.1.5", space_text)
        self.assertIn("页面生命周期窄范围例外", space_text)
        self.assertIn("页面生命周期窄范围例外", shared_text)
        self.assertIn("第一次就携带 `--yes`", shared_text)

    def test_new_page_flows_use_dedicated_space_list_api(self) -> None:
        for relative_path in NEW_PAGE_FLOW_DOCS:
            path = PAGE_DIR / relative_path
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=relative_path):
                self.assertIn(SPACE_LIST_API, text)
                self.assertIn("真实 ID", text)

        exact_command_docs = (
            PAGE_DIR / "entry.md",
            PAGE_DIR / "page-manage.md",
            PAGE_DIR / "static-page-flow.md",
            PAGE_DIR / "artifact-contract.md",
            LIST_USER_SPACES_REFERENCE,
        )
        for path in exact_command_docs:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIn(SPACE_LIST_COMMAND, text)

    def test_unspecified_space_uses_first_team_space_without_fallback(self) -> None:
        docs = [
            *(PAGE_DIR / path for path in NEW_PAGE_FLOW_DOCS),
            LIST_USER_SPACES_REFERENCE,
            SPACE_SKILL,
        ]
        for path in docs:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIn('mode == "team"', text)

        for path in page_markdown_files():
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(PAGE_DIR)):
                self.assertNotIn("moma moma-space api GET_api_v1_tools_spaces", text)

        reference_text = LIST_USER_SPACES_REFERENCE.read_text(encoding="utf-8")
        self.assertIn("选择第一项，不询问", reference_text)
        self.assertIn("不回退个人空间", reference_text)

    def test_page_upload_requires_selected_space_and_project_folder(self) -> None:
        manage_text = (PAGE_DIR / "page-manage.md").read_text(encoding="utf-8")
        artifact_text = (PAGE_DIR / "artifact-contract.md").read_text(encoding="utf-8")
        for text in (manage_text, artifact_text):
            with self.subTest(document="page upload contract"):
                self.assertIn("`space_id`", text)
                self.assertIn("真实 ID", text)
                self.assertIn("`parent_id`", text)
                self.assertRegex(text, r"space_id[^\n]*必填")
                self.assertRegex(text, r"parent_id[^\n]*必填")

    def test_documented_write_commands_include_yes(self) -> None:
        for path in page_markdown_files():
            text = path.read_text(encoding="utf-8")
            bash_blocks = re.findall(r"```bash\n(.*?)\n```", text, flags=re.DOTALL)
            for block in bash_blocks:
                commands = re.findall(
                    r"(?ms)^moma moma-space api (\S+)(.*?)(?=^moma moma-space api |\Z)",
                    block,
                )
                for api_name, arguments in commands:
                    if api_name not in WRITE_APIS:
                        continue
                    with self.subTest(path=path.relative_to(PAGE_DIR), api=api_name):
                        self.assertIn("--yes", arguments)


if __name__ == "__main__":
    unittest.main()
