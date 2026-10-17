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

A payment state machine is a deterministic finite state automaton governing the lifecycle of financial transactions across mutually exclusive, strictly monotonic states:
- The Binary Fallacy in Financial Systems:
  - In ordinary applications, network requests are often modeled as a boolean `Result.Success` or `Result.Failure`.
  - In point-of-sale (POS) and fintech systems, this simplification causes catastrophic double-charging. A network timeout does not mean the transaction failed; the issuing bank may have deducted funds while the mobile client failed to receive the TCP packet.
- The 6 Canonical Payment States:
  1. `Initiated`: Transaction intent, cryptographic correlation ID, and amount are durably committed to SQLite/Room before opening any network socket.
  2. `Processing`: The transaction payload has been dispatched to the payment gateway or bank switch; client awaits cryptographic authorization.
  3. `Approved`: The issuer returns a signed authorization code confirming funds hold; receipt can be printed.
  4. `Declined`: Explicit rejection code from the card issuer (e.g., insufficient balance, expired card, incorrect PIN); a definitive terminal state requiring no retry.
  5. `Unknown` (In-Doubt): The socket dropped, timed out, or process terminated while waiting for response. The ledger state is undefined; funds may or may not be debited.
  6. `Reversed`: An automated reversal (such as ISO 8583 message 0400/0420) was dispatched and acknowledged, releasing any pre-authorized hold on the cardholder's funds.
- Monotonicity and Durability Invariants:
  - State transitions must be strictly unidirectional and written using write-ahead logging (WAL) transactions. Once a transaction reaches `Approved` or `Declined`, it can never transition back to `Processing`.

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

    // 3. Terminal success: Authorization code granted
    data class Approved(
        override val transactionId: String,
        override val amountCents: Long,
        val authCode: String,
        val rrn: String // Retrieval Reference Number
    ) : PaymentState

    // 4. Terminal failure: Explicit bank refusal
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
        val failureReason: Throwable
    ) : PaymentState

    // 6. Terminal release: Pre-authorization hold cancelled
    data class Reversed(
        override val transactionId: String,
        override val amountCents: Long,
        val reversalReference: String
    ) : PaymentState
}
```

## Explanation in Arabic

ما هي آلة حالة الدفع (Payment State Machine) وما هي الحالات الأساسية (Initiated, Processing, Approved, Declined, Unknown, Reversed) ولماذا تعتبر حاسمة في التطبيقات المالية؟

1. خطورة التعامل مع المدفوعات كـ Boolean (Success/Failure):
   - في التطبيقات العادية، قد تكفيك نتيجة `true` أو `false`.
   - في الأنظمة المالية ونقاط البيع (POS/Fintech)، **هذا التبسيط يؤدي لكوارث مالية (Double-charging أو خسارة أموال التاجر)**!
   - الشبكة قد تنقطع بعد خصم الأموال من حساب العميل وقبل وصول الرد للهاتف؛ فإذا اعتبرت العملية "فاشلة"، سيقوم العميل بالدفع مرة أخرى ويُخصم منه مرتين!

2. الحالات الست الصارمة لآلة حالة الدفع (The 6 Payment States):
   - **1. Initiated (تم البدء)**: تم إنشاء الطلب محلياً وتوليد معرف ارتباط فريد (Correlation ID) وحفظه في قاعدة البيانات المحلية (Room) قبل إرسال أي بايت عبر الشبكة.
   - **2. Processing (قيد المعالجة)**: تم إرسال الطلب إلى معالج الدفع (Payment Gateway / Bank Switch) وننتظر الرد.
   - **3. Approved (مقبول ومؤكد)**: وصل رد رسمي وبتوقيع رقمي من البنك يؤكد حجز الأموال بنجاح.
   - **4. Declined (مرفوض)**: رد صريح من البنك بالرفض (رصيد غير كافٍ، بطاقة منتهية، كلمة سر خاطئة). حالة نهائية لا تتطلب إعادة محاولة.
   - **5. Unknown / In-Doubt (حالة معلقة وغير محددة)**: **أهم وأخطر حالة**! انقطاع اتصال (Timeout)، سقوط الخادم، أو إعادة تشغيل الهاتف أثناء انتظار الرد. لا يجوز اعتبارها نجاحاً ولا فشلاً، بل تتطلب استعلاماً لاحقاً (Reconciliation) أو عملية عكس (Reversal).
   - **6. Reversed (معكوس / ملغى)**: تم إرسال طلب إلغاء فوري للبنك لحذف الحجز واستعادة رصيد العميل بسبب عطل محلي.

## Practical walkthrough

تمثيل آلة حالة الدفع الصارمة باستخدام Kotlin Sealed Class في كود معماري آمن:
```kotlin
sealed interface PaymentState {
    val transactionId: String
    val amountInCents: Long

    // 1. تم إنشاء المعاملة وحفظها محلياً في Room:
    data class Initiated(override val transactionId: String, override val amountInCents: Long) : PaymentState

    // 2. تم إرسال الطلب للبنك وننتظر الرد:
    data class Processing(override val transactionId: String, override val amountInCents: Long, val idempotencyKey: String) : PaymentState

    // 3. تأكيد نهائي بالخصم:
    data class Approved(override val transactionId: String, override val amountInCents: Long, val authCode: String) : PaymentState

    // 4. رفض صريح من البنك:
    data class Declined(override val transactionId: String, override val amountInCents: Long, val reason: String) : PaymentState

    // 5. حالة معلقة (انقطاع شبكة أثناء المعالجة - تتطلب تحقيق ومطابقة):
    data class Unknown(override val transactionId: String, override val amountInCents: Long, val error: Throwable) : PaymentState

    // 6. تم إلغاء المعاملة واسترجاع الرصيد بنجاح:
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

A payment state machine is a deterministic automaton that manages financial lifecycles across six explicit states: Initiated, Processing, Approved, Declined, Unknown, and Reversed. It replaces dangerous boolean success-failure models with durable, crash-resilient transitions, ensuring that network timeouts enter an in-doubt state requiring automated reconciliation or ISO 8583 reversal rather than risking double-charging.

## Interview answer — structured

A deterministic payment state machine is the core architectural safeguard in mobile point-of-sale and fintech engineering.
Standard mobile applications frequently treat network operations as a binary success or failure. In financial systems, this binary assumption leads to double-charging because a socket timeout indicates an ambiguous state where the bank might have debited funds while the client lost connectivity.
The state machine models six mutually exclusive states. Initiated guarantees that the transaction intent and idempotency key are durably saved to local storage before opening a network socket. Processing marks the request in-flight. Approved and Declined represent definitive terminal outcomes from the card issuer.
The critical state is Unknown or In-Doubt, triggered by connection drops or process termination. Transactions in this state are never treated as declined and are never naively retried. Instead, they transition to Reversed via an automated ISO 8583 reversal message or are resolved through backend ledger reconciliation.

## Interview answer — deep senior

From an ISO 8583 banking switch and EMV terminal architecture perspective, a payment state machine enforces ledger consistency across distributed, unreliable mobile networks.
The most dangerous vulnerability in client-side payments is treating an in-doubt state as a declined transaction. When a merchant taps to charge fifty dollars, a thirty-second gateway timeout can occur after the issuing bank captures the funds but before the mobile client receives the HTTP response. If the client naive logic marks this as failed, the cashier prompts the customer to swipe again, causing a catastrophic duplicate charge and merchant chargeback penalties.
To prevent this, the client architecture must enforce an atomic state machine backed by persistent storage like SQLite Room with Write-Ahead Logging. The transition to Initiated occurs inside a local transaction. When entering Processing, the app assigns an immutable idempotency key and correlation ID.
If a timeout or sudden power failure occurs, the state engine transitions to Unknown. The system immediately enqueues a background task in an isolated reversal queue, utilizing ISO 8583 0400 reversal messages. Furthermore, before initiating any subsequent transaction on the terminal, the POS software queries the gateway status endpoint. If the gateway confirms that authorization succeeded, the local transaction updates monotonically to Approved and prints the customer receipt. If authorization failed or was absent, the reversal releases held funds. This ensures perfect accounting balance regardless of battery pulls or carrier drops.

## How to answer in the interview

- **Why:** timeout leaves financial outcome unknown.
- **How:** tie every legal transition to evidence and a durable operation ID.
- **Trade-off:** the model must map richer provider states without inventing equivalence.
- **Failure case:** a late callback overwrites a reconciled result.
- **Production solution:** commit intent before I/O, guard transitions, and reconcile nonfinal rows.

## Deep-dive talking points

Prompt for transition table, unknown timeout, durable intent, late callback ordering and provider evidence.

## Follow-up questions

- **Interviewer:** "Why is treating a network timeout as a 'Declined' payment dangerous in financial apps?"
  **Answer:** "Because the issuer may have already approved and deducted the funds; treating it as declined causes the customer to pay twice upon re-trying."

- **Interviewer:** "What is the primary objective of an ISO 8583 reversal message?"
  **Answer:** "To instruct the issuer to release pre-authorized funds and void an in-doubt transaction when the client terminal did not receive confirmation."

## Self-check rubric

Can I distinguish timeout from decline, identify authoritative transitions and describe recovery?

## References and reviewed-on date

- [Stripe PaymentIntent lifecycle](https://docs.stripe.com/payments/paymentintents/lifecycle) — one provider’s state model.
- [Android offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first) — durable local data concepts.

Technically reviewed against primary documentation on 2026-10-13.
