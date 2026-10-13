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

Use 'supervisorScope' with parallel 'async' tasks and handle child exceptions locally using try-catch that explicitly rethrows CancellationException. This isolates failures so successful sibling results are preserved while ensuring top-level lifecycle cancellation still terminates all work.

## Interview answer — structured

To preserve partial success across independent concurrent API calls without breaking cancellation, use `supervisorScope` combined with selective local error handling.

Inside `supervisorScope`, each `async` coroutine is supervised. If one child throws an exception, the failure is isolated: the supervisor scope does not cancel, and sibling tasks continue running. This allows the UI to render whatever data succeeded (e.g., displaying news articles even if the weather widget fails).

To satisfy the critical requirement of **not swallowing cancellation**, wrap each individual call in a try-catch block that inspects the exception: if `e is CancellationException`, rethrow it immediately. If the user navigates away and the parent ViewModel cancels the scope, the `CancellationException` propagates cleanly down and aborts all network connections.

## Interview answer — deep senior

Under the hood, `supervisorScope` installs a `SupervisorJob` as the parent context. When a child coroutine fails with a non-cancellation exception, `childCancelled` on the supervisor returns `false`. This prevents the scope from entering the `CANCELLING` state.

A dangerous antipattern is writing:

```kotlin
// ❌ ANTI-PATTERN:
supervisorScope {
    val news = async { runCatching { api.getNews() }.getOrNull() }
}
```

Standard `runCatching` catches `Throwable`, which intercepts `CancellationException` and converts it to a null result! When the user exits the screen, the coroutines keep running on background threads, ignoring cancellation. In production, we define a dedicated `runSuspendCatching` extension that rethrows `CancellationException`, guaranteeing both partial fault tolerance and responsive lifecycle cancellation.

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
