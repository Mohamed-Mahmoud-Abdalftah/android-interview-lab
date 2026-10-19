package academy

import interviewlab.cor_10.scan
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class CooperativeCancellationSnippetTest {
    @Test
    fun activeScanProcessesEveryItem() = runBlocking {
        val inspected = mutableListOf<String>()
        scan(listOf("a", "b", "c"), inspected::add)
        assertEquals(listOf("a", "b", "c"), inspected)
    }

    @Test
    fun cancelledScanStopsAtNextCheck() = runBlocking {
        val inspected = AtomicInteger()
        val job = launch {
            scan((0..1024).map(Int::toString)) {
                if (inspected.incrementAndGet() == 300) this@launch.cancel()
            }
        }
        job.join()
        assertTrue(job.isCancelled)
        assertEquals(512, inspected.get())
    }
}
