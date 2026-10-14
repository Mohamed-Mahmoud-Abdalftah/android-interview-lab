---
id: "SYS-21"
question: "Design a Home screen that relies on 3 independent services with partial failure."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "C"
phase: 4
priority: "P1"
order: 350
editorial_status: "reviewed"
---

# SYS-21

## Original interview question

Design a Home screen that relies on 3 independent services with partial failure.

## What the interviewer evaluates

Design Home with three independent services and partial failures without swallowing cancellation.

## Explanation in Arabic

كيف تصمم شاشة رئيسية (Home Screen) تعتمد على 3 خدمات مستقلة وتدعم الفشل الجزئي (Partial Failure) دون تعطل الشاشة بالكامل؟

1. خطأ التصميم الكارثي (The All-or-Nothing Anti-Pattern):
   - استخدام `zip` أو `awaitAll` لدمج استجابات الخدمات الثلاث (مثلاً: Stories API, Feed API, Recommendations API).
   - **المشكلة**: إذا فشلت خدمة التوصيات (Recommendations) أو استغرقت 10 ثوانٍ، فإن الشاشة بالكامل تفشل وتعرض شاشة بيضاء أو رسالة خطأ، وتمنع المستخدم من رؤية الـ Feed والـ Stories الأساسية!

2. المعمارية السليمة: العزل التام والتراجع المتدرج (Graceful Degradation):
   - **استقلالية الجلب (Independent Concurrent Fetching)**: جلب بيانات كل خدمة في Coroutine مستقل مع عزل الأخطاء عبر `runCatching`.
   - **تمثيل الحالة المنفصل (Independent State Streams)**: كل ميزة تمتلك حالة خاصة بها:
     `storiesState: StateFlow<SectionState<List<Story>>>`,
     `feedState: StateFlow<SectionState<List<Post>>>`,
     `recommendationsState: StateFlow<SectionState<List<Recommendation>>>`.
   - **التراجع للكاش المحلي (Cache Fallback)**: إذا فشلت خدمة الـ Feed عبر الإنترنت، يتم عرض آخر بيانات مخزنة محلياً من الـ Room DB مع علامة صغيرة توضح أن البيانات غير محدثة.
   - **واجهة مستخدم مرنة في Compose**: تعرض الـ Stories والـ Feed بشكل طبيعي، بينما تعرض خانة الـ Recommendations زراً صغيراً لإعادة المحاولة (Inline Retry) أو تخفي القسم بهدوء دون إفساد تجربة المستخدم.

## Practical walkthrough

تنفيذ تجميع مرن ومقاوم للفشل الجزئي لثلاث خدمات مستقلة في ViewModel و Compose:
```kotlin
sealed interface SectionState<out T> {
    object Loading : SectionState<Nothing>
    data class Success<T>(val data: T) : SectionState<T>
    data class Error(val message: String, val cachedFallback: Boolean = false) : SectionState<Nothing>
}

data class HomeUiState(
    val banners: SectionState<List<Banner>> = SectionState.Loading,
    val feedItems: SectionState<List<FeedItem>> = SectionState.Loading,
    val recommendations: SectionState<List<Recommendation>> = SectionState.Loading
)

class HomeViewModel @Inject constructor(
    private val bannerRepo: BannerRepository,
    private val feedRepo: FeedRepository,
    private val recsRepo: RecommendationsRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    fun loadHomeScreenData() {
        // 1. جلب Banners بشكل مستقل مع عزل الخطأ
        viewModelScope.launch {
            bannerRepo.getBanners()
                .onSuccess { data -> _uiState.update { it.copy(banners = SectionState.Success(data)) } }
                .onFailure { _uiState.update { it.copy(banners = SectionState.Error("Could not load banners")) } }
        }

        // 2. جلب الـ Feed بشكل مستقل
        viewModelScope.launch {
            feedRepo.getFeedStream().collect { feed ->
                _uiState.update { it.copy(feedItems = SectionState.Success(feed)) }
            }
        }

        // 3. جلب الـ Recommendations بشكل مستقل؛ الفشل هنا لا يؤثر إطلاقاً على الـ Feed أو الـ Banners!
        viewModelScope.launch {
            recsRepo.getRecommendations()
                .onSuccess { recs -> _uiState.update { it.copy(recommendations = SectionState.Success(recs)) } }
                .onFailure { _uiState.update { it.copy(recommendations = SectionState.Error("Recommendations unavailable")) } }
        }
    }
}
```

## Why it matters and how it works

Start calls concurrently under a ViewModel-owned suspend operation, capture domain failures inside each child and await all. Parent cancellation still cancels supervised children. State model has per-card Loading/Ready/Error/Stale, and retries target only failed dependencies. Bound fan-out/timeouts per service.

## Worked example

Kotlin/JVM conceptual aggregator; services return independent strings and shared `outcome` preserves cancellation.

```kotlin
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.async
import kotlinx.coroutines.supervisorScope

suspend fun <T> outcome(call: suspend () -> T): Result<T> =
    try { Result.success(call()) }
    catch (e: CancellationException) { throw e }
    catch (e: Exception) { Result.failure(e) }
suspend fun home(a: suspend () -> String, b: suspend () -> String,
                 c: suspend () -> String) = supervisorScope {
    listOf(a, b, c).map { call -> async { outcome(call) } }.map { it.await() }
}
```

## Trade-offs and decision criteria

Partial success improves resilience but increases UI/error complexity and can hide a dependency outage unless measured. All-or-nothing is better if cards jointly form one valid quote. Cached fallback needs freshness label, not silent stale success.

## Failure modes

Using ordinary coroutineScope may cancel all three on one child failure. Bare runCatching can swallow cancellation. A failed card retried with an unbounded loop can overload service. Returning a Home success flag conceals partial outage.

## Production perspective

A commerce Home loads offers, order status and support tips independently, each with its own state and targeted retry. A server correlation ID and per-card metrics identify outages; process death rebuilds from cached Room snapshots.

## Interview answer — short

Design aggregate screens for partial failure by fetching independent services concurrently using isolated supervisor scopes with cancellation-preserving error handling. Represent sections with independent state streams in a unified UI state, fall back to local cached data where available, and render inline section retries without blocking or failing the entire screen.

## Interview answer — structured

Aggregating multiple microservices into a single mobile dashboard requires defensive concurrency and resilient UI state composition.

First, **Avoid All-or-Nothing Composition**. Next, combining calls via `zip`, `combine` with synchronous throws, or `awaitAll` creates an all-or-nothing anti-pattern. If a non-essential service (e.g. Recommendations) throws a 500 or times out, the entire screen fails.
**Independent Section Concurrency**. Launch three independent coroutine jobs within a supervisory scope (`supervisorScope`), capturing exceptions while strictly preserving `CancellationException`. If the Recommendations service fails, its exception is caught in isolation, allowing the Feed and Hero Banners to load and render immediately.
**Modular State Modeling**. Model the overall screen state as an aggregate data class holding individual `SectionState<T>` wrappers (`Loading`, `Success`, `Error`). Compose renders each section according to its discrete state.
**Graceful UI Degradation & Cache Fallbacks**. Finally, if a service fails, check Room persistence for cached records. If cached data exists, render it with a subtle 'Offline' chip. If no cache exists, render an inline retry placeholder or cleanly collapse the section without breaking the parent layout.


## Interview answer — deep senior

From a staff-level systems perspective, partial failure resilience extends into network protocol design and backend orchestration.

First, with Backend-for-Frontend (BFF) vs. Client Aggregation, in enterprise architectures, mobile clients should ideally query a single mobile BFF gateway. The BFF aggregates the 3 microservices concurrently on high-speed datacenter backbones. If recommendations time out within 150ms, the BFF returns a partial JSON payload containing banners and feed items along with a partial-error metadata flag, saving mobile battery and round-trips. Next, with Independent Section Pull-to-Refresh, when the user performs a pull-to-refresh gesture, trigger refresh jobs across all three sections concurrently. Keep already-rendered cached content on screen while refreshing, transitioning sections to loading indicators only if no data was previously visible.
Finally, with Targeted Telemetry & Alerting, log individual endpoint failure rates. If Recommendations fail for 15% of sessions while Core Feed succeeds, telemetry surfaces microservice-specific degradation rather than generic app-level crash alarms.


## How to answer in the interview

- **Why:** independent widgets can provide value through partial failure.
- **How:** supervise direct children and publish per-card typed outcomes with freshness.
- **Trade-off:** more UI states and retry controls add complexity.
- **Failure case:** swallowing cancellation or showing stale data as fresh.
- **Production solution:** source-specific retry, monitoring, and parent-cancellation tests.

## Deep-dive talking points

Compare independent card semantics with all-or-nothing quote and test cancellation.

## Follow-up questions

- **Interviewer:** "What is SupervisorJob and why is it useful when fetching multiple independent services?"
  **Answer:** "A SupervisorJob ensures that failure in one child coroutine does not automatically cancel its sibling coroutines or the parent scope."

- **Interviewer:** "How should Compose handle an empty state versus an error state in a lazy list section?"
  **Answer:** "An empty state displays a friendly empty graphic or collapses gracefully; an error state provides an inline error message with a dedicated section retry button."

## Self-check rubric

Can I show three outcomes, preserve cancellation and avoid masking an outage?

## References and reviewed-on date

- [Kotlin exception handling](https://kotlinlang.org/docs/exception-handling.html) — supervision.
- [Android UI architecture](https://developer.android.com/topic/architecture/ui-layer) — state holders.

Technically reviewed against primary documentation on 2026-10-13.
