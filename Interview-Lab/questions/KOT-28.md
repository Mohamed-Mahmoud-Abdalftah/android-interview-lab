---
id: "KOT-28"
question: "How do you design a type-safe result API without losing error information?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "C"
phase: 1
priority: "P1"
order: 28
editorial_status: "reviewed"
---

# KOT-28

## Original interview question

How do you design a type-safe result API without losing error information?

## What the interviewer evaluates

Design an outcome API with stable typed categories, retained diagnostic context, cancellation and retry semantics.

## Explanation in Arabic

Type-safe result API لازم تفرق بين `Success(value)` وفشل معروف بحالات محددة، وتحتفظ بمعلومات تكفي للتصرف: validation field، auth state، retryability، request/correlation ID. ما تحوّلش كل errors لـ`Boolean` أو `null`؛ ده بيمسح سبب الفشل. برضه ما تعرضش raw server message أو Throwable للـUI لأنه ممكن يسرّب بيانات أو يكون غير مستقر. في suspend code، `CancellationException` لازم تعدّي، مش تتحول `Failure`. والـnetwork timeout معناه outcome مجهول أحيانًا، خصوصًا payment، فصمّم `PendingVerification` بدل افتراض فشل نهائي.

## Why it matters and how it works

Typed errors make caller decisions exhaustive and testable while preserving enough context for recovery and observability. Stable domain categories should not depend on exception class names or user-facing text.

## Worked example

JVM domain model with explicit uncertainty and safe code; transport exceptions are mapped at a separate boundary.
```kotlin
sealed interface SubmitResult {
    data class Accepted(val receiptId: String) : SubmitResult
    data class Rejected(val code: String) : SubmitResult
    data class PendingVerification(val requestId: String) : SubmitResult
}
fun message(r: SubmitResult) = when (r) {
    is SubmitResult.Accepted -> "Accepted"
    is SubmitResult.Rejected -> "Rejected: ${r.code}"
    is SubmitResult.PendingVerification -> "Checking status"
}
```

## Practical walkthrough

ابدأ بقرارات caller: `Accepted(receiptId)` تفتح receipt، `Rejected(code)` تعرض تصحيح واضح، و`PendingVerification(requestId)` تمنع retry عشوائي. sealed result بيخلي required payload في كل case. Error من network مش دايمًا business rejection؛ timeout ممكن يكون الطلب اتنفذ والسيرفر ردّه ضاع. عند boundary، احتفظ بـcause للـlogs مع correlation ID من غير تسريب secrets، وmap status codes حسب API contract. لو عملية غير idempotent، استخدم client request ID ثابت وserver idempotency + query/reconciliation قبل retry. في coroutine لا تحوّل cancellation لحالة domain failure.

## Trade-offs and decision criteria

A sealed hierarchy is verbose but makes business cases explicit. Kotlin `Result<T>` is concise for exception-bearing infrastructure, but `Throwable` alone is a weak public domain contract. Keep a cause internally where safe; expose stable codes and localized UI messages separately.

## Failure modes

A timeout is mapped to `Rejected`, leading the user to retry a payment that may have succeeded. Persist request ID and reconcile with the server. Another mistake is `runCatching` swallowing coroutine cancellation; rethrow it before mapping known exceptions.

## Production perspective

A checkout repository returns typed outcomes, logs a correlation ID without card details, and stores pending request IDs for process-death recovery. Tests cover accepted, rejected, timeout-uncertain, cancellation, duplicate retry, and unknown server errors.

## Interview answer — short

I model outcomes around caller actions, with named cases and required data. For a payment-like submission I distinguish accepted, rejected, and unknown pending verification. I preserve diagnostic causes internally, respect cancellation, and reconcile uncertain network outcomes with a server idempotency key.

## Interview answer — structured

A type-safe result API should make impossible combinations difficult to construct and retain enough context for a useful decision. I start with consumer actions: show a receipt, ask for correction, or wait for verification. Those become sealed cases with required payloads rather than one object full of nullable fields. I map transport exceptions at the boundary and keep the original cause and correlation ID for diagnostics, while exposing stable domain reasons to the UI. A timeout is not proof of rejection; for a submission I use a stable request ID, server-side idempotency, and reconciliation before retry. Cancellation remains cancellation rather than a user-facing failure case.

## Interview answer — deep senior

I start with consumer decisions: retry, re-authenticate, correct input, wait, or escalate. Those become explicit cases with required payloads. A raw `Throwable` may be retained in internal telemetry, but it should not become the UI contract or leak secrets. I distinguish confirmed server rejection from transport uncertainty and define idempotency and reconciliation with the backend. Cancellation is control flow and must propagate. I version error codes deliberately, test exhaustive mapping, and ensure process-death recovery retains only safe identifiers.

Imagine a submit endpoint returning Accepted with a receipt, Rejected with a stable reason, or PendingVerification after a timeout. These cases guide different caller actions; a `Boolean` or nullable receipt cannot express the uncertainty safely. I would map transport failures at the repository boundary, retain the cause and request ID for internal telemetry, and expose only safe domain fields to UI. For retry, the client must reuse the same request identity under a documented server idempotency contract, then query status after process death. I test exhaustive handling and never convert coroutine cancellation into a domain rejection.

## How to answer in the interview

- **Why:** Communicate operation outcomes with rich, type-safe error context without relying on throwing exceptions.
- **How:** Create a sealed result hierarchy (`Result.Success<T>`, `Result.Failure(error: DomainError)`) where `DomainError` is a sealed class classifying failure causes.
- **Trade-offs:** Typed result hierarchies require callers to explicitly unwrap outcomes, increasing boilerplate compared to unchecked exceptions.
- **Failure cases:** Using a single generic string for error messages, preventing the UI layer from distinguishing retryable network timeouts from fatal authentication failures.
- **Production solution:** Define domain error types with structured metadata (HTTP code, error category, idempotency key), and map low-level exceptions at repository boundaries.

## Deep-dive talking points

Discuss sealed domain errors, cause retention, localization, cancellation, retry classification, idempotency and unknown outcomes.

## Follow-up questions

- [KOT-19](../kot-19/): Where is Kotlin Result useful? **Answer:** a generic exception boundary, before mapping into domain-specific cases.
- [KOT-26](../kot-26/): Why a sealed state for payment? **Answer:** each outcome has required data and exhaustive handling.

## Self-check rubric

Define three actionable errors, explain where causes live, and handle cancellation plus uncertain timeout.

## References and reviewed-on date

- [Kotlin sealed classes and interfaces](https://kotlinlang.org/docs/sealed-classes.html) — explicit case modeling.
- [Kotlin Result API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/-result/) — generic failure wrapper.

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
