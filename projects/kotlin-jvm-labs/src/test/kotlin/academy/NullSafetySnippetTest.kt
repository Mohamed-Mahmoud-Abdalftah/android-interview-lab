package academy

import interviewlab.kot_03.label
import interviewlab.kot_03.normalizedToken
import interviewlab.kot_03.requireAccountId
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNull

class NullSafetySnippetTest {
    @Test
    fun `optional label falls back while required id fails clearly`() {
        assertNull(normalizedToken(null))
        assertNull(normalizedToken("  "))
        assertEquals("Ada", normalizedToken(" Ada "))
        assertEquals("Guest", label("  "))
        assertEquals("acct-1", requireAccountId("acct-1"))
        assertFailsWith<IllegalArgumentException> { requireAccountId(null) }
        assertFailsWith<IllegalArgumentException> { requireAccountId(" ") }
    }

    @Test
    fun `elvis uses nullable let result even with a present receiver`() {
        val present = "present"
        val result = present.let { null as String? } ?: "fallback"
        assertEquals("fallback", result)
    }
}
