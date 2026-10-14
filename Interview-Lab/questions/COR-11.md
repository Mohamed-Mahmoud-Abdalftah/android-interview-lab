---
id: "COR-11"
question: "Compare coroutineScope and supervisorScope including failure propagation."
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 92
editorial_status: "reviewed"
---

# COR-11

## Original interview question

Compare coroutineScope and supervisorScope including failure propagation.

## What the interviewer evaluates

- Structured concurrency hierarchy: How child jobs relate to parent jobs in the `Job` tree.
- Bidirectional vs unidirectional failure propagation: Why a regular child failure cancels its parent and siblings, whereas supervision isolates direct children.
- Exception handling mechanisms: The behavioral differences between `launch` (exception propagated to handler) and `async` (exception encapsulated in `Deferred`).
- Cancellation propagation: Recognizing that cancelling the parent scope cascades downward to all children in both scope builders.
- Practical production decision-making: Choosing all-or-nothing aggregate transactions vs independent resilient UI widgets.

## Explanation in Arabic

علشان تفهم الفرق الجوهري بين `coroutineScope` و `supervisorScope`، لازم تتخيل الـ **Job Hierarchy** (شجرة الـ Coroutines) كعلاقة بين أب وأطفاله:

في Coroutines، أي Scope بيعمل تعليق (`suspends`) ومبيخلصش إلا لما كل الأطفال اللي جواه يخلصوا شغلهم تماماً. ده مبدأ **Structured Concurrency**. لكن الفرق القاتل هو: **إيه اللي بيحصل لما طفل من الأطفال يفشل ويضرب Exception غير ممسوك (Uncaught Exception)؟**

```text
[coroutineScope — All or Nothing]
            Parent Job
           /     |     \
     Child 1  Child 2  Child 3
     (Success) (FAILS!) (Running)
                 |
                 +--> يلغي الأب (Parent)
                        |
                        +--> الأب يلغي باقي الإخوة (Child 3 Cancelled!)

[supervisorScope — Sibling Isolation]
         SupervisorJob (Parent)
           /     |     \
     Child 1  Child 2  Child 3
     (Success) (FAILS!) (Running)
                 |
                 +--> الأب يفضل حي، والإخوة يكملوا عادي!
```

### 1. في حالة `coroutineScope`:
الفشل بيمشي في اتجاهين:
1. من الطفل للأب: الطفل اللي فشل بيلغي الـ Parent فوراً.
2. من الأب لباقي الأطفال: الـ Parent بيلغي كل إخوته الشغالين (`CancellationException`).
ده مناسب جداً لعمليات الـ "All-or-Nothing"؛ مثلاً بتحسب إجمالي فاتورة: محتاج سعر المنتجات + الضريبة + كود الخصم. لو الضريبة فشلت، مفيش أي داعي تكمل حساب الخصم لأن النتيجة النهائية بقت باطلة.

### 2. في حالة `supervisorScope`:
الفشل معزول (`Isolated`):
- فشل أي طفل مباشر **مش هيلغي الأب**، وبالتالي **مش هيلغي إخوته**.
- ده مناسب جداً لشاشات الـ Dashboard؛ عندك كارت لبيانات المستخدم، كارت للعروض، وكارت للإشعارات. لو كارت العروض فشل، كارت المستخدم والإشعارات يكملوا ويعرضوا بياناتهم عادي، والكارت الفاشل يعرض زرار Retry.

### 3. قاعدة ذهبية لا تتغير في الحالتين:
لو الـ **Parent نفسه اتلغى** (مثلاً المستخدم قفل الشاشة والـ `viewModelScope` اتلغى)، الـ Cancellation بتنزل لتحت وتلغي كل الأطفال في الحالتين فوراً. الـ Supervision بتعزل فشل الأطفال عن بعضهم، لكن مبتفصلش الأطفال عن دورة حياة الأب.

## Practical walkthrough

تخيل شاشة Home في تطبيق تجارة إلكترونية بتنادي 3 APIs على التوازي: `fetchUserProfile()`، `fetchBanners()`، و `fetchUnreadCount()`.

- **النهج الخاطئ:** استخدام `coroutineScope` عادي مع `async`:
  ```kotlin
  // كارثة في الـ Production: لو الـ banners سيرفرها واقع،
  // الـ HomeScreen كلها هتضرب وتظهر شاشة بيضاء أو Error كامل للمستخدم!
  coroutineScope {
      val user = async { api.getUser() }
      val banners = async { api.getBanners() } // لو ده ضرب 500
      val count = async { api.getCount() }     // ده هيتلغي فوراً!
      Dashboard(user.await(), banners.await(), count.await())
  }
  ```
- **النهج الصحيح:** استخدام `supervisorScope` مع الحفاظ الصريح على `CancellationException`:
  ```kotlin
  supervisorScope {
      val userDeferred = async {
          try {
              Result.success(api.getUser())
          } catch (e: CancellationException) {
              throw e // الحفاظ على إلغاء الـ Scope عند خروج المستخدم
          } catch (e: Exception) {
              Result.failure(e)
          }
      }
      val bannersDeferred = async {
          try {
              Result.success(api.getBanners())
          } catch (e: CancellationException) {
              throw e
          } catch (e: Exception) {
              Result.failure(e)
          }
      }
      val countDeferred = async {
          try {
              Result.success(api.getCount())
          } catch (e: CancellationException) {
              throw e
          } catch (e: Exception) {
              Result.failure(e)
          }
      }
      
      // نجمع النتائج بأمان، وكل child معزول تماماً
      val user = userDeferred.await()
      val banners = bannersDeferred.await()
      val count = countDeferred.await()
  }
  ```
- **تنبيه حرج:** تجنب استخدام `runCatching` العادية داخل كود الـ Coroutines لأنها تلتقط `Throwable` (بما فيها `CancellationException`) وتبتلعها، مما يعطل إلغاء العمليات الخلفية ويسرب الموارد عند مغادرة الشاشة. يجب إما استخدام `try-catch` مع إعادة رمي `CancellationException`، أو دالة مساعدة تعيد رمي الإلغاء.

## Why it matters and how it works

With `coroutineScope`, the boundary creates an ordinary `Job`. If any child throws an uncaught exception other than `CancellationException`, it cancels its parent, which subsequently cancels all sibling jobs. Catching an exception by wrapping `await()` in a `try/catch` outside the child will not prevent cancellation: the child already crashed the parent scope before you awaited it.

With `supervisorScope`, the boundary installs a `SupervisorJob`. A failure of a direct child is not propagated upward to the parent or outward to siblings. However:
1. If an uncaught exception is thrown directly inside the supervisor block itself (outside any child coroutine), the supervisor scope fails and cancels all children.
2. With `launch`, an unhandled failure in a supervised child is dispatched to the thread's uncaught exception handler unless caught or intercepted via `CoroutineExceptionHandler`.
3. With `async`, the exception is encapsulated in the returned `Deferred` and only thrown when `await()` is invoked.

## Worked example

Here is a tested Kotlin implementation comparing sibling isolation and parent cancellation under `supervisorScope`:

```kotlin
// Compiled and tested illustration of resilient parallel card loading
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.supervisorScope

data class DashboardCardState(
    val profile: String?,
    val offers: String?,
    val notifications: Int?
)

suspend fun loadDashboardResilient(
    fetchProfile: suspend () -> String,
    fetchOffers: suspend () -> String,
    fetchNotifications: suspend () -> Int
): DashboardCardState = supervisorScope {
    val profileDeferred = async {
        try {
            fetchProfile()
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            null
        }
    }

    val offersDeferred = async {
        try {
            fetchOffers()
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            null
        }
    }

    val notificationsDeferred = async {
        try {
            fetchNotifications()
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            null
        }
    }

    DashboardCardState(
        profile = profileDeferred.await(),
        offers = offersDeferred.await(),
        notifications = notificationsDeferred.await()
    )
}
```

```kotlin
// Pure JVM Unit Test asserting partial success under supervision
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest

@OptIn(ExperimentalCoroutinesApi::class)
fun main() = runTest {
    val state = loadDashboardResilient(
        fetchProfile = { "Ada Lovelace" },
        fetchOffers = { throw IllegalStateException("Offers service timeout 504") },
        fetchNotifications = { 3 }
    )

    check(state.profile == "Ada Lovelace") { "Profile should succeed" }
    check(state.offers == null) { "Failing offers should gracefully fallback to null" }
    check(state.notifications == 3) { "Notifications must complete despite offers failure" }
    println("COR-11 verification passed: Partial success verified under supervisorScope.")
}
```

## Trade-offs and decision criteria

- **Use `coroutineScope` when:** Operations have strict atomic dependencies where partial execution is invalid or dangerous (e.g. checkout pricing, biometric auth + token exchange, DB migration).
- **Use `supervisorScope` when:** Tasks represent independent features or screen modules where partial results provide a better user experience than total failure (e.g. dashboard widgets, analytics dispatch, prefetching).
- **Overhead & Complexity:** Supervision requires explicit UI error states for each child card and careful exception handling, whereas all-or-nothing scopes allow centralized error boundaries.

## Failure modes

- **Swallowing CancellationException:** Catching `Exception` inside a supervised child without rethrowing `CancellationException` breaks cooperative cancellation when the user navigates away from the screen.
- **Catching `await()` too late in `coroutineScope`:** Wrapping `val result = deferred.await()` in `try/catch` in an ordinary `coroutineScope` will not save siblings; the child has already cancelled the scope when it threw.
- **Uncaught `launch` crashes in `supervisorScope`:** Believing `supervisorScope` "catches" exceptions. A crashing `launch` inside `supervisorScope` will still crash the app unless handled or captured by `CoroutineExceptionHandler`.

## Production perspective

In a production Android app:
- Screen-level orchestrators in `ViewModel` consume independent domain use cases via `supervisorScope`. Each use case maps HTTP errors to a typed `Result<T>` before passing it to the UI.
- Cancellation remains tied to `viewModelScope`: when the Activity finishes or the Composable leaves the composition, parent cancellation immediately terminates all active network calls.
- For financial mutations and critical multi-step operations, an all-or-nothing `coroutineScope` is combined with backend idempotent transaction IDs (`Idempotency-Key`).

## Interview answer — short

The main difference is how they handle a child failure. With `coroutineScope`, if one child fails with an uncaught exception, the scope cancels the other children. With `supervisorScope`, one child's failure doesn't automatically cancel its siblings. I'd use the first when all operations must succeed together, and the second when I can accept partial results. Both still respect cancellation from their parent.

## Interview answer — structured

Both `coroutineScope` and `supervisorScope` follow structured concurrency, so they wait for their child coroutines to finish. The difference is what happens when one child fails. In a normal `coroutineScope`, that failure cancels the scope and its siblings. In `supervisorScope`, sibling tasks can continue.

For example, imagine a home screen loading the profile, offers, and notifications in parallel. If offers fail, I still want to show the profile and notifications, so I'd use supervision and handle each API result separately. But if those requests are all needed to calculate a payment quote, I'd use an all-or-nothing approach.

One important detail is that `supervisorScope` doesn't handle exceptions for you. I still need to convert expected failures into meaningful results, and I must let `CancellationException` propagate when the screen is cancelled.


## Interview answer — deep senior

The important distinction is failure propagation, not just whether we're using `async`. In `coroutineScope`, a child throwing an uncaught exception cancels the parent scope and its sibling jobs. Catching a failure only when calling `await()` may be too late, because the child can already have cancelled the scope.

In `supervisorScope`, a direct child's failure doesn't cancel the other children. However, if an exception escapes from the supervisor block itself, that block fails and the remaining children are cancelled. Also, supervision does not make exceptions disappear. With `async`, the exception is stored in the `Deferred` and may be rethrown on `await`; with a failing `launch`, I need a deliberate reporting or handling strategy.

Say the dashboard has three independent endpoints. I'd launch them in a `supervisorScope`, catch expected network failures inside each child, map each outcome to a typed UI result, and explicitly rethrow cancellation. That lets the screen display two successful sections and a retry action for the failed one. I'd use `runTest` to verify partial success and to confirm that cancelling the parent stops the pending requests.

For operations that must all succeed together, such as gathering mandatory inputs for a financial calculation, I'd normally prefer `coroutineScope`. The choice comes from the product invariant, not personal preference. And neither scope means an already accepted network request has been rolled back, so external side effects need their own idempotency and reconciliation rules.


## How to answer in the interview

- **Why:** Failure policy follows product dependencies: atomic aggregations require fail-fast cancellation, while independent widgets require fault isolation.
- **How:** `coroutineScope` propagates failures bidirectionally across the Job hierarchy; `supervisorScope` stops upward failure propagation from direct children while preserving downward parent cancellation.
- **Trade-offs:** Supervision requires handling individual errors and modeling partial UI states instead of relying on a single global error screen.
- **Failure cases:** Swallowing `CancellationException` prevents cleanup; wrapping `await()` in an ordinary scope does not prevent sibling cancellation.
- **Production solution:** Supervise independent queries, catch domain exceptions inside children, rethrow cancellation, and map each outcome to a typed UI state.

## Deep-dive talking points

- **Job Tree Internals:** How `CompletableJob` and `SupervisorJob` override `childCancelled()` differently in the coroutine runtime.
- **Exception Delivery:** Why `launch` delivers unhandled exceptions to `CoroutineExceptionHandler` immediately, while `async` holds the exception until `await()`.
- **Scope Block Escapes:** Why throwing an exception directly in the body of `supervisorScope { throw RuntimeException() }` cancels all children.
- **Parent Cancellation:** Confirming that when `viewModelScope` cancels, both `coroutineScope` and `supervisorScope` cancel active children without delay.

## Follow-up questions

- [COR-12](../cor-12/): **Interviewer:** "If you use supervisorScope, can you skip try/catch?"
  **Answer:** "No. It isolates sibling failures, but it doesn't turn exceptions into a successful result. I still handle expected exceptions inside each child, and I decide how the UI represents a failed section. If I simply await a failed Deferred and let that exception escape the supervisor block, I can still fail the overall operation."

- **Interviewer:** "What happens when the user leaves the screen?"
  **Answer:** "If the work is owned by `viewModelScope`, clearing the ViewModel cancels that scope. Cancellation propagates into the supervisor and its children. I don't convert `CancellationException` into a normal network error, because then the work might continue after it's no longer needed."

- [COR-26](../cor-26/): **Interviewer:** "Do you always need supervisorScope for partial success?"
  **Answer:** "Not necessarily. If each child handles its expected failures internally and returns a value, you can achieve partial success under `coroutineScope` too. I'd choose supervision when I explicitly want sibling failure isolation, while still handling errors and cancellation correctly."

## Self-check rubric

- Can I trace failure propagation in the Job tree for both scope types?
- Can I explain why catching an `await()` inside `coroutineScope` is too late to prevent sibling cancellation?
- Can I justify choosing `coroutineScope` vs `supervisorScope` based on business invariants?
- Can I explain why `CancellationException` must always be rethrown inside supervised children?

## References and reviewed-on date

- [Kotlin Coroutines Exception Handling](https://kotlinlang.org/docs/exception-handling.html) — official supervision and exception handling guide.
- [Android Coroutines Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) — structured concurrency and ViewModel lifecycles.

Technically reviewed against primary Kotlin and Android documentation on 2026-10-13; illustrative examples compiled and validated on JVM.
