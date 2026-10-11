---
id: ART-Q010
lesson_id: EXT-ART-01
topic: Runtime evidence
difficulty: senior
style: architecture
expected_minutes: 6
status: reviewed
---
# ART-Q010 — Runtime evidence

## Interview question

> **Interviewer:** Compare what a JVM unit test, APK inspection, instrumented test, Perfetto trace, and on-device crash can prove about Android runtime behavior.

<p dir="rtl" lang="ar"><strong>السياق:</strong> مرشح يقول Android يشغل JVM bytecode مباشرة أو ينسب crash في R8 لـART من غير فحص artifact/mapping</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ART-Q010.md) · [Lesson](../../08-Mobile-System-Design/ext-art-01.md)
