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

Design retries by distinguishing transient network/server errors (503, timeouts) from permanent client errors (400, 401, 404). Use exponential backoff with full jitter to prevent thundering herd spikes on the backend, respect server Retry-After headers on 429 status codes, and mandate client-side Idempotency Keys on all retried mutations.

## Interview answer — structured

A production-grade retry architecture balances user resilience against backend capacity.

First, **Error Classification**. Next, with Retryable (Transient), `SocketTimeoutException`, `UnknownHostException`, and HTTP `502`, `503`, `504`.
Additionally, with Non-Retryable (Permanent), client errors (`400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`). Retrying permanent errors burns battery and cellular quota without any chance of success. **Exponential Backoff with Full Jitter**.
Simple fixed delays (e.g. Retrying every 2 seconds) cause the **Thundering Herd Problem**: if an outage resolves, millions of devices retry at synchronized intervals, knocking the server offline again. Exponential backoff ($1s, 2s, 4s, 8s$) paired with randomized Jitter (`delay = Random(0, currentBackoff)`) spreads retry distribution smoothly across the timeline.
**Rate Limit Governance (`429 Too Many Requests`)**. Always parse the `Retry-After` header. If present, pause coroutines or queue execution for the server-requested duration rather than applying client backoff.
Finally, with Write Idempotency, never retry a mutating `POST` request unless backed by a persistent client-generated `Idempotency-Key`.


## Interview answer — deep senior

When designing background synchronization retries in Android, senior architects offload execution from in-memory coroutine loops to **`WorkManager`**.

If an in-memory coroutine retry loop is executing with a 30-second delay, and the user swipes the app away from recents, Android kills the process and cancels the coroutine, dropping the pending retry permanently.

By encapsulating offline retries inside WorkManager.

First, workManager persists the retry intent in its own SQLite database. Next, it supports native backoff policies: `setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)`.
Finally, it respects OS constraints (`NetworkType.CONNECTED`, battery not low), ensuring retries execute deterministically even after phone reboots.


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
