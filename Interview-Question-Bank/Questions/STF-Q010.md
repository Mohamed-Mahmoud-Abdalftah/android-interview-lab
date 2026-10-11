---
id: STF-Q010
lesson_id: EXT-STAFF-01
topic: Operational design
difficulty: senior
style: architecture
expected_minutes: 6
status: reviewed
---
# STF-Q010 — Operational design

## Interview question

> **Interviewer:** Review a design document that covers components but omits dashboards, alerts, runbooks, ownership, migration, and rollback. What must be added before approval?

<p dir="rtl" lang="ar"><strong>السياق:</strong> فريق يعيد كتابة التطبيق كله من غير migration path أو success metrics، أو platform team تبني abstraction بلا users</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/STF-Q010.md) · [Lesson](../../08-Mobile-System-Design/ext-staff-01.md)
