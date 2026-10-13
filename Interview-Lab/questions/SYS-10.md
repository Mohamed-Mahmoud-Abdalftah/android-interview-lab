---
id: "SYS-10"
question: "How do you model states and transitions with an explicit state machine?"
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "B"
phase: 4
priority: "P1"
order: 339
editorial_status: "reviewed"
---

# SYS-10

## Original interview question

How do you model states and transitions with an explicit state machine?

## What the interviewer evaluates

Model business states and legal transitions explicitly, including persistence and idempotency.

## Explanation in Arabic

State machine بتحدد حالات واضحة وانتقالات مسموحة بدل Booleans متفرقة. مثل upload: Pending → Uploading → Complete أو Retryable/Failed، مع event IDs وشروط لكل انتقال. Payment: Unknown بعد timeout لا تتحول Failed من غير server proof. نخزن states المهمة transactionally، ونرفض transitions قديمة/out-of-order، ونكتب tests لكل edge وحالة process death.

## Practical walkthrough

في upload، `Sending(attempt=2)` ما ينفعش ترجع `Pending` بسبب callback قديمة بعد `Complete`. اكتب transition function تقبل current state وevent وترد state جديدة أو رفض؛ خزن version مع الحالة المهمة. Payment timeout حالة Unknown، مش Failed، لحد backend يثبت النتيجة. اختبر illegal transitions وreplay والسباق بين worker وnetwork callback قبل ربطها بالـUI.

## Why it matters and how it works

A reducer/transition function centralizes rules and can be pure for testability. Persistent state version or compare-and-set prevents concurrent workers overwriting newer results. External effects are issued through durable commands with stable IDs; completion events must be reconciled against authoritative source.

## Worked example

Kotlin conceptual pure transition function for a local upload; server business states need stronger authority.

```kotlin
sealed interface UploadState {
    data object Pending : UploadState
    data class Sending(val attempt: Int) : UploadState
    data class Complete(val receipt: String) : UploadState
}
sealed interface UploadEvent { data object Start : UploadEvent
    data class Acknowledged(val receipt: String) : UploadEvent }
fun reduce(state: UploadState, event: UploadEvent): UploadState = when {
    state is UploadState.Pending && event is UploadEvent.Start -> UploadState.Sending(1)
    state is UploadState.Sending && event is UploadEvent.Acknowledged -> UploadState.Complete(event.receipt)
    else -> state // production may reject/log illegal transitions explicitly
}
```

## Trade-offs and decision criteria

Explicit states add code but prevent impossible combinations like loading=true and settled=true. A permissive reducer that silently ignores illegal transitions can hide bugs; choose rejection/telemetry where appropriate. Distinguish UI transient state from durable business state.

## Failure modes

Two workers can race to mark Pending and Complete if updates lack version checks. A late network failure can overwrite a newer success. Treating timeout as final failure can trigger duplicate payment. Migration must preserve older state encodings.

## Production perspective

A payment repository stores operation state/version, applies server receipts transactionally and rejects stale updates. UI derives a screen from state; workers replay pending IDs after crash. Property tests enumerate legal/illegal transitions and race interleavings.

## Interview answer — short

“I define finite states and allowed events, centralize transitions and persist business state with version checks. That prevents contradictory flags and stale updates; an ambiguous timeout remains Unknown until authoritative reconciliation.”

## Interview answer — structured

“An explicit state machine makes failure semantics reviewable. I list states and legal transitions, then implement a reducer or repository transition function. For durable operations I store state and version transactionally, so a late worker cannot overwrite a newer outcome. UI renders from current state rather than juggling unrelated booleans. A payment timeout goes to Unknown/Pending, not Failed, until server status resolves it. Tests cover every legal edge, invalid event and process-death restart.”

## Interview answer — deep senior

“I use the state machine to capture invariants that would otherwise live in comments. Each event has an identity and precondition, transitions are validated against current version, and persistent updates are atomic. That matters when two workers or callbacks race: a delayed error must not overwrite an already confirmed success. External side effects are separate from pure state transitions, so I persist a command/operation ID before send and reconcile receipt afterward. For UI, a sealed state avoids impossible Boolean combinations; for payments, backend ledger remains authoritative and local Unknown is honest. I test every transition, duplicate event, out-of-order response, cancellation and crash window, and I log rejected transitions for diagnosis without leaking sensitive data. Migration must preserve older state encodings. The key test is an out-of-order event: a delayed timeout callback arrives after a success receipt. The transition function must reject moving Complete back to Retryable. For durable workflows I would store version and state in one transaction and use compare-and-set semantics so two workers cannot both advance an operation from the same prior version. I would model Unknown explicitly for remote ambiguity and require authoritative status before terminal payment state. Pure transition tests cover allowed and forbidden edges; integration tests cover persistence races.”

## How to answer in the interview

- **Why:** explicit states make invariants reviewable.
- **How:** define events, preconditions, versions, and atomic transition persistence.
- **Trade-off:** more types and transitions require maintenance.
- **Failure case:** delayed callback overwrites a terminal state.
- **Production solution:** pure transition tests plus transactional compare-and-set on durable state.

## Deep-dive talking points

Draw state graph with duplicate/out-of-order events and version guard.

## Follow-up questions

- [SYS-05](../sys-05/): Why Unknown payment state? **Answer:** client timeout does not prove server failure.
- [SYS-11](../sys-11/): How handle retries? **Answer:** state transition and stable operation ID govern repeat attempts.

## Self-check rubric

Can I enumerate states, reject illegal transitions and protect against stale concurrent updates?

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — UDF and SSOT.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable operation states.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
