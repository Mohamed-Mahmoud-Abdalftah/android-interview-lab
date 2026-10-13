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

The Liskov Substitution Principle (LSP) is violated. Subclasses must be substitutable for their superclass without breaking behavioral contracts. Throwing `UnsupportedOperationException` breaks caller expectations. Fix it by removing the unsupported behavior from the base class and extracting it into a separate interface or composable delegate.

## Interview answer — structured

Throwing `UnsupportedOperationException` from an overridden subclass method is the textbook signature of a **Liskov Substitution Principle (LSP)** violation.

When a superclass declares a public method, it establishes an explicit behavioral contract with calling code: *'Any instance of this type or its subtypes can execute this operation and will return a valid result without throwing unexpected state errors.'*

When a subclass overrides that method with `throw UnsupportedOperationException()`, it violates this contract:
1. It is no longer substitutable for its parent type.
2. Any generic polymorphic collection processing instances of the superclass (`birds.forEach { it.fly() }`) crashes at runtime upon reaching this subtype.
3. It forces calling code to write defensive `if (item !is Penguin)` type checks, which recursively violates the Open/Closed Principle (OCP).

**The Architectural Resolution**:
- Prune the method from the superclass hierarchy.
- Segregate optional capabilities into dedicated interfaces (`Flyable`, `Editable`, `Shareable`).
- Use **Composition over Inheritance**: rather than inheriting a base class with unwanted baggage, inject only the specific behaviors required.

## Interview answer — deep senior

In Android architecture, this appears in repositories and storage implementations. Suppose a base `interface CacheStorage<T>` declares `read()`, `write()`, and `clear()`. A read-only `AssetStorage` implementation backed by the APK's read-only assets directory throws `UnsupportedOperationException("Cannot write to APK assets")` inside `write()`.

The resolution requires applying ISP and LSP together: split the contract into `ReadableStorage<T>` and `WritableStorage<T>`. `AssetStorage` implements only `ReadableStorage`, ensuring that clients requiring write operations can never accidentally be passed an un-writable storage instance at compile time.

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
