---
id: INT-Q009
lesson_id: INT-001
topic: Observability contract
difficulty: senior
style: architecture
expected_minutes: 5
status: reviewed
---
# INT-Q009 — Observability contract

## Interview question

> **Interviewer:** Define logs, metrics, traces, operation IDs, and redaction for a sync operation so an engineer can reconstruct failure without storing user content.

<p dir="rtl" lang="ar"><strong>السياق:</strong> save تظهر success قبل durable transaction، worker تشتغل بحساب قديم، أو tests تستخدم fake تخفي migration/cancellation.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/INT-Q009.md) · [Lesson](../../09-Leadership-English/int-001-capstone-integration-and-tests.md)
