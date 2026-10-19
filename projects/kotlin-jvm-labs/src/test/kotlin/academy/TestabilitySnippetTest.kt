package academy

import interviewlab.tst_04.Order
import interviewlab.tst_04.OrderApi
import interviewlab.tst_04.OrderProcessor
import interviewlab.tst_04.OrderStore
import java.time.Clock
import java.time.Instant
import java.time.ZoneOffset
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals

class TestabilitySnippetTest {
    @Test
    fun `expiry is deterministic at the boundary and persisted`() = runTest {
        val expiry = Instant.parse("2026-10-19T09:00:00Z")
        val api = object : OrderApi {
            override suspend fun fetch(id: String) = Order(id, expiry)
        }
        val writes = mutableListOf<Pair<String, String>>()
        val store = object : OrderStore {
            override suspend fun saveStatus(id: String, status: String) {
                writes += id to status
            }
        }
        val dispatcher = StandardTestDispatcher(testScheduler)
        val before = OrderProcessor(api, store, Clock.fixed(expiry.minusNanos(1), ZoneOffset.UTC), dispatcher)
        val atExpiry = OrderProcessor(api, store, Clock.fixed(expiry, ZoneOffset.UTC), dispatcher)

        assertEquals("PROCESSED", before.process("order-1"))
        assertEquals("EXPIRED", atExpiry.process("order-2"))
        assertEquals(listOf("order-1" to "PROCESSED", "order-2" to "EXPIRED"), writes)
    }
}
