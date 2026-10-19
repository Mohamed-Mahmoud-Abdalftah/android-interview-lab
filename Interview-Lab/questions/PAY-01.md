---
id: "PAY-01"
question: "What is a payment state machine (initiated, processing, approved, declined, unknown, reversed)?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "A"
phase: 5
priority: "P2"
order: 471
editorial_status: "reviewed"
---

# PAY-01

## Original interview question

What is a payment state machine (initiated, processing, approved, declined, unknown, reversed)?

## What the interviewer evaluates

- Explicit legal transitions and unknown state.
- Separation of terminal display, backend/provider truth and reversal.

## Concept and technical explanation

A payment state machine records what the client and backend actually know about one attempt. `Initiated` means an attempt ID and intent have been persisted. `Processing` means the request may be in flight. `Approved` and `Declined` require authoritative outcomes under the provider contract. `Unknown` means the response is missing or ambiguous; it must not be treated as a decline. `Reversed` should be used only after the provider confirms a reversal, if that operation applies to the integration.

Persist transitions atomically within the local database, but never claim that a local transaction is atomic with a remote payment. Keep a stable attempt ID and any provider correlation reference so the backend can resolve an unknown outcome after a crash. An idempotency key helps with retries only if the provider or backend honors it under documented rules. Recovery may involve a status inquiry, reconciliation, or a protocol-specific reversal; no single command works for every provider. Test every failure window, including a lost approval response and an unconfirmed reversal.

## Practical walkthrough (English)

Modeling a deterministic financial payment state machine in Kotlin:
```kotlin
sealed interface PaymentState {
    val transactionId: String
    val amountCents: Long

    // 1. Durably recorded in Room prior to network transmission
    data class Initiated(
        override val transactionId: String,
        override val amountCents: Long,
        val createdAtEpoch: Long
    ) : PaymentState

    // 2. In-flight over HTTPS/TCP to gateway
    data class Processing(
        override val transactionId: String,
        override val amountCents: Long,
        val idempotencyKey: String
    ) : PaymentState

    // 3. Provider-confirmed authorization under this integration's contract
    data class Approved(
        override val transactionId: String,
        override val amountCents: Long,
        val authCode: String,
        val rrn: String // Retrieval Reference Number
    ) : PaymentState

    // 4. Provider-confirmed decline under this integration's contract
    data class Declined(
        override val transactionId: String,
        override val amountCents: Long,
        val errorCode: String,
        val reason: String
    ) : PaymentState

    // 5. In-Doubt state: Network timeout or crash during flight
    data class Unknown(
        override val transactionId: String,
        override val amountCents: Long,
        val reasonCode: String // safe to persist; do not persist Throwable
    ) : PaymentState

    // 6. Provider-confirmed reversal; release timing may differ
    data class Reversed(
        override val transactionId: String,
        override val amountCents: Long,
        val reversalReference: String
    ) : PaymentState
}
```

## Explanation in Arabic

آلة حالات الدفع بتسجل إحنا نعرف إيه فعلاً عن محاولة واحدة. `Initiated` معناها حفظ نية الدفع ومعرف ثابت، و`Processing` معناها إن الطلب قد يكون خرج، و`Approved` أو `Declined` يحتاجان رداً موثوقاً حسب عقد مزود الدفع. `Unknown` معناها إن الرد ناقص أو ملتبس، ومش مسموح نعتبرها رفضاً. `Reversed` تُستخدم بعد تأكيد العكس من المزود، لو العملية دي موجودة في البروتوكول.

أحفظ كل انتقال محلي داخل Transaction مناسبة، لكن قاعدة البيانات المحلية ما تقدرش تعمل Transaction ذرية مع خصم بعيد على الشبكة. معرف المحاولة ومرجع المزود يسمحان للـ Backend بحسم الحالة بعد سقوط التطبيق. Idempotency Key مفيد فقط ضمن شروط المزود ومدة احتفاظه. الاسترداد ممكن يحتاج Status Inquiry أو Reconciliation أو Reversal محدداً؛ مفيش أمر واحد صالح لكل تكامل. أختبر ضياع رد الموافقة وتعطل الجهاز والعكس غير المؤكد.

## Practical walkthrough

تمثيل توضيحي لحالات محاولة دفع؛ قواعد الانتقال تأتي من عقد مزود الدفع:
```kotlin
sealed interface PaymentState {
    val transactionId: String
    val amountInCents: Long

    // 1. تم إنشاء المعاملة وحفظها محلياً في Room:
    data class Initiated(override val transactionId: String, override val amountInCents: Long) : PaymentState

    // 2. تم إرسال الطلب للبنك وننتظر الرد:
    data class Processing(override val transactionId: String, override val amountInCents: Long, val idempotencyKey: String) : PaymentState

    // 3. تأكيد التفويض وفق عقد المزود:
    data class Approved(override val transactionId: String, override val amountInCents: Long, val authCode: String) : PaymentState

    // 4. رفض صريح من البنك:
    data class Declined(override val transactionId: String, override val amountInCents: Long, val reason: String) : PaymentState

    // 5. حالة معلقة تحتاج استعلاماً أو مطابقة؛ نخزن رمزاً آمناً لا Throwable:
    data class Unknown(override val transactionId: String, override val amountInCents: Long, val reasonCode: String) : PaymentState

    // 6. المزود أكد العكس؛ توقيت تحرير الرصيد قد يختلف:
    data class Reversed(override val transactionId: String, override val amountInCents: Long, val reversalRef: String) : PaymentState
}
```

## Why it matters and how it works

State transitions are guarded by server/provider evidence and transaction identity. A client callback can report observations, not final financial truth. Unknown is a first-class state that triggers status lookup, reconciliation or reversal under the payment contract. A terminal state should not be rewritten by a stale callback.

## Worked example

After sending authorization, the terminal loses network. Persist `unknown(operationId)` and show “checking status”; query backend/provider when connected. If authoritative status says approved, show approved; if a reversal is required, enqueue a durable reversal intent. Never create a new purchase ID for a retry.

### Kotlin/Android sketch

```kotlin
// Domain model; provider statuses must be mapped under its contract.
sealed interface PaymentState {
    data object Initiated : PaymentState
    data object Processing : PaymentState
    data object Unknown : PaymentState
    data class Approved(val providerRef: String) : PaymentState
    data class Declined(val reasonCode: String) : PaymentState
    data class Reversed(val reversalRef: String) : PaymentState
}
fun onTimeout(current: PaymentState): PaymentState =
    if (current == PaymentState.Processing) PaymentState.Unknown else current
```

## Trade-offs and decision criteria

A strict state machine adds implementation work but makes crash recovery and audit possible. Provider-specific states may be richer; map them carefully without collapsing pending/unknown into failure.

## Failure modes

UI navigation exits and discards `processing` state, then a late approval arrives. Persist before network send and let a repository/backend own transitions. Test duplicate callbacks, timeout then success and process death.

## Production perspective

Keep a transition table with allowed evidence, actor and durable write for each state. Log opaque IDs and state changes, reconcile unresolved records, and test against the provider’s documented authorization/reversal semantics.

## Interview answer — short

A payment state machine gives each attempt a clear status: initiated, processing, approved, declined, unknown, or reversed. The key distinction is that a timeout means unknown, not declined; the provider may have processed the payment even though the app missed the reply. I persist an attempt identifier and use the provider's status or reconciliation flow before offering a new charge. The exact transitions depend on the payment contract.

## Interview answer — structured

I use a payment state machine so the UI cannot turn every network error into “payment failed.” The states describe what we actually know: initiated and processing while an attempt is underway, approved or declined when the processor gives a definitive result, unknown when the response is missing, and reversed when a reversal is confirmed.

The important case is a timeout after we sent the request. The customer might have been charged, so I would not show a definite decline or create a fresh payment attempt just because the phone lost connectivity. I would persist the attempt's identifier before sending it, then ask the backend or provider for its status. If the provider supports idempotent retries, I reuse the same key within that contract. Reversal is a separate operation with its own acknowledgement, not something the phone can assume happened.

For a POS app I would make the on-screen message honest: “We are checking this payment” is safer than “Try again” while the outcome is unknown. The server and payment processor are authoritative for the final result. Local state helps recovery after process death, but it does not by itself guarantee exactly-once charging or perfect reconciliation.

## Interview answer — deep senior

I would first ask which payment provider and protocol we are integrating with, because the state names are our application model, while valid transitions and recovery commands come from the provider contract. A local record should include a stable attempt ID, provider correlation data, the latest known state, and enough safe metadata to investigate without storing sensitive card data. I would persist the intent before the irreversible call, but I would not claim the local database transaction is atomic with the remote payment. There is always a failure window between them.

After a timeout, I treat the result as unknown. I can query a provider status endpoint, reconcile with backend events, or use a prescribed reversal flow where the protocol calls for one. I must not automatically fire an ISO 8583 reversal for every missing HTTP response; some integrations do not expose that operation, and a reversal request can itself time out. Until a confirmed response arrives, the app should preserve the uncertainty and prevent an accidental new charge. An idempotency key helps only if the server honors it for the relevant operation and retention window.

For recovery, I would test power loss before send, after send but before response, after approval but before local persistence, and during reversal. The backend should resolve attempts using stable IDs and durable records, with an operator path for cases that remain ambiguous. The client can schedule retries under OS limits, but it cannot promise immediate delivery or guarantee that a payment was reversed. I would measure unresolved attempts and time to reconciliation, while keeping PAN, PIN, and secrets out of logs.

## How to answer in the interview

- **Why:** timeout leaves financial outcome unknown.
- **How:** tie every legal transition to evidence and a durable operation ID.
- **Trade-off:** the model must map richer provider states without inventing equivalence.
- **Failure case:** a late callback overwrites a reconciled result.
- **Production solution:** commit intent before I/O, guard transitions, and reconcile nonfinal rows.

## Deep-dive talking points

Prompt for transition table, unknown timeout, durable intent, late callback ordering and provider evidence.

## Follow-up questions

- **Interviewer:** "The app timed out. Can the cashier simply retry?"
  **Answer:** "Not as a new charge. First I would look up the existing attempt. If the provider supports an idempotent retry, I would reuse that attempt's key under its documented rules; otherwise I would wait for status or reconciliation."

- **Interviewer:** "Would you send a reversal for every unknown result?"
  **Answer:** "Only if the provider's protocol requires it for that state. I would track the reversal as its own pending operation and wait for confirmation, because a reversal request can fail or time out too."

- **Interviewer:** "What if power dies after approval but before the app saves it?"
  **Answer:** "The local record may still say processing. On restart I would resolve the stable attempt ID against the authoritative backend or provider rather than infer the result from local state."

## Self-check rubric

Can I distinguish timeout from decline, identify authoritative transitions and describe recovery?

## References and reviewed-on date

- [Stripe PaymentIntent lifecycle](https://docs.stripe.com/payments/paymentintents/lifecycle) — one provider’s state model.
- [Android offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable local data concepts.

Technically reviewed against the cited primary documentation on 2026-10-19; agent editorial review, not human verification.
