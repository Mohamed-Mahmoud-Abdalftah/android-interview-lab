---
id: "SOL-13"
question: "Why can creating an interface for every class make design worse?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "B"
phase: 2
priority: "P1"
order: 184
editorial_status: "reviewed"
---

# SOL-13

## Original interview question

Why can creating an interface for every class make design worse?

## What the interviewer evaluates

Explain interface cost and distinguish useful polymorphism from ceremonial one-to-one pairs.

## Concept and technical explanation

Creating an interface for every single concrete class—frequently referred to as the 'Interface-itis' or '1:1 Interface-to-Implementation' anti-pattern—degrades software architecture by adding needless indirection, cognitive friction, and maintenance overhead without providing genuine abstraction. While abstractions are essential at genuine architectural boundaries (such as isolating domain logic from external data sources), blindly pairing every simple utility, helper, or single-implementation service with an interface violates YAGNI (You Aren't Gonna Need It) and the KISS principle. In modern Kotlin, where classes can be easily faked or mocked directly on the JVM, unjustified interfaces pollute IDE navigation and create illusory flexibility.

## Practical walkthrough (English)

Contrasting unnecessary interface ceremony with pragmatic, clean concrete design:
```kotlin
// BAD ANTI-PATTERN: Speculative generality creating 1:1 Interface-to-Implementation bloat
interface UserProfileDateFormatter { // Only used in one place, has exactly one implementation
    fun formatJoinedDate(timestamp: Long): String
}

class UserProfileDateFormatterImpl @Inject constructor() : UserProfileDateFormatter {
    override fun formatJoinedDate(timestamp: Long): String = DateUtils.format(timestamp)
}

// ARCHITECTURAL BEST PRACTICE: Pragmatic concrete class without unnecessary abstraction
// Cohesive, pure, deterministic Kotlin class that is trivially testable on JVM without an interface!
class UserProfileDateFormatter @Inject constructor() {
    fun formatJoinedDate(timestamp: Long): String {
        return DateTimeFormatter.ISO_INSTANT.format(Instant.ofEpochMilli(timestamp))
    }
}

// Inject directly into callers: Zero navigation friction, zero boilerplate maintenance!
class UserProfileViewModel @Inject constructor(
    private val dateFormatter: UserProfileDateFormatter // Direct concrete dependency
) : ViewModel()
```

## Explanation in Arabic

لماذا قد يؤدي إنشاء واجهة (Interface) لكل كلاس إلى تدهور التصميم وجعله أسوأ (Interface Exhaustion / Over-abstraction)؟

1. ظاهرة الـ Interface-itis (الإفراط في إنشاء الواجهات):
   - بعض المطورين يعتقدون خطأً أن الاحترافية تعني كتابة `interface UserProfileUseCase` ومعه `class UserProfileUseCaseImpl`، و `interface CartCalculator` ومعه `class CartCalculatorImpl` لكل كلاس في التطبيق!

2. لماذا يجعل هذا التصميم أسوأ؟
   - **مضاعفة حجم وتعقيد الكود بلا داعٍ (Double the Code / Navigational Friction)**: يتضاعف عدد ملفات المشروع بنسبة 100%. عند الضغط على الدالة في Android Studio (Ctrl+B)، لا تذهب مباشرة للكود الحقيقي بل للـ Interface الفارغ، مما يشتت المطورين.
   - **تضخم تكلفة الصيانة وتوليد الكود (Maintenance & DI Overhead)**: يتطلب كل Interface كتابة سطر `@Binds` إضافي في Dagger/Hilt، مما يزيد من وقت الـ Annotation Processing وحجم ملفات الـ DEX.
   - **تجريد زائف (False Abstraction)**: التجريد الذي ليس له سوى تطبيق حقيقي وحيد ولن يتغير أبداً هو تجريد وهمي لا يقدم أي قيمة تعددية (Polymorphism).

3. متى ننشئ Interface؟
   - فقط عند وجود حدود معمارية حقيقية (Clean Architecture DIP)، أو وجود تطبيقات متعددة بالفعل (Polymorphism)، أو لعزل خدمات النظام الخارجية الصعبة.

## Practical walkthrough

المقارنة بين البويلربليت غير المجدي والتصميم البراغماتي النظيف:
```kotlin
// ❌ OVER-ABSTRACTION: واجهة عقيمة لكل كلاس UseCase بسيط:
interface CalculateTaxUseCase {
    fun execute(subtotal: Long): Long
}
class CalculateTaxUseCaseImpl : CalculateTaxUseCase {
    override fun execute(subtotal: Long): Long = (subtotal * 0.15).toLong()
}
// بالإضافة لكتابة Hilt Module كامل لربط Interface بـ Impl لمجرد عملية حسابية!

// ✅ تصميم نقي وعملي: الكلاس الملموس كافٍ ومثالي وقابل للاختبار الفوري:
class CalculateTaxUseCase {
    operator fun invoke(subtotal: Long): Long = (subtotal * 0.15).toLong()
}
// في الـ Test: يتم استدعاؤه فورياً: CalculateTaxUseCase().invoke(100L) دون أي Mocking أو DI!
```

## Why it matters and how it works

Abstraction is a trade-off. It can decouple change and enable substitution, but every interface adds names, wiring and maintenance. A one-to-one mirror is not automatically a stable contract.

## Worked example

Example: `PriceFormatter(locale)` has one deterministic implementation and can be tested directly. `PaymentGateway` has two SDK adapters and a policy consumer, so an interface has a clear role. Hilt can inject either a concrete formatter or a bound gateway interface.

## Trade-offs and decision criteria

Premature abstraction can be revised later after a second implementation appears. Conversely, delaying a boundary when policy imports a volatile SDK can make testing and change costly. Use evidence from change patterns.

## Failure modes

A new field requires editing `ProfileFormatter`, `IProfileFormatter`, a binding module, fake, and dozens of mocks, with no behavior variation. The interface has created work without reducing coupling. Simplify and test public behavior.

## Production perspective

A feature team keeps concrete validators and formatters internal, with narrow interfaces for session state and payment providers. Architecture tests ensure DTOs do not leak across those meaningful contracts.

## Interview answer — short

Creating an interface for every class makes design worse because it introduces speculative generality, doubles the number of files, and adds cognitive friction without delivering architectural value. In modern Kotlin, you do not need an interface to write unit tests on the JVM. Unless a class represents a genuine architectural boundary, has multiple runtime implementations, or requires physical decoupling across Gradle modules, writing a direct, cohesive concrete class is far cleaner and adheres to YAGNI and KISS.

## Interview answer — structured

The dogmatic rule of creating an interface for every class is a legacy habit from early Java enterprise development that actively harms modern Android codebases.
When developers automatically create an interface alongside every single class (like UserDateFormatter and UserDateFormatterImpl), the codebase suffers from severe architectural bloat.
First, it creates cognitive tax and hurts developer ergonomics. When navigating code in Android Studio, clicking on a method call jumps to the interface definition rather than the actual execution logic, requiring an extra navigation step (Cmd+Option+B) every single time.
Second, it violates YAGNI (You Aren't Gonna Need It). In ninety percent of cases, that single implementation never acquires a second variant throughout the entire application lifecycle. The abstraction was purely speculative.
Third, the historical argument that interfaces were strictly necessary for unit testing is obsolete. Modern Kotlin testing tools like Mockk easily mock final classes, and pure domain classes can be instantiated directly in JVM tests without any mocks at all.
Senior engineers introduce interfaces purposefully: at module boundaries, for polymorphic strategies, or to decouple pure domain rules from volatile I/O infrastructure.

## Interview answer — deep senior

Under the hood, widespread 1:1 interface-to-implementation bloat degrades compilation efficiency, increases DEX method count, and impairs runtime inline optimizations in the Android ART runtime.
Every interface declared in Kotlin generates its own .class bytecode file and corresponding DEX type descriptor entry. In large applications with thousands of classes, redundant interfaces inflate the total method references inside the DEX file, inching closer to multidex splitting limits and bloating the download APK size.
At runtime, invoking a method on an interface requires ART to execute an invoke-interface bytecode instruction rather than an invoke-virtual or invoke-direct instruction. While ART's Inline Cache (IC) mitigates interface call overhead for monomorphic call sites, invoke-interface still involves a slightly more complex runtime dispatch resolution table lookup compared to direct devirtualized calls.
Furthermore, redundant interfaces create high maintenance friction during rapid refactoring. If an engineer changes a method parameter type, they must update both the interface contract and the implementation class in tandem, doubling Git diff noise.
Staff engineers follow the Rule of Three: write clean, cohesive concrete classes first. Extract an interface only when a second genuine implementation emerges, or when physical decoupling across Gradle module boundaries is strictly mandated by Dependency Inversion. This pragmatic approach keeps codebases lean, understandable, and immediately navigable.

## How to answer in the interview

- **Why:** Use formatter versus gateway.
- **How:** state change-boundary test.
- **Trade-offs:** discuss extra files.
- **Failure cases:** flag interface/implementation lockstep.
- **Production solutions:** finish with delayed, contract-driven abstraction..

## Deep-dive talking points

Compare one-to-one interface pair with provider contract; inspect client and change axis.

## Follow-up questions

- **Interviewer:** "What is the 'Rule of Three' regarding abstractions?"
  **Answer:** "Do not extract an abstraction or interface until you find yourself writing the same code or needing polymorphism for the third time. Premature abstraction is worse than slight duplication."

- **Interviewer:** "Does creating an interface make code automatically decoupled?"
  **Answer:** "No. If an interface leaks implementation details in its method signatures or exceptions (e.g. `fun fetchSqliteUser()`), it is tightly coupled despite being an interface."

## Self-check rubric

Choose a formatter and a payment gateway; justify which one needs an interface and why.

## References and reviewed-on date

- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) — adaptable design guidance.
- [Android dependency injection](https://developer.android.com/training/dependency-injection) — constructor injection without mandatory interfaces.

Technically reviewed against primary documentation on 2026-10-13.
