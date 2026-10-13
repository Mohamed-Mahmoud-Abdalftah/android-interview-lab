---
id: "COR-27"
question: "A payment timeout occurs after a request reaches the server. How do you avoid duplicate charges on retry?"
topic: "Kotlin Coroutines & Concurrency"
code: "COR"
group: "C"
phase: 1
priority: "P1"
order: 108
editorial_status: "reviewed"
---

# COR-27

## Original interview question

A payment timeout occurs after a request reaches the server. How do you avoid duplicate charges on retry?

## What the interviewer evaluates

Handle payment timeout as an ambiguous server outcome using durable keys and reconciliation.

## Explanation in Arabic

لو payment request وصلت السيرفر والعميل عمل timeout، النتيجة **unknown** مش failed. إعادة الإرسال بـidempotency key جديد ممكن تعمل charge مرتين. نسجل operation ID ثابت قبل الإرسال، نستخدم نفس key عند retry حسب عقد الـbackend، ونسأل السيرفر عن حالة العملية أو نعمل reconciliation مع webhook/ledger. UI تفضل Pending لحد الحالة الموثوقة.

## Practical walkthrough

لو request الدفع وصلت السيرفر ثم client عمل timeout، رسالة `failed` للمستخدم ممكن تكون كدب؛ العملية قد تكون اتسجلت. خزّن `operationId` و`idempotencyKey` وpayload hash قبل الإرسال. عند retry استخدم نفس key حسب عقد backend، واسأل status أو اعمل reconciliation. لو key انتهت صلاحيتها، لا تعمل charge جديد بشكل أعمى؛ اعتمد على ledger أو دعم backend.

## Why it matters and how it works

Coroutine timeout cancels client waiting, not necessarily the HTTP transport or server transaction. A server-side idempotency contract can deduplicate retries with the same stable key, but it does not prove exactly-once network execution. Persist pending state and key transactionally before request; recover after process death and verify authoritative status before any repeat.

## Worked example

Conceptual Android repository skeleton; `gateway` must enforce one charge per stable key and document its retention and payload-matching contract. The store persists before network send. A pending operation is reconciled later by status lookup.

```kotlin
import java.net.SocketTimeoutException

data class PaymentOp(val id: String, val key: String)
sealed interface PaymentOutcome {
    data class Confirmed(val receipt: String) : PaymentOutcome
    data object Pending : PaymentOutcome
}
interface PaymentStore {
    suspend fun savePending(op: PaymentOp)
    suspend fun markConfirmed(id: String, receipt: String)
}
interface PaymentGateway {
    suspend fun charge(op: PaymentOp): String
    suspend fun status(id: String): String
}
suspend fun submit(
    op: PaymentOp, store: PaymentStore, gateway: PaymentGateway,
): PaymentOutcome {
    store.savePending(op)
    val receipt = try {
        gateway.charge(op) // retry only with the same key and payload
    } catch (e: SocketTimeoutException) {
        return PaymentOutcome.Pending // do not infer server rejection
    }
    store.markConfirmed(op.id, receipt)
    return PaymentOutcome.Confirmed(receipt)
}
```

## Trade-offs and decision criteria

A stable key helps only if the server enforces deduplication with defined retention and payload matching. Status lookup/reconciliation increases complexity but prevents false failure claims and duplicate financial effects. Do not convert every timeout to a new charge attempt.

## Failure modes

Client cancellation after server acceptance can leave a pending charge. Process death can occur after send but before local success write. A new key on retry may charge again; reusing a key outside its server retention window may also be unsafe. Log operation IDs, not payment credentials.

## Production perspective

A checkout creates a unique operation, stores it as Pending, submits with a stable key, and on timeout checks server status. WorkManager resumes reconciliation from durable state. The backend ledger decides success/failure; customer UI shows Pending while uncertain, and support tooling can inspect the correlation ID.

## Interview answer — short

“A timeout means the client stopped waiting; the server may have charged. I persist one operation ID and idempotency key, query authoritative status, and retry only under the backend’s deduplication contract with the same key. The UI shows Pending until reconciled.”

## Interview answer — structured

“I never treat a payment timeout as a definite failure. Before sending, I persist an operation record and stable idempotency key. The server must enforce a documented deduplication rule for retries, and I use a status endpoint or reconciliation feed to resolve uncertainty. If the app dies after the request, a durable worker resumes from Pending rather than creating a new operation. The UI does not offer an unsafe fresh charge button; it shows Pending and later the authoritative result.”

## Interview answer — deep senior

“There are two independent facts: the coroutine or HTTP client timed out, and the payment server may already have committed. Cancellation cannot roll back the second fact. My design records a stable operation ID, amount and key before transmission, and the server maps that key to one logical payment under an explicit retention and payload contract. After ambiguous timeout or process death, the client queries transaction status or awaits a backend reconciliation signal. A retry, if allowed, reuses the same key and is safe only within the server’s contract; I never claim exactly-once network delivery. I instrument state transitions, suppress sensitive logging, and test crash points before send, after server commit and before local acknowledgement. A human-readable Pending state prevents the user from triggering a duplicate. The tricky case is a timeout after the provider accepted the request. The local HTTP exception describes client observation, not the financial result. I would persist one operation identity and payload before the send, reuse its idempotency key only within the provider's documented contract, and query authoritative status after uncertainty. A worker can reconcile Pending after process death. Support tooling needs an audit trail, while the UI must avoid offering a fresh charge before the old operation is resolved.”

## How to answer in the interview

- **Why:** client timeout cannot establish payment outcome.
- **How:** persist a stable operation identity before sending and reconcile status after ambiguity.
- **Trade-off:** idempotency contracts and pending UX add complexity.
- **Failure case:** generating a new key on retry produces a duplicate charge.
- **Production solution:** server-enforced deduplication, an authoritative ledger, and auditable Pending state.

## Deep-dive talking points

Walk through crash points and distinguish idempotent logical operation from exactly-once network execution.

## Follow-up questions

- [COR-17](../cor-17/): Does coroutine timeout mean server failure? **Answer:** no; commit status can be unknown.
- [COR-18](../cor-18/): Which key on retry? **Answer:** the same durable operation key under the backend contract.

## Self-check rubric

Can I name every crash window, use a stable key, reconcile status and avoid declaring an uncertain charge failed?

## References and reviewed-on date

- [Kotlin withTimeout API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html) — local deadline semantics.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable queued writes/reconciliation patterns.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-13; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
