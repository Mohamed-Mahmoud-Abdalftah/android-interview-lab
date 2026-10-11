---
id: SYS-Q024
lesson_id: SYS-005
topic: Location freshness
difficulty: senior
style: architecture
expected_minutes: 5
status: reviewed
---
# SYS-Q024 — Location freshness

## Interview question

> **Interviewer:** A courier app shows location. Define freshness, accuracy, permission, battery, background, and out-of-order update rules before choosing the API and interval.

<p dir="rtl" lang="ar"><strong>السياق:</strong> push تصل قبل data أو مرتين، location updates تستهلك battery، أو reconnect يكرر رسائل.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q024.md) · [Lesson](../../08-Mobile-System-Design/sys-005-messaging-and-realtime-tracking-design.md)
