---
id: INT-Q010
lesson_id: INT-001
topic: Toolchain honesty
difficulty: senior
style: system-design
expected_minutes: 6
status: reviewed
---
# INT-Q010 — Toolchain honesty

## Interview question

> **Interviewer:** In an interview, you implemented a JVM model but did not run Android device tests. How do you explain the evidence precisely and propose the missing verification without underselling the work?

<p dir="rtl" lang="ar"><strong>السياق:</strong> save تظهر success قبل durable transaction، worker تشتغل بحساب قديم، أو tests تستخدم fake تخفي migration/cancellation.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/INT-Q010.md) · [Lesson](../../09-Leadership-English/int-001-capstone-integration-and-tests.md)
