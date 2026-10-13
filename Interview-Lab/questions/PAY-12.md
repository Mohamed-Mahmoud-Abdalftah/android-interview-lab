---
id: "PAY-12"
question: "A POS transaction is approved by issuer but the terminal loses power before saving it. Describe recovery and reconciliation."
topic: "Bonus: Payment/POS & Security Scenarios"
code: "PAY"
group: "C"
phase: 5
priority: "P2"
order: 482
editorial_status: "reviewed"
---

# PAY-12

## Original interview question

A POS transaction is approved by issuer but the terminal loses power before saving it. Describe recovery and reconciliation.

## What the interviewer evaluates

- Recovery when issuer approved but terminal lost power before local save.
- Need for backend/provider record and reconciliation beyond local DB.

## Explanation in Arabic

وافق البنك المصدر (Issuer) على معاملة نقطة البيع (POS)، ولكن الماكينة فقدت الطاقة تماماً وانطفأت قبل حفظ الموافقة. اشرح بالتفصيل بروتوكول التعافي والمطابقة (Recovery & Reconciliation)؟

1. توصيف الكارثة المالية (The Nightmare Scenario):
   - التاجر يدخل عملية بيع بـ 1,000 دولار.
   - يتصل البنك ويوافق ويحجز الـ 1,000 دولار من حساب العميل (Approved).
   - قبل أن يكتب التطبيق كود الموافقة في قاعدة البيانات، انطفأت الماكينة (فصل الكهرباء أو نزع البطارية)!
   - العميل تصله رسالة SMS على هاتفه: "تم خصم 1,000 دولار".
   - الماكينة عند إقلاعها: لا تعرف هل تمت العملية أم لا، ولم تطبع إيصالاً، والتاجر يرفض تسليم البضاعة!

2. بروتوكول التعافي التلقائي عند الإقلاع (Post-Boot Recovery Protocol):
   - **الخطوة 1: فحص الإقلاع (Startup Ledger Audit)**:
     * عند إقلاع تطبيق الـ POS، يبحث فوراً في قاعدة البيانات عن أي معاملة في حالة `PROCESSING` أو `INITIATED`.
     * يجد المعاملة رقم `tx_987` معلقة بدون قرار نهائي.
   - **الخطوة 2: الاستعلام عن الحالة (Status Inquiry / Query Host)**:
     * ترسل الماكينة استعلاماً فورياً لخادم الدفع باستخدام الـ `Correlation ID` والـ `Idempotency Key` المحفوظين قبل انقطاع الكهرباء: "ما هي النتيجة النهائية للمعاملة `tx_987`؟"
   - **الخطوة 3: معالجة سيناريوهات الرد**:
     * **السيناريو أ (الموافقة كانت مؤكدة)**: يرد الخادم ببيانات الموافقة (`AuthCode: 458921`). يقوم التطبيق بتحديث السجل إلى `APPROVED` فوراً، ويطبع إيصالاً بعنوان بارز: **"إيصال مسترجع - تم الخصم بنجاح (RECOVERED DUPLICATE RECEIPT)"** لتسليم البضاعة للعميل.
     * **السيناريو ب (المعاملة لم تكتمل أو معلقة في البنك)**: ترسل الماكينة طلب عكس فوري (**Auto-Reversal 0400**) لإلغاء الحجز فوراً واسترجاع المبلغ لحساب العميل، وتطبع إيصال إلغاء وتطلب من الكاشير إعادة المحاولة.

## Practical walkthrough

مخطط منطق التعافي الآلي عند إقلاع تطبيق أندرويد POS بعد انقطاع الطاقة:
```kotlin
class StartupRecoveryManager(
    private val paymentDao: PaymentDao,
    private val gatewayApi: PaymentGatewayApi,
    private val receiptPrinter: ReceiptPrinter
) {
    suspend fun recoverInDoubtTransactionsOnBoot() = withContext(Dispatchers.IO) {
        // 1. استخراج أي معاملات كانت قيد المعالجة ولم تكتمل:
        val strandedTransactions = paymentDao.getTransactionsByState("PROCESSING")

        for (tx in strandedTransactions) {
            try {
                // 2. الاستعلام عن حالة العملية لدى خادم الدفع باستخدام نفس الـ ID:
                val statusResponse = gatewayApi.queryTransactionStatus(tx.idempotencyKey)

                if (statusResponse.isApproved) {
                    // تم الخصم بنجاح: تأكيد محلي وطباعة إيصال التعافي:
                    paymentDao.markApproved(tx.id, statusResponse.authCode)
                    receiptPrinter.printDuplicateReceipt(tx, statusResponse.authCode)
                } else {
                    // لم تكتمل في البنك: إطلاق Reversal لتنظيف أي حجز معلق:
                    gatewayApi.sendReversal(tx.toReversalPayload())
                    paymentDao.markReversed(tx.id)
                    receiptPrinter.printReversalNotice(tx)
                }
            } catch (e: Exception) {
                // تعذر الاتصال بالخادم: إدراجها في Reversal Queue للمطابقة لاحقاً:
                paymentDao.markAwaitingReconciliation(tx.id)
            }
        }
    }
}
```

## Why it matters and how it works

Local and remote commits cannot be atomic. A write-ahead attempt reduces uncertainty, while server operation records and provider references supply independent evidence. Reconciliation compares terminal, backend and issuer/acquirer status; a protocol-specific reversal may be required when sale completion cannot be confirmed.

## Worked example

On restart, load nonterminal attempts and query status by original operation ID. If approval is found, persist it and decide whether the sale can complete or needs reversal under the acquirer’s rules. If no local attempt survived, backend reconciles provider records using terminal/batch references and raises an operations case.

## Trade-offs and decision criteria

More durable pre-send writes add latency but reduce orphaned approvals. Local backup is insufficient for a physically destroyed terminal; central records are necessary. Provider status APIs may be delayed, so unknown may persist temporarily.

## Failure modes

Marking the transaction declined because no local row exists can prompt a second charge. Trusting a new local row to undo issuer approval is also wrong. Test power removal at every point and reconcile independently of terminal UI.

## Production perspective

Use an operations dashboard for orphaned authorizations, settlement mismatches and reversal deadlines. Store only safe references locally; provider/backend retains authoritative financial records and incident runbooks.

## Interview answer — short

Recover an in-doubt transaction after sudden power loss by auditing the database on boot, querying the payment gateway using the persistent idempotency key via a Status Inquiry, and either marking the transaction Approved and printing a recovered receipt if captured, or dispatching an automated Reversal if unconfirmed.

## Interview answer — structured

Handling power loss during the authorization commit window is a core requirement of POS terminal certification:

1. **The In-Doubt Dilemma**:
   - The acquiring host approved the transaction and sent the SMS to the cardholder, but terminal volatile RAM was destroyed before the approval code hit SQLite or the thermal printer engaged.

2. **The Systematic Recovery Protocol**:
   - **Boot-Time Ledger Scan**: Upon application startup, a `StartupRecoveryService` scans the persistent Room ledger for records lingering in `PROCESSING` or `INITIATED` status.
   - **Host Status Inquiry**: The terminal dispatches a Status Inquiry request (`GET /v1/payments/status`) presenting the durable `idempotency_key` and original `correlation_id`.
   - **Branch A (Gateway Captured)**: If the host confirms approval, the terminal transitions the local state to `APPROVED`, persists the authorization code, and automatically prints a marked duplicate receipt (`RECOVERED TRANSACTION RECEIPT`) so the merchant can release goods.
   - **Branch B (Host Incomplete / Pending)**: If the host reports the transaction as pending or unconfirmed, the terminal generates an automated reversal (0400 Reversal message) to release the authorization hold, marks local state as `REVERSED`, and prints a void notification.

3. **End-of-Day Batch Reconciliation Safety Net**:
   - If connectivity fails completely during boot inquiry, the record is flagged for end-of-day batch reconciliation. During clearing, host and terminal ledgers are reconciled before merchant settlement payout.

## Interview answer — deep senior

From an EMV Level 2 transaction state machine perspective, hardware terminal certification enforces specific rules:

1. **EMV Second Generate AC (Application Cryptogram) Failure**: In chip transactions, after receiving host authorization, the terminal must feed the issuer script back to the physical chip to generate the final Application Cryptogram (TC - Transaction Certificate). If power is lost before the chip generates TC, the transaction is **legally incomplete under EMV rules**, even if the issuer approved it! In this scenario, EMV compliance mandates issuing an automatic reversal because the chip never confirmed the sale.

2. **Preventing Cashier Panic Retries**: During boot recovery, the UI must display a non-dismissible modal: 'Reconciling pending transactions, please wait...' This prevents a hurried cashier from attempting a second card swipe before the system has determined the fate of the first charge.

3. **Merchant Protection Receipts**: The thermal printer must produce physical receipts with clear cryptographic audit markers (STAN, RRN, Auth Code, masked PAN) so the merchant is protected against chargeback disputes.

## How to answer in the interview

- **Why:** issuer approval and terminal persistence cannot be one atomic transaction.
- **How:** recover by original ID, then compare independent ledgers.
- **Trade-off:** some cases require manual operations when evidence is incomplete.
- **Failure case:** new charge or false declined receipt after power loss.
- **Production solution:** pre-send write, reconciliation, escalation, and tested reboot path.

## Deep-dive talking points

Prompt for pre-send intent, missing-local-record case, central ledger, delayed status and reversal SLA.

## Follow-up questions

- **Interviewer:** "What is an EMV Transaction Certificate (TC) and why does power loss break it?"
  **Answer:** "A cryptographic proof generated by the card chip confirming completion; if power is cut before the chip generates TC, EMV rules mandate reversing the transaction."

- **Interviewer:** "Why should the POS UI display a blocking dialog during startup recovery?"
  **Answer:** "To prevent the cashier from initiating a new charge while the terminal is reconciling whether the previous customer was already billed."

## Self-check rubric

Can I recover with and without a local intent and explain the unavoidable distributed gap?

## References and reviewed-on date

- [Android Room transactions](https://developer.android.com/reference/kotlin/androidx/room/package-summary) — local transaction boundary.
- [Stripe PaymentIntent lifecycle](https://docs.stripe.com/payments/paymentintents/lifecycle) — example provider status lifecycle.

Technically reviewed against primary documentation on 2026-10-13.
