import unittest

from import_interview_lab import SOURCE, parse_source
import validate_interview_lab
from validate_interview_lab import validate


class InterviewLabSourceTests(unittest.TestCase):
    def test_exact_source_inventory(self):
        questions = parse_source(SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(len(questions), 485)
        self.assertEqual(len({q["id"] for q in questions}), 485)
        self.assertEqual(len({q["code"] for q in questions}), 21)
        self.assertEqual(questions[0]["id"], "KOT-01")
        self.assertEqual(questions[-1]["id"], "PAY-15")

    def test_records_preserve_source(self):
        report = validate()
        self.assertEqual(report["missing"], 0)
        self.assertEqual(report["errors"], [])

    def test_speaking_answer_rejects_copied_explanation_sentences(self):
        source = "A database transaction holds the write lock while network I/O waits for a server. This blocks a competing query from completing."
        answer = "First I locate the lock holder. A database transaction holds the write lock while network I/O waits for a server. I then shorten that transaction."
        self.assertEqual(
            validate_interview_lab.copied_long_sentences(source, answer),
            ["A database transaction holds the write lock while network I/O waits for a server."],
        )

    def test_speaking_answer_accepts_distinct_reasoning(self):
        source = "A database transaction holds the write lock while network I/O waits for a server."
        answer = "I would find which thread owns the transaction, move the remote call outside it, and persist a pending state for recovery."
        self.assertEqual(validate_interview_lab.copied_long_sentences(source, answer), [])

    def test_review_footer_rejects_trailing_question(self):
        section = "- [Source](https://example.com)\n\nTechnically reviewed on 2026-10-11.\nOriginal question?"
        self.assertEqual(validate_interview_lab.review_footer_extra(section), "Original question?")
        self.assertEqual(validate_interview_lab.review_footer_extra(section.split("\nOriginal")[0]), "")

    def test_coverage_report_tracks_each_question_and_topic(self):
        report = validate()
        self.assertEqual(len(report["questionStatus"]), 485)
        self.assertEqual(report["questionStatus"]["AND-01"]["topic"], "AND")
        self.assertIn(report["questionStatus"]["AND-01"]["status"], {"reviewed", "source-only"})
        self.assertEqual(sum(topic["total"] for topic in report["topicCoverage"].values()), 485)
        self.assertEqual(len(report["sourceOnlyIds"]), report["sourceOnly"])
        self.assertEqual(report["qualityPassing"], sum(
            item["automatedQuality"] == "passes-checks" for item in report["questionStatus"].values()))


if __name__ == "__main__":
    unittest.main()
