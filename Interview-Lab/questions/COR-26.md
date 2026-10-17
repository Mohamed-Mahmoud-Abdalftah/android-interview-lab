---
id: "COR-26"
question: "Call 3 independent APIs concurrently. How do you preserve partial success without swallowing cancellation?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "C"
phase: 1
priority: "P1"
order: 107
editorial_status: "reviewed"
---

# COR-26

## Original interview question

Call 3 independent APIs concurrently. How do you preserve partial success without swallowing cancellation?

## What the interviewer evaluates

- Differentiating product-level partial success from coroutine-level failure isolation.
- Understanding parent/child cancellation hierarchy and why `CancellationException` must escape without being trapped.
- Designing typed outcomes, lifecycle ownership, error classification, and meaningful test assertions.
- Distinguishing independent composite UI sections from atomic transactions (such as a financial payment quote).

## Concept and technical explanation

When an application screen comprises distinct, non-critical sub-components—such as an e-commerce dashboard featuring a user profile card, a personalized product recommendation carousel, and an active promotional banner—the business domain permits partial success. If the promotional banner service suffers an outage, the screen should still render the user profile and recommendation list successfully. Executing these independent operations requires a supervisorScope rather than a standard coroutineScope. A supervisorScope isolates child failures: if one child coroutine fails with an uncaught exception, its failure does not cascade upwards to cancel the supervisor parent or active sibling coroutines. However, engineers frequently introduce catastrophic bugs by failing to distinguish between operational failure isolation and cancellation propagation. If the user navigates away from the dashboard, viewModelScope cancels the entire supervisorScope. If child error-handling logic catches broad Exception or Throwable and swallows CancellationException, the child coroutines continue executing in the background, violating structured concurrency. Preserving partial success safely demands wrapping child results in typed outcomes while explicitly allowing CancellationException to escape.

## Practical walkthrough (English)

Consider loading an Android dashboard composed of three independent API calls:
```kotlin
data class DashboardState(
    val profile: Profile?,
    val recommendations: List<Item>,
    val banner: Banner?
)

// Production-grade partial success with strict cancellation preservation:
suspend fun loadDashboard(userId: String): DashboardState = supervisorScope {
    val profileDeferred = async { fetchSafely { profileApi.getProfile(userId) } }
    val recsDeferred = async { fetchSafely { recsApi.getRecommendations(userId) } ?: emptyList() }
    val bannerDeferred = async { fetchSafely { bannerApi.getBanner() } }

    DashboardState(
        profile = profileDeferred.await(),
        recommendations = recsDeferred.await(),
        banner = bannerDeferred.await()
    )
}

// Helper that isolates domain exceptions but NEVER swallows CancellationException:
private suspend fun <T> fetchSafely(block: suspend () -> T): T? = try {
    block()
} catch (e: CancellationException) {
    throw e // Must escape to honour parent scope cancellation!
} catch (e: Exception) {
    null // Gracefully degrade domain failure to null
}
```
If bannerApi fails with HTTP 500, banner resolves to null while profile and recommendations render normally. Conversely, if viewModelScope cancels during loading, CancellationException unblocks all three deferred jobs immediately.

## Explanation in Arabic

استدعاء 3 APIs مستقلة بالتوازي مع الحفاظ على النجاح الجزئي (Partial Success) وعدم ابتلاع الإلغاء هو عكس السؤال السابق تماماً:

1. المعمارية المطلوبة:
   - الشاشة بتعرض: الأخبار، الطقس، والإعلانات.
   - لو فشل جلب الطقس، نريد عرض الأخبار والإعلانات بنجاح بدلاً من تدمير الشاشة بالكامل (Graceful Degradation).
   - **لكن انتبه للشرط الحرج:** 'دون ابتلاع الإلغاء' (Without swallowing cancellation). لو المستخدم قفل الشاشة، نريد إلغاء كل العمليات فوراً!

2. الأداة المناسبة: `supervisorScope { }`:
   - `supervisorScope` يعزل فشل الأبناء عن بعضهم؛ فشل طلب لا يلغي الإخوة.
   - ولكنه ما زال خاضعاً لـ Structured Concurrency: لو الأب نفسه تم إلغاؤه (المستخدم غادر الشاشة)، يلغي جميع الأبناء فوراً!

3. نمط الكود الصحيح:
   - نستخدم `runCatching` أو `try-catch` حول كل استدعاء `await()` **مع إعادة رمي `CancellationException` صراحة**:
     `if (e is CancellationException) throw e`

## Practical walkthrough

تنفيذ عملي لشاشة لوحة التحكم (Home Dashboard):
```kotlin
data class DashboardState(
    val news: List<NewsItem>?,
    val weather: WeatherInfo?,
    val ads: List<AdBanner>?
)

suspend fun fetchDashboard(): DashboardState = supervisorScope {
    val newsDeferred = async { safeApiCall { api.getNews() } }
    val weatherDeferred = async { safeApiCall { api.getWeather() } }
    val adsDeferred = async { safeApiCall { api.getAds() } }
    
    DashboardState(
        news = newsDeferred.await(),
        weather = weatherDeferred.await(),
        ads = adsDeferred.await()
    )
}

suspend fun <T> safeApiCall(block: suspend () -> T): T? = try {
    block()
} catch (e: CancellationException) {
    throw e // لا نبلع الإلغاء أبداً!
} catch (e: Exception) {
    null // فشل جزئي آمن
}
```

## Why it matters and how it works

`supervisorScope` prevents one direct child failure from cancelling its siblings, but it does not automatically convert failures into values. Capturing each result inside each `async` block and awaiting all three allows building a composite state. Parent cancellation still cancels the entire group because `supervisorScope` respects parent job cancellation. Catching `CancellationException` and converting it to a failure object is a severe bug because it causes an abandoned screen to continue doing background work and potentially dispatch state to a destroyed lifecycle.

## Worked example

```kotlin
import java.io.IOException
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.async
import kotlinx.coroutines.supervisorScope

data class Profile(val displayName: String)
data class Offers(val titles: List<String>)
data class Alerts(val unreadCount: Int)

sealed interface Section<out T> {
    data class Ready<T>(val value: T) : Section<T>
    data class Unavailable(val message: String) : Section<Nothing>
}

data class DashboardSnapshot(
    val profile: Section<Profile>,
    val offers: Section<Offers>,
    val alerts: Section<Alerts>,
)

interface DashboardApi {
    suspend fun fetchProfile(): Profile
    suspend fun fetchOffers(): Offers
    suspend fun fetchAlerts(): Alerts
}

class DashboardRepository(private val api: DashboardApi) {
    suspend fun load(): DashboardSnapshot = supervisorScope {
        val profile = async { request { api.fetchProfile() } }
        val offers = async { request { api.fetchOffers() } }
        val alerts = async { request { api.fetchAlerts() } }

        DashboardSnapshot(
            profile = profile.await(),
            offers = offers.await(),
            alerts = alerts.await(),
        )
    }

    private suspend fun <T> request(call: suspend () -> T): Section<T> =
        try {
            Section.Ready(call())
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (network: IOException) {
            Section.Unavailable("Network is temporarily unavailable")
        }
}
```

In unit tests with `runTest`:
1. Test partial success: stub `fetchOffers()` to throw `IOException`; assert `profile` and `alerts` are `Ready`, while `offers` is `Unavailable`.
2. Test parent cancellation: launch `load()` in a child job and cancel it while pending; verify `CancellationException` propagates and unfinished calls are aborted.

## Trade-offs and decision criteria

Partial rendering increases UI states, retry logic, telemetry, and consistency overhead. If dashboard sections are strictly independent, this resilience is worth the cost. However, for interdependent data (such as a checkout quote with price, tax, and promotional discounts), partial success is an invalid state: the entire quote must be all-or-nothing, demanding a standard `coroutineScope`. Furthermore, if the UX requires progressive streaming rather than a final snapshot, emit per-section StateFlow updates instead of a single composite return.

## Failure modes

- **Swallowing Cancellation:** Using standard `runCatching` catches `Throwable`, which intercepts `CancellationException` and converts cancellation into normal failure data, leaking coroutines.
- **Fail-fast on Independent Data:** Using standard `coroutineScope` causes one flaky network call to cancel healthy siblings.
- **Unbounded Retries:** Blindly retrying 4xx errors adds useless network traffic; only idempotent 5xx errors should be retried with exponential backoff.
- **Missing Freshness Metadata:** Displaying cached stale offers alongside fresh profile data without visual indicators confuses users.

## Production perspective

In a production banking or commerce app, load each card with explicit cache and freshness metadata. If offers fail, display a cached version with a "Pull to refresh" badge while profile displays live balances. Isolate dependency latency in telemetry so one degrading microservice does not go unnoticed. Unit test the repository by verifying that cancelling the parent job immediately halts all child network requests.

## Interview answer — short

supervisorScope isolates child failures for independent concurrent operations, allowing partial success when non-critical tasks fail. Each child async catches domain exceptions to degrade gracefully without cancelling siblings. Crucially, child catches must never swallow CancellationException: if the parent scope cancels, CancellationException must propagate immediately to abort all children and prevent resource leaks.

## Interview answer — structured

Executing independent concurrent API calls where partial success is acceptable requires supervisorScope rather than a standard coroutineScope. In a dashboard architecture, failure in a non-critical widget like a weather feed should not crash or abort vital widgets like the user profile.

SupervisorScope creates a supervision boundary where child failures are strictly isolated. When an individual child coroutine launched via async fails, the supervisor parent remains active and active sibling coroutines continue executing undisturbed.

In production, the critical challenge is managing cancellation versus failure. While we want to isolate domain network exceptions by catching them and degrading to fallback values or nulls, we must never intercept or swallow CancellationException. If the user navigates back and the parent ViewModel is cleared, the supervisorScope is cancelled.

Child catch blocks must explicitly check if the caught exception is a CancellationException and rethrow it immediately. This guarantees that screen departure cleanly aborts all concurrent child requests while still delivering robust partial success when the screen remains active.


## Interview answer — deep senior

At the internal architecture level, supervisorScope creates a SupervisorCoroutine whose underlying Job implements the supervisor contract. When a child coroutine throws an uncaught exception, its cancellation hook calls parent.childCancelled(cause). A standard ScopeCoroutine returns true and cancels all children, whereas a SupervisorCoroutine returns false and refuses to cancel itself. Consequently, the failed child transitions to Completed exceptionally while active sibling nodes remain in the Active state. However, many developers misunderstand how async interacts with supervisorScope. If an async coroutine inside supervisorScope throws an exception that is not caught inside its body, calling deferred.await() will rethrow that exception directly at the call-site. If await() is called without a surrounding try-catch, it will terminate the caller and propagate the failure outside the supervisorScope, defeating the purpose of partial success. Therefore, the error-handling boundary must live inside each individual child coroutine, wrapping the remote call in a typed result pattern like Result<T> or nullable fallback. The subtle danger lies in naive catch blocks: writing catch (e: Throwable) without rethrowing CancellationException breaks the parent-to-child cancellation pipeline. While parent cancellation signals cascade down through the Job hierarchy, a child coroutine executing a generic catch block will intercept the CancellationException, convert it into an ordinary failure result, and continue executing subsequent logic. In staff-level architecture, we enforce a strict helper utility—such as fetchSafely or runSuspendCatching—that explicitly permits CancellationException to bubble up. This guarantees that partial success operates strictly during active screen lifecycles while preserving instant teardown upon user navigation.

## How to answer in the interview

- **Why:** Independent dashboard cards should not take each other down; partial success preserves user value.
- **How:** Use `supervisorScope` + `async`, map expected errors inside the child to typed outcomes, and rethrow `CancellationException`.
- **Trade-offs:** Increases UI state complexity and retry handling; invalid for atomic financial transactions.
- **Failure cases:** Catching `CancellationException` via naive `runCatching`, or using standard `coroutineScope` which cancels siblings.
- **Production solution:** Expose per-card typed states with freshness markers, bound retries, and test parent cancellation explicitly.

## Deep-dive talking points

Contrast `coroutineScope` vs `supervisorScope` exception propagation, explain `Job` vs `SupervisorJob` hierarchy, detail why `runCatching` is dangerous without cancellation filtering, and describe progressive rendering via separate StateFlows.

## Follow-up questions

- **Interviewer:** "What is the difference between failure isolation in `supervisorScope` and passing `SupervisorJob()` to a regular scope?"
  **Answer:** "Passing `SupervisorJob()` to `launch` creates an unattached parent Job, breaking structured concurrency and preventing automatic child cancellation on scope exit. `supervisorScope` preserves structured concurrency: it is a suspending function that waits for all active children and cancels them if the parent scope cancels."

- **Interviewer:** "How do you represent partial failure in the UI layer?"
  **Answer:** "Using a sealed UI model or a data class where independent section models hold sealed states (e.g., `news: SectionState<List<News>>`, which can be `Success(data)` or `Error(reason)` with a localized retry action)."

- **Interviewer:** "Can you use Kotlin Flow `merge` or `zip` for this instead?"
  **Answer:** "Yes. You can emit each API call as a separate Flow, use `catch { emit(null) }` on individual streams, and combine them using `combine(flow1, flow2, flow3)` for reactive UI rendering."

## Self-check rubric

Can I draw the difference between `coroutineScope` and `supervisorScope` failure flows, demonstrate how to preserve cancellation in code, and articulate when partial success becomes a correctness bug?

## References and reviewed-on date

- [Kotlin coroutine exception handling](https://kotlinlang.org/docs/exception-handling.html) — supervision and cancellation mechanics.
- [Kotlin cancellation and timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html) — handling CancellationException properly.
- [Android Coroutines best practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) — lifecycle and structured concurrency.

Technically reviewed against primary documentation on 2026-10-13.
