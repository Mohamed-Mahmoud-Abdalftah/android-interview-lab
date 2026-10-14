---
id: "COR-17"
question: "How do timeout, withTimeout, and withTimeoutOrNull work?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 98
editorial_status: "reviewed"
---

# COR-17

## Original interview question

How do timeout, withTimeout, and withTimeoutOrNull work?

## What the interviewer evaluates

Can the candidate distinguish a coroutine deadline from network commit certainty and handle timeout nullability?

## Explanation in Arabic

إدارة الـ Timeouts في Kotlin Coroutines تتم عبر دالتين رئيسيتين: `withTimeout` و `withTimeoutOrNull`:

1. دالة `withTimeout(timeMillis)`:
   - بتعلق الـ Coroutine وتحدد مهلة زمنية قصوى لتنفيذ البلوك.
   - لو الوقت انتهى قبل اكتمال الكود، بترمي **`TimeoutCancellationException`** (وهي نوع خاص من `CancellationException`).
   - **تحذير خطير:** بما إنها ترمي Exception، لو الكود مش محاط بـ `try-catch`، الـ Exception هيلغي الـ Coroutine بالكامل!

2. دالة `withTimeoutOrNull(timeMillis)`:
   - البديل الأكثر أماناً وأناقة في معظم سيناريوهات الـ UI والشبكات.
   - لو البلوك انتهى في الوقت المحدد: بترجع النتيجة بنجاح.
   - لو الوقت انتهى: تلغي البلوك وترجع **`null`** بدون رمي أي Exception وبدون إلغاء الـ Scope!

3. نقطة دقيقة للمحترفين (Under the hood Caveat):
   - عملية فحص الـ Timeout هي عملية **تعاونية (Cooperative)**. لو الكود الداخلي عبارة عن Loop حسابية مفيهاش أي Suspension point، الـ Timeout مش هيقدر يوقفها حتى لو الوقت خلص!

## Practical walkthrough

في شاشة جلب الموقع الجغرافي أو المصادقة البيومترية:
- المستخدم بيطلب تحديد موقعه الحالي بنظام GPS؛ لو الـ GPS لم يستجب خلال 5 ثوانٍ، نريد استخدام آخر موقع محفوظ في الـ Cache بدلاً من تعليق الشاشة.
```kotlin
suspend fun getCurrentLocation(): Location {
    // نستخدم withTimeoutOrNull بمهلة 5 ثوانٍ:
    val freshLocation = withTimeoutOrNull(5_000L) {
        gpsClient.awaitSingleFix()
    }
    
    // لو رجع null (حصل timeout)، نستخدم الـ Cache فوراً:
    return freshLocation ?: locationCache.getLastKnownLocation()
}
```

## Why it matters and how it works

Timeout is a structured child boundary and can race with a successful return. Use a positive duration and handle nullable domain values separately if `withTimeoutOrNull` is ambiguous. To convert timeout into a domain failure, map it at the correct boundary without swallowing unrelated parent cancellation. Transport timeouts and application deadlines are separate layers.

## Worked example

JVM illustration uses `kotlinx-coroutines-core`; `lookup` is a cancellable, side-effect-free suspend API, so `null` is a safe fallback meaning timeout here.

```kotlin
import kotlinx.coroutines.withTimeoutOrNull

suspend fun cachedLookup(
    lookup: suspend () -> String,
): String = withTimeoutOrNull(2_000) { lookup() } ?: "cached"
```

## Trade-offs and decision criteria

Use `withTimeout` when timeout is exceptional and `withTimeoutOrNull` when a fallback is natural. Do not use `null` to encode timeout if null is also a legitimate result. Set transport deadlines too, and make external writes idempotent/reconcilable rather than assuming cancellation undoes them.

## Failure modes

A `Thread.sleep` inside the block ignores coroutine cancellation and can exceed the deadline. A payment request may reach the server before timeout, so immediately retrying with a new key can charge twice. Closing a returned resource must account for cancellation racing with return.

## Production perspective

An address suggestion API uses a short timeout and cached suggestions as fallback. A checkout payment uses an operation ID, persists pending state, queries server status after ambiguous timeout and retries only with the same idempotency key according to the server contract.

## Interview answer — short

withTimeout cancels the block and throws a TimeoutCancellationException if the time limit expires. withTimeoutOrNull cancels the block and safely returns null upon timeout instead of throwing an exception, making it much more ergonomic for fallbacks and retry logic.

## Interview answer — structured

Both `withTimeout` and `withTimeoutOrNull` enforce execution time limits on suspending blocks, but they handle deadline expiration differently.

`withTimeout` cancels the enclosed coroutine block and throws a `TimeoutCancellationException` if the duration elapses before completion. Because `TimeoutCancellationException` inherits from `CancellationException`, it cancels the enclosing coroutine unless explicitly caught with a `try-catch` block around `withTimeout`.

`withTimeoutOrNull` is much more ergonomic for Android fallback scenarios. When the deadline expires, it cancels the internal block and cleanly returns `null` instead of throwing an exception. This allows elegant fallback expressions using the Elvis operator (`?:`), such as falling back to cached database data if a network request exceeds two seconds.


## Interview answer — deep senior

Under the hood, both functions schedule a delayed task on the coroutine dispatcher's event loop via `Delay.scheduleResumeAfterDelay()`. When the timer fires, it calls `cancelCoroutine(TimeoutCancellationException)`. However, timeout cancellation is strictly cooperative. If the code running inside `withTimeout` is executing a non-suspending, blocking loop (like heavy crypto or file I/O), the timeout cannot preempt the thread. It will only cancel when the block reaches a suspension point or checks `ensureActive()`.

Another critical nuance is resource cleanup. If an unmanaged resource (like a database cursor or network socket) is opened inside `withTimeout`, a timeout cancellation during the open call could leak the resource before the assignment finishes. To guard against resource leaks, always allocate resources outside the timeout block or protect them with `try-finally`.


## How to answer in the interview

- **Why:** a deadline bounds caller waiting, not remote side effects.
- **How:** withTimeout throws TimeoutCancellationException; withTimeoutOrNull maps its own timeout to null.
- **Trade-off:** fallback suits safe reads, while writes need reconciliation.
- **Failure case:** uncooperative blocking code keeps running or null conflates states.
- **Production solution:** define a typed timeout outcome and set transport/server deadlines too.

## Deep-dive talking points

Discuss races with return, resource cleanup, blocking code and the difference between client deadline and server transaction status.

## Follow-up questions

- **Interviewer:** "Why does catching `CancellationException` outside `withTimeout` catch the timeout exception?"
  **Answer:** "Because `TimeoutCancellationException` is a subclass of `CancellationException`. If you catch `CancellationException`, you will catch timeout errors as well, which is why `withTimeoutOrNull` is generally preferred to avoid accidental exception handling confusion."

- **Interviewer:** "How does `withTimeout` interact with deterministic unit tests?"
  **Answer:** "When using `runTest` from `kotlinx-coroutines-test`, virtual time is automatically skipped by default. `withTimeout` will either complete instantly if virtual time is advanced, or time out deterministically when calling `advanceTimeBy(delay)`."

- **Interviewer:** "Can you use `withTimeout` with blocking Java network calls?"
  **Answer:** "Only if the blocking call is running on `Dispatchers.IO` and explicitly checks for cancellation. Standard blocking calls like `InputStream.read()` will not respond to `withTimeout` until the socket read returns or closes."

## Self-check rubric

Can I choose an API, interpret null safely, name cooperative-cancellation limits, and explain ambiguous server outcome?

## References and reviewed-on date

- [Kotlin withTimeout API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html) — deadline and race semantics.
- [Kotlin withTimeoutOrNull API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout-or-null.html) — nullable timeout result.

Technically reviewed against primary documentation on 2026-10-13.
