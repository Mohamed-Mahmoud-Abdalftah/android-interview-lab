---
id: INT-Q008
lesson_id: INT-001
topic: Failure injection
difficulty: senior
style: debugging
expected_minutes: 5
status: reviewed
---
# INT-Q008 — Failure injection

## Interview question

> **Interviewer:** For an offline-first checkout flow, inject process death, timeout after commit, duplicate delivery, stale auth, and database failure. State the invariant each case tests.

<p dir="rtl" lang="ar"><strong>السياق:</strong> save تظهر success قبل durable transaction، worker تشتغل بحساب قديم، أو tests تستخدم fake تخفي migration/cancellation.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/INT-Q008.md) · [Lesson](../../09-Leadership-English/int-001-capstone-integration-and-tests.md)
