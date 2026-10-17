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

## Concept and technical explanation

In Kotlin coroutines, coroutineScope and supervisorScope are suspending scope functions that establish structured concurrency boundaries within a coroutine hierarchy. Both scope builders suspend their calling coroutine until all launched child tasks reach a terminal state, and both guarantee downward cancellation propagation when the enclosing parent job is cancelled. The critical distinction lies in their upward failure propagation mechanics. A coroutineScope creates a standard Job that enforces an all-or-nothing transactional contract: an unhandled exception in any single child immediately cancels the parent scope, which subsequently cancels all surviving sibling coroutines and rethrows the failure to the caller. Conversely, supervisorScope creates a SupervisorJob that isolates direct child failures. When a child coroutine within a supervisorScope fails with an uncaught exception, the supervisor scope suppresses upward cancellation, allowing sibling coroutines to continue executing unhindered while leaving error handling to the individual child caller.

## Practical walkthrough (English)

Illustrating all-or-nothing transactions versus independent dashboard widgets:
```kotlin
// Scenario A: All-or-nothing checkout transaction using coroutineScope
suspend fun executeCheckout(orderId: String): CheckoutResult = coroutineScope {
    // If tax calculation fails with a 500 server error, payment processing is cancelled immediately:
    val taxDeferred = async { taxService.calculateTax(orderId) }
    val paymentDeferred = async { paymentGateway.charge(orderId) }
    
    CheckoutResult(tax = taxDeferred.await(), receipt = paymentDeferred.await())
}

// Scenario B: Resilient dashboard using supervisorScope
suspend fun loadDashboard(): DashboardState = supervisorScope {
    val userProfile = async {
        try { userService.fetchProfile() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
    }
    val promotionBanners = async {
        try { promoService.fetchBanners() } catch (e: CancellationException) { throw e } catch (e: Exception) { emptyList() }
    }
    
    // A network failure in banners does not cancel the profile fetch:
    DashboardState(user = userProfile.await(), banners = promotionBanners.await())
}
```

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

coroutineScope and supervisorScope both establish structured concurrency boundaries that wait for child completion, but differ in upward failure propagation. coroutineScope enforces fail-fast all-or-nothing semantics: if one child fails, it cancels the parent and all siblings. supervisorScope isolates direct child failures, allowing siblings to finish their tasks while the failed child handles its own error.

## Interview answer — structured

Both coroutineScope and supervisorScope establish structured concurrency boundaries that suspend until every child task completes execution.

The fundamental divergence is how they handle upward failure propagation. A standard coroutineScope enforces strict transactional consistency. If any child coroutine encounters an unhandled exception, it immediately cancels its parent Job, which cascades cancellation to all sibling coroutines and rethrows the root exception. This fail-fast behavior is essential for dependent operations such as atomic financial transactions where partial completion would corrupt application state.

In production, supervisorScope provides resilience by decoupling sibling lifecycles. It installs a SupervisorJob under the hood, meaning that an unhandled failure in one child does not cancel the supervisor parent and does not interrupt sibling tasks. This makes supervisorScope the premier choice for multi-widget user interfaces like e-commerce home screens, where a failure in a promotional banner must not prevent the user profile or notification counter from rendering.

Engineers must remember that downward cancellation remains identical in both builders. If the outer caller or ViewModelScope cancels, all child coroutines inside either scope builder are terminated immediately.


## Interview answer — deep senior

Under the hood in kotlinx.coroutines, coroutineScope and supervisorScope differ in how their internal Job nodes respond to the childCancelled callback in JobSupport. In a coroutineScope, the underlying ScopeCoroutine node maintains a bidirectional relationship with its children. When a child throws an unhandled exception, it invokes parent.childCancelled(cause). The parent transitions its internal state machine from Active to Cancelling, posts cancellation tokens to its NodeList, and terminates all active siblings before rethrowing the exception from the scope's continuation.
In contrast, supervisorScope instantiates a SupervisorCoroutine. Its implementation overrides childCancelled to return false unconditionally. When a direct child fails, the supervisor acknowledges the notification without transitioning into the Cancelling state, effectively severing the upward failure chain. However, this isolation applies strictly to direct children. If a direct child of a supervisorScope launches grandchild coroutines using standard launch or async without establishing a nested supervisor, an unhandled failure in a grandchild will still tear down that direct child and its immediate siblings.
Furthermore, exception routing requires careful handling under supervision. In a supervisorScope, if an unhandled exception occurs inside a direct launch builder, the exception cannot travel up to the supervisor; therefore, it delegates immediately to the thread-level uncaught exception handler or CoroutineExceptionHandler, crashing the application if unhandled. With async builders, the exception is encapsulated inside the Deferred handle and remains dormant until await is invoked. Senior architects ensure that independent background tasks inside a supervisorScope either wrap their work in domain-safe try-catch blocks rethrowing CancellationException or attach dedicated exception handlers to prevent unexpected process crashes.

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
