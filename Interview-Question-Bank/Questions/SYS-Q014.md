---
id: SYS-Q014
lesson_id: SYS-003
topic: Account partitioning
difficulty: senior
style: architecture
expected_minutes: 5
status: reviewed
---
# SYS-Q014 — Account partitioning

## Interview question

> **Interviewer:** A multi-account app shares Room tables, caches, WorkManager jobs, and notifications. Design the account keying and cleanup rules that prevent cross-account data leakage.

<p dir="rtl" lang="ar"><strong>السياق:</strong> refresh قديمة ترجع بعد logout فتحيي session، أو cache من account A تظهر في B.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q014.md) · [Lesson](../../08-Mobile-System-Design/sys-003-mobile-auth-and-session-state-design.md)
