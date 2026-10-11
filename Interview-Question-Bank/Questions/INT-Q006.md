---
id: INT-Q006
lesson_id: INT-001
topic: Capstone boundaries
difficulty: foundational
style: conceptual
expected_minutes: 4
status: reviewed
---
# INT-Q006 — Capstone boundaries

## Interview question

> **Interviewer:** Describe one mobile feature end to end from UI intent through local state, durable work, backend acknowledgement, telemetry, and recovery. Be explicit about what each test layer proves.

<p dir="rtl" lang="ar"><strong>السياق:</strong> save تظهر success قبل durable transaction، worker تشتغل بحساب قديم، أو tests تستخدم fake تخفي migration/cancellation.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/INT-Q006.md) · [Lesson](../../09-Leadership-English/int-001-capstone-integration-and-tests.md)
