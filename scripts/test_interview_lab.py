import unittest

from import_interview_lab import SOURCE, parse_source
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


if __name__ == "__main__":
    unittest.main()
