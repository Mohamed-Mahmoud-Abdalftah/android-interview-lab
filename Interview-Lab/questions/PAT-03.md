---
id: "PAT-03"
question: "Explain Singleton, Factory, Abstract Factory, and Builder."
topic: "Design Patterns"
code: "PAT"
group: "A"
phase: 2
priority: "P1"
order: 194
editorial_status: "reviewed"
---

# PAT-03

## Original interview question

Explain Singleton, Factory, Abstract Factory, and Builder.

## What the interviewer evaluates

Contrast one shared instance, object selection, related-family construction, and staged configuration.

## Explanation in Arabic

شرح الأنماط الإنشائية الأساسية: Singleton و Factory و Abstract Factory و Builder، ومتى نستخدم كلاً منها في Android:

1. نمط الكائن الأحادي (Singleton Pattern):
   - **الهدف**: ضمان وجود **نسخة واحدة فقط** من الكائن في الذاكرة طوال حياة التطبيق وتوفير نقطة وصول عامة له.
   - **في Kotlin**: يُبنى بكلمة `object` أو عبر `@Singleton` في Hilt.
   - **الاستخدام**: قواعد بيانات Room، عميل Retrofit/OkHttp، ومدير الـ Analytics.

2. نمط المصنع (Factory Method Pattern):
   - **الهدف**: تفويض إنشاء الكائن إلى دالة أو كلاس مصنع بدلاً من استدعاء الـ Constructor المباشر.
   - **في Android**: `ViewModelProvider.Factory` لإنشاء كائنات ViewModel تحتاج لمعاملات في الـ Constructor.

3. نمط المصنع المجرد (Abstract Factory Pattern):
   - **الهدف**: مصنع للمصانع! إنشاء **عائلات كاملة من الكائنات المرتبطة** دون تحديد كلاساتها الملموسة.
   - **الاستخدام**: عائلة مكونات واجهة تختلف حسب الثيم (DarkUIFactory ينشئ DarkButton و DarkDialog، بينما LightUIFactory ينشئ LightButton و LightDialog).

4. نمط الباني (Builder Pattern):
   - **الهدف**: بناء كائنات معقدة تحتوي على العديد من المعاملات الاختيارية خطوة بخطوة وتأكيد بنائها في النهاية بـ `.build()`.
   - **في Android**: `NotificationCompat.Builder`, `AlertDialog.Builder`, `OkHttpClient.Builder`.

## Practical walkthrough

أمثلة كود توضح الأنماط الإنشائية الأربعة في Android:
```kotlin
// 1. SINGLETON (عبر Hilt أو object):
@Singleton
class AppDatabaseManager @Inject constructor(@ApplicationContext context: Context) { ... }

// 2. FACTORY METHOD: مصنع لإنشاء كائنات من نوع محدد بناءً على إدخال:
interface PaymentGatewayFactory {
    fun create(type: PaymentType): PaymentGateway
}

// 3. ABSTRACT FACTORY: مصنع لعائلات كائنات مرتبطة:
interface UIThemeFactory {
    fun createButton(): AppButton
    fun createDialog(): AppDialog
}
class DarkThemeFactory : UIThemeFactory { ... }
class LightThemeFactory : UIThemeFactory { ... }

// 4. BUILDER: بناء كائن OkHttpClient بإعدادات متعددة:
val client = OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(30, TimeUnit.SECONDS)
    .addInterceptor(AuthInterceptor())
    .build()
```

## Why it matters and how it works

Each creational pattern addresses a different construction problem. Singleton controls instance count within an owner; factory selects type; abstract factory maintains consistency across a family; builder manages complex configuration. None guarantees business correctness or durable state.

## Worked example

Example: `object CurrencyCodes` holds stateless constants; `PaymentRouteFactory` selects a provider adapter; an `EnvironmentFactory` could create matching API and serializer for sandbox/production; an OkHttp-style builder configures timeouts/interceptors before creation. These are conceptual roles, not an instruction to implement all four.

## Trade-offs and decision criteria

A constructor is best when creation is simple. Factories and builders add names and indirection but can enforce invariants. A global singleton is convenient but hard to reset in tests and risky for mutable state. Hilt scopes may replace manual singleton wiring.

## Failure modes

A process-wide `object Session` stores `isLoggedIn = true` and is treated as source of truth. Process death resets it; token expiry can make it stale. Use repository/persistence and server validation. Another failure is a Builder that allows `build()` with missing required endpoint.

## Production perspective

A networking module uses DI-managed client construction with validated config, while session status remains repository-backed. Integration tests verify correct environment family and timeouts.

## Interview answer — short

Singleton ensures a single shared instance (Room DB, OkHttp). Factory creates single objects hiding instantiation logic (`ViewModelProvider.Factory`). Abstract Factory creates families of related objects (Theme components). Builder constructs complex multi-parameter objects step-by-step (`NotificationCompat.Builder`).

## Interview answer — structured

These four creational patterns govern object creation boundaries in Android development:

1. **Singleton**: Guarantees a class has only one instance per process lifecycle. In Kotlin, implemented natively via `object` or managed via `@Singleton` in Dagger/Hilt. Best for expensive, stateful shared resources (e.g. SQLite connection pools, OkHttp client engines).

2. **Factory Method**: Defines an interface for creating an object, but lets subclasses or specialized providers decide which class to instantiate. In Android, `ViewModelProvider.Factory` creates ViewModels parameterized with dependencies that standard system reflection cannot resolve.

3. **Abstract Factory**: Provides an interface for creating **families of related or dependent objects** without specifying their concrete classes. For instance, a `DesignSystemFactory` supplying matching typography, buttons, and dialogs tailored for distinct brand flavors (e.g. `ConsumerThemeFactory` vs `EnterpriseThemeFactory`).

4. **Builder**: Separates the construction of a complex object from its representation, allowing step-by-step assembly and producing an immutable result via `.build()`. Ubiquitous across Android framework APIs (`NotificationCompat.Builder`, `AlertDialog.Builder`, `WorkRequest.Builder`).

## Interview answer — deep senior

The **Builder Pattern vs Kotlin Named Arguments** trade-off is a frequent design debate. For simple domain data classes, a builder is an anti-pattern in Kotlin: `data class UserConfig(val timeout: Long = 10, val retries: Int = 3)` provides built-in validation and optionality in a single line.

However, the Builder pattern remains vital in SDK design when:
- Construction requires cross-field validation invariants checked at commit time (`build()`).
- Step order matters or certain combinations are mutably staged before creating an immutable thread-safe core (e.g. `OkHttpClient.Builder`).
- Java interoperability is required, as Java cannot consume Kotlin default argument bytecode ergonomically without `@JvmOverloads`.

## How to answer in the interview

- **Why:** Each creational pattern solves a different construction or lifetime constraint.
- **How:** Contrast `object`, one-product factory, compatible-family factory and validated builder.
- **Trade-off:** Direct constructor beats Builder for a small fixed input set.
- **Failure case:** Global session Singleton leaks state or outlives the account.
- **Production solution:** Scope providers correctly and test environment/account transitions.

## Deep-dive talking points

Compare construction intent, instance lifetime, related product families, validation and Hilt scope.

## Follow-up questions

- **Interviewer:** "Why can global Singleton objects cause issues in unit tests?"
  **Answer:** "Global singletons retain state across test runs, causing tests to become order-dependent and flaky. We mitigate this by scoping singletons via Hilt components that are recreated per test."

- **Interviewer:** "What is the difference between Factory and Abstract Factory?"
  **Answer:** "Factory Method creates a single product. Abstract Factory is a factory of factories, creating an entire suite of related products that belong to the same family or theme."

## Self-check rubric

Choose among constructor, factory, abstract factory and builder for four cases; identify a singleton lifecycle risk.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — creational patterns.
- [Kotlin object declarations](https://kotlinlang.org/docs/object-declarations.html) — Kotlin singleton syntax.

Technically reviewed against primary documentation on 2026-10-13.
