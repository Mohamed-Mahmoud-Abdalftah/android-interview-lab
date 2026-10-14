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

المقارنة بين sealed class و sealed interface و enum class و abstract class بتحدد كيفية نمذجة البيانات والـ State في معمارية التطبيق:

1. enum class: بيمثل مجموعة ثابتة ومحدودة من القيم الثابتة (Constants)؛ كل عنصر فيه بيملك نفس الخصائص والدوال بالضبط (زي OrderStatus.PENDING, SHIPPED, DELIVERED). مينفعش عنصر يشيل بيانات مختلفة عن الباقيين.
2. sealed class: بيمثل تسلسل هرمي مقيد ومعروف مسبقاً للمترجم. كل Subclass يقدر يكون data class مستقل ببيانات وحقول مختلفة كلياً، وميزة المترجم إنه بيضمن الـ Exhaustiveness في when بدون الحاجة لـ else!
3. sealed interface: ظهرت في Kotlin 1.5، وهي أفضل من sealed class لأنها بتسمح بالـ Multiple Inheritance؛ الكائن يقدر يورث من كذا sealed interface، وده مثالي لتنظيم حالات الـ UI المعقدة.
4. abstract class: كلاس مفتوح للوراثة في أي مكان أو موديول، والمترجم ميعرفش كل فروعه، وبالتالي when عليه لازم تطلب else دايماً.

## Practical walkthrough

في شاشة تفاصيل الدفع:
- استخدام enum class خطأ لأن حالة الفشل محتاجة كود الخطأ ورسالة وزرار إعادة المحاولة (PaymentState.Error(val code: Int, val canRetry: Boolean)) بينما حالة النجاح محتاجة رقم الإيصال.
- الحل الأفضل: استخدام sealed interface لتحديد حالات الشاشة:
  sealed interface PaymentUiState {
      object Idle : PaymentUiState
      object Loading : PaymentUiState
      data class Success(val receiptId: String) : PaymentUiState
      data class Error(val message: String, val canRetry: Boolean) : PaymentUiState
  }
- في Compose: دالة when بتكون Exhaustive؛ لو ضفت حالة جديدة زي PendingBiometric مستقبلاً، المترجم هيكسر الـ build وينبهك لكل شاشة محتاجة تتعامل مع الحالة دي.

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

Enums represent a fixed set of constant values with identical schemas. Sealed classes and interfaces model restricted type hierarchies where each subtype can hold distinct data fields and states. Sealed interfaces allow multiple inheritance across hierarchies, while abstract classes allow unrestricted inheritance and require an else branch in when expressions.

## Interview answer — structured

I choose between these constructs based on data variation and inheritance constraints.

An enum class is strictly for constant values that share the exact same fields, such as days of the week or simple HTTP methods. However, if states require different payloads—like a UI state where Success carries data, Loading carries progress, and Error carries an exception—I use a sealed hierarchy.

Between sealed class and sealed interface, I strongly prefer sealed interfaces in modern Kotlin. They avoid consuming a class's single inheritance slot, allowing a data class to implement multiple sealed interfaces while retaining compile-time exhaustive when checks without an else branch.

Abstract classes remain useful for sharing base implementation logic across open, extensible libraries where the full set of subclasses cannot be known at compile time.


## Interview answer — deep senior

Under the hood, sealed hierarchies provide compile-time exhaustive pattern matching. In Kotlin bytecode, a sealed class compiles with a private or protected constructor, restricting subclassing to the same package and compilation module. The compiler generates metadata attributes listing all permitted subclasses. When evaluated in a when expression, the compiler inspects this table. If all branches are covered, it omits the default case; if a branch is missing, it fails compilation.

The addition of sealed interfaces solved a major JVM limitation: single class inheritance. Prior to Kotlin 1.5, if a data class extended a sealed class, it could not extend any other class. With sealed interfaces, a state object like UserSession can implement both a sealed NavigationDestination interface and a sealed AnalyticsTrackable interface. Furthermore, sealed interfaces allow enum classes or value classes to implement them, enabling rich compositional architectures.

In production Android architecture, we use sealed interfaces for MVI/UDF UI states and domain errors. Enums are reserved for database-persisted lookup constants or query filters. Abstract classes are restricted to internal base classes (like a BaseRepository) where shared implementation code must be inherited rather than composed.


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
  **Answer:** "No. Subclasses of a sealed class or interface must be defined in the same compilation module and package. This rule allows the compiler to guarantee that it knows every possible subtype at compile time."

- **Interviewer:** "When would you prefer a sealed class over a sealed interface?"
  **Answer:** "The only time I prefer a sealed class is when I need to store shared non-abstract state or constructor parameters across all subclasses, or enforce a common non-public constructor. If there is no shared constructor state, sealed interface is always the cleaner, more flexible choice."

## Self-check rubric

Give one enum use case and one sealed use case; explain payload advantage, exhaustiveness, and an open-extension use case.

## References and reviewed-on date

- [Kotlin sealed classes and interfaces](https://kotlinlang.org/docs/sealed-classes.html) — restricted hierarchies and exhaustive `when`.
- [Kotlin enum classes](https://kotlinlang.org/docs/enum-classes.html) — enum constants and behavior.

Technically reviewed against primary documentation on 2026-10-13.
