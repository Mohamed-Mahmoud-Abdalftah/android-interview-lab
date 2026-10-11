---
id: ART-Q008
lesson_id: EXT-ART-01
topic: Boxing and allocation
difficulty: senior
style: system-design
expected_minutes: 6
status: reviewed
---
# ART-Q008 — Boxing and allocation

## Interview question

> **Interviewer:** A hot Kotlin loop stores millions of Int values in generic collections. Explain where boxing appears, how you would measure its cost, and when specialized storage is justified.

<p dir="rtl" lang="ar"><strong>السياق:</strong> مرشح يقول Android يشغل JVM bytecode مباشرة أو ينسب crash في R8 لـART من غير فحص artifact/mapping</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ART-Q008.md) · [Lesson](../../08-Mobile-System-Design/ext-art-01.md)
