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

Enums are strictly for static constants that share identical attributes across all instances. Sealed hierarchies are superior for UI and payment states because they allow individual states to hold distinct payloads (e.g., Success holds a Receipt, while Failed holds an ErrorReason), eliminating invalid states and enabling compiler-enforced smart casting in when expressions.

## Interview answer — structured

I choose sealed hierarchies over enums whenever different states require different payloads. Enums represent fixed sets of uniform constants; every enum entry must share the exact same constructor properties, and every entry is a singleton instantiated when the class is loaded.

In real-world UI and payment flows, states are inherently heterogeneous. An Idle state carries no data, a Loading state might carry a progress percentage, a Success state carries a PaymentReceipt object, and a Failed state carries an error domain model and a retry policy. Modeling this with an enum forces you into a bloated 'God state' with dozens of nullable properties, creating invalid states like being in Success status with a null receipt.

With a sealed interface, illegal states become unrepresentable in the type system. In the UI or ViewModel, Kotlin's when expression guarantees exhaustive branch coverage and smart-casts each branch to its concrete type, giving safe, direct access to that state's payload without null assertions.

## Interview answer — deep senior

From an architectural domain-modeling perspective, sealed hierarchies embody Algebraic Data Types (specifically Sum Types with Product Type variants). Using `sealed interface` combined with `data object` (introduced in Kotlin 1.9) gives the best of both worlds: parameterless states like `Idle` compile to singletons with clean toString() logging, while parameterized states like `Success(val receipt: Receipt)` allocate new instances holding distinct payloads.

In contrast, forcing an enum to represent dynamic states leads to architectural rot: developers often resort to mutable companion objects, global singletons, or nullable fields in a single giant class. If a new business requirement emerges—such as adding a `TwoFactorRequired(val challengeToken: String)` state to a payment flow—with a sealed interface, the Kotlin compiler will fail compilation at every single `when` expression across the entire project that doesn't handle the new variant, acting as an automated refactoring guide.

In Jetpack Compose, sealed states are especially critical for recomposition stability. Distinct state classes allow Compose to skip recomposition when only unrelated properties in sibling states change, boosting rendering performance.

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
