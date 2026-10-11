---
id: "DSA-11"
question: "Explain BFS versus DFS and their typical applications."
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "B"
phase: 5
priority: "P2"
order: 450
editorial_status: "reviewed"
---

# DSA-11

## Original interview question

Explain BFS versus DFS and their typical applications.

## What the interviewer evaluates

- BFS queue versus DFS stack/recursion and complexity.
- Shortest unweighted path, memory and Android use cases.

## Explanation in Arabic

BFS بيزور graph مستوى بمستوى باستخدام queue، مناسب لأقصر مسار بعدد edges في graph غير موزون. DFS يدخل عميق باستخدام stack/recursion، مناسب traversal، cycle checks أو backtracking حسب algorithm. الاتنين O(V+E) مع visited set على adjacency list، لكن BFS queue قد تكبر بعرض graph وDFS stack بعمقه.

## Why it matters and how it works

Both algorithms need visited handling in cyclic graphs. BFS shortest-path guarantee requires unweighted/equal-edge-cost graph; weighted shortest path needs another algorithm. Recursive DFS can overflow stack on deep graphs, so iterative stack may be safer.

## Worked example

For a navigation/dependency graph, BFS can find fewest screen transitions; DFS can detect a module-dependency cycle with visiting/visited states. Android module graphs can be large enough that iterative traversal avoids recursion depth risk.

## Trade-offs and decision criteria

BFS uses more memory on wide graphs; DFS can explore irrelevant deep paths before finding a nearby target. Choose by desired result, graph shape and memory constraints.

## Failure modes

Using BFS on weighted routes and calling first found path “cheapest” is wrong. Forgetting visited set loops forever on cycles. Test disconnected graph, self-loop and large/deep graph.

## Production perspective

In production, expose graph traversal as pure Kotlin logic and test with synthetic fixtures. Avoid doing large graph search on main thread; cache only when graph version is stable.

## Interview answer — short

“BFS uses a queue and finds shortest paths in an unweighted graph; DFS uses a stack or recursion and explores depth. Both are O(V+E) with visited tracking, but their memory patterns differ.”

## Interview answer — structured

“I choose BFS when levels or fewest-edge paths matter, and DFS for traversal or cycle/backtracking tasks. With adjacency lists and visited set both visit vertices/edges once, O(V+E). BFS may hold a wide frontier; DFS holds the current depth and can stack overflow if recursive. The shortest-path claim does not apply to weighted costs. The mechanics matter. Both algorithms need visited handling in cyclic graphs. BFS shortest-path guarantee requires unweighted/equal-edge-cost graph; weighted shortest path needs another algorithm. Recursive DFS can overflow stack on deep graphs, so iterative stack may be safer. The choice has a trade-off. BFS uses more memory on wide graphs; DFS can explore irrelevant deep paths before finding a nearby target. Choose by desired result, graph shape and memory constraints.”

## Interview answer — deep senior

“For a modular Android dependency graph I might run DFS with three-color state to detect a cycle and produce a path; for a support flow I might use BFS to find the fewest transitions to a target screen. I would state graph representation, visited semantics and whether edges carry weights. On large graphs I prefer iterative DFS to avoid JVM stack exhaustion and test self-cycles/disconnected nodes. I profile memory under wide frontiers before using BFS in a constrained device path. Consider a concrete case. For a navigation/dependency graph, BFS can find fewest screen transitions; DFS can detect a module-dependency cycle with visiting/visited states. Android module graphs can be large enough that iterative traversal avoids recursion depth risk. A failure case illustrates the risk. Using BFS on weighted routes and calling first found path “cheapest” is wrong. Forgetting visited set loops forever on cycles. Test disconnected graph, self-loop and large/deep graph. In production, the response is concrete. In production, expose graph traversal as pure Kotlin logic and test with synthetic fixtures. Avoid doing large graph search on main thread; cache only when graph version is stable. The decision has a trade-off. BFS uses more memory on wide graphs; DFS can explore irrelevant deep paths before finding a nearby target. Choose by desired result, graph shape and memory constraints.”

## Deep-dive talking points

Prompt for queue/stack, V+E, unweighted shortest path, recursion limit and cycles.

## Follow-up questions

- [DSA-05](../dsa-05/): Which structures support traversal? **Answer:** queue for BFS, stack for DFS.
- [DSA-14](../dsa-14/): Where should heavy graph work run? **Answer:** off main thread with measured data size.

## Self-check rubric

Can you derive the bound, explain the Android example, identify a trade-off/failure, and answer both follow-ups?

## References and reviewed-on date

- [Kotlin ArrayDeque](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/-array-deque/) — queue/stack implementation.
- [Android performance](https://developer.android.com/topic/performance) — main-thread costs.

Technically reviewed against the cited primary documentation on 2026-10-11; automated technical review only, not human review.
