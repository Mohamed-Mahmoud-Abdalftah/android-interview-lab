package academy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class MigrationCoveragePlannerTest {
    private val steps = listOf(
        SchemaStep(1, 2, "create drafts"),
        SchemaStep(2, 3, "add server version"),
        SchemaStep(3, 4, "add mutation id"),
    )

    @Test fun plansACompleteMultiStepUpgrade() {
        assertEquals(steps, planMigration(current = 1, target = 4, steps = steps))
    }

    @Test fun choosesTheFewestSupportedStepsDeterministically() {
        val direct = SchemaStep(1, 4, "verified direct migration")
        val alternatives = steps + direct + SchemaStep(1, 3, "legacy shortcut")
        assertEquals(listOf(direct), planMigration(1, 4, alternatives))
    }

    @Test fun reportsNoPlanWhenAnUpgradeEdgeIsMissing() {
        assertEquals(null, planMigration(1, 4, steps.filterNot { it.from == 2 }))
    }

    @Test fun sameVersionNeedsNoMigration() {
        assertEquals(emptyList<SchemaStep>(), planMigration(4, 4, steps))
    }

    @Test fun downgradeIsExplicitlyUnsupportedByThisAuditModel() {
        assertEquals(null, planMigration(4, 2, steps))
    }

    @Test fun invalidOrDuplicateDefinitionsAreRejected() {
        assertThrows(IllegalArgumentException::class.java) {
            planMigration(1, 3, listOf(SchemaStep(2, 2, "no-op")))
        }
        assertThrows(IllegalArgumentException::class.java) {
            planMigration(1, 3, listOf(SchemaStep(1, 2, "a"), SchemaStep(1, 2, "b")))
        }
    }

    @Test fun auditsEverySupportedInstalledVersionAgainstTheReleaseTarget() {
        assertEquals(setOf(1), missingMigrationStarts(target = 4, supportedStarts = setOf(1, 2, 3, 4), steps = steps.drop(1)))
        assertEquals(emptySet<Int>(), missingMigrationStarts(4, setOf(1, 2, 3, 4), steps))
    }
}
