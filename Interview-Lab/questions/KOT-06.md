---
id: "KOT-06"
question: "Compare sealed class, sealed interface, enum class, and abstract class."
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "A"
phase: 1
priority: "P1"
order: 6
editorial_status: "reviewed"
---

# KOT-06

## Original interview question

Compare sealed class, sealed interface, enum class, and abstract class.

## What the interviewer evaluates

Explain closed hierarchies, payload support, enum limitations, and open extension policies.

## Explanation in Arabic

`enum class` مجموعة قيم ثابتة من نفس enum، وكل قيمة ممكن يكون لها properties وسلوك، لكن مش subtype مختلف ببيانات constructor خاصة بكل حالة. `sealed class` و`sealed interface` يقفلوا الـdirect subtype set حسب قواعد Kotlin، فيقدر `when` يبقى exhaustive بدون `else` لو كل الحالات متغطية. sealed class تقدر تحتفظ state أو constructor، والـinterface تسمح بتنفيذها مع inheritance من class تانية وبأكثر من interface. `abstract class` مش closed hierarchy؛ مكتبات أو modules تقدر تزود implementations حسب visibility، فـ`when` مش مضمون exhaustive.

## Why it matters and how it works

Closed hierarchies turn missing cases into compile-time feedback. They are useful when UI or domain states have different payloads. An open abstract type is better when extension by clients is part of the API contract. Enums are compact for a fixed set of uniform constants.

## Worked example

JVM example: payload-bearing states are modeled as separate cases.
```kotlin
sealed interface LoadState {
    data object Loading : LoadState
    data class Ready(val count: Int) : LoadState
    data class Failed(val message: String) : LoadState
}
fun label(state: LoadState): String = when (state) {
    LoadState.Loading -> "Loading"
    is LoadState.Ready -> "${state.count} items"
    is LoadState.Failed -> state.message
}
```

## Practical walkthrough

في `LoadState`، `Ready(items)` محتاجة payload مختلف عن `Failed(cause)`؛ sealed hierarchy تضمن إن `when` على الحالات المعروفة يغطيهم. `enum` أنسب لو مجرد مجموعة constants ثابتة زي sort mode، حتى لو enum عندها properties مشتركة، إنما مش payload فريد لكل occurrence. `abstract class` تقدر تسمح extension مفتوح لو ده مقصود؛ sealed بتقيّد direct subclasses حسب قواعد Kotlin. `sealed interface` مفيدة لو case لازم تطبق أكتر من contract، لكن لو public library بتتطور كتير، إضافة case جديدة ممكن تكسر exhaustive consumers عند إعادة الترجمة.

## Trade-offs and decision criteria

Choose enum for fixed, uniform constants such as sort direction. Choose sealed types for case-specific data and exhaustive branching. Use abstract class or interface if consumers must add implementations. Serialization and cross-module API evolution need care when adding a new sealed case.

## Failure modes

A payment result enum with separate nullable `receiptId` and `errorCode` allows impossible combinations. Sealed cases bind each payload to the state that requires it. Conversely, using sealed for a plugin API prevents third parties from adding cases.

## Production perspective

A checkout ViewModel exposes `CheckoutState` as sealed cases. Rendering handles `Idle`, `Processing`, `Succeeded(receipt)`, and `Failed(reason)` exhaustively. Domain payment authorization still lives server-side; UI state is only presentation.

## Interview answer — short

I use an enum for a fixed set of constant choices, and a sealed hierarchy when each case can carry different data. A sealed `when` can be exhaustive. An abstract class is useful when extension is intentionally open, while a sealed interface can combine contracts.

## Interview answer — structured

The design test is whether cases have different payloads and whether the set should be closed. A UI load result has Loading, Ready with data, and Failed with an error, so a sealed type models legal shapes and enables exhaustive handling. A sort order with fixed constants is simpler as an enum. A plain abstract class is appropriate when third parties should add implementations; a sealed class can share constructor state, while a sealed interface supports multiple interface inheritance. In production I consider API evolution: introducing another sealed case obliges consumers with exhaustive `when` expressions to handle it when they recompile.

## Interview answer — deep senior

The design question is whether the set of cases is closed and whether each case has a distinct payload. Sealed types make state transitions and rendering explicit, but adding a case can break exhaustive consumers, which is often desirable inside an app and more delicate in a public library. Enums are efficient and discoverable for fixed constants, but bolting payloads onto one enum often creates invalid states. Abstract classes permit extension and shared implementation, at the cost of weaker exhaustiveness. I choose based on API evolution as well as syntax.

Consider a search result: Loading has no data, Ready has a list, and Failed has a reason. A sealed hierarchy avoids a single record with nullable `items` and `error` that allows contradictory combinations. It does not, however, enforce that Ready can only follow Loading; transition rules belong in a reducer or coordinator. If this is a public library, adding a new sealed case requires consumers to update exhaustive `when` logic, which is a compatibility decision. For a simple fixed filter option, I would choose an enum and avoid the extra hierarchy.

## How to answer in the interview

- **Why:** Model domain and UI state machines with exhaustive compile-time verification.
- **How:** Use `enum` for simple constants without state payloads, and `sealed class` / `sealed interface` when states require heterogeneous parameters.
- **Trade-offs:** Adding branches to a public sealed hierarchy in an exported library breaks consumer `when` statements unless managed carefully.
- **Failure cases:** Leaving an `else` branch in a UI state `when` block, which masks newly added states and causes unhandled UI rendering bugs.
- **Production solution:** Enforce exhaustive `when` expressions without `else` for UI/payment state machines, and model network errors as explicit sealed subtypes with retry metadata.

## Deep-dive talking points

Discuss direct-subclass restrictions, exhaustive `when`, `data object`, state-specific data, binary compatibility and serialization.

## Follow-up questions

- [KOT-26](../kot-26/): Why prefer sealed payment states? **Answer:** each outcome can carry required payload and make invalid combinations unrepresentable.
- [KOT-28](../kot-28/): How can errors retain detail? **Answer:** use a sealed error family with stable categories and associated data.

## Self-check rubric

Give one enum use case and one sealed use case; explain payload advantage, exhaustiveness, and an open-extension use case.

## References and reviewed-on date

- [Kotlin sealed classes and interfaces](https://kotlinlang.org/docs/sealed-classes.html) — restricted hierarchies and exhaustive `when`.
- [Kotlin enum classes](https://kotlinlang.org/docs/enum-classes.html) — enum constants and behavior.

Technically reviewed against the linked primary documentation on 2026-10-13. Examples are illustrative JVM snippets; no Android device claim is made.
