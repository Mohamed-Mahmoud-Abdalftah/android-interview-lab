---
id: "MOD-11"
question: "How do you manage dependency injection across modules?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 364
editorial_status: "reviewed"
---

# MOD-11

## Original interview question

How do you manage dependency injection across modules?

## What the interviewer evaluates

- Place binding ownership and contracts correctly.
- Explain Hilt aggregation, scopes and variant visibility.
- Note dynamic-feature exception and test graph assembly.

## Explanation in Arabic

كيف تدير حقن التبعيات (Dependency Injection) عبر موديولات Gradle المتعددة؟

1. القاعدة المعمارية للـ DI في الـ Multi-Module:
   - **فصل العقد عن التنفيذ (Contract vs. Implementation Separation)**:
     * موديول الـ API أو الـ Domain يعرف الواجهة (`interface CartRepository`).
     * موديول الـ Data أو الـ Feature Impl يحتوي على الكلاس الملموس (`class CartRepositoryImpl @Inject constructor(...)`).
     * يوفر موديول الـ Data موديول Hilt معلّم بـ `@InstallIn(SingletonComponent::class)` يحتوي على `@Binds` يربط الواجهة بالتنفيذ.

2. التجميع المركزي في Hilt (Decentralized Aggregation in `:app`):
   - موديول `:app` يعتمد على جميع موديولات التطبيق.
   - يقوم Hilt في وقت التجميع بجمع (Aggregate) جميع الـ Modules المعلمة بـ `@InstallIn` عبر جميع موديولات Gradle ودمجها في شجرة Dagger Graph واحدة متكاملة ومتحقق منها.

3. إدارة الـ Scopes عبر الموديولات:
   - تجنب وضع `@Singleton` عشوائياً في موديولات الـ Features.
   - استخدم `@ViewModelScoped` لمنطق الشاشات في موديولات الـ Feature Impl، واحتفظ بـ `@Singleton` فقط للموارد المشتركة في موديولات الـ Core والـ Data.

## Practical walkthrough

هيكل تنظيم الـ Hilt Modules عبر الموديولات المختلفة:
```kotlin
// 📁 في موديول ':domain:payment' (موديول Kotlin نقي):
interface PaymentGateway {
    suspend fun pay(orderId: String, amount: Double): Result<TransactionReceipt>
}

// 📁 في موديول ':data:payment' (يحتوي على التنفيذ الفعلي وموديول Hilt):
class StripePaymentGateway @Inject constructor(
    private val stripeClient: StripeClient
) : PaymentGateway { /* ... */ }

@Module
@InstallIn(SingletonComponent::class)
abstract class PaymentDataModule {
    @Binds @Singleton
    abstract fun bindPaymentGateway(impl: StripePaymentGateway): PaymentGateway
}

// 📁 في موديول ':feature:checkout':
@HiltViewModel
class CheckoutViewModel @Inject constructor(
    private val paymentGateway: PaymentGateway // يعتمد على الواجهة فقط من :domain:payment!
) : ViewModel()
// موديول :app يقوم بتجميع PaymentDataModule وحقنه تلقائياً في CheckoutViewModel!
```

## Why it matters and how it works

Generated DI components collect reachable binding declarations for an app variant. Gradle compile visibility therefore shapes graph completeness. Scopes cache objects for component lifetimes, so a binding declared in one module can still be wrong if it owns a shorter-lived Android object. A contract module permits features to compile independently of the implementation chosen by the app.

## Worked example

Catalog feature depends on `CatalogRepository` API; `:data:catalog` binds `RealCatalogRepository` and app includes both. The binding is installed in a component matching its stateful lifetime, and tests replace it with an in-memory fake. A debug variant with a fake API client and release with real client each assemble successfully. An on-demand scanner uses a documented bridge instead of assuming base Hilt knows its classes.

## Trade-offs and decision criteria

Bindings near implementations make ownership clear; app-level selection supports multiple implementations but can grow a composition file. Too many broad modules/qualifiers make graph diagnostics hard. Hilt gives compile-time errors for many missing/duplicate bindings but cannot catch every semantic lifecycle leak.

## Failure modes

Implementation module absent from app variant produces a missing binding. Two unqualified bindings collide. A Singleton provider captures an Activity. Dynamic feature declares a Hilt binding that base compilation cannot aggregate. Tests use a fake binding that differs in qualifier from production.

## Production perspective

Maintain an injection graph inventory of contract, binding module, qualifier, scope and variants. Run app assembly, graph smoke tests and test binding replacement in CI; review module edge changes with DI owners.

## Interview answer — short

Manage multi-module DI by keeping interfaces in domain/api modules, implementations and @InstallIn Hilt binding modules in data/impl modules, and letting the :app module aggregate the graph at compile time. Feature modules inject interfaces without depending on implementation modules.

## Interview answer — structured

Managing dependency injection cleanly in a multi-module architecture relies on Hilt's decentralized compilation model:

1. **Contract Definition**: Domain and API modules define pure interfaces (e.g. `AuthRepository`) without depending on Hilt or Android frameworks.

2. **Implementation & Module Packaging**: Data and implementation modules contain the concrete class with an `@Inject constructor`. Alongside the implementation, the module includes a Hilt `@Module` annotated with `@InstallIn(SingletonComponent::class)` using `@Binds` to bind the interface to the concrete class.

3. **Consumer Decoupling**: Feature modules inject the interface into their `@HiltViewModel` constructors, depending only on the interface module. They have zero compile-time dependencies on the implementation module.

4. **Root Aggregation**: The `:app` module aggregates all implementation modules at compile time, resolving the full Dagger graph with zero manual component wiring.

## Interview answer — deep senior

A critical pitfall in multi-module DI is **Accidental Dependency Leakage via Hilt Aggregation**.

Because Hilt aggregates modules across the entire classpath of `:app`, if two feature modules accidentally bind the same interface without qualifiers, Dagger fails at the root `:app` compilation level with a `DuplicateBindingException`, even though both feature modules compiled individually without errors!

Furthermore, for **Dynamic Feature Modules (Play Feature Delivery)**, standard Hilt `@InstallIn` cannot be resolved because `:app` does not depend on dynamic feature modules. To provide dependencies into dynamic features, developers must use `@EntryPoint` to explicitly retrieve base graph dependencies from the `applicationContext`.

## How to answer in the interview

- **Why:** DI graph must match module graph.
- **How:** expose bindings through correct dependency direction.
- **Trade-off:** convenience versus scope complexity.
- **Failure case:** dynamic feature missing Hilt binding.
- **Production solution:** compile graph and runtime feature test.

## Deep-dive talking points

Discuss contracts, aggregation, variant graph, qualifiers, scope, dynamic feature bridge and smoke tests.

## Follow-up questions

- **Interviewer:** "Can a Hilt module in a library module be installed in `ActivityComponent`?"
  **Answer:** "Yes. `@InstallIn(ActivityComponent::class)` works in any library module, scoping those dependencies to Activities in the consuming application."

- **Interviewer:** "How do you test a feature module's ViewModel in isolation without compiling the whole Hilt graph?"
  **Answer:** "In JVM unit tests, bypass Hilt completely. Instantiate the ViewModel directly using its constructor and pass a Fake implementation of the interface."

## Self-check rubric

Draw binding visibility, choose scope and qualifier, and test one normal and one dynamic feature path.

## References and reviewed-on date

- [Hilt in multi-module apps](https://developer.android.com/training/dependency-injection/hilt-multi-module) — visibility and dynamic features.
- [Hilt on Android](https://developer.android.com/training/dependency-injection/hilt-android) — scopes and modules.

Technically reviewed against primary documentation on 2026-10-13.
