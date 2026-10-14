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

التعامل مع الأخطاء والـ Failures في Kotlin من أهم مواضيع الـ Clean Architecture:

1. إيه هو `kotlin.Result<T>`؟
   - هو Discriminated Union بيعبر عن إما نجاح (`Result.success(value)`) أو فشل استثنائي (`Result.failure(throwable)`).
   - هو `@JvmInline value class`، يعني لو تم استخدامه كـ Return type مباشر، المترجم بيحاول يعمل inline للقيمة لتجنب الـ Heap Allocation.
   - **المشكلة الكبرى في `kotlin.Result`:** الفشل محصور دائماً في `java.lang.Throwable`! ده معناه إنه بيعامل أخطاء الـ Domain العادية (زي رصيد غير كاف، كلمة سر غير صحيحة، أو منتج غير متوفر) كأنها Exceptions، وإنشاء Throwable بيكلف جمع الـ StackTrace المكلف جداً في الـ CPU.

2. ليه نمذجة أخطاء الـ Domain بـ Sealed Hierarchy أفضل بكثير؟
   - في الـ Business Logic، الفشل مش 'حادث استثنائي'؛ الفشل هو نتيجة متوقعة وشرعية من قواعد العمل (Expected Business Outcome).
   - باستخدام `sealed interface DomainResult<out T, out E>`:
     * بنفصل النجاح والخطأ بدقة Type-safe.
     * أخطاء الـ Domain (زي `InsufficientFunds`, `UserBlocked`) بتكون كائنات عادية بدون StackTrace وبدون Overhead.
     * الـ Compiler بالـ `when` expression بيجبر المطور يعالج كل حالات الخطأ بدون نسيان (Exhaustive Handling).

## Practical walkthrough

في نظام الدفع والشراء في تطبيق Android:
- المستخدم بيضغط 'تأكيد الدفع' بمبلغ 100 دولار.
- **النهج السيئ باستخدام Exceptions و Result:**
  `fun pay(): Result<Receipt> = try { ... } catch(e: InsufficientFundsException) { Result.failure(e) }`
  كل مرة رصيد المستخدم لا يكفي، بننشئ Exception ونجمع الـ Stack Trace كامل من الـ OS! ده بطيء ومسيء لنمذجة منطق العمل.
- **النهج الاحترافي باستخدام Domain Sealed Result:**
  sealed interface PaymentResult {
      data class Success(val receipt: Receipt) : PaymentResult
      sealed interface Failure : PaymentResult {
          data class InsufficientFunds(val balance: BigDecimal, val required: BigDecimal) : Failure
          data object NetworkTimeout : Failure
          data class CardExpired(val expiryDate: String) : Failure
      }
  }
- في الـ ViewModel:
  `when (result) { is Success -> navigate(); is InsufficientFunds -> showTopUpDialog(); ... }`
  الـ IDE والـ Compiler يضمنان معالجة كل حالة بنسبة 100% بدون أي Runtime Crash.

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

## Trade-offs and decision criteria

`Result<T>` is concise for generic exception-bearing boundaries and transformations. A sealed outcome is more verbose but communicates recovery and observability. Avoid exposing raw infrastructure exceptions as a stable public domain API. Keep unexpected programmer defects visible rather than mapping everything to “network error.”

## Failure modes

A suspend repository wraps its body in `runCatching` and returns `Result.failure(CancellationException)`; the caller treats cancellation as a retryable UI error. Re-throw cancellation before domain mapping. Another mistake is reducing all HTTP failures to `null`, losing actionable status.

## Production perspective

A payments repository maps transport failures to `PaymentError.Network`, `Declined(code)`, or `AuthRequired`, with safe server reason codes. It logs correlation IDs without PII. Cancellation propagates, and the server remains authoritative for transaction status.

## Interview answer — short

Kotlin's built-in Result models either a value or a Throwable as an inline value class. For domain logic, modeling errors with a custom sealed hierarchy or an Either type is much better because domain failures are expected business outcomes, not exceptions; sealed classes avoid costly stack-trace generation and enable exhaustive compiler-checked handling.

## Interview answer — structured

Kotlin's standard Result<T> is designed primarily for encapsulating the outcome of operations that might throw exceptions, capturing either a successful value or a Throwable. Because it is implemented as an inline value class, it avoids heap allocations when used directly.

However, using Result for domain errors has a fundamental flaw: its failure branch is hardcoded to Throwable. In clean domain architecture, business failures—such as InsufficientFunds or InvalidCredentials—are not unexpected runtime exceptions; they are legitimate, expected outcomes of domain rules. Creating a Throwable forces the JVM to capture an entire stack trace, which is expensive in terms of CPU and memory.

Instead, I model domain outcomes using a custom sealed interface—like `sealed interface DataResult<out T, out E>`—or dedicated state hierarchies. This gives compile-time exhaustive type checking via when expressions, attaches strongly typed metadata to failures, and avoids the performance penalty of exception allocation.


## Interview answer — deep senior

When designing domain layers in production Android apps, the choice between Kotlin Result, Arrow's Either, and custom sealed hierarchies directly impacts code clarity and diagnostic capabilities. Until Kotlin 1.5, kotlin.Result could not even be returned from functions without compiler flags because of inline class ABI considerations. Even today, it suffers from ergonomic limitations: you cannot customize the failure type, and functions like `mapCatching` swallow all Throwables, including `CancellationException`, which breaks Coroutine cancellation hierarchies if not carefully handled.

With a custom sealed hierarchy like `sealed interface AppResult<out T, out E>`: 1. Domain errors can carry rich context (e.g., `data class NetworkError(val httpCode: Int, val retryAfterSeconds: Int)`). 2. When consuming the result in a ViewModel or MVI reducer, the Kotlin compiler enforces exhaustiveness on the `E` domain error sealed branch without needing an `else` branch, eliminating runtime unhandled edge cases. 3. Stack traces are never collected for expected business validation failures, reducing GC churn in high-frequency operations.


## How to answer in the interview

- **Why:** Model operations that can succeed or fail as values rather than throwing unchecked exceptions.
- **How:** Use Kotlin's `Result<T>` or custom sealed domain hierarchies (`Outcome.Success`, `Outcome.Failure`).
- **Trade-offs:** `Result<T>` wraps exceptions as `Throwable`, which lumps programming bugs, network timeouts, and cancellation together.
- **Failure cases:** Catching `CancellationException` inside `runCatching` and boxing it into `Result.failure`, breaking coroutine cancellation in Android view models.
- **Production solution:** Build custom sealed error hierarchies (`NetworkError`, `ValidationError`, `AuthError`) for expected domain failures, letting unexpected exceptions crash or propagate.

## Deep-dive talking points

Discuss `runCatching` behavior, exception cause retention, cancellation, typed error evolution and idempotent retries.

## Follow-up questions

- **Interviewer:** "Why is catching Throwable or using `runCatching` dangerous with Kotlin Coroutines?"
  **Answer:** "`runCatching` catches all `Throwable` instances, which includes `CancellationException`. If a Coroutine is cancelled and runs code inside `runCatching`, the cancellation exception is swallowed and converted into a `Result.failure`, breaking structured concurrency and preventing the coroutine from canceling properly. You must always rethrow `CancellationException`."

- **Interviewer:** "When would you actually recommend using `kotlin.Result`?"
  **Answer:** "It is well-suited for low-level infrastructure boundaries, such as wrapping raw HTTP client calls, database drivers, or legacy Java SDKs where exceptions are the native error mechanism. At that boundary, you can catch the Throwable, and then map it into your typed domain sealed error hierarchy before passing it up to use cases."

- **Interviewer:** "Does `kotlin.Result` allocate memory on the heap?"
  **Answer:** "When returned directly from a function, it is compiled as an inline value class and unboxed, avoiding allocation. However, if you store it in a generic collection like `List<Result<T>>` or cast it to Any, it is boxed into a heap object."

## Self-check rubric

Explain Result payloads, choose typed error cases for a domain API, and identify the cancellation trap.

## References and reviewed-on date

- [Kotlin Result API](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/-result/) — success/failure operations.
- [Kotlin cancellation and timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html) — cancellation propagation.

Technically reviewed against primary documentation on 2026-10-13.
