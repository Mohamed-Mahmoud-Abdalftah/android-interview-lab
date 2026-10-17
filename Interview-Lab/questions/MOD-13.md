---
id: "MOD-13"
question: "When should a module depend on an interface versus a concrete type?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 366
editorial_status: "reviewed"
---

# MOD-13

## Original interview question

When should a module depend on an interface versus a concrete type?

## What the interviewer evaluates

- Use abstraction where independent substitution/ownership is real.
- Avoid interface-per-class ceremony.
- Explain compile boundary, tests and dependency direction.

## Concept and technical explanation

The decision to depend on an interface versus a concrete type across module boundaries governs architectural coupling and build cache efficiency:
- Depend on an Interface when: Crossing team ownership or feature boundaries; depending on volatile business implementations that change frequently; abstracting external infrastructure like network APIs, databases, or payment gateways that require test doubles in unit tests; or breaking potential circular dependency loops. Housing the interface in an independent :api module decouples consumers from internal implementation changes, preserving the Application Binary Interface (ABI) boundary.
- Depend on a Concrete Type when: The type represents an immutable value object, domain entity, or pure data transfer model without behavioral logic; relying on completely stable, foundational platform utilities that are never mocked (e.g., Kotlin standard library collections, time primitives); or operating within the private internal boundary of a single module. Creating interfaces for trivial, stable data models introduces needless indirection without architectural benefit.

## Practical walkthrough (English)

Contrasting interface contracts with concrete data models across module boundaries:
```kotlin
// 1. DEPEND ON CONCRETE TYPE: Immutable domain entity (Stable, pure data)
// In :core:model
data class MonetaryAmount(val amountInCents: Long, val currencyCode: String)

// 2. DEPEND ON INTERFACE: Volatile business capability with external I/O
// In :feature:payment:api
interface PaymentProcessor {
    suspend fun executePayment(amount: MonetaryAmount): Result<PaymentConfirmation>
}

// 3. In :feature:checkout:impl: Consumes the interface and concrete model
class CheckoutViewModel @Inject constructor(
    private val processor: PaymentProcessor // Interface dependency allows mocking in tests
) : ViewModel() {
    fun pay(cents: Long) = viewModelScope.launch {
        processor.executePayment(MonetaryAmount(cents, "USD"))
    }
}
```

## Explanation in Arabic

متى يجب أن يعتمد الموديول على واجهة مجردة (Interface) ومتى يكون اعتماده على كلاس ملموس (Concrete Type) أفضل وأكثر عملية؟

1. متى يجب الاعتماد على واجهة مجردة (Interface):
   - **عبر حدود الموديولات (Cross-Module Boundaries)**: عندما يعتمد موديول Presentation على موديول Data، الاعتماد على `UserRepository` كـ Interface يسمح بتطوير واختبار الـ UI بشكل مستقل تماماً.
   - **تعدد التطبيقات الحقيقية (Multiple Implementations)**: عندما يكون هناك تطبيقان فعليان للكلاس (مثل `StripePaymentGateway` و `PayPalPaymentGateway`).
   - **عزل المكتبات الخارجية المتقلبة (Volatile 3rd Party SDKs)**: عزل كود التحقق من الهوية أو التتبع بواجهة نقية.
   - **فصل وقت التجميع (Decoupling Compile Classpaths)**: التغيير في تنفيذ الـ Class لا يجبر الموديول المستهلك على إعادة التجميع طالما أن الـ Interface لم تتغير.

2. متى يكون الاعتماد على كلاس ملموس (Concrete Type) أفضل وأكثر واقعية:
   - **نماذج البيانات غير القابلة للتغيير (Immutable Data Classes / Value Objects)**: كلاسات مثل `User`, `Money`, `Address` يجب أن تكون Concrete Data Classes، ولا داعي لعمل `interface IUser` إطلاقاً!
   - **الكلاسات المساعدة النقية الخالية من الحالة (Stateless Utility Classes)**: دوال الرياضيات وتنسيق النصوص.
   - **الاستخدام الداخلي المحصور داخل الموديول الواحد (Same Module Internals)**: إذا كان الكلاس خاصاً بالـ Feature ولا يتم استخدامه خارجها، فالاعتماد المباشر يوفر طبقات وهمية غير مفيدة.

## Practical walkthrough

المقارنة بين التجريد الصحيح والتجريد المتكلف غير المبرر:
```kotlin
// ❌ تجريد متكلف لا داعي له (Over-abstraction on Data Models):
interface IUser { val id: String; val name: String }
class UserImpl(override val id: String, override val name: String) : IUser
// هذا هراء معماري يضاعف حجم الكود بدون أي فائدة حقيقية!

// ✅ استخدام Concrete Data Class لنماذج البيانات النظيفة:
data class User(val id: String, val name: String, val email: String)

// ✅ استخدام Interface فقط للحدود المعمارية ومصادر البيانات:
interface UserRepository {
    val currentUser: Flow<User>
    suspend fun updateProfile(name: String): Result<Unit>
}

// في الـ Feature ViewModel: الاعتماد على Interface يتيح اختبار الـ ViewModel بـ Fake في ثوانٍ:
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: UserRepository // Interface: سهولة خارقة في الاختبار والعزل
) : ViewModel()
```

## Why it matters and how it works

An interface can invert compile dependency from policy to implementation: the consumer compiles against a contract and an outer composition root provides a concrete binding. This enables independent testing and replacement. The abstraction only reduces coupling when its methods express stable capability; a mirror interface that changes with every implementation edit preserves coupling under a new name.

## Worked example

Orders ViewModel depends on `OrderRepository` exposing `observeOrder(id)` and `submitOrder(command)`, with domain results. `:data:orders` implements it with Room and API clients. Tests inject a fake. In the same feature, a final `CurrencyLabelFormatter` used in one place may be passed concretely until a real module or behavior boundary emerges.

## Trade-offs and decision criteria

Interfaces cost design, DI binding and maintenance but can isolate high-volatility implementation. Concrete dependencies are simpler when code changes together and no external contract is needed. Testability alone is not an excuse to abstract every class; constructor injection can also test many concrete collaborators.

## Failure modes

A contract returns Retrofit `Response` and therefore still couples the feature to transport. An interface has one method per implementation detail and changes every sprint. A feature directly imports a data implementation to avoid one needed interface. An unnecessary interface forest makes navigation through code slow.

## Production perspective

Review dependency direction and contract change frequency. Keep public interfaces small and semantically owned, and use integration tests to ensure selected implementations satisfy critical behavior beyond fake tests.

## Interview answer — short

A module should depend on an interface when crossing architectural boundaries, interacting with volatile implementations, or abstracting external systems like networks and databases that require mocking. It should depend on a concrete type when dealing with immutable domain entities, stable value models, or internal utilities within the same module.

## Interview answer — structured

Deciding whether to depend on an interface or a concrete type determines how changes ripple through your multi-module build graph.
You should depend on an interface whenever you are crossing architectural or organizational boundaries.
When a feature module needs to invoke capabilities from another feature, or interacts with external I/O systems like network clients and databases, relying on an interface is essential.
This decouples the caller from volatile implementation details and allows effortless substitution with test doubles during unit testing.
Conversely, you should depend directly on concrete types when dealing with immutable data structures, domain entities, and stable value objects.
A data class representing a user identifier or monetary amount contains no execution logic and rarely changes its structure.
Wrapping pure data models in interfaces adds pointless indirection without improving decoupling.

## Interview answer — deep senior

From a systems compilation and testing perspective, the choice between interface and concrete dependencies directly affects build cache invalidation and unit test execution speed.
When module A depends on a concrete class in module B, any modification to module B's class—including changing private variables or refactoring internal methods—alters module B's bytecode.
This triggers recompilation of module A unless strict ABI firewalls are maintained.
By introducing an interface inside an independent :api module, module A depends on a stable contract that rarely changes.
Refactoring the concrete implementation inside module B leaves module A's compile classpath clean, allowing Gradle to mark module A's compileKotlin task as UP-TO-DATE and preserving the build cache.
Furthermore, depending on interfaces is mandatory for architectural decoupling: it allows unit tests to substitute mock implementations instantly without loading device runtimes or starting real HTTP servers.
However, dogmatically creating interfaces for every single class is an anti-pattern known as interface pollution.
Immutable data models, value objects, and domain entities should always remain concrete classes.
A data class MonetaryAmount has no hidden behavior, does not perform I/O, and does not require mocking.
We reserve interfaces for components with operational behavior, external side effects, or cross-boundary coordination, ensuring maximum architectural flexibility without unneeded structural bloat.

## How to answer in the interview

- **Why:** interfaces protect variability, not aesthetics.
- **How:** place contract with consumer or stable core.
- **Trade-off:** flexibility versus boilerplate.
- **Failure case:** mock passes while real SDK fails.
- **Production solution:** pair seam test with integration.

## Deep-dive talking points

Discuss inversion, contract owner, implementation leakage, test fake drift, and abstraction cost.

## Follow-up questions

- **Interviewer:** "What is the 'Interface per Class' anti-pattern?"
  **Answer:** "Blindly creating an interface for every single class in a project, even when there is only one implementation and no architectural boundary, creating unnecessary indirection."

- **Interviewer:** "Can a Kotlin `interface` contain concrete method implementations?"
  **Answer:** "Yes, default interface methods allow providing default behavior without forcing consumers to override them."

## Self-check rubric

Choose one interface and one concrete dependency, justify ownership, and identify API leakage.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — boundaries and encapsulation.
- [Dependency injection on Android](https://developer.android.com/training/dependency-injection) — substitution and graph design.

Technically reviewed against primary documentation on 2026-10-13.
