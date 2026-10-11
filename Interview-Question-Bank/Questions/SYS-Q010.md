---
id: SYS-Q010
lesson_id: SYS-002
topic: Graph test boundaries
difficulty: senior
style: system-design
expected_minutes: 6
status: reviewed
---
# SYS-Q010 — Graph test boundaries

## Interview question

> **Interviewer:** Design a compact test set for a directed-graph algorithm covering disconnected nodes, self-loops, duplicate edges, equal paths, invalid weights, and numeric overflow.

<p dir="rtl" lang="ar"><strong>السياق:</strong> Dijkstra على negative edge، BFS على weighted graph، أو DP table من غير تعريف معنى الخانة.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q010.md) · [Lesson](../../08-Mobile-System-Design/sys-002-trees-graphs-heaps-and-basic-dp.md)
