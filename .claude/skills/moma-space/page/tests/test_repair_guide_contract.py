from __future__ import annotations

import unittest
from pathlib import Path


PAGE_DIR = Path(__file__).resolve().parents[1]
SPACE_SKILL = PAGE_DIR.parent / "SKILL.md"
REPAIR_GUIDE = PAGE_DIR / "repair-guide.md"


class RepairGuideContractTests(unittest.TestCase):
    def test_repair_guide_is_routed_and_indexed(self) -> None:
        self.assertTrue(REPAIR_GUIDE.is_file())
        for path in (
            PAGE_DIR / "entry.md",
            PAGE_DIR / "edit-flow.md",
            SPACE_SKILL,
        ):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIn("repair-guide.md", text)

        skill_text = SPACE_SKILL.read_text(encoding="utf-8")
        self.assertGreaterEqual(skill_text.count("page/repair-guide.md"), 3)

    def test_sdk_and_successful_data_are_authoritative(self) -> None:
        text = REPAIR_GUIDE.read_text(encoding="utf-8")
        self.assertIn("SDK、合同中定义的方法和 SDK 成功返回的数据均是权威结果", text)
        self.assertIn("可以无条件信任", text)
        prohibited_contracts = (
            "修复过程中不得因为怀疑 SDK 或返回数据而增加",
            "二次查询、重复拉取或额外的数据正确性核验",
            "mock 数据、fallback 数据、静态替代数据或静默默认值",
            "为修正所谓异常返回而编写的归一化、过滤或防御性分支",
        )
        for contract in prohibited_contracts:
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_repair_prioritizes_interaction_then_visual_style(self) -> None:
        text = REPAIR_GUIDE.read_text(encoding="utf-8")
        interaction = text.index("**核心交互可用：**")
        feedback = text.index("**交互体验清晰：**")
        visual = text.index("**视觉样式完善：**")
        minimal = text.index("**最小代码调整：**")
        self.assertLess(interaction, feedback)
        self.assertLess(feedback, visual)
        self.assertLess(visual, minimal)

    def test_repair_checklist_covers_interaction_and_responsive_states(self) -> None:
        text = REPAIR_GUIDE.read_text(encoding="utf-8")
        markers = (
            "键盘",
            "触控",
            ":focus-visible",
            "submitting/disabled",
            "弹层",
            "滚动",
            "桌面、平板、移动窄屏",
            "视觉样式",
        )
        for marker in markers:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_repair_preserves_existing_page_identity_and_data(self) -> None:
        text = REPAIR_GUIDE.read_text(encoding="utf-8")
        self.assertIn("保留原 node ID、Space ID、当前路径、父目录和 Database ID", text)
        self.assertIn("不开展无关的数据层重构", text)


if __name__ == "__main__":
    unittest.main()
