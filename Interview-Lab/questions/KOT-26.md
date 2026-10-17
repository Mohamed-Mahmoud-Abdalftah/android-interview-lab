---
id: "KOT-26"
question: "When would a sealed hierarchy be better than an enum for UI or payment states?"
topic: "Kotlin Core & Advanced"
code: "KOT"
group: "C"
phase: 1
priority: "P1"
order: 26
editorial_status: "reviewed"
---

# KOT-26

## Original interview question

When would a sealed hierarchy be better than an enum for UI or payment states?

## What the interviewer evaluates

Model payload-bearing state and transitions, distinguish UI display from server-side payment authority.

## Concept and technical explanation

Deciding between an Enum class and a Sealed Hierarchy (`sealed interface` / `sealed class`) is a foundational architectural decision in Kotlin domain and UI state modeling. Enums represent a strictly closed set of constant, immutable singleton values. Every enum constant must conform to identical constructor parameters, cannot carry dynamic, stateful payloads that vary per instance, and cannot vary its fields across different instances. In stark contrast, a sealed hierarchy models a closed family of distinct types. Each subclass within a sealed hierarchy can be declared as an object (for stateless cases), a data class (with distinct, strongly typed payload parameters), or even another sealed hierarchy. For complex domain workflows—such as e-commerce checkout flows or asynchronous UI state machines—states inevitably carry disparate payloads (e.g., an Idle state has no data, a Loading state carries progress metadata, a Success state carries a domain Receipt, and an Error state carries failure codes and recovery policies). Sealed hierarchies represent these diverse states without resorting to nullable anti-patterns, while ensuring exhaustive compiler evaluation in `when` expressions.

## Practical walkthrough (English)

Consider modeling an e-commerce checkout state machine. If an engineer naively attempts an enum: `enum class CheckoutState { IDLE, LOADING, SUCCESS, FAILED }`, all state-specific payloads must be shoved into nullable fields on the host ViewModel or enum: `var receipt: Receipt? = null; var error: String? = null`. This creates an illegal state space where `CheckoutState.SUCCESS` can coexist with a null receipt, leading to defensive assertions and runtime crashes. By implementing a sealed hierarchy: `sealed interface CheckoutState { data object Idle : CheckoutState; data class Processing(val progress: Float) : CheckoutState; data class Success(val receipt: Receipt) : CheckoutState; data class Failed(val reason: String, val canRetry: Boolean) : CheckoutState }`, invalid state combinations become completely unrepresentable in the type system. In Jetpack Compose or ViewModel observers, a `when (state)` block exhaustively handles each branch with zero unsafe casting.

## Explanation in Arabic

المقارنة بين `enum` و `sealed class` / `sealed interface` في نمذجة الحالات (UI & Payment States) هي محور أساسي في تصميم الأنظمة الحديثة:

1. متى يكون الـ Enum كافياً (When Enum is enough)?
   - الـ Enum مناسب فقط لما تكون الحالات **مجموعة ثابتة من الثوابت المجردة (Simple Fixed Constants)** بدون بيانات متغيرة خاصة بكل حالة.
   - مثال: اتجاهات الشاشة (`LANDSCAPE`, `PORTRAIT`) أو أيام الأسبوع (`MONDAY`, `TUESDAY`).
   - عيب الـ Enum: كل القيم لازم تشترك في نفس الـ Properties المحددة في الـ Constructor، ولا يمكن لحالة واحدة تحمل Payload مختلف عن باقي الحالات.

2. متى تكون الـ Sealed Hierarchy متفوقة وضرورية (Why Sealed Hierarchies Win)?
   - في الـ UI States والـ Payment States، كل حالة بتحتاج **بيانات مختلفة تماماً (State-Specific Payloads)**:
     * حالة `Idle`: لا بيانات.
     * حالة `Loading`: رسالة تحميل اختيارية ونسبة مئوية `progress: Float`.
     * حالة `Success`: بيانات الإيصال `receipt: PaymentReceipt` ومعرف المعاملة.
     * حالة `Failure`: نوع الخطأ `error: PaymentError` ورقم هاتف الدعم ورابط إعادة المحاولة.
   - الـ `sealed interface` بتسمح بتعريف `data object` للحالات المجردة (لتوفير الذاكرة)، و `data class` للحالات اللي فيها بيانات.
   - الـ Compiler في `when` بيضمن معالجة كل الحالات (Exhaustive Checking) ويقوم بعمل Smart Cast تلقائياً للبيانات الخاصة بكل حالة.

## Practical walkthrough

في شاشة إتمام عملية الدفع (Checkout Payment Flow):
- **النهج الفاشل باستخدام Enum و God Data Class:**
  data class CheckoutState(
      val status: PaymentStatus, // Enum: IDLE, PROCESSING, SUCCESS, ERROR
      val receipt: Receipt? = null,
      val errorMessage: String? = null,
      val retryCount: Int = 0
  )
  هذا التصميم يخلق حالات غير شرعية (Illegal States): ممكن يكون الـ Status = SUCCESS لكن الـ receipt = null! المطور مضطر يكتب `receipt!!` أو `receipt?.let` في كل حتة.
- **النهج الصحيح باستخدام Sealed Interface (Make Illegal States Unrepresentable):**
  sealed interface PaymentUiState {
      data object Idle : PaymentUiState
      data class Processing(val step: String) : PaymentUiState
      data class Success(val receipt: Receipt) : PaymentUiState
      data class Failed(val reason: PaymentError, val canRetry: Boolean) : PaymentUiState
  }
  الآن مستحيل تقنياً تمثيل حالة نجاح بدون إيصال!

## Why it matters and how it works

A closed payload-bearing hierarchy makes invalid combinations harder to represent and forces handling new cases. It also clarifies transition semantics, but persistence and network uncertainty need separate design.

## Worked example

JVM illustration of distinct case payloads.
```kotlin
sealed interface CheckoutState {
    data object Idle : CheckoutState
    data class Processing(val requestId: String) : CheckoutState
    data class Succeeded(val receiptId: String) : CheckoutState
    data class Failed(val code: String) : CheckoutState
}
fun terminal(s: CheckoutState) = when (s) {
    CheckoutState.Idle, is CheckoutState.Processing -> false
    is CheckoutState.Succeeded, is CheckoutState.Failed -> true
}
```

## Trade-offs and decision criteria

Sealed cases are more verbose and adding a case affects exhaustive clients. That is useful within a controlled app; a public extensible API may need an interface. Enum remains best for simple fixed choices such as payment method display category. Persisted wire values need explicit mapping, not implicit class names.

## Failure modes

A timeout is mapped straight to `Failed`, but the payment may have succeeded server-side. Represent `PendingVerification` or query authoritative status before allowing retry. Idempotency keys reduce duplicate effects but do not prove exactly-once network execution.

## Production perspective

Checkout ViewModel renders sealed local states while repository persists request ID and queries server after uncertain outcomes. It restores state after process death, logs correlation IDs without card data, and tests retry/reconciliation paths.

## Interview answer — short

Enums represent fixed, stateless singleton instances sharing identical fields, ideal for static categories like days or directions. Sealed hierarchies represent closed type families where each branch can have distinct types, payloads, and lifecycles, making them far superior for state machines and UI models where each state requires distinct data.

## Interview answer — structured

The choice between an enum and a sealed hierarchy in Kotlin hinges on whether the states require distinct, type-safe data payloads. An enum class represents a fixed collection of singleton constants that share identical constructor properties, making it optimal for uniform categories such as order sorting modes or days of the week.

Sealed hierarchies represent closed algebraic data types where each case can be an independent class with unique fields, or a data object for stateless transitions.

In production, such as payment flows or screen UI states, states require radically different payloads: an idle state carries nothing, while a success state holds an order receipt, and a failure state holds an error code and retry policy.

Sealed hierarchies make invalid states completely unrepresentable in the type system and provide compile-time exhaustive evaluation in when expressions without fallback else clauses.


## Interview answer — deep senior

Under the hood, Kotlin sealed hierarchies compile to standard JVM classes with restricted visibility mechanisms. Prior to Kotlin 1.5, sealed classes were compiled as abstract classes with private synthetic constructors, permitting subclasses only within the same file. Starting with Kotlin 1.5+, `sealed interface` was introduced, compiling to standard JVM interfaces equipped with permitted subclass metadata recognized by modern JVM bytecode verifiers, allowing subclasses across any file within the same compilation module and package. In contrast, every enum constant compiles to a `public static final` singleton instance inheriting from `java.lang.Enum`, holding an internal integer ordinal and string name. Regarding memory lifecycle, enum constants reside permanently in the JVM PermGen/Metaspace heap once loaded, whereas sealed data class instances are instantiated on demand, updated dynamically, and reclaimed by the garbage collector when state transitions occur. For serialization in modern Android applications, `kotlinx.serialization` handles sealed hierarchies through compile-time polymorphic serializers (`@Polymorphic` or `@SerialName`), allowing dynamic JSON discrimination based on a type descriptor property. In fintech payment systems, a critical distinction must be drawn between transient local UI state and server-side transaction authority. A network timeout in a payment flow must not be mapped naively to a terminal `Failed` state if the server might have already authorized the charge. Senior engineers model this using a dedicated `PaymentState.PendingVerification(val transactionId: String)` branch, forcing the client to poll or reconcile with the server before declaring finality.

## How to answer in the interview

- **Why:** Enforce type-safe state modeling with distinct data payloads for complex domain and payment workflows.
- **How:** Use sealed classes where states have distinct parameters (e.g., `PaymentState.Success(txId)`, `PaymentState.Failed(code, retryable)`).
- **Trade-offs:** Sealed hierarchies cannot be iterated over like enum values (`values()`), and adding new subtypes requires handling across all `when` expressions.
- **Failure cases:** Using an enum with nullable fields for state payloads, allowing invalid states (e.g., `PaymentState.SUCCESS` paired with an error message) to exist at runtime.
- **Production solution:** Model UI and checkout flows using sealed classes to make invalid states unrepresentable, combining exhaustive `when` matching with targeted UI rendering.

## Deep-dive talking points

Discuss case-specific payloads, exhaustive rendering, transition tests, process death, idempotency and server reconciliation.

## Follow-up questions

- **Interviewer:** "Can a sealed class have subclasses outside the module?"
  **Answer:** "No. All direct subclasses of a sealed class or interface must be defined in the same package and the same compilation module. This restriction is precisely what allows the Kotlin compiler to guarantee exhaustive when expressions without requiring an else branch."

- **Interviewer:** "Why prefer `sealed interface` over `sealed class` in modern Kotlin?"
  **Answer:** "`sealed interface` allows multiple inheritance (a state can implement multiple domain marker interfaces, like `NavigableState` and `CacheableState`), and it does not consume a class inheritance slot on the JVM. It also generates cleaner bytecode with less hierarchy overhead."

- **Interviewer:** "How do you serialize a sealed state hierarchy to JSON with kotlinx.serialization?"
  **Answer:** "By annotating the sealed interface with `@Serializable`. Kotlinx.serialization automatically attaches a polymorphic class discriminator (by default `type: "Success"`) to the JSON output and decodes incoming payloads into the exact concrete subclass at runtime without reflection."

## Self-check rubric

Model success/failure payloads, justify enum alternative, and explain timeout uncertainty in a payment flow.

## References and reviewed-on date

- [Kotlin sealed classes and interfaces](https://kotlinlang.org/docs/sealed-classes.html) — closed cases and exhaustive `when`.
- [Android app architecture](https://developer.android.com/topic/architecture) — separation of UI and data sources.

Technically reviewed against primary documentation on 2026-10-13.
