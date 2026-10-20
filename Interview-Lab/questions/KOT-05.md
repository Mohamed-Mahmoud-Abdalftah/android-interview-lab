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

## Concept and technical explanation

These declarations differ in generated behavior and instance lifetime, rather than enforcing particular architectural roles:
1. `data class` may have `val` or `var` constructor properties, so it is **not inherently immutable**. The compiler normally derives `equals()`, `hashCode()`, `toString()`, `copy()`, and `componentN()` from primary-constructor properties. Explicit or inherited implementations affect some generated methods. `copy()` is shallow; neither `val` nor a read-only `List` type makes referenced objects deeply immutable.
2. A regular `class` gives you control over identity, invariants, state, and behavior. It is final by default; use `open` or an interface when polymorphism is needed. It can also be an immutable value holder, but does not generate data-class operations.
3. An `object` declaration supplies one instance **per class loader**, initialized on first access in a thread-safe way on Kotlin/JVM. Initialization safety does not make mutable fields or subsequent calls thread-safe. In Android, its state is lost after process death.
4. A `companion object` is an object associated with an enclosing class. It can expose factories or implement interfaces, but its members are not automatically Java static methods. Use `@JvmStatic` only when Java static-call interoperability is needed; do not claim it is a general performance optimization.

## Practical walkthrough (English)

Consider designing a banking transfer feature in an Android application:

Failure Scenario — Misusing Data Class with Mutable Collections:
```kotlin
data class TransferUiState(
    val recipient: String,
    val transactionHistory: MutableList<String> // Anti-pattern!
)

fun demonstrateFailure() {
    val state1 = TransferUiState("Alice", mutableListOf("Tx1"))
    val state2 = state1.copy() // Shallow copy!
    
    state2.transactionHistory.add("Tx2")
    // state1.transactionHistory is also modified!
    println(state1 == state2) // true, but state1 was silently corrupted
}
```
Because copy() generates a shallow copy of member references, mutating the collection via one copy mutates the state visible to all other copies.

Production Architecture — Clean Separation of Class Roles:
```kotlin
// 1. Data class: snapshot by convention; copy collections defensively at boundaries
data class TransferUiState(
    val recipient: String,
    val history: List<String> = emptyList()
) {
    // 4. Companion Object: Factory for initial state
    companion object {
        val Initial = TransferUiState(recipient = "")
    }
}

// 2. Regular Class: Encapsulates stateful business logic and dependencies
class TransferRepository(private val apiService: TransferApi) {
    suspend fun executeTransfer(state: TransferUiState): Result<Unit> {
        return apiService.send(state.recipient)
    }
}

// 3. Object: Stateless utility or single-instance formatter
object CurrencyFormatter {
    fun formatUsd(amount: Double): String = "$%.2f".format(amount)
}
```

Bytecode Decompilation Verification:
A representative Kotlin/JVM compilation of an object uses static initialization:
```java
public final class CurrencyFormatter {
    public static final CurrencyFormatter INSTANCE;
    static {
        INSTANCE = new CurrencyFormatter();
    }
}
```
This is a representative JVM shape, not a portable source-level guarantee. A companion can have a custom name; Java callers normally access its member through that companion unless a suitable Java bridge is generated.

## Explanation in Arabic

في Kotlin، عندنا 4 تصنيفات رئيسية للكلاسات، كل واحد فيهم معمول علشان يحل مشكلة معمارية محددة:

1. الـ `data class` بيسهّل تمثيل البيانات، لكن **مش بيضمن الثبات**: تقدر تستخدم `var`، و`val` يمنع إعادة إسناد المرجع بس. المترجم بيولّد عمليات مقارنة ونسخ وتفكيك من خصائص الـ primary constructor، والـ `copy()` نسخ سطحي. الخصائص اللي في جسم الكلاس خارج المقارنة والنسخ التلقائي.
2. الـ regular `class` مناسب لما تحتاج تتحكم في الهوية أو السلوك أو شروط صحة الحالة. هو `final` افتراضياً، وممكن يخزن بيانات ثابتة برضه؛ اختيار النوع مش قاعدة مفروضة على المعمارية.
3. الـ `object` بيدي نسخة واحدة لكل class loader، وتهيئته الأولى آمنة بين الخيوط على JVM. ده **ما بيخليش حالة `MutableList` جواه آمنة للتعديل المتزامن**، ومش مكان لحفظ بيانات لازم تعيش بعد موت عملية أندرويد.
4. الـ `companion object` كائن تابع للكلاس، مفيد للمصانع والثوابت، وممكن ينفّذ interface. أعضاؤه مش كلهم `static` في Java تلقائياً؛ `@JvmStatic` عند الحاجة لتوافق الاستدعاء من Java.

## Practical walkthrough

في تطبيق أندرويد بنكي:
- بنستخدم `data class TransferUiState(val amount: Double, val recipient: String)` كلقطة حالة، ونتجنب تسريب مجموعات قابلة للتعديل من حدود الـ API. حتى `List` واجهة قراءة فقط وممكن تخفي قائمة أصلها mutable؛ عند الحدود اعمل snapshot دفاعي عند الحاجة.
- بنستخدم companion object داخل الـ State لتعريف الحالة الابتدائية: companion object { val Initial = TransferUiState(0.0, "") }.
- بنستخدم object لتعريف Singleton عديم الحالة زي PaymentFormatter.
- لو `object` احتفظ بمرجع `Activity` بعد تدميرها، هيطوّل عمرها لحد ما المرجع يتشال أو العملية تنتهي. خليه عديم الحالة قدر الإمكان، واحفظ الحالة الدائمة في مخزن مناسب بدل الذاكرة العامة.

## Why it matters and how it works

These declarations communicate different contracts. Generated data-class operations support value-oriented state but do not enforce immutability. Ordinary classes can model identity or immutable values. An object offers one instance per class loader on Kotlin/JVM but can retain unsafe mutable state. A companion groups creation logic and can implement interfaces.

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

A data class containing `MutableList` is copied, then one copy mutates the list and changes the other copy’s visible state. Replace it with immutable snapshots or deep-copy intentionally. A singleton retaining an Activity leaks the screen; avoid retaining lifecycle-bound references in long-lived objects.

## Production perspective

An Android app can use `data class ProfileUiState` for value-oriented rendering, `class ProfileRepository` for injected stateful behavior, `object` for a stateless formatter, and a companion factory only when construction must enforce an invariant.

## Interview answer — short

A data class generates value-oriented operations from primary-constructor properties, but it can contain var properties and mutable references; copy() is shallow. A regular class gives explicit control over identity, behavior, and inheritance. An object declaration is a singleton per class loader whose initialization is thread-safe on Kotlin/JVM, while its mutable state needs separate synchronization. A companion object groups class-associated factories or constants and is not automatically equivalent to Java static members.

## Interview answer — structured

Start with the contract rather than a slogan. A data class is useful when constructor properties define value equality and a generated shallow copy is appropriate. Kotlin permits var and mutable collections inside it, so immutability is a design choice that needs defensive snapshots at boundaries. Body properties are excluded from generated equality and copy.

A regular class can be either mutable or immutable; choose it when identity, invariants, lifecycle, or explicit equality matter. It is final unless declared open. An object declaration provides one instance per class loader and safe initialization on Kotlin/JVM. It is appropriate for stateless helpers; shared mutable fields still require coordination, and Android process death clears in-memory state.

A companion object is a named or unnamed object attached to a class. It can implement interfaces and contain factories. Java callers use the companion unless a specific static bridge is generated, for example with @JvmStatic. For Android UI state, explain shallow-copy risks and keep lifecycle references out of long-lived objects.

## Interview answer — deep senior

Generated data-class members derive from primary-constructor properties, except where explicit or inherited implementations affect generation. A property declared only in the body does not participate in generated equals(), hashCode(), toString(), componentN(), or copy(). The generated copy() constructs a new outer instance but reuses referenced nested objects. For example, two copies containing the same MutableList observe each other's mutations. Even a val List property is a read-only view rather than a deep-immutability guarantee if a mutable list is retained elsewhere. Use snapshots or persistent immutable collections where the contract requires stable values, and avoid mutating keys already stored in hash-based collections.

A regular class makes equality and lifecycle decisions explicit. A data class cannot be open, abstract, sealed, or inner, but it can extend a suitable base class. An object declaration is initialized safely on first access on Kotlin/JVM, with one instance per class loader. That guarantee covers construction, not arbitrary concurrent writes to its fields. Its in-memory data also disappears after Android process death; persistence belongs in storage and short-lived screen state in lifecycle-aware owners.

A companion object can be named, can implement an interface, and can access private constructors for validated factories. It is a real object rather than a blanket translation of every member to a Java static method. @JvmStatic adds a Java-facing static bridge where interoperability requires it; it should not be presented as an automatic runtime optimization. Explain the source-level contracts first, then mention representative JVM lowering without relying on bytecode shape as the architectural reason.

## How to answer in the interview

- **Why:** Match language constructs to data modeling, identity, and lifecycle requirements.
- **How:** Use `data class` for value-oriented state snapshots, regular `class` for stateful actors, `object` for singletons, and `companion object` for factory methods.
- **Trade-offs:** `data class` generates `copy()`, `equals()`, and `hashCode()` based on primary constructor properties; shallow copying mutable references breaks deep immutability.
- **Failure cases:** Treating an `object` singleton as durable storage across process death, leading to state reset and `NullPointerException` when Android restores the activity.
- **Production solution:** Store session-scoped state in `ViewModel` or `SavedStateHandle`, persist durable data in Room/DataStore, and restrict `object` to stateless utilities.

## Deep-dive talking points

Discuss data-class constructor fields, shallow copy, singleton initialization and process death, companion factories and Java interop.

## Follow-up questions

- **Interviewer:** "Does data class mean immutable?"
  **Answer:** "No. Constructor properties may be val or var, and a val reference can point to a mutable collection. copy() is shallow, so I make snapshots at API boundaries when stable value semantics matter."

- **Interviewer:** "Why is a mutable collection inside a data class risky?"
  **Answer:** "Both copies may hold the same list. Mutating it changes both visible values and can even invalidate hash-based collection assumptions if that list contributes to hashCode()."

- **Interviewer:** "Is an object thread-safe?"
  **Answer:** "Its first initialization is thread-safe on Kotlin/JVM. Mutations to fields inside it are a separate concurrency problem, and the instance is not persistent across Android process death."

- **Interviewer:** "When do you use @JvmStatic in a companion?"
  **Answer:** "When Java callers or a Java framework need a static method on the enclosing class. Normal Kotlin calls need no annotation."

## Self-check rubric

Choose a declaration for UI state, repository, and factory; explain shallow copy and one singleton lifecycle risk.

## References and reviewed-on date

- [Kotlin data classes](https://kotlinlang.org/docs/data-classes.html) — generated members and copy.
- [Kotlin object declarations](https://kotlinlang.org/docs/object-declarations.html) — objects and companions.

Technically reviewed against primary documentation on 2026-10-19.
