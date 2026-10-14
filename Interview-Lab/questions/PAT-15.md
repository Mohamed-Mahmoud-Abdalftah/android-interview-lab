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

To support multiple payment providers without creating a God Factory, define a clean Strategy interface (PaymentStrategy) representing unified payment contracts. Implement isolated Adapters for each provider SDK. Instead of hardcoding all initializations in a massive factory switch-statement, use Dagger/Hilt multibindings to inject a map or set of strategies, adhering strictly to the Open/Closed Principle.

## Interview answer — structured

When designing a multi-payment architecture, the common failure is building a monolithic 'God Factory' that imports every vendor SDK, configures their credentials, handles their distinct callback listeners, and manages UI presentation logic in a giant `when` statement.

A clean production architecture decouples this into three distinct layers.

First, with Unified Strategy Contract, we declare a high-level `PaymentStrategy` interface exposing common transaction semantics: `suspend fun pay(orderId: String, amount: Money): PaymentResult`. Next, with Isolated Vendor Adapters, each provider (Stripe, PayPal, Google Pay) lives in its own class—or even its own Gradle module. The adapter handles SDK initialization, maps vendor exceptions into typed domain results, and keeps third-party imports quarantined.
Finally, with Registry via DI Multibindings, instead of a monolithic factory class, we use Dagger/Hilt multibindings (`@IntoSet` or `@IntoMap`). The `PaymentProcessor` receives an injected `Map<PaymentMethod, PaymentStrategy>`. Adding a new payment provider requires writing one new adapter class and one binding module; existing code is completely untouched, honoring the Open/Closed Principle.


## Interview answer — deep senior

The subtle architectural challenge in multi-payment systems is that payment providers rarely share identical lifecycle and UI capabilities. For example, Google Pay presents a native Android BottomSheet sheet, Stripe requires a 3D Secure Webview/Activity redirect, while direct card entry requires PCI-DSS compliant tokenization fields.

If you force all these divergent requirements into a single synchronous `pay()` method, your Strategy abstraction leaks. To address this in enterprise systems.

First, with Capability Interfaces, we break the strategy into capabilities: `DirectCheckoutStrategy` for headless API payments, and `InteractiveCheckoutStrategy` for providers requiring an Activity result launcher (`ActivityResultLauncher`). Next, an Idempotency and Reconciliation is the payment processor must be backed by an idempotency key generated prior to engaging the strategy. If the user completes 3DS verification and the app process dies while returning, the app queries the backend status rather than retrying through the strategy.
Finally, with Feature Flagging & Remote Fallbacks, strategies can be decorated with a `CircuitBreakerDecorator` or remote configuration flag. If Stripe experiences an outage in a specific region, the processor dynamically removes Stripe from the UI and falls back to PayPal without deploying a new app binary.


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
