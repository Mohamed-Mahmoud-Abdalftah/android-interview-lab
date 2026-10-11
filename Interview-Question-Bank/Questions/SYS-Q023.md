---
id: SYS-Q023
lesson_id: SYS-005
topic: Reconnect policy
difficulty: senior
style: debugging
expected_minutes: 5
status: reviewed
---
# SYS-Q023 — Reconnect policy

## Interview question

> **Interviewer:** Design one WebSocket connection owner across lifecycle changes and network flaps. Cover backoff, token refresh, generation, catch-up, and duplicate connection prevention.

<p dir="rtl" lang="ar"><strong>السياق:</strong> push تصل قبل data أو مرتين، location updates تستهلك battery، أو reconnect يكرر رسائل.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q023.md) · [Lesson](../../08-Mobile-System-Design/sys-005-messaging-and-realtime-tracking-design.md)
