package academy

import java.util.PriorityQueue

data class WeightedEdge(val to: String, val weight: Long)
data class PathResult(val distance: Long, val nodes: List<String>)

private data class QueueNode(val label: String, val distance: Long)

/** Dijkstra shortest path for a directed graph with non-negative weights. */
fun shortestPath(
    graph: Map<String, List<WeightedEdge>>,
    start: String,
    target: String,
): PathResult? {
    require(graph.values.flatten().none { it.weight < 0 }) { "Dijkstra requires non-negative weights" }
    val nodes = graph.keys + graph.values.flatten().map(WeightedEdge::to)
    if (start !in nodes || target !in nodes) return null

    val distances = mutableMapOf(start to 0L)
    val previous = mutableMapOf<String, String>()
    val queue = PriorityQueue(compareBy<QueueNode> { it.distance }.thenBy { it.label })
    queue += QueueNode(start, 0)

    while (queue.isNotEmpty()) {
        val current = queue.poll()
        if (distances[current.label] != current.distance) continue
        if (current.label == target) break
        for (edge in graph[current.label].orEmpty()) {
            if (current.distance > Long.MAX_VALUE - edge.weight) continue
            val candidate = current.distance + edge.weight
            if (candidate < distances.getOrDefault(edge.to, Long.MAX_VALUE)) {
                distances[edge.to] = candidate
                previous[edge.to] = current.label
                queue += QueueNode(edge.to, candidate)
            }
        }
    }

    val distance = distances[target] ?: return null
    val reversed = mutableListOf(target)
    while (reversed.last() != start) {
        reversed += previous[reversed.last()] ?: return null
    }
    return PathResult(distance, reversed.asReversed())
}
