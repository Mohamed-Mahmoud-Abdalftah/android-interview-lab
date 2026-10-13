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

## Practical walkthrough

`data class Account(id, name)` مناسبة لـsnapshot UI فيها value semantics. لكن `copy()` shallow: لو جواها `MutableList` فالنسخة والاصل ممكن يشتركوا فيها. `class Session` مناسبة لما فيه identity وlifecycle أو controlled construction؛ `companion object` يعمل factory جنب النوع لكنه مش object instance لكل Session. `object` singleton داخل process، مش persistent store ولا scoped لكل user. في app فيه account switch، حط session state عند owner قابل للreset بدل global `object` ممكن يحتفظ ببيانات user قديم.

## Trade-offs and decision criteria

Use data class when all primary fields define value equality; use regular class for controlled identity or mutable invariants. `object` avoids duplicate instances but complicates state isolation and tests if it holds mutable data. Companion factories are discoverable; top-level functions may be simpler for stateless helpers.

## Failure modes

A data class containing `MutableList` is copied, then one copy mutates the list and changes the other copy’s visible state. Replace it with immutable snapshots or deep-copy intentionally. A singleton retaining an Activity leaks the screen; never place lifecycle-bound references in a process-wide object.

## Production perspective

An Android app uses `data class ProfileUiState` for immutable rendering, `class ProfileRepository` for injected stateful behavior, `object` for a stateless formatter, and a companion factory only when construction must enforce an invariant.

## Interview answer — short

A data class is for value-like records with generated equality and copy. A regular class suits identity and behavior. An `object` is a singleton declaration, while a companion object holds class-level factories or members. I choose by lifecycle and equality needs.

## Interview answer — structured

I first ask whether the type is a value or an entity with identity. A data class gives component functions, equality, and `copy`, but the copy is shallow, so nested mutable state needs care. A regular class lets me define construction and identity deliberately. An `object` creates a process-level singleton, which is useful for stateless utilities but risky for user session state. A companion object belongs to the class declaration and is a good place for a validated factory. In a multi-account app I would keep session ownership in a scoped component and use a data class for immutable account display state.

## Interview answer — deep senior

I would ask what defines equality, who owns lifecycle, and whether construction needs validation. Data classes generate value-like methods, but their `copy` does not clone nested objects. Regular classes can hide mutable state behind methods. Objects are lazily initialized singletons within a classloader, so they are process-local and unsuitable as durable storage or as holders of an Activity. Companions are real objects and can implement interfaces; Java interoperability may need deliberate annotations. The choice should make invariants obvious to callers.

For an account feature, I might model the displayed account as a data class, a session controller as a regular class with explicit lifecycle, a stateless format validator as an `object`, and a validated session factory in a companion. The failure mode is placing the current user in a global object: it can retain stale state after account switching and disappears after process death. I would scope session state to the authenticated owner and reload it from the authoritative source. I would also test `copy()` with nested collections so it does not masquerade as a deep snapshot.

## How to answer in the interview

- **Why:** Match language constructs to data modeling, identity, and lifecycle requirements.
- **How:** Use `data class` for immutable state payloads, regular `class` for stateful actors, `object` for singletons, and `companion object` for factory methods.
- **Trade-offs:** `data class` generates `copy()`, `equals()`, and `hashCode()` based on primary constructor properties; shallow copying mutable references breaks deep immutability.
- **Failure cases:** Treating an `object` singleton as durable storage across process death, leading to state reset and `NullPointerException` when Android restores the activity.
- **Production solution:** Store session-scoped state in `ViewModel` or `SavedStateHandle`, persist durable data in Room/DataStore, and restrict `object` to stateless utilities.

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

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets; no Android device claim is made.
