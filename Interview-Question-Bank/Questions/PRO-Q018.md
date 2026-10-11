---
id: PRO-Q018
lesson_id: PRO-004
topic: R8 keep rules
difficulty: senior
style: debugging
expected_minutes: 5
status: reviewed
---
# PRO-Q018 — R8 keep rules

## Interview question

> **Interviewer:** A serializer works in debug and fails in minified release. Explain how you would prove whether shrinking or obfuscation is responsible and write the narrowest kind of keep rule you would accept.

<p dir="rtl" lang="ar"><strong>السياق:</strong> release crash بسبب class اتشالت بالshrink، والفريق يضيف keep all فيلغي قيمة R8، أو secret متخزنة في BuildConfig.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q018.md) · [Lesson](../../06-Production-Engineering/pro-004-gradle-agp-9-d8-r8-and-signing.md)
