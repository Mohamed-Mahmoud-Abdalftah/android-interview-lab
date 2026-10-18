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

Can the candidate preserve an attempt identity before submission, distinguish issuer authorization from capture and settlement, recover an unknown result through provider-specific status inquiry, and reconcile local and authoritative records without assuming an automatic reversal?

## Concept and technical explanation

An issuer may authorize a transaction while the POS device loses power before recording the response. The local attempt is then in doubt; a missing device response is not a decline. Persist an attempt and the required correlation identifiers before sending. On restart or restored connectivity, query the terminal, backend, or processor using the integration contract. A local database transaction cannot be atomic with a remote authorization. If the local record itself is missing, reconcile against external records; an empty journal is not evidence that the payment did not occur. Authorization, capture, and settlement remain distinct states.

## Practical walkthrough (English)

The terminal records an attempt ID and protocol references before submitting a sale. Power fails after issuer approval. When the app opens again, it shows the sale as Unknown and blocks a fresh sale for the same purchase. A recovery path requests the original transaction status. A confirmed processed result updates the journal; an in-progress or unreachable result stays unresolved. The cashier follows the provider and merchant policy for receipts. Later reconciliation compares device, backend, and acquirer records. No automatic reversal follows merely from missing a response.

## Explanation in Arabic

لو الـ Issuer وافق لكن الجهاز فصل قبل حفظ الرد، السجل المحلي ممكن يفضل Processing رغم إن التفويض اتسجل عند مزود الدفع. الموافقة مش دليل لوحدها إن المبلغ اتعمله Capture أو Settlement؛ ده يعتمد على عقد الدفع. العلاج يبدأ قبل الإرسال: احفظ محاولة بمعرّف ثابت وبيانات ربط مناسبة. بعد رجوع الجهاز، اعتبر النتيجة Unknown، واستعلم بالطريقة اللي مزود الدفع بيدعمها. لو المصدر الموثوق أكد النتيجة، حدّث السجل؛ لو الرد لسه غير حاسم، ما تبدأش عملية جديدة لنفس البيع من غير إجراء متفق عليه. لو مفيش سجل محلي أصلًا، لازم مسار مطابقة مع الـ Backend أو مزود الدفع؛ قاعدة البيانات الفاضية مش إثبات إن العملية ما حصلتش.

## Practical walkthrough

الكاشير بدأ بيع بمبلغ محدد. التطبيق حفظ محاولة `attemptId` ومعرّفات البروتوكول المطلوبة قبل الطلب، ثم الجهاز فقد الطاقة بعد موافقة الـ Issuer. عند تشغيل التطبيق، السجل ما زال Processing؛ الواجهة تعرض إن النتيجة قيد التحقق وتمنع Retry بمفتاح جديد. الـ Recovery worker أو شاشة التشغيل تستعلم من الـ Terminal/Backend حسب عقد التكامل، وتربط الرد بنفس المحاولة. لو رجع Approved، تحفظ نتيجة التفويض وتسمح بإيصال وفق سياسة التاجر؛ لو InProgress أو الشبكة مقطوعة، تفضل Unknown مع مسار متابعة واضح.

## Why it matters and how it works

A local journal gives recovery identity and intent but does not make the device and payment provider one atomic system. SQLite WAL can help local persistence according to configuration; it cannot prove what the issuer processed. Provider APIs may report processed, in progress, or not found, and each requires interpretation under that provider’s contract. Reconciliation catches mismatches that an immediate inquiry cannot settle.

## Worked example

Conceptual recovery sequence, not a runnable Kotlin or ISO 8583 implementation:

1. Persist an attempt with the protocol correlation IDs before submission.
2. Submit the sale and retain its identity across retries.
3. After restart, mark unresolved attempts Unknown and query their status.
4. Persist a confirmed response, or keep the attempt unresolved with an escalation path.
5. Compare device attempts with backend and acquirer records during reconciliation.

## Trade-offs and decision criteria

An immediate inquiry can reduce cashier uncertainty but does not replace later reconciliation. A locally durable attempt reduces lost identity but cannot guarantee remote consistency. Cancel, reversal, and refund are different operations with provider-specific eligibility and asynchronous outcomes. Choose only after establishing the actual transaction state and integration contract.

## Failure modes

Treating a missing response as decline can prompt a second charge. Blind reversal can be wrong for a transaction that was never received or has moved to another state. Printing an approved receipt from an unconfirmed local assumption misleads the customer. Losing correlation IDs before submission can make recovery dependent on external search and manual investigation.

## Production perspective

Keep the minimum allowed attempt and correlation data, avoiding sensitive card data. Recover at app startup or through suitable scheduled work, but do not rely on a boot broadcast for immediate financial correctness. Surface unresolved attempts to operations and prevent the cashier from silently repeating them. Match later settlement and acquirer records with local and backend attempts.

## Interview answer — short

I would treat the result as unknown, because issuer approval may have happened even though the terminal did not save the response. The attempt and provider correlation IDs need to be durable before submission. After restart I would query the original transaction through the supported terminal or backend path, then reconcile the device record with provider records. I would not start a new sale or assume a reversal succeeded while the original state is unresolved.

## Interview answer — structured

The missing local response does not mean the payment failed. The issuer may have authorized it while the terminal still shows an in-flight attempt. Before sending, I persist an attempt identity and the protocol references needed to find that exact transaction again.

After restart I show the cashier an unknown outcome and prevent a new sale for the same purchase. I use the provider’s status inquiry through the correct integration path. If it returns a confirmed original response, I store the corresponding state and follow merchant policy for a receipt. If it is in progress or connectivity is unavailable, I keep the attempt unresolved and arrange a retry or escalation. I also reconcile the device, backend, and acquirer records to catch later mismatches.

I separate issuer authorization from capture and settlement. Whether cancellation, reversal, or refund is appropriate depends on the provider contract and the confirmed state; sending one of those requests is not proof of completion.

## Interview answer — deep senior

This is a failure window between two systems. The remote processor may have an authorization while the device loses the response before writing it. Even a local Room transaction committed before submission cannot make the SQLite record atomic with the issuer. A local write-ahead log addresses local database durability conditions, not remote agreement. I therefore persist the attempt identity and permitted correlation references before calling the payment interface.

At startup or when connectivity returns, unresolved attempts are Unknown, not Declined. I ask the authoritative terminal, backend, or provider endpoint for the original result using the IDs required by that integration. A response can be processed, in progress, not found, or unavailable. Not found is not universally a safe retry signal: the IDs may be wrong, or the initial request may not have arrived. I follow the provider’s documented interpretation. If the local journal is gone entirely, external backend or acquirer records and merchant references become the recovery source, possibly with manual investigation.

When authorization is confirmed, I update the device record but do not automatically call it captured or settled. Receipt handling follows the merchant and terminal contract. If a cancel or reversal is appropriate, I submit it only for an eligible state and wait for confirmation; a request being sent does not mean funds are instantly released. Reconciliation then compares amounts, attempt IDs, provider references, and final outcomes across device, backend, and acquirer records. The user interface must keep an unresolved sale visible so a cashier cannot quietly repeat it.

## How to answer in the interview

Open with the unknown outcome. Explain pre-submission identity, status inquiry, and reconciliation. Distinguish authorization from later money movement and qualify provider-specific recovery.

## Deep-dive talking points

Local versus remote durability; correlation IDs; provider-specific processed/in-progress/not-found results; receipts after confirmation; manual recovery when the device journal is lost; later settlement discrepancies.

## Follow-up questions

- **Interviewer:** "What if status inquiry says not found?" **Answer:** "I verify the original IDs and the provider contract before retrying; not found can mean an incorrect reference or that the request never arrived."
- **Interviewer:** "Would you reverse every unknown payment?" **Answer:** "No. I first establish the actual state and use the contract’s cancel, reversal, or refund path only when appropriate, then confirm its outcome."

## Self-check rubric

Can I describe the two-system failure window, distinguish Unknown from Declined, and choose recovery without promising automatic reversal or settlement?

## References and reviewed-on date

- [Adyen verify transaction status](https://docs.adyen.com/point-of-sale/basic-tapi-integration/verify-transaction-status/).
- [Adyen capture and cancellation](https://docs.adyen.com/point-of-sale/capturing-payments/).
- [Android persistent work](https://developer.android.com/develop/background-work/background-tasks/persistent).

Adyen is one contract example, not a universal payment protocol. Technically reviewed against primary documentation on 2026-10-18.
