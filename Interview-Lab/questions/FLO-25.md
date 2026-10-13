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

تصميم شريط بحث (Search Box) احترافي يجمع بين الـ Debounce وإلغاء الطلبات القديمة (Cancelling stale API calls) هو أحد أهم الأسئلة المعمارية العملية:

1. المتطلبات الهندسية لشريط البحث المثالي:
   - **تأخير الإرسال (Debounce):** لا نرسل طلب شبكة مع كل حرف يكتبه المستخدم؛ ننتظر 300ms حتى يتوقف عن الكتابة.
   - **منع التكرار (Deduplication):** لو مسح المستخدم حرفاً وأعاده فوراً في أقل من 300ms، لا نكرر نفس البحث.
   - **إلغاء الطلبات البطيئة السابقة (Stale Request Cancellation):** لو تم إرسال طلب للبحث عن 'App' واستغرق وقتاً طويلاً، ثم كتب المستخدم 'Apple'، يجب **إلغاء طلب 'App' فوراً** حتى لا تعود نتيجته متأخرة وتمسح شاشة نتائج 'Apple' (Race condition)!
   - **معالجة النصوص الفارغة (Empty Query):** مسح النتائج فوراً دون إرسال طلب للسيرفر.

2. التركيبة المعمارية الثلاثية:
   - `debounce(300L)`
   - `distinctUntilChanged()`
   - `flatMapLatest { query -> ... }`

## Practical walkthrough

تنفيذ كامل للـ Search Pipeline في ViewModel:
```kotlin
class SearchViewModel(
    private val searchRepository: SearchRepository
) : ViewModel() {

    val queryFlow = MutableStateFlow("")

    val searchState: StateFlow<SearchUiState> = queryFlow
        .map { it.trim() } // 1. تنظيف الفراغات
        .debounce(300L)   // 2. تأخير 300ms للانتظار بعد انتهاء الكتابة
        .distinctUntilChanged() // 3. تجاهل الكلمات المكررة المتتالية
        .flatMapLatest { query -> // 4. يلغي الطلب القديم المعلق فوراً بمجرد وصول كلمة جديدة
            if (query.isBlank()) {
                flowOf(SearchUiState.Idle)
            } else {
                searchRepository.searchProducts(query)
                    .map { SearchUiState.Success(it) }
                    .onStart { emit(SearchUiState.Loading) }
                    .catch { emit(SearchUiState.Error(it.message ?: "Error")) }
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000L),
            initialValue = SearchUiState.Idle
        )
}
```

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

Design the search pipeline using query.map { it.trim() }.debounce(300).distinctUntilChanged().flatMapLatest { query -> repository.search(query) }. flatMapLatest guarantees that any in-flight, stale network call is immediately cancelled the moment a new query arrives.

## Interview answer — structured

To build a responsive search pipeline that debounces input and cancels stale API calls, I chain four essential Flow operators in the ViewModel:

1. **`map { it.trim() }`**: Sanitizes whitespace to avoid trivial variations.
2. **`debounce(300L)`**: Waits for a 300ms quiet period after the user stops typing, preventing rapid keystroke storms.
3. **`distinctUntilChanged()`**: Prevents redundant search dispatches if the query string after trimming equals the previous search.
4. **`flatMapLatest { query -> ... }`**: This is the critical cancellation operator. If a query 'A' is sent and takes 800ms, and the user types 'AB' at 500ms, `flatMapLatest` immediately cancels the ongoing HTTP call for 'A' via cooperative cancellation, executing the fresh search for 'AB' instead. This completely eliminates out-of-order response race conditions.

## Interview answer — deep senior

From an API optimization and networking standpoint, `flatMapLatest` cancels the OkHttp Call at the network layer if OkHttp's asynchronous enqueue or Coroutine bridge is used, terminating the underlying socket read loop and saving device radio battery.

Inside `flatMapLatest`, we wrap the repository call with: `.onStart { emit(SearchUiState.Loading) }` and `.catch { emit(SearchUiState.Error(...)) }`. This encapsulates the entire asynchronous lifecycle of each individual query cleanly within the inner flow.

Finally, pairing this with `stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), SearchUiState.Idle)` ensures that if the user rotates the device, the current search results are retained instantly from the `StateFlow`'s cache without re-triggering the network query.

## How to answer in the interview

- **Why:** keep typing instant while reducing obsolete requests.
- **How:** normalize, debounce, distinct, latest search, query-tagged state.
- **Trade-off:** request latency versus network load.
- **Failure case:** old response overwrites current query.
- **Production solution:** inverted-delay tests and lifecycle collection.

## Deep-dive talking points

Trace query generation, stale response race, lifecycle sharing and error/cancellation split.

## Follow-up questions

- **Interviewer:** "What happens if the network API returns responses out of order without `flatMapLatest`?"
  **Answer:** "If query 'A' is slow (takes 2s) and query 'AB' is fast (takes 200ms), without `flatMapLatest`, 'AB' will render first, and 1.8 seconds later 'A' will arrive and overwrite the screen with stale results! `flatMapLatest` completely prevents this."

- **Interviewer:** "How do you handle immediate searches when the user taps the search keyboard button?"
  **Answer:** "Expose an `onSearchSubmitted(query)` method in the ViewModel that directly updates an active query without going through the debounce delay."

- **Interviewer:** "Can you test this search pipeline deterministically in a unit test?"
  **Answer:** "Yes, using `runTest` and Turbine. Emit 'A', call `advanceTimeBy(100)`, emit 'AB', call `advanceTimeBy(300)`, and verify that only the search for 'AB' was dispatched."

## Self-check rubric

Can I define pipeline order, guard late responses, model all UI states and test virtual timing?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — debounce/flatMapLatest.
- [Android StateFlow/SharedFlow guide](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) — ViewModel UI state.

Technically reviewed against primary documentation on 2026-10-13.
