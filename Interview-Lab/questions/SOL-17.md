---
id: "SOL-17"
question: "A subclass needs to throw UnsupportedOperationException for a base behavior. What design principle might be violated?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "C"
phase: 2
priority: "P1"
order: 188
editorial_status: "reviewed"
---

# SOL-17

## Original interview question

A subclass needs to throw UnsupportedOperationException for a base behavior. What design principle might be violated?

## What the interviewer evaluates

Recognize a likely LSP violation while allowing legitimately optional contracts.

## Concept and technical explanation

When a subclass throws UnsupportedOperationException to opt out of a method inherited from its parent class or interface, the Liskov Substitution Principle (LSP) is directly violated. LSP, formalized by Barbara Liskov, asserts that subtypes must be completely substitutable for their base types without altering program correctness or violating consumer expectations. Throwing an exception strengthens method preconditions and shatters behavioral subtyping, breaking the contract promised by the base abstraction. The solution requires replacing monolithic inheritance hierarchies with fine-grained interfaces (Interface Segregation) or composition.

## Practical walkthrough (English)

Contrasting an LSP violation with behavioral subtyping in an Android data repository:
```kotlin
// BAD ANTI-PATTERN: Violates LSP (Subclass breaks base contract by throwing runtime exception)
interface DocumentStorage {
    suspend fun readDocument(id: String): Document
    suspend fun writeDocument(doc: Document) // Base contract implies all implementations can write!
}

class ReadOnlyCloudDocumentStorage : DocumentStorage {
    override suspend fun readDocument(id: String) = fetchFromCloud(id)
    override suspend fun writeDocument(doc: Document) {
        // Blatant LSP Violation! Calling code expecting DocumentStorage crashes at runtime!
        throw UnsupportedOperationException("Read-only cloud storage cannot write documents")
    }
}

// ARCHITECTURAL BEST PRACTICE: Segregated behavioral contracts adhering to LSP
interface ReadableStorage { suspend fun readDocument(id: String): Document }
interface WritableStorage { suspend fun writeDocument(doc: Document) }

// Fully substitutable read-only storage
class ReadOnlyCloudStorage(private val api: DocApi) : ReadableStorage {
    override suspend fun readDocument(id: String) = api.getDocument(id)
}

// Fully substitutable read-write storage
class LocalDiskStorage(private val dao: DocDao) : ReadableStorage, WritableStorage {
    override suspend fun readDocument(id: String) = dao.getDocument(id)
    override suspend fun writeDocument(doc: Document) = dao.saveDocument(doc)
}
```

## Explanation in Arabic

عندما يضطر كلاس فرعي (Subclass) لرمي `UnsupportedOperationException` لتجاهل سلوك مفروض عليه من الكلاس الأساسي: ما هو المبدأ الذي تم انتهاكه؟ وكيف يُعالج؟

1. المبدأ المنتهك حتماً: مبدأ لسكوف للاستبدال (Liskov Substitution Principle - LSP):
   - رمي `UnsupportedOperationException` هو الدليل القاطع والجريمة المشهودة على انتهاك **LSP**!
   - الكلاس الأساسي (Superclass) قطع وعداً بأن هذه العملية مدعومة ومتاحة. عندما يقوم الكلاس الفرعي بنقض هذا الوعد ورمي استثناء، فإنه **يضعف الشروط اللاحقة (Weakens Postconditions)** ويفشل في العمل كبديل صالح لكلاسه الأساسي.

2. ما هي الآثار الجانبية لهذا الانتهاك؟
   - انهيار البرنامج في وقت التشغيل (Runtime Crashes)؛ الكود المستدعي الذي يتعامل مع الكلاس الأساسي لا يتوقع هذا الاستثناء، مما يفجر أخطاء غير معالجة.
   - إجبار الكود الخارجي على عمل `if (instance is SpecificSubclass)` قبل الاستدعاء، مما يكسر مبدأ Polymorphism تماماً!

3. كيف يُعالج هندسياً؟
   - **إزالة السلوك من الكلاس الأساسي**: الكلاس الأساسي يجب أن يحتوي فقط على القاسم المشترك الأعظم (Greatest Common Divisor) للسلوكيات الحقيقية لجميع الأبناء دون استثناء.
   - **استبدال الوراثة بالتركيب (Composition)**: فصل السلوك غير المشترك في واجهة مستقلة (Capability Interface) أو Delegate خارجي.

## Practical walkthrough

تصحيح انتهاك LSP الذي يرمي UnsupportedOperationException:
```kotlin
// ❌ انتهاك صارخ لـ LSP: طائر لا يستطيع الطيران يرمي استثناء في دالة موروثة!
open class Bird {
    open fun fly(): Altitude = Altitude(1000)
}

class Penguin : Bird() {
    override fun fly(): Altitude {
        // 💥 يكسر LSP: المستدعي يتوقع طيراناً، والبطريق يرمي Crash!
        throw UnsupportedOperationException("Penguins cannot fly!")
    }
}

// ✅ الحل المعماري السليم: تقسيم الشجرة أو استخدام Composition:
open class Bird // طائر عام (يأكل، ينام، يتكاثر)

interface Flyable {
    fun fly(): Altitude
}

class Eagle : Bird(), Flyable {
    override fun fly(): Altitude = Altitude(2000)
}

class Penguin : Bird() {
    // لا ينفذ Flyable؛ الكود الذي يبحث عن طيران لن يستدعيه، ولن يحدث أي استثناء!
}
```

## Why it matters and how it works

LSP is judged by behavioral expectations for valid calls. An unsupported operation often means the base abstraction promised too much. Narrow capabilities can let clients request exactly what they need.

## Worked example

Conceptual Kotlin: `interface Reader { suspend fun read(id: String): Data? }` and `interface Writer { suspend fun save(data: Data) }`; a read-only cache implements only `Reader`. A writable store implements both. Callers needing `save` depend on `Writer`, not a broad `Storage`.

## Trade-offs and decision criteria

Splitting interfaces adds types but makes capabilities explicit. A documented partial operation can be valid in some APIs, though callers must handle its result and it may be less ergonomic. Avoid subclass checks as the primary design.

## Failure modes

A UI expects all repositories to support refresh; a local-only subclass throws when the refresh button is tapped. The crash appears only in one build variant. Contract tests reveal the mismatch; redesign interface or UI capability selection.

## Production perspective

A document app has read-only shared files and editable local files. It exposes read and write capabilities separately, and UI derives whether Edit is available from the actual domain permission, not a subclass name.

## Interview answer — short

Throwing an UnsupportedOperationException in a subclass directly violates the Liskov Substitution Principle (LSP). LSP dictates that any subclass must be safely substitutable for its parent type without breaking caller expectations. When a subclass refuses an inherited method by throwing an exception, it shatters the behavioral contract, causing runtime crashes for callers relying on polymorphism. The proper fix is segregating the bloated base contract into smaller, focused interfaces that subclasses can fulfill completely.

## Interview answer — structured

When a subclass throws an UnsupportedOperationException for an inherited method, it is the textbook indicator of a broken Liskov Substitution Principle (LSP).
LSP asserts that if program S is designed to operate on base type T, S must function correctly when given any subtype of T without knowing the concrete variant. A base class or interface establishes an implicit contract: every public method represents a valid, supported capability.
When a subclass overrides a method with UnsupportedOperationException, it breaks this contract.
In Android, this anti-pattern frequently surfaces in repository hierarchies and collection adapters. For instance, creating a general-purpose DocumentStorage interface with both read and write methods, and then implementing a ReadOnlyDocumentStorage that throws an exception in the write method. When a background sync worker or ViewModel invokes write, the application crashes in production.
The remedy is to refactor the inheritance hierarchy using the Interface Segregation Principle.
Split the contract into fine-grained interfaces: ReadableStorage and WritableStorage.
Classes that only support reading implement only the readable contract. Clients expecting write capabilities accept only WritableStorage, transforming runtime exception crashes into safe, compile-time type guarantees.

## Interview answer — deep senior

Under the hood, throwing UnsupportedOperationException shatters the mathematical foundation of Design by Contract that governs the Liskov Substitution Principle.
In contract theory, a method defines preconditions (requirements the caller must satisfy before execution) and postconditions (guarantees the method provides upon completion). To maintain behavioral subtyping, a subtype may weaken preconditions (demand less) and strengthen postconditions (guarantee more), but it must never strengthen preconditions.
Throwing an UnsupportedOperationException effectively strengthens the precondition to 'false'—meaning the method cannot be called under any condition whatsoever. This shatters polymorphism at the bytecode level, forcing callers to employ dirty runtime inspections like 'if (storage is ReadOnlyStorage)' before invoking methods, defeating the entire purpose of object-oriented design.
A notorious framework example occurred in legacy Java with Collections.unmodifiableList(), which implemented java.util.List but threw UnsupportedOperationException on add(). If an Android developer passed an unmodifiable list into an adapter expecting a standard mutable list, the application crashed with a fatal exception.
Kotlin eradicated this design defect at the language level by bifurcating the collection hierarchy into List (read-only covariant interface) and MutableList (read-write invariant interface).
Senior Android engineers apply this exact principle to domain modeling: never use exceptions to opt out of inherited contracts. Segregate interfaces or switch to composition so that every type satisfies its full contract unconditionally.

## How to answer in the interview

- **Why:** State the base promise.
- **How:** show reader/writer split.
- **Trade-offs:** discuss documented unsupported outcome.
- **Failure cases:** cite runtime save crash.
- **Production solutions:** finish with contract tests and capability-aware UI..

## Deep-dive talking points

Contrast invalid input failure with unsupported valid operation; design capability interfaces and contract tests.

## Follow-up questions

- **Interviewer:** "How does throwing UnsupportedOperationException force calling code to violate OCP?"
  **Answer:** "Callers are forced to add `if (item is SpecificClass)` checks to skip the unsupported operation. Every time a new non-supporting subclass is created, callers must be modified with new `if/else` checks, violating OCP."

- **Interviewer:** "Can Java's Collections API be criticized for this exact LSP violation?"
  **Answer:** "Yes! `java.util.Collections.unmodifiableList()` returns a `List` whose `add()` method throws `UnsupportedOperationException`, which is a famous language-level violation of LSP in the standard Java library."

## Self-check rubric

State the base promise, classify a thrown case correctly, and redesign a read-only subtype.

## References and reviewed-on date

- [Liskov and Wing, A Behavioral Notion of Subtyping](https://www.cs.columbia.edu/~wing/publications/LiskovWing94.pdf) — substitution.
- [Kotlin inheritance](https://kotlinlang.org/docs/inheritance.html) — override mechanics.

Technically reviewed against primary documentation on 2026-10-13.
