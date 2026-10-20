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

## Concept and technical explanation

Choose a hierarchy by the kinds of variants it must represent and who may extend it:
1. An enum class defines a fixed set of singleton entries. Entries may have different constructor values and may override behavior, but all share one enum type and constructor contract; they are awkward for distinct payload shapes such as Success(receipt) versus Failure(error).
2. A sealed class restricts direct subclasses to the same package and module, and can hold constructor state or implementation. Direct subclasses must have a proper name and cannot be local or anonymous. Indirect subclasses of a non-sealed direct subclass may be open.
3. A sealed interface gives the same restricted direct-subtype model without consuming a class-inheritance slot. A type may implement several interfaces.
4. An abstract class may be extended wherever access rules permit, so the compiler cannot enumerate every subclass for exhaustive when checking. It is useful when external extension is part of the API.
Exhaustiveness is a source-level compiler check; do not infer a universal JVM switch layout or the absence of a runtime fallback from it.

## Practical walkthrough (English)

Consider modeling checkout payment processing in an Android e-commerce application:

Failure Scenario — Using Enums with Leaky Nullable Payloads:
```kotlin
enum class PaymentStatus {
    IDLE,
    PROCESSING,
    SUCCESS, // Needs receiptId
    FAILED   // Needs errorCode and canRetry
}

class PaymentStateHolder(
    val status: PaymentStatus,
    val receiptId: String?, // Leaky nullable
    val errorCode: Int?     // Leaky nullable
)
```
Consumers must check for impossible states, such as `PaymentStatus.SUCCESS` with a null `receiptId` or with a non-null `errorCode`.

Production Architecture — Sealed Interface Algebraic Data Types:
```kotlin
sealed interface CheckoutUiState {
    data object Idle : CheckoutUiState
    data object Processing : CheckoutUiState
    data class Success(val receiptId: String, val timestamp: Long) : CheckoutUiState
    data class Error(val code: Int, val message: String, val canRetry: Boolean) : CheckoutUiState
}

fun renderCheckoutState(state: CheckoutUiState): String = when (state) {
    CheckoutUiState.Idle -> "Ready to pay"
    CheckoutUiState.Processing -> "Authorizing transaction..."
    is CheckoutUiState.Success -> "Paid! Receipt #${state.receiptId}"
    is CheckoutUiState.Error -> "Failed (${state.code}): ${state.message}"
    // No else branch needed; compiler enforces exhaustiveness statically
}
```

Bytecode Decompilation Verification:
A particular Kotlin/JVM compiler version may lower a sealed class with a private constructor and a synthetic bridge, for example:
```java
public abstract class CheckoutUiState {
    private CheckoutUiState() {}
    public CheckoutUiState(DefaultConstructorMarker $constructor_marker) {
        this();
    }
}
```
The source restriction is enforced by the Kotlin compiler. A `when` over sealed variants is checked for exhaustiveness at compile time; its JVM bytecode shape is version- and target-dependent.

## Explanation in Arabic

السؤال الأساسي هنا: الحالات معروفة ومقفولة، ولا المكتبة سامحة لناس تانية تزود حالات؟
- `enum class` مناسب لعدد ثابت من القيم، وكل entry نسخة وحيدة. ينفع كل entry تاخد قيمة مختلفة في نفس حقول الـ constructor أو تنفّذ سلوك مختلف؛ اللي ما ينفعش بسهولة هو إن كل حالة يكون لها شكل بيانات مستقل زي `Success(receipt)` و`Failure(error)`.
- `sealed class` بيحصر الورثة المباشرين في نفس الـ package والـ module، وممكن يحمل بيانات أو كود مشترك. القيد على الورثة **المباشرين**؛ لو واحد منهم `open`، ممكن تظهر وراثة غير مباشرة حسب قواعده.
- `sealed interface` نفس فكرة حصر الورثة المباشرين، لكن الكلاس يقدر ينفّذ أكتر من interface.
- `abstract class` يسمح بالامتداد حسب الرؤية والـ API، فالمترجم ما يقدرش يحصر كل الحالات في `when`.
اكتب `when` من غير `else` لما عايز المترجم ينبهك عند إضافة حالة مباشرة جديدة. ده فحص وقت البناء، مش وعد بشكل bytecode معين.

## Practical walkthrough

في شاشة الدفع، لو كتبت `PaymentStatus.SUCCESS` جنب `receiptId: String?` ممكن الحالة تقول نجاح وفي نفس الوقت رقم الإيصال `null`. الحل إنك تمثّل كل نتيجة بشكلها: `data object Idle` و`data class Success(val receiptId: String)` و`data class Error(val reason: String)` تحت `sealed interface CheckoutUiState`.

خلّي `when (state)` يعالج الفروع صراحة. لما تضيف `RequiresVerification`، البناء هينبهك للمواضع اللي تحتاج تعديل. لو عندك API محتاج أطراف خارجية تضيف حالات جديدة، اختار `abstract class` أو interface مفتوح وتعامل مع فرع افتراضي بوضوح. `enum` يظل اختيار بسيط لو كل الحالات نفس شكل البيانات.

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

An enum class models a fixed set of constant singleton values sharing uniform structure. A sealed class or sealed interface defines a closed hierarchy where subclasses are known at compile time, enabling heterogeneous payloads and compiler-checked exhaustive when expressions without an else branch. A sealed interface permits multiple inheritance across hierarchies. In contrast, an abstract class is open for external extension but lacks compiler exhaustiveness guarantees.

## Interview answer — structured

Selecting the appropriate hierarchy construct in Kotlin depends on whether the domain demands compile-time exhaustiveness or open polymorphism. An enum class is tailored for a fixed set of singleton constants that can hold different values for shared fields, such as HTTP methods or card networks.

Sealed classes and sealed interfaces represent restricted hierarchies. They restrict direct inheritance to the same package and module, enabling the compiler to verify that every subtype is handled in when expressions without an else branch. Unlike enums, each sealed case can carry distinct typed payloads and maintain independent state lifecycles. Sealed interfaces further enhance modularity by allowing a domain model to belong to multiple sealed hierarchies simultaneously.

In production, an abstract class is suited only when building open frameworks where consumers outside the module must extend base behavior.

Senior engineers model MVI and Jetpack Compose screen states using sealed interfaces, ensuring that impossible states are unrepresentable in the type system and preventing runtime defects.


## Interview answer — deep senior

At the source level, sealed classes and sealed interfaces restrict direct subclasses to the same package and module. That closed direct set lets the compiler check exhaustive when expressions and supported when statements. An else branch can hide newly added variants, although an else can be intentional at interoperability boundaries. Indirect subclasses may still be open if a direct subclass is not itself sealed.

An enum defines fixed singleton entries of one type. Entries can receive different values through shared constructor parameters and can override abstract or open behavior, so claiming that enum entries cannot carry different data is inaccurate. A sealed hierarchy is more expressive when variants need different fields or multiple instances. A sealed class can carry shared constructor state and implementation; a sealed interface supports multiple interface inheritance. Abstract classes leave extension open wherever access rules allow.

On Kotlin/JVM, enums use the JVM enum model, but compiler lowering for sealed hierarchies and when varies with Kotlin and JVM target versions. Exhaustiveness is not evidence of a particular tableswitch, lookupswitch, synthetic constructor, or runtime branch shape. A runtime fallback can remain for binary compatibility when a library evolves without recompiling consumers. In an Android UI, model Idle as a data object and Success(receiptId) or Error(reason) as data classes, then handle each branch. Choose the hierarchy based on API extensibility and shared state rather than declaring one sealed form universally superior.

## How to answer in the interview

- **Why:** Model domain and UI state machines with exhaustive compile-time verification.
- **How:** Use `enum` for simple constants without state payloads, and `sealed class` / `sealed interface` when states require heterogeneous parameters.
- **Trade-offs:** Adding branches to a public sealed hierarchy in an exported library breaks consumer `when` statements unless managed carefully.
- **Failure cases:** Leaving an `else` branch in a UI state `when` block, which masks newly added states and causes unhandled UI rendering bugs.
- **Production solution:** Enforce exhaustive `when` expressions without `else` for UI/payment state machines, and model network errors as explicit sealed subtypes with retry metadata.

## Deep-dive talking points

Discuss direct-subclass restrictions, exhaustive `when`, `data object`, state-specific data, binary compatibility and serialization.

## Follow-up questions

- **Interviewer:** "Why is adding an `else` branch to a `when` expression over a sealed interface considered an anti-pattern?"
  **Answer:** "Because it destroys compiler exhaustiveness checking. If you include an `else` branch, and another developer adds a new state like `PaymentState.RequiresVerification` next month, the compiler will not warn you. The new state will silently fall into the `else` branch, causing subtle production bugs. Omitting `else` forces the compiler to break the build until the new state is explicitly handled."

- **Interviewer:** "Can a sealed class have subclasses in a different Gradle module?"
  **Answer:** "Direct subclasses must be in the same compilation module and package; an indirect subclass of an open direct subclass follows that subclass's normal inheritance rules. This rule allows the compiler to guarantee that it knows every possible subtype at compile time."

- **Interviewer:** "When would you prefer a sealed class over a sealed interface?"
  **Answer:** "I prefer a sealed class when shared constructor state or implementation is useful. A sealed interface is convenient when variants already inherit from another class or participate in more than one hierarchy. Neither is universally better."

## Self-check rubric

Give one enum use case and one sealed use case; explain payload advantage, exhaustiveness, and an open-extension use case.

## References and reviewed-on date

- [Kotlin sealed classes and interfaces](https://kotlinlang.org/docs/sealed-classes.html) — restricted hierarchies and exhaustive `when`.
- [Kotlin enum classes](https://kotlinlang.org/docs/enum-classes.html) — enum constants and behavior.

Technically reviewed against primary documentation on 2026-10-19.
