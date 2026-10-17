---
id: "DAT-14"
question: "How do you design retries while respecting idempotency and rate limits?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "B"
phase: 3
priority: "P1"
order: 271
editorial_status: "reviewed"
---

# DAT-14

## Original interview question

How do you design retries while respecting idempotency and rate limits?

## What the interviewer evaluates

Design retries from HTTP semantics, server throttling and operation identity.

## Concept and technical explanation

Designing resilient network retry architectures requires balancing recovery from transient failures against server protection and transactional safety:
- Idempotency & Operation Identity:
  * Safe vs Unsafe Retries: HTTP GET, PUT, and DELETE are idempotent by specification and can be retried automatically upon network dropouts. In contrast, POST requests modify server state (such as placing orders or charging payments).
  * Idempotency Keys: Mobile applications must inject client-generated UUIDs (e.g., X-Idempotency-Key) into mutable operations and persist them in Room alongside the pending request. This ensures that if a network timeout occurs after the server processed the transaction, retrying with the identical key deduplicates the operation on the backend without duplicate charges.
- Exponential Backoff with Jitter:
  * Exponential Delay Formula: Delay doubles with each successive failure: T = Base * 2^(attempt).
  * Full Jitter: Adding randomized randomness (delay = random(0, T)) breaks synchronization among thousands of mobile devices recovering from an outage, preventing the 'thundering herd' spike from crashing recovering infrastructure.
- Server Throttling & 429/503 Governance:
  * Parse Retry-After: When a backend returns HTTP 429 (Too Many Requests) or HTTP 503 (Service Unavailable), the client must extract the Retry-After header (in seconds or HTTP-date) and halt all retries until that window elapses.
  * Fatal Error Classification: Client errors (400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found) are non-transient and must fail immediately without retrying, conserving radio battery.

## Practical walkthrough (English)

Production retry policy combining exponential backoff, jitter, and Retry-After handling:
```kotlin
suspend fun <T> retryWithBackoff(
    maxAttempts: Int = 3,
    initialDelayMs: Long = 1000L,
    maxDelayMs: Long = 10000L,
    factor: Double = 2.0,
    block: suspend () -> Response<T>
): Response<T> {
    var currentDelay = initialDelayMs

    repeat(maxAttempts - 1) { attempt ->
        try {
            val response = block()
            if (response.isSuccessful) return response

            // 1. Handle Server Rate Limits (429 or 503)
            val statusCode = response.code()
            if (statusCode == 429 || statusCode == 503) {
                val retryAfterSec = response.headers()["Retry-After"]?.toLongOrNull() ?: (currentDelay / 1000)
                delay(retryAfterSec * 1000L)
            } else if (statusCode in 400..499) {
                // Fatal client error; do not retry
                return response
            }
        } catch (e: IOException) {
            // Transient network failure: proceed with jittered backoff
        }

        // 2. Exponential Backoff with Full Jitter
        val jitteredDelay = Random.nextLong(0, currentDelay)
        delay(jitteredDelay)
        currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelayMs)
    }

    return block() // Final attempt
}
```

## Explanation in Arabic

كيف تصمم استراتيجية إعادة المحاولة (Retry Strategy) مع احترام مبادئ الـ Idempotency وحدود معدل الطلبات (Rate Limits)؟

1. القواعد الذهبية لإعادة المحاولة (Retry Rules):
   - **فصل القراءة عن الكتابة (Read vs. Write)**:
     * طلبات القراءة (`GET`) آمنة ويمكن إعادة محاولتها تلقائياً.
     * طلبات الكتابة (`POST`) غير آمنة؛ لا تعيد محاولتها إلا إذا كانت تحتوي على **Idempotency Key** فريد وثابت.
   - **التمييز بين الأخطاء العابرة والدائمة (Transient vs. Permanent Errors)**:
     * أخطاء عابرة (Transient): انقطاع الشبكة المؤقت، مهلة الاتصال `ConnectTimeout`, أو أخطاء السيرفر `503 Service Unavailable`, `502 Bad Gateway` -> تستحق إعادة المحاولة.
     * أخطاء دائمة (Permanent): أخطاء التحقق `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found` -> **ممنوع إعادة المحاولة** لأنها ستفشل دائماً وتضيع بطارية الهاتف والموارد.

2. خوارزمية التراجع الأسي مع التشتت العشوائي (Exponential Backoff with Full Jitter):
   - لا تعيد المحاولة في نفس الثانية! كل محاولة فاشلة تضاعف وقت الانتظار: 1s ثم 2s ثم 4s ثم 8s.
   - **Full Jitter**: إضافة قيمة عشوائية (Random Offset) لوقت الانتظار. إذا انقطع السيرفر عن العمل، وعادت الشبكة لـ 100 ألف هاتف في نفس اللحظة، فإن الـ Jitter يمنع كل الهواتف من إعادة الطلب في نفس الثانية بالظبط، مما يحمي السيرفر من الانهيار (Thundering Herd Problem).

3. احترام ترويسة `429 Too Many Requests` و `Retry-After`:
   - إذا أرجع السيرفر كود `429` أو `503` مع ترويسة `Retry-After: 60`، يجب أن يعلق التطبيق جميع الطلبات لنفس الـ Endpoint لمدة 60 ثانية بالكامل.

## Practical walkthrough

تنفيذ خوارزمية Exponential Backoff with Jitter واحترام ترويسة Retry-After:
```kotlin
suspend fun <T> retryWithBackoff(
    maxAttempts: Int = 3,
    initialDelayMs: Long = 1000L,
    maxDelayMs: Long = 16000L,
    factor: Double = 2.0,
    block: suspend () -> T
): Result<T> {
    var currentDelay = initialDelayMs
    
    repeat(maxAttempts - 1) { attempt ->
        try {
            return Result.success(block())
        } catch (e: HttpException) {
            // 1. فحص كود 429 أو 503 مع احترام Retry-After:
            if (e.code() == 429 || e.code() == 503) {
                val retryAfterSeconds = e.response()?.headers()?.get("Retry-After")?.toLongOrNull()
                if (retryAfterSeconds != null) {
                    delay(retryAfterSeconds * 1000L)
                    return@repeat
                }
            }
            // 2. إذا كان الخطأ غير عابر (4xx): توقف فوراً ولا تعد المحاولة!
            if (e.code() in 400..499) return Result.failure(e)
        } catch (e: IOException) {
            // أخطاء اتصال عابرة (SocketTimeout / Network loss) -> مؤهلة لإعادة المحاولة
        }

        // 3. حساب Exponential Backoff مع Full Jitter لمنع الـ Thundering Herd:
        val jitter = Random.nextLong(0, currentDelay)
        delay(jitter)
        currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelayMs)
    }
    
    return runCatching { block() } // المحاولة الأخيرة
}
```

## Why it matters and how it works

HTTP status alone is not enough: a timeout can occur after server commit. Classify network failures and endpoint contract, persist write operation ID, and avoid retry storms. Retry-After may be a delay or date; parse per RFC and cap within product deadlines. Log attempts without sensitive payloads.

## Worked example

Conceptual Kotlin read retry; production injects clock/random and handles server Retry-After before this fallback.

```kotlin
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.delay

suspend fun <T> retryRead(call: suspend () -> T): T {
    repeat(3) { attempt ->
        try { return call() }
        catch (e: CancellationException) { throw e }
        catch (e: java.io.IOException) {
            if (attempt == 2) throw e
            delay(200L shl attempt)
        }
    }
    error("unreachable")
}
```

## Trade-offs and decision criteria

Extra retries improve transient success but amplify load and latency. Jitter and server guidance reduce synchronized bursts. A durable worker is appropriate for pending offline writes, but must use stable IDs and server deduplication.

## Failure modes

Retrying `401` forever can mask revoked credentials. Retrying validation `400` wastes bandwidth. A payment timeout followed by new POST key can create duplicate charge. Catching cancellation as IOException-like domain failure keeps work alive.

## Production perspective

A feed refresh uses bounded retries for network I/O, records stale cache on failure and respects rate limits. A reversal worker persists a key, consults server status and repeats only under the backend’s idempotency contract.

## Interview answer — short

Designing retries requires respecting idempotency by attaching client UUID keys to POST requests, applying exponential backoff with randomized jitter to prevent thundering herd spikes, and honoring Retry-After headers on 429 and 503 responses while failing client errors immediately.

## Interview answer — structured

A resilient mobile retry strategy must protect the backend from cascading collapse while recovering gracefully from flaky cellular connections.
First, retries must respect operation idempotency. While GET and PUT are safe to retry automatically, state-changing POST requests require unique client-generated idempotency keys to guarantee that network timeouts do not trigger duplicate transactions or charges.
Second, retry timing must incorporate exponential backoff with jitter. Rather than retrying at fixed intervals, the client doubles delay intervals and adds randomized variance, de-synchronizing thousands of client retries.
Third, the client must strictly adhere to server backpressure signals. When receiving HTTP 429 Too Many Requests or 503 Service Unavailable, the client parses the Retry-After header and suspends requests. Non-retryable 4xx client errors abort immediately to conserve battery.

## Interview answer — deep senior

In large-scale distributed systems, naive client retry loops frequently cause catastrophic self-inflicted Denial of Service (DoS) outages.
When an edge gateway experiences a transient hiccup, thousands of mobile clients fail simultaneously.
If every app retries immediately or at fixed 2-second intervals, the client fleet forms a synchronized wave of traffic that repeatedly hammers the recovering backend, keeping it down permanently in an outage death spiral.
To prevent this, our retry policy enforces three mandatory architectural rules.
First, we apply Full Jitter to our exponential backoff formula.
Randomizing the backoff sleep duration across the interval [0, Base * 2^attempt] flattens the retry curve into a smooth, manageable background distribution that allows servers to recover gracefully.
Second, we implement strict status code classification.
Transient transport failures like SocketTimeoutException and server 5xx codes warrant retries.
Conversely, client errors such as 400 Bad Request, 401 Unauthorized, or 403 Forbidden indicate non-recoverable state; retrying them is a bug that wastes CPU cycles and battery power.
When receiving a 429 or 503, our interceptor parses the Retry-After header and halts automated background sync for the specified duration.
Finally, for all mutating financial operations, we require an X-Idempotency-Key.
Even if a cellular connection drops and the client re-executes the transaction via WorkManager three hours later, the backend identifies the key and returns the cached receipt without charging the customer twice.

## How to answer in the interview

- **Why:** Retries can amplify outages or duplicate writes.
- **How:** Matrix by endpoint, error class, `Retry-After`, deadline and key.
- **Trade-offs:** Bound backoff/jitter against user latency.
- **Failure cases:** Global POST replay or endless 4xx retry.
- **Production solution:** Persist identity, reconcile uncertainty and test lost replies.

## Deep-dive talking points

Build retry matrix for GET versus financial POST; explain throttling and timeout ambiguity.

## Follow-up questions

- **Interviewer:** "What is the Thundering Herd Problem in mobile systems?"
  **Answer:** "When a major service outage recovers and thousands of mobile clients retry simultaneously, overwhelming server CPU and causing immediate cascading failures."

- **Interviewer:** "What does 'Full Jitter' mean mathematically?"
  **Answer:** "`sleep = random_between(0, min(max_backoff, initial_backoff * 2^attempt))`, which maximizes randomness and flattens traffic spikes."

## Self-check rubric

Can I classify errors, bound retries, honor Retry-After and protect writes?

## References and reviewed-on date

- [HTTP Semantics RFC 9110](https://httpwg.org/specs/rfc9110.html) — method/status semantics.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — queued write retry.

Technically reviewed against primary documentation on 2026-10-13.
