---
id: ART-Q005
lesson_id: EXT-ART-01
topic: Class loading identity
difficulty: senior
style: live-coding
expected_minutes: 6
status: reviewed
---
# ART-Q005 — Class loading identity

## Interview question

> **Interviewer:** Two classes have the same fully qualified name but come from different ClassLoaders. Are they the same type? Relate the answer to dynamic features or plugin code.

<p dir="rtl" lang="ar"><strong>السياق:</strong> مرشح يقول Android يشغل JVM bytecode مباشرة أو ينسب crash في R8 لـART من غير فحص artifact/mapping</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ART-Q005.md) · [Lesson](../../08-Mobile-System-Design/ext-art-01.md)
