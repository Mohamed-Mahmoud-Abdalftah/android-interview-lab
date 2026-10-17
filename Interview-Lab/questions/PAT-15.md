---
id: "PAT-15"
question: "Design multiple payment providers with Strategy or Factory. How do you avoid a god-factory?"
topic: "Design Patterns"
code: "PAT"
group: "C"
phase: 2
priority: "P1"
order: 206
editorial_status: "reviewed"
---

# PAT-15

## Original interview question

Design multiple payment providers with Strategy or Factory. How do you avoid a god-factory?

## What the interviewer evaluates

Design multi-provider selection without centralizing every provider behavior in a single factory.

## Concept and technical explanation

Architecting multiple payment provider integrations requires combining the Strategy pattern for polymorphic payment execution with a decoupled creation mechanism, such as Dagger/Hilt Multibindings, to avoid creating an anti-pattern God Factory. In a naive design, a centralized factory switch-statement hardcodes constructor references to every concrete payment gateway (such as Stripe, PayPal, GooglePay, and Klarna), violating the Open/Closed Principle whenever a new provider is added. By decoupling creation into a distributed map of provider factories using dependency injection multibindings, new payment strategies register themselves modularly at compile time, allowing the system to resolve strategies dynamically without central monolithic coupling.

## Practical walkthrough (English)

Decoupling multiple payment strategies using Dagger Multibindings:
```kotlin
// 1. Unified Domain Strategy Interface
interface PaymentStrategy {
    val method: PaymentMethod
    suspend fun executePayment(amountCents: Long, currency: String): Result<PaymentReceipt>
}

// 2. Concrete Strategy implementations (Isolated in independent modules)
class StripePaymentStrategy @Inject constructor(private val stripeClient: StripeClient) : PaymentStrategy {
    override val method = PaymentMethod.STRIPE
    override suspend fun executePayment(amountCents: Long, currency: String) = stripeClient.charge(amountCents)
}

class PayPalPaymentStrategy @Inject constructor(private val payPalSdk: PayPalSdk) : PaymentStrategy {
    override val method = PaymentMethod.PAYPAL
    override suspend fun executePayment(amountCents: Long, currency: String) = payPalSdk.checkout(amountCents)
}

// 3. Extensible Multi-binding Module (Eliminates God Factory switch-statements!)
@Module
@InstallIn(SingletonComponent::class)
abstract class PaymentModule {
    @Binds @IntoMap @PaymentMethodKey(PaymentMethod.STRIPE)
    abstract fun bindStripe(impl: StripePaymentStrategy): PaymentStrategy

    @Binds @IntoMap @PaymentMethodKey(PaymentMethod.PAYPAL)
    abstract fun bindPayPal(impl: PayPalPaymentStrategy): PaymentStrategy
}

// 4. Client Resolver (Open/Closed: never needs modification when new providers are added!)
class PaymentProcessor @Inject constructor(
    private val strategies: Map<PaymentMethod, @JvmSuppressWildcards Provider<PaymentStrategy>>
) {
    suspend fun process(method: PaymentMethod, amount: Long, currency: String): Result<PaymentReceipt> {
        val strategyProvider = strategies[method] ?: return Result.failure(UnsupportedPaymentException(method))
        return strategyProvider.get().executePayment(amount, currency)
    }
}
```

## Explanation in Arabic

تصميم نظام دفع يدعم مزودي خدمة متعددين (Stripe, PayPal, Google Pay) باستخدام Strategy أو Factory، وكيفية تجنب الـ God Factory:

1. المشكلة مع الـ God Factory:
   - وضع جميع تفاصيل المزودين في كلاس واحد `PaymentFactory`: الكلاس يعرف تفاصيل كل SDK، وينشئ الـ UI الخاص بكل مزود، ويعالج الـ Callbacks والـ Retries الخاصة بكل بنك.
   - النتيجة: كلاس ضخم ينتهك مبدأ Single Responsibility و Open/Closed Principle. كلما أردت إضافة مزود دفع جديد، تضطر لتعديل واختبار `PaymentFactory` من جديد.

2. الحل المعماري النظيف (Strategy + Factory / DI Multibindings):
   - **Strategy Interface**: واجهة موحدة ونقية (`PaymentGateway` أو `PaymentStrategy`) تعرف عقداً عاماً لمعالجة الدفع: `suspend fun processPayment(request: PaymentRequest): PaymentResult`.
   - **Adapters مستقلة لكل مزود**: كلاس مستقل لكل مزود (`StripePaymentAdapter`, `GooglePayAdapter`, `PayPalAdapter`) يغلف الـ SDK الخاص به ويعزل تفاصيله تماماً.
   - **تجنب الـ God Factory عبر DI Multibindings (Dagger/Hilt)**: بدلاً من كتابة `when(type) { STRIPE -> StripeAdapter(...) }`، نستخدم خريطة محقونة تلقائياً `Map<PaymentType, @JvmSuppressWildcards PaymentStrategy>`. إضافة مزود جديد تتطلب فقط كتابة كلاس جديد وتزويد الـ Module برابط له دون لمس سطر واحد في الكود القائم.

## Practical walkthrough

تنفيذ Strategy Pattern مع DI Multibindings لتفادي الـ God Factory:
```kotlin
// 1. العقد الموحد (Strategy Interface):
interface PaymentStrategy {
    val supportedType: PaymentType
    suspend fun pay(orderId: String, amount: Money): PaymentResult
}

// 2. تطبيق مستقل لكل مزود يعزل الـ SDK تماماً (Concrete Strategies):
class StripeStrategy @Inject constructor(
    private val stripeClient: StripeSdkClient
) : PaymentStrategy {
    override val supportedType = PaymentType.STRIPE
    override suspend fun pay(orderId: String, amount: Money): PaymentResult {
        return stripeClient.confirmPayment(orderId, amount.toCents()).toDomain()
    }
}

class GooglePayStrategy @Inject constructor(
    private val paymentsClient: PaymentsClient
) : PaymentStrategy {
    override val supportedType = PaymentType.GOOGLE_PAY
    override suspend fun pay(orderId: String, amount: Money): PaymentResult {
        return paymentsClient.requestPayment(orderId, amount).toDomain()
    }
}

// 3. مدير الدفع النظيف الخالي من الـ God Factory عبر Map Injection:
class PaymentProcessor @Inject constructor(
    private val strategies: Set<@JvmSuppressWildcards PaymentStrategy>
) {
    private val strategyMap: Map<PaymentType, PaymentStrategy> by lazy {
        strategies.associateBy { it.supportedType }
    }

    suspend fun executePayment(type: PaymentType, orderId: String, amount: Money): PaymentResult {
        val strategy = strategyMap[type] 
            ?: throw IllegalArgumentException("Unsupported payment provider: $type")
        return strategy.pay(orderId, amount)
    }
}
```

## Why it matters and how it works

Strategy isolates interchangeable provider behavior; a factory or registry only selects or constructs it. Separating selection from execution prevents a god-factory and protects stable policy. Common outcome semantics matter more than class names.

## Worked example

JVM routing core; provider adapters and server verification are app-owned. Each strategy must satisfy the same `SubmitOutcome` contract and the repository persists the attempt identity before calling the router.
```kotlin
enum class PaymentMethod { CARD, WALLET }
sealed interface SubmitOutcome {
    data class Accepted(val receiptId: String) : SubmitOutcome
    data class Rejected(val reason: String) : SubmitOutcome
    data class PendingVerification(val attemptId: String) : SubmitOutcome
    data object UnsupportedMethod : SubmitOutcome
}
interface PaymentStrategy {
    val method: PaymentMethod
    suspend fun submit(attemptId: String): SubmitOutcome
}
class PaymentRouter(strategies: Set<PaymentStrategy>) {
    private val byMethod = strategies.associateBy(PaymentStrategy::method)
    init { require(byMethod.size == strategies.size) { "Duplicate payment method" } }
    suspend fun submit(method: PaymentMethod, id: String): SubmitOutcome =
        byMethod[method]?.submit(id) ?: SubmitOutcome.UnsupportedMethod
}
```
The router only selects; authentication, idempotency, redacted telemetry and reconciliation belong to the shared data boundary, with final authority on the server.

## Trade-offs and decision criteria

A simple `when` is enough for a stable two-provider app. A registry scales when providers change, but dynamic registration can hide duplicate keys or missing bindings; validate graph at startup/tests. Avoid reflection discovery without a real need.

## Failure modes

Factory branches on provider for every SDK call and silently maps wallet timeout to failure while card timeout is pending. Duplicate payment retry risk follows. Move mapping into adapters and enforce shared contract tests.

## Production perspective

A commerce app adds a bank transfer provider through one adapter and DI binding, then runs provider contract and backend reconciliation tests. Server holds credentials and authorizes charges.

## Interview answer — short

To design multiple payment providers without a God Factory, combine the Strategy pattern with Dagger/Hilt Multibindings. Define a unified PaymentStrategy interface implemented by isolated payment adapters. Instead of hardcoding all providers into a monolithic factory switch-statement that violates the Open/Closed Principle, use multibindings to inject a Map of provider factories. Adding a new payment provider requires only binding the new strategy in its own module, leaving existing processor code untouched.

## Interview answer — structured

Designing a scalable multi-provider payment architecture requires separating algorithmic strategy execution from provider instantiation mechanics.
The traditional pitfall in payment architecture is creating a God Factory. In this anti-pattern, a single factory class contains a massive switch or when block that directly instantiates Stripe, PayPal, Adyen, and crypto providers. This violates the Open/Closed Principle: every time a payment vendor is added, modified, or decommissioned, the shared factory file must be edited, recompiled, and retested, creating merge conflicts and tight coupling across independent vendor dependencies.
To solve this cleanly, architects implement the Strategy pattern alongside distributed dependency injection.
First, a clean PaymentStrategy interface establishes a common contract for processing transactions, handling two-factor authentication callbacks, and returning standardized receipts. Each concrete payment provider implements this strategy within an isolated feature or infrastructure module.
To avoid the God Factory, the system uses Dagger/Hilt Multibindings to collect strategies into a map: Map<PaymentMethod, Provider<PaymentStrategy>>. Each module contributes its own strategy binding using @IntoMap and a custom key annotation.
The calling PaymentProcessor simply queries the injected map at runtime. Adding a new payment provider involves authoring the new class and registering its binding, achieving complete extensibility without altering a single line of existing orchestrator code.

## Interview answer — deep senior

Under the hood, using Provider<PaymentStrategy> inside the injected map is essential for memory efficiency, cold-start latency, and classloading optimization.
If the map injected direct strategy instances: Map<PaymentMethod, PaymentStrategy>, the dependency injection container would be forced to eagerly initialize every payment SDK, allocate network pools, and load foreign vendor native libraries during application launch, severely degrading cold startup time even if the user never opens the checkout flow.
By wrapping each map value in a Dagger Provider, strategies are instantiated lazily on demand. The vendor SDK and its associated memory footprint are only allocated when the user explicitly taps that specific payment option.
Furthermore, this architecture enforces strict multi-module compilation boundaries. Each payment gateway can reside in its own isolated Gradle module, such as :feature:payment:stripe and :feature:payment:paypal. These implementation modules depend on the abstract payment contract module, while the app module combines them via Gradle dependencies.
This separation allows Gradle to build payment modules in parallel, isolates sensitive third-party SDK dependencies from core domain logic, and enables dynamic feature delivery where rarely used payment gateways can be downloaded on demand via Android Play Feature Delivery. Furthermore, incorporating Circuit Breaker or Retry decorators around individual payment strategies shields the core checkout flow against transient vendor outages, providing predictable failover mechanisms without polluting strategy logic.

## How to answer in the interview

- **Why:** Provider variation should stay local without centralizing every policy.
- **How:** Inject strategies, select by method, return one domain outcome type.
- **Trade-off:** Put shared policy in coordinator, not duplicated strategy code.
- **Failure case:** God-factory or silent fallback to wrong provider.
- **Production solution:** Common contract tests plus explicit unsupported-method outcome.

## Deep-dive talking points

Separate selection, strategy execution, shared policy and server status; test unknown/duplicate registration.

## Follow-up questions

- **Interviewer:** "How do Dagger/Hilt multibindings eliminate factory modification?"
  **Answer:** "By using `@IntoSet` or `@IntoMap`, each provider module declares its own strategy binding independently. Dagger assembles them into an injected collection automatically without modifying any central factory class."

- **Interviewer:** "How do you handle providers that require an ActivityResultLauncher?"
  **Answer:** "Define a capability interface like `ActivityLauncherPaymentStrategy` where the UI provides a registered launcher contract before executing the payment."

## Self-check rubric

Sketch a router and one adapter, then name two responsibilities forbidden in the router.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — Strategy and Factory patterns.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository coordination.

Technically reviewed against primary documentation on 2026-10-13.
