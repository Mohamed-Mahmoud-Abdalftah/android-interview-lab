---
id: COR-Q009
lesson_id: COR-002
topic: CancellationException preservation
difficulty: senior
style: code-review
expected_minutes: 5
status: reviewed
---
# COR-Q009 — CancellationException preservation

Why can `runCatching { suspendingCall() }` be dangerous in a long-lived worker, and what exact cancellation behavior should a corrected implementation preserve?

[Open complete model answer](../Model-Answers/COR-Q009.md) · [Lesson](../../02-Coroutines-Flow/cor-002-job-hierarchy-exceptions-and-supervision.md)
