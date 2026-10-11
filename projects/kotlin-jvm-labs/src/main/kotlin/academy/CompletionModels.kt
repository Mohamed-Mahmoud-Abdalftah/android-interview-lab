package academy

import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.supervisorScope

data class ChildResult<T>(val value: T? = null, val error: String? = null)

suspend fun <T> supervisedBatch(tasks: List<suspend () -> T>): List<ChildResult<T>> = supervisorScope {
    tasks.map { task ->
        async {
            runCatching { task() }.fold(
                onSuccess = { ChildResult(value = it) },
                onFailure = {
                    if (it is CancellationException) throw it
                    ChildResult(error = it.message ?: it::class.simpleName.orEmpty())
                },
            )
        }
    }.awaitAll()
}

fun cooperativeBatches(items: List<Int>, batchSize: Int, cancelledAfterBatches: Int): List<Int> {
    require(batchSize > 0)
    require(cancelledAfterBatches >= 0)
    val output = mutableListOf<Int>()
    items.chunked(batchSize).take(cancelledAfterBatches).forEach(output::addAll)
    return output
}

sealed interface StreamKind { data object State : StreamKind; data object Event : StreamKind; data object Query : StreamKind }
fun chooseStreamKind(needsCurrentValue: Boolean, everySubscriberSeesFutureValues: Boolean): StreamKind = when {
    needsCurrentValue -> StreamKind.State
    everySubscriberSeesFutureValues -> StreamKind.Event
    else -> StreamKind.Query
}

data class VersionedResult<T>(val requestId: Long, val value: T)
fun <T> newestResult(currentRequestId: Long, candidate: VersionedResult<T>): T? =
    candidate.value.takeIf { candidate.requestId == currentRequestId }

class DeterministicQueue {
    private val tasks = ArrayDeque<() -> Unit>()
    fun enqueue(task: () -> Unit) { tasks.addLast(task) }
    fun runCurrent() { repeat(tasks.size) { tasks.removeFirst().invoke() } }
    val size: Int get() = tasks.size
}

data class RestoredEditor(val draft: String, val selectedTab: Int)
fun restoreEditor(saved: Map<String, String>, durableDraft: String?): RestoredEditor = RestoredEditor(
    draft = saved["draft"] ?: durableDraft.orEmpty(),
    selectedTab = saved["tab"]?.toIntOrNull()?.coerceAtLeast(0) ?: 0,
)

data class IntentEnvelope(val action: String?, val scheme: String?, val host: String?, val immutable: Boolean)
fun acceptsReturnIntent(intent: IntentEnvelope): Boolean =
    intent.action == "academy.PAYMENT_RETURN" && intent.scheme == "https" &&
        intent.host == "pay.academy.example" && intent.immutable

enum class WorkMechanism { IN_PROCESS, EXPEDITED_WORK, DURABLE_WORK, FOREGROUND_SERVICE }
fun chooseWorkMechanism(userVisibleNow: Boolean, mustSurviveRestart: Boolean, urgent: Boolean): WorkMechanism = when {
    userVisibleNow -> WorkMechanism.FOREGROUND_SERVICE
    mustSurviveRestart && urgent -> WorkMechanism.EXPEDITED_WORK
    mustSurviveRestart -> WorkMechanism.DURABLE_WORK
    else -> WorkMechanism.IN_PROCESS
}

enum class ScopeLevel(val rank: Int) { REQUEST(0), SCREEN(1), ACTIVITY(2), SINGLETON(3) }
fun dependencyScopeIsSafe(owner: ScopeLevel, dependency: ScopeLevel): Boolean = dependency.rank >= owner.rank

data class Route(val name: String, val argument: String? = null)
fun reduceBackStack(stack: List<Route>, destination: Route, singleTop: Boolean): List<Route> = when {
    singleTop && stack.lastOrNull() == destination -> stack
    else -> stack + destination
}

data class RetryDecision(val retry: Boolean, val delayMillis: Long, val terminalReason: String?)
fun retryDecision(method: String, attempt: Int, status: Int?, hasIdempotencyKey: Boolean): RetryDecision {
    require(attempt >= 0)
    val safe = method in setOf("GET", "HEAD", "PUT", "DELETE") || hasIdempotencyKey
    if (!safe) return RetryDecision(false, 0, "unsafe-operation")
    if (attempt >= 4) return RetryDecision(false, 0, "attempt-limit")
    if (status != null && status !in setOf(408, 429) && status < 500) return RetryDecision(false, 0, "non-retryable-status")
    return RetryDecision(true, (250L shl attempt).coerceAtMost(4_000L), null)
}

fun minPathSum(grid: List<List<Int>>): Int {
    require(grid.isNotEmpty() && grid.all { it.size == grid.first().size && it.isNotEmpty() })
    val dp = IntArray(grid.first().size) { Int.MAX_VALUE }
    dp[0] = 0
    for (row in grid) for (column in row.indices) {
        val best = minOf(dp[column], if (column == 0) Int.MAX_VALUE else dp[column - 1])
        dp[column] = Math.addExact(best, row[column])
    }
    return dp.last()
}

data class NoteVersion(val id: String, val text: String, val revision: Long, val deviceId: String)
fun resolveNoteConflict(local: NoteVersion, remote: NoteVersion): NoteVersion {
    require(local.id == remote.id)
    return compareValuesBy(local, remote, NoteVersion::revision, NoteVersion::deviceId).let {
        if (it >= 0) local else remote
    }
}

sealed interface SessionState {
    data object SignedOut : SessionState
    data class Active(val accountId: String, val accessToken: String) : SessionState
    data class Refreshing(val accountId: String) : SessionState
    data class ReauthenticationRequired(val accountId: String) : SessionState
}

fun reduceRefresh(state: SessionState, newToken: String?): SessionState = when (state) {
    is SessionState.Refreshing -> if (newToken == null) SessionState.ReauthenticationRequired(state.accountId)
    else SessionState.Active(state.accountId, newToken)
    else -> state
}

enum class IncidentAction { MITIGATE, ROLLBACK, KEEP_INVESTIGATING }
fun incidentAction(crashFreeDropPercent: Double, reproduced: Boolean, rollbackAvailable: Boolean): IncidentAction = when {
    crashFreeDropPercent >= 1.0 && rollbackAvailable -> IncidentAction.ROLLBACK
    crashFreeDropPercent >= 0.2 || reproduced -> IncidentAction.MITIGATE
    else -> IncidentAction.KEEP_INVESTIGATING
}

data class ReleaseSignals(val testsPass: Boolean, val migrationPass: Boolean, val crashRatePercent: Double, val securityBlocker: Boolean)
fun releaseAllowed(signals: ReleaseSignals): Boolean =
    signals.testsPass && signals.migrationPass && signals.crashRatePercent < 0.5 && !signals.securityBlocker
