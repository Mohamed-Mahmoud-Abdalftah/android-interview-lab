---
id: "PAY-03"
question: "What are authorization, reversal, void, refund, and reconciliation?"
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "A"
phase: 5
priority: "P2"
order: 473
editorial_status: "reviewed"
---

# PAY-03

## Original interview question

What are authorization, reversal, void, refund, and reconciliation?

## What the interviewer evaluates

- Distinct meanings of authorization, reversal, void, refund and reconciliation.
- Provider/network-specific timing and state.

## Concept and technical explanation

The card payment lifecycle consists of distinct financial, cryptographic, and accounting operations governing how funds move between cardholders, merchants, and acquiring banks:
- 1. Authorization:
  - Definition: The cardholder's issuing bank verifies credentials (CVV, 3D Secure, PIN) and places an administrative hold (pre-authorization) on the requested amount.
  - Financial Impact: Funds are reserved in the cardholder's credit limit, but no actual money transfers between bank accounts yet.
- 2. Reversal (Auto-Reversal):
  - Definition: Immediate cancellation of an in-flight or in-doubt authorization (ISO 8583 0400/0420 transaction).
  - Condition: Executed when a terminal crashes, times out, or detects a local printing/hardware failure right after transmitting authorization.
  - Financial Impact: Releases the hold immediately. Zero merchant fees incurred because clearing never began.
- 3. Void:
  - Definition: Cancellation of an approved transaction on the same calendar day *before* the merchant's end-of-day batch settlement cut-off.
  - Condition: Customer immediately cancels purchase at the checkout counter before the register closes.
  - Financial Impact: Erases the transaction from the pending batch. Funds hold drops off within hours; no interchange fees charged.
- 4. Refund:
  - Definition: Transfer of money back to the cardholder *after* batch settlement and funds clearance have completed.
  - Condition: Customer returns physical merchandise days after the original purchase.
  - Financial Impact: Requires a separate financial settlement cycle (3-5 business days) and incurs non-refundable merchant interchange processing fees.
- 5. Reconciliation (Settlement Balancing):
  - Definition: The end-of-day accounting audit (Z-Report) comparing the mobile/POS terminal's local durable transaction journal against the acquirer/switch ledger.
  - Outcome: Detects missing transactions, out-of-balance batches, or orphaned authorizations, ensuring complete ledger parity.

## Practical walkthrough (English)

State mapping and lifecycle semantics in Kotlin domain models:
```kotlin
enum class FinancialOperationType {
    AUTHORIZE,  // Reserves funds (Hold on cardholder account)
    REVERSAL,   // Immediate release of in-doubt hold prior to batch close
    VOID,       // Cancellation of approved charge before end-of-day settlement
    REFUND,     // Credit transfer back to cardholder post-settlement
    RECONCILE   // Batch matching local terminal records vs bank switch
}

data class TransactionRecord(
    val transactionId: String,
    val rrn: String?,          // Retrieval Reference Number
    val authCode: String?,
    val amountCents: Long,
    val state: OperationState,
    val settledAtBatchId: String? // Null if unsettled (eligible for Void)
) {
    val canBeVoided: Boolean
        get() = settledAtBatchId == null && state == OperationState.APPROVED

    val requiresRefund: Boolean
        get() = settledAtBatchId != null && state == OperationState.APPROVED
}
```

## Explanation in Arabic

ما هي الفروق الجوهرية بين العمليات المالية الأساسية: التفويض (Authorization)، والعكس (Reversal)، والإلغاء (Void)، والاسترداد (Refund)، والمطابقة (Reconciliation)؟

1. التفويض (Authorization - Auth):
   - عملية حجز المبلغ في حساب حامل البطاقة والتأكد من وجود رصيد كافٍ وصلاحية البطاقة دون سحب المبلغ فوراً إلى حساب التاجر.
   - يتم سحب المبلغ فعلياً لاحقاً في مرحلة تسمى **التسوية (Capture / Settlement)**.

2. العكس التلقائي (Reversal):
   - عملية إلغاء فورية وفنية تُطلقها ماكينة الدفع أو التطبيق **أثناء المعاملة نفسها وقبل إتمام الجلسة**.
   - تحدث عندما يفشل الهاتف في استلام الرد، أو ينفد ورق الطابعة، أو يفشل قارئ البطاقات الذكية (EMV Chip Failure). يقوم البنك بإلغاء حجز المبلغ فوراً وإعادته للعميل في ثوانٍ.

3. الإلغاء اليدوي (Void):
   - إلغاء معاملة كاملة وافق عليها البنك بالفعل، ولكن **قبل إغلاق دورة العمل اليومية وتسوية الحسابات (Before Batch Settlement)**.
   - ميزته: لا يتم خصم أي رسوم معالجة (Interchange fees) على التاجر أو العميل لأن الأموال لم تنتقل بعد بين البنوك.

4. الاسترداد (Refund):
   - إعادة الأموال للعميل **بعد إغلاق الدورة المالية وانتقال الأموال لحساب التاجر (After Settlement)** (مثلاً بعد يومين عندما يرجع العميل البضاعة).
   - تستغرق من 3 إلى 10 أيام عمل لتظهر في كشف حساب العميل وتتحمل الشركة رسوم معالجة.

5. المطابقة اليومية (Reconciliation):
   - فحص وتطابق السجلات المحلية المخزنة في ماكينة الـ POS مع سجلات البنك وخادم الدفع في نهاية كل يوم؛ للتأكد من عدم وجود أي مبالغ مفقودة أو معاملات معلقة.

## Practical walkthrough

جدول مقارنة شامل للعمليات المالية ودورة حياة المعاملة:
```markdown
| العملية المالية | التوقيت (Timing) | التأثير على الرصيد | الرسوم (Fees) | زمن الظهور للعميل |
|---|---|---|---|---|
| **Authorization** | لحظة الشراء | حجز المبلغ (Hold) | لا توجد رسوم نهائية | فوري |
| **Reversal** | فوري (ثوانٍ بعد عطل فني) | إلغاء الحجز فوراً | صفر | ثوانٍ إلى دقائق |
| **Void** | نفس اليوم (قبل إغلاق الـ Batch) | إلغاء العملية بالكامل | صفر رسوم انتقال | 24 إلى 48 ساعة |
| **Refund** | بعد أيام (بعد إغلاق الـ Batch) | تحويل عكسي من التاجر للعميل | يتحمل التاجر رسوم المعالجة | 3 إلى 7 أيام عمل |
| **Reconciliation** | يومياً في نهاية الـ Shift | مطابقة دفاتر الحسابات | - | تقرير تدقيق مالي |
```
نموذج الكود لإصدار Reversal فوري عند فشل محلي في أندرويد:
```kotlin
suspend fun executePaymentWithSafeReversal(paymentRequest: PaymentRequest) {
    val txId = paymentDao.insertPending(paymentRequest)
    try {
        val authResponse = paymentGateway.authorize(paymentRequest)
        // إذا انقطع التيار الكهربائي هنا أو تعطل طبع الإيصال، يجب إطلاق Reversal!
        printReceiptOrThrow(authResponse)
        paymentDao.markCompleted(txId, authResponse.authCode)
    } catch (e: ReceiptPrintException) {
        // عطل محلي بعد الموافقة -> إطلاق Reversal فوري للبنك لحماية العميل:
        reversalQueueManager.enqueueImmediateReversal(txId, paymentRequest)
        throw PaymentAbortedException("Hardware failure; transaction reversed.", e)
    }
}
```

## Why it matters and how it works

The payment lifecycle has separate business and accounting effects. An approved authorization is not automatically settled cash. Reversal, void and refund have different allowed windows, references and provider APIs. Reconciliation compares independent ledgers and resolves unknown/missing outcomes.

## Worked example

A POS authorization times out after the issuer approved it. The terminal marks unknown, queries status and may send a reversal with the original transaction reference under the acquirer protocol. If a settled customer purchase is returned days later, that is a refund workflow, not an authorization reversal.

## Trade-offs and decision criteria

Automatic reversal can limit open authorizations, but an incorrect reversal may conflict with completed sale state. Refunds have customer-service and fraud considerations. Decide only after authoritative status and provider-specific rules.

## Failure modes

Treating every timeout as “refund” can create a second financial movement even if the original payment never settled. Treating void and reversal as synonyms can call the wrong API. Maintain explicit states and protocol references.

## Production perspective

Document provider mapping and settlement cutoffs with payments specialists. Reconciliation jobs compare transaction IDs and amounts, flag mismatches, and route unresolved cases to operations without exposing PAN/PIN in logs.

## Interview answer — short

Authorization places a hold on cardholder funds without moving money. Reversal cancels an in-doubt authorization immediately due to terminal errors with zero fees. Void cancels an approved transaction before daily batch settlement. Refund returns settled money days later incurring processing fees. Reconciliation audits local terminal journals against bank switch ledgers to resolve financial discrepancies.

## Interview answer — structured

The card payment lifecycle consists of five distinct accounting and settlement operations.
Authorization verifies card validity and places a temporary hold on the customer's funds. Money does not change hands until final capture.
Reversal is an automated emergency operation executed immediately when a terminal experiences a communication timeout or crash while awaiting authorization. It signals the bank to cancel the hold right away, incurring zero merchant fees.
Void cancels an approved transaction within the same business day before the merchant closes and settles the daily batch. The transaction is removed from the settlement file, sparing both parties processing fees.
Refund occurs after batch settlement has finalized and money has moved to the merchant's bank account. Returning funds requires a new transaction that takes several days to clear and incurs processing fees.
Reconciliation is the end-of-day balancing process where the terminal transmits its local transaction journal to the bank switch to detect and reconcile any missing or mismatched records.

## Interview answer — deep senior

From a payment operations and financial settlement architecture standpoint, distinguishing between these five operations is vital for ledger integrity and merchant fee minimization.
Authorization is purely an administrative hold on the cardholder's credit limit. Under EMV and ISO 8583 standards, an authorization code confirms that funds exist and are locked, but actual interbank clearing occurs during nightly batch processing.
The critical distinction between Reversal and Void lies in timing and certainty. A Reversal is an automated, real-time message dispatched when the terminal detects an ambiguous failure, such as a printer paper jam or a socket disconnect after sending an authorization request. Reversals release held funds instantaneously and protect the merchant from chargebacks. A Void, conversely, is an intentional business action taken when a customer returns goods before batch cut-off. Because the transaction has not settled, voiding erases the transaction without interchange fees.
Refunds, on the other hand, occur post-settlement. Once the merchant's daily batch is submitted and funds are wired through the clearing house, the original transaction cannot be voided. A refund must be initiated as a separate credit transaction, which takes three to five business days and permanently forfeits merchant processing fees.
Finally, Reconciliation is the audit mechanism that guarantees ledger truth. Every certified POS terminal maintains a local tamper-evident journal. At end-of-day, the terminal executes a settlement handshake, transmitting transaction counts and sums. If discrepancies appear, automated exception reports trigger dispute workflows, ensuring full accounting alignment across banks and merchants.

## How to answer in the interview

- **Why:** these operations act at different lifecycle and accounting stages.
- **How:** identify the original authorization, settlement state, and permitted provider action.
- **Trade-off:** provider vocabulary and windows vary.
- **Failure case:** treating a settled charge as voidable or a lost response as decline.
- **Production solution:** map the acquirer contract, record references, and reconcile ledgers.

## Deep-dive talking points

Prompt for lifecycle timing, original reference, separate refund identity and reconciliation ledger matching.

## Follow-up questions

- **Interviewer:** "Why is a Void commercially preferred over a Refund if a customer cancels an order on the same day?"
  **Answer:** "Because a Void cancels the transaction before settlement, eliminating payment gateway interchange processing fees for the merchant."

- **Interviewer:** "What is the difference between Authorization and Settlement (Capture)?"
  **Answer:** "Authorization holds the funds on the cardholder's credit limit; Settlement captures and transfers the actual money from the issuer to the merchant bank."

## Self-check rubric

Can I classify five terms by lifecycle stage and avoid assuming universal provider behavior?

## References and reviewed-on date

- [Stripe PaymentIntent lifecycle](https://docs.stripe.com/payments/paymentintents/lifecycle) — provider-specific authorization/capture states.
- [Stripe refunds](https://docs.stripe.com/refunds) — refund as separate workflow.

Technically reviewed against primary documentation on 2026-10-13.
