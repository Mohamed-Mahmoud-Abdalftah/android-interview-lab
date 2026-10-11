package academy

import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

class DuplicateScanTest {
    @Test
    fun `empty and single element inputs have no duplicate`() {
        assertEquals(DuplicateScan(null, 0), firstDuplicateNested(intArrayOf()))
        assertEquals(DuplicateScan(null, 1), firstDuplicateWithSet(intArrayOf(8)))
    }

    @Test
    fun `both strategies return the first value repeated in input order`() {
        val values = intArrayOf(9, 4, 4, 9)

        assertEquals(4, firstDuplicateNested(values).duplicate)
        assertEquals(4, firstDuplicateWithSet(values).duplicate)
    }

    @Test
    fun `unique input exposes quadratic versus linear probe growth`() {
        val values = intArrayOf(5, 1, 9, -3, 7)

        assertEquals(DuplicateScan(null, 10), firstDuplicateNested(values))
        assertEquals(DuplicateScan(null, 5), firstDuplicateWithSet(values))
    }

    @Test
    fun `early duplicate stops both scans without reading the tail`() {
        val values = intArrayOf(7, 7, 8, 9)

        assertEquals(DuplicateScan(7, 1), firstDuplicateNested(values))
        assertEquals(DuplicateScan(7, 2), firstDuplicateWithSet(values))
    }

    @Test
    fun `integer boundaries are ordinary stable keys`() {
        val values = intArrayOf(Int.MIN_VALUE, -1, Int.MAX_VALUE, Int.MIN_VALUE)

        assertEquals(Int.MIN_VALUE, firstDuplicateNested(values).duplicate)
        assertEquals(Int.MIN_VALUE, firstDuplicateWithSet(values).duplicate)
    }

    @Test
    fun `neither strategy mutates caller input`() {
        val values = intArrayOf(3, 2, 1, 3)
        val snapshot = values.copyOf()

        firstDuplicateNested(values)
        firstDuplicateWithSet(values)

        assertArrayEquals(snapshot, values)
    }

    @Test
    fun `probe count is evidence about this implementation not elapsed time`() {
        val result = firstDuplicateWithSet(intArrayOf(1, 2, 3, 4))

        assertNull(result.duplicate)
        assertEquals(4, result.probes)
    }
}
