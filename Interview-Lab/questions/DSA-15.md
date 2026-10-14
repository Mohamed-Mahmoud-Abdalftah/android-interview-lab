---
id: "DSA-15"
question: "Build a rate limiter or deduplication map for requests. What data structure fits?"
topic: "Data Structures, Algorithms & Big O"
code: "DSA"
group: "C"
phase: 5
priority: "P2"
order: 454
editorial_status: "reviewed"
---

# DSA-15

## Original interview question

Build a rate limiter or deduplication map for requests. What data structure fits?

## What the interviewer evaluates

- Rate limiter versus dedup map semantics and expiry.
- Local map is not payment-wide exactly-once authority.

## Explanation in Arabic

كيف تبني نظام تحديد معدل الطلبات (Rate Limiter) أو خريطة لمنع تكرار الطلبات المتزامنة (Request Deduplication) في أندرويد، وما هو الهيكل الأنسب؟

1. متطلبات النظام:
   - **Rate Limiting**: السماح بحد أقصى من الطلبات (مثلاً: 5 طلبات في الثانية) ورفض أو تأخير الطلبات الزائدة.
   - **Request Deduplication**: إذا تم استدعاء نفس الـ API بنفس المعاملات 3 مرات بالتوازي قبل اكتمال الطلب الأول، يتم تنفيذ **طلب شبكة واحد فقط** ومشاركة النتيجة مع المستدعين الثلاثة (Coalescing).

2. اختيار هياكل البيانات المناسبة:
   - **للـ Rate Limiting (خوارزمية Sliding Window Log)**:
     * **`ArrayDeque<Long>`**: لتخزين الطوابع الزمنية (Timestamps) للطلبات الأخيرة.
     * عند كل طلب جديد: نزيل الطوابع الأقدم من (`now - windowSize`) من بداية الـ Deque في $O(1)$.
     * إذا كان حجم الـ Deque أقل من الحد المسموح، نضيف الوقت الحالي ونقبل الطلب، وإلا نرفضه.
   - **للـ Deduplication (دمج الطلبات المتزامنة)**:
     * **`ConcurrentHashMap<String, Deferred<Response>>`** (مع Kotlin Coroutines):
     * إذا كان المفتاح موجوداً في الخريطة، نقوم بعمل `await()` على نفس النتيجة الجاري تحميلها دون فتح اتصال جديد!
     * عند انتهاء الطلب، نزيل المفتاح من الخريطة في بلوك `finally`.

## Practical walkthrough

تنفيذ Rate Limiter و Request Deduplication في كوتلن بشكل آمن ومتزامن:
```kotlin
// 1. Sliding Window Rate Limiter آمن الخيوط (Thread-Safe):
class SlidingWindowRateLimiter(private val maxRequests: Int, private val windowDurationMs: Long) {
    private val timestamps = ArrayDeque<Long>()
    private val lock = Any()

    fun tryAcquire(): Boolean = synchronized(lock) {
        val now = System.currentTimeMillis()
        // إزالة الطوابع الزمنية المنتهية الصلاحية من بداية الطابور:
        while (timestamps.isNotEmpty() && (now - timestamps.first()) > windowDurationMs) {
            timestamps.removeFirst()
        }
        if (timestamps.size < maxRequests) {
            timestamps.addLast(now)
            true // مسموح بالطلب
        } else {
            false // تم تجاوز المعدل (Rate limited)
        }
    }
}

// 2. Request Deduplicator (Single-Flight Pattern) باستخدام Coroutines:
class RequestDeduplicator<T> {
    private val inFlight = ConcurrentHashMap<String, Deferred<T>>()

    suspend fun execute(key: String, block: suspend () -> T): T = coroutineScope {
        val deferred = inFlight.computeIfAbsent(key) {
            async(Dispatchers.IO) { block() }
        }
        try {
            deferred.await() // ينتظر الطلب المشترك
        } finally {
            inFlight.remove(key, deferred) // تنظيف بعد الاكتمال
        }
    }
}
```

## Why it matters and how it works

Token bucket stores tokens, capacity and last-refill time per key; each request refills by elapsed monotonic time and consumes atomically. Dedup state maps stable identity to immutable parameters and prior result, with TTL and concurrency control. Eviction must not precede provider retention/reconciliation needs.

## Worked example

For search typing, an in-memory map keyed by query can coalesce requests and expire entries. For payment POST, backend durable store has unique operation ID and compares amount/order; Android persists same ID and queries status after timeout. Do not use a client LRU as financial ledger.

This in-process limiter is only a UI/network-load guard; it is not a financial deduplication authority. Injecting monotonic time makes boundary tests deterministic, and a server-side durable key remains necessary for one business effect.

```kotlin
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

private class RequestLimiter(
    private val windowMillis: Long,
    private val nowMillis: () -> Long
) {
    private val lastAccepted = mutableMapOf<String, Long>()

    fun accept(key: String): Boolean {
        val now = nowMillis()
        val previous = lastAccepted[key]
        if (previous != null && now - previous < windowMillis) return false
        lastAccepted[key] = now
        return true
    }
}

class RateLimiterExampleTest {
    @Test fun acceptsAtBoundaryForSameKey() {
        var now = 0L
        val limiter = RequestLimiter(1_000) { now }
        assertEquals(true, limiter.accept("search"))
        now = 999
        assertEquals(false, limiter.accept("search"))
        now = 1_000
        assertEquals(true, limiter.accept("search"))
        assertEquals(true, limiter.accept("other"))
    }
}
```

The simple map needs a retention policy and synchronization if callers access it concurrently; a distributed rate limit belongs on the server.

## Trade-offs and decision criteria

Hash maps give expected O(1) lookup but need memory bounds and cleanup. A sliding-window limiter can be more precise but store more timestamps. Distributed rate limiting needs shared atomic state; local per-device limits are bypassable.

## Failure modes

Wall clock moves backward, making refill wrong; use monotonic time for in-process limiter and server time/transaction semantics for distributed policy. Concurrent check-then-put without lock permits duplicates.

## Production perspective

Production limits by authenticated identity and endpoint, monitors denial rates, and distinguishes abuse throttling from financial idempotency. Test eviction, concurrency and process death.

## Interview answer — short

For a rate limiter, a sliding window log using an ArrayDeque of timestamps fits best, pruning expired entries in O(1) amortized time. For concurrent request deduplication, use a ConcurrentHashMap mapping request keys to in-flight Coroutine Deferred instances (Single-Flight pattern), coalescing concurrent duplicate calls into a single network invocation.

## Interview answer — structured

Designing rate limiters and deduplication managers requires thread-safe collections tailored to sliding time windows and task coalescing.

First, **Sliding Window Rate Limiter (`ArrayDeque<Long>`)**. Next, a Mechanism maintains timestamps of recent requests in an `ArrayDeque`. On each incoming request at time $t$, pop timestamps older than $t - \text{windowDuration}$ from the head in $O(1)$ time. If the remaining deque size is within limits, push $t$ to the tail and allow the request; otherwise, throttle.
Additionally, a Trade-off provides exact precision without the boundary burst vulnerabilities of fixed-window counters, consuming minimal $O(k)$ memory where $k$ is the rate limit. **Concurrent Request Deduplication (Single-Flight Pattern)**.
With Mechanism, use a `ConcurrentHashMap<String, Deferred<Result>>`. When a request arrives, invoke `computeIfAbsent(key) { async { executeNetworkCall() } }`. Multiple concurrent callers subscribe to the identical `Deferred.await()`, eliminating duplicate network traffic. Finally, with Cleanup, in a `finally` block, remove the key from the map once the network call completes to ensure subsequent requests fetch fresh data.


## Interview answer — deep senior

From an Android networking and resilience perspective, these patterns protect battery and server quotas.

First, with Thundering Herd Mitigation on Screen Launch, when 4 distinct UI components on a dashboard independently request the current user profile upon startup, naive code fires 4 duplicate HTTP requests. The Single-Flight deduplication pattern coalesces these into 1 HTTP call, saving radio wakeups and network bandwidth. Next, with Token Bucket Algorithm Alternative, for high-throughput client scenarios, the Token Bucket algorithm (`AtomicInteger` tokens replenished at a constant rate) is preferred over timestamp deques because it consumes $O(1)$ space and handles traffic bursts gracefully without logging individual timestamps.
Finally, with Handling Network Failures in Deduplication, if the in-flight network call fails with an exception, all awaiting callers must receive the exception cleanly, and the key must be removed from the map immediately so retry logic is not stuck on a failed cached future.


## How to answer in the interview

- **Why:** duplicate requests waste capacity or money.
- **How:** define key, clock, window and concurrency.
- **Trade-off:** memory/burst allowance versus throttling.
- **Failure case:** in-memory map called payment dedup.
- **Production solution:** server identity for business effects.

## Deep-dive talking points

Prompt for token bucket state, atomic check-and-set, monotonic time, TTL and payment authority.

## Follow-up questions

- **Interviewer:** "What is the primary advantage of the sliding window log over a fixed-window counter for rate limiting?"
  **Answer:** "It prevents the double-burst edge case where twice the allowed requests arrive across the boundary between two adjacent fixed windows."

- **Interviewer:** "Why is `remove(key, deferred)` preferred over `remove(key)` in the deduplication cleanup block?"
  **Answer:** "It atomically ensures you only remove the entry if it still points to the exact completed task, avoiding race conditions with newly started requests."

## Self-check rubric

Choose map/set plus timestamp or token bucket according to exact rate/dedup semantics; bound memory, define expiration and concurrency, and test collisions and burst behavior.

## References and reviewed-on date

- [Kotlin Map API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/-map/) — map operations.
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — financial retry semantics.

Technically reviewed against primary documentation on 2026-10-13.
