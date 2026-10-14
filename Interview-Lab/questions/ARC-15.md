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

Introduce interfaces at architectural boundaries to invert dependencies (e.g. Domain Repository interfaces), when multiple production implementations exist (e.g. Stripe vs Google Pay), or to abstract volatile external systems (e.g. GPS, Bluetooth). Concrete classes are sufficient for single-implementation Use Cases and ViewModels.

## Interview answer — structured

Deciding when to introduce interfaces distinguishes pragmatic senior engineers from dogmatic architects suffering from 'Interface-itis'.

First, **When Interfaces are Genuinely Necessary**. Next, inversion of Control across Boundaries is the quintessential Clean Architecture contract: the Domain layer declares `interface OrderRepository`, and the Data layer implements it, keeping the Domain pure.
Additionally, with Multiple Real Implementations, when the system genuinely supports swappable implementations (e.g. `interface PaymentGateway` implemented by `StripeGateway` and `PayPalGateway`). With Abstracting Flaky External Systems, wrapping hardware, system frameworks, or third-party SDKs (`LocationManager`, `BluetoothScanner`, `BiometricAuth`) behind an interface allows creating high-speed `Fake` implementations for JVM unit testing.
**When Concrete Classes are Sufficient**. An Use Cases (Interactors) is a Use Case encapsulates a single business scenario in pure Kotlin. Creating `interface CheckoutUseCase` paired with `CheckoutUseCaseImpl` is 100% redundant boilerplate.
ViewModels have a single implementation bound to UI state. Finally, with Internal Utilities, helper classes and mappers.


## Interview answer — deep senior

A legacy justification for interfaces was testability in Java: developers couldn't mock concrete classes without interfaces. In modern Kotlin, with MockK and Mockito-inline, mocking concrete classes is trivial. More importantly, modern testing best practices advocate using **Fakes over Mocks**. For a pure Kotlin Use Case, you don't even need a mock or a fake—you instantiate the concrete class directly in your test!

In large multi-module codebases, interfaces enable **Compilation Avoidance**. If an interface lives in an API module (`:feature:chat:api`) and its implementation lives in an implementation module (`:feature:chat:impl`), changing the internal implementation logic does not invalidate or recompile the dozens of downstream modules that only depend on the API module.

We adhere to the Rule of Three: do not abstract with an interface until you have two distinct implementations or a strict architectural dependency boundary.


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
