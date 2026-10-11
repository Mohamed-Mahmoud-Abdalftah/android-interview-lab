---
id: PRO-Q017
lesson_id: PRO-004
topic: Compatibility matrix
difficulty: intermediate
style: code-review
expected_minutes: 4
status: reviewed
---
# PRO-Q017 — Compatibility matrix

## Interview question

> **Interviewer:** The app builds after upgrading AGP but fails only on API 23 release devices. Build a compatibility investigation across JDK, Gradle, AGP, Kotlin, desugaring, minSdk, and device runtime.

<p dir="rtl" lang="ar"><strong>السياق:</strong> release crash بسبب class اتشالت بالshrink، والفريق يضيف keep all فيلغي قيمة R8، أو secret متخزنة في BuildConfig.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q017.md) · [Lesson](../../06-Production-Engineering/pro-004-gradle-agp-9-d8-r8-and-signing.md)
