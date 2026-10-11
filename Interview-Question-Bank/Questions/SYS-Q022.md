---
id: SYS-Q022
lesson_id: SYS-005
topic: Ordering and gaps
difficulty: intermediate
style: code-review
expected_minutes: 4
status: reviewed
---
# SYS-Q022 — Ordering and gaps

## Interview question

> **Interviewer:** Events arrive with sequence numbers 41, 43, 42, and 43 again. Show how the client detects the gap, buffers or catches up, orders application, and deduplicates.

<p dir="rtl" lang="ar"><strong>السياق:</strong> push تصل قبل data أو مرتين، location updates تستهلك battery، أو reconnect يكرر رسائل.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q022.md) · [Lesson](../../08-Mobile-System-Design/sys-005-messaging-and-realtime-tracking-design.md)
