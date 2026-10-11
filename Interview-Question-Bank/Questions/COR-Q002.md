---
id: COR-Q002
lesson_id: COR-001
topic: Parent waits for children
difficulty: intermediate
style: code-review
expected_minutes: 4
status: reviewed
---
# COR-Q002 — Parent waits for children

In coroutineScope, two independent async children load a name and a badge count. The badge count finishes first, while name.await() appears before badges.await(). When can the parent return and what does await order mean?

[Open complete model answer](../Model-Answers/COR-Q002.md) · [Lesson](../../02-Coroutines-Flow/cor-001-suspend-dispatchers-and-structured-scopes.md)
