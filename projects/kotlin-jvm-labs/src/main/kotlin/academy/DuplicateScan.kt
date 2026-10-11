package academy

/**
 * A deterministic teaching signal. [probes] counts candidate comparisons or
 * set insert attempts; it is not a wall-clock benchmark.
 */
data class DuplicateScan(
    val duplicate: Int?,
    val probes: Int,
)

fun firstDuplicateNested(values: IntArray): DuplicateScan {
    var comparisons = 0
    for (currentIndex in values.indices) {
        for (previousIndex in 0 until currentIndex) {
            comparisons += 1
            if (values[previousIndex] == values[currentIndex]) {
                return DuplicateScan(values[currentIndex], comparisons)
            }
        }
    }
    return DuplicateScan(null, comparisons)
}

fun firstDuplicateWithSet(values: IntArray): DuplicateScan {
    val seen = HashSet<Int>(values.size)
    var probes = 0
    for (value in values) {
        probes += 1
        if (!seen.add(value)) return DuplicateScan(value, probes)
    }
    return DuplicateScan(null, probes)
}
