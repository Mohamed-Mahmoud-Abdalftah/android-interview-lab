package academy

import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.async
import kotlinx.coroutines.delay
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

@OptIn(ExperimentalCoroutinesApi::class)
class CompletionModelsTest {
    @Test fun `supervision preserves sibling result and captures failure`() = runTest {
        val result = supervisedBatch(listOf({ 7 }, { error("remote failed") }, { 11 }))
        assertEquals(listOf(7, null, 11), result.map { it.value })
        assertEquals("remote failed", result[1].error)
    }

    @Test fun `supervision does not turn parent cancellation into data`() = runTest {
        val operation = async { supervisedBatch(listOf({ delay(Long.MAX_VALUE); 1 })) }
        runCurrent()
        operation.cancel()
        try {
            operation.await()
            fail("Cancellation must be observable by the caller")
        } catch (_: CancellationException) {
            assertTrue(operation.isCancelled)
        }
    }

    @Test fun `cooperative batch boundary returns only completed batches`() {
        assertEquals((1..6).toList(), cooperativeBatches((1..10).toList(), 3, 2))
        assertThrows(IllegalArgumentException::class.java) { cooperativeBatches(listOf(1), 0, 1) }
    }

    @Test fun `stream contract distinguishes state event and cold query`() {
        assertEquals(StreamKind.State, chooseStreamKind(true, true))
        assertEquals(StreamKind.Event, chooseStreamKind(false, true))
        assertEquals(StreamKind.Query, chooseStreamKind(false, false))
    }

    @Test fun `stale completion cannot overwrite newest request`() {
        assertNull(newestResult(9, VersionedResult(8, "old")))
        assertEquals("new", newestResult(9, VersionedResult(9, "new")))
    }

    @Test fun `deterministic queue runs snapshot and leaves nested task`() {
        val queue = DeterministicQueue(); val trace = mutableListOf<String>()
        queue.enqueue { trace += "first"; queue.enqueue { trace += "nested" } }
        queue.enqueue { trace += "second" }
        queue.runCurrent()
        assertEquals(listOf("first", "second"), trace); assertEquals(1, queue.size)
        queue.runCurrent(); assertEquals(listOf("first", "second", "nested"), trace)
    }

    @Test fun `saved state wins over durable fallback and invalid tab is safe`() {
        assertEquals(RestoredEditor("memory", 2), restoreEditor(mapOf("draft" to "memory", "tab" to "2"), "disk"))
        assertEquals(RestoredEditor("disk", 0), restoreEditor(mapOf("tab" to "bad"), "disk"))
    }

    @Test fun `intent policy requires exact trusted immutable shape`() {
        assertTrue(acceptsReturnIntent(IntentEnvelope("academy.PAYMENT_RETURN", "https", "pay.academy.example", true)))
        assertFalse(acceptsReturnIntent(IntentEnvelope("academy.PAYMENT_RETURN", "javascript", "pay.academy.example", true)))
        assertFalse(acceptsReturnIntent(IntentEnvelope("academy.PAYMENT_RETURN", "https", "evil.example", true)))
    }

    @Test fun `work chooser makes durability and user visibility explicit`() {
        assertEquals(WorkMechanism.FOREGROUND_SERVICE, chooseWorkMechanism(true, true, true))
        assertEquals(WorkMechanism.EXPEDITED_WORK, chooseWorkMechanism(false, true, true))
        assertEquals(WorkMechanism.DURABLE_WORK, chooseWorkMechanism(false, true, false))
        assertEquals(WorkMechanism.IN_PROCESS, chooseWorkMechanism(false, false, false))
    }

    @Test fun `short lived owner cannot retain shorter dependency`() {
        assertTrue(dependencyScopeIsSafe(ScopeLevel.SCREEN, ScopeLevel.SINGLETON))
        assertFalse(dependencyScopeIsSafe(ScopeLevel.SINGLETON, ScopeLevel.SCREEN))
    }

    @Test fun `single top compares full typed route`() {
        val stack = listOf(Route("list"), Route("detail", "7"))
        assertSame(stack, reduceBackStack(stack, Route("detail", "7"), true))
        assertEquals(3, reduceBackStack(stack, Route("detail", "8"), true).size)
    }

    @Test fun `retry requires safe semantics and caps exponential delay`() {
        assertEquals(RetryDecision(false, 0, "unsafe-operation"), retryDecision("POST", 0, null, false))
        assertEquals(RetryDecision(true, 250, null), retryDecision("POST", 0, 503, true))
        assertEquals(RetryDecision(false, 0, "non-retryable-status"), retryDecision("GET", 0, 401, false))
        assertEquals(RetryDecision(false, 0, "attempt-limit"), retryDecision("GET", 4, 503, false))
    }

    @Test fun `minimum path sum uses right and down recurrence`() {
        assertEquals(7, minPathSum(listOf(listOf(1, 3, 1), listOf(1, 5, 1), listOf(4, 2, 1))))
        assertThrows(IllegalArgumentException::class.java) { minPathSum(emptyList()) }
    }

    @Test fun `note conflict uses revision then deterministic device tie break`() {
        val a = NoteVersion("n", "local", 4, "a")
        val b = NoteVersion("n", "remote", 5, "b")
        assertEquals(b, resolveNoteConflict(a, b))
        assertEquals(b.copy(revision = 4), resolveNoteConflict(a, b.copy(revision = 4)))
    }

    @Test fun `refresh result cannot revive unrelated session state`() {
        assertEquals(SessionState.Active("a", "new"), reduceRefresh(SessionState.Refreshing("a"), "new"))
        assertEquals(SessionState.ReauthenticationRequired("a"), reduceRefresh(SessionState.Refreshing("a"), null))
        assertEquals(SessionState.SignedOut, reduceRefresh(SessionState.SignedOut, "unexpected"))
    }

    @Test fun `incident action favors rollback for material regression`() {
        assertEquals(IncidentAction.ROLLBACK, incidentAction(1.1, false, true))
        assertEquals(IncidentAction.MITIGATE, incidentAction(0.3, false, false))
        assertEquals(IncidentAction.KEEP_INVESTIGATING, incidentAction(0.01, false, true))
    }

    @Test fun `release gate requires every blocking signal`() {
        assertTrue(releaseAllowed(ReleaseSignals(true, true, 0.1, false)))
        assertFalse(releaseAllowed(ReleaseSignals(true, false, 0.1, false)))
        assertFalse(releaseAllowed(ReleaseSignals(true, true, 0.7, false)))
        assertFalse(releaseAllowed(ReleaseSignals(true, true, 0.1, true)))
    }
}
