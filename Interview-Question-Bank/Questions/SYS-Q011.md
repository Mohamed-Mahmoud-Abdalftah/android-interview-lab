---
id: SYS-Q011
lesson_id: SYS-003
topic: Session state machine
difficulty: foundational
style: conceptual
expected_minutes: 4
status: reviewed
---
# SYS-Q011 — Session state machine

## Interview question

> **Interviewer:** Model SignedOut, Refreshing, Authenticated, and Expired states. Which events are legal in each state, and how do you stop an old refresh result from resurrecting a logged-out session?

<p dir="rtl" lang="ar"><strong>السياق:</strong> refresh قديمة ترجع بعد logout فتحيي session، أو cache من account A تظهر في B.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q011.md) · [Lesson](../../08-Mobile-System-Design/sys-003-mobile-auth-and-session-state-design.md)
