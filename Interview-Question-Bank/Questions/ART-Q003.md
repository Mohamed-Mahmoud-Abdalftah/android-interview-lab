---
id: ART-Q003
lesson_id: EXT-ART-01
topic: ART execution
difficulty: intermediate
style: debugging
expected_minutes: 6
status: reviewed
---
# ART-Q003 — ART execution

## Interview question

> **Interviewer:** Does Android execute ordinary JVM bytecode directly? Explain DEX loading, interpretation, JIT, AOT profiles, and why execution strategy can vary by device and install history.

<p dir="rtl" lang="ar"><strong>السياق:</strong> مرشح يقول Android يشغل JVM bytecode مباشرة أو ينسب crash في R8 لـART من غير فحص artifact/mapping</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/ART-Q003.md) · [Lesson](../../08-Mobile-System-Design/ext-art-01.md)
