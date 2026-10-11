package academy

import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.withContext

data class ProfileCard(val name: String, val badgeCount: Int)

/** Loads two independent fields under the caller's job and an injected dispatcher. */
suspend fun loadProfileCard(
    profile: suspend () -> String,
    badges: suspend () -> Int,
    dispatcher: CoroutineDispatcher,
): ProfileCard = withContext(dispatcher) {
    coroutineScope {
        val name = async { profile() }
        val badgeCount = async { badges() }
        ProfileCard(name.await(), badgeCount.await())
    }
}
