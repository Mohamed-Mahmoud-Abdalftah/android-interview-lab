---
id: STF-Q002
lesson_id: EXT-STAFF-01
topic: Architecture evolution
difficulty: intermediate
style: code-review
expected_minutes: 6
status: reviewed
---
# STF-Q002 — Architecture evolution

## Interview question

> **Interviewer:** A monolith is slowing delivery, but a rewrite would stop feature work for a year. Design an incremental seam, migration order, compatibility period, and rollback.

<p dir="rtl" lang="ar"><strong>السياق:</strong> فريق يعيد كتابة التطبيق كله من غير migration path أو success metrics، أو platform team تبني abstraction بلا users</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/STF-Q002.md) · [Lesson](../../08-Mobile-System-Design/ext-staff-01.md)
