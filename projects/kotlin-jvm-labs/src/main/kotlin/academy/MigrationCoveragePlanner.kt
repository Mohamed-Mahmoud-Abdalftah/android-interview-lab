package academy

data class SchemaStep(
    val from: Int,
    val to: Int,
    val label: String,
)

/**
 * Release-audit model for supported upgrade paths.
 *
 * It deliberately supports upgrades only and does not execute SQL or reproduce
 * Room's internal migration selection. The shortest declared path is useful for
 * finding release gaps before an Android integration test executes the real DB.
 */
fun planMigration(
    current: Int,
    target: Int,
    steps: Collection<SchemaStep>,
): List<SchemaStep>? {
    require(current > 0 && target > 0) { "Schema versions must be positive" }
    validateSteps(steps)
    if (current == target) return emptyList()
    if (current > target) return null

    data class Candidate(val version: Int, val path: List<SchemaStep>)

    val outgoing = steps
        .groupBy(SchemaStep::from)
        .mapValues { (_, candidates) -> candidates.sortedWith(compareBy(SchemaStep::to, SchemaStep::label)) }
    val queue = ArrayDeque<Candidate>()
    val visited = mutableSetOf(current)
    queue.addLast(Candidate(current, emptyList()))

    while (queue.isNotEmpty()) {
        val candidate = queue.removeFirst()
        for (step in outgoing[candidate.version].orEmpty()) {
            if (step.to > target || !visited.add(step.to)) continue
            val path = candidate.path + step
            if (step.to == target) return path
            queue.addLast(Candidate(step.to, path))
        }
    }
    return null
}

fun missingMigrationStarts(
    target: Int,
    supportedStarts: Set<Int>,
    steps: Collection<SchemaStep>,
): Set<Int> {
    require(target > 0 && supportedStarts.all { it > 0 }) { "Schema versions must be positive" }
    return supportedStarts
        .filterTo(linkedSetOf()) { start -> planMigration(start, target, steps) == null }
}

private fun validateSteps(steps: Collection<SchemaStep>) {
    steps.forEach { step ->
        require(step.from > 0 && step.to > 0) { "Schema versions must be positive" }
        require(step.from < step.to) { "This audit model accepts forward migrations only" }
        require(step.label.isNotBlank()) { "Every migration needs an audit label" }
    }
    require(steps.groupBy { it.from to it.to }.values.none { it.size > 1 }) {
        "Only one declared migration is allowed for each version pair"
    }
}
