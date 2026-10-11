---
id: ART-Q009
lesson_id: EXT-ART-01
topic: Crash retrace
difficulty: senior
style: live-coding
expected_minutes: 6
status: reviewed
---
# ART-Q009 — Crash retrace

## Interview question

> **Interviewer:** A production stack trace is obfuscated. Describe how mapping files, build IDs, native symbols, and exact artifact versions turn it into actionable evidence.

<p dir="rtl" lang="ar"><strong>السياق:</strong> مرشح يقول Android يشغل JVM bytecode مباشرة أو ينسب crash في R8 لـART من غير فحص artifact/mapping</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ART-Q009.md) · [Lesson](../../08-Mobile-System-Design/ext-art-01.md)
