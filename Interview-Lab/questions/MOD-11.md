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

## Concept and technical explanation

Managing Dependency Injection (DI) across a multi-module Android project requires establishing clean component lifecycles and decoupling interface contracts from concrete implementations:
- Interface Contracts in API/Core: Public contracts and repository interfaces are declared in leaf-level API or core domain modules, completely decoupled from injection frameworks.
- Module Bindings: Feature implementation modules provide Hilt/Dagger modules (annotated with @Module @InstallIn(SingletonComponent::class) or ActivityRetainedComponent) that bind the concrete class to the interface via @Binds.
- Dynamic Features & EntryPoints: Because dynamic feature modules invert dependencies and cannot be processed by the standard monolithic Hilt component at compile time, they access dependencies on-demand via @EntryPoint interfaces resolved through EntryPoints.get(applicationContext, MyEntryPoint::class).
- Multibindings for Pluggable Architecture: Sets (@IntoSet) and maps (@IntoMap) allow independent modules to register navigation destinations, network interceptors, or background workers into the root application container without central coupling.

## Practical walkthrough (English)

Multi-module Hilt setup with interface binding and dynamic feature EntryPoints:
```kotlin
// 1. In :core:network (Interface contract)
interface TokenProvider {
    fun getAuthToken(): String?
}

// 2. In :feature:auth:impl (Implements and binds the contract)
class TokenProviderImpl @Inject constructor(private val sessionManager: SessionManager) : TokenProvider {
    override fun getAuthToken(): String? = sessionManager.token
}

@Module
@InstallIn(SingletonComponent::class)
abstract class AuthBindingModule {
    @Binds abstract fun bindTokenProvider(impl: TokenProviderImpl): TokenProvider
}

// 3. In :dynamic:feature (Consumes dependency via EntryPoint)
@EntryPoint
@InstallIn(SingletonComponent::class)
interface DynamicFeatureDependencies {
    fun tokenProvider(): TokenProvider
}

fun injectDynamicFeature(context: Context) {
    val deps = EntryPoints.get(context.applicationContext, DynamicFeatureDependencies::class.java)
    val token = deps.tokenProvider().getAuthToken()
}
```

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

Managing multi-module dependency injection requires declaring interfaces in api modules and providing bindings in implementation modules. Hilt aggregates these modules into the root app component during compilation. Dynamic feature modules retrieve dependencies at runtime using EntryPoints, while multibindings allow features to contribute navigation entries or interceptors into root collections without tight coupling.

## Interview answer — structured

Managing dependency injection in a multi-module Android architecture demands clean decoupling between interface contracts and concrete implementations.
We declare interfaces and repository contracts inside leaf-level api or domain modules, keeping them free of Android-specific implementation logic.
Inside the private implementation module, we write the concrete classes annotated with Inject constructor, alongside Hilt modules that bind the interface to the implementation using Binds.
During compilation, Hilt aggregates these distributed modules into the root application component in the app module.
For dynamic feature modules that invert Gradle dependencies, standard compile-time component injection is impossible.
Instead, dynamic modules define EntryPoint interfaces and retrieve dependencies on-demand at runtime using EntryPoints.get from the application context.
Furthermore, multibindings allow feature modules to contribute elements into shared sets, such as interceptors or navigation graphs, enabling a pluggable architecture.

## Interview answer — deep senior

In enterprise Android engineering, our dependency injection architecture mirrors the Directed Acyclic Graph of our Gradle subprojects.
When using Hilt and Dagger across dozens of modules, the greatest threat is leaky abstraction and circular dependency generation.
We prevent this by strictly separating where contracts are defined from where they are bound.
Interface contracts reside in leaf-level :api modules.
Concrete implementations live in :impl modules, utilizing constructor injection.
The Hilt binding module resides directly inside the :impl module, declaring an abstract Binds method installed in SingletonComponent.
Because Hilt uses bytecode manipulation and annotation processing to aggregate all installed modules into the root ApplicationComponent inside the :app module, :feature:cart never needs to know that TokenProvider is implemented by :feature:auth:impl; it simply injects the interface.
Dynamic delivery introduces a unique constraint: dynamic feature modules depend on :app rather than the reverse, preventing Hilt from compiling them into the root component.
To resolve this, dynamic features declare an EntryPoint interface specifying the required dependencies.
At runtime, the dynamic feature resolves the interface using EntryPoints.get passing the application context.
To extend capabilities further, we leverage Dagger Multibindings with IntoSet to construct pluggable architectures.
Feature modules contribute navigation routes or OkHttp interceptors into injected collections, allowing the core network or navigation coordinator to discover feature contributions without hardcoded dependencies in the root module.

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
