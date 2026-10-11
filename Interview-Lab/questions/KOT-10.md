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

Contrast deferred read-only initialization with deferred mutable assignment and identify lifecycle misuse.

## Explanation in Arabic

`lazy` delegate لـ`val` بيحسب القيمة أول مرة تتقري، وبيخزنها بعدها؛ افتراضيًا `LazyThreadSafetyMode.SYNCHRONIZED` بيضمن نشرها مرة واحدة بين threads، وفيه modes تانية لو السياق يبرر. `lateinit` ينفع لـnon-null `var` مناسب النوع، يتسند بعد البناء؛ القراءة قبل التهيئة ترمي `UninitializedPropertyAccessException`. الاتنين مش حل عام لتأجيل dependency design. في Android، `lazy` ممكن يمسك View من Activity قديمة لو الـowner طويل العمر، و`lateinit` ممكن يفشل بعد lifecycle transition.

## Why it matters and how it works

These constructs address different initialization constraints. `lazy` owns the initializer and computes on first access; `lateinit` requires a later explicit assignment. Thread-safety mode and lifecycle ownership matter more than saving a few constructor lines.

## Worked example

JVM illustration; one property computes once, the other must be assigned before read.
```kotlin
class ParserHolder {
    val parser: Regex by lazy { Regex("[A-Z]+") }
    lateinit var label: String
}
fun main() {
    val holder = ParserHolder()
    holder.label = "Ready"
    println(holder.parser.matches("ABC") && holder.label == "Ready")
}
```

## Trade-offs and decision criteria

Prefer constructor injection when a dependency is required immediately. `lazy` is useful for an expensive optional value; its synchronized mode has small coordination cost. `lateinit` fits framework-driven assignment, such as test setup or view binding inside a controlled lifecycle, but nullable property plus explicit state may be clearer.

## Failure modes

An Activity stores binding in `lateinit` and accesses it before `onCreate` or after the View lifecycle ends; this crashes or leaks. In fragments, clear view binding in `onDestroyView` or use a lifecycle-aware binding pattern. Never use `LazyThreadSafetyMode.NONE` for shared cross-thread access.

## Production perspective

A repository lazily builds a rarely used parser with a stable application-scoped owner. A Fragment binding is created and cleared with the view lifecycle rather than kept in a process singleton. Tests include access order and recreation behavior.

## Interview answer — short

`lazy` initializes a `val` on first access and caches it; `lateinit` lets a non-null `var` be assigned later. `lateinit` throws if read before assignment. I choose based on who performs initialization and the object’s lifecycle.

## Interview answer — structured

With `lazy`, I supply the initializer and the value is computed on first read, normally once under the default synchronized mode. With `lateinit`, some later code must assign a non-null property before use. I prefer constructor injection for required dependencies and use these tools only when deferral has a reason. On Android I check that the owner does not outlive the View or Activity it holds. If I can construct a dependency at object creation, constructor injection is usually clearer. If an expensive parser is optional, `lazy` lets me defer it until needed and caches it. For Android view references I tie storage to the view lifecycle rather than a longer-lived singleton.

## Interview answer — deep senior

The key questions are initialization timing, publication across threads, and cleanup. `lazy` delegates value creation and caching; alternative thread-safety modes change guarantees. `lateinit` expresses a mutable initialization gap and can be checked with `::property.isInitialized` where visible, but that is not a replacement for a sound lifecycle. In a Fragment, view-scoped resources must be cleared when the view is destroyed. For dependency injection, constructor parameters are clearer when the object cannot function without the dependency. `lazy` and `lateinit` solve different problems. A `lazy val` owns an initializer and computes on first read; the default mode synchronizes initialization, while other modes trade guarantees for overhead. The cached value may still be mutable, so lazy initialization does not make later operations thread-safe. A `lateinit var` has no initializer and must be assigned before access, otherwise Kotlin throws `UninitializedPropertyAccessException`. It is limited to suitable non-null property types and can be checked for initialization in the right scope, but that is a symptom check rather than a lifecycle design. In a Fragment, a binding belongs to the View lifetime, which may end before the Fragment itself. Required dependencies are better supplied through the constructor.

## Deep-dive talking points

Discuss `LazyThreadSafetyMode`, exception retry semantics, allowed `lateinit` types, and Android Fragment view lifecycle.

## Follow-up questions

- [KOT-02](../kot-02/): Is a `lazy val` deeply immutable? **Answer:** no; the cached object may itself be mutable.
- [KOT-25](../kot-25/): Does lazy initialization make subsequent mutations safe? **Answer:** no; only initialization publication is addressed by a suitable mode.

## Self-check rubric

Explain which construct owns initialization, predict an early `lateinit` read, and identify one lifecycle and one thread-safety risk.

## References and reviewed-on date

- [Kotlin delegated properties](https://kotlinlang.org/docs/delegated-properties.html) — lazy delegation.
- [Kotlin properties](https://kotlinlang.org/docs/properties.html) — `lateinit` semantics.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.
