---
id: COR-Q007
lesson_id: COR-002
topic: CoroutineExceptionHandler boundary
difficulty: senior
style: debugging
expected_minutes: 5
status: reviewed
---
# COR-Q007 — CoroutineExceptionHandler boundary

A developer installs `CoroutineExceptionHandler` on a child `launch` inside `viewModelScope` and expects the handler to keep the parent alive. Why is this mental model wrong, and where should recovery live?

[Open complete model answer](../Model-Answers/COR-Q007.md) · [Lesson](../../02-Coroutines-Flow/cor-002-job-hierarchy-exceptions-and-supervision.md)
