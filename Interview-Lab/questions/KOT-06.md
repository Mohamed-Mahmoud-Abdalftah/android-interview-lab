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

## Trade-offs and decision criteria

Choose enum for fixed, uniform constants such as sort direction. Choose sealed types for case-specific data and exhaustive branching. Use abstract class or interface if consumers must add implementations. Serialization and cross-module API evolution need care when adding a new sealed case.

## Failure modes

A payment result enum with separate nullable `receiptId` and `errorCode` allows impossible combinations. Sealed cases bind each payload to the state that requires it. Conversely, using sealed for a plugin API prevents third parties from adding cases.

## Production perspective

A checkout ViewModel exposes `CheckoutState` as sealed cases. Rendering handles `Idle`, `Processing`, `Succeeded(receipt)`, and `Failed(reason)` exhaustively. Domain payment authorization still lives server-side; UI state is only presentation.

## Interview answer — short

Enums are fixed constants; sealed classes and interfaces define a closed set of subtypes with different payloads; abstract classes are extensible. I use a sealed hierarchy when the compiler should force every state to be handled.

## Interview answer — structured

If cases are uniform constants, an enum is simplest. If `Success` has a receipt and `Failure` has an error, a sealed hierarchy models those payloads without nullable fields. A sealed interface supports multiple inheritance patterns, while a sealed class can share constructor state. `when` over a closed hierarchy can be exhaustive. An abstract class is appropriate when I intentionally allow external implementations. If the state is just `ASCENDING` or `DESCENDING`, an enum is easy to read. If `Ready` needs items and `Failed` needs a cause, separate sealed cases ensure each payload is present only where it belongs. `when` can then force callers to handle a newly added case. I would choose an open abstract type only when plugin authors or other modules are supposed to provide new implementations.

## Interview answer — deep senior

The design question is whether the set of cases is closed and whether each case has a distinct payload. Sealed types make state transitions and rendering explicit, but adding a case can break exhaustive consumers, which is often desirable inside an app and more delicate in a public library. Enums are efficient and discoverable for fixed constants, but bolting payloads onto one enum often creates invalid states. Abstract classes permit extension and shared implementation, at the cost of weaker exhaustiveness. I choose based on API evolution as well as syntax. A sealed class or interface lets me encode a finite state space. The compiler can check an exhaustive `when`, so adding `PendingVerification` to a checkout flow exposes all places that need a decision. Enums are excellent for uniform constants and can themselves hold properties, but they do not give each case a separate subtype with distinct constructor data. An abstract class is intentionally open to more subclasses and therefore offers a different evolution contract. In production I would also consider serialization: persisted values need stable wire codes and migration, not assumptions about Kotlin class names. Closedness helps local correctness, but it does not replace server authority or transition tests.

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

Technically reviewed against the linked primary documentation on 2026-10-11. Examples are illustrative JVM snippets; no Android device claim is made.
