---
id: PRO-Q013
lesson_id: PRO-002
topic: Token refresh single-flight
difficulty: senior
style: debugging
expected_minutes: 5
status: reviewed
---
# PRO-Q013 — Token refresh single-flight

## Interview question

> **Interviewer:** Ten requests receive 401 at the same time and each starts a token refresh. Design a single-flight refresh flow, including refresh failure, a repeated 401, cancellation, and replaying the original requests once.

<p dir="rtl" lang="ar"><strong>السياق:</strong> عشر requests تاخد 401 فتعمل عشر refreshes، أو POST timed out يتكرر ويخصم مرتين.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q013.md) · [Lesson](../../06-Production-Engineering/pro-002-http-timeouts-retries-and-token-refresh.md)
