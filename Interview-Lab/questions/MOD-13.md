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

Depend on interfaces across module boundaries where independent substitution, test seams, and compile-time decoupling are required (e.g. repositories, payment gateways). Depend on concrete types for immutable data models, value objects, and internal same-module utilities where multiple implementations will never exist.

## Interview answer — structured

The decision to depend on an interface versus a concrete type is an architectural choice balancing flexibility against ceremony.

First, **Depend on an Interface**. Next, with Architectural Seams, between domain layers and data layers (Repositories, Gateways). This allows UI and Domain logic to be tested on the JVM with fast Fakes without compiling Room or Retrofit.
Additionally, with Cross-Module API Contracts, when splitting modules into `:feature:api` and `:feature:impl` to break rebuild cascades and circular dependencies. With Polymorphism, when multiple implementations exist (e.g., debug mock data source vs. Production network data source).
**Depend on a Concrete Type**. With Data Models and Value Objects, immutable data classes (`User`, `TransactionDetails`) should never be wrapped in interfaces. They carry data, not behavior.
Finally, with Same-Module Collaborators, internal helpers within a single feature module that will never need polymorphic variation or independent substitution.


## Interview answer — deep senior

From a build system perspective, an interface serves as an **ABI firewall**.

If module `A` depends on concrete class `DatabaseUserRepository` in module `B`, any private change inside `DatabaseUserRepository` (even changing a private helper method or adding a local variable) alters `B`'s bytecode. Depending on Gradle caching granularity, this can trigger recompilations.

If module `A` instead depends on `interface UserRepository` in `:domain:user-api`, module `A`'s compile classpath references **only the interface's ABI**. You can rewrite the entire SQL query, add caching, or refactor private methods inside `DatabaseUserRepository` in `:data:user`, and Gradle will **never recompile module `A`**. This compile-time insulation is one of the primary drivers of developer velocity in 100+ module repositories.


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
