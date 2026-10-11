---
id: ART-Q001
lesson_id: EXT-ART-01
topic: Kotlin to DEX pipeline
difficulty: foundational
style: conceptual
expected_minutes: 6
status: reviewed
---
# ART-Q001 — Kotlin to DEX pipeline

## Interview question

> **Interviewer:** Trace a suspend Kotlin function from source to class files, desugared bytecode, DEX, a minified APK, and ART. Which stage owns each transformation?

<p dir="rtl" lang="ar"><strong>السياق:</strong> مرشح يقول Android يشغل JVM bytecode مباشرة أو ينسب crash في R8 لـART من غير فحص artifact/mapping</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ART-Q001.md) · [Lesson](../../08-Mobile-System-Design/ext-art-01.md)
