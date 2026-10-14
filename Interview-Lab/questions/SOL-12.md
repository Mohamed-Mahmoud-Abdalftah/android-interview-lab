---
id: "SOL-12"
question: "How does strategy-based payment routing support OCP?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "B"
phase: 2
priority: "P1"
order: 183
editorial_status: "reviewed"
---

# SOL-12

## Original interview question

How does strategy-based payment routing support OCP?

## What the interviewer evaluates

Use provider strategy to isolate variation while stating what remains in shared payment policy.

## Explanation in Arabic

كيف يدعم توجيه المدفوعات القائم على الاستراتيجية (Strategy-Based Payment Routing) مبدأ Open/Closed Principle (OCP)؟

1. المشكلة في معالجة المدفوعات التقليدية:
   - كلما أضاف البنك طريقة دفع جديدة (Credit Card, PayPal, Apple Pay, Klarna, Fawry, Vodafone Cash):
   - في الكود التقليدي، تضطر لتعديل كلاس الـ `PaymentManager` وإضافة شروط جديدة في `when (paymentType)`.
   - هذا ينتهك OCP بشكل صريح ويعرض المدفوعات القائمة لمخاطر الانهيار (Regression Risks)!

2. تطبيق نمط الاستراتيجية (The Strategy Pattern):
   - نقوم بتعريف واجهة عامة موحدة: `interface PaymentStrategy`.
   - كل مزود دفع يصبح كلاس مستقل ينفذ هذه الواجهة (`StripePaymentStrategy`, `ApplePayStrategy`).
   - كلاس `PaymentRouter` يصبح **مغلقاً للتعديل (Closed for Modification)**: لا يمتلك أي كتل `if/else`، بل يستقبل خريطة أو قائمة من الاستراتيجيات (`Map<PaymentType, PaymentStrategy>`) ويختار الاستراتيجية المناسبة في وقت التشغيل.

3. النتيجة:
   - لإضافة طريقة دفع سادسة، نقوم ببساطة بإنشاء ملف كلاس جديد وربطه عبر Dagger/Hilt، دون لمس أو تعديل سطر واحد في كلاسات الدفع القديمة!

## Practical walkthrough

هندسة توجيه المدفوعات باستخدام نمط Strategy و Hilt Multibindings:
```kotlin
// 1. العقد الموحد للاستراتيجيات (Strategy Interface):
interface PaymentStrategy {
    val method: PaymentMethod
    suspend fun authorize(amountCents: Long, details: PaymentDetails): PaymentResult
}

// 2. تطبيقات مستقلة ومعزولة لكل مزود خدمة:
class StripePaymentStrategy @Inject constructor(...) : PaymentStrategy {
    override val method = PaymentMethod.CREDIT_CARD
    override suspend fun authorize(amountCents: Long, details: PaymentDetails) = ...
}

class PayPalPaymentStrategy @Inject constructor(...) : PaymentStrategy {
    override val method = PaymentMethod.PAYPAL
    override suspend fun authorize(amountCents: Long, details: PaymentDetails) = ...
}

// 3. الموجه (PaymentRouter) مغلق تماماً للتعديل ومفتوح للتوسيع (OCP):
class PaymentRouter @Inject constructor(
    private val strategies: Set<@JvmSuppressWildcards PaymentStrategy>
) {
    suspend fun routeAndPay(method: PaymentMethod, amountCents: Long, details: PaymentDetails): PaymentResult {
        val strategy = strategies.firstOrNull { it.method == method }
            ?: return PaymentResult.Error("Payment method not supported")
        return strategy.authorize(amountCents, details)
    }
}
```

## Why it matters and how it works

Strategies isolate interchangeable algorithms behind a stable caller contract. Shared policy remains in the orchestration layer; provider-specific SDK mapping stays in adapters. Adding an implementation still needs registration and verification.

## Worked example

Conceptual Kotlin:
```kotlin
interface PaymentStrategy {
    val method: String
    suspend fun submit(request: PaymentRequest): PaymentOutcome
}
data class PaymentRequest(val minor: Long, val requestId: String)
sealed interface PaymentOutcome { data class Pending(val id: String): PaymentOutcome; data class Rejected(val code: String): PaymentOutcome }
```
Server status must later confirm completion; this snippet is a contract, not a transaction implementation.

## Trade-offs and decision criteria

For two fixed methods, an explicit `when` can be clearer. A strategy registry earns its cost when variation is frequent or provider code is large. Keep selection policy explicit; dynamic reflection discovery is not necessary for OCP.

## Failure modes

One adapter maps a timeout to `Rejected` while another maps it to `Pending`, breaking substitutability and retry safety. Define shared semantics and contract tests. Another failure is putting provider secrets in APK; backend owns them.

## Production perspective

A wallet app routes card and bank methods through adapters, persists request IDs, and reconciles uncertain outcomes with server. Provider-specific metrics are labeled without logging sensitive details.

## Interview answer — short

Strategy-based payment routing implements OCP by abstracting providers behind a common `PaymentStrategy` interface. A `PaymentRouter` delegates payments to the matching strategy at runtime. New payment methods are introduced by adding new strategy classes without modifying, recompiling, or risking regressions in existing payment code.

## Interview answer — structured

Strategy-based payment routing is the premier textbook demonstration of the Open/Closed Principle (OCP) in production architecture.

First, **The Anti-Pattern (Closed to Extension, Open to Modification)**. Next, a centralized `PaymentManager` uses a massive `when(type)` statement branching into credit card, PayPal, and crypto logic.
Every time a product manager requests Apple Pay or a regional provider, engineers must edit `PaymentManager.kt`. This introduces regression risks to existing revenue streams, causes Git merge conflicts, and invalidates existing payment test suites. **The OCP Architecture (Open to Extension, Closed to Modification)**.
With Abstractions, define a `PaymentStrategy` interface with `authorize(amount, details)`. With Concrete Strategies, each provider is encapsulated in an isolated class: `StripeStrategy`, `PayPalStrategy`, `GooglePayStrategy`.
Finally, a The Open Router is the `PaymentRouter` depends strictly on a collection of injected strategies (`Set<PaymentStrategy>`), selecting the appropriate handler by querying `strategy. Method == requestedMethod`.

Adding a new provider requires creating a new class and registering it with Dagger/Hilt; the core `PaymentRouter` and existing providers remain 100% untouched and closed to modification.


## Interview answer — deep senior

Under the hood, Dagger/Hilt's **Multibindings (`@IntoSet`)** perfectly operationalizes this pattern. A feature module can define `class KlarnaStrategy : PaymentStrategy` and bind it into the multibinding set inside its own internal Hilt module. The core `:feature:payment` module doesn't even have a compile-time dependency on Klarna's SDK! Dagger collects all strategies at application assembly time, realizing true runtime extensibility without coupling.

In testing, verifying `PaymentRouter` requires a simple unit test with mock/fake strategies to ensure it returns the correct error when a method is unsupported, while each strategy's network integration is tested in complete isolation.


## How to answer in the interview

- **Why:** Identify stable checkout policy.
- **How:** walk through adapter and router.
- **Trade-offs:** mention indirection.
- **Failure cases:** flag semantic mismatch and timeouts.
- **Production solutions:** finish with contract tests and server confirmation..

## Deep-dive talking points

Define strategy contract, shared policy, provider mapping, selection, contract tests and server reconciliation.

## Follow-up questions

- **Interviewer:** "How do you handle provider-specific input fields (e.g. CVV vs PayPal token)?"
  **Answer:** "By modeling payment credentials as a sealed class hierarchy `PaymentCredentials` (`CreditCard(number, cvv)`, `PayPal(token)`). Each strategy inspects its expected credential type safely."

- **Interviewer:** "How does Dagger `@IntoSet` multibinding support OCP?"
  **Answer:** "It allows independent modules to contribute their strategy implementations to a shared `Set<PaymentStrategy>` without central code having to explicitly instantiate or list them."

## Self-check rubric

Add a third provider on paper and count which files change; include timeout and cancellation contract tests.

## References and reviewed-on date

- [Robert C. Martin, Open Closed Principle](https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html) — strategic extension.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — adapter/repository boundary.

Technically reviewed against primary documentation on 2026-10-13.
