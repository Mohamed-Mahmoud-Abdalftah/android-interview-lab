package academy

import interviewlab.di_20.CatalogBridge
import interviewlab.di_20.LegacyCatalogContainer
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Test

class ManualToHiltBridgeSnippetTest {
    @Test
    fun temporaryBridgeSharesLegacyOwnerInsteadOfDuplicatingState() {
        val legacy = LegacyCatalogContainer()
        val bridge = CatalogBridge(legacy)
        assertSame(legacy.repository, bridge.repository())
        legacy.repository.add("cached item")
        assertEquals(listOf("cached item"), bridge.repository().all())
    }
}
