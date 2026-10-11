---
id: ART-Q004
lesson_id: EXT-ART-01
topic: Zygote model
difficulty: senior
style: architecture
expected_minutes: 6
status: reviewed
---
# ART-Q004 — Zygote model

## Interview question

> **Interviewer:** Explain how Zygote starts an Android app process, what memory can be shared through copy-on-write, and why app initialization still runs in the child process.

<p dir="rtl" lang="ar"><strong>السياق:</strong> مرشح يقول Android يشغل JVM bytecode مباشرة أو ينسب crash في R8 لـART من غير فحص artifact/mapping</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ART-Q004.md) · [Lesson](../../08-Mobile-System-Design/ext-art-01.md)
