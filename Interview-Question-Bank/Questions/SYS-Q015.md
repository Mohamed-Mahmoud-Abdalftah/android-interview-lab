---
id: SYS-Q015
lesson_id: SYS-003
topic: Server authority
difficulty: senior
style: system-design
expected_minutes: 6
status: reviewed
---
# SYS-Q015 — Server authority

## Interview question

> **Interviewer:** A client has a valid-looking token and cached role=admin. Explain why the server must remain the authorization authority and how the client should behave offline.

<p dir="rtl" lang="ar"><strong>السياق:</strong> refresh قديمة ترجع بعد logout فتحيي session، أو cache من account A تظهر في B.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q015.md) · [Lesson](../../08-Mobile-System-Design/sys-003-mobile-auth-and-session-state-design.md)
