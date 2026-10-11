package academy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class ShortestPathTest {
    @Test fun choosesLowerTotalCostInsteadOfFewestEdges() {
        val graph = mapOf(
            "A" to listOf(WeightedEdge("B", 8), WeightedEdge("C", 2)),
            "C" to listOf(WeightedEdge("B", 2)),
            "B" to emptyList(),
        )
        assertEquals(PathResult(4, listOf("A", "C", "B")), shortestPath(graph, "A", "B"))
    }

    @Test fun skipsStaleHeapEntriesAfterFindingABetterRoute() {
        val graph = mapOf(
            "A" to listOf(WeightedEdge("B", 10), WeightedEdge("C", 1)),
            "C" to listOf(WeightedEdge("B", 1)),
            "B" to listOf(WeightedEdge("D", 1)),
            "D" to emptyList(),
        )
        assertEquals(PathResult(3, listOf("A", "C", "B", "D")), shortestPath(graph, "A", "D"))
    }

    @Test fun returnsNullWhenTargetIsUnreachableOrMissing() {
        val graph = mapOf("A" to emptyList<WeightedEdge>(), "B" to emptyList())
        assertNull(shortestPath(graph, "A", "B"))
        assertNull(shortestPath(graph, "A", "missing"))
    }

    @Test fun startEqualsTargetHasZeroCostWhenNodeExists() {
        assertEquals(PathResult(0, listOf("A")), shortestPath(mapOf("A" to emptyList()), "A", "A"))
    }

    @Test fun rejectsNegativeWeightsBeforeSearching() {
        val graph = mapOf("A" to listOf(WeightedEdge("B", -1)), "B" to emptyList())
        assertThrows(IllegalArgumentException::class.java) { shortestPath(graph, "A", "B") }
    }

    @Test fun avoidsLongOverflowCreatingAFakeShortPath() {
        val graph = mapOf(
            "A" to listOf(WeightedEdge("B", Long.MAX_VALUE), WeightedEdge("C", 7)),
            "B" to listOf(WeightedEdge("C", 10)),
            "C" to emptyList(),
        )
        assertEquals(PathResult(7, listOf("A", "C")), shortestPath(graph, "A", "C"))
    }

    @Test fun treatsDestinationOnlyLabelsAsGraphNodes() {
        val graph = mapOf("A" to listOf(WeightedEdge("B", 5)))
        assertEquals(PathResult(5, listOf("A", "B")), shortestPath(graph, "A", "B"))
    }
}
