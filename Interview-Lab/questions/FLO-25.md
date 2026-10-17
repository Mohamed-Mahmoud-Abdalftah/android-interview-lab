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

## Concept and technical explanation

Designing a reactive search input pipeline in Android requires combining user text stream observations with rate limiting, input deduplication, and eager cancellation of obsolete in-flight network requests.
When a user types into a query field, characters arrive in rapid succession. Querying remote search endpoints on every keystroke overwhelms the network layer, triggers HTTP 429 rate limits, and causes out-of-order response rendering (race conditions) where a slower response for a previous single character overwrites the results for the completed word.
The foundational architecture leverages Kotlin Flow operators: debounce introduces a temporal delay (typically 300ms) to ensure queries dispatch only after typing pauses; distinctUntilChanged filters redundant identical submissions; and flatMapLatest (or collectLatest) automatically cancels in-flight network jobs when a newer query arrives, ensuring only the freshest search result mutates UI state.

## Practical walkthrough (English)

Implementing a resilient search box with debounce and flatMapLatest:
```kotlin
class SearchViewModel(private val searchRepository: SearchRepository) : ViewModel() {
    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    @OptIn(FlowPreview::class, ExperimentalCoroutinesApi::class)
    val searchResults: StateFlow<SearchUiState> = _searchQuery
        .debounce(300L) // Pauses 300ms after last keystroke
        .map { it.trim() }
        .distinctUntilChanged() // Ignores duplicate queries
        .flatMapLatest { query ->
            flow {
                if (query.isBlank()) {
                    emit(SearchUiState.Empty)
                } else {
                    emit(SearchUiState.Loading)
                    try {
                        val results = searchRepository.search(query)
                        emit(SearchUiState.Success(results))
                    } catch (e: CancellationException) {
                        throw e // Respect cancellation!
                    } catch (e: Exception) {
                        emit(SearchUiState.Error(e.localizedMessage ?: "Unknown error"))
                    }
                }
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = SearchUiState.Empty
        )

    fun onQueryChanged(newQuery: String) {
        _searchQuery.value = newQuery
    }
}
```

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

We observe search input via StateFlow, applying debounce(300L) to throttle keystrokes and distinctUntilChanged to discard identical inputs. We then chain flatMapLatest to cancel in-flight network requests immediately when newer input arrives, converting results into UI state via stateIn.

## Interview answer — structured

Designing a robust search box requires managing input frequency, query sanitization, and request concurrency.

Emitting network requests on every keystroke creates severe race conditions and exhausts bandwidth. We buffer raw text emissions inside a MutableStateFlow and route them through debounce with a 300-millisecond threshold, preventing premature dispatches while the user types.

In production, we sanitize the stream by trimming whitespace and chaining distinctUntilChanged, preventing redundant network roundtrips if the user types and immediately deletes a trailing space.
As for concurrency management, flatMapLatest represents the pivotal operator. When a new sanitized query passes the debounce threshold, flatMapLatest automatically cancels the coroutine executing the previous in-flight HTTP request before launching the new query, ensuring out-of-order network responses never corrupt current UI search results.


## Interview answer — deep senior

Under the hood in kotlinx.coroutines.flow, flatMapLatest is an alias for transformLatest, implemented via ChannelFlow. When an upstream query arrives, transformLatest immediately cancels the previous downstream child coroutine by throwing a CancellationException through the coroutine hierarchy.
This eager cancellation relies on cooperative cancellation within the underlying networking client. For OkHttp and Retrofit, coroutine cancellation automatically invokes Call.cancel(), cleanly terminating the underlying TCP socket write and socket read loops. This prevents backend server saturation and halts unnecessary payload decoding.
A critical architectural consideration is managing empty and short queries. If a user clears the search field, emitting an empty string into flatMapLatest must immediately yield an Empty UI state without invoking the network repository. Furthermore, exceptions inside the search flow must be trapped within the flatMapLatest inner flow rather than upstream; catching errors upstream would terminate the entire search stream permanently, rendering the search box unresponsive to subsequent keystrokes.
In enterprise multi-module applications, senior engineers encapsulate this search pipeline inside a dedicated domain UseCase or repository query stream. By separating raw UI text binding from asynchronous query transformations, the search pipeline becomes fully unit-testable using TestScope and Turbine without coupling to Android framework classes.
Staff engineers enforce state preservation and lifecycle safety: wrapping the pipeline in stateIn with SharingStarted.WhileSubscribed(5000) guarantees that active searches survive screen orientation changes while pausing background network polling when the user switches apps.

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
