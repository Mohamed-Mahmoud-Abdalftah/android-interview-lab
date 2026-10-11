---
id: DSA-Q007
lesson_id: EXT-DSA-01
topic: LRU cache design
difficulty: intermediate
style: code-review
expected_minutes: 6
status: reviewed
---
# DSA-Q007 — LRU cache design

## Interview question

> **Interviewer:** Design an LRU cache with expected O(1) `get` and `put`. Explain which two structures must stay consistent.

<p dir="rtl" lang="ar"><strong>السياق:</strong> حل سريع يفشل duplicates أو overflow، والمرشح يعلن O(n) من غير حساب memory/hash assumptions</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/DSA-Q007.md) · [Lesson](../../07-DSA-Live-Coding/ext-dsa-01.md)
