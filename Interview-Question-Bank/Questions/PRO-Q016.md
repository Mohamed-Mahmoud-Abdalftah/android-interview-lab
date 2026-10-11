---
id: PRO-Q016
lesson_id: PRO-004
topic: Build pipeline
difficulty: foundational
style: conceptual
expected_minutes: 4
status: reviewed
---
# PRO-Q016 — Build pipeline

## Interview question

> **Interviewer:** Trace one Kotlin function from source through Kotlin compilation, desugaring, D8 or R8, DEX packaging, signing, installation, and ART execution. Where can debug and release behavior diverge?

<p dir="rtl" lang="ar"><strong>السياق:</strong> release crash بسبب class اتشالت بالshrink، والفريق يضيف keep all فيلغي قيمة R8، أو secret متخزنة في BuildConfig.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q016.md) · [Lesson](../../06-Production-Engineering/pro-004-gradle-agp-9-d8-r8-and-signing.md)
