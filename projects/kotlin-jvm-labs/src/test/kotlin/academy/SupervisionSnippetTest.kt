package academy

import interviewlab.cor_11.loadCards
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.awaitCancellation
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class SupervisionSnippetTest {
    @Test
    fun oneCardFailureStillReturnsOtherCard() = runBlocking {
        val cards = loadCards(
            profile = { "Ada" },
            offers = { throw IllegalStateException("offers unavailable") }
        )
        assertEquals("Ada", cards.profile.getOrNull())
        assertTrue(cards.offers.isFailure)
        assertEquals("offers unavailable", cards.offers.exceptionOrNull()?.message)
    }

    @Test
    fun cancellingParentCancelsBothLoaders() = runBlocking {
        val profileStarted = CompletableDeferred<Unit>()
        val offersStarted = CompletableDeferred<Unit>()
        val profileCleaned = AtomicBoolean()
        val offersCleaned = AtomicBoolean()
        val parent = launch {
            loadCards(
                profile = {
                    profileStarted.complete(Unit)
                    try { awaitCancellation() } finally { profileCleaned.set(true) }
                },
                offers = {
                    offersStarted.complete(Unit)
                    try { awaitCancellation() } finally { offersCleaned.set(true) }
                }
            )
        }
        profileStarted.await()
        offersStarted.await()
        parent.cancelAndJoin()
        assertTrue(parent.isCancelled)
        assertTrue(profileCleaned.get())
        assertTrue(offersCleaned.get())
    }
}
