---
id: "COR-18"
question: "How do you retry requests with exponential backoff and jitter?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "B"
phase: 1
priority: "P1"
order: 99
editorial_status: "reviewed"
---

# COR-18

## Original interview question

How do you retry requests with exponential backoff and jitter?

## What the interviewer evaluates

Can the candidate design bounded retries with exponential backoff, jitter, cancellation and idempotency constraints?

## Explanation in Arabic

إعادة المحاولة مع التراجع الأسي والعشوائية (Exponential Backoff with Jitter) هي أفضل نمط إنتاجي للتعامل مع أخطاء الشبكة العابرة (Transient Network Errors):

1. ما هي مشكلة إعادة المحاولة الثابتة (Fixed Retries)؟
   - لو 10,000 مستخدم فتحوا التطبيق في نفس الوقت والسيرفر كان مضغوطاً ورجع خطأ 503، وكل التطبيقات أعادت المحاولة بعد ثانية واحدة بالظبط:
   - كل الـ 10,000 جهاز هيضربوا السيرفر في نفس الميلي-ثانية! ده بيعمل **Thundering Herd Problem (أو Retry Storm)** ويوقع السيرفر تماماً.

2. الـ Exponential Backoff:
   - بنضاعف وقت الانتظار بعد كل محاولة فاشلة (مثلاً: 1 ثانية، ثم 2، ثم 4، ثم 8 ثوانٍ).

3. دور الـ Jitter (العشوائية الضرورية):
   - إضافة وقت عشوائي صغير (Random Jitter من 0 إلى 500ms) لكل جهاز، حتى لا ترسل الأجهزة طلباتها في نفس التوقيت المتزامن، فيتم توزيع الحمل بسلاسة على السيرفر.

4. متى نعيد المحاولة ومتى نتوقف؟
   - **نكرر المحاولة فقط في:** أخطاء الشبكة العابرة (Timeout, 502, 503, 504).
   - **لا نكرر المحاولة أبداً في:** أخطاء العميل الحتمية (400 Bad Request, 401 Unauthorized, 404 Not Found)، ولا عند إلغاء الـ Coroutine (`CancellationException`).

## Practical walkthrough

دالة إنتاجية متكاملة لـ Retry with Backoff & Jitter في Kotlin:
```kotlin
suspend fun <T> retryWithBackoff(
    times: Int = 3,
    initialDelayMs: Long = 1000L,
    maxDelayMs: Long = 10000L,
    factor: Double = 2.0,
    block: suspend () -> T
): T {
    var currentDelay = initialDelayMs
    repeat(times - 1) { attempt ->
        try {
            return block()
        } catch (e: Exception) {
            if (e is CancellationException) throw e // لا تبلع الإلغاء أبداً!
            if (!isTransientError(e)) throw e // لا تعيد المحاولة في أخطاء 4xx
        }
        val jitter = Random.nextLong(0, 500L)
        delay(minOf(currentDelay + jitter, maxDelayMs))
        currentDelay = (currentDelay * factor).toLong()
    }
    return block() // المحاولة الأخيرة بدون catch
}
```

## Why it matters and how it works

Exponential delay grows by attempts, capped to prevent overflow and excessive wait; jitter spreads clients. `delay` is cancellable. Check the operation’s safety: a read may be retried, while a non-idempotent write needs a stable operation key and server deduplication. Retrying after process death requires persisting attempt state or handing it to durable work.

## Worked example

JVM illustration for a read-only API. `shouldRetry` must reject permanent/auth errors; the caller owns overall deadline. Randomized jitter is injected for tests.

```kotlin
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.delay
import kotlin.random.Random

suspend fun <T> retryRead(
    shouldRetry: (Exception) -> Boolean,
    request: suspend () -> T,
    jitter: (Long) -> Long = { Random.nextLong(it + 1) },
): T {
    var cap = 200L
    repeat(4) { attempt ->
        try { return request() }
        catch (e: CancellationException) { throw e }
        catch (e: Exception) {
            if (attempt == 3 || !shouldRetry(e)) throw e
            delay(jitter(cap))
            cap = (cap * 2).coerceAtMost(2_000)
        }
    }
    error("Unreachable")
}
```

## Trade-offs and decision criteria

Full jitter reduces synchronized retry spikes but makes individual latency variable. A smaller cap improves responsiveness but can overload a struggling service. For HTTP writes, only retry under a documented idempotency contract and use the same key; some errors should fail fast.

## Failure modes

Retrying every exception can loop on authentication or validation failures. A swallowed cancellation makes a closed screen keep retrying. A new idempotency key per attempt can duplicate a payment. Even a stable key does not imply exactly-once network execution; it relies on server semantics.

## Production perspective

An offline-first feed refresh retries transient read failures with bounded backoff and respects server throttling. Logs include attempt count and final outcome without sensitive payloads. A payment path instead persists operation state and reconciles before retrying with the same key.

## Interview answer — short

Retry with exponential backoff doubles the delay between consecutive failed attempts, while jitter adds a randomized time offset to prevent the 'thundering herd' problem. Crucially, retry loops must never catch CancellationException and must only retry transient server/network failures, never permanent 4xx client errors.

## Interview answer — structured

Exponential backoff with jitter is an essential resilience pattern for handling transient network failures without overwhelming backend services.

When a transient error occurs (like an HTTP 503 or socket timeout), retrying immediately or with a fixed delay causes the 'thundering herd' problem: thousands of mobile clients retry in unison, creating synchronized traffic spikes that keep the recovering server down. With exponential backoff, each retry doubles the wait time (e.g., 1s, 2s, 4s, up to a maximum cap).

Adding **jitter** injects a randomized offset (e.g., plus a random 0 to 500ms) into the delay calculation. This desynchronizes retry attempts across thousands of distributed devices, smoothing the load curve on backend systems.

In coroutines, we implement this as an inline suspending helper. Crucially, the retry loop must rethrow `CancellationException` immediately so coroutines cancel properly, and must only retry transient failures—never retrying permanent 4xx client errors like 401 Unauthorized or 404 Not Found.

## Interview answer — deep senior

From a distributed systems engineering perspective, full jitter (picking a uniform random value between 0 and the exponential backoff ceiling) provides superior desynchronization compared to equal jitter or no jitter.

When integrating this pattern with reactive streams or Kotlin Flow, the `retryWhen` operator provides the idiomatic abstraction: ```kotlin
flow.retryWhen { cause, attempt ->
    if (attempt < 3 && cause is IOException) {
        val delayTime = minOf(1000L * (1L shl attempt.toInt()) + Random.nextLong(200L), 10_000L)
        delay(delayTime)
        true
    } else false
}
```

In unit testing with `runTest`, testing backoff algorithms is straightforward because `delay()` integrates with the test scheduler's virtual clock, advancing time instantaneously with `advanceTimeBy()` without forcing tests to sleep in real time.

## How to answer in the interview

- **Why:** transient failures are recoverable, synchronized retries are harmful.
- **How:** classify failures, cap exponential delay, add jitter, and stop at an overall deadline.
- **Trade-off:** retries increase tail latency and load.
- **Failure case:** retrying auth errors or a non-idempotent write duplicates effects.
- **Production solution:** share a retry budget, preserve cancellation, and instrument attempt counts.

## Deep-dive talking points

Defend error classification, cap/jitter math, cancellation, process death and payment retry safety.

## Follow-up questions

- **Interviewer:** "Why shouldn't you retry HTTP 401 or 403 errors with exponential backoff?"
  **Answer:** "Because 401 and 403 are client authentication and permission failures, not transient network drops. Retrying them without refreshing the authentication token will fail every single time, wasting mobile battery and backend compute."

- **Interviewer:** "How does OkHttp's Interceptor compare to a coroutine retry wrapper?"
  **Answer:** "An OkHttp Interceptor handles retries at the transport layer, which is fast and transparent. However, a coroutine-level retry wrapper is superior for business-level logic, such as switching from a failed primary API to a fallback CDN, or updating UI progress messages between retries."

- **Interviewer:** "What is the maximum delay cap, and why is it necessary?"
  **Answer:** "Without a maximum delay cap (e.g., 10 or 30 seconds), exponential backoff grows unboundedly (1s, 2s, 4s, 8s, 16s, 32s, 64s...). A cap prevents the user from waiting minutes for an operation that should simply fail fast and prompt manual intervention."

## Self-check rubric

Can I state retryable errors, bound attempts/time, preserve cancellation, add jitter and explain write safety?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — retry and sync design.
- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — cancellable delay.

Technically reviewed against primary documentation on 2026-10-13.
