---
id: "FLO-15"
question: "Explain debounce and distinctUntilChanged for search."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 128
editorial_status: "reviewed"
---

# FLO-15

## Original interview question

Explain debounce and distinctUntilChanged for search.

## What the interviewer evaluates

Explain debouncing and equality suppression for search without promising cancellation of server work.

## Explanation in Arabic

المشغلان `debounce` و `distinctUntilChanged` هما الثنائي الكلاسيكي لبناء مربع بحث (Search Box) فائق الكفاءة والسرعة:

1. المشغل `debounce(timeoutMillis)`:
   - يؤخر تمرير العنصر حتى يمر وقت محدد (مثلاً 300ms) **بدون أن يصدر الـ Upstream أي عنصر جديد**.
   - **لماذا في البحث؟** المستخدم عندما يكتب كلمة 'Android'، يضغط على 7 أزرار في أقل من ثانية. بدون debounce، التطبيق سيرسل 7 طلبات شبكة للسيرفر! مع `debounce(300L)`، التطبيق ينتظر حتى يتوقف المستخدم عن الكتابة لمدة 300ms ثم يرسل طلباً واحداً فقط بالكلمة النهائية.

2. المشغل `distinctUntilChanged()`:
   - يقمع ويتجاهل العنصر الجديد **إذا كان مطابقاً للعنصر السابق مباشرة** (بالمقارنة بـ `equals()`).
   - **لماذا في البحث؟** لو المستخدم كتب 'Kotlin'، ثم مسح حرف الـ 'n' ثم أعاد كتابته بسرعة في أقل من 300ms، النص النهائي لا يزال 'Kotlin'! المشغل `distinctUntilChanged()` يكتشف أن النص لم يتغير ويتجاهل إرسال طلب شبكة مكرر للسيرفر.

## Practical walkthrough

الكود المعماري المثالي لشريط البحث في ViewModel:
```kotlin
class SearchViewModel(private val repository: SearchRepository) : ViewModel() {
    val searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<SearchResultsUiState> = searchQuery
        .map { it.trim() } // 1. تنظيف المسافات الزائدة
        .debounce(300L)   // 2. الانتظار 300ms بعد توقف المستخدم عن الكتابة
        .distinctUntilChanged() // 3. منع تكرار البحث لو النص مطابق للسابق
        .flatMapLatest { query ->
            if (query.isEmpty()) {
                flowOf(SearchResultsUiState.Empty)
            } else {
                repository.search(query)
                    .map { SearchResultsUiState.Success(it) }
                    .catch { emit(SearchResultsUiState.Error(it.message ?: "Error")) }
            }
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000L), SearchResultsUiState.Empty)
}
```

## Why it matters and how it works

Order matters: trim/normalize before distinct, debounce before expensive search, then switch latest. Debounce uses time and may delay perceived responsiveness; immediate local suggestions can be separate. `distinctUntilChanged` compares adjacent values, not a cache of all past queries.

## Worked example

JVM/Android-compatible snippet with Flow input and cancellable repository search Flow; coroutines-core is required.

```kotlin
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.FlowPreview
import kotlinx.coroutines.flow.*

@OptIn(FlowPreview::class, ExperimentalCoroutinesApi::class)
fun searchResults(
    typed: Flow<String>,
    search: (String) -> Flow<List<String>>,
): Flow<List<String>> = typed
    .map { it.trim() }
    .debounce(300)
    .distinctUntilChanged()
    .flatMapLatest { q -> if (q.isBlank()) flowOf(emptyList()) else search(q) }
```

## Trade-offs and decision criteria

A 300 ms debounce reduces calls but adds latency; tune with usage metrics. Distinct prevents adjacent duplicates but does not replace response caching. Latest-only results fit search, not required writes. Show local results immediately if UX needs fast feedback.

## Failure modes

Applying distinct before normalization sends duplicate equivalent queries. A non-cooperative search client may complete after cancellation; the flow should still avoid publishing stale results to UI. Collecting twice may trigger duplicate requests if not shared.

## Production perspective

A catalog ViewModel holds query state, applies the pipeline, exposes StateFlow of loading/results/error, and collects with lifecycle awareness. Tests use virtual time to type rapidly, pause, repeat query and deliver a slow old response.

## Interview answer — short

debounce pauses emission until a specified quiet period (e.g., 300ms) elapses with no new input, throttling rapid typing; distinctUntilChanged filters out emissions that equal the immediately preceding emission, preventing duplicate search requests for identical query strings.

## Interview answer — structured

In Android search architecture, `debounce` and `distinctUntilChanged` work in tandem to eliminate redundant network traffic and improve UI responsiveness.

**`debounce(300L)`** acts as a rate limiter. When a user types rapidly on a software keyboard, an emission fires for every keystroke. `debounce` starts a timer on each character. If another keystroke arrives before 300 milliseconds elapse, the timer resets. Only when the user pauses typing for a full 300ms does the latest text emission proceed downstream.

**`distinctUntilChanged()`** acts as an equality filter. It compares the incoming value against the previously emitted value using `equals()`. If the user types 'A', quickly deletes it, and types 'A' again, the debounced text is still 'A'. `distinctUntilChanged` recognizes that the query hasn't changed and suppresses the duplicate emission, preventing a redundant network query.

## Interview answer — deep senior

Under the hood, `debounce` launches a timer coroutine on the coroutine scheduler. When a new upstream emission arrives, the previous delayed task is cancelled, and a new delayed emission is scheduled. When testing `debounce` with `runTest`, virtual time makes verification instantaneous: you can advance time by 299ms to assert no search occurred, and then call `advanceTimeBy(2)` to verify the search query triggered.

With `distinctUntilChanged()`, the operator maintains a reference to the previous emission in memory. You can also provide a custom key selector: `distinctUntilChangedBy { it.id }` or a custom comparison lambda. Pairing this pipeline with `flatMapLatest` guarantees that even if a debounced search query is sent, if the user starts typing again while the backend is responding, the stale network call is immediately cancelled in favor of the newer query.

## How to answer in the interview

- **Why:** search requests should follow stable intent without slowing text entry.
- **How:** immediate field, normalize, debounce, distinct, latest request.
- **Trade-off:** fewer calls versus result latency.
- **Failure case:** debouncing the field or letting old results win.
- **Production solution:** test request count and rapid typing.

## Deep-dive talking points

Trace operator order, timing, stale response and query-associated UI state.

## Follow-up questions

- **Interviewer:** "Why should you call `.map { it.trim() }` before `distinctUntilChanged()`?"
  **Answer:** "Because users frequently type accidental trailing spaces. Trimming the query beforehand ensures that 'Android ' and 'Android' evaluate as equal, preventing duplicate search queries."

- **Interviewer:** "What happens if a user submits a search via the keyboard 'Enter' action?"
  **Answer:** "The 'Enter' action should bypass the debounce delay. In the ViewModel, you provide an explicit `searchImmediately()` method that immediately triggers the search without waiting for the 300ms debounce timer."

- **Interviewer:** "Does `distinctUntilChanged()` work on complex data classes?"
  **Answer:** "Yes, as long as the data class generates structural `equals()` for all properties. If custom classes are used, you must properly implement `equals()` and `hashCode()`."

## Self-check rubric

Can I justify operator order, distinguish adjacent equality from cache, and handle a late old response?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — debounce and distinctUntilChanged.

Technically reviewed against primary documentation on 2026-10-13.
