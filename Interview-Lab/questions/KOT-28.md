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

## Concept and technical explanation

Designing a type-safe result API in Kotlin without losing error information requires balancing strong compiler type guarantees with rich diagnostic observability. In naive architectures, result types either discard failure details by reducing errors to generic strings or boolean flags, or couple callers to low-level transport exceptions like `IOException` or `SQLException`. A production-grade result API addresses this through a strongly typed, payload-bearing closed hierarchy—such as `sealed interface AppResult<out T, out E : DomainError>`. The error type `E` is itself a sealed hierarchy representing distinct, mutually exclusive business failure categories (such as `ValidationError`, `NetworkError`, `AuthenticationError`, or `PaymentDeclined`). Each failure case carries domain-specific metadata (such as HTTP response codes, failed form field maps, or retry eligibility), while retaining an optional root cause exception for telemetry. This ensures presentation layers handle failures exhaustively in `when` expressions without type casting or string parsing, while diagnostic pipelines capture full root causes without leaking internal stack traces to users.

## Practical walkthrough (English)

Consider a checkout transaction API in an enterprise Android application. A flawed API returns `Result<Receipt>`, forcing the UI layer to inspect untyped exceptions: `if (result.exceptionOrNull() is InsufficientFundsException) ...`, which breaks encapsulation and causes runtime bugs if an exception type changes. A disciplined result API structures the outcome cleanly: `sealed interface CheckoutResult { data class Success(val receipt: Receipt) : CheckoutResult; sealed interface Failure : CheckoutResult { data class InsufficientBalance(val balance: Long, val required: Long) : Failure; data class CardDeclined(val declineCode: String, val canRetry: Boolean) : Failure; data class NetworkTimeout(val cause: Throwable, val correlationId: String) : Failure } }`. In the ViewModel, a `when` expression pattern-matches on `CheckoutResult`. If `InsufficientBalance` occurs, the UI displays a specialized top-up sheet showing exact currency amounts. If `NetworkTimeout` occurs, the UI presents a retry banner while forwarding the `correlationId` and `cause` to Crashlytics, completely separating user messaging from technical diagnostics.

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

A type-safe result API models outcomes with a sealed hierarchy carrying strongly typed domain error categories rather than generic strings or raw exceptions. This preserves rich diagnostic metadata and correlation IDs for observability while enabling exhaustive, compiler-checked error handling in presentation layers.

## Interview answer — structured

Designing a type-safe result API requires preserving structural failure details without tightly coupling the domain layer to low-level transport exceptions. Standard solutions that reduce errors to strings or generic Throwables force presentation code to rely on fragile string parsing or unsafe type casting.

The optimal design employs a closed type hierarchy where the failure branch is constrained to a domain-specific sealed error taxonomy.

In production, each failure variant carries typed domain properties—such as HTTP status codes, validation maps, or retry eligibility flags—while encapsulating a correlation identifier for diagnostic logging.

This design allows UI layers and MVI reducers to handle errors exhaustively in when expressions with full compiler enforcement, while production telemetry pipelines capture technical root causes without exposing stack traces to end users.


## Interview answer — deep senior

From an architectural and functional perspective, a robust result API incorporates monadic transformation combinators—such as `map`, `flatMap`, `recover`, and `fold`—while maintaining Kotlin's idiomatic readability. Unlike raw functional programming libraries like Arrow, which introduce heavy monadic abstractions and learning curves, a pragmatic Kotlin result API implements lightweight inline extension functions. These combinators transform successful values while propagating strongly typed errors downstream without nesting callback pyramids. Regarding coroutines and structured concurrency, the result API must never intercept or swallow `CancellationException`. When mapping low-level network or database calls inside boundary adapters, engineers must explicitly catch `CancellationException` and rethrow it immediately, ensuring that parent job cancellations propagate properly across scopes. From an observability and security standpoint, enterprise mobile applications must adhere to strict data classification policies. Technical error payloads often contain Personally Identifiable Information (PII) or sensitive banking tokens within network response bodies or stack traces. A well-architected result API decouples the user-facing domain model (which contains localized, sanitized error descriptions) from the internal diagnostic event (which pairs a non-PII Correlation ID with sanitized error codes sent to remote telemetry backends like Datadog or Firebase). This architecture guarantees that even if a full stack trace is logged in internal crash reporting, no sensitive customer data is leaked in presentation layers or logcat outputs.

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
