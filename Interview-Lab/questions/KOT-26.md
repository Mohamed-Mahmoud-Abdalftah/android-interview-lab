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

## Trade-offs and decision criteria

Sealed cases are more verbose and adding a case affects exhaustive clients. That is useful within a controlled app; a public extensible API may need an interface. Enum remains best for simple fixed choices such as payment method display category. Persisted wire values need explicit mapping, not implicit class names.

## Failure modes

A timeout is mapped straight to `Failed`, but the payment may have succeeded server-side. Represent `PendingVerification` or query authoritative status before allowing retry. Idempotency keys reduce duplicate effects but do not prove exactly-once network execution.

## Production perspective

Checkout ViewModel renders sealed local states while repository persists request ID and queries server after uncertain outcomes. It restores state after process death, logs correlation IDs without card data, and tests retry/reconciliation paths.

## Interview answer — short

A sealed hierarchy is better when each state has different required data, such as a receipt for success and a reason for failure. An enum is simpler for uniform constants. For payments I also separate UI state from server-authoritative transaction status.

## Interview answer — structured

Enums model a fixed list of constants well. Sealed types let each case carry its own payload, so a success without receipt or failure without reason is harder to construct. Exhaustive `when` branches help when the state machine evolves. In a payment flow, I would add an uncertain or pending-verification state for timeouts and reconcile with the server rather than treating the client enum or sealed object as authoritative. For UI or payment state, I first list what data each case requires. `Succeeded` needs a receipt, `Failed` needs a reason, and a timeout may need a request ID for verification. A sealed hierarchy packages those fields with the corresponding case and lets `when` handling be exhaustive. An enum remains a good choice for simple uniform choices such as sort order or an unadorned display category.

## Interview answer — deep senior

I would start by listing legal states and transitions. If cases need different fields, sealed types encode those invariants, and exhaustiveness makes UI rendering and tests more robust. But a closed class hierarchy does not solve distributed uncertainty: a request can time out after server success. The client persists an idempotency/request key and checks server status, including after process death. Serialization uses stable explicit codes, and sensitive payment decisions remain server-side. If the domain truly has simple uniform constants, an enum avoids unnecessary hierarchy. The real design gain is eliminating invalid combinations. A single enum plus optional receipt and error fields permits a state that says success with no receipt or failure with a success payload. Sealed cases give each outcome its own constructor and help the compiler point out unhandled additions. For a public API I would think about how adding a new case affects clients and use stable wire codes for persistence. In payments, I also separate client presentation state from the authoritative transaction record. Idempotency helps prevent duplicate effects under server rules, but it does not mean the network request executed exactly once.

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

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
