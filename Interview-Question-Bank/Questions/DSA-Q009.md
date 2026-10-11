---
id: DSA-Q009
lesson_id: EXT-DSA-01
topic: Cycle detection
difficulty: senior
style: architecture
expected_minutes: 6
status: reviewed
---
# DSA-Q009 — Cycle detection

## Interview question

> **Interviewer:** Given a directed graph, return whether it contains a cycle. Cover disconnected components and a self-loop.

<p dir="rtl" lang="ar"><strong>السياق:</strong> حل سريع يفشل duplicates أو overflow، والمرشح يعلن O(n) من غير حساب memory/hash assumptions</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/DSA-Q009.md) · [Lesson](../../07-DSA-Live-Coding/ext-dsa-01.md)
