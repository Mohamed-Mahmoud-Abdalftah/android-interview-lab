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

## Concept and technical explanation

Designing client-side rate limiters and in-flight request deduplication systems requires choosing data structures that ensure thread-safety, bounded memory footprints, and low-latency execution:
- Sliding Window Log (Rate Limiting):
  - Architecture: A thread-safe map (`ConcurrentHashMap<String, ArrayDeque<Long>>`) mapping endpoint keys to queues of request epoch timestamps.
  - Algorithm: On an incoming request, purge timestamps older than `now - windowDuration` from the queue front. If remaining count is below the threshold, append `now` and approve; otherwise, throttle.
  - Complexity: Amortized $O(1)$ operations, exact boundary accuracy, with memory bounded by `maxRequestsPerWindow` timestamps per key.
- Token Bucket (Low-Footprint Rate Limiting):
  - Architecture: Tracks two primitive numeric variables per endpoint: `availableTokens: Double` and `lastRefillTimestamp: Long`.
  - Algorithm: On arrival, calculates tokens accumulated since last refill: `tokens += (now - lastRefill) * refillRate`. If `tokens >= 1.0`, decrement and allow; otherwise, reject.
  - Complexity: Strictly $O(1)$ constant time and $O(1)$ memory (only 16 bytes per endpoint), allowing burst capacity while smoothing traffic.
- In-Flight Request Deduplication (Coalescing):
  - Architecture: `ConcurrentHashMap<RequestKey, Deferred<Response>>`.
  - Algorithm: When a network request fires (such as repeated button taps or parallel screen initializations), inspect the map. If an active `Deferred` exists, await it directly without launching a second HTTP call.
  - Clean-up Invariant: A `finally` block or completion callback guarantees key removal upon request termination, preventing memory leaks and stale cached responses.

## Practical walkthrough (English)

Thread-safe Sliding Window Rate Limiter and Request Deduplicator in Kotlin:
```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentHashMap

// 1. Thread-safe Sliding Window Rate Limiter
class SlidingWindowRateLimiter(
    private val maxRequests: Int,
    private val windowDurationMs: Long
) {
    private val requestLogs = ConcurrentHashMap<String, ArrayDeque<Long>>()

    @Synchronized
    fun shouldAllowRequest(endpointKey: String): Boolean {
        val now = System.currentTimeMillis()
        val queue = requestLogs.getOrPut(endpointKey) { ArrayDeque() }

        // Evict expired timestamps outside the active window
        while (queue.isNotEmpty() && (now - queue.first()) > windowDurationMs) {
            queue.removeFirst()
        }

        return if (queue.size < maxRequests) {
            queue.addLast(now)
            true // Request permitted
        } else {
            false // Throttled
        }
    }
}

// 2. Coroutine-based In-Flight Request Deduplicator
class RequestDeduplicator {
    private val inFlight = ConcurrentHashMap<String, Deferred<String>>()

    suspend fun executeDeduplicated(key: String, networkCall: suspend () -> String): String {
        val deferred = inFlight.compute(key) { _, existing ->
            existing ?: CoroutineScope(Dispatchers.IO).async {
                try {
                    networkCall()
                } finally {
                    inFlight.remove(key) // Guaranteed memory cleanup
                }
            }
        }!!
        return deferred.await()
    }
}
```

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

Implement a rate limiter using a sliding window log via ConcurrentHashMap and ArrayDeque for precise timestamp eviction, or a Token Bucket for minimal O(1) memory overhead. Deduplicate in-flight requests using a ConcurrentHashMap of Coroutine Deferred instances, allowing concurrent calls to share a single network invocation with guaranteed cleanup in a finally block.

## Interview answer — structured

Designing rate limiting and request deduplication on Android requires matching data structures to specific concurrency and memory constraints.
For rate limiting with strict boundary precision, the sliding window log is an excellent fit. It utilizes a ConcurrentHashMap mapping endpoint keys to an ArrayDeque of timestamps. When a request arrives, timestamps older than the active window are evicted from the queue. If the remaining count is within limits, the request proceeds, delivering amortized O(1) performance.
If memory efficiency is paramount, the Token Bucket algorithm stores just two numbers per endpoint: current tokens and last refill timestamp. It runs in strictly O(1) constant time and negligible memory, smoothly accommodating bursts.
For request deduplication, we use a ConcurrentHashMap mapping request keys to active Coroutine Deferred objects. When duplicate requests fire simultaneously, subsequent callers attach to the in-flight Deferred rather than spawning duplicate network requests. An explicit finally block guarantees map eviction upon completion, preventing memory leaks.

## Interview answer — deep senior

From a high-concurrency client systems perspective, request governance mechanisms protect both mobile battery life and backend microservices from accidental Denial of Service conditions.
When architecting a client-side rate limiter, the sliding window log offers superior accuracy compared to fixed-window counters, which suffer from boundary traffic spikes where double the limit executes across the reset boundary. By maintaining a timestamp queue inside an ArrayDeque, we achieve amortized O of one eviction. However, if thousands of unique parameterized query keys are generated, the map can grow unbounded. We resolve this by constraining the map with an LRU eviction policy or adopting the Token Bucket algorithm. Token Bucket calculates available capacity lazily through timestamp deltas, requiring only two numeric primitives per key and zero object allocations during active traffic.
Request deduplication requires atomic state coordination. A frequent bug in Android networking occurs when a user repeatedly taps a purchase or refresh button, or when multiple ViewModels request the same user profile simultaneously. If unmanaged, the app initiates redundant HTTP requests, wasting cellular data and risking duplicate state mutations.
By maintaining a ConcurrentHashMap of Coroutine Deferred objects, we coalesce duplicate requests atomically. The first caller initiates the network call and registers the Deferred. Concurrent callers atomically acquire the existing Deferred and await the identical response. To ensure fault tolerance and prevent memory leaks, we wrap the execution in a try-finally construct that removes the key from the map upon completion or cancellation. This architecture guarantees single-flight network efficiency with ironclad thread safety.

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
