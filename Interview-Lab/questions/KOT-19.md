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

## Concept and technical explanation

Kotlin's standard `kotlin.Result<T>` is a discriminated union representing either a successful outcome containing a value of type T or a failure containing a Throwable. Implemented as an `@JvmInline value class`, Result avoids heap allocations in unboxed scenarios, making it concise for capturing operations that interact with throwing infrastructure. However, using Result for domain errors has profound architectural deficiencies. Because its failure branch is permanently hardcoded to `java.lang.Throwable`, it forces business rules to treat normal domain outcomes—such as insufficient funds, expired sessions, or validation errors—as exceptions. Allocating a Throwable forces the JVM and ART runtime to capture an entire call stack trace, which consumes substantial CPU cycles and memory. Furthermore, idiomatic domain modeling requires strongly typed, exhaustive error categorization. By modeling domain results using custom closed type hierarchies—such as `sealed interface DomainResult<out T, out E>`—teams achieve compile-time exhaustive checking in `when` expressions, avoid stack trace overhead, and isolate business logic from transport-level exceptions.

## Practical walkthrough (English)

Consider a checkout workflow in a mobile banking application. If an engineer relies on standard exceptions: `fun processPayment(): Result<Receipt> = runCatching { ... }`, multiple architectural issues arise. First, throwing an `InsufficientFundsException` captures a full stack trace even though having a low balance is an expected business condition. Second, `runCatching` catches all Throwables indiscriminately, including `CancellationException`. If a user navigates away and the coroutine is cancelled, `runCatching` intercepts the cancellation, swallows it, and produces a failure result, breaking Kotlin's structured concurrency. The correct architecture uses a typed domain result: `sealed interface PaymentResult { data class Success(val receipt: Receipt) : PaymentResult; sealed interface Failure : PaymentResult { data class InsufficientBalance(val current: Long, val required: Long) : Failure; data object NetworkTimeout : Failure } }`. In the ViewModel, a `when` expression handles every failure case exhaustively without needing an else branch or allocating stack traces.

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

Kotlin's Result models either a value or a Throwable as an inline value class, ideal for capturing throwing infrastructure calls. For domain logic, modeling outcomes with a custom sealed hierarchy is vastly superior because business failures are expected outcomes, not exceptions; sealed classes avoid costly stack trace capture and enable compile-time exhaustive handling.

## Interview answer — structured

Kotlin's standard Result class is designed primarily to encapsulate the outcome of operations that might throw exceptions, capturing either a successful value or a Throwable. Because it is implemented as an inline value class, it avoids heap allocations when returned directly from functions.

However, using Result for domain errors violates clean architecture principles. In business domains, failures such as an invalid coupon code or insufficient funds are expected, legitimate outcomes of business rules, rather than system errors. Forcing these outcomes into a Throwable requires the runtime to capture an entire execution stack trace, which introduces measurable CPU and memory overhead.

In production, `runCatching` presents a severe concurrency danger because it catches `CancellationException`, inadvertently swallowing coroutine cancellation and breaking structured concurrency.

Senior engineers model domain outcomes using custom sealed interfaces, which enable compile-time exhaustive checking in when expressions without exception overhead.


## Interview answer — deep senior

From a runtime and bytecode perspective, `kotlin.Result<T>` relies on advanced compiler synthesis. Declared as an `@JvmInline value class`, it stores either the success value or a synthetic `Result.Failure` wrapper wrapping the Throwable. When returned directly from a Kotlin function, the compiler unboxes the value, returning a raw Object in bytecode to prevent heap allocation. However, boxing immediately occurs if the Result is stored in a collection, cast to Any, or used as a generic type parameter. Furthermore, prior to Kotlin 1.5, `kotlin.Result` was strictly restricted from being returned from public API boundaries due to ABI stability concerns surrounding inline classes. Even today, developers must be extremely cautious when composing Result pipelines; functions like `mapCatching` intercept all throwables without discrimination, creating silent logical bugs where severe runtime errors are treated as routine domain failures. The most insidious danger of `runCatching` in modern asynchronous Android architectures is its interaction with Kotlin Coroutines. The coroutine framework relies on `CancellationException` to propagate cooperative cancellation up the job hierarchy. Because `runCatching` catches `Throwable` without rethrowing `CancellationException`, it converts cooperative cancellation into a failed result, keeping coroutines active and causing memory leaks or delayed screen updates. By implementing a typed domain hierarchy like `sealed interface AppResult<out T, out E>`, we completely decouple business failures from JVM exceptions. Domain errors carry strongly typed contextual payloads (such as validation failure maps or retry delays) without allocating stack traces, and the Kotlin compiler enforces complete exhaustiveness on the `E` error branch in when expressions without requiring an unsafe `else` fallback.

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
