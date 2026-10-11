import re
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
QUESTIONS = ROOT / "Interview-Question-Bank" / "Questions"
ANSWERS = ROOT / "Interview-Question-Bank" / "Model-Answers"
ARABIC = re.compile(r"[\u0600-\u06ff]")
BANNED_BOILERPLATE = (
    "The owner receives input, changes state, crosses the relevant boundary",
    "Identify the exact layer, owner, input artifact or state, transition, and output",
    "How would this answer change when the owner is recreated or the operation is delivered twice?",
    "How would you prove the claim without a production experiment?",
    "Use the named pattern and add a retry",
    "The platform or pattern handles it automatically",
    "Define the accepted input, observable output, ownership, and terminal states",
    "Re-run the same trace with the production failure below",
    "The concrete risk in this case is a production path that violates the stated owner or invariant",
    "because it is the recommended pattern, then retry if it fails",
    "Expected rule:",
    "Owning boundary:",
    "First broken invariant:",
    "Full credit requires the exact rule",
    "I would reproduce the stated counterexample at the owning boundary",
)
BANNED_PROMPTS = (
    "A senior review exposes this failure:",
    "During a specialist interview, explain",
    "What is the exact contract and who owns it?",
    "State which part cannot be proved by a local unit test.",
    "## What you need to answer",
    "## English interview prompt",
    "A production issue points to",
    "Design the ownership and data flow for",
    "Would you approve it? Identify the correctness risk",
    "Do you agree? Explain **",
)


class InterviewQualityTests(unittest.TestCase):
    def test_bank_contains_300_complete_pairs(self):
        self.assertEqual(300, len(list(QUESTIONS.glob("*.md"))))
        self.assertEqual(300, len(list(ANSWERS.glob("*.md"))))

    def test_generic_answer_boilerplate_is_absent(self):
        offenders = []
        for path in ANSWERS.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            for phrase in BANNED_BOILERPLATE:
                if phrase in text:
                    offenders.append(f"{path.name}: {phrase}")
        self.assertEqual([], offenders)

    def test_generated_prompts_are_real_scenarios_not_meta_instructions(self):
        offenders = []
        for path in QUESTIONS.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            for phrase in BANNED_PROMPTS:
                if phrase in text:
                    offenders.append(f"{path.name}: {phrase}")
        self.assertEqual([], offenders)

    def test_english_model_sections_contain_no_arabic(self):
        offenders = []
        for path in ANSWERS.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            match = re.search(
                r"## (?:Polished English answer|English model answer)\s*(.*?)(?=\n## |\Z)",
                text,
                flags=re.DOTALL,
            )
            if match and ARABIC.search(match.group(1)):
                offenders.append(path.name)
        self.assertEqual([], offenders)

    def test_representative_answers_use_topic_specific_reasoning(self):
        checks = {
            "AND-Q016.md": ("main thread", "Perfetto", "WorkManager"),
            "COR-Q016.md": ("stateIn/shareIn", "collectorين", "sequential execution"),
            "ARC-Q016.md": ("component graph", "account/session", "Repository and UseCase"),
            "DSA-Q006.md": ("next.start &lt;= last.end", "point-set oracle", "WorkManager"),
            "POS-Q006.md": ("attempt identity", "reconcile", "new payment request immediately"),
        }
        failures = []
        for filename, (required_a, required_b, forbidden) in checks.items():
            text = (ANSWERS / filename).read_text(encoding="utf-8")
            if required_a not in text or required_b not in text or forbidden in text:
                failures.append(filename)
        self.assertEqual([], failures)

    def test_rebuilt_answers_have_real_mechanisms_without_long_copy_paste(self):
        rebuilt = [
            path for path in ANSWERS.glob("*.md")
            if "## الإجابة المختصرة" in path.read_text(encoding="utf-8")
        ]
        self.assertEqual(205, len(rebuilt))
        missing_mechanism = [
            path.name for path in rebuilt
            if "<strong>تحت الغطا في " not in path.read_text(encoding="utf-8")
        ]
        self.assertEqual([], missing_mechanism)

        paragraphs = Counter()
        for path in rebuilt:
            text = path.read_text(encoding="utf-8")
            for paragraph in re.split(r"\n\s*\n", text):
                normalized = " ".join(paragraph.split())
                if len(normalized) >= 220 and not normalized.startswith("```"):
                    paragraphs[normalized] += 1
        repeated = [paragraph for paragraph, count in paragraphs.items() if count >= 5]
        self.assertEqual([], repeated)

    def test_rebuilt_question_prompts_are_spoken_interview_questions(self):
        rebuilt = []
        offenders = []
        prompts = []
        for path in QUESTIONS.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            if "## Interview question" not in text:
                continue
            rebuilt.append(path)
            match = re.search(r"^> \*\*Interviewer:\*\* (.+)$", text, flags=re.MULTILINE)
            if not match or ARABIC.search(match.group(1)):
                offenders.append(path.name)
            elif match:
                prompts.append(match.group(1))
        self.assertEqual(160, len(rebuilt))
        self.assertEqual([], offenders)
        self.assertEqual(160, len(set(prompts)))


if __name__ == "__main__":
    unittest.main()
