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

## Concept and technical explanation

Retrying failed asynchronous network requests with exponential backoff and randomized jitter is the standard resilience pattern for mitigating transient distributed faults without overloading infrastructure. When client coroutines encounter transient network anomalies like connection drops, socket timeouts, or HTTP 503 Service Unavailable, immediate fixed retries synchronize thousands of clients into a unified retry wave, causing the destructive thundering herd problem. Exponential backoff progressively multiplies delay durations between successive retry attempts (e.g., 1s, 2s, 4s, 8s), capped at a sensible upper bound to avoid indefinite postponement. Adding randomized jitter distributes retry spikes across a uniform window, decorrelating client requests and smoothing server traffic. In Kotlin coroutines, delay is cooperative and cancellable, ensuring that if a user navigates away during an active backoff window, the delay immediately unblocks with a CancellationException. Crucially, retries must strictly filter exceptions: only transient transport and server errors should be retried, whereas permanent 4xx client errors, authentication failures, and CancellationException must never trigger retries. Furthermore, non-idempotent operations must use persistent idempotency keys.

## Practical walkthrough (English)

A robust, production-ready retry implementation with exponential backoff, jitter, and cancellation safety:
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
            if (e is CancellationException) throw e // Never swallow cancellation!
            if (!isTransientError(e)) throw e // Do not retry 4xx client errors
        }
        val jitter = Random.nextLong(0, 500L)
        delay(minOf(currentDelay + jitter, maxDelayMs))
        currentDelay = (currentDelay * factor).toLong()
    }
    return block() // Final attempt executes without catching
}
```
In an erroneous design, catching generic Throwable or failing to check e is CancellationException will cause delay to catch cancellation and retry even after the enclosing ViewModel has been cleared, keeping leaked network requests running against dying components.

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

Exponential backoff doubles retry delays progressively while randomized jitter introduces random variance to prevent synchronized client retry storms. In coroutines, retries use cancellable delay, ensuring prompt termination if the parent scope cancels. Retries must strictly target transient errors (timeouts, 503) while immediately rethrowing client errors (4xx) and CancellationException. Non-idempotent mutations require durable idempotency keys.

## Interview answer — structured

Retrying network requests with exponential backoff and jitter is the standard architectural strategy for recovering from transient network failures. When backend servers face temporary load spikes, multiple mobile clients attempting immediate retries trigger a thundering herd that exacerbates backend collapse.

Exponential backoff multiplies the wait duration exponentially across successive attempts, while randomized jitter injects a uniform random offset to decorrelate concurrent client spikes.

In production, this is implemented using a bounded retry loop where suspension is handled via standard delay. Because delay is cooperatively cancellable, if the user exits the screen during a backoff period, the coroutine terminates immediately without waiting for the timer to expire.

Exception filtering is critical. The retry mechanism must exclusively target transient network faults such as socket timeouts, connection resets, and HTTP 502, 503, or 504 status codes. Permanent client errors like HTTP 400 Bad Request, 401 Unauthorized, and 404 Not Found must fail fast without retry. Above all, CancellationException must be rethrown immediately, preventing retries from becoming zombie processes.


## Interview answer — deep senior

At the systems engineering level, naive retries are one of the most common causes of cascading outages in distributed systems. When hundreds of thousands of mobile apps experience a transient micro-outage and retry with a fixed delay, their requests align into coherent pulse waves, repeatedly knocking recovering service clusters offline. Algorithms like Full Jitter or Equal Jitter distribute these requests across the entire interval, ensuring Poisson-like traffic distributions that servers can handle gracefully. When implementing this pattern with Kotlin coroutines, the interaction with structured concurrency demands rigorous scrutiny. The retry loop maintains state (such as the current delay and attempt index) within local stack frames. When delay executes, the coroutine unregisters its active execution thread and registers a delayed continuation in the dispatcher event loop. If the surrounding scope is cancelled—for instance, during a screen rotation or back-press where viewModelScope cancels—the active delay immediately throws a CancellationException. If the catch block intercepts generic Throwable or Exception without filtering, it will catch the CancellationException, trigger the next iteration, and launch another unwanted network request. This is why we strictly enforce checking if (e is CancellationException) throw e as the first line of any retry catch clause. Furthermore, idempotency dictates whether an operation is retry-safe. Idempotent operations like HTTP GET, PUT, and DELETE can safely be retried because executing them multiple times produces identical state mutations. In contrast, non-idempotent operations like HTTP POST for submitting an order or charging a credit card cannot be retried at the transport layer without a persistent, server-validated idempotency key. Without such keys, a dropped acknowledgment on an already-processed charge would result in duplicate billing if retried automatically.

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
