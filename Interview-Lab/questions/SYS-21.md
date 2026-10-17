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

## Concept and technical explanation

Designing an enterprise Home screen dependent on multiple independent upstream services—such as a promotional banner service, a personalized user feed, and an algorithm-driven recommendation engine—requires an architecture that isolates partial failures. In mobile application design, a single failing or slow secondary service must never compromise the entire user experience. If the recommendation engine suffers a backend outage, the user must still view their active feed items and promotional banners. The presentation layer models screen state around independent section containers, each maintaining discrete loading, success, and error states. Concurrency must be coordinated using Kotlin Coroutines where child requests execute under a SupervisorJob or via independent async blocks wrapped in runCatching, preventing uncaught cancellations from bubbling up. Furthermore, applying the Stale-While-Revalidate caching pattern allows the UI to render cached local database entities immediately while refreshing sections asynchronously over the network.

## Practical walkthrough (English)

Implementing partial failure isolation and independent section states for a Home screen:
```kotlin
// 1. Independent sealed section state modeling partial failure per surface
sealed interface SectionState<out T> {
    data object Loading : SectionState<Nothing>
    data class Success<T>(val data: T) : SectionState<T>
    data class Error(val errorMessage: String, val cachedFallback: Boolean = false) : SectionState<Nothing>
}

// 2. Composed UI state representing the entire Home screen
data class HomeUiState(
    val banners: SectionState<List<Banner>> = SectionState.Loading,
    val feed: SectionState<List<FeedItem>> = SectionState.Loading,
    val recommendations: SectionState<List<Recommendation>> = SectionState.Loading
)

// 3. ViewModel coordinating concurrent fetches without cross-job cancellation
class HomeViewModel @Inject constructor(
    private val bannerRepo: BannerRepository,
    private val feedRepo: FeedRepository,
    private val recommendationRepo: RecommendationRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState = _uiState.asStateFlow()

    fun loadHomeScreen() = viewModelScope.launch {
        // Execute independent async jobs wrapped in runCatching to isolate failures
        val bannersDeferred = async { runCatching { bannerRepo.fetchBanners() } }
        val feedDeferred = async { runCatching { feedRepo.fetchFeed() } }
        val recommendationsDeferred = async { runCatching { recommendationRepo.fetchRecommendations() } }

        _uiState.update { current ->
            current.copy(
                banners = bannersDeferred.await().fold(
                    onSuccess = { SectionState.Success(it) },
                    onFailure = { SectionState.Error("Failed to load banners") }
                ),
                feed = feedDeferred.await().fold(
                    onSuccess = { SectionState.Success(it) },
                    onFailure = { SectionState.Error("Failed to load feed") }
                ),
                recommendations = recommendationsDeferred.await().fold(
                    onSuccess = { SectionState.Success(it) },
                    onFailure = { SectionState.Error("Recommendations unavailable") }
                )
            )
        }
    }
}
```

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

We design resilient Home screens by modeling each content area with independent loading, success, and error states. We fetch data concurrently using Kotlin Coroutines wrapped in runCatching to isolate service exceptions, showing cached local data immediately while individual failed sections display retry buttons without breaking the rest of the screen.

## Interview answer — structured

Designing a Home screen powered by multiple independent backend services requires isolating failures so that a broken endpoint never brings down the whole screen.
I structure the presentation layer around independent section states. The screen UI state does not represent a binary success or failure. Instead, each section—banners, feed, and recommendations—manages its own discrete state.
In the ViewModel, we dispatch concurrent network requests using Kotlin Coroutines async blocks governed by a SupervisorJob.
Each call is wrapped inside runCatching so that an exception in one service does not cancel sibling coroutines or trigger an unhandled failure.
We adopt a Stale-While-Revalidate caching strategy using Room. When the screen opens, it immediately renders cached data from disk.
When network responses arrive, successful sections update seamlessly, while any failing section retains its cached content and displays an inline retry action without blocking user interactions with the rest of the screen.

## Interview answer — deep senior

From a staff architecture perspective, multi-service aggregation on mobile requires defensive concurrency, selective degradation, and careful lifecycle management.
A common architectural anti-pattern is using standard coroutineScope with async when aggregating endpoints. Under standard coroutines, if the recommendation service fails with an HTTP 500, the exception automatically cancels the parent scope, aborting the feed and banner requests even if they were about to succeed. We eliminate this by utilizing supervisorScope or wrapping each async child in runCatching, ensuring failure containment.
We also introduce differential timeout budgets. User feed data is critical, so we allocate an eight-second deadline, whereas personalized recommendations are secondary and receive a strict three-second timeout. If recommendations do not respond within three seconds, the client abandons the request and collapses the section gracefully or displays popular fallbacks.
Furthermore, we prevent UI layout jank by designing skeleton placeholder loaders that match the exact aspect ratio of incoming content, preventing intrusive layout shifts when sections load at varying speeds.
To handle flaky network connections without stalling interactive rendering, each section independently tracks its own stale-while-revalidate timestamp. If the user scrolls rapidly past a failed section, the hosting recyclerview or lazy column unbinds the section view without aborting in-flight retry requests from other sections, ensuring optimal memory utilization and butter-smooth scrolling performance across legacy devices.
Finally, we implement partial refresh mechanics. When the user performs a swipe-to-refresh gesture, our state holder triggers refreshes only for stale or previously failed sections, saving bandwidth and delivering a highly responsive user experience.

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
