---
id: SYS-Q013
lesson_id: SYS-003
topic: Secure storage
difficulty: senior
style: debugging
expected_minutes: 5
status: reviewed
---
# SYS-Q013 — Secure storage

## Interview question

> **Interviewer:** What security guarantee does Android Keystore provide for an auth token, what does it not provide, and how do server revocation and rooted-device risk change your design?

<p dir="rtl" lang="ar"><strong>السياق:</strong> refresh قديمة ترجع بعد logout فتحيي session، أو cache من account A تظهر في B.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q013.md) · [Lesson](../../08-Mobile-System-Design/sys-003-mobile-auth-and-session-state-design.md)
