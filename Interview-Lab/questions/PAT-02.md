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

Creational patterns govern object instantiation (Singleton, Factory, Builder). Structural patterns govern class and object composition to form larger systems (Adapter, Facade, Decorator). Behavioral patterns govern communication algorithms and responsibility distribution between collaborating objects (Observer, Strategy, State).

## Interview answer — structured

The Gang of Four (GoF) classifies design patterns into three distinct categories based on their intent.

First, **Creational Patterns (Object Instantiation Mechanisms)**. Next, abstract the instantiation process, making systems independent of how objects are created, composed, and represented.
*Android Examples*. With Singleton, single shared instance (`object`, Room database instance).
With Builder, multi-step configuration of immutable objects (`NotificationCompat.Builder`, `AlertDialog.Builder`). With Factory Method, delegating instantiation to subclasses or providers (`ViewModelProvider.Factory`).
**Structural Patterns (Composition & Relationships)**. Deal with how classes and objects are assembled into larger, decoupled structures.
*Android Examples*. With Adapter, converts one interface into another that clients expect (`RecyclerView.Adapter`).
With Facade, exposes a simplified, cohesive API over a complex underlying subsystem (wrapping multi-step third-party SDKs). With Decorator, dynamically augments behavior without subclassing (`OkHttp Interceptors`).
**Behavioral Patterns (Communication & Algorithms)**. Deal with algorithms, assignments of responsibility, and communication protocols between objects.
*Android Examples*. With Observer, publish-subscribe reactive notifications (`StateFlow`, `SharedFlow`, `LiveData`).
With Strategy, encapsulating interchangeable algorithms selected at runtime (Payment providers, sorting algorithms). Finally, with Chain of Responsibility, passing a request along a chain of handlers (`OkHttp Interceptor Chain`).


## Interview answer — deep senior

Modern Kotlin has absorbed several GoF patterns directly into language syntax.

First, with Singleton, native `object` keyword. Next, with Decorator / Adapter, first-class **Class Delegation** (`class Foo(bar: Bar) : Bar by bar`) and **Extension Functions**.
Additionally, with Strategy, passing higher-order functions or lambdas (`(T) -> Boolean`) directly instead of creating single-method interface hierarchies. Finally, with Builder, named parameters and default arguments (`data class Config(val timeout: Long = 5000, val retries: Int = 3)`).

Understanding which patterns are native language idioms versus structural components helps engineers write cleaner code without unnecessary boilerplate classes.


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
