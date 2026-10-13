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

تخيل إن الـHome Dashboard عندك بيعرض 3 كروت: بيانات الحساب، العروض المتاحة، والتنبيهات. لو أول API رجعت بنجاح، والتانية واجهت timeout أو 503، والتالتة رجعت بنجاح، الـBusiness Requirement الطبيعي إننا نعرض الكارتين السليمين بدل ما نقفل الشاشة كلها بـError Screen كاملة. ده اسمه **Partial Success**، وهو قرار منتج ومعماري قبل ما يكون اختيار Coroutine Builder.

لو استعملنا `coroutineScope` عادية وطلقنا الـ3 Calls بـ`async`، أي exception في child واحد هتلغي الـparent فتلغي الأخوات فوراً وتضيع البيانات السليمة. الحل الهندسي إننا نستخدم `supervisorScope`، ونعزل كل child بحيث يمسك فقط **الـDomain/Network Exceptions المتوقعة** ويحولها لـTyped Outcome (`Section.Ready` أو `Section.Unavailable`). في نفس الوقت، لو المستخدم خرج من الشاشة والـViewModel اتلغى، `CancellationException` لازم يُعاد رميها وما تتبلعش جوه الـcatch؛ لأن الإلغاء إشارة توقف مش عطل شبكة.

## Practical walkthrough

في dashboard حقيقي، الـSupervisor بيعزل فشل الـSiblings عن بعض، لكن مش بيحوّل الفشل تلقائياً لـSuccess/Failure Values؛ المطور هو اللي بيعمل ده عبر الـResult Type. لو جمعت الثلاثة بـ`supervisorScope`:
1. عند `t=0`: الطلبات الثلاثة تبدأ بالتوازي عبر `async`.
2. عند `t=150ms`: الحساب يرجع بنجاح فيبقى `Ready(profile)`.
3. عند `t=250ms`: العروض تفشل بـ`IOException` فتتحول لـ`Unavailable("Offers unavailable")` بينما الطلبات التانية مستمرة.
4. عند `t=400ms`: التنبيهات ترجع بنجاح، فنطلع Snapshot فيه 2 كروت جاهزة وكارت فيه زرار Retry.
5. لو المستخدم رجع للخلف أثناء التحميل: الـ`viewModelScope` يتلغي، وتمر `CancellationException` فتوقف أي عملية معلقة فوراً.

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

“If three APIs are independent, I avoid an all-or-nothing scope so one network failure does not cancel useful sibling data. I wrap concurrent calls in `supervisorScope` using `async`, catch expected service exceptions inside each child into a typed outcome like `Section.Unavailable`, and explicitly rethrow `CancellationException`. The UI then displays available cards with a targeted retry option.”

## Interview answer — structured

“First, I verify the product invariant: if the three endpoints power independent UI sections, partial success is desirable. I launch the calls concurrently in `supervisorScope` to isolate sibling failures. Inside each `async` block, I catch only expected network or domain exceptions and map them to a sealed `Section` state, while letting `CancellationException` escape so screen teardown stops all work. Awaiting the deferred values produces a composite snapshot. If the three endpoints instead represented a financial transaction or payment quote where every value is mandatory, I would intentionally use standard `coroutineScope` to fail fast and preserve strict atomicity.”

## Interview answer — deep senior

“I separate failure isolation at the coroutine level from error modeling at the product level. `supervisorScope` stops child failures from propagating upwards to siblings, but it does not magically handle exceptions: unhandled exceptions in a supervised child still crash unless awaited or caught inside the child block. Inside each child, I catch domain exceptions and map them into an explicit result type, but rethrow `CancellationException` to preserve structured concurrency when the user navigates away. 

For observability, I log latency and error rates per dependency rather than as a single composite metric. For the UI layer, if progressive rendering is required, I expose individual flows instead of awaiting a composite snapshot. When caching is involved, each card carries its own freshness timestamp. Most importantly, I never apply partial success blindly: independent cards benefit from it, but transactional operations like checkout calculations must remain fail-fast.”

## How to answer in the interview

- **Why:** Independent dashboard cards should not take each other down; partial success preserves user value.
- **How:** Use `supervisorScope` + `async`, map expected errors inside the child to typed outcomes, and rethrow `CancellationException`.
- **Trade-offs:** Increases UI state complexity and retry handling; invalid for atomic financial transactions.
- **Failure cases:** Catching `CancellationException` via naive `runCatching`, or using standard `coroutineScope` which cancels siblings.
- **Production solution:** Expose per-card typed states with freshness markers, bound retries, and test parent cancellation explicitly.

## Deep-dive talking points

Contrast `coroutineScope` vs `supervisorScope` exception propagation, explain `Job` vs `SupervisorJob` hierarchy, detail why `runCatching` is dangerous without cancellation filtering, and describe progressive rendering via separate StateFlows.

## Follow-up questions

- [COR-25](../cor-25/): Why shouldn't a payment quote accept partial success? **Answer:** A quote requires consistent item totals, taxes, and discounts; missing any part corrupts the total.
- [COR-16](../cor-16/): Why must `CancellationException` never be swallowed in a catch block? **Answer:** It signals that the parent scope was cancelled; swallowing it breaks cooperative cancellation and leaks resources.

## Self-check rubric

Can I draw the difference between `coroutineScope` and `supervisorScope` failure flows, demonstrate how to preserve cancellation in code, and articulate when partial success becomes a correctness bug?

## References and reviewed-on date

- [Kotlin coroutine exception handling](https://kotlinlang.org/docs/exception-handling.html) — supervision and cancellation mechanics.
- [Kotlin cancellation and timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html) — handling CancellationException properly.
- [Android Coroutines best practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) — lifecycle and structured concurrency.

Technically reviewed against primary documentation on 2026-10-13. Illustrative Kotlin examples tested against standard coroutines semantics.
