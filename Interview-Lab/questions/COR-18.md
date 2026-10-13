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

الـretry الصح مش `while(true)` بسرعة. بنحدد أخطاء transient بس، عدد محاولات وdeadline، delay بيتضاعف مع cap وjitter لتقليل thundering herd. لازم `CancellationException` توقف الحلقة فورًا، وطلبات الكتابة ما تتعادش من غير idempotency contract أو reconciliation. `Retry-After` وقيود السيرفر لها أولوية لو موجودة.

## Practical walkthrough

لو خدمة قراءة catalog رجّعت 503، جرّب تاني بـexponential backoff وjitter عشان كل العملاء ما يرجعوش في نفس اللحظة. لازم توقف عند عدد محاولات أو overall deadline، وما تكرر 401 أو validation error. `delay` قابل للإلغاء؛ لو الشاشة اتقفلت خلال الانتظار، ارمِ الإلغاء بدل محاولة إضافية. عمليات الكتابة تحتاج idempotency قبل أي retry.

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

“I retry only classified transient failures, with a bounded attempt count, capped exponential backoff and jitter. `delay` stays cancellable and I rethrow cancellation. For writes, I require a stable idempotency key and server reconciliation rather than blindly resending.”

## Interview answer — structured

“A retry policy is part of an API contract. I classify errors first, then set a maximum attempt count or deadline, increase delay exponentially with a cap, and add jitter so clients do not stampede the service. `delay` gives cancellation a chance to stop the loop, and I never catch cancellation as a retryable exception. Reads are usually simpler. For non-idempotent writes such as payment I persist a stable operation ID, follow the server’s idempotency and status-query contract, and treat timeouts as uncertain outcomes.”

## Interview answer — deep senior

“Production retry design needs safety and operability, not just a delay formula. I separate transport failures from validation/auth failures, honor server retry guidance such as `Retry-After` where specified, bound total elapsed time, and cap the exponential calculation to avoid overflow. Full jitter spreads clients; tests inject the random source and virtual clock. For UI reads the ViewModel can cancel retries when the screen goes away. For durable sync I persist enough state for WorkManager to resume after process death. For writes, a stable idempotency key can let the server deduplicate requests, but it does not prove exactly-once network delivery; I query authoritative transaction state before deciding whether another attempt is safe. I would define the retry budget before writing the loop: maximum attempts, total deadline, retryable status codes, and an idempotency rule. Full jitter spreads clients after a 503 rather than causing a synchronized second spike. `delay` is cancellable, so closing the screen during backoff should stop the next request. Metrics should include attempt count and final cause, without treating a cancelled request as a service failure.”

## How to answer in the interview

- **Why:** transient failures are recoverable, synchronized retries are harmful.
- **How:** classify failures, cap exponential delay, add jitter, and stop at an overall deadline.
- **Trade-off:** retries increase tail latency and load.
- **Failure case:** retrying auth errors or a non-idempotent write duplicates effects.
- **Production solution:** share a retry budget, preserve cancellation, and instrument attempt counts.

## Deep-dive talking points

Defend error classification, cap/jitter math, cancellation, process death and payment retry safety.

## Follow-up questions

- [COR-17](../cor-17/): What does timeout mean? **Answer:** the caller stopped waiting; server commit status may remain unknown.
- [COR-27](../cor-27/): How retry payment? **Answer:** reuse a durable key under a server idempotency contract and reconcile status.

## Self-check rubric

Can I state retryable errors, bound attempts/time, preserve cancellation, add jitter and explain write safety?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — retry and sync design.
- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — cancellable delay.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
