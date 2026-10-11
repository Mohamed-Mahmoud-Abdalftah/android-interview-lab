package academy

/** First pair by its second index; returns original indices and does not mutate input. */
fun pairIndicesForTarget(values: IntArray, target: Int): Pair<Int, Int>? {
    val earliestIndex = HashMap<Int, Int>()
    for (index in values.indices) {
        val complement = target.toLong() - values[index].toLong()
        if (complement in Int.MIN_VALUE.toLong()..Int.MAX_VALUE.toLong()) {
            val first = earliestIndex[complement.toInt()]
            if (first != null) return first to index
        }
        if (values[index] !in earliestIndex) earliestIndex[values[index]] = index
    }
    return null
}

/** Finds values in nondecreasing input; validation is included in O(n). */
fun pairValuesInSorted(values: IntArray, target: Int): Pair<Int, Int>? {
    for (index in 1 until values.size) {
        require(values[index - 1] <= values[index]) { "Input must be sorted in nondecreasing order" }
    }
    var left = 0
    var right = values.lastIndex
    while (left < right) {
        val sum = values[left].toLong() + values[right].toLong()
        when {
            sum == target.toLong() -> return values[left] to values[right]
            sum < target.toLong() -> left++
            else -> right--
        }
    }
    return null
}
