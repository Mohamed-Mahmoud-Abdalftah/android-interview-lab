---
id: PRO-Q012
lesson_id: PRO-002
topic: Retry safety
difficulty: intermediate
style: code-review
expected_minutes: 4
status: reviewed
---
# PRO-Q012 — Retry safety

## Interview question

> **Interviewer:** A POST /orders request timed out after bytes were sent. Is an automatic retry safe? Design the idempotency key, retry classification, and status lookup needed to prevent a duplicate order.

<p dir="rtl" lang="ar"><strong>السياق:</strong> عشر requests تاخد 401 فتعمل عشر refreshes، أو POST timed out يتكرر ويخصم مرتين.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q012.md) · [Lesson](../../06-Production-Engineering/pro-002-http-timeouts-retries-and-token-refresh.md)
