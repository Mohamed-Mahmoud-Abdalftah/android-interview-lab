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

### Practical walkthrough in Egyptian Arabic

BFS queue تصل لأقصر عدد edges في graph غير موزون، وDFS stack/recursion مناسبة للاستكشاف أو backtracking لا تضمن أقصر مسار. ضع visited عند enqueue كي لا تكرر cycle، واختبر disconnected node. لو edges لها أوزان، BFS لا يحل shortest weighted path؛ استعمل Dijkstra بشروطه. في Android مثال dependency graph أو navigation graph محدود الحجم.

## Why it matters and how it works

Both algorithms need visited handling in cyclic graphs. BFS shortest-path guarantee requires unweighted/equal-edge-cost graph; weighted shortest path needs another algorithm. Recursive DFS can overflow stack on deep graphs, so iterative stack may be safer.

## Worked example

For a navigation/dependency graph, BFS can find fewest screen transitions; DFS can detect a module-dependency cycle with visiting/visited states. Android module graphs can be large enough that iterative traversal avoids recursion depth risk.

A breadth-first traversal uses a queue and a visited set. For an unweighted graph it discovers nodes in increasing edge distance; mark a node visited when it is enqueued so a cycle cannot enqueue it repeatedly.

```kotlin
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

private fun shortestHops(graph: Map<String, List<String>>, start: String, goal: String): Int? {
    val queue = ArrayDeque<Pair<String, Int>>()
    val seen = mutableSetOf(start)
    queue.addLast(start to 0)
    while (queue.isNotEmpty()) {
        val (node, distance) = queue.removeFirst()
        if (node == goal) return distance
        for (next in graph[node].orEmpty()) {
            if (seen.add(next)) queue.addLast(next to distance + 1)
        }
    }
    return null
}

class BfsExampleTest {
    @Test fun shortestUnweightedRouteAndCycle() {
        val graph = mapOf("A" to listOf("B", "C"), "B" to listOf("A", "D"), "C" to listOf("D"))
        assertEquals(2, shortestHops(graph, "A", "D"))
        assertEquals(null, shortestHops(graph, "A", "missing"))
    }
}
```

## Trade-offs and decision criteria

BFS uses more memory on wide graphs; DFS can explore irrelevant deep paths before finding a nearby target. Choose by desired result, graph shape and memory constraints.

## Failure modes

Using BFS on weighted routes and calling first found path “cheapest” is wrong. Forgetting visited set loops forever on cycles. Test disconnected graph, self-loop and large/deep graph.

## Production perspective

In production, expose graph traversal as pure Kotlin logic and test with synthetic fixtures. Avoid doing large graph search on main thread; cache only when graph version is stable.

## Interview answer — short

“BFS uses a queue and finds shortest paths in an unweighted graph; DFS uses a stack or recursion and explores depth. Both are O(V+E) with visited tracking, but their memory patterns differ.”

## Interview answer — structured

“I choose BFS when levels or fewest-edge paths matter, and DFS for traversal or cycle/backtracking tasks. With adjacency lists and visited set both visit vertices/edges once, O(V+E). BFS may hold a wide frontier; DFS holds the current depth and can stack overflow if recursive. The shortest-path claim does not apply to weighted costs.”

## Interview answer — deep senior

“BFS expands nodes in layers with a queue, so in an unweighted graph the first time it reaches a target gives the fewest edges. DFS follows one path with a stack or recursion and backtracks; it is useful for reachability or exhaustive exploration but does not generally give the shortest route. Both traverse each reachable vertex and edge at most a constant number of times with a visited set, giving O(V + E) work. Memory differs: BFS may hold a broad frontier, while DFS holds a path/stack and visited set. I mark a node visited when it enters the BFS queue to avoid repeated enqueues in cycles. If edges have weights, ordinary BFS is the wrong shortest-path algorithm; I would choose a weighted algorithm such as Dijkstra only when nonnegative weights satisfy its contract. In an Android feature, a dependency graph or navigation graph may be small enough that clarity matters more than micro-optimization. I test cycles, disconnected nodes, start equals target and graph size limits.”

## How to answer in the interview

- **Why:** graph traversal choice depends on goal.
- **How:** show queue/stack and visited invariant.
- **Trade-off:** BFS memory versus DFS depth.
- **Failure case:** using BFS for weighted shortest path.
- **Production solution:** choose by graph contract and test cycles.

## Deep-dive talking points

Prompt for queue/stack, V+E, unweighted shortest path, recursion limit and cycles.

## Follow-up questions

- [DSA-05](../dsa-05/): Which structures support traversal? **Answer:** queue for BFS, stack for DFS.
- [DSA-14](../dsa-14/): Where should heavy graph work run? **Answer:** off main thread with measured data size.

## Self-check rubric

Trace the frontier order for BFS and DFS on a small graph; choose BFS for unweighted shortest path and DFS for traversal, then handle visited nodes and memory bounds.

## References and reviewed-on date

- [Kotlin ArrayDeque](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/-array-deque/) — queue/stack implementation.
- [Android performance](https://developer.android.com/topic/performance) — main-thread costs.

Technically reviewed against the cited primary documentation on 2026-10-13; automated technical review only, not human review.
