---
id: "KOT-10"
question: "Compare lazy and lateinit. When is each appropriate?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "A"
phase: 1
priority: "P1"
order: 10
editorial_status: "reviewed"
---

# KOT-10

## Original interview question

Compare lazy and lateinit. When is each appropriate?

## What the interviewer evaluates

Explain who initializes the value, when it becomes available, the mutability and type restrictions, lazy thread-safety modes, and the Android lifecycle case where neither construct should own a View reference indefinitely.

## Concept and technical explanation

`val value by lazy { ... }` gives a read-only property a delegate that runs its initializer on first access and caches the result. The default `SYNCHRONIZED` mode publishes one initialized value safely across threads. `PUBLICATION` may run the initializer more than once concurrently but publishes one result, so side effects in that initializer need care. `NONE` provides no thread-safety guarantee; use it only when all access is confined to one thread. A lazy value remains held by its owner until that owner is released, so it is not a lifecycle cleanup mechanism.

`lateinit var value: Type` defers an explicit assignment to a non-null, non-primitive mutable property or local variable. Reading before assignment throws `UninitializedPropertyAccessException`. It cannot represent an intentionally cleared nullable state, and assigning a new value is allowed after initialization. `::property.isInitialized` is available only within the documented visibility and declaration scope; it checks state but does not replace lifecycle ownership. Prefer a constructor parameter for required dependencies when the constructor is under your control.

## Practical walkthrough (English)

A test fixture may use `lateinit var service` because setup assigns it before each test. A parser used rarely can be a `val by lazy` if its owner and thread access are clear. In a Fragment, a ViewBinding must be cleared in `onDestroyView()` because the Fragment may outlive its View. A `lateinit` binding cannot be reset to uninitialized, and a `lazy` binding would cache the old View. Use a nullable backing property or a well-tested view-lifecycle delegate.

## Explanation in Arabic

`val by lazy` معناها إن الـ Delegate هيشغّل Initializer عند أول قراءة ويحتفظ بالنتيجة؛ مناسب لقيمة Read-only مرتبطة بعمر الـ Owner. الوضع الافتراضي `SYNCHRONIZED` آمن للوصول المتزامن. `PUBLICATION` ممكن تشغّل Initializer أكتر من مرة لو Threads سبقت بعضها، لكن قيمة واحدة هي اللي تتنشر؛ لذلك ما أحطّش Side Effect حساس جوّاها. `NONE` مفيهاش ضمان Thread Safety، فأستخدمها فقط لو كل الوصول محصور في Thread واحدة.

`lateinit var` معناها إن حد هيسند قيمة صريحة بعد إنشاء الكائن. لازم النوع يكون Non-null وغير Primitive، ولو قريتها قبل الإسناد هترمي `UninitializedPropertyAccessException`. ممكن أعيد إسنادها، لكن ما أقدرش أرجعها لحالة «لسه ما اتعملتش» بـ `null`. `::property.isInitialized` يفحص التهيئة ضمن Scope مسموحة، لكنه مش حل لتنظيف Lifecycle. لو Dependency ضرورية والـ Constructor تحت سيطرتي، أمررها فيه غالبًا.

## Practical walkthrough

في Test Fixture، `lateinit var service` مناسبة لما `setup` هيسندها قبل كل Test. Parser نادر الاستخدام ممكن يبقى `val by lazy` لو عارف مين مالكه ومين هيقرأه. لكن ViewBinding في Fragment لازم يتشال مرجعها في `onDestroyView()` لأن الـ Fragment ممكن تعيش بعد الـ View. `lateinit` ما ينفعش أصفرها، و`lazy` هتخزن View قديمة. هنا أستخدم Nullable Backing Property أو Delegate مجرّبة مرتبطة بـ View Lifecycle.

## Why it matters and how it works

Both mechanisms defer work but have different owners. `lazy` computes and caches; `lateinit` waits for an external assignment. Thread safety and lifetime decide whether the value is still valid when read.

## Worked example

The standalone JVM example demonstrates first-access caching and a late assignment. It is compiled by the Kotlin lab.

```kotlin
class ParserHolder {
    var constructionCount = 0
        private set
    val parser: Regex by lazy {
        constructionCount++
        Regex("[A-Z]+")
    }
    lateinit var label: String

    fun labelReady(): Boolean = this::label.isInitialized
}

fun main() {
    val holder = ParserHolder()
    check(holder.constructionCount == 0 && !holder.labelReady())
    check(holder.parser.matches("ABC") && holder.parser.matches("XYZ"))
    check(holder.constructionCount == 1)
    holder.label = "Ready"
    check(holder.labelReady() && holder.label == "Ready")
}
```

## Trade-offs and decision criteria

`lazy` keeps the computed value for the owner's lifetime and has default synchronization cost. `NONE` removes synchronization guarantees, so confinement must be real. `lateinit` avoids a nullable type while introducing an initialization-order contract that can fail at runtime. Constructor injection is clearer for required inputs; nullable state is clearer when teardown must clear a reference.

## Failure modes

A Fragment stores its ViewBinding in `lateinit` without clearing it after `onDestroyView()`, retaining a destroyed View. A `lazy` binding caches that View across recreation. `PUBLICATION` runs a side-effecting initializer more than once under contention; `NONE` is accessed across threads despite no safety guarantee. An `isInitialized` check hides a broken setup path rather than fixing ownership.

## Production perspective

Check the owner and lifetime of each deferred property, then choose the simplest mechanism. Test access before setup, first-access caching and Fragment view recreation where applicable. Do not select `NONE` solely for a presumed micro-optimization; confirm thread confinement and measure a real cost first.

## Interview answer — short

`by lazy` is for a read-only `val`: it computes on first access and caches the result. `lateinit` is for a non-null, non-primitive `var` assigned later; reading before assignment throws. I use `lazy` when the owner should compute the value and `lateinit` when a framework or test setup assigns it. For Fragment ViewBinding, I need a clear-and-recreate pattern instead of keeping a cached View.

## Interview answer — structured

The key difference is ownership. With `val by lazy`, the property owns an initializer; the delegate runs it on first read and caches the value. Default `SYNCHRONIZED` mode is safe across threads. `PUBLICATION` can run the initializer more than once before one result wins, and `NONE` has no concurrency guarantee. I choose a mode based on actual access, not an assumed speedup.

With `lateinit var`, some later code assigns a non-null reference. It suits test setup or framework-driven field injection when constructor injection is unavailable. If I read it first, I get `UninitializedPropertyAccessException`. `::property.isInitialized` is a limited check, not a lifecycle strategy.

The Android trap is Fragment ViewBinding: the Fragment can remain while its View is destroyed and recreated. A `lateinit` binding cannot be reset to null, and a `lazy` binding can cache the old View. I use a nullable backing property cleared in `onDestroyView()` or a verified lifecycle delegate. For a required dependency in a class I construct myself, I normally prefer a constructor parameter.

## Interview answer — deep senior

`lazy` and `lateinit` both defer initialization but encode different contracts. A `Lazy<T>` delegate supplies and caches the value on the first read of a `val`. The cache remains attached to its owner; a `val` only prevents reassignment of the property, not mutation of the referenced object. By default `lazy` uses `SYNCHRONIZED`, which ensures one initializer execution and safe publication across threads. `PUBLICATION` may invoke the initializer several times concurrently and retain only one result, so an initializer with payments, writes or registration side effects is a poor fit. `NONE` makes no thread-safety promise, including visibility, so I use it only with demonstrated confinement.

`lateinit var` is a promise that code will assign a non-null, non-primitive value before any read. It can be reassigned, and an early read throws `UninitializedPropertyAccessException`. `::property.isInitialized` can help at a permitted declaration scope, but it does not turn the property into nullable state or fix incorrect initialization order. If the dependency is required and I control construction, a constructor parameter states the requirement more clearly.

In Android the lifetime question often matters more than the keyword. A Fragment instance can outlive its View. Binding held in `lateinit` cannot be cleared to null in `onDestroyView()`, while a `lazy` binding would cache a reference to a destroyed View. A nullable backing field cleared on view teardown makes the valid window explicit. I would test view recreation and access order, rather than assuming `isInitialized` makes it safe.

I would also keep performance claims proportionate. A rare first access is unlikely to justify `NONE` without a measured issue; synchronized mode is the default for a reason. I pick the mechanism from who initializes the value, who owns it, and how long that owner should retain it.

## How to answer in the interview

Compare initializer ownership, first-read versus later assignment, type restrictions, failure on early read, and thread-safety modes. Finish with the Fragment ViewBinding lifetime counterexample and a safe alternative.

## Deep-dive talking points

`SYNCHRONIZED`, `PUBLICATION`, `NONE`; first-read caching; `lateinit` early-read exception; `isInitialized` scope; View versus Fragment lifetime; constructor injection and nullable teardown.

## Follow-up questions

- **Interviewer:** "Can `PUBLICATION` call the initializer twice?"
  **Answer:** "Yes, concurrent first reads may run it more than once, although one value is published. I keep that initializer free of non-repeatable side effects."

- **Interviewer:** "Why not use `lateinit` for Fragment ViewBinding?"
  **Answer:** "The binding must be released when the View ends, but `lateinit` cannot be set to null. A nullable backing property cleared in `onDestroyView()` expresses the lifetime."

- **Interviewer:** "Does `isInitialized` make a property safe?"
  **Answer:** "It checks whether assignment has happened in permitted scope. It does not guarantee the value still belongs to the current lifecycle or that concurrent access is safe."

## Self-check rubric

Explain who initializes each property, show an early-read failure, distinguish the three lazy modes, and choose a binding pattern that survives Fragment view recreation.

## References and reviewed-on date

- [Kotlin delegated properties](https://kotlinlang.org/docs/delegated-properties.html) — first-read caching and lazy modes.
- [Kotlin properties](https://kotlinlang.org/docs/properties.html) — `lateinit` rules and `isInitialized` scope.
- [Kotlin `LazyThreadSafetyMode`](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/-lazy-thread-safety-mode/) — concurrency guarantees.
- [Android View Binding](https://developer.android.com/topic/libraries/view-binding#fragments) — clear Fragment binding in `onDestroyView()`.

Technically reviewed against the cited primary documentation on 2026-10-19; agent editorial review, not human verification.
