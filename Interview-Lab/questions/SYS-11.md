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

نرسم operation boundaries: هل 3 calls كلهم مطلوبين؟ `coroutineScope` تفشل معًا؛ مستقلين؟ supervision مع outcomes منفصلة. timeout local deadline، مش rollback للسيرفر. retries للأخطاء المؤقتة فقط مع cap/backoff/jitter، وwrite لها operation ID ثابت وserver idempotency/status query. Shared state تحتاج Mutex/transaction حسب مكان invariant، وUI cancellation لا تلغي durable business work.

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

“I choose concurrency from result semantics, bound it, set deadlines and retry only classified safe operations. Cancellation stays cooperative. Writes use stable server-enforced idempotency keys and status reconciliation because timeout is not rollback.”

## Interview answer — structured

“For all-or-nothing parallel reads I use a structured scope that cancels siblings on failure; for independent cards I supervise and return separate outcomes. I limit fan-out separately from dispatcher selection. I apply a deadline and bounded backoff to transient reads while preserving cancellation. For writes, especially payment, I persist one operation ID and use backend idempotency and status lookup. Shared local state uses an appropriate lock or transaction, but the server owns cross-device invariants. Parallelism improves latency but can overload service; semaphores and server limits constrain it. Fast timeout improves UI but increases Unknown outcomes. Retrying reads is simpler than writes; idempotency backend support costs development but prevents duplicate financial effects. A checkout aggregates required quote calls with structured cancellation, limits fan-out, then submits one payment operation under durable ID.”

## Interview answer — deep senior

“I would define a per-operation policy matrix. It states dependency graph, failure aggregation, maximum parallelism, per-call/overall deadline, retryable errors and whether the operation has external side effects. Coroutines and scopes govern local cancellation; they do not roll back network work. A semaphore protects downstream capacity, Room transactions protect local invariants and backend transactions protect financial state. A timed-out read can often retry; a timed-out write is Unknown until server reconciliation using the same stable key. WorkManager provides restartable attempts after process death, and each attempt is repeat-safe. I test one child failing, slow cancellation, token refresh races, 429 backoff, duplicate worker runs and server-commit/client-response-loss. Scope hierarchy controls local lifetime, dispatcher selects execution, semaphore bounds fan-out, and database/server transactions protect invariants. Set per-call and overall deadlines, classify transient/permanent failures, respect 429 guidance and preserve CancellationException. Process death requires persisted pending operations and repeat-safe workers. An unawaited async child can still cancel parent. Catching CancellationException can trigger obsolete retries. A local Mutex cannot protect cross-device balance. A payment timeout retried with new key may charge twice. A checkout aggregates required quote calls with structured cancellation, limits fan-out, then submits one payment operation under durable ID. UI shows Pending on timeout and WorkManager reconciles. Metrics track dependency failure and unknown payment age.”

## Deep-dive talking points

Build a per-endpoint policy and test uncertainty at every boundary.

## Follow-up questions

- [COR-25](../cor-25/): What for all-or-nothing calls? **Answer:** coroutineScope cancels sibling work.
- [DAT-14](../dat-14/): Which retries safe? **Answer:** classified transient operations under idempotency contract.

## Self-check rubric

Can I separate local concurrency from server effects and justify deadline/retry/idempotency choices?

## References and reviewed-on date

- [Kotlin coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html) — structured cancellation.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable retry.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
