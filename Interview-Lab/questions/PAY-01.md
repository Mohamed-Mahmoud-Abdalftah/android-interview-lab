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

A payment state machine governs financial transaction lifecycles across explicit states: Initiated (locally persisted), Processing (in-flight), Approved (issuer authorized), Declined (issuer rejected), Unknown (network drop/timeout during transit), and Reversed (undone via auto-reversal). It prevents double-charging and catastrophic state ambiguity.

## Interview answer — structured

A deterministic payment state machine is the foundational architectural safeguard in fintech and POS engineering.

First, **Eliminating the Binary Fallacy**. Next, financial transactions must never be modeled as a boolean (success/failure). Network timeouts produce ambiguous states where funds were deducted at the issuer bank but never acknowledged on the mobile terminal.
**The Six Canonical Transaction States**. With Initiated, transaction intent, idempotency key, and payload are durably written to disk (Room/SQLite) before opening any socket connection.
A Processing is the payload is in transit to the payment gateway or EMV switch. With Approved, cryptographically signed confirmation received with an authorization code.
With Declined, explicit rejection code (e.g., insufficient funds, expired card); a terminal state requiring no automatic retries. With Unknown / In-Doubt, network timeout, socket hangup, or terminal reboot occurs mid-flight. Funds may or may not have been captured.
A Reversed is an automated reversal (0400/0420 ISO 8583 message) has released held funds back to the cardholder. **State Transition Guarantees**.
Finally, transitions must be strictly monotonic and persisted atomically in local databases to survive sudden process termination or hardware battery pulls.


## Interview answer — deep senior

From an ISO 8583 and payment terminal compliance perspective, managing the 'Unknown' state dictates ledger consistency.

First, with The 'In-Doubt' Protocol, when a transaction enters the `Unknown` state due to a 30-second gateway read timeout, client apps must **never immediately retry the authorization request**. Doing so risks charging the customer twice. The terminal must enqueue an automated Reversal (ISO 8583 0400 reversal message) and mark the local record as pending reversal. Next, with Terminal Status Inquiry vs. Auto-Reversal, high-reliability POS devices execute a Status Inquiry (`/v1/payments/{id}/status`) before issuing a reversal. If the gateway confirms the charge was captured, the client reconciles the transaction as Approved and prints the receipt; if not captured or still pending, it executes the reversal.
Finally, with Crash-Resistant State Machine Engines, in Android, state machines must be tied to persistent WorkManager tasks and Room database observers rather than ViewModel in-memory state. If Android kills the app process due to low memory while in `Processing`, upon next launch the app inspects Room and resumes the reconciliation workflow.


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
