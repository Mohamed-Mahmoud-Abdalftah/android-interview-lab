package academy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DeferredRequestTest {
    @Test
    fun factoryDoesNotReadProviderOrSendRequest() {
        var reads = 0
        val sent = mutableListOf<String>()

        createDeferredProfileRequest(
            currentId = { reads++; "Ada" },
            request = { sent.add(it) },
        )

        assertEquals(0, reads)
        assertEquals(emptyList<String>(), sent)
    }

    @Test
    fun invocationReadsCurrentValueRatherThanCreationSnapshot() {
        var current = "old"
        val sent = mutableListOf<String>()
        val callback = createDeferredProfileRequest({ current }, { sent.add(it) })

        current = "new"
        assertTrue(callback())

        assertEquals(listOf("new"), sent)
    }

    @Test
    fun nullAndBlankValuesDoNotSendRequest() {
        var current: String? = null
        val sent = mutableListOf<String>()
        val callback = createDeferredProfileRequest({ current }, { sent.add(it) })

        assertFalse(callback())
        current = "   "
        assertFalse(callback())
        assertEquals(emptyList<String>(), sent)
    }

    @Test
    fun validInputIsTrimmedAndSentOncePerInvocation() {
        val sent = mutableListOf<String>()
        val callback = createDeferredProfileRequest({ "  Ada  " }, { sent.add(it) })

        assertTrue(callback())
        assertEquals(listOf("Ada"), sent)
    }

    @Test
    fun eachInvocationReadsProviderAgain() {
        var current = "one"
        val sent = mutableListOf<String>()
        val callback = createDeferredProfileRequest({ current }, { sent.add(it) })

        assertTrue(callback())
        current = "two"
        assertTrue(callback())

        assertEquals(listOf("one", "two"), sent)
    }

    @Test
    fun requestExceptionPropagatesInsteadOfBeingSilentlyConvertedToFalse() {
        val callback = createDeferredProfileRequest(
            currentId = { "Ada" },
            request = { throw IllegalStateException("network failure") },
        )

        org.junit.jupiter.api.assertThrows<IllegalStateException> { callback() }
    }
}
