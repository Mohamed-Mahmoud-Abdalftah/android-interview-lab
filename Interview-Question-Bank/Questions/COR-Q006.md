---
id: COR-Q006
lesson_id: COR-002
topic: Failure propagation in a Job tree
difficulty: foundational
style: conceptual
expected_minutes: 4
status: reviewed
---
# COR-Q006 — Failure propagation in a Job tree

Three `async` children run inside `coroutineScope`. The second throws `IOException` while the others are suspended. Trace what happens to the parent and siblings, and explain when returning partial data would be a different contract.

[Open complete model answer](../Model-Answers/COR-Q006.md) · [Lesson](../../02-Coroutines-Flow/cor-002-job-hierarchy-exceptions-and-supervision.md)
