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

## Concept and technical explanation

Strategy-based payment routing supports the Open/Closed Principle (OCP) by encapsulating variable payment provider mechanics behind a stable, polymorphic contract. In transactional systems, business logic must adapt dynamically to diverse payment rails such as Google Pay, Stripe, PayPal, and local gateways without continually editing core checkout workflows. By defining a common PaymentStrategy interface and leveraging dependency injection multibindings, adding a new gateway becomes an entirely additive operation: developers write a new isolated strategy class and register it into the DI graph, keeping core orchestrator classes strictly closed to modification.

## Practical walkthrough (English)

Implementing an extensible payment routing architecture adhering to OCP:
```kotlin
// 1. Stable abstraction contract
interface PaymentStrategy {
    fun supports(method: PaymentMethod): Boolean
    suspend fun processPayment(amount: Long, payload: PaymentData): Result<TransactionReceipt>
}

// 2. Additive concrete payment rail implementations
class StripePaymentStrategy @Inject constructor(private val stripeClient: StripeClient) : PaymentStrategy {
    override fun supports(method: PaymentMethod) = method is PaymentMethod.CreditCard
    override suspend fun processPayment(amount: Long, payload: PaymentData): Result<TransactionReceipt> {
        return runCatching { stripeClient.charge(amount, payload.token) }
    }
}

class GooglePayStrategy @Inject constructor(private val gPayClient: GooglePayClient) : PaymentStrategy {
    override fun supports(method: PaymentMethod) = method is PaymentMethod.GooglePay
    override suspend fun processPayment(amount: Long, payload: PaymentData): Result<TransactionReceipt> {
        return runCatching { gPayClient.authorizeAndCapture(amount) }
    }
}

// 3. Routing orchestrator is strictly CLOSED to modification
class PaymentRouter @Inject constructor(
    private val strategies: Set<@JvmSuppressWildcards PaymentStrategy>
) {
    suspend fun routePayment(method: PaymentMethod, amount: Long, payload: PaymentData): Result<TransactionReceipt> {
        val strategy = strategies.firstOrNull { it.supports(method) }
            ?: return Result.failure(IllegalArgumentException("Unsupported payment rail: $method"))
        return strategy.processPayment(amount, payload)
    }
}
```

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

Strategy-based payment routing upholds OCP by delegating transaction execution to polymorphic strategy classes conforming to a common interface. Instead of maintaining a central checkout class with growing when statements that require editing for every new payment method, the router receives a collection of strategies via dependency injection. Adding a new provider like Google Pay simply requires implementing the interface in a new class, leaving the orchestrator completely untouched and free from regression risks.

## Interview answer — structured

Using the Strategy pattern for payment routing is a quintessential textbook demonstration of the Open/Closed Principle in enterprise Android engineering.
In anti-pattern architectures, payment routing is implemented through a centralized checkout manager with a massive when expression. Every time business requirements introduce a new payment method or regional banking rail, engineers are forced to open the critical checkout class, add a new conditional branch, and modify existing code. This introduces high regression risk, invalidates past QA certification, and causes merge conflicts among feature teams.
To uphold OCP, the checkout mechanism is divided into an orchestrator and isolated strategies.
First, a PaymentStrategy interface defines the contract, requiring each strategy to declare which payment methods it supports and execute the transaction.
Second, each provider (Stripe, PayPal, Google Pay) is implemented as a self-contained strategy class encapsulating its specific SDK dependencies and error mapping.
Third, the orchestrating PaymentRouter injects a set of strategies using Dagger Multibindings (@IntoSet). At runtime, it iterates through the injected set to select and execute the appropriate strategy polymorphically.
When new payment methods arrive, engineers write a new strategy without altering a single line of existing routing logic.

## Interview answer — deep senior

Under the hood, strategy-based payment routing replaces hardcoded compiler branch instructions (tableswitch or lookupswitch bytecodes) with dynamic polymorphic dispatch and set lookups.
In a large multi-module Gradle architecture, this pattern provides significant compilation avoidance benefits. If the central payment router directly imports Stripe, PayPal, and Google Pay SDKs, the payment feature module becomes coupled to massive external vendor dependencies. Upgrading the Stripe SDK triggers a complete recompilation of the checkout feature module and all its consumers.
By applying OCP with Dagger Multibindings, the core :feature:checkout module depends solely on the abstract PaymentStrategy interface. Each provider lives in its own isolated Gradle module: :payment:stripe, :payment:googlepay, and :payment:paypal.
These provider modules plug their strategies into the Dagger dependency graph via @Binds @IntoSet within their respective Hilt modules. The :feature:checkout module never compiles against the third-party payment SDKs, keeping incremental compilation times minimal and enabling parallel compilation across CI build nodes.
Furthermore, this architecture maximizes runtime safety and testing velocity. Unit testing the PaymentRouter requires only passing a simple mock or fake strategy into the set, verifying routing logic in milliseconds on the JVM without loading heavyweight merchant SDKs or native cryptography libraries. This design isolates transient vendor API breaking changes from affecting the core checkout pipeline, guaranteeing maximum transactional reliability.

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
