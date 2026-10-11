---
id: SYS-Q021
lesson_id: SYS-005
topic: Push as signal
difficulty: foundational
style: conceptual
expected_minutes: 4
status: reviewed
---
# SYS-Q021 — Push as signal

## Interview question

> **Interviewer:** A product manager says push notifications guarantee the phone has every update. Explain delivery limits and design push as a hint that triggers idempotent catch-up.

<p dir="rtl" lang="ar"><strong>السياق:</strong> push تصل قبل data أو مرتين، location updates تستهلك battery، أو reconnect يكرر رسائل.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q021.md) · [Lesson](../../08-Mobile-System-Design/sys-005-messaging-and-realtime-tracking-design.md)
