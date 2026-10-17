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

Kotlin provides four distinct class constructs tailored for specific architectural responsibilities:
1. data class: A specialized class designed strictly as an immutable value carrier. The compiler automatically synthesizes structural methods based on properties declared in the primary constructor: equals(), hashCode(), toString(), copy(), and componentN() destructuring operators.
2. Regular class: A standard object-oriented class encapsulating mutable state, complex business logic, open inheritance hierarchies, and polymorphic behavior. It does not synthesize data operations automatically.
3. object: Declares a thread-safe Singleton instance lazily initialized upon first class loading by the JVM. It encapsulates global stateless utilities or shared application-wide coordinators.
4. companion object: A singleton object scoped within the namespace of an enclosing class. It acts as the idiomatic Kotlin replacement for Java static members, providing factory methods, compile-time constants, and interface implementations linked to the class.

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
// 1. Data Class: Immutable UI state snapshot
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
Decompiling an object reveals standard JVM static initialization:
```java
public final class CurrencyFormatter {
    public static final CurrencyFormatter INSTANCE;
    static {
        INSTANCE = new CurrencyFormatter();
    }
}
```
Decompiling a companion object reveals a static inner class instantiated as a static field named Companion inside the enclosing class.

## Explanation in Arabic

في Kotlin، عندنا 4 تصنيفات رئيسية للكلاسات، كل واحد فيهم معمول علشان يحل مشكلة معمارية محددة:

1. الـ data class: معمول خصيصاً لتمثيل حوامل البيانات (Data Holders). المترجم بيولد له تلقائياً equals و hashCode و toString و copy و componentN بناءً على حقول الـ Primary Constructor.
2. الـ Regular Class: كلاس عادي للخدمات والمنطق (Services, ViewModels, Repositories). افتراضياً مقفول ضد الوراثة (final)، ومبيولدش دوال مقارنة تلقائية.
3. الـ object: يعرف Singleton حقيقي على مستوى الـ Process، بيتم إنشاؤه بطريقة Thread-safe بواسطة الـ ClassLoader في الـ static initializer (<clinit>).
4. الـ companion object: كائن مرتبط بالكلاس نفسه وهو البديل للـ static members في Java، ومناسب جداً للـ Factory Methods وحفظ الـ Constants.

## Practical walkthrough

في تطبيق أندرويد بنكي:
- بنستخدم data class لتمثيل حالة الشاشة TransferUiState(val amount: Double, val recipient: String).
- بنستخدم companion object داخل الـ State لتعريف الحالة الابتدائية: companion object { val Initial = TransferUiState(0.0, "") }.
- بنستخدم object لتعريف Singleton عديم الحالة زي PaymentFormatter.
- احذر من تخزين Activity Context أو مراجع دورية داخل object؛ ده هيعمل Memory Leak طول عمر التطبيق لأن الـ Singleton مبيتحذفش أبداً من الـ Garbage Collector.

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

In Kotlin, a data class is an immutable value carrier with auto-generated equals, hashCode, toString, and copy methods. A regular class encapsulates state and behavior with custom lifecycles and inheritance. An object defines a thread-safe singleton initialized upon class loading. A companion object is a singleton tied to an enclosing class, serving as a factory or holding static-like constants.

## Interview answer — structured

Kotlin categorizes class declarations according to their architectural purpose. A data class is purpose-built to model state, automatically synthesizing value-based equals, hashCode, copy, and destructuring functions from primary constructor properties. A regular class, by contrast, is intended for behavior, lifecycle management, and complex object-oriented hierarchies.

Singletons are first-class language constructs. An object declaration creates a thread-safe singleton instantiated lazily on class load, perfect for stateless utility formatters or navigation routers. Meanwhile, a companion object belongs to the namespace of an enclosing class, offering a clean idiomatic alternative to Java static factory methods while retaining the ability to implement interfaces.

In production, a common failure mode is placing mutable collections inside data classes. Because the compiler-generated copy method performs a shallow copy, mutating the collection in one instance corrupts all copies across the system.

Senior engineers model UI state using immutable data classes, encapsulate domain logic inside regular classes with dependency injection, and leverage companion objects for typed factory creation.


## Interview answer — deep senior

Analyzing the bytecode generated for each class construct reveals critical memory and runtime performance trade-offs. For a data class, kotlinc synthesizes equals and hashCode by combining all primary constructor properties. If a property is added to the class body rather than the primary constructor, the compiler omits it from generated equality and copy methods, which can lead to subtle bugs. Furthermore, each property generates a synthetic componentN() method enabling destructuring declarations; however, destructuring positional indices can easily cause bugs if constructor parameters are reordered during refactoring.

The object construct compiles to a final Java class with a private constructor and a public static final field named INSTANCE, initialized in a static class initializer block (<clinit>). This leverages the JVM's class-loading mechanism to guarantee thread-safe initialization without double-checked locking overhead. However, in Android architectures, relying on object singletons for stateful components hampers testability and prevents dependency injection scoping.

The companion object similarly compiles to a static nested class named Companion with an enclosing instance holder. When invoking companion methods from Java without @JvmStatic, callers must access EnclosingClass.Companion.method(), requiring an extra reference dereference. Marking companion methods with @JvmStatic instructs the compiler to generate true static forwarding methods on the outer class, optimizing interop performance and reducing method dispatch overhead.

In large-scale Android applications, senior engineers enforce strict separation: data classes must remain deeply immutable value objects used for Compose UI states and Room entities; regular classes represent injected, testable domain interactors; standalone objects are restricted to stateless utilities; and companion objects are reserved for domain factories and Parceler serializers.

## How to answer in the interview

- **Why:** Match language constructs to data modeling, identity, and lifecycle requirements.
- **How:** Use `data class` for immutable state payloads, regular `class` for stateful actors, `object` for singletons, and `companion object` for factory methods.
- **Trade-offs:** `data class` generates `copy()`, `equals()`, and `hashCode()` based on primary constructor properties; shallow copying mutable references breaks deep immutability.
- **Failure cases:** Treating an `object` singleton as durable storage across process death, leading to state reset and `NullPointerException` when Android restores the activity.
- **Production solution:** Store session-scoped state in `ViewModel` or `SavedStateHandle`, persist durable data in Room/DataStore, and restrict `object` to stateless utilities.

## Deep-dive talking points

Discuss data-class constructor fields, shallow copy, singleton initialization and process death, companion factories and Java interop.

## Follow-up questions

- **Interviewer:** "Why can't a data class be marked as open or abstract?"
  **Answer:** "Because the compiler generates equals(), hashCode(), and copy() based strictly on primary constructor properties. If a data class were subclassed with additional properties, the symmetric contract of equals() (a.equals(b) == b.equals(a)) would break, leading to subtle bugs in collections. To model polymorphic hierarchies, we use sealed classes or sealed interfaces with data class leaves."

- **Interviewer:** "How is a Kotlin object guaranteed to be thread-safe without using synchronized blocks?"
  **Answer:** "In JVM bytecode, the singleton instance is assigned in the static class initializer block (<clinit>). The JVM specification strictly guarantees that class loading and static initialization are atomic and thread-safe. No thread can see the instance in a partially constructed state."

- **Interviewer:** "When should you annotate a companion object method with @JvmStatic?"
  **Answer:** "You use @JvmStatic when the method must be called from Java code as a real static method, such as ClassName.method() rather than ClassName.Companion.method(). It is also required when creating methods for certain frameworks or JUnit 5 @MethodSource factories that reflectively look for static methods."

## Self-check rubric

Choose a declaration for UI state, repository, and factory; explain shallow copy and one singleton lifecycle risk.

## References and reviewed-on date

- [Kotlin data classes](https://kotlinlang.org/docs/data-classes.html) — generated members and copy.
- [Kotlin object declarations](https://kotlinlang.org/docs/object-declarations.html) — objects and companions.

Technically reviewed against primary documentation on 2026-10-13.
