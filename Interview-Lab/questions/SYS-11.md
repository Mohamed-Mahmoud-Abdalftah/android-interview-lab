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

Manage concurrency via structured coroutines and Mutex locks, enforce fine-grained network and coroutine timeouts, apply exponential backoff with full jitter to avoid thundering-herd server spikes, and use client-generated UUID idempotency keys to guarantee at-most-once mutation semantics.

## Interview answer — structured

Building resilient network and data layers requires coordinating concurrency, time bounds, and retry semantics:

1. **Structured Concurrency & Race Conditions**:
   - Scope coroutines strictly to their lifecycle owners (`viewModelScope`, WorkManager). Avoid unstructured `GlobalScope`.
   - Eliminate shared mutable state using atomic primitives or `Mutex`. For search autocomplete or rapid filter clicks, use `collectLatest` or cancel active jobs to drop obsolete responses.

2. **Fine-Grained Timeouts**:
   - Configure distinct OkHttp timeouts: short connect timeouts (10s) to detect dead networks rapidly, and appropriate read/write timeouts (15–30s) for payloads. Wrap sensitive domain operations in `withTimeoutOrNull` to guarantee UI unblocking.

3. **Exponential Backoff with Full Jitter**:
   - When an outage occurs, millions of mobile clients retrying at synchronized intervals will overwhelm recovered servers. Calculate delays using exponential backoff randomized with full jitter: `delay = Random(0, base * 2^attempt)`. Never retry non-idempotent 4xx client errors (e.g. 400, 401, 422).

4. **Idempotency Keys**:
   - For state-altering mutations (payments, order creation), attach a client-generated UUID `Idempotency-Key` header. If a network timeout prompts a retry, the backend processes the request safely without duplicating effects.

## Interview answer — deep senior

From a staff-level systems perspective, retry and concurrency policies must be designed end-to-end:

1. **The Circuit Breaker Pattern on Mobile**: If network calls repeatedly fail with 503 Service Unavailable or consecutive timeouts, the mobile client should trip a local **Circuit Breaker**. For the next 60 seconds, fail requests immediately with cached error state without hitting the cellular radio, preserving device battery and giving the backend breathing room.

2. **Safe Idempotent Methods vs. Unsafe Mutations**: RFC 7231 defines GET, PUT, and DELETE as inherently idempotent. Retrying GET or PUT is safe. Retrying POST is hazardous. Explicitly distinguish between safe retry policies (transparently retrying idempotent read queries) and guarded retry policies (requiring user confirmation or idempotency keys for mutations).

3. **Coroutine Cancellation Cooperativeness**: Ensure custom background loops and heavy data parsing check `isActive` or invoke `ensureActive()`. If a coroutine does not yield, cancellation requests triggered by screen departures or timeouts will be ignored, resulting in leaked background compute.

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
