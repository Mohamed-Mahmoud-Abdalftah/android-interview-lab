---
id: "ARC-15"
question: "When do you introduce interfaces, and when can concrete implementations be sufficient?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 160
editorial_status: "reviewed"
---

# ARC-15

## Original interview question

When do you introduce interfaces, and when can concrete implementations be sufficient?

## What the interviewer evaluates

Choose interfaces for meaningful polymorphism, boundaries and tests, not one per class.

## Concept and technical explanation

Interfaces in software architecture decouple contractual abstractions from concrete execution details, enabling polymorphism, the Dependency Inversion Principle, and isolated unit testing. Interfaces should be introduced when: (1) multiple distinct production implementations exist or are planned (such as PaymentGateway implemented via Stripe, PayPal, and Google Pay, or BiometricAuthenticator with platform variants), (2) formal architectural boundaries must be enforced across modules (e.g., Domain defines a Repository interface, while Data provides the concrete implementation), or (3) high-fidelity test fakes are required for deterministic JVM testing without mocking libraries. Conversely, concrete classes are entirely sufficient for internal helpers, data mappers, private repository implementations, and Use Cases that have exactly one logical implementation. Creating 1:1 interfaces (e.g. ILoginUseCase and LoginUseCaseImpl) creates interface pollution, adds navigation indirection, and provides zero architectural value.

## Practical walkthrough (English)

Contrasting necessary boundary interfaces with sufficient concrete classes:
```kotlin
// 1. GENUINE NEED FOR INTERFACE: Architectural boundary & test fakes
interface PaymentGateway {
    suspend fun processPayment(amount: Double): Result<TransactionReceipt>
}
// Concrete production implementation in :core:data
class StripePaymentGateway(private val api: StripeApi) : PaymentGateway { ... }
// Test fake in :core:testing for lightning-fast unit tests
class FakePaymentGateway : PaymentGateway {
    var shouldFail = false
    override suspend fun processPayment(amount: Double) =
        if (shouldFail) Result.failure(Exception("Declined")) else Result.success(TransactionReceipt("TX-1"))
}

// 2. CONCRETE SUFFICIENT: Single-purpose UseCase with pure domain rules
class CalculateLoanInterestUseCase { // ❌ DO NOT create ICalculateLoanInterestUseCase!
    operator fun invoke(principal: Double, rate: Double, tenureMonths: Int): Double {
        return (principal * rate * tenureMonths) / 1200.0
    }
}
```

## Explanation in Arabic

متى تقوم بإنشاء واجهات (Interfaces)، ومتى تكون الكلاسات الحقيقية الملموسة (Concrete Implementations) كافية دون إفراط؟

1. متى يكون الـ Interface واجباً ومبرراً بنسبة 100%؟
   - **تطبيق مبدأ Inversion of Control (عكس التبعية)**: في حدود الـ Clean Architecture؛ مثل `UserRepository` في الـ Domain والـ `UserRepositoryImpl` في الـ Data، لمنع الـ Domain من الاعتماد على مكتبات خارجية.
   - **تعدد طرق التنفيذ الفعلية (Polymorphism / Multiple Implementations)**: مثل `PaymentProcessor` الذي يمتلك تنفيذين حقيقيين: `StripeProcessor` و `GooglePayProcessor`.
   - **عزل المكونات الخارجية صعبة الاختبار (Flaky / Native / Third-Party)**: مثل خدمات الموقع `LocationProvider`، مشغل الصوت `MediaPlayer`، أو مستشعرات البلوتوث؛ حيث تحتاج لـ `FakeLocationProvider` للاختبار على الـ JVM.

2. متى تكون الكلاسات الملموسة (Concrete Classes) كافية ويفضل تجنب الـ Interfaces؟
   - **كلاسات الـ UseCases الفردية**: الـ `PlaceOrderUseCase` هو كلاس كوتلن نقي 100% ليس له سوى تنفيذ وحيد؛ إنشاء `interface PlaceOrderUseCase` ومعه `PlaceOrderUseCaseImpl` هو تكرار عقيم وبويلربليت لا فائدة منه (Interface-itis).
   - **الـ ViewModels**: لا تحتاج إطلاقاً لـ Interface لأن الـ Composable أو الـ Fragment يستهلكها كـ Concrete Holder.
   - **خدمات البيانات الداخلية غير المعقدة** التي ليس لها سوى تطبيق واحد.

## Practical walkthrough

المقارنة بين استخدام مبرر لـ Interface واستخدام غير مبرر (Boilerplate):
```kotlin
// ❌ INTERFACE-ITIS (بويلربليت غير مبرر): كلاس نقي له تطبيق وحيد:
interface CalculateDiscountUseCase {
    fun execute(order: Order): Long
}
class CalculateDiscountUseCaseImpl : CalculateDiscountUseCase {
    override fun execute(order: Order): Long = (order.total * 0.1).toLong()
}

// ✅ الكود الأبسط والأنظف: UseCase كـ Concrete Class مباشرة:
class CalculateDiscountUseCase {
    operator fun invoke(order: Order): Long = (order.total * 0.1).toLong()
}

// ✅ استخدام مبرر وممتاز للـ Interface: عزل خدمة خارجية وتعدد التنفيذات:
interface AnalyticsTracker {
    fun track(event: String, params: Map<String, Any> = emptyMap())
}
class FirebaseAnalyticsTracker : AnalyticsTracker { ... }
class DebugConsoleAnalyticsTracker : AnalyticsTracker { ... } // مفيد للـ Debug
class FakeAnalyticsTracker : AnalyticsTracker { ... } // مفيد للـ Unit Tests
```

## Why it matters and how it works

Abstractions are valuable when they protect independent change or express a stable consumer contract. Testability comes from substitutable dependencies and deterministic seams, not simply counting interfaces.

## Worked example

Example decision: `PaymentProcessor` interface with `CardProcessor` and `WalletProcessor` supports provider strategy and tests. A single `PriceFormatter` pure class with no planned variation can stay concrete. If its constructor accepts locale/format dependency, tests can still instantiate it.

## Trade-offs and decision criteria

Interfaces add indirection, API maintenance, and potential abstraction drift. Concrete dependencies can be simpler until a variation or module boundary emerges. Extracting an interface later is often cheaper than maintaining a premature one.

## Failure modes

An interface mirrors every method of one class, then both change together on each feature request. It is not an abstraction boundary. Conversely, a domain module importing `RetrofitPaymentClient` couples stable policy to volatile transport.

## Production perspective

A subscription app uses a narrow `EntitlementSource` contract consumed by policy code, with production and fake implementations. Inside one feature, a simple formatter remains concrete and tests call it directly.

## Interview answer — short

Introduce interfaces at architectural boundaries to invert dependencies, when multiple implementations exist like different payment gateways, or to enable fake implementations in tests. Concrete classes are sufficient for internal use cases, mappers, and utilities where only one implementation exists and mocking or direct instantiation is straightforward.

## Interview answer — structured

Deciding between an interface and a concrete class requires evaluating boundary isolation and polymorphic necessity against navigation friction.

Interfaces are essential at architectural boundaries where you need to enforce the Dependency Inversion Principle. For example, declaring a Repository interface in the domain layer allows the data layer to implement it without the domain depending on data implementation details.

In production, interfaces are mandatory when multiple implementations exist, such as swapping between Google Play Billing and Stripe, or providing high-fidelity test fakes for fast JVM unit tests without mock libraries.
As for concrete classes, they are entirely sufficient for use cases, mappers, and internal repository helpers that have only one reasonable implementation. Creating 1:1 interfaces with names like ILoginUseCase adds navigation indirection and cognitive noise without delivering any real polymorphic or testability advantage.


## Interview answer — deep senior

Under the hood, dogmatic adherence to the interface-everything rule stems from legacy Java and C# paradigms where mocking libraries required interfaces to generate dynamic proxies. In modern Kotlin and Android development with MockK and native test fakes, creating an interface with a single Impl class for every single component is an anti-pattern known as interface pollution.
Interfaces shine when they define stable contracts across module boundaries. In multi-module Gradle setups, a feature module should depend only on an interface PaymentRepository defined in core model or core domain, while the concrete PaymentRepositoryImpl in core data is wired in via Hilt. This drastically reduces incremental build times because modifying the internal logic of PaymentRepositoryImpl does not invalidate the build cache of the consuming feature module.
Furthermore, interfaces are superior when creating hand-crafted test fakes. While mocking libraries introduce reflection overhead, implementing a lightweight FakeUserRepository backing operations with a simple in-memory list makes unit tests lightning-fast, readable, and deterministic.
Staff engineers apply a clear rule: use interfaces at architectural and module boundaries, when multiple production implementations exist, or for external hardware/SDK wrappers. Use concrete classes for internal business logic, UseCases, and private helpers where polymorphism is absent and 1:1 interfaces merely add visual clutter.

## How to answer in the interview

- **Why:** abstraction should isolate variability.
- **How:** introduce interface at meaningful boundary.
- **Trade-off:** testability versus interface sprawl.
- **Failure case:** fake hides broken real adapter.
- **Production solution:** pair fake policy test with integration.

## Deep-dive talking points

Compare a provider strategy with a pure formatter. Discuss consumer-owned contracts, fakes, DI and abstraction drift.

## Follow-up questions

- **Interviewer:** "What is 'Interface-itis'?"
  **Answer:** "The dogmatic anti-pattern of creating a 1-to-1 interface for every single class in an application (e.g. `Foo` and `FooImpl`), which doubles file counts and maintenance overhead without providing any polymorphism or decoupling value."

- **Interviewer:** "How do API/Impl module splits leverage interfaces for faster build times?"
  **Answer:** "Consuming modules depend only on the stable API module containing interfaces. When code inside the Impl module changes, Gradle skips recompiling the consuming modules because public ABI signatures haven't changed."

## Self-check rubric

Name one interface worth extracting and one concrete class you would keep; justify both by change boundaries.

## References and reviewed-on date

- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) — dependency practices.
- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — reuse and testability.

Technically reviewed against primary documentation on 2026-10-13.
