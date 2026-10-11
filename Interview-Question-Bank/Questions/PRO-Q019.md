---
id: PRO-Q019
lesson_id: PRO-004
topic: Variant isolation
difficulty: senior
style: architecture
expected_minutes: 5
status: reviewed
---
# PRO-Q019 — Variant isolation

## Interview question

> **Interviewer:** A release APK accidentally contains a staging endpoint and debug-only dependency. Show how you would isolate variants and add a CI check against the packaged artifact.

<p dir="rtl" lang="ar"><strong>السياق:</strong> release crash بسبب class اتشالت بالshrink، والفريق يضيف keep all فيلغي قيمة R8، أو secret متخزنة في BuildConfig.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q019.md) · [Lesson](../../06-Production-Engineering/pro-004-gradle-agp-9-d8-r8-and-signing.md)
