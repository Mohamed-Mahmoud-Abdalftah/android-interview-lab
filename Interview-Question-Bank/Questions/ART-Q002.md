---
id: ART-Q002
lesson_id: EXT-ART-01
topic: D8 versus R8
difficulty: intermediate
style: code-review
expected_minutes: 6
status: reviewed
---
# ART-Q002 — D8 versus R8

## Interview question

> **Interviewer:** A teammate says D8 and R8 are interchangeable names for the same optimizer. Correct the model and explain what artifact and failure each tool helps you investigate.

<p dir="rtl" lang="ar"><strong>السياق:</strong> مرشح يقول Android يشغل JVM bytecode مباشرة أو ينسب crash في R8 لـART من غير فحص artifact/mapping</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ART-Q002.md) · [Lesson](../../08-Mobile-System-Design/ext-art-01.md)
