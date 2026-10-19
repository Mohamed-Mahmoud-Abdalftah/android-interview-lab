package academy

import interviewlab.cor_09.BlockingStore
import interviewlab.cor_09.loadLabel
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class WithContextSnippetTest {
    @Test
    fun returnedValuePassesBackThroughUpdatedContext() = runTest {
        val store = object : BlockingStore {
            override fun read(id: String) = " Ada "
        }
        assertEquals("Ada", loadLabel(store, "42", StandardTestDispatcher(testScheduler)))
    }

    @Test
    fun exceptionPropagatesToCaller() = runTest {
        val failure = IllegalStateException("disk unavailable")
        val store = object : BlockingStore {
            override fun read(id: String): String = throw failure
        }
        val observed = try {
            loadLabel(store, "42", StandardTestDispatcher(testScheduler))
            null
        } catch (error: IllegalStateException) {
            error
        }
        assertEquals("disk unavailable", observed?.message)
    }
}
