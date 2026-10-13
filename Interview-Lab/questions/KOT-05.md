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

A data class automatically generates equals, hashCode, toString, copy, and component functions for data modeling. A regular class is an unspecialized class used for logic and behavior. An object defines a thread-safe singleton managed by the JVM classloader. A companion object belongs to the class itself, serving as a factory or static-like member container.

## Interview answer — structured

In Kotlin, each of these constructs serves a distinct architectural purpose:

A data class is designed for pure data holders. The compiler generates equals, hashCode, toString, componentN, and copy functions based on its primary constructor properties, making it the ideal choice for UI states, network DTOs, and domain entities.

A regular class holds business logic, state machines, or services like ViewModels and Repositories, where identity and lifecycle matter more than structural value comparison.

An object declares a lazy, thread-safe singleton initialized upon first classloader access. It is great for stateless utilities or navigation routes.

Finally, a companion object acts like static members in Java but remains a first-class object that can implement interfaces. I primarily use companion objects for factory methods like fromDto or storing class-scoped constants.

## Interview answer — deep senior

Under the hood on the JVM, these four constructs compile into very different bytecode patterns.

A data class generates bytecode for equals() that compares every primary constructor property, an appropriate hashCode() using primes, and a copy() method with default arguments that uses synthetic flags to selectively replace fields. It is strictly final and cannot be open or abstract. A critical caveat is that properties declared inside the class body are completely ignored by generated equality and copy methods.

An object compiles into a final class with a private constructor and a public static final INSTANCE field initialized in the static initializer (<clinit>). The JVM specification guarantees that class loading is synchronized, making object instantiation inherently thread-safe without explicit locking. However, using objects to store mutable state creates global state, complicates unit testing, and risks memory leaks if Android Context is stored.

A companion object compiles into an inner class named Companion, with a static instance held by the enclosing class. When called from Kotlin, it provides concise syntax, but from Java, callers must use EnclosingClass.Companion.method() unless annotated with @JvmStatic. In production architecture, I use data classes for immutable UI states and DTOs, companion objects for test factories or serializers, and avoid stateful objects in favor of dependency injection with Hilt.

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
