---
id: "FLO-25"
question: "Design a search box that debounces input and cancels stale API calls."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "C"
phase: 1
priority: "P1"
order: 138
editorial_status: "reviewed"
---

# FLO-25

## Original interview question

Design a search box that debounces input and cancels stale API calls.

## What the interviewer evaluates

Design debounced search with stale-request cancellation, query ownership and UI state.

## Explanation in Arabic

نحفظ text كـStateFlow في ViewModel، نعمل normalize ثم debounce ثم distinct، وبعدها `flatMapLatest` لنتائج query الحالية. blank query تعرض اقتراحات/empty state متعمدة. كل emission تحمل query أو generation علشان UI ما تعرضش نتيجة قديمة لو client تجاهل cancel. Network errors تبقى state مرتبطة بالquery، و`CancellationException` ما تتحولش error.

### Practical walkthrough in Egyptian Arabic

الـTextField تتحدث فورًا من `query`، لكن API request تتأخر `debounce(250)` بعد آخر حرف. `distinctUntilChanged` بعد normalization تمنع نفس بحث يتكرر؛ `flatMapLatest` تلغي collection القديمة، وstate تعرض Loading/Ready/Error للquery الحالية. لو backend request ما بتتلغيش فعليًا، tag كل response بـquery وتأكد قبل commit عشان نتيجة `a` ما تغطيش `ab`.

## Why it matters and how it works

`flatMapLatest` cancels prior inner collection, but an HTTP request already sent may still consume server resources or complete. A cancellable client plus query ID guard protects UI consistency. Expose one StateFlow so multiple composables do not repeat a cold network source.

## Worked example

Conceptual ViewModel pipeline; `SearchState`, `api.search`, and `SearchApi` are application types with main-safe suspend contract.

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.FlowPreview
import kotlinx.coroutines.flow.*

sealed interface SearchState {
    data object Empty : SearchState
    data class Loading(val query: String) : SearchState
    data class Ready(val query: String, val items: List<String>) : SearchState
    data class Error(val query: String, val message: String) : SearchState
}
interface SearchApi { suspend fun search(query: String): List<String> }

@OptIn(FlowPreview::class, ExperimentalCoroutinesApi::class)
class SearchViewModel(private val api: SearchApi) : ViewModel() {
    private val query = MutableStateFlow("")
    val queryText = query.asStateFlow() // field updates immediately
    val results: StateFlow<SearchState> = query.map(String::trim).debounce(300)
        .distinctUntilChanged()
        .flatMapLatest { q ->
            if (q.isEmpty()) flowOf<SearchState>(SearchState.Empty)
            else flow<SearchState> {
                emit(SearchState.Loading(q))
                emit(SearchState.Ready(q, api.search(q)))
            }.catch { e ->
                if (e is CancellationException) throw e
                emit(SearchState.Error(q, "Search failed"))
            }
        }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), SearchState.Empty)
    fun setQuery(value: String) { query.value = value }
}
// Keep old server work idempotent; test late responses and cancellation.
```

## Trade-offs and decision criteria

Debounce reduces requests but delays first remote result; local suggestions can remain immediate. Latest-only is safe for replaceable search views, not required writes. Sharing prevents duplicate API calls across UI collectors but introduces scope/freshness choices.

## Failure modes

A non-cooperative client may return after cancellation; do not publish if query/generation no longer matches. Catching cancellation as Error creates a stale banner. Rapid rotation can restart upstream unless stateIn grace policy covers it.

## Production perspective

A marketplace search screen emits typed Loading/Ready/Error per query, logs request count and latency, and caches recent results. Tests type rapidly with virtual time, force an old response after a new one and check no stale render.

## Interview answer — short

“I normalize and debounce query input, suppress adjacent duplicates and use flatMapLatest for replaceable results. I expose one ViewModel StateFlow, tag results with query identity and preserve cancellation so stale responses cannot overwrite current UI.”

## Interview answer — structured

“The ViewModel owns query state. Its pipeline normalizes input, debounces remote calls, applies distinctUntilChanged and switches inner search streams with flatMapLatest. Empty input has an explicit state. I model loading, result and error with the query that produced them, so a late old result is rejected even if the network client does not promptly cancel. The UI collects lifecycle-aware and the ViewModel shares upstream to avoid duplicate requests. Tests advance virtual time and deliver responses out of order.”

## Interview answer — deep senior

“Search is a latest-state problem, so discarding old results is correct, but implementation details matter. I keep immediate text rendering separate from a debounced network path, normalize before equality filtering, and switch to a new cancellable request when the query changes. A request may already be on the wire; therefore I tag every result with the originating query or generation and refuse to commit it if it no longer matches the current input. Expected API failures map to query-scoped error state, while CancellationException propagates. I share the final stream in viewModelScope with a policy that avoids duplicate collectors, bound API load and measure latency. Tests cover rapid typing, duplicate queries, blank input, slow old response, rotation and cancellation. I would separate input responsiveness from network policy. The ViewModel accepts every character immediately and exposes it to the field. A separate query pipeline normalizes, debounces, removes consecutive duplicates, and uses `flatMapLatest` for repository search so old inner collections are cancelled. The UI receives an explicit Loading/Ready/Error state carrying the query identity. Cancellation may stop client observation but may not undo remote server work, so I also check that a late result belongs to the current query before committing it if the adapter is not fully cancellable. I would choose the debounce interval with product input latency in mind and test rapid `a` to `ab`, empty query, error recovery, and screen recreation.”

## How to answer in the interview

- **Why:** keep typing instant while reducing obsolete requests.
- **How:** normalize, debounce, distinct, latest search, query-tagged state.
- **Trade-off:** request latency versus network load.
- **Failure case:** old response overwrites current query.
- **Production solution:** inverted-delay tests and lifecycle collection.

## Deep-dive talking points

Trace query generation, stale response race, lifecycle sharing and error/cancellation split.

## Follow-up questions

- [FLO-15](../flo-15/): Why normalize before distinct? **Answer:** semantically equal queries should not repeat requests.
- [FLO-14](../flo-14/): Which operator replaces old inner flow? **Answer:** flatMapLatest.

## Self-check rubric

Can I define pipeline order, guard late responses, model all UI states and test virtual timing?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — debounce/flatMapLatest.
- [Android StateFlow/SharedFlow guide](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) — ViewModel UI state.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
