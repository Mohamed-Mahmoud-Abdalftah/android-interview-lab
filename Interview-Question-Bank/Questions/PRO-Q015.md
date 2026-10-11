---
id: PRO-Q015
lesson_id: PRO-002
topic: Backoff and jitter
difficulty: senior
style: system-design
expected_minutes: 6
status: reviewed
---
# PRO-Q015 — Backoff and jitter

## Interview question

> **Interviewer:** Thousands of clients reconnect after an outage. Derive a capped exponential backoff with jitter, explain when to honor Retry-After, and name failures that must not be retried.

<p dir="rtl" lang="ar"><strong>السياق:</strong> عشر requests تاخد 401 فتعمل عشر refreshes، أو POST timed out يتكرر ويخصم مرتين.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q015.md) · [Lesson](../../06-Production-Engineering/pro-002-http-timeouts-retries-and-token-refresh.md)
