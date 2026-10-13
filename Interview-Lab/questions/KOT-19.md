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

JVM illustration of a domain result with explicit failure categories. The `fetch` lambda stands for an I/O adapter; this code preserves coroutine cancellation before mapping an ordinary I/O error.
```kotlin
import java.io.IOException
import java.util.concurrent.CancellationException

sealed interface LoadUser {
    data class Found(val name: String) : LoadUser
    data object Missing : LoadUser
    data class Unavailable(val retryable: Boolean) : LoadUser
}
 suspend fun load(fetch: suspend () -> String?): LoadUser = try {
    fetch()?.let(LoadUser::Found) ?: LoadUser.Missing
} catch (cancelled: CancellationException) {
    throw cancelled
} catch (io: IOException) {
    LoadUser.Unavailable(retryable = true)
}
fun display(result: LoadUser): String = when (result) {
    is LoadUser.Found -> result.name
    LoadUser.Missing -> "No account"
    is LoadUser.Unavailable -> "Try again"
}
```

## Practical walkthrough

`Result<T>` مناسب عند adapter صغير بيرجع success أو `Throwable` وعايز تحتفظ بالcause. لكنه مش domain vocabulary: UI محتاجة تعرف هل `Missing`، `Unauthorized`، أو `Unavailable(retryable)` عشان تاخد قرار. map exceptions في boundary: HTTP 404 → Missing مثلًا فقط لو endpoint contract يقول كده، timeout → حالة uncertain أو retriable حسب operation. لا تستخدم `runCatching` حوالين suspend call من غير ما تعيد رمي `CancellationException`، وإلا تلغي cancellation وتحوّلها failure عادية. خليك واضح هل failure exception داخلي ولا expected business outcome.

## Trade-offs and decision criteria

`Result<T>` is concise for generic exception-bearing boundaries and transformations. A sealed outcome is more verbose but communicates recovery and observability. Avoid exposing raw infrastructure exceptions as a stable public domain API. Keep unexpected programmer defects visible rather than mapping everything to “network error.”

## Failure modes

A suspend repository wraps its body in `runCatching` and returns `Result.failure(CancellationException)`; the caller treats cancellation as a retryable UI error. Re-throw cancellation before domain mapping. Another mistake is reducing all HTTP failures to `null`, losing actionable status.

## Production perspective

A payments repository maps transport failures to `PaymentError.Network`, `Declined(code)`, or `AuthRequired`, with safe server reason codes. It logs correlation IDs without PII. Cancellation propagates, and the server remains authoritative for transaction status.

## Interview answer — short

`Result<T>` packages success or a `Throwable`, which is useful near an operation boundary. For domain behavior, I often prefer a sealed outcome with named cases and payloads. In suspending code I preserve cancellation rather than turning it into an ordinary failure.

## Interview answer — structured

I choose the result type from the caller’s decisions. A low-level adapter can return `Result<T>` when preserving an exception is useful, but a screen needs stable meanings such as Missing, Unauthorized, and TemporarilyUnavailable. I map transport errors once at the boundary, retain diagnostic causes for logging, and do not expose raw exception classes as the whole product contract. In coroutine code I avoid swallowing `CancellationException`; a broad `runCatching` can accidentally capture it, so I rethrow cancellation before mapping genuine failures. The outcome type should tell the caller whether to retry, ask for credentials, or stop.

## Interview answer — deep senior

I choose the failure type based on who consumes it. At a generic adapter, `Result<T>` can package an exception while preserving the original cause. At a domain boundary, stable sealed errors let UI and tests handle offline, unauthorized, and business rejection separately without parsing messages. I retain diagnostic context in logs and correlation IDs, not raw secrets. Coroutine cancellation is not a business failure; it must propagate through structured concurrency. I also specify whether a retry is safe and distinguish transport uncertainty from a confirmed server outcome.

For a user lookup, I might map a 404 into Missing only if the endpoint contract says it means no user, map a transient I/O failure into Unavailable, and preserve a cause plus correlation ID for diagnosis. A raw exception message should not become user text or a stable error code. In suspending code, a broad `runCatching` catches `CancellationException` too; I rethrow it so closing the screen can cancel the work correctly. For an unsafe write operation, a timeout can mean the server completed the action but the response was lost, so the result model needs an uncertain state and an idempotent recovery path.

## How to answer in the interview

- **Why:** Model operations that can succeed or fail as values rather than throwing unchecked exceptions.
- **How:** Use Kotlin's `Result<T>` or custom sealed domain hierarchies (`Outcome.Success`, `Outcome.Failure`).
- **Trade-offs:** `Result<T>` wraps exceptions as `Throwable`, which lumps programming bugs, network timeouts, and cancellation together.
- **Failure cases:** Catching `CancellationException` inside `runCatching` and boxing it into `Result.failure`, breaking coroutine cancellation in Android view models.
- **Production solution:** Build custom sealed error hierarchies (`NetworkError`, `ValidationError`, `AuthError`) for expected domain failures, letting unexpected exceptions crash or propagate.

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

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets; no Android device claim is made.
