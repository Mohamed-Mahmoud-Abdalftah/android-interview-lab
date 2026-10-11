---
id: INT-Q007
lesson_id: INT-001
topic: Test portfolio
difficulty: intermediate
style: code-review
expected_minutes: 4
status: reviewed
---
# INT-Q007 — Test portfolio

## Interview question

> **Interviewer:** A team has 2,000 slow UI tests and few lower-level tests. Rebuild the portfolio around failure risk, feedback speed, framework boundaries, and production evidence.

<p dir="rtl" lang="ar"><strong>السياق:</strong> save تظهر success قبل durable transaction، worker تشتغل بحساب قديم، أو tests تستخدم fake تخفي migration/cancellation.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/INT-Q007.md) · [Lesson](../../09-Leadership-English/int-001-capstone-integration-and-tests.md)
