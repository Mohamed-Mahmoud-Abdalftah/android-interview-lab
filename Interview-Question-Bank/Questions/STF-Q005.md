---
id: STF-Q005
lesson_id: EXT-STAFF-01
topic: Blast-radius control
difficulty: senior
style: live-coding
expected_minutes: 6
status: reviewed
---
# STF-Q005 — Blast-radius control

## Interview question

> **Interviewer:** You must replace the networking stack used by every feature. Design flags, cohorts, shadow traffic, observability, and rollback to limit blast radius.

<p dir="rtl" lang="ar"><strong>السياق:</strong> فريق يعيد كتابة التطبيق كله من غير migration path أو success metrics، أو platform team تبني abstraction بلا users</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/STF-Q005.md) · [Lesson](../../08-Mobile-System-Design/ext-staff-01.md)
