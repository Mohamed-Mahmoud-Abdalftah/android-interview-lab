---
id: PRO-Q020
lesson_id: PRO-004
topic: Signing boundary
difficulty: senior
style: system-design
expected_minutes: 6
status: reviewed
---
# PRO-Q020 — Signing boundary

## Interview question

> **Interviewer:** Walk through Android app signing from CI to Play delivery. Which keys exist, where should each live, and what breaks if the upload key or app signing key is compromised?

<p dir="rtl" lang="ar"><strong>السياق:</strong> release crash بسبب class اتشالت بالshrink، والفريق يضيف keep all فيلغي قيمة R8، أو secret متخزنة في BuildConfig.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q020.md) · [Lesson](../../06-Production-Engineering/pro-004-gradle-agp-9-d8-r8-and-signing.md)
