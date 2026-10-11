---
id: ARC-Q028
lesson_id: ARC-006
topic: Repository conflict review
difficulty: senior
style: debugging
expected_minutes: 5
status: reviewed
---
# ARC-Q028 — Repository conflict review

## Interview question

> **Interviewer:** A repository exposes Room as the source of truth but also writes network responses straight into ViewModel state. Identify the two authorities and show how a stale response can overwrite newer local data.

<p dir="rtl" lang="ar"><strong>السياق:</strong> Reviewer يطلب pattern أكبر من غير failure حقيقي، أو يوافق على repository بتكتب network result فوق local edits من غير conflict policy.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ARC-Q028.md) · [Lesson](../../04-Architecture-DI/arc-006-revision-architecture-code-review-and-dsa.md)
