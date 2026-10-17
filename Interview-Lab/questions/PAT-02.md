---
id: "PAT-02"
question: "Compare creational, structural, and behavioral patterns."
topic: "Design Patterns"
code: "PAT"
group: "A"
phase: 2
priority: "P1"
order: 193
editorial_status: "reviewed"
---

# PAT-02

## Original interview question

Compare creational, structural, and behavioral patterns.

## What the interviewer evaluates

Classify patterns by intent and give discriminating examples, not just memorized lists.

## Concept and technical explanation

The Gang of Four design patterns are fundamentally categorized into creational, structural, and behavioral classifications based on their underlying architectural intent. Creational patterns (such as Singleton, Factory Method, Abstract Factory, and Builder) abstract and manage object instantiation mechanisms, decoupling systems from how objects are created, configured, and represented in memory. Structural patterns (such as Adapter, Facade, Decorator, and Proxy) address class and object composition, establishing flexible interfaces and transparent wrappers that enable disparate types to collaborate cleanly. Behavioral patterns (such as Observer, Strategy, State, Command, and Chain of Responsibility) govern algorithmic execution, responsibility assignment, and communication protocols between collaborating components without tightly coupling senders and receivers.

## Practical walkthrough (English)

Categorizing pattern archetypes across Android engineering:
```kotlin
// 1. CREATIONAL PATTERN: Factory Method / Builder
class NetworkClient private constructor(val baseUrl: String, val timeoutMs: Long) {
    class Builder { // Creational: Safely configures and instantiates complex objects
        var baseUrl: String = ""
        var timeoutMs: Long = 10_000
        fun build() = NetworkClient(baseUrl, timeoutMs)
    }
}

// 2. STRUCTURAL PATTERN: Adapter Pattern
interface ModernCryptoEngine { fun encrypt(data: ByteArray): ByteArray }
class LegacyJavaCipherWrapper(private val cipher: javax.crypto.Cipher) : ModernCryptoEngine {
    // Structural: Adapts legacy imperative API to modern contract
    override fun encrypt(data: ByteArray): ByteArray = cipher.doFinal(data)
}

// 3. BEHAVIORAL PATTERN: Strategy Pattern
interface RetryPolicy { fun nextDelayMs(attempt: Int): Long } // Behavioral: Swappable algorithm
class ExponentialBackoff : RetryPolicy {
    override fun nextDelayMs(attempt: Int): Long = (1000L * (1 shl attempt)).coerceAtMost(30_000L)
}
```

## Explanation in Arabic

المقارنة بين فئات أنماط التصميم الثلاث (Gang of Four): الإنشائية (Creational)، الهيكلية (Structural)، والسلوكية (Behavioral):

1. الأنماط الإنشائية (Creational Patterns):
   - **الهدف**: التحكم في **كيفية إنشاء الكائنات وإدارتها** دون ربط الكود بتفاصيل الـ new المباشرة.
   - **أمثلة شهيرة في أندرويد**:
     * **Singleton**: نسخة واحدة فقط في الذاكرة (`object` في كوتلن، Room Database).
     * **Factory / Abstract Factory**: إنشاء كائنات من عائلة معينة دون تحديد كلاساتها الملموسة (`ViewModelProvider.Factory`).
     * **Builder**: بناء كائنات معقدة خطوة بخطوة (`NotificationCompat.Builder`, `AlertDialog.Builder`).

2. الأنماط الهيكلية (Structural Patterns):
   - **الهدف**: تنظيم **العلاقات والتركيب بين الكلاسات والكائنات** لتكوين هياكل أكبر وأكثر مرونة.
   - **أمثلة شهيرة في أندرويد**:
     * **Adapter**: التوفيق بين واجهتين غير متوافقتين (`RecyclerView.Adapter`).
     * **Facade**: توفير واجهة بسيطة وموحدة لنظام معقد أو SDK خارجي.
     * **Decorator**: إضافة سلوك لكائن ديناميكياً دون وراثة (`OkHttp Interceptor`).
     * **Proxy**: التحكم في الوصول لكائن آخر (مثل Binder IPC في نظام أندرويد).

3. الأنماط السلوكية (Behavioral Patterns):
   - **الهدف**: تنظيم **طرق التواصل وتوزيع المسؤوليات وتدفق البيانات** بين الكائنات.
   - **أمثلة شهيرة في أندرويد**:
     * **Observer**: مراقبة تغيرات البيانات والتفاعل معها (`Flow`, `LiveData`, `StateFlow`).
     * **Strategy**: تبديل الخوارزميات وطرق المعالجة في وقت التشغيل (طرق الدفع).
     * **State**: تغيير سلوك الكائن عند تغير حالته الداخلية (آلة حالات المشغل).
     * **Chain of Responsibility**: تمرير الطلب عبر سلسلة معالجات (`OkHttp Interceptor Chain`).

## Practical walkthrough

أمثلة تمثل الفئات الثلاث في كود Android:
```kotlin
// 1. CREATIONAL: Builder Pattern لبناء إشعار معقد بأمان:
val notification = NotificationCompat.Builder(context, CHANNEL_ID)
    .setContentTitle("Order Shipped")
    .setSmallIcon(R.drawable.ic_truck)
    .setAutoCancel(true)
    .build()

// 2. STRUCTURAL: Facade Pattern لتبسيط SDK خرائط معقد خلف واجهة بسيطة:
class LocationTrackerFacade(private val fusedClient: FusedLocationProviderClient) {
    suspend fun getFreshCoordinates(): Coordinates = ...
}

// 3. BEHAVIORAL: Observer Pattern لمراقبة تغيرات تدفق البيانات:
viewModel.userFlow
    .onEach { user -> renderProfile(user) }
    .launchIn(lifecycleScope)
```

## Why it matters and how it works

The taxonomy helps choose a starting family: construction, composition/interface shaping, or changing behavior and communication. The same feature may use several categories at distinct boundaries. Intent and consequence matter more than a pattern name.

## Worked example

Scenario: SDK needs complex configuration, so Builder creates a client (creational). A wrapper converts its callback to a domain result (Adapter, structural). Checkout chooses card or wallet route (Strategy, behavioral). UI observes repository state (Observer-like behavior).

## Trade-offs and decision criteria

Categorization is a navigation aid, not an implementation rule. A factory can hide an SDK while a strategy selects behavior; do not confuse them because both may appear in provider routing. Patterns add indirection if simple language constructs suffice.

## Failure modes

A class named `PaymentFactory` contains SDK calls, retry policy and UI navigation; the name “creational” cannot excuse mixed concerns. Separate construction/selection from provider behavior and UI state.

## Production perspective

A multi-provider app uses Hilt for construction, adapters for vendor APIs, strategies for provider behavior and observable state for UI. Contract tests verify semantics across each boundary.

## Interview answer — short

Creational patterns abstract object instantiation to decouple creation from execution, such as Builder and Factory. Structural patterns organize classes and interfaces into cohesive compositions and wrappers, such as Adapter and Facade. Behavioral patterns govern communication protocols, state transitions, and interchangeable algorithms between collaborating objects, such as Observer and Strategy. Each category solves a fundamentally distinct dimension of software design.

## Interview answer — structured

The classification of design patterns into creational, structural, and behavioral categories is based on the specific dimension of software construction each addresses.
Creational patterns focus on the mechanics of object creation. In complex applications, hardcoding direct constructor calls creates rigid coupling to concrete classes and complicates lifecycle management. Creational patterns like Factory Method, Abstract Factory, and Builder encapsulate instantiation logic, allowing the system to determine what gets instantiated, who instantiates it, and how it is configured without exposing creation internals to consumers.
Structural patterns focus on composition and relationships between classes. They solve interface mismatches and manage subsystem complexity by creating wrappers, proxies, or composite trees. For instance, the Adapter pattern allows incompatible classes to work together, while the Facade pattern provides a simplified entry point to a complex subsystem.
Behavioral patterns focus on communication and the distribution of responsibilities. They decouple objects that request actions from the objects that execute them. Patterns like Observer, Strategy, and State model dynamic interactions, event propagation, and swappable algorithms, ensuring that state transitions and behavioral changes occur without rigid mutual dependencies.

## Interview answer — deep senior

Under the hood, these three categories operate at distinct phases of an object's lifecycle in memory: creational patterns control allocation and initial graph wiring; structural patterns define memory layouts, delegation wrappers, and interface dispatch tables; behavioral patterns govern runtime message dispatch and state mutations.
In modern Android development using Kotlin, language features have fundamentally reshaped how these categories are implemented. Many classic creational patterns like Builder are rendered obsolete by Kotlin's named arguments and default parameter values. Dependency injection frameworks like Hilt handle creational lifecycles natively, replacing manual factories with compile-time Directed Acyclic Graphs.
For structural patterns, Kotlin's class delegation by-interface (class LoggingList(inner: List) : List by inner) provides first-class language support for the Decorator pattern without manual forwarding boilerplate.
For behavioral patterns, higher-order functions and lambdas frequently replace single-method Strategy interfaces, while Kotlin Coroutines and Flow serve as the definitive standard for the Observer pattern across reactive presentation layers.
Staff engineers select patterns based on architectural friction rather than textbook dogma. If a problem is creational, they delegate to Hilt. If it is structural, they isolate third-party SDKs behind Facades and Adapters. If it is behavioral, they leverage reactive UDF state machines. Furthermore, Kotlin value classes and sealed hierarchies allow modern behavioral patterns to represent distinct domain states with zero runtime memory allocation overhead, combining compile-time safety with superior heap efficiency on Android runtimes.

## How to answer in the interview

- **Why:** Categories describe different design pressures, not required class counts.
- **How:** Use Builder, Adapter and Strategy in one checkout flow.
- **Trade-off:** Prefer constructor/direct call when no construction or interface problem exists.
- **Failure case:** Pattern taxonomy turns into unnecessary wrappers.
- **Production solution:** Tie each pattern to validation, SDK isolation, or behavior variation tests.

## Deep-dive talking points

Classify Builder, Adapter, Strategy and Observer in one checkout flow; note overlapping roles.

## Follow-up questions

- **Interviewer:** "How do Kotlin default arguments reduce the need for the Builder pattern?"
  **Answer:** "Data classes with default parameter values and named arguments allow instantiating objects with any combination of optional parameters directly in a single call, eliminating the need for separate Builder classes for basic data structures."

- **Interviewer:** "Which category does OkHttp's Interceptor mechanism belong to?"
  **Answer:** "It combines both Structural (Decorator pattern, wrapping requests/responses) and Behavioral (Chain of Responsibility pattern, passing the request through the interceptor pipeline)."

## Self-check rubric

Classify four named patterns by problem, then reject one unnecessary factory in a simple case.

## References and reviewed-on date

- [Kotlin object declarations](https://kotlinlang.org/docs/object-declarations.html) — language-level Singleton example.
- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — original taxonomy and catalog.

Technically reviewed against primary documentation on 2026-10-13.
