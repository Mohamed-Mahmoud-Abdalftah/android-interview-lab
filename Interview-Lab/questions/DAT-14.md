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

الـretry لازم يفرق بين read وwrite، وبين transient failure وvalidation/auth error. نستخدم max attempts/total deadline، exponential backoff مع jitter، ونحترم `Retry-After` في `429`/`503` إذا السيرفر رجّعه. `GET` غالبًا قابل للإعادة؛ `POST` مالي يحتاج idempotency key ثابت وstatus reconciliation. الـcancellation توقف loop، وWorkManager retries لا تعني exactly-once.

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

“I retry classified transient failures with bounded exponential backoff and jitter, honor server throttling, and stop on cancellation. Writes require stable idempotency and reconciliation; a timeout is not proof that nothing happened.”

## Interview answer — structured

“Retry policy depends on operation semantics. For a read I may retry connection failures and selected server errors, with an attempt cap, overall deadline, backoff and jitter. I respect Retry-After for throttling and fail fast on validation or permanent authentication errors. For a write, especially payment, I persist a stable operation key and query authoritative status after an uncertain timeout before sending again. Cancellation must terminate the policy, and metrics should show attempts and final outcome.”

## Interview answer — deep senior

“I would design a retry matrix per endpoint, not a global interceptor that repeats every request. Method semantics, server idempotency contract, error class and user deadline all matter. I cap retries and backoff, add jitter to prevent a fleet-wide surge, parse Retry-After where relevant, and apply circuit/rate limits if the backend is unhealthy. A lost response can follow a committed write, so the app records a durable operation ID and reconciles status; using the same key can make the logical operation idempotent only if the server enforces it. WorkManager may run a worker again after crash; that is why server-side deduplication and local state transitions are essential. Tests cover cancellation and duplicate execution. Log attempts without sensitive payloads. Retrying validation `400` wastes bandwidth.”

## Deep-dive talking points

Build retry matrix for GET versus financial POST; explain throttling and timeout ambiguity.

## Follow-up questions

- [DAT-02](../dat-02/): Does POST retry safely by default? **Answer:** no; it needs an endpoint-specific idempotency contract.
- [DAT-20](../dat-20/): What after lost payment response? **Answer:** reconcile server state before another send.

## Self-check rubric

Can I classify errors, bound retries, honor Retry-After and protect writes?

## References and reviewed-on date

- [HTTP Semantics RFC 9110](https://httpwg.org/specs/rfc9110.html) — method/status semantics.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — queued write retry.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
