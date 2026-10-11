---
id: "KOT-05"
question: "Compare data class, regular class, object, and companion object."
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "A"
phase: 1
priority: "P1"
order: 5
editorial_status: "reviewed"
---

# KOT-05

## Original interview question

Compare data class, regular class, object, and companion object.

## What the interviewer evaluates

Choose among value carrier, behavior-bearing class, singleton, and class-level factory without conflating their lifetimes.

## Explanation in Arabic

`data class` مناسبة لقيم بيانات لها `equals/hashCode/toString/copy` مولّدين من الـprimary constructor. `class` عادية مناسبة لو الهوية، invariants، أو behavior أهم من نسخ القيمة. `object` singleton على مستوى الـclassloader لشيء واحد، مش مخزن global آمن لكل state. `companion object` عضو مرتبط بالـclass لتنظيم factory أو constants؛ مش static field مطابق تمامًا لـJava في كل interop حالة. `copy` shallow، فـmutable list جوا data class تفضل مشتركة.

## Why it matters and how it works

These declarations communicate different contracts. Generated data-class operations help immutable state. Ordinary classes encapsulate lifecycle and identity. An object offers one instance but can retain mutable global state. A companion groups creation logic and can implement interfaces.

## Worked example

JVM illustration: value model and validated factory.
```kotlin
data class Account(val id: String, val name: String)
class Session private constructor(val account: Account) {
    companion object {
        fun start(account: Account): Session = Session(account)
    }
}
object AccountIdFormat { fun valid(id: String) = id.isNotBlank() }
```

## Trade-offs and decision criteria

Use data class when all primary fields define value equality; use regular class for controlled identity or mutable invariants. `object` avoids duplicate instances but complicates state isolation and tests if it holds mutable data. Companion factories are discoverable; top-level functions may be simpler for stateless helpers.

## Failure modes

A data class containing `MutableList` is copied, then one copy mutates the list and changes the other copy’s visible state. Replace it with immutable snapshots or deep-copy intentionally. A singleton retaining an Activity leaks the screen; never place lifecycle-bound references in a process-wide object.

## Production perspective

An Android app uses `data class ProfileUiState` for immutable rendering, `class ProfileRepository` for injected stateful behavior, `object` for a stateless formatter, and a companion factory only when construction must enforce an invariant.

## Interview answer — short

A data class is a value-oriented class with generated equality and copy; a regular class gives explicit identity and behavior; `object` declares one instance; and a companion object groups members with a class, often factories or constants. I choose by ownership and equality semantics.

## Interview answer — structured

For UI models I use immutable data classes so equality and copy have clear meaning. For a repository with dependencies and a lifetime, I use a regular class. A stateless singleton can be an `object`, but mutable singleton state is hard to test and can leak Android components. A companion is useful for validated construction. I remember that data-class copy is shallow and generated members only use primary-constructor properties. I would keep Activity references out of process-wide objects and avoid mutable lists inside copied state models. I would also test data-class equality with separately constructed values and avoid using a singleton as a hidden mutable service locator. Those tests expose the contract rather than merely checking that syntax compiles.

## Interview answer — deep senior

I would ask what defines equality, who owns lifecycle, and whether construction needs validation. Data classes generate value-like methods, but their `copy` does not clone nested objects. Regular classes can hide mutable state behind methods. Objects are lazily initialized singletons within a classloader, so they are process-local and unsuitable as durable storage or as holders of an Activity. Companions are real objects and can implement interfaces; Java interoperability may need deliberate annotations. The choice should make invariants obvious to callers. I review these declarations through equality and lifetime. An `object` gives a single instance in the process, which is convenient for stateless functions but dangerous for mutable global state and Android component references. A companion object groups construction logic with a class and may implement interfaces; it is not a magical persistent store. For a public API I also check how Java callers access companion members and how tests replace dependencies. The simplest declaration is the one that makes the object's ownership and equality behavior unsurprising. When a companion factory enforces construction rules, I keep validation there or in the constructor and test Java callers if the API is public. Process death means an `object` instance is recreated, so it cannot own durable session truth. Dependencies with different lifetimes belong in DI scopes or explicit owners.

## Deep-dive talking points

Discuss data-class constructor fields, shallow copy, singleton initialization and process death, companion factories and Java interop.

## Follow-up questions

- [KOT-04](../kot-04/): Why can two data-class copies compare equal? **Answer:** generated equality compares primary-constructor values.
- [KOT-02](../kot-02/): Does `val` inside a data class make nested objects immutable? **Answer:** no; it fixes the property reference only.

## Self-check rubric

Choose a declaration for UI state, repository, and factory; explain shallow copy and one singleton lifecycle risk.

## References and reviewed-on date

- [Kotlin data classes](https://kotlinlang.org/docs/data-classes.html) — generated members and copy.
- [Kotlin object declarations](https://kotlinlang.org/docs/object-declarations.html) — objects and companions.

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.
