package academy

import interviewlab.pat_17.IsSignedIn
import interviewlab.pat_17.SessionStore
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class SessionOwnershipSnippetTest {
    @Test
    fun separateOwnersDoNotShareSessionState() {
        val first = SessionStore()
        val second = SessionStore()
        first.update("Ada")
        assertTrue(IsSignedIn(first).check())
        assertFalse(IsSignedIn(second).check())
    }

    @Test
    fun explicitLogoutClearsTheChosenOwner() {
        val store = SessionStore("Ada")
        assertTrue(IsSignedIn(store).check())
        store.update(null)
        assertFalse(IsSignedIn(store).check())
    }
}
