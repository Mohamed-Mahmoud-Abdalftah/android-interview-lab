---
id: ART-Q007
lesson_id: EXT-ART-01
topic: Reflection and shrinking
difficulty: senior
style: debugging
expected_minutes: 6
status: reviewed
---
# ART-Q007 — Reflection and shrinking

## Interview question

> **Interviewer:** A class is reached only by reflection and disappears in release. Explain why R8 cannot infer the edge, then choose between explicit registration, generated code, and a narrow keep rule.

<p dir="rtl" lang="ar"><strong>السياق:</strong> مرشح يقول Android يشغل JVM bytecode مباشرة أو ينسب crash في R8 لـART من غير فحص artifact/mapping</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ART-Q007.md) · [Lesson](../../08-Mobile-System-Design/ext-art-01.md)
