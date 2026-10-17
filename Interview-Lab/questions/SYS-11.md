---
id: "SYS-11"
question: "How do you deal with concurrency, timeouts, retries, and idempotency?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "B"
phase: 4
priority: "P1"
order: 340
editorial_status: "reviewed"
---

# SYS-11

## Original interview question

How do you deal with concurrency, timeouts, retries, and idempotency?

## What the interviewer evaluates

Integrate concurrency, deadlines, retry and idempotency by operation semantics.

## Concept and technical explanation

Enterprise mobile applications operate across unpredictable network topologies, intermittent connectivity drops, and concurrent background synchronizations. Robust system design mandates a coordinated approach to concurrency, timeouts, retries, and idempotency. Concurrency must be governed through structured coroutines where parent scopes bind child tasks, preventing leaked background operations upon screen dismissal. Timeouts must be categorized based on operation semantics: aggressive deadlines for user-facing reads and extended deadlines with explicit progress indicators for critical mutations. Retrying network requests blindly leads to retry storms that exhaust device batteries and overload backend infrastructure. Retries should apply strictly to transient infrastructure failures using truncated exponential backoff with full jitter, while immediately failing deterministic client errors. Crucially, non-idempotent mutations like payment authorizations or order placements must transmit unique client-generated idempotency keys, guaranteeing that duplicate network packets caused by timeout recovery never trigger duplicate server side mutations.

## Practical walkthrough (English)

Implementing resilient mutations with exponential backoff jitter and idempotency keys:
```kotlin
// 1. Client-generated mutation request with unique idempotency envelope
data class PaymentRequest(
    val idempotencyKey: String = UUID.randomUUID().toString(),
    val accountId: String,
    val amountCents: Long,
    val currency: String
)

// 2. Retry execution policy with full jitter backoff algorithm
class ResilientNetworkExecutor @Inject constructor() {
    suspend fun <T> executeWithRetry(
        maxAttempts: Int = 3,
        initialDelayMs: Long = 1000L,
        maxDelayMs: Long = 8000L,
        block: suspend () -> T
    ): Result<T> {
        var currentAttempt = 0
        while (currentAttempt < maxAttempts) {
            try {
                // Enforce strict cooperative deadline per attempt
                return withTimeout(5000L) {
                    Result.success(block())
                }
            } catch (e: Exception) {
                currentAttempt++
                // Never retry client-side validation errors or deliberate cancellations
                if (e is CancellationException) throw e
                if (e is HttpException && e.code() in 400..499 && e.code() != 429) {
                    return Result.failure(e)
                }
                if (currentAttempt >= maxAttempts) return Result.failure(e)

                // Exponential backoff calculation with full randomized jitter
                val exponentialDelay = (initialDelayMs * 2.0.pow(currentAttempt - 1)).toLong().coerceAtMost(maxDelayMs)
                val jitteredDelay = Random.nextLong(0, exponentialDelay)
                delay(jitteredDelay)
            }
        }
        return Result.failure(IllegalStateException("Exhausted retries"))
    }
}
```

## Explanation in Arabic

كيف تتعامل مع التزامن (Concurrency)، فترات الانتظار (Timeouts)، إعادة المحاولة (Retries)، وعدم التكرار (Idempotency) في بيئات الموبايل؟

1. إدارة التزامن (Concurrency Management via Coroutines):
   - **تجنب الـ Shared Mutable State**: استخدام `StateFlow` و `SharedFlow` غير القابلة للتعديل خارج الـ ViewModel.
   - **Mutex لحماية العمليات الحرجة**: منع تشغيل عمليتين حساستين معاً (مثل محاولة تجديد التوكن مرتين أو دفع فاتورة مرتين) باستخدام `kotlinx.coroutines.sync.Mutex`.
   - **إلغاء العمليات السابقة (Canceling Stale Jobs)**: استخدام `collectLatest` أو إلغاء الـ `Job` السابق عند قيام المستخدم بالبحث المتكرر لمنع إهدار الموارد وعرض نتائج قديمة (Race Conditions).

2. فترات الانتظار (Timeouts):
   - تحديد فترات انتظار دقيقة ومخصصة على مستوى OkHttp: `connectTimeout` (10s), `readTimeout` (15s), `writeTimeout` (15s).
   - استخدام `withTimeout(duration) { ... }` في Coroutines للعمليات التي تعتمد على معالجة محلية أو تدفقات بيانات غير منتهية.

3. استراتيجية إعادة المحاولة الذكية (Exponential Backoff with Full Jitter):
   - **الكارثة**: إعادة المحاولة فوراً وبشكل ثابت (مثل كل ثانية) يؤدي إلى هجوم حرمان خدمة ذاتي (Self-inflicted DDoS) على السيرفر عند تعافيه!
   - **الحل الصحيح**: تأخير تضاعفي مع عشوائية كاملة:
     `delay = min(maxDelay, baseDelay * (2 ^ attempt)) + Random(0, jitter)`.

4. عدم التكرار (Idempotency):
   - العمليات غير القابلة للتكرار بطبيعتها (مثل POST لإنشاء طلب أو تحويل أموال) يجب أن تُرفق بـ `Idempotency-Key` (UUID) منشأ في العميل لضمان معالجتها مرة واحدة فقط على السيرفر.

## Practical walkthrough

تنفيذ دالة تنفيذ شبكي مرنة ومقاومة للأخطاء مع Exponential Backoff و Jitter ومعالجة الـ Idempotency:
```kotlin
suspend fun <T> executeWithRetry(
    maxRetries: Int = 3,
    baseDelayMs: Long = 1000L,
    maxDelayMs: Long = 10000L,
    block: suspend () -> T
): Result<T> {
    var currentAttempt = 0
    while (currentAttempt < maxRetries) {
        try {
            return Result.success(block())
        } catch (e: IOException) {
            currentAttempt++
            if (currentAttempt >= maxRetries) return Result.failure(e)
            
            // حساب Exponential Backoff مع Full Jitter لمنع الـ Thundering Herd:
            val exponential = (baseDelayMs * (1 shl (currentAttempt - 1))).coerceAtMost(maxDelayMs)
            val jitter = Random.nextLong(0, exponential)
            delay(jitter)
        } catch (e: Exception) {
            // الأخطاء غير القابلة للتعافي (مثل 400 Bad Request أو 403 Forbidden) لا يُعاد محاولتها
            return Result.failure(e)
        }
    }
    return Result.failure(IllegalStateException("Exhausted retries"))
}
```

## Why it matters and how it works

Scope hierarchy controls local lifetime, dispatcher selects execution, semaphore bounds fan-out, and database/server transactions protect invariants. Set per-call and overall deadlines, classify transient/permanent failures, respect 429 guidance and preserve CancellationException. Process death requires persisted pending operations and repeat-safe workers.

## Worked example

Conceptual policy table; real implementation should test each endpoint contract.

```kotlin
data class OperationPolicy(
    val allResultsRequired: Boolean,
    val maxParallelCalls: Int,
    val deadlineMs: Long,
    val retryableRead: Boolean,
    val requiresIdempotencyKey: Boolean,
)
// A payment write uses requiresIdempotencyKey=true and status reconciliation.
```

## Trade-offs and decision criteria

Parallelism improves latency but can overload service; semaphores and server limits constrain it. Fast timeout improves UI but increases Unknown outcomes. Retrying reads is simpler than writes; idempotency backend support costs development but prevents duplicate financial effects.

## Failure modes

An unawaited async child can still cancel parent. Catching CancellationException can trigger obsolete retries. A local Mutex cannot protect cross-device balance. A payment timeout retried with new key may charge twice.

## Production perspective

A checkout aggregates required quote calls with structured cancellation, limits fan-out, then submits one payment operation under durable ID. UI shows Pending on timeout and WorkManager reconciles. Metrics track dependency failure and unknown payment age.

## Interview answer — short

We handle mobile network instability by binding operations to structured coroutine scopes with explicit timeouts and exponential backoff jitter. We retry strictly transient errors like socket drops and server rate limits, while pairing all mutating network requests with client-generated idempotency keys to prevent duplicate transactions.

## Interview answer — structured

A resilient mobile communication layer coordinates timeouts, retries, and idempotency to survive flaky cellular networks without corrupting backend state.
I structure network operations within structured coroutine scopes, ensuring background jobs cancel cooperatively when the hosting lifecycle terminates.
Timeouts are tailored to intent: fast five-second deadlines for read operations to display cached data quickly, and longer fifteen-second windows for critical mutations paired with clear UI progress feedback.
For retries, I restrict repeated attempts strictly to transient network dropouts and server rate limits. Deterministic client errors like bad credentials fail immediately.
Retries always execute using truncated exponential backoff randomized with full jitter to prevent thundering herd spikes on backend clusters.
For any state-mutating operation like placing an order or making a payment, the client generates a unique idempotency UUID and persists it locally before transmission, allowing safe retries over ambiguous timeout failures.

## Interview answer — deep senior

From a staff systems engineering perspective, handling network failure requires distinguishing between transport failure and application outcome ambiguity.
When an HTTP mutation times out, the client cannot know whether the server never received the packet, processed the transaction and crashed, or responded while the cellular tower dropped the downlink. Treating timeouts as outright failures leads to dangerous UX errors. By persisting the idempotency key in local storage alongside the pending transaction, our retry engine safely resubmits the exact same token. The backend detects the existing key, bypasses duplicate processing, and returns the original transaction outcome.
Mobile devices frequently experience split-brain network transitions when switching between Wi-Fi and mobile data mid-transfer. This causes TCP sockets to hang indefinitely without returning an RST packet. We guard against this by configuring strict OkHttp call timeouts alongside coroutine withTimeout deadlines to enforce deterministic termination.
For high-volume background synchronizations, naive retry loops quickly drain device batteries. We delegate offline backlogs to WorkManager, utilizing OS-level constraints such as unmetered Wi-Fi and battery not low, paired with platform-managed exponential backoff.
Inside the client process, concurrency races on shared mutable state are neutralized by routing operations through single-threaded coroutine dispatchers or Mutex locks rather than broad JVM synchronized blocks.
Finally, we implement circuit breaker patterns on mobile clients. If successive calls to a downstream service experience continuous timeouts, the client temporarily trips the circuit, serving cached fallbacks immediately for a cooldown period to protect system responsiveness and prevent radio exhaustion.

## How to answer in the interview

- **Why:** operation semantics determine concurrency and retry policy.
- **How:** classify dependencies, set deadlines and limits, and assign stable IDs to writes.
- **Trade-off:** retries improve transient success but add load and latency.
- **Failure case:** timed-out payment retried with a new identity.
- **Production solution:** cancellation tests, idempotent backend contract, and status reconciliation.

## Deep-dive talking points

Build a per-endpoint policy and test uncertainty at every boundary.

## Follow-up questions

- **Interviewer:** "What is Full Jitter in retry backoff algorithms?"
  **Answer:** "Selecting a random delay between 0 and the calculated exponential ceiling, spreading retries evenly across time to prevent clustered spikes."

- **Interviewer:** "Why should you never retry an HTTP 401 response using a standard retry interceptor?"
  **Answer:** "401 indicates invalid authentication credentials; retrying without refreshing tokens will fail repeatedly and lock user accounts."

## Self-check rubric

Can I separate local concurrency from server effects and justify deadline/retry/idempotency choices?

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — structured cancellation.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable retry.

Technically reviewed against primary documentation on 2026-10-13.
