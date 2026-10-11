---
id: "DAT-20"
question: "The server accepted a payment but the response was lost. How do you recover safely?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "C"
phase: 3
priority: "P1"
order: 277
editorial_status: "reviewed"
---

# DAT-20

## Original interview question

The server accepted a payment but the response was lost. How do you recover safely?

## What the interviewer evaluates

Recover a server-accepted payment whose response was lost, without duplicate charge.

## Explanation in Arabic

الـserver قبل payment لكن response ضاعت؛ عند العميل ده outcome مجهولة، مش فشل. قبل الإرسال كنا لازم نخزن operation ID وidempotency key ثابتين. بعد timeout أو restart نسأل backend عن الحالة بنفس ID، أو نستقبل reconciliation/webhook عبر backend؛ ما نضغطش charge جديد بمفتاح جديد. UI تعرض Pending لحد authoritative state، والworker repeat-safe.

## Why it matters and how it works

A client-side timeout cannot reverse a server transaction. Stable operation identity plus server deduplication allows safe logical retries within the backend contract, but not exactly-once network execution. Persist pending/acknowledged states transactionally and audit transitions. If status endpoint lags, keep pending with bounded retry and support escalation.

## Worked example

Conceptual suspend workflow; Gateway status is authoritative and Store persists operation state. Never treat unknown as a failed charge.

```kotlin
sealed interface ChargeStatus { data object Pending: ChargeStatus
    data object Settled: ChargeStatus; data object Rejected: ChargeStatus }
interface Gateway {
    suspend fun status(operationId: String): ChargeStatus
    suspend fun charge(operationId: String, key: String): ChargeStatus
}
suspend fun recover(id: String, gateway: Gateway): ChargeStatus = gateway.status(id)
```

## Trade-offs and decision criteria

Immediate retry improves responsiveness only when server idempotency is documented and status is reconciled. Waiting for status reduces duplicate risk but can leave Pending UX longer. A support/audit path is essential for unresolved financial operations.

## Failure modes

A naive retry with a new key can create a second charge. A local Success write may fail after server success, so the next launch must query server rather than assume absence of local record means no charge. An idempotency key retention window may expire.

## Production perspective

A checkout backend stores a ledger operation keyed by client operation ID and exposes status. Android persists Pending before request, uses WorkManager for reconciliation after process death, and shows Pending/Settled/Rejected. Tests crash after server commit but before client acknowledgement.

## Interview answer — short

“A lost response leaves the payment outcome unknown. I use the original durable operation ID and server status endpoint to reconcile, then retry only with the same key under a documented idempotency contract. The UI remains Pending meanwhile.”

## Interview answer — structured

“I would not create a new payment request. The app should have persisted a stable operation ID and idempotency key before sending. On timeout, it marks the operation Pending and queries authoritative server status. If the server reports success, the app updates local state; if it reports rejection, it shows that; if status is not yet final, a durable worker continues reconciliation. A retry is allowed only under the server’s deduplication contract with the same key. This handles process death and avoids falsely telling the user they were not charged. Immediate retry improves responsiveness only when server idempotency is documented and status is reconciled. Waiting for status reduces duplicate risk but can leave Pending UX longer. A support/audit path is essential for unresolved financial operations.”

## Interview answer — deep senior

“The hardest failure window is server commit followed by lost response and app crash before local acknowledgement. My workflow makes that recoverable: local Pending record is committed first, the backend assigns one logical charge to a stable key, and status can be queried by operation ID. A worker resumes Pending rows after restart. Idempotency deduplicates logical retries but does not imply only one HTTP request was executed; key retention and payload equality rules must be explicit. I do not let the UI initiate a fresh key while status is uncertain. I monitor unresolved Pending age, provide support correlation IDs and test every crash point, including delayed status propagation and duplicate worker runs. A client-side timeout cannot reverse a server transaction. Stable operation identity plus server deduplication allows safe logical retries within the backend contract, but not exactly-once network execution. Persist pending/acknowledged states transactionally and audit transitions. If status endpoint lags, keep pending with bounded retry and support escalation. A naive retry with a new key can create a second charge. A local Success write may fail after server success, so the next launch must query server rather than assume absence of local record means no charge. An idempotency key retention window may expire. A checkout backend stores a ledger operation keyed by client operation ID and exposes status.”

## Deep-dive talking points

Trace pre-send persistence, server commit, lost response and process restart.

## Follow-up questions

- [DAT-14](../dat-14/): When retry a write? **Answer:** under a server idempotency contract after reconciling uncertainty.
- [BG-18](../bg-18/): Who owns reversal after app exit? **Answer:** durable operation plus restartable worker and server deduplication.

## Self-check rubric

Can I hold Pending, query authority, reuse key and test the commit/ack crash window?

## References and reviewed-on date

- [Kotlin withTimeout API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html) — local deadline limitations.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable write synchronization.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
