---
id: "KOT-26"
question: "When would a sealed hierarchy be better than an enum for UI or payment states?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "C"
phase: 1
priority: "P1"
order: 26
editorial_status: "reviewed"
---

# KOT-26

## Original interview question

When would a sealed hierarchy be better than an enum for UI or payment states?

## What the interviewer evaluates

Model payload-bearing state and transitions, distinguish UI display from server-side payment authority.

## Explanation in Arabic

`enum PaymentState { PROCESSING, SUCCESS, FAILURE }` بسيط، بس لو `SUCCESS` لازم receipt و`FAILURE` لازم reason، هتضطر تحط nullable fields جنب enum وده يسمح بحالات غير منطقية. sealed hierarchy تخلي كل حالة شايلة بياناتها المطلوبة: `Processing(requestId)`, `Succeeded(receipt)`, `Failed(code)`. `when` exhaustive يلفت النظر لما تزود حالة. لكن لو الحالات مجرد constants ثابتة بلا payload، enum أبسط. وفي المدفوعات الـUI state مش مصدر الحقيقة؛ حالة السيرفر والـwebhook/reconciliation هي المرجع بعد timeouts أو process death.

## Why it matters and how it works

A closed payload-bearing hierarchy makes invalid combinations harder to represent and forces handling new cases. It also clarifies transition semantics, but persistence and network uncertainty need separate design.

## Worked example

JVM illustration of distinct case payloads.
```kotlin
sealed interface CheckoutState {
    data object Idle : CheckoutState
    data class Processing(val requestId: String) : CheckoutState
    data class Succeeded(val receiptId: String) : CheckoutState
    data class Failed(val code: String) : CheckoutState
}
fun terminal(s: CheckoutState) = when (s) {
    CheckoutState.Idle, is CheckoutState.Processing -> false
    is CheckoutState.Succeeded, is CheckoutState.Failed -> true
}
```

## Practical walkthrough

في checkout، `Processing(requestId)` و`Succeeded(receiptId)` عندهم data مختلفة، و`Failed(code, retryable)` فيها قرار UI. sealed hierarchy بتخلي payload مطلوب في الحالة الصح بدل enum واحد فيه nullable fields كتير ممكن تنتج `Succeeded(receiptId=null)`. لكن sealed type ما تمنعش transition غلط من `Succeeded` لـ`Processing`؛ reducer أو state machine وtests لازم يحددوا legal transitions. مهم كمان timeout في دفع: `PendingVerification` أحسن من `Failed` لو server outcome مجهول؛ ما تعيدش الخصم عشوائيًا. enum تفضل مناسبة لثوابت مستقلة من payload زي payment method category.

## Trade-offs and decision criteria

Sealed cases are more verbose and adding a case affects exhaustive clients. That is useful within a controlled app; a public extensible API may need an interface. Enum remains best for simple fixed choices such as payment method display category. Persisted wire values need explicit mapping, not implicit class names.

## Failure modes

A timeout is mapped straight to `Failed`, but the payment may have succeeded server-side. Represent `PendingVerification` or query authoritative status before allowing retry. Idempotency keys reduce duplicate effects but do not prove exactly-once network execution.

## Production perspective

Checkout ViewModel renders sealed local states while repository persists request ID and queries server after uncertain outcomes. It restores state after process death, logs correlation IDs without card data, and tests retry/reconciliation paths.

## Interview answer — short

A sealed hierarchy is better when states carry different required data, such as a receipt only on success. An enum is simpler for fixed constants without per-instance payloads. I still validate legal transitions separately; exhaustiveness does not make the state machine correct.

## Interview answer — structured

I choose the representation from the shape of the state. For a payment flow, Processing needs a request ID, Succeeded needs a receipt, and an uncertain timeout may need PendingVerification. A sealed hierarchy makes those payloads specific to each case and lets a `when` renderer be exhaustive. An enum with several nullable fields admits impossible combinations such as success without a receipt. I would still implement transition rules in a reducer or coordinator, because a sealed type only limits shapes, not history. For a fixed choice with no distinct payload, an enum is smaller and clearer. In production, uncertain network outcomes must be reconciled using server idempotency rather than treated as definite failure.

## Interview answer — deep senior

I would start by listing legal states and transitions. If cases need different fields, sealed types encode those invariants, and exhaustiveness makes UI rendering and tests more robust. But a closed class hierarchy does not solve distributed uncertainty: a request can time out after server success. The client persists an idempotency/request key and checks server status, including after process death. Serialization uses stable explicit codes, and sensitive payment decisions remain server-side. If the domain truly has simple uniform constants, an enum avoids unnecessary hierarchy.

For checkout UI, I would define Processing with an attempt ID, Succeeded with a receipt ID, Rejected with a code, and PendingVerification when a response is lost. That avoids an enum plus several nullable fields which can represent success without a receipt. Still, the sealed type only constrains shapes; a reducer must prevent illegal transitions, and the server is authoritative for the payment outcome. I would persist the attempt ID before submission and reconcile after process death, using the same server idempotency key for any allowed retry. If cases carry no distinct data, an enum is less ceremony.

## How to answer in the interview

- **Why:** Enforce type-safe state modeling with distinct data payloads for complex domain and payment workflows.
- **How:** Use sealed classes where states have distinct parameters (e.g., `PaymentState.Success(txId)`, `PaymentState.Failed(code, retryable)`).
- **Trade-offs:** Sealed hierarchies cannot be iterated over like enum values (`values()`), and adding new subtypes requires handling across all `when` expressions.
- **Failure cases:** Using an enum with nullable fields for state payloads, allowing invalid states (e.g., `PaymentState.SUCCESS` paired with an error message) to exist at runtime.
- **Production solution:** Model UI and checkout flows using sealed classes to make invalid states unrepresentable, combining exhaustive `when` matching with targeted UI rendering.

## Deep-dive talking points

Discuss case-specific payloads, exhaustive rendering, transition tests, process death, idempotency and server reconciliation.

## Follow-up questions

- [KOT-06](../kot-06/): How does sealed differ from enum? **Answer:** sealed cases can be distinct subclasses with different payloads.
- [PAY-02](../pay-02/): What does idempotency guarantee? **Answer:** duplicate requests can map to one effect if server rules support it; it does not ensure one network execution.

## Self-check rubric

Model success/failure payloads, justify enum alternative, and explain timeout uncertainty in a payment flow.

## References and reviewed-on date

- [Kotlin sealed classes and interfaces](https://kotlinlang.org/docs/sealed-classes.html) — closed cases and exhaustive `when`.
- [Android app architecture](https://developer.android.com/topic/architecture) — separation of UI and data sources.

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
