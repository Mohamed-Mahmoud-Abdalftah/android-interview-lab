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

## Concept and technical explanation

Creational patterns abstract the instantiation process to make systems independent of how their collaborating objects are created, composed, and represented. Singleton restricts class instantiation to a single shared instance per process or scope, providing a global point of access. Factory Method defines an interface for creating an object while allowing implementing subclasses or providers to decide the concrete class instantiated. Abstract Factory elevates this abstraction by providing an interface for creating families of related or dependent objects without specifying their concrete classes. Builder separates the step-by-step construction of a complex object from its internal representation, allowing the identical construction process to yield different representations and immutable instances.

## Practical walkthrough (English)

Comparing Creational Patterns in modern Kotlin and Android:
```kotlin
// 1. SINGLETON: Process-wide single instance (via Kotlin object or Hilt @Singleton)
@Singleton
class InMemoryTokenStore @Inject constructor() {
    private var token: String? = null
    fun saveToken(newToken: String) { token = newToken }
}

// 2. FACTORY METHOD: Encapsulates creation of a specific interface variant
interface AnalyticsTracker { fun log(event: String) }
class FirebaseTracker : AnalyticsTracker { override fun log(event: String) {} }

class TrackerFactory @Inject constructor() {
    fun create(isProd: Boolean): AnalyticsTracker = 
        if (isProd) FirebaseTracker() else ConsoleTracker()
}

// 3. ABSTRACT FACTORY: Creates families of related products
interface DialogThemeFactory {
    fun createButton(context: Context): Button
    fun createHeader(context: Context): TextView
}
class Material3DialogThemeFactory : DialogThemeFactory {
    override fun createButton(context: Context) = MaterialButton(context)
    override fun createHeader(context: Context) = TextView(context).apply { textSize = 20f }
}

// 4. BUILDER: Step-by-step construction of complex immutable objects
class NotificationRequest private constructor(
    val title: String,
    val body: String,
    val channelId: String
) {
    class Builder(private val title: String) {
        var body: String = ""
        var channelId: String = "default"
        fun setBody(text: String) = apply { this.body = text }
        fun build() = NotificationRequest(title, body, channelId)
    }
}
```

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

Singleton guarantees a single shared instance throughout a defined lifecycle. Factory Method encapsulates object instantiation behind a method to decouple callers from concrete classes. Abstract Factory provides an interface to create families of related objects without binding to concrete implementations. Builder constructs complex objects incrementally through step-by-step parameterization, ensuring immutability upon completion. Each creational pattern targets a distinct creation complexity.

## Interview answer — structured

Creational patterns provide structured strategies for managing object construction while preserving loose coupling.
The Singleton pattern ensures that a class has exactly one instance and provides a centralized access point. In Kotlin, this can be declared via the object keyword or managed via Hilt's @Singleton scope. Singletons are appropriate for state-free or thread-safe shared resources like Room databases or token caches, though indiscriminate usage introduces global state and testing pollution.
The Factory Method pattern defines a method for object creation, allowing the instantiation logic to vary independently from the client that uses the object. It decouples the caller from concrete subclasses, enabling dynamic runtime decisions based on configuration or environment.
The Abstract Factory pattern extends this concept to families of related objects. Instead of creating a single product, an Abstract Factory exposes multiple creation methods that yield consistent, coordinated components, such as platform-specific UI widgets or environment-specific encryption engines.
The Builder pattern solves the telescoping constructor problem. When an object requires numerous configuration parameters, optional properties, or validation rules before becoming valid, a Builder constructs the object step-by-step, producing an immutable, fully-validated instance at the terminal build invocation.

## Interview answer — deep senior

Under the hood, these creational patterns directly influence memory layout, thread synchronization, and class-loading dynamics.
In traditional Java, Singleton required complex Double-Checked Locking with volatile fields to guarantee thread safety without synchronization bottlenecks. In Kotlin, the object keyword implements lazy thread-safe initialization via static JVM initialization blocks. However, staff engineers prefer dependency-injected singletons managed by Hilt's SingletonComponent, because framework scoping allows unit tests to substitute lightweight fakes easily, whereas static JVM singletons cannot be reset without reflection.
Factory and Abstract Factory patterns govern dynamic dispatch. By returning an abstract interface rather than a concrete class, these patterns introduce a layer of virtual method table indirection. While this carries negligible CPU overhead, the architectural gain is massive: it enables strict modularization where feature modules declare contracts and factories while concrete implementations reside in hidden internal modules.
Regarding Builder, senior engineers recognize that Kotlin's language features diminish its necessity for internal data models. Default arguments and named parameters in data classes provide clean, readable construction with compile-time validation. However, the Builder pattern remains critical in public SDK design, Java interoperability layers, and complex framework configurations like OkHttpClient and Retrofit where validation logic must execute atomically across multiple interrelated properties before instance emission.

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
