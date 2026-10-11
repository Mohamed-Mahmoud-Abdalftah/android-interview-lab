---
id: "KOT-19"
question: "What is Kotlin Result? How would you model domain errors instead?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "B"
phase: 1
priority: "P1"
order: 19
editorial_status: "reviewed"
---

# KOT-19

## Original interview question

What is Kotlin Result? How would you model domain errors instead?

## What the interviewer evaluates

Know Result success/failure mechanics, exception payloads, and domain error modeling without swallowing cancellation.

## Explanation in Arabic

`Result<T>` تمثل نجاح بقيمة `T` أو فشل بـ`Throwable`، ومعاها operators زي `map`, `mapCatching`, `fold`, `getOrElse`. مناسبة عند boundary شغال أصلًا بالـexceptions، لكن `Throwable` لوحده مش contract واضح لعميل domain: هل الفشل offline، unauthorized، validation، ولا server؟ domain sealed error type بتخلي الحالات المعلنة قابلة للمعالجة exhaustively، وتحافظ على metadata الآمنة. في coroutines ما تمسكش `CancellationException` وتحولها لفشل عادي؛ cancellation جزء من التحكم في عمر الشغل.

## Why it matters and how it works

A generic success/failure wrapper can make exception handling explicit, but stable business decisions need a typed taxonomy. `runCatching` catches `Throwable`, so coroutine cancellation needs special treatment in suspend code.

## Worked example

JVM illustration of a domain result with explicit failure categories.
```kotlin
sealed interface LoadUser {
    data class Found(val name: String) : LoadUser
    data object Missing : LoadUser
    data class Unavailable(val retryable: Boolean) : LoadUser
}
fun display(result: LoadUser): String = when (result) {
    is LoadUser.Found -> result.name
    LoadUser.Missing -> "No account"
    is LoadUser.Unavailable -> "Try again"
}
```

## Trade-offs and decision criteria

`Result<T>` is concise for generic exception-bearing boundaries and transformations. A sealed outcome is more verbose but communicates recovery and observability. Avoid exposing raw infrastructure exceptions as a stable public domain API. Keep unexpected programmer defects visible rather than mapping everything to “network error.”

## Failure modes

A suspend repository wraps its body in `runCatching` and returns `Result.failure(CancellationException)`; the caller treats cancellation as a retryable UI error. Re-throw cancellation before domain mapping. Another mistake is reducing all HTTP failures to `null`, losing actionable status.

## Production perspective

A payments repository maps transport failures to `PaymentError.Network`, `Declined(code)`, or `AuthRequired`, with safe server reason codes. It logs correlation IDs without PII. Cancellation propagates, and the server remains authoritative for transaction status.

## Interview answer — short

Kotlin `Result<T>` holds a success value or a `Throwable` failure. I use it for generic exception boundaries, but model domain errors with explicit sealed cases when callers need reliable recovery decisions. In coroutines I let cancellation propagate.

## Interview answer — structured

`Result` gives operators for handling success and exception failure, which is convenient at an infrastructure boundary. It is less expressive as a domain contract when product behavior depends on specific categories. I map known failures to a sealed outcome with fields such as retryability or validation reasons, keep unknown failures visible, and avoid leaking sensitive exception messages to UI. `runCatching` can catch cancellation, so a suspend implementation must rethrow `CancellationException`. For a checkout screen, however, callers need stable categories like authentication required, declined, unavailable, or pending verification. A cancelled coroutine should not be reported as a failed payment. For an unknown server failure, I keep a generic but observable fallback rather than pretending it is a known decline. That helps both UI recovery and incident diagnosis.

## Interview answer — deep senior

I choose the failure type based on who consumes it. At a generic adapter, `Result<T>` can package an exception while preserving the original cause. At a domain boundary, stable sealed errors let UI and tests handle offline, unauthorized, and business rejection separately without parsing messages. I retain diagnostic context in logs and correlation IDs, not raw secrets. Coroutine cancellation is not a business failure; it must propagate through structured concurrency. I also specify whether a retry is safe and distinguish transport uncertainty from a confirmed server outcome. The design starts with what the consumer needs to decide. Kotlin `Result` wraps a successful value or a `Throwable` and has useful transformations, but a `Throwable` hierarchy is not usually a stable business contract. A sealed domain result can carry a decline code, retry-after hint, or correlation ID without exposing raw server messages. I pay special attention to `runCatching`: it catches `Throwable`, including `CancellationException`, so suspend code must rethrow cancellation rather than converting it to a UI error. This keeps structured concurrency working and avoids spurious retries. Tests cover each category and verify that logged details omit tokens and personal data. The transport layer may preserve an underlying exception internally while the domain API exposes stable categories. I test that classification against offline, timeout, unauthorized, malformed response, and cancellation cases. Those are distinct paths with different safe retry behavior.

## Deep-dive talking points

Discuss `runCatching` behavior, exception cause retention, cancellation, typed error evolution and idempotent retries.

## Follow-up questions

- [KOT-28](../kot-28/): How do you avoid losing error detail? **Answer:** carry stable category, code, retryability, and safe cause/correlation context.
- [COR-06](../cor-06/): Why rethrow cancellation? **Answer:** it is structured-concurrency control, not a recoverable domain error.

## Self-check rubric

Explain Result payloads, choose typed error cases for a domain API, and identify the cancellation trap.

## References and reviewed-on date

- [Kotlin Result API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/-result/) — success/failure operations.
- [Kotlin cancellation and timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html) — cancellation propagation.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.
