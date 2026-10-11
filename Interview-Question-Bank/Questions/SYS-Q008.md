---
id: SYS-Q008
lesson_id: SYS-002
topic: Dijkstra precondition
difficulty: senior
style: debugging
expected_minutes: 5
status: reviewed
---
# SYS-Q008 — Dijkstra precondition

## Interview question

> **Interviewer:** A graph contains one negative edge but no negative cycle. Explain exactly why Dijkstra can finalize the wrong distance and choose a valid alternative.

<p dir="rtl" lang="ar"><strong>السياق:</strong> Dijkstra على negative edge، BFS على weighted graph، أو DP table من غير تعريف معنى الخانة.</p>

## Follow-ups an interviewer may ask

1. What is the most common wrong answer here, and what production failure can it cause?
2. What exact test or trace would convince you that the fix works?
3. Under which constraint would you choose a different design?

[Open complete model answer](../Model-Answers/SYS-Q008.md) · [Lesson](../../08-Mobile-System-Design/sys-002-trees-graphs-heaps-and-basic-dp.md)
