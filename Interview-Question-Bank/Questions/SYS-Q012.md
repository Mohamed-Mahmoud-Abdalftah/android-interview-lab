---
id: SYS-Q012
lesson_id: SYS-003
topic: Refresh race
difficulty: intermediate
style: code-review
expected_minutes: 4
status: reviewed
---
# SYS-Q012 — Refresh race

## Interview question

> **Interviewer:** A token refresh starts, the user logs out, and the refresh succeeds later. Trace the race and show how an account generation or session ID prevents stale commit.

<p dir="rtl" lang="ar"><strong>السياق:</strong> refresh قديمة ترجع بعد logout فتحيي session، أو cache من account A تظهر في B.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q012.md) · [Lesson](../../08-Mobile-System-Design/sys-003-mobile-auth-and-session-state-design.md)
