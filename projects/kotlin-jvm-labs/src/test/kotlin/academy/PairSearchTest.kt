package academy

import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class PairSearchTest {
    @Test fun hashMapFindsOriginalIndicesWithoutMutatingInput() {
        val values = intArrayOf(2, 7, 11, 15)
        assertEquals(0 to 1, pairIndicesForTarget(values, 9))
        assertArrayEquals(intArrayOf(2, 7, 11, 15), values)
    }

    @Test fun duplicateValuesUseDistinctIndices() {
        assertEquals(0 to 1, pairIndicesForTarget(intArrayOf(3, 3), 6))
    }

    @Test fun overflowDoesNotCreateFalsePair() {
        assertNull(pairIndicesForTarget(intArrayOf(Int.MAX_VALUE, 1), Int.MIN_VALUE))
    }

    @Test fun negativeExtremesCanFormAValidPair() {
        assertEquals(0 to 1, pairIndicesForTarget(intArrayOf(Int.MIN_VALUE, Int.MAX_VALUE), -1))
    }

    @Test fun returnsFirstPairBySecondIndex() {
        assertEquals(1 to 2, pairIndicesForTarget(intArrayOf(1, 2, 3, 4), 5))
    }

    @Test fun sortedTwoPointersFindValuesWithoutExtraMap() {
        assertEquals(2 to 7, pairValuesInSorted(intArrayOf(1, 2, 5, 7, 9), 9))
    }

    @Test fun sortedTwoPointersHandleNoPairAndRejectBadContract() {
        assertNull(pairValuesInSorted(intArrayOf(1, 2, 5), 100))
        assertThrows(IllegalArgumentException::class.java) {
            pairValuesInSorted(intArrayOf(2, 1), 3)
        }
    }
}
