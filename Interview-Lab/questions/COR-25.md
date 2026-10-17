---
id: "COR-25"
question: "Call 3 dependent APIs concurrently. If one fails, how do you cancel siblings and return a consistent failure?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "C"
phase: 1
priority: "P1"
order: 106
editorial_status: "reviewed"
---

# COR-25

## Original interview question

Call 3 dependent APIs concurrently. If one fails, how do you cancel siblings and return a consistent failure?

## What the interviewer evaluates

Design three concurrent all-or-nothing API calls, cancellation of siblings and one consistent failure.

## Concept and technical explanation

Executing multiple dependent or interdependent concurrent operations where the composite result requires all sub-tasks to succeed is a classic challenge solved by coroutineScope. When an operation—such as an e-commerce checkout prerequisite validation—requires results from three distinct backend microservices (e.g., verifying product inventory, validating user KYC credit limits, and calculating promotional coupon discounts), all three calls must succeed to form a consistent transaction payload. If any one of the three calls fails, proceeding is impossible, and allowing the remaining two calls to continue executing is a direct waste of battery, network bandwidth, and cloud server compute. The standard architectural solution is using coroutineScope. Unlike supervisorScope, a standard coroutineScope enforces strict fail-fast sibling cancellation: launching concurrent operations via async inside coroutineScope ensures that if any child encounters an uncaught exception, the scope cancels itself, immediately issues cancellation signals to all running sibling Deferred tasks, awaits their cooperative teardown, aggregates any secondary exceptions as suppressed throwables, and rethrows the root failure.

## Practical walkthrough (English)

Consider coordinating three checkout prerequisite validations concurrently:
```kotlin
data class CheckoutPayload(val inventory: Inventory, val credit: Credit, val discount: Discount)

// Production-grade all-or-nothing concurrent execution:
suspend fun validateCheckoutPrerequisites(userId: String, cartId: String): CheckoutPayload = coroutineScope {
    // Launch all 3 calls in parallel:
    val inventoryDeferred = async { inventoryApi.checkStock(cartId) }
    val creditDeferred = async { userApi.verifyCredit(userId) }
    val discountDeferred = async { promoApi.getDiscount(cartId) }

    // If inventoryApi throws an IOException, coroutineScope immediately cancels
    // creditDeferred and discountDeferred via CancellationException!
    CheckoutPayload(
        inventory = inventoryDeferred.await(),
        credit = creditDeferred.await(),
        discount = discountDeferred.await()
    )
}
```
If creditDeferred throws an HTTP 403 Forbidden while inventoryApi is still awaiting network packets, coroutineScope intercepts the failure, issues prompt cancellation to inventoryApi and promoApi, suppresses subsequent errors, and bubbles the HTTP 403 exception directly to the caller.

## Explanation in Arabic

استدعاء 3 APIs معتمدة على بعضها بالتوازي مع الإلغاء الفوري عند فشل أي منها (Fail-Fast with Sibling Cancellation) هو النمط الكلاسيكي للـ Structured Concurrency:

1. المعمارية المطلوبة:
   - نريد تشغيل 3 طلبات بالتوازي لتوفير الوقت.
   - إذا فشل أي طلب، نريد **إلغاء الطلبين الآخرين فوراً** لمنع إهدار باقة وبيانات المستخدم.
   - إرجاع خطأ موحد ومتسق للمتصل.

2. الأداة المناسبة: `coroutineScope { }`:
   - دالة `coroutineScope` هي الحل المثالي لأنها تستخدم **Standard Job**.
   - بمجرد أن يفشل أي `async` child برمي Exception، يقوم `coroutineScope` بإلغاء جميع الـ `async` الآخرين فوراً، ويعيد رمي الاستثناء الأصلي للأعلى.

3. ما الذي يجب تجنبه؟
   - تجنب `supervisorScope` هنا، لأن `supervisorScope` يعزل الفشل ويترك باقي الطلبات تعمل حتى لو فشل أحدها!
   - تجنب وضع `try-catch` حول كل `async.await()` داخل `coroutineScope` لأن ذلك قد يربك معالجة الأخطاء.

## Practical walkthrough

تنفيذ عملي لحجز رحلة يتطلب حجز الطيران والفندق وتأجير السيارة معاً:
```kotlin
suspend fun bookPackage(userId: String): BookingConfirmation = coroutineScope {
    // نطلق الـ 3 عمليات بالتوازي داخل coroutineScope:
    val flightDeferred = async { flightApi.bookFlight(userId) }
    val hotelDeferred = async { hotelApi.bookHotel(userId) }
    val carDeferred = async { carApi.bookCar(userId) }
    
    // إذا فشل bookFlight مثلاً، coroutineScope سيلغي hotelDeferred و carDeferred فوراً!
    BookingConfirmation(
        flight = flightDeferred.await(),
        hotel = hotelDeferred.await(),
        car = carDeferred.await()
    )
}
```
في الـ ViewModel: نحيط استدعاء `bookPackage` بـ `try-catch` لمعالجة الخطأ الموحد وإظهار رسالة 'فشل حجز الباقة' للمستخدم.

## Why it matters and how it works

Start independent prerequisites with `async` inside `coroutineScope`, await all, then validate a consistent aggregate before publishing. If there are true data dependencies, split into sequential stages. Parent cancellation cancels children; an ordinary child failure cancels siblings. Use a typed domain result at the outer boundary, with cancellation propagated.

## Worked example

Illustrative Kotlin/JVM: three fetches have no input dependency but the final response needs all three; callers supply cancellable, main-safe suspending APIs.

```kotlin
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope

data class CheckoutView(val price: Int, val tax: Int, val stock: Int)
suspend fun checkout(
    price: suspend () -> Int,
    tax: suspend () -> Int,
    stock: suspend () -> Int,
): CheckoutView = coroutineScope {
    val p = async { price() }
    val t = async { tax() }
    val s = async { stock() }
    CheckoutView(p.await(), t.await(), s.await())
}
```

## Trade-offs and decision criteria

All-or-nothing is right for a checkout quote where partial data is invalid. Parallel requests improve latency only when they are independent. If B depends on A, await A before launching B; if any call changes server state, design compensation or reconciliation rather than assuming sibling cancellation rolls it back.

## Failure modes

Launching three requests outside a structured scope can leave siblings running after one fails. Publishing price before stock arrives presents an inconsistent quote. A cancelled HTTP request may already have reached a server, so a failure response is not proof of rollback.

## Production perspective

A checkout repository fetches pricing, tax and stock under one request ID, validates quote version/expiry, and emits one immutable success or error. It logs which dependency failed and server correlation IDs; tests force each of the three failure positions and verify sibling cancellation and no partial UI commit.

## Interview answer — short

When 3 concurrent API calls are interdependent and required to construct a composite entity, coroutineScope provides all-or-nothing fail-fast cancellation. Inside coroutineScope, multiple async tasks run in parallel. If any call fails, the scope cancels itself and immediately terminates all active sibling tasks with CancellationException, aggregating secondary errors and rethrowing the root failure.

## Interview answer — structured

Coordinating three concurrent API calls where the final operation requires all three results is the quintessential use case for coroutineScope.

This represents an all-or-nothing transaction. If one service fails, the entire composite operation is doomed, and allowing sibling tasks to continue executing needlessly consumes mobile device battery and backend server resources.

In production, we wrap the concurrent calls inside coroutineScope and launch each request using async. Because coroutineScope installs a standard Job hierarchy, it enforces fail-fast error propagation. If any child coroutine encounters an uncaught exception, it notifies the parent scope. The scope immediately transitions to the Cancelling state and dispatches cancellation signals to all running sibling Deferred jobs.

CoroutineScope ensures that no orphan tasks remain in flight; it awaits the complete teardown of all children, collects any exceptions thrown during sibling cancellation as suppressed throwables, and rethrows the original triggering exception to the caller for consistent, unified error handling.


## Interview answer — deep senior

Under the hood, coroutineScope creates a ScopeCoroutine that implements JobSupport and wraps the caller's outer CoroutineContext. When child coroutines are spawned via async, each DeferredCoroutine is linked as a child Node in the parent's internal NodeList. When one async block throws an unhandled exception—such as a network SocketTimeoutException—its completion pathway invokes parent.childCancelled(cause). In a standard coroutineScope (unlike a supervisorScope), the parent acknowledges the cancellation, records the triggering cause as its root failure, and immediately iterates through its child NodeList, calling cancel(CancellationException(cause)) on every active sibling. Crucially, the fail-fast cancellation occurs before await() is ever called on the failing job. Even if the caller is currently suspended on inventoryDeferred.await(), an unhandled crash in the subsequent discountDeferred immediately unblocks the caller with the discount exception. Furthermore, if a sibling coroutine also encounters an exception while unwinding its execution during cancellation, the ScopeCoroutine attaches that secondary failure to the root exception using Throwable.addSuppressed(). This guarantees that no diagnostic failure data is lost in production crash logs or telemetry traces. In staff-level Android engineering, we strictly contrast this pattern with supervisorScope: supervisorScope isolates failures, allowing siblings to run to completion even if one fails. For all-or-nothing composite state aggregates (such as financial transactions or atomic state bundles), using supervisorScope is an architectural error because it leaves orphaned partial mutations active, whereas coroutineScope guarantees complete atomic consistency.

## How to answer in the interview

- **Why:** consistency depends on both input dependencies and output requirements.
- **How:** sequentially resolve required inputs, then parallelize independent reads inside coroutineScope.
- **Trade-off:** parallelism saves latency only when APIs can overlap.
- **Failure case:** publishing a partial checkout quote or assuming cancellation undoes a server write.
- **Production solution:** validate versions and reconcile any side effects.

## Deep-dive talking points

Draw the dependency DAG, distinguish input-dependence from all-results-needed, and reason about remote side effects.

## Follow-up questions

- **Interviewer:** "Why wouldn't you wrap each `await()` in a `try-catch` inside `coroutineScope`?"
  **Answer:** "Because in a standard `coroutineScope`, once an `async` child fails, the scope is ALREADY cancelled. Even if you catch the exception at `await()`, subsequent operations inside that scope will fail with CancellationException because the scope is dead."

- **Interviewer:** "How do you test this scenario deterministically in a unit test?"
  **Answer:** "Using `runTest`: configure one mock API call to throw an exception and the other two to have simulated delays. Verify that the test throws the expected exception and assert that the other two API jobs were cancelled without completing."

- **Interviewer:** "What happens if all 3 APIs need rollback logic if one fails?"
  **Answer:** "If any successful booking must be reversed upon sibling failure, catch the exception outside `coroutineScope`, and in the catch block or using a saga pattern, launch compensatory rollback calls (like refunding the successful flight)."

## Self-check rubric

Can I parallelize only independent inputs, return one consistent result, test all failure positions, and avoid false rollback claims?

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — structured concurrent children.
- [Coroutine exceptions](https://kotlinlang.org/docs/exception-handling.html) — sibling failure propagation.

Technically reviewed against primary documentation on 2026-10-13.
