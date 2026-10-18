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

Does the candidate treat a client timeout as an unknown remote outcome, preserve a stable operation identity, depend on an actual backend idempotency contract, and reconcile before starting another charge?

## Concept and technical explanation

A client timeout after submission does not establish whether the server executed a payment. Persist a stable attempt identity before sending. The backend or provider must define idempotency scope, key retention, payload matching, and status lookup. After timeout, the client should show an unknown outcome and query the authoritative state. Repeating the same request with the same key is safe only within the documented contract. An idempotency key does not create exactly-once network execution.

## Practical walkthrough (English)

The customer confirms one order. The app stores an attempt ID and the identifiers required by the backend, then submits it. The response is lost. The UI shows Pending or Unknown and blocks a fresh charge for that order. A status inquiry finds the original attempt. A confirmed outcome updates the UI; an unresolved one remains pending with follow-up. The app retries a POST only if the backend contract supports the same key and payload within the key’s validity period.

## Explanation in Arabic

الـ Timeout يقول إن العميل ما استلمش نتيجة في الوقت المحدد؛ ما يقولش إن السيرفر ما نفذش. لو بدأت محاولة جديدة بمفتاح جديد ممكن يتكرر الخصم. استخدم هوية ثابتة للعملية تحفظها قبل الإرسال، وخلي الـ Backend أو مزود الدفع يطبّق Idempotency بحسب عقد واضح يشمل مدة الاحتفاظ بالمفتاح ومطابقة الطلب. بعد Timeout، الحالة Unknown لحد ما تعمل Status Inquiry أو Reconciliation. إعادة الطلب بنفس المفتاح تنفع فقط إذا العقد يسمح وبنفس المعطيات؛ Idempotency مش إثبات exactly-once network execution.

## Practical walkthrough

المستخدم أكد Order مرة واحدة. التطبيق خزّن `operationId` ومعاه Key مناسب للعقد، وبعت الطلب. الرد ما وصلش. الواجهة تعرض Pending/Unknown وتمنع زرار دفع جديد لنفس الـ Order. التطبيق يسأل الـ Backend عن نفس الـ operation؛ لو النتيجة مؤكدة يعرضها، ولو لسه Pending ينتظر أو يعيد الاستعلام. لو الـ Backend يسمح بإعادة POST بنفس Key ونفس Payload ضمن مدة صلاحيته، ممكن يعملها حسب سياسته. غير كده يحتاج مسار مراجعة بدل التخمين.

## Why it matters and how it works

`withTimeout` ends or cancels the client wait; it cannot roll back a remote effect. Local persistence preserves correlation across process death but cannot enforce server-side deduplication. The backend is the authority for the financial result, and a status API may use a payment ID or merchant reference rather than the idempotency key itself.

## Worked example

Conceptual sequence, not a runnable gateway SDK:

1. `createOrLoadAttempt(orderId)` persists one identity for the logical operation.
2. `submit(attempt.key, attempt.payload)` sends the request.
3. On timeout, persist `Unknown(attempt.id)` and query `status(attempt.id)` through the supported backend API.
4. Retry the POST only under the same-key, same-payload, valid-retention contract. Otherwise escalate for reconciliation.

## Trade-offs and decision criteria

Status inquiry adds an API and pending UI but gives a basis for decisions. Same-key retry helps only when the server enforces and documents deduplication. Local state can survive process death but cannot settle the payment by itself.

## Failure modes

A new key for the same purchase can create a second charge. An expired key might be treated as new. The same key with a changed payload may be rejected or have provider-specific behavior. Calling a local timeout a definite failure encourages another payment attempt.

## Production perspective

Use a backend-owned payment attempt and an explicit status or reconciliation endpoint. The Android client persists the reference, shows unresolved outcomes honestly, and resumes inquiry after process death. Support tooling must expose stuck or conflicting attempts without storing sensitive card data in logs.

## Interview answer — short

A timeout on the phone is an unknown payment outcome, not proof of failure. The server may have processed the request and lost the response. I persist one attempt identity before sending, then ask the backend for that attempt’s status. If a retry is allowed, I use the same idempotency key and payload within the provider’s documented window; I do not start a new charge blindly.

## Interview answer — structured

If the request reached the server and the phone timed out, I cannot infer whether the charge happened. The first protection is one stable payment attempt for the order. I persist its identity before the network call and send the idempotency key that the backend contract expects.

After timeout I show an unknown or pending result and prevent a fresh charge for the same purchase. I query the original attempt through the backend’s status path. A confirmed success or decline can update the UI; an in-progress or unreachable result remains unresolved with follow-up. A POST retry uses the same key and unchanged payload only if the backend supports it within its retention period.

The key is not magic. The backend must actually deduplicate the financial effect, and I need to know what happens when the key expires or a payload changes. For a stuck case I reconcile or escalate rather than announcing a failure I cannot prove.

## Interview answer — deep senior

The failure window is between submission and observing the result. `withTimeout` may cancel the local coroutine, and an HTTP timeout may stop waiting for the response, but neither proves the remote server did nothing. The operation identity therefore has to outlive a coroutine or ViewModel instance. I persist it with the order before sending and use the identifiers required by the backend.

The backend idempotency contract is what prevents a repeated logical charge. I need its key scope, retention period, payload matching rule, response replay behavior, and status lookup path. Some APIs replay the first response for a key, including an error; that does not by itself prove the eventual financial state. A status endpoint may need a payment ID or merchant reference rather than the idempotency key. I do not invent a universal `GET /charges/{key}` route.

On timeout I keep the attempt Unknown and block a new attempt for the same purchase. I query the authoritative system, update only from confirmed results, and retain unresolved work for later inquiry or operational review. If the contract permits same-key POST retry, I use the identical payload within its validity window. Idempotency aims to deduplicate the financial effect under a defined contract; it does not mean exactly one network request was executed.

On Android, local persistence and a scheduled worker can resume inquiry after process death, but they cannot guarantee an immediate answer or enforce provider behavior. I would test the lost-response case by letting the backend accept the charge and then dropping the response. The assertion belongs on the backend operation count and the client’s honest pending state, not merely on the caught timeout.

## How to answer in the interview

Lead with timeout means unknown. Explain persistent operation identity, the backend idempotency contract, status inquiry, and safe retry conditions before discussing coroutine internals.

## Deep-dive talking points

Key retention, same-payload rule, status lookup identifiers, process death after send, backend deduplication versus exactly-once execution, lost-response testing.

## Follow-up questions

- **Interviewer:** "What if there is no idempotency API?" **Answer:** "I need a backend-owned attempt and a way to query or reconcile it before treating retry as safe."
- **Interviewer:** "Does `withTimeout` cancel the charge?" **Answer:** "It cancels local waiting; the remote side may still complete."

## Self-check rubric

Can I distinguish local timeout from remote result, name the backend contract, and explain the unresolved UI state?

## References and reviewed-on date

- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests).
- [Kotlin withTimeout](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-timeout.html).
- [Adyen verify transaction status](https://docs.adyen.com/point-of-sale/basic-tapi-integration/verify-transaction-status/).

Provider contracts differ. Technically reviewed against primary documentation on 2026-10-18.
