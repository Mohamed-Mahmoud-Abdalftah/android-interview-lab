---
id: ART-Q006
lesson_id: EXT-ART-01
topic: JNI boundary
difficulty: senior
style: performance
expected_minutes: 6
status: reviewed
---
# ART-Q006 — JNI boundary

## Interview question

> **Interviewer:** A native call crashes only on one ABI. Walk through symbol packaging, thread attachment, local and global references, exception checking, and the artifacts you inspect.

<p dir="rtl" lang="ar"><strong>السياق:</strong> مرشح يقول Android يشغل JVM bytecode مباشرة أو ينسب crash في R8 لـART من غير فحص artifact/mapping</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ART-Q006.md) · [Lesson](../../08-Mobile-System-Design/ext-art-01.md)
