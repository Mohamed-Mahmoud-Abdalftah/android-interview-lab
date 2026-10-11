---
id: SYS-Q025
lesson_id: SYS-005
topic: Privacy and observability
difficulty: senior
style: system-design
expected_minutes: 6
status: reviewed
---
# SYS-Q025 — Privacy and observability

## Interview question

> **Interviewer:** You need to debug failed location sync without logging coordinates or user identity. Design useful redacted telemetry and its retention and access controls.

<p dir="rtl" lang="ar"><strong>السياق:</strong> push تصل قبل data أو مرتين، location updates تستهلك battery، أو reconnect يكرر رسائل.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q025.md) · [Lesson](../../08-Mobile-System-Design/sys-005-messaging-and-realtime-tracking-design.md)
