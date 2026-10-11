package academy

import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.async
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

@OptIn(ExperimentalCoroutinesApi::class)
class ProfileCardTest {
    @Test
    fun parentWaitsForBothChildrenWithoutBlockingTheTestThread() = runTest {
        val profile = CompletableDeferred<String>()
        val badges = CompletableDeferred<Int>()
        val pending = async {
            loadProfileCard(
                profile = { profile.await() },
                badges = { badges.await() },
                dispatcher = StandardTestDispatcher(testScheduler),
            )
        }
        runCurrent()
        assertFalse(pending.isCompleted)
        profile.complete("Ada")
        runCurrent()
        assertFalse(pending.isCompleted)
        badges.complete(2)
        runCurrent()
        assertEquals(ProfileCard("Ada", 2), pending.await())
    }

    @Test
    fun childFailurePropagatesRatherThanReturningPartialCard() {
        assertThrows<IllegalArgumentException> {
            runTest {
                loadProfileCard(
                    profile = { throw IllegalArgumentException("bad profile") },
                    badges = { 2 },
                    dispatcher = StandardTestDispatcher(testScheduler),
                )
            }
        }
    }

    @Test
    fun cancellingParentCancelsWaitingChildren() = runTest {
        val profile = CompletableDeferred<String>()
        val badges = CompletableDeferred<Int>()
        var profileCancelled = false
        var badgesCancelled = false
        val pending = async {
            loadProfileCard(
                profile = {
                    try { profile.await() } finally { profileCancelled = true }
                },
                badges = {
                    try { badges.await() } finally { badgesCancelled = true }
                },
                dispatcher = StandardTestDispatcher(testScheduler),
            )
        }
        runCurrent()
        pending.cancel()
        runCurrent()
        assertTrue(profileCancelled)
        assertTrue(badgesCancelled)
    }
}
