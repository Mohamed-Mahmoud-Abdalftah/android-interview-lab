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

Kotlin provides four distinct constructs for modeling hierarchies and state spaces:
1. enum class: Models a closed, finite set of constant values known at compile time. Each enum constant is a singleton instance of the enum class, sharing identical properties and functions. They cannot carry varying instance payloads across different cases.
2. sealed class: Represents a restricted, closed class hierarchy where all direct subclasses are known at compile time and defined within the same package and module. Unlike enums, subclasses of a sealed class can be instantiated multiple times, maintain independent state shapes, and carry heterogeneous constructor payloads.
3. sealed interface: Extends sealed hierarchy semantics to interfaces, allowing a class to implement multiple sealed hierarchies simultaneously. This circumvents single-inheritance limitations and enables composable algebraic data types without JVM class inheritance coupling.
4. abstract class: An open, extensible base class intended for traditional object-oriented polymorphism across arbitrary packages and external modules. The compiler does not enforce exhaustive checking on abstract classes in when expressions.

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
Decompiling a sealed class reveals that kotlinc generates a private synthetic constructor:
```java
public abstract class CheckoutUiState {
    private CheckoutUiState() {}
    public CheckoutUiState(DefaultConstructorMarker $constructor_marker) {
        this();
    }
}
```
This bytecode structure prevents external packages from subclassing. Furthermore, when compiling a `when` expression over a sealed type, kotlinc synthesizes a lookupswitch or tableswitch mapping known subclass tokens, proving compile-time exhaustiveness.

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

An enum class models a fixed set of constant singleton values sharing uniform structure. A sealed class or sealed interface defines a closed hierarchy where subclasses are known at compile time, enabling heterogeneous payloads and exhaustive when expressions without an else branch. A sealed interface permits multiple inheritance across hierarchies. In contrast, an abstract class is open for external extension but lacks compiler exhaustiveness guarantees.

## Interview answer — structured

Selecting the appropriate hierarchy construct in Kotlin depends on whether the domain demands compile-time exhaustiveness or open polymorphism. An enum class is tailored for uniform constants where each entry is a static singleton sharing identical attributes, such as HTTP methods or card networks.

Sealed classes and sealed interfaces represent algebraic data types. They restrict inheritance to the current compilation unit, enabling the compiler to verify that every subtype is handled in when expressions without an else branch. Unlike enums, each sealed case can carry distinct typed payloads and maintain independent state lifecycles. Sealed interfaces further enhance modularity by allowing a domain model to belong to multiple sealed hierarchies simultaneously.

In production, an abstract class is suited only when building open frameworks where consumers outside the module must extend base behavior.

Senior engineers model MVI and Jetpack Compose screen states using sealed interfaces, ensuring that impossible states are unrepresentable in the type system and preventing runtime defects.


## Interview answer — deep senior

At the bytecode and JVM level, the mechanisms enforcing these hierarchy constructs diverge significantly. An enum class compiles to a subclass of java.lang.Enum, with each constant emitted as a public static final field initialized in the class initializer <clinit>. Because each constant is a JVM singleton, enums cannot carry dynamic constructor state across instances, and every constant incurs class-loading overhead upon first access.

In contrast, a sealed class compiles to an abstract Java class whose constructor is marked private or synthetic with a DefaultConstructorMarker. This bytecode convention guarantees that external bytecode cannot extend the class, while permitting nested or same-file subclasses to invoke the synthetic constructor. When evaluating a when expression over a sealed class, kotlinc evaluates the runtime instance using instanceof instructions or synthesizes an integer-mapped switch table. If all sealed subtypes are covered, the compiler omits the default switch label, ensuring that adding a new subclass immediately breaks compilation across all unhandled sites.

Sealed interfaces compile directly to JVM interface class files accompanied by PermittedSubclasses compiler metadata (or kotlin.Metadata attributes). This enables classes to participate in multiple sealed domains without consuming the single class inheritance slot on the JVM. From a memory allocation perspective, sealed hierarchies can combine data object singletons for stateless cases (like Loading or Idle) with data class instances for payload-bearing cases (like Success or Error), eliminating heap allocations for static states while preserving rich payload modeling.

In enterprise Android architecture, senior engineers strictly prefer sealed interfaces over abstract classes for UI and navigation state. Abstract classes permit external subclasses to leak into domain boundaries without compiler validation, whereas sealed interfaces ensure strict architectural containment, deterministic state transitions, and seamless integration with Compose recomposition pruning.

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
