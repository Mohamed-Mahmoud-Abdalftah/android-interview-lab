---
id: "FLO-18"
question: "Compare catch, retry, retryWhen, and onCompletion."
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "B"
phase: 1
priority: "P1"
order: 131
editorial_status: "reviewed"
---

# FLO-18

## Original interview question

Compare catch, retry, retryWhen, and onCompletion.

## What the interviewer evaluates

Compare upstream catch, retry/retryWhen predicates and completion observation.

## Explanation in Arabic

`catch` تمسك exceptions من upstream اللي فوقها، وتقدر تطلع fallback؛ ما تمسكش خطأ `collect` اللي تحتها. `retry` و`retryWhen` يعيدوا collection للمصدر بعد failure حسب predicate، وده ممكن يعيد side effects في cold Flow. `onCompletion` يلاحظ النهاية/الخطأ/الإلغاء لكنه مش بدل catch. لازم `CancellationException` تفضل خارجة، والretry للقراءات أو operations idempotent فقط.

## Why it matters and how it works

Operator order defines which stages are covered. `retryWhen` exposes cause and attempt count for backoff; `retry` uses a simpler predicate. Upstream cold source is resubscribed, so repeatable side effects need safety. `onCompletion` can inspect cause and run cleanup, but failure still propagates unless separately caught.

## Worked example

JVM snippet retries transient read failures at most twice; cancellation remains propagated. The API call is read-only.

```kotlin
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.flow.*

fun readFeed(fetch: suspend () -> String): Flow<String> = flow { emit(fetch()) }
    .retryWhen { cause, attempt ->
        if (cause is CancellationException) throw cause
        val retryable = cause is java.io.IOException && attempt < 2
        if (retryable) kotlinx.coroutines.delay(200L * (attempt + 1))
        retryable
    }
    .catch { emit("cached") }
```

## Trade-offs and decision criteria

Catch can provide a user-visible fallback but may hide outages if telemetry is absent. Retry improves transient reliability but repeats cold upstream and can amplify load. onCompletion is suitable for logging or resource cleanup, not error recovery by itself.

## Failure modes

`catch` before a failing downstream `map` will not catch that map. A retry on a payment-writing flow can repeat the charge unless server idempotency is enforced. Treating cancellation as a retryable error keeps obsolete work alive.

## Production perspective

A feed repository retries transient read failures with capped backoff and then emits cached data, while recording refresh failure separately. Payment submission is modeled as durable operation state and server reconciliation, not a generic `retry` chain.

## Interview answer — short

“catch handles upstream exceptions; retry and retryWhen resubscribe upstream on selected failures; onCompletion observes how the flow ended. I preserve cancellation and only retry operations whose repeated execution is safe.”

## Interview answer — structured

“I place error operators deliberately. `catch` sees upstream failures and can emit fallback data, but cannot catch an exception thrown downstream in a later collector. `retry` and `retryWhen` restart the cold upstream; retryWhen gives attempt count for bounded backoff. `onCompletion` runs for normal completion, failure or cancellation and can inspect the cause, but does not automatically recover. I classify transient errors and never swallow cancellation. For remote writes I need an idempotency/reconciliation contract before resubscription is safe.”

## Interview answer — deep senior

“Flow error handling is location-sensitive. I draw the pipeline and mark the upstream each catch or retry covers. A retry reruns source code, including any network side effect inside a cold builder; that is safe for many reads but dangerous for non-idempotent writes. `retryWhen` supports attempt-based capped backoff and server guidance, but I bound total time and avoid retrying auth/validation errors. `catch` can convert a final read failure to cached data while telemetry records staleness. `onCompletion` is analogous to finally for observing cause and cleanup, not a replacement for result mapping. Tests inject upstream and downstream failures separately, cancel during delay and count actual source subscriptions.”

## Deep-dive talking points

Trace operator placement, resubscription side effects and cancellation during backoff.

## Follow-up questions

- [COR-18](../cor-18/): How bound retries? **Answer:** classify errors, cap attempts/delay, add jitter and preserve cancellation.
- [FLO-32](../flo-32/): Why avoid bare runCatching? **Answer:** it can convert cancellation to a normal result.

## Self-check rubric

Can I identify catch coverage, count resubscriptions, preserve cancellation and distinguish observation from recovery?

## References and reviewed-on date

- [Kotlin Flow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/) — exception transparency and operators.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
