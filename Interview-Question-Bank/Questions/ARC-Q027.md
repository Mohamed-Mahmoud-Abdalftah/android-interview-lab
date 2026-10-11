---
id: ARC-Q027
lesson_id: ARC-006
topic: Review severity
difficulty: intermediate
style: code-review
expected_minutes: 4
status: reviewed
---
# ARC-Q027 — Review severity

## Interview question

> **Interviewer:** A pull request contains a naming issue, an unbounded retry, and a possible duplicate payment. Classify the comments by severity and explain what blocks the merge.

<p dir="rtl" lang="ar"><strong>السياق:</strong> Reviewer يطلب pattern أكبر من غير failure حقيقي، أو يوافق على repository بتكتب network result فوق local edits من غير conflict policy.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ARC-Q027.md) · [Lesson](../../04-Architecture-DI/arc-006-revision-architecture-code-review-and-dsa.md)
