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

## Trade-offs and decision criteria

A sealed hierarchy is verbose but makes business cases explicit. Kotlin `Result<T>` is concise for exception-bearing infrastructure, but `Throwable` alone is a weak public domain contract. Keep a cause internally where safe; expose stable codes and localized UI messages separately.

## Failure modes

A timeout is mapped to `Rejected`, leading the user to retry a payment that may have succeeded. Persist request ID and reconcile with the server. Another mistake is `runCatching` swallowing coroutine cancellation; rethrow it before mapping known exceptions.

## Production perspective

A checkout repository returns typed outcomes, logs a correlation ID without card details, and stores pending request IDs for process-death recovery. Tests cover accepted, rejected, timeout-uncertain, cancellation, duplicate retry, and unknown server errors.

## Interview answer — short

I use a sealed success/error contract with stable categories and enough safe context for recovery. I preserve causes in diagnostics, keep UI text separate, propagate cancellation, and model network uncertainty explicitly.

## Interview answer — structured

A type-safe result API should let callers handle known outcomes without parsing exception messages. I define success and domain error cases with stable codes, retryability, and correlation information where useful. Infrastructure exceptions are mapped at the repository boundary; unknown failures remain observable. For suspend functions I rethrow cancellation. For payment timeouts I represent pending verification and ask the server, because timeout does not prove failure. I begin with decisions callers need to make: show a validation hint, require sign-in, retry safely, or verify an uncertain operation. That yields explicit cases with required fields instead of a Boolean or a null. I keep raw exception details and correlation IDs in protected diagnostics, while the UI receives stable safe codes and localized messages.

## Interview answer — deep senior

I start with consumer decisions: retry, re-authenticate, correct input, wait, or escalate. Those become explicit cases with required payloads. A raw `Throwable` may be retained in internal telemetry, but it should not become the UI contract or leak secrets. I distinguish confirmed server rejection from transport uncertainty and define idempotency and reconciliation with the backend. Cancellation is control flow and must propagate. I version error codes deliberately, test exhaustive mapping, and ensure process-death recovery retains only safe identifiers. A type-safe result API should make the legal outcomes and their payloads visible in the type system. A sealed hierarchy can distinguish accepted, rejected, unavailable, and pending verification, each with the information the caller needs. Kotlin `Result<T>` is useful at an exception-bearing infrastructure boundary, but exposing only a `Throwable` forces domain callers to inspect unstable classes or messages. I map known failures once, retain the original cause for safe logging, and keep user-facing text separate from protocol codes. For a payment request, timeout is not proof of failure; the server may have committed the operation. I preserve a request ID, use server reconciliation and carefully designed idempotent retries, and restore pending work after process death.

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

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets unless explicitly labeled conceptual; no Android device claim is made.
