---
id: ARC-Q030
lesson_id: ARC-006
topic: DSA invariant in review
difficulty: senior
style: system-design
expected_minutes: 6
status: reviewed
---
# ARC-Q030 — DSA invariant in review

## Interview question

> **Interviewer:** A teammate submits a one-pass two-sum implementation that inserts before looking up the complement. Use [3] with target 6 and [3,3] with target 6 to review the invariant and the bug.

<p dir="rtl" lang="ar"><strong>السياق:</strong> Reviewer يطلب pattern أكبر من غير failure حقيقي، أو يوافق على repository بتكتب network result فوق local edits من غير conflict policy.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ARC-Q030.md) · [Lesson](../../04-Architecture-DI/arc-006-revision-architecture-code-review-and-dsa.md)
