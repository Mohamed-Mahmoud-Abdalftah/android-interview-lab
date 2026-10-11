"""Regression tests for catalog, authored content, and navigation checks."""

import json
import tempfile
import unittest
from pathlib import Path

from validate import validate


LESSON = """---
id: L-1
title: A complete lesson
module: 01-Core
tier: Core
estimated_minutes: 30
prerequisite_ids: []
learning_outcomes:
  - Explain a boundary
status: reviewed
code_verification: tested
last_source_checked: 2026-10-10
source_urls:
  - https://example.org/lesson
example_paths:
  - code/main.kt
  - code/test.kt
question_ids: [Q-1]
---
# Lesson

## Mental model
A concrete mental model explains the boundary and how a learner uses it.

## Mechanism and trace
The input is transformed step by step and the result is checked.

## Wrong and corrected implementation
The wrong call fails; the corrected call checks the input first.

## Tests and failure cases
The test source exercises the invalid and valid inputs.

## Interview explanation
I describe the decision and the tradeoff in ordinary terms.

## Senior follow-ups
An experienced engineer asks about a second failure mode and recovery.

## Misconceptions and revision
The learner must not assume an unchecked value is safe.
"""

QUESTION = """---
id: Q-1
lesson_id: L-1
topic: Boundary safety
difficulty: foundational
style: product-android
expected_minutes: 2
status: reviewed
---
# Q-1 — Boundary safety

Explain how you handle an unchecked value at a boundary and what failure you test.

[Complete answer](answer.md)
"""

ANSWER = """---
id: Q-1-ANSWER
question_id: Q-1
status: reviewed
---
# Q-1 — Model answer

**Spoken answer:** I check the input at the boundary and return a documented result.

**Mechanics:** The invalid input is rejected before any state is mutated.

**Follow-up 1:** What if the input is missing? **Answer:** Return a typed error and keep the existing state intact.

**Follow-up 2:** How would you test recovery? **Answer:** Exercise the invalid branch and then verify a valid request still succeeds.
"""


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.manifest = {"items": [
            {"id": "L-1", "type": "lesson", "title": "A complete lesson", "path": "lesson.md",
             "day": 1, "prerequisites": [], "sequence_previous": None, "status": "reviewed",
             "source_status": "verified", "code_verification": "tested",
             "verification_evidence": "BUILD-VERIFICATION.md", "question_ids": ["Q-1"],
             "example_paths": ["code/main.kt", "code/test.kt"],
             "source_urls": ["https://example.org/lesson"]},
            {"id": "Q-1", "type": "question", "path": "question.md",
             "answer_path": "answer.md", "prerequisites": ["L-1"], "status": "reviewed",
             "source_status": "verified", "code_verification": "not_applicable",
             "verification_evidence": None, "question_ids": [], "example_paths": [], "source_urls": []},
        ]}
        self.write("lesson.md", LESSON)
        self.write("question.md", QUESTION)
        self.write("answer.md", ANSWER)
        self.write("code/main.kt", "fun safe(value: String?): String = value ?: \"missing\"\n")
        self.write("code/test.kt", "class BoundaryTest { fun missingInputIsSafe() {} }\n")
        self.write(".gitignore", "build/\n")
        self.write("BUILD-VERIFICATION.md", "./gradlew clean test check run --no-daemon\n2 tests completed, 0 failed, 0 skipped\nBUILD SUCCESSFUL\n")
        self.write("COVERAGE-MATRIX.md", "# Coverage\n\n| Topic ID | Parent domain | Level | Prerequisite | Minutes | Path | Questions | Example / tests | Sources | Status | Rationale |\n|---|---|---|---|---:|---|---|---|---|---|---|\n| L-1 | 01-Core | Core | none | 120 | [L-1](lesson.md) | Q-1 | [test](code/test.kt) | [source](https://example.org/lesson) | reviewed | Covers the boundary |\n")
        self.write("Interview-Question-Bank/BY-TOPIC.md", "| Topic | Question | Complete answer |\n|---|---|---|\n| Boundary safety | [Q-1](../question.md) | [Model answer](../answer.md) |\n")
        self.write("Interview-Question-Bank/BY-DIFFICULTY.md", "- Foundational: [Q-1](../question.md) — [answer](../answer.md)\n")
        self.write("Interview-Question-Bank/BY-INTERVIEW-STYLE.md", "- Product Android: [Q-1](../question.md) — [answer](../answer.md)\n")
        self.save_manifest()
        self.refresh_inventory()

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def save_manifest(self):
        self.write("CONTENT-MANIFEST.json", json.dumps(self.manifest))

    def refresh_inventory(self):
        paths = sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*") if p.is_file())
        self.write("FILE-INVENTORY.md", "# Actual file inventory\n\n```text\n" + "\n".join(paths + ["FILE-INVENTORY.md"]) + "\n```\n")

    def assert_problem(self, phrase):
        problems = validate(self.root)
        self.assertTrue(any(phrase in problem for problem in problems), problems)

    def test_consistent_small_catalog_passes(self):
        self.assertEqual([], validate(self.root))

    def test_manifest_id_must_match_authored_front_matter(self):
        self.write("lesson.md", LESSON.replace("id: L-1", "id: L-99", 1))
        self.assert_problem("front matter ID")

    def test_duplicate_front_matter_keys_are_invalid(self):
        self.write("question.md", QUESTION.replace("status: reviewed", "status: reviewed\nstatus: draft"))
        self.assert_problem("duplicate front matter key")

    def test_front_matter_values_must_match_manifest(self):
        self.write("lesson.md", LESSON.replace("status: reviewed", "status: draft"))
        self.assert_problem("front matter status")

    def test_all_authored_ids_must_be_registered_or_owned_answers(self):
        self.write("orphan.md", "---\nid: EXTRA-1\nstatus: reviewed\n---\n# Orphan\n")
        self.assert_problem("unregistered front matter ID")

    def test_conceptual_prerequisite_rejects_non_topic_id(self):
        self.manifest["items"][0]["prerequisites"] = ["Q-1"]
        self.save_manifest()
        self.assert_problem("invalid prerequisite type")

    def test_conceptual_prerequisite_cycle_is_rejected(self):
        self.manifest["items"].append(dict(self.manifest["items"][0], id="L-2", path="second.md", day=2,
                                           prerequisites=["L-1"], sequence_previous="L-1", question_ids=[],
                                           status="planned", source_status="pending_verification",
                                           code_verification="not_run", verification_evidence=None,
                                           example_paths=[], source_urls=[]))
        self.manifest["items"][0]["prerequisites"] = ["L-2"]
        self.save_manifest()
        self.assert_problem("prerequisite cycle")

    def test_sequence_previous_is_checked_separately_from_prerequisites(self):
        self.manifest["items"].append(dict(self.manifest["items"][0], id="L-2", path="second.md",
                                           day=2, prerequisites=[], sequence_previous="Q-1",
                                           question_ids=[], status="planned", source_status="pending_verification",
                                           code_verification="not_run", verification_evidence=None,
                                           example_paths=[], source_urls=[]))
        self.save_manifest()
        self.assert_problem("sequence_previous")

    def test_question_must_belong_to_existing_lesson(self):
        self.write("question.md", QUESTION.replace("lesson_id: L-1", "lesson_id: L-99"))
        self.assert_problem("lesson_id")

    def test_extended_topic_can_own_complete_learning_material(self):
        topic = self.manifest["items"][0]
        topic["type"] = "extended_topic"
        topic.pop("day")
        topic.pop("sequence_previous")
        self.save_manifest()
        (self.root / "FILE-INVENTORY.md").unlink()
        self.refresh_inventory()
        self.assertEqual([], validate(self.root))

    def test_lesson_cannot_list_an_unregistered_question(self):
        self.manifest["items"][0]["question_ids"].append("Q-99")
        self.save_manifest()
        self.assert_problem("unknown question_id")

    def test_answer_followups_need_substantive_answers(self):
        self.write("answer.md", ANSWER.replace("Return a typed error and keep the existing state intact.", "Yes."))
        self.assert_problem("incomplete follow-up")

    def test_question_mark_inside_code_does_not_truncate_followup_question(self):
        self.write("answer.md", ANSWER.replace("What if the input is missing?", "Can `String?` be missing?"))
        self.assertEqual([], validate(self.root))

    def test_tested_lesson_must_reference_test_source(self):
        self.manifest["items"][0]["example_paths"] = ["code/main.kt"]
        self.save_manifest()
        self.write("lesson.md", LESSON.replace("  - code/test.kt\n", ""))
        self.assert_problem("test source")

    def test_reviewed_unrun_example_still_has_to_exist(self):
        self.manifest["items"][0]["code_verification"] = "not_run"
        self.manifest["items"][0]["example_paths"] = ["code/missing.kt"]
        self.save_manifest()
        self.write("lesson.md", LESSON.replace("code_verification: tested", "code_verification: not_run")
                   .replace("  - code/main.kt\n  - code/test.kt", "  - code/missing.kt"))
        self.assert_problem("missing example")

    def test_reviewed_lesson_needs_required_sections(self):
        self.write("lesson.md", LESSON.replace("## Tests and failure cases", "## Random notes"))
        self.assert_problem("missing lesson section")

    def test_duplicate_question_in_registry_is_rejected(self):
        registry = self.root / "Interview-Question-Bank/BY-DIFFICULTY.md"
        self.write(str(registry.relative_to(self.root)), registry.read_text() + "- Foundational: [Q-1](../question.md)\n")
        self.assert_problem("duplicate registry entry")

    def test_broken_local_anchor_is_rejected(self):
        self.write("lesson.md", LESSON + "\n[missing heading](#never-written)\n")
        self.assert_problem("broken anchor")

    def test_broken_local_html_href_is_rejected(self):
        self.write("lesson.md", LESSON + '\n<p dir="rtl" lang="ar">افتح <a dir="ltr" href="missing.md">missing</a>.</p>\n')
        self.assert_problem("broken link")

    def test_html_heading_id_is_a_valid_local_anchor(self):
        self.write("lesson.md", LESSON + '\n<h2 dir="rtl" lang="ar" id="arabic-heading">عنوان عربي واضح</h2>\n\n[go](#arabic-heading)\n')
        self.assertEqual([], validate(self.root))

    def test_arabic_html_paragraph_needs_direction_and_language(self):
        self.write("lesson.md", LESSON + "\n<p>دي فقرة عربية كاملة ومقصود تظهر من اليمين للشمال.</p>\n")
        self.assert_problem("Arabic paragraph needs dir=rtl and lang=ar")

    def test_code_inside_arabic_block_needs_ltr_direction(self):
        self.write("lesson.md", LESSON + '\n<p dir="rtl" lang="ar">قيمة <code>String?</code> ممكن تغيب.</p>\n')
        self.assert_problem("inline code needs dir=ltr")

    def test_markdown_notation_inside_raw_html_is_rejected(self):
        self.write("lesson.md", LESSON + '\n<p dir="rtl" lang="ar">ده **مهم** في الشرح.</p>\n')
        self.assert_problem("Markdown syntax inside raw HTML")

    def test_duplicate_html_ids_are_rejected(self):
        self.write("lesson.md", LESSON + '\n<h2 dir="rtl" lang="ar" id="same">عنوان أول</h2>\n<h2 dir="rtl" lang="ar" id="same">عنوان تاني</h2>\n')
        self.assert_problem("duplicate HTML ID")

    def test_invisible_bidi_controls_are_rejected(self):
        self.write("lesson.md", LESSON + "\n\u202ehidden control\n")
        self.assert_problem("invisible bidi control")

    def test_coverage_status_must_match_manifest(self):
        path = self.root / "COVERAGE-MATRIX.md"
        self.write("COVERAGE-MATRIX.md", path.read_text().replace("| reviewed | Covers", "| planned | Covers"))
        self.assert_problem("coverage status")

    def test_inventory_must_list_each_existing_source_file(self):
        self.write("extra.md", "# Real extra document\n")
        self.assert_problem("inventory missing file")

    def test_generated_distribution_zip_is_not_source_inventory(self):
        path = self.root / "dist" / "source.zip"
        path.parent.mkdir()
        path.write_bytes(b"generated archive")
        self.assertEqual([], validate(self.root))

    def test_generated_site_mock_copy_is_not_source_inventory(self):
        self.write("site/src/content/docs/mocks/mock-001.md", "derived website copy\n")
        self.assertEqual([], validate(self.root))

    def test_tested_status_requires_recorded_success_and_test_count(self):
        self.write("BUILD-VERIFICATION.md", "A build was attempted, but no test result was recorded.\n")
        self.assert_problem("verification evidence")

    def test_gradle_xml_test_counts_are_valid_evidence(self):
        self.write("BUILD-VERIFICATION.md", "./gradlew clean test check run --no-daemon\nBUILD SUCCESSFUL\nJUnit XML: tests=8, skipped=0, failures=0, errors=0\n")
        self.assertEqual([], validate(self.root))

    def test_zero_executed_tests_do_not_support_tested_status(self):
        self.write("BUILD-VERIFICATION.md", "./gradlew clean test check run --no-daemon\nBUILD SUCCESSFUL\nJUnit XML: tests=0, skipped=0, failures=0, errors=0\n")
        self.assert_problem("verification evidence")

    def test_all_skipped_tests_do_not_support_tested_status(self):
        self.write("BUILD-VERIFICATION.md", "./gradlew clean test check run --no-daemon\nBUILD SUCCESSFUL\nJUnit XML: tests=8, skipped=8, failures=0, errors=0\n")
        self.assert_problem("verification evidence")

    def test_historical_success_cannot_mask_current_failed_run(self):
        self.write("BUILD-VERIFICATION.md", "## Current run\n./gradlew clean test check run --no-daemon\nBUILD FAILED\nJUnit XML: tests=8, skipped=0, failures=1\n\n## Historical run\n./gradlew clean test check run --no-daemon\nBUILD SUCCESSFUL\nJUnit XML: tests=8, skipped=0, failures=0\n")
        self.assert_problem("verification evidence")

    def test_planned_sources_cannot_be_marked_verified(self):
        self.manifest["items"][0]["status"] = "planned"
        self.manifest["items"][0]["source_status"] = "verified"
        self.save_manifest()
        self.assert_problem("source_status")


if __name__ == "__main__":
    unittest.main()
