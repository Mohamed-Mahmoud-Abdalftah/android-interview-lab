---
id: DSA-Q006
lesson_id: EXT-DSA-01
topic: Interval merge invariant
difficulty: foundational
style: conceptual
expected_minutes: 6
status: reviewed
---
# DSA-Q006 — Interval merge invariant

## Interview question

> **Interviewer:** Merge `[[1,3],[2,6],[8,10],[10,12]]` using an explicitly stated closed-interval policy.

<p dir="rtl" lang="ar"><strong>السياق:</strong> حل سريع يفشل duplicates أو overflow، والمرشح يعلن O(n) من غير حساب memory/hash assumptions</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/DSA-Q006.md) · [Lesson](../../07-DSA-Live-Coding/ext-dsa-01.md)
