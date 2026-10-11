---
id: PRO-Q011
lesson_id: PRO-002
topic: Timeout taxonomy
difficulty: foundational
style: conceptual
expected_minutes: 4
status: reviewed
---
# PRO-Q011 — Timeout taxonomy

## Interview question

> **Interviewer:** An API call reports a timeout. Distinguish connect, read, call, and application deadlines. For each one, state what you know about whether the server executed the request.

<p dir="rtl" lang="ar"><strong>السياق:</strong> عشر requests تاخد 401 فتعمل عشر refreshes، أو POST timed out يتكرر ويخصم مرتين.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q011.md) · [Lesson](../../06-Production-Engineering/pro-002-http-timeouts-retries-and-token-refresh.md)
