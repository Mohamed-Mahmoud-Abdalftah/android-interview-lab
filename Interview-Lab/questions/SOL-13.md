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

Creating an interface for every class doubles file counts, introduces IDE navigation friction, adds redundant Dagger/Hilt binding boilerplate, and creates 'false abstractions' with no polymorphic value. Concrete classes are simpler, faster to compile, and trivially testable in modern Kotlin.

## Interview answer — structured

The dogmatic practice of creating an interface for every single concrete class (the `IFoo` / `FooImpl` anti-pattern) harms codebases through cognitive friction, maintenance bloat, and compile-time costs.

First, with Navigational Friction & Cognitive Overhead, it doubles the file count in the project. When developers navigate code in Android Studio ('Go to Implementation'), they are constantly routed through empty interface definitions rather than directly to the executing code. Next, a False Abstraction is an interface that has exactly one implementation and will only ever have one implementation is not an abstraction—it is redundant ceremony. True abstractions emerge from polymorphism or strict dependency inversion boundaries, not mechanical habits.
Finally, with Build & Dagger Overhead, every 1-to-1 interface requires an explicit `@Binds` declaration in a Dagger module, bloating generated annotation processor code (KSP) and increasing APK DEX method counts.

In modern Kotlin, concrete classes are open to testing (instantiating pure classes directly or using MockK), meaning speculative interfaces offer zero testing benefit for pure business classes like Use Cases.


## Interview answer — deep senior

Historically, Java codebases relied on interfaces because Java proxies (and legacy Mockito) could not mock final or concrete classes without bytecode manipulation tools like PowerMock. In modern Android with Kotlin and contemporary testing tools, this technical constraint no longer exists.

Furthermore, senior architects distinguish between **API Boundaries** and **Internal Implementation Details**. Interfaces belong at architectural boundaries (such as a Domain Repository consumed by a ViewModel across a multi-module boundary). Within the boundaries of a single cohesive module, internal helper classes, validators, and single-purpose use cases should remain concrete until polymorphism is genuinely required.


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
