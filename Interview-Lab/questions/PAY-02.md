---
id: "PAY-02"
question: "What is idempotency, and why does it matter for financial transactions?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "A"
phase: 5
priority: "P2"
order: 472
editorial_status: "reviewed"
---

# PAY-02

## Original interview question

What is idempotency, and why does it matter for financial transactions?

## What the interviewer evaluates

- Definition of one business effect across retries, distinct from exactly-once network execution.
- Understanding of stable operation identity, server-side key handling, and unknown outcomes after timeouts.
- Ability to connect durable client state, reconciliation, and payment-provider constraints.

## Explanation in Arabic

Idempotency معناها إن تكرار نفس العملية بالـidentity نفسها ما يعملش أثر مالي جديد كل مرة. الـnetwork ممكن تبعت request والـserver تنفذها وبعدين الرد يضيع؛ العميل يشوف timeout لكنه ما يعرفش هل الدفع نجح. لو رجّع request بمفتاح جديد، ممكن يخصم مرتين. عشان كده العميل يحتفظ بـoperation ID ثابت ويعيده، والـserver يطبّق سياسة idempotency ومعاها status lookup وreconciliation. ده يدي at-least-once delivery مع business effect محمي، مش وعد إن الـHTTP request اتنفذت مرة واحدة بالضبط.

### Practical walkthrough in Egyptian Arabic

مثال عملي: العميل ضغط Pay مرة، الـserver نفذت charge لكن response ضاعت. قبل retry، العميل يقرأ intent المحفوظة ويرجع بنفس key ونفس amount/currency، مش UUID جديدة. لو provider dedupe window انتهت، نفس key وحدها مش ضمان؛ status lookup وledger reconciliation لازم يسبقوا إعادة الإرسال. في Stripe API v1 تحديدًا أول نتيجة محفوظة ممكن تكون `500`، فمتفسرش replay كنجاح.

## Why it matters and how it works

An idempotency key identifies one intended operation and its stable parameters. The server must atomically associate that identity with processing/result according to a documented retention and concurrency policy. A retry with the same key can return the prior result or current status; a retry with changed parameters should be rejected. A client timeout means **unknown**, not automatically failed. Provider implementations differ: for example, Stripe documents retention, parameter comparison, and replay behavior, so an app must follow its actual provider contract rather than assume a universal guarantee.

## Worked example

This Kotlin domain sketch is independent of Android framework APIs. The repository contract is deliberately explicit: `submit` uses the same `operationId` for retries, and `lookup` checks authority after an unknown outcome. The server must implement the idempotency rule; a client-side UUID alone is insufficient.

```kotlin
data class PaymentIntent(val operationId: String, val amountMinor: Long)
sealed interface SubmitResult {
    data object Unknown : SubmitResult
    data class Final(val approved: Boolean) : SubmitResult
}

interface PaymentGateway {
    suspend fun submit(intent: PaymentIntent): SubmitResult
    suspend fun lookup(operationId: String): SubmitResult
}

suspend fun resolvePayment(intent: PaymentIntent, gateway: PaymentGateway): SubmitResult {
    val first = gateway.submit(intent)
    return if (first is SubmitResult.Unknown) gateway.lookup(intent.operationId) else first
}
```

A real client must persist the intent before the first send and decide what to do when lookup is also unknown; this snippet illustrates the identity and status-check boundary, not a complete payment system.

## Trade-offs and decision criteria

Stable keys and server records cost storage and require retention policy, concurrency control, and safe parameter comparison. Reusing one key for a genuinely new purchase is wrong; generating a new key for a retry of the same purchase is also wrong. Local deduplication helps UI behavior but cannot establish financial truth after process death. Reconciliation may be needed beyond the provider's idempotency retention window.

## Failure modes

**Wrong:** UI times out, creates a new UUID, and submits a second charge. The first charge may already have succeeded. **Right:** preserve the original operation identity, show an unknown/pending state, query authoritative status, and retry only under the documented idempotency contract. Also never infer payment approval solely from a local callback or a successful HTTP transport status.

## Production perspective

A POS terminal loses connectivity after an authorization request. It durably retains the operation ID and safe transaction metadata, never raw PAN/PIN. On restart it queries the backend/provider, reconciles unknown outcomes, and uses a durable reversal workflow when required by the payment protocol. Server logs and client telemetry use correlation IDs without sensitive card data.

## Interview answer — short

“The key identifies one business intent across retries, but the backend must enforce it. After a timeout I reuse the key and unchanged parameters, then look up the outcome rather than assuming a failed payment.”

## Interview answer — structured

“A financial operation must tolerate at-least-once delivery without creating duplicate business effects. Suppose a charge is approved but the response is lost; the client sees a timeout, not proof of failure. Before sending, I persist a stable operation ID and immutable parameters. The server or provider atomically recognizes retries with that ID, rejects mismatched payloads, and exposes a status lookup. The client displays pending or unknown until authority resolves it. This design needs an idempotency retention window, concurrency rules, and reconciliation after crashes. It does not guarantee exactly-once HTTP execution, and provider behavior must be checked rather than assumed. A Stripe API v1 replay can repeat the original 500 response; it is still an unknown outcome to investigate.”

## Interview answer — deep senior

“Idempotency is a business-effect contract across repeated delivery, not a claim that only one packet or handler invocation occurs. A client can lose the response after a provider commits a charge. I persist the intended operation ID and immutable amount/order details before send; the backend atomically binds that ID to one logical effect and exposes a status query. A retry uses the same key and identical parameters only within the provider's documented retention rules; after key expiry or ambiguous failure, reconciliation is safer than inventing a new attempt. Concurrent duplicate requests, partial failures, reversal, and webhook ordering are part of the server design. The UI represents pending or unknown until authoritative status arrives. I would document the provider’s deduplication retention and parameter rules, then test a timeout after remote execution. For a concrete example, the server receives an authorization and commits it, but the HTTP response never reaches the terminal. A second request with a new key is a new business intent from the provider's perspective; the client must reuse the original key and unchanged request fingerprint. I would not describe this as exactly-once network delivery. Multiple requests can happen, while the business effect is guarded by the server and provider contract. Stripe API v1, for instance, documents result replay, parameter comparison, and a retention window; after that window, lookup or reconciliation is safer than blindly assuming the old key still deduplicates. I test simultaneous retries and lost responses.”

## How to answer in the interview

- **Why:** retrying transport is common; duplicate financial effects are unacceptable.
- **How:** persist one operation identity and immutable request fingerprint.
- **Trade-off:** each provider has retention and concurrency rules.
- **Failure case:** new key or changed amount on retry creates a second intent or rejection.
- **Production solution:** server-side deduplication, status lookup, and retention-aware reconciliation.

## Deep-dive talking points

Discuss duplicate concurrent requests, key-retention expiry, atomic server commits, response replay, reversal queues, reconciliation reports, and how to test a lost response after server success.

## Follow-up questions

- [PAY-08](../pay-08/): What should the UI do after timeout? **Answer:** show an unknown or pending outcome, keep attempt identity, and query authoritative status rather than start a new charge.
- [PAY-12](../pay-12/): How do you recover after terminal power loss? **Answer:** reload a durably recorded attempt and reconcile it against provider/backend status before another financial action.
- [PAY-15](../pay-15/): How do reversals survive offline periods? **Answer:** persist reversal intent and identity, retry under a deduplication contract, and reconcile confirmed outcome with the backend.

## Self-check rubric

Score 0–5, one point each: define idempotent business effect; explain unknown timeout; preserve stable identity/parameters; name the server-side contract; describe crash recovery or reconciliation. Deduct confidence if you claim exactly-once network delivery.

## References and reviewed-on date

- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) — one provider's concrete key, replay, and retention contract.
- [Android data-layer guidance](https://developer.android.com/topic/architecture/data-layer) — repository ownership and data coordination in Android apps.

Technically reviewed against the linked primary documentation on 2026-10-11. The provider-specific behavior is an example, not a universal payment-network guarantee.
