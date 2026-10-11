---
id: SYS-Q007
lesson_id: SYS-002
topic: Heap invariant
difficulty: intermediate
style: code-review
expected_minutes: 4
status: reviewed
---
# SYS-Q007 — Heap invariant

## Interview question

> **Interviewer:** A developer assumes iterating PriorityQueue returns sorted order. Explain the actual heap guarantee and show how stale entries are handled in Dijkstra.

<p dir="rtl" lang="ar"><strong>السياق:</strong> Dijkstra على negative edge، BFS على weighted graph، أو DP table من غير تعريف معنى الخانة.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q007.md) · [Lesson](../../08-Mobile-System-Design/sys-002-trees-graphs-heaps-and-basic-dp.md)
