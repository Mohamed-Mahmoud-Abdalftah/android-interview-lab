---
id: "SYS-05"
question: "Design a robust payment transaction lifecycle."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 334
editorial_status: "reviewed"
---

# SYS-05

## Original interview question

Design a robust payment transaction lifecycle.

## What the interviewer evaluates

Design payment lifecycle with idempotent backend, pending state and reconciliation.

## Explanation in Arabic

Payment state machine: Created locally → PendingSubmit → Authorized/Declined → Captured/Settled أو Reversed حسب backend contract. نعمل operation ID ثابت قبل network، ونرسل idempotency key مع payload مطابق؛ timeout يعني Unknown/Pending وليس Failed. backend ledger يفرض transitions وdeduplication، وAndroid worker تستعلم عن status وتتصالح بعد process death. UI ما تعرضش نجاح أو تسمح charge جديد من غير authority.

## Practical walkthrough

تخيّل POS بعت authorize والـUI عملت timeout. نفس `operationId` و`idempotencyKey` يفضلوا محفوظين، والـUI تعرض Pending لحد status من ledger أو provider. ممنوع تبدأ authorize جديدة بمفتاح جديد لمجرد إن HTTP فشل؛ ممكن تخصم مرتين. فرّق بين Authorized وCaptured وSettled وReversed لأن كل انتقال ليه صاحب وسبب. سجل transition timestamp وcorrelation ID للتسوية والدعم.

## Why it matters and how it works

Payment authorization and capture may be separate server operations with their own IDs and rules. Persist local intent and transition records; never trust device clock or balance as authority. Use bounded retry only with same key and status query. Reversal is a new linked operation, not deleting a row.

## Worked example

Conceptual Kotlin state representation; backend owns validation and ledger.

```kotlin
sealed interface PaymentState {
    data class Pending(val operationId: String) : PaymentState
    data class Authorized(val authId: String) : PaymentState
    data class Settled(val receiptId: String) : PaymentState
    data class Rejected(val reason: String) : PaymentState
    data class Unknown(val operationId: String) : PaymentState
}
```

## Trade-offs and decision criteria

Fast optimistic UI reduces perceived latency but is dangerous if it asserts success before server confirmation. Pending UX may be slower but honest. Server idempotency and status APIs cost engineering work; they are essential for safe retries.

## Failure modes

A timeout after server commit can be followed by a new key and double charge. A captured payment cannot be “rolled back” by deleting local state; it needs a server reversal/refund transition. Worker duplicate run must not duplicate ledger entries.

## Production perspective

A checkout persists operation ID/amount, submits through backend, shows Pending on timeout and schedules reconciliation. Server exposes ledger status and receipts; support monitors unresolved operations. Tests crash before send, after commit, before local acknowledgement and during reversal.

## Interview answer — short

“I model payment as explicit states, persist a stable operation ID before send and let backend ledger enforce idempotency and transitions. Timeout is unknown, so UI stays Pending and a durable worker reconciles status. Reversal is a separate linked operation.”

## Interview answer — structured

“A robust payment flow begins with a local pending record and stable idempotency key. The server validates the amount and owns authorization/capture state. Android sends the request and records only an authoritative result; if the response is lost, it shows Pending and queries status rather than creating a new charge. WorkManager resumes reconciliation after process death. A reversal or refund is a new linked transaction with its own server contract, not a local deletion. I test retries, duplicate workers and crash windows.”

## Interview answer — deep senior

“I separate logical payment identity from HTTP attempts. Before transmission, the client persists an operation ID and immutable amount/order context. The backend binds that ID to one ledger operation, rejects payload mismatch and exposes status. Authorization, capture, settlement and reversal may be distinct transitions, and only backend authority can confirm them. A coroutine or HTTP timeout merely stops client waiting; it cannot prove the charge failed or undo it. The app keeps Unknown/Pending, schedules repeat-safe reconciliation and reuses the same key only under documented retention rules. I instrument state transition latency and unresolved Pending age, suppress sensitive logs, and test duplicate taps, process death at every boundary, delayed webhooks and reversal races. I would draw the payment timeline with separate authorization, capture, settlement and reversal transitions and name the system allowed to perform each. A network timeout moves the client to Pending or Unknown, not Declined. The backend keeps a ledger and provider reference, deduplicates stable operation IDs under a documented retention policy, and exposes status for reconciliation. I would test response loss after provider acceptance, worker repetition and process death. Metrics should age unresolved operations and alert before support sees duplicate-charge reports.”

## How to answer in the interview

- **Why:** client observations and financial state can diverge.
- **How:** persist operation identity, use backend ledger transitions, and reconcile ambiguous results.
- **Trade-off:** Pending UX is more complex than a simple success/failure toast.
- **Failure case:** retry with a new key after lost response.
- **Production solution:** server idempotency, authoritative status lookup, and auditable transitions.

## Deep-dive talking points

Draw payment states and justify how every crash window converges to authoritative status.

## Follow-up questions

- [DAT-20](../dat-20/): How recover lost response? **Answer:** query server status by original operation ID.
- [BG-18](../bg-18/): How handle reversal after exit? **Answer:** durable linked operation and server deduplication.

## Self-check rubric

Can I define states, preserve unknown outcomes and prevent duplicate charges?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable pending operations.
- [Kotlin withTimeout API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html) — timeout limits.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
