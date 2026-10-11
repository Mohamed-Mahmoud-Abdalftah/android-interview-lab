---
id: PRO-Q014
lesson_id: PRO-002
topic: Unknown outcome
difficulty: senior
style: architecture
expected_minutes: 5
status: reviewed
---
# PRO-Q014 — Unknown outcome

## Interview question

> **Interviewer:** A payment request times out after the backend may have committed it. Model the client state and user experience until the result can be reconciled. Why are both success and failure unsafe guesses?

<p dir="rtl" lang="ar"><strong>السياق:</strong> عشر requests تاخد 401 فتعمل عشر refreshes، أو POST timed out يتكرر ويخصم مرتين.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/PRO-Q014.md) · [Lesson](../../06-Production-Engineering/pro-002-http-timeouts-retries-and-token-refresh.md)
