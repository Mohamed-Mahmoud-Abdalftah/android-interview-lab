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

Use 'coroutineScope' with parallel 'async' tasks. Because coroutineScope uses a standard Job, if any child fails, it automatically cancels all active siblings immediately (fail-fast) and rethrows the failure, guaranteeing consistent transactional error handling without orphaned background requests.

## Interview answer — structured

To call 3 dependent APIs concurrently and ensure that the failure of any one immediately cancels the others, the standard architectural pattern is using `coroutineScope` combined with `async`.

`coroutineScope` creates a structured child scope backed by a standard `Job`. Inside the block, we launch all three network requests in parallel using `async`. We then await all three results:

```kotlin
suspend fun fetchDashboardData(): DashboardData = coroutineScope {
    val user = async { api.getUser() }
    val config = async { api.getConfig() }
    val feed = async { api.getFeed() }
    DashboardData(user.await(), config.await(), feed.await())
}
```

If `api.getUser()` fails with a NetworkException, structured concurrency guarantees that the failure propagates to `coroutineScope`. The scope cancels itself and immediately sends cancellation signals to `config` and `feed`, aborting their HTTP connections and rethrowing the initial exception to the caller.

## Interview answer — deep senior

Under the hood, when `user` throws an exception, it triggers `parent.childCancelled(cause)`. The parent `coroutineScope` transitions into the `CANCELLING` state and traverses its child list, invoking `child.cancel(CancellationException(cause))` on `config` and `feed`. If OkHttp or Ktor is used, the underlying HTTP socket connection is immediately closed and its read loop is interrupted.

If one of the sibling coroutines also throws an exception while being cancelled, `coroutineScope` collects that secondary exception and adds it to the root cause via `Throwable.addSuppressed()`. This preserves full diagnostic logging in Crashlytics.

Do NOT use `supervisorScope` for this use case: a supervisor scope would isolate the failure, allowing the remaining two calls to complete and waste bandwidth on a request that has already fundamentally failed.

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
