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

## Concept and technical explanation

When a payment is approved by the card issuer but the terminal loses electrical power before persisting the approval response, the system enters a split-brain state requiring disciplined boot-time recovery and batch reconciliation:
- The Split-Brain Disaster:
  - Bank Ledger State: The issuer approved the transaction, assigned an authorization code and Retrieval Reference Number (RRN), and locked or deducted the cardholder's funds.
  - Terminal Ledger State: The local database record remains in `INITIATED` or `PROCESSING` because the device lost power before flushing the `APPROVED` state to flash memory.
- Multi-Stage Recovery Architecture:
  1. Boot-Time Journal Scan:
     - Upon reboot (`android.intent.action.BOOT_COMPLETED`), the application startup coordinator inspects the local Room database before opening any cashier UI.
     - Any transaction stranded in `INITIATED` or `PROCESSING` is immediately flagged as `IN_DOUBT`.
  2. Authoritative Status Inquiry (Check Before Reverse):
     - The terminal dispatches an authenticated Status Inquiry request to the payment gateway using the immutable `idempotencyKey` and `correlationId`.
     - Scenario A (Approved on Gateway): The gateway returns the original authorization response. The terminal updates the local journal to `APPROVED`, saves the RRN, and automatically prints a receipt marked "RECOVERED TRANSACTION - DUPLICATE RECEIPT".
     - Scenario B (Unknown / Expired on Gateway): The terminal dispatches an ISO 8583 0400 Reversal to release any orphaned funds hold.
  3. End-of-Day Settlement Reconciliation (Z-Report):
     - If the terminal remains offline throughout the business day, the end-of-day batch settlement process compares the terminal's journal against the acquirer's switch ledger. Any unmatched authorization is automatically flagged for merchant review and resolved without double-billing.

## Practical walkthrough (English)

Implementing boot-time payment recovery and status reconciliation in Kotlin:
```kotlin
class BootRecoveryCoordinator(
    private val journalDao: PaymentJournalDao,
    private val paymentGatewayApi: PaymentGatewayApi,
    private val receiptPrinter: PosReceiptPrinter
) {
    suspend fun recoverStrandedTransactions() {
        val strandedTransactions = journalDao.getStrandedInFlightTransactions()

        for (tx in strandedTransactions) {
            // Mark as IN_DOUBT locally to prevent conflicting cashier actions
            journalDao.updateStatus(tx.id, "IN_DOUBT")

            try {
                // Authoritative Status Inquiry using the original immutable idempotency key
                val statusResult = paymentGatewayApi.queryStatus(
                    orderId = tx.orderId,
                    idempotencyKey = tx.idempotencyKey
                )

                when (statusResult) {
                    is GatewayStatus.Approved -> {
                        // Issuer approved it: Reconcile locally and print recovered receipt
                        journalDao.markApproved(tx.id, statusResult.authCode, statusResult.rrn)
                        receiptPrinter.printCustomerReceipt(
                            orderId = tx.orderId,
                            amount = tx.amountCents,
                            authCode = statusResult.authCode,
                            isRecovered = true
                        )
                    }
                    is GatewayStatus.NotFoundOrDeclined -> {
                        // Gateway has no record or failed: Execute Reversal to guarantee customer safety
                        paymentGatewayApi.sendReversal(tx.id, tx.correlationId)
                        journalDao.markReversed(tx.id)
                    }
                    is GatewayStatus.Pending -> {
                        // Gateway is still processing: Keep in-doubt and retry on next cycle
                    }
                }
            } catch (e: IOException) {
                // Network unavailable: will be reconciled during nightly settlement
            }
        }
    }
}
```

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

When a terminal loses power before recording an issuer approval, a split-brain state occurs. On reboot, the terminal identifies the stranded transaction, flags it as in-doubt, and performs an authoritative status inquiry using the original idempotency key. If approved, it records the authorization and prints a recovered receipt; if absent, it dispatches an automated reversal, resolving offline discrepancies during end-of-day reconciliation.

## Interview answer — structured

Handling a sudden power loss after bank approval but before local persistence requires an automated recovery and reconciliation protocol.
In this failure scenario, a split-brain condition arises: the cardholder's issuing bank has captured the funds, but the terminal's local database remains in an in-flight processing state.
To restore accounting consistency, the terminal executes a recovery routine during device boot before permitting any new sales. It scans the local database for stranded in-flight records and transitions them to In-Doubt.
Next, the terminal initiates a status inquiry to the payment gateway utilizing the persisted idempotency key and correlation ID.
If the gateway confirms that the authorization succeeded, the terminal updates the transaction to Approved, saves the authorization code and reference numbers, and prints a duplicate receipt for the merchant and customer.
If the gateway reports that the transaction was never captured, the terminal issues an ISO 8583 reversal message to release any potential funds hold. If the device remains offline, the discrepancy is reconciled during the end-of-day batch settlement.

## Interview answer — deep senior

From an ISO 8583 transaction processing and financial audit reconciliation perspective, a power failure occurring precisely between bank authorization and local persistence represents one of the most critical operational edge cases in retail engineering.
In this split-brain failure mode, the issuing bank has debited or held the customer's funds, and the payment gateway has recorded a successful transaction. However, because electrical power was cut before the terminal's SQLite database committed the response payload, the terminal boots up with no record of success. If the cashier assumes the payment failed and requests another card swipe, the customer is double-billed, leading to severe chargeback disputes.
The robust architectural solution divides resolution into immediate boot recovery and deferred batch reconciliation.
At boot time, triggered by the BOOT_COMPLETED intent, the startup manager queries Room for records stuck in INITIATED or PROCESSING. The system immediately locks the terminal cashier interface to prevent further transactions.
The recovery engine then dispatches a Status Inquiry request to the gateway, supplying the original immutable idempotency key and correlation ID. The gateway looks up the transaction in its distributed ledger.
If the gateway returns an Approved status, the terminal executes an atomic database transaction updating the record to APPROVED with the original authCode and RRN, immediately spooling a customer receipt clearly stamped "RECOVERED TRANSACTION - DUPLICATE".
If the gateway reports that the transaction timed out or was declined, the terminal enqueues an ISO 8583 0400 reversal to release any pending holds.
Finally, as an ironclad safety net, if connectivity cannot be re-established, the nightly Z-Report batch reconciliation compares the terminal's offline journal with the acquirer switch summary. Any unpaired transaction is flagged in an exception report, enabling finance teams to balance the books without manual customer friction.

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
