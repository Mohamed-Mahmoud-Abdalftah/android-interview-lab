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

تصميم Type-Safe Result API بدون فقدان تفاصيل الخطأ (Without losing error context) هو الفارق بين كود مبتدئ وكود معماري ناضج:

1. المشاكل في الـ APIs التقليدية للنتائج:
   - **`kotlin.Result<T>`:** بيحصر الخطأ في `Throwable` فقط؛ فبتفقد الـ Type-Safety لأخطاء الـ Domain، ومضطر تعمل Type Cast للـ Throwable.
   - **الـ Nullable Returns (`User?`):** لو الدالة رجعت `null`، المتصل ميعرفش السبب: هل المستخدم غير موجود؟ ولا السيرفر واقع؟ ولا التوكن انتهى؟ تفقد كل سياق الخطأ تماماً.
   - **الـ Generic Error Code (`Int` أو `String`):** استخدام أكواد رقمية زي `404` أو strings زي `"USER_NOT_FOUND"` يفتقر للـ Type Safety وعرضة للأخطاء الإملائية.

2. أفضل نمط معماري (The Senior Pattern):
   - استخدام `sealed interface Result<out T, out E>`:
     * المتغير `T` يمثل البيانات الناجحة (Success Data).
     * المتغير `E` يمثل الـ Domain Error ويكون هو نفسه Sealed Hierarchy.
   - في حالة الفشل، الـ Error Model يحمل معلومات غنية ومحددة (Structured Metadata)، زي `HttpCode`, `UserMessage`, أو `RetryPolicy`.
   - توفير Extension Functions عملية زي `map`, `flatMap`, `onSuccess`, `onError` لسهولة ربط العمليات بسلاسة (Monadic Chaining).

## Practical walkthrough

في طبقة المصادقة وتسجيل الدخول (Authentication Repository):
- **تصميم الـ Result API:**
  sealed interface AuthResult<out T> {
      data class Success<T>(val data: T) : AuthResult<T>
      sealed interface Error : AuthResult<Nothing> {
          data class InvalidCredentials(val attemptsRemaining: Int) : Error
          data class AccountLocked(val unlockTime: Instant) : Error
          data class Network(val cause: IOException) : Error
      }
  }
- **في الـ ViewModel:**
  when (val result = authRepository.login(username, password)) {
      is AuthResult.Success -> emitNavigation(HomeRoute)
      is AuthResult.Error.InvalidCredentials -> showWarning("Remaining: ${result.attemptsRemaining}")
      is AuthResult.Error.AccountLocked -> showLockedScreen(result.unlockTime)
      is AuthResult.Error.Network -> showRetrySnackbar()
  }
- النتيجة: الـ ViewModel يعرف بالضبط كل تفصيلة خطأ بدون أي Exception وبدون أي Casting.

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

Design a typed sealed hierarchy like Result<out T, out E> where both success and failure are strongly typed. Failures carry structured metadata rather than generic strings or raw Throwables, eliminating casting and allowing the compiler to enforce exhaustive, context-rich error handling.

## Interview answer — structured

To design a type-safe result API without losing error context, I use a parametric sealed hierarchy: `sealed interface NetworkResult<out T, out E>`. The key design principle is treating failures as first-class domain entities rather than second-class exceptions or generic strings.

In this design, `Success<T>` holds the strongly typed response payload. The failure branch is not tied to `java.lang.Throwable`; instead, it is typed to a sealed error hierarchy `E` specific to that feature—such as `AuthError.InvalidCredentials(val attemptsRemaining: Int)` or `AuthError.AccountLocked(val unlockTime: Instant)`. This preserves rich diagnostic context and metadata.

Callers consume the API with exhaustive `when` expressions, giving the compiler the ability to verify that every domain error variant is explicitly handled. We also provide functional transformations like `map`, `mapError`, and `flatMap` so pipelines can chain results cleanly without nested try-catch blocks.

## Interview answer — deep senior

Architecturally, a well-engineered Result type follows Monadic patterns (similar to Arrow's Either<L, R>) while maintaining idiomatic Kotlin ergonomics. To maximize performance and ergonomics in Android: 1. Covariance: use `out T` and `out E` with `Success<out T>` and `Failure<out E> : Result<Nothing, E>`, allowing seamless polymorphism and subtyping. 2. Preserve low-level diagnostics: for network and infrastructure failures, attach the underlying root cause (`val cause: Throwable? = null`) so logging and Crashlytics can report full diagnostic breadcrumbs without exposing Throwables to the domain logic. 3. Inline utility methods: implement combinators like `inline fun <T, E, R> Result<T, E>.map(transform: (T) -> R): Result<R, E>` as inline functions to ensure zero heap allocation overhead during transformation chains.

This pattern completely decouples business error recovery from system crash reporting, providing absolute compile-time safety across multi-module boundaries.

## How to answer in the interview

- **Why:** Communicate operation outcomes with rich, type-safe error context without relying on throwing exceptions.
- **How:** Create a sealed result hierarchy (`Result.Success<T>`, `Result.Failure(error: DomainError)`) where `DomainError` is a sealed class classifying failure causes.
- **Trade-offs:** Typed result hierarchies require callers to explicitly unwrap outcomes, increasing boilerplate compared to unchecked exceptions.
- **Failure cases:** Using a single generic string for error messages, preventing the UI layer from distinguishing retryable network timeouts from fatal authentication failures.
- **Production solution:** Define domain error types with structured metadata (HTTP code, error category, idempotency key), and map low-level exceptions at repository boundaries.

## Deep-dive talking points

Discuss sealed domain errors, cause retention, localization, cancellation, retry classification, idempotency and unknown outcomes.

## Follow-up questions

- **Interviewer:** "Why not just use Kotlin's built-in `Result<T>`?"
  **Answer:** "Because `kotlin.Result<T>` fixes the error type to `Throwable`. In domain logic, business errors are not exceptions. Tying errors to Throwable loses domain type specificity, requires runtime type-casting (`e as CustomException`), and causes performance overhead due to stack-trace capture."

- **Interviewer:** "How do you handle Coroutine cancellation with custom Result types?"
  **Answer:** "When wrapping repository calls, if a `CancellationException` is caught, you must immediately re-throw it instead of wrapping it into your custom Result.failure. Wrapping CancellationException breaks structured concurrency and prevents the coroutine tree from terminating properly."

- **Interviewer:** "How does this pattern benefit unit testing?"
  **Answer:** "It simplifies unit tests immensely. Instead of testing for thrown exceptions with `assertFailsWith` and inspecting exception messages, you assert directly on strongly typed sealed objects (e.g., `assertThat(result).isEqualTo(AuthResult.Error.AccountLocked(expectedTime))`)."

## Self-check rubric

Define three actionable errors, explain where causes live, and handle cancellation plus uncertain timeout.

## References and reviewed-on date

- [Kotlin sealed classes and interfaces](https://kotlinlang.org/docs/sealed-classes.html) — explicit case modeling.
- [Kotlin Result API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/-result/) — generic failure wrapper.

Technically reviewed against primary documentation on 2026-10-13.
