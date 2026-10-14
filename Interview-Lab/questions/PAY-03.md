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

Authorization holds funds on the card. Reversal immediately cancels an in-flight authorization due to technical failure before completion. Void cancels an approved transaction on the same day before batch settlement with no interchange fees. Refund transfers settled funds back days later incurring fees. Reconciliation audits terminal records against bank ledgers.

## Interview answer — structured

Understanding financial lifecycle operations is essential for architects building transactional mobile systems.

First, **Authorization (Auth)**. Next, verifies card authenticity and places a temporary hold on the customer's credit line. Does not transfer money; funds are transferred only upon subsequent 'Capture' or batch settlement.
**Reversal (Auto-Reversal / 0400 Message)**. An automated, immediate technical rollback executed by terminal firmware or client code when a transaction succeeds at the bank but fails locally (e.g. Printer paper jam, EMV chip reader failure, or client timeout). Releases the hold within seconds.
**Void**. A merchant-initiated cancellation of an approved transaction executed **prior to end-of-day batch settlement**. The transaction is dropped from the clearing batch; no interchange fees are incurred, and the hold drops off.
**Refund**. Executed **post-settlement** when funds have already migrated into the merchant's acquiring bank. It initiates an inverse funds transfer, incurring interchange transaction processing fees and taking 3–7 business days.
**Reconciliation**. Finally, the operational auditing process matching local terminal transaction storage records against payment gateway settlement logs, isolating discrepancies and stranded balances.


## Interview answer — deep senior

From an EMV L2 kernel and payment network compliance perspective, subtle operational nuances exist.

First, with The 'Void vs. Reversal' Architecture Nuance, developers often confuse Voids and Reversals. A Reversal undoes an authorization that never successfully finished its complete terminal protocol handshake. A Void cancels a transaction that was 100% completed, printed, and approved, but the merchant manually voids it before midnight settlement. Next, with Partial Reversals in Split Tenders, in multi-tender checkouts (e.g. Paying $50 with Gift Card and $50 with Visa), if the Visa authorization succeeds but the Gift Card fails, the client engine must trigger a Partial Reversal strictly against the Visa transaction while restoring the cart state.
Finally, with Reconciliation Batch Balancing, in Smart POS Android devices (Pax, Poynt, Sunmi), closing the business batch sends an ISO 8583 0500 Batch Upload message summarizing total counts and debit volumes. If terminal and host totals mismatch by even 1 cent, the host halts settlement and forces a manual transaction-by-transaction reconciliation audit.


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
