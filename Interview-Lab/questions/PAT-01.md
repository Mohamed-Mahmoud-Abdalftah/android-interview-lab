---
id: "PAT-01"
question: "What is a design pattern, and how is it different from architecture?"
topic: "Design Patterns"
code: "PAT"
group: "A"
phase: 2
priority: "P1"
order: 192
editorial_status: "reviewed"
---

# PAT-01

## Original interview question

What is a design pattern, and how is it different from architecture?

## What the interviewer evaluates

Define pattern as reusable local design idea and distinguish it from system-level architecture and implementation recipe.

## Explanation in Arabic

ما هو نمط التصميم (Design Pattern) وكيف يختلف جوهرياً عن المعمارية (Architecture)؟

1. ما هي المعمارية (Architecture - النظرة الشاملة من أعلى Macro)؟
   - المعمارية هي **المخطط الهيكلي العام للبرنامج (System Blueprint)**.
   - تحدد: كيفية تقسيم النظام ككل إلى طبقات (Presentation, Domain, Data)، اتجاه تدفق البيانات والتبعيات (Clean Architecture / MVI)، وكيف تتواصل الموديولات الكبيرة مع بعضها.
   - قرارات المعمارية صعبة ومكلفة التغيير بعد اتخاذها؛ تغيير المعمارية يشبه تغيير أساسات المبنى بالكامل.

2. ما هو نمط التصميم (Design Pattern - النظرة الدقيقة الموضعية Micro)؟
   - نمط التصميم هو **حل نموذجي قابل لإعادة الاستخدام لمشكلة برمجية شائعة ومحددة تظهر داخل كود كلاس أو كلاسين**.
   - أمثلة: كيفية إنشاء كائن معقد (Builder / Factory)، كيفية مطابقة واجهة غير متوافقة (Adapter)، أو كيفية إشعار عدة كائنات بحدث ما (Observer).
   - أنماط التصميم تقع *داخل* المعمارية ويمكن استبدالها أو تعديلها موضعياً بسهولة.

3. الخلاصة:
   - المعمارية تجيب على: *"كيف يتدفق النظام ككل وتتوزع الطبقات؟"*
   - نمط التصميم يجيب على: *"كيف تحل كلاسات هذه الميزة مشكلة محددة في الكود؟"*

## Practical walkthrough

المقارنة العملية بين القرار المعماري ونمط التصميم في تطبيق Android:
```kotlin
// 1. قرار معماري (Architecture): اختيار Clean Architecture و UDF:
// الطبقات مقسمة إلى Presentation و Domain و Data مع تدفق أحادي الاتجاه:
class CheckoutViewModel(private val checkoutUseCase: CheckoutUseCase) : ViewModel() {
    val uiState: StateFlow<CheckoutUiState> = ...
}

// 2. نمط تصميم موضعي (Design Pattern - Strategy Pattern):
// داخل طبقة Data، يتم استخدام نمط Strategy لاختيار وسيلة الدفع المناسبة:
interface PaymentStrategy {
    suspend fun pay(amount: Long): PaymentResult
}
class StripeStrategy : PaymentStrategy { ... }
class PayPalStrategy : PaymentStrategy { ... }
// هذا النمط يعيش داخل تفاصيل طبقة Data ولا يؤثر على هيكل المعمارية العام للنظام!
```

## Why it matters and how it works

Patterns provide shared vocabulary for object collaboration; architecture sets larger boundaries, data flow and quality attributes. A pattern is applied within a context and can be combined with other patterns. The implementation must still honor lifecycle, concurrency and failure contracts.

## Worked example

Example: a checkout app uses a repository boundary to coordinate Room/network, a Strategy for multiple payment providers, and Adapter wrappers for SDK callback differences. Its architecture also defines UI/data modules, server authority and process-death recovery. These are different scales of decision.

## Trade-offs and decision criteria

A named pattern can speed review when the team shares its meaning. Forcing pattern classes into a simple feature adds indirection. Kotlin language features such as `object`, lambdas and delegation can implement the intent with less boilerplate.

## Failure modes

A team calls a global `object ApiManager` “Singleton pattern” and stores Activity plus token state in it. The name hides lifecycle leak and process-death fragility. Review ownership and invariants, not labels.

## Production perspective

A finance app uses an SDK adapter at data boundary while the app architecture keeps payment policy and server verification separate. Contract tests show whether swapping SDKs preserves behavior.

## Interview answer — short

Architecture is the macro-level system blueprint defining global layers, module boundaries, and dependency directions (e.g. Clean Architecture, MVI). Design patterns are micro-level, localized templates solving specific recurring object-oriented problems within classes (e.g. Builder, Strategy, Adapter).

## Interview answer — structured

The distinction between Architecture and Design Patterns is fundamentally a matter of scope and structural impact.

First, **Architecture (Macro-Level / System Blueprint)**. Next, defines the high-level organization of the entire software system.
Establishes foundational layers (Presentation, Domain, Data), dependency boundaries, data flow rules (Unidirectional Data Flow), and modularization strategy. Architectural decisions are costly and difficult to change once implemented (e.g. Migrating from Monolithic MVC to Multi-Module Clean Architecture).
Answers: *'Where do responsibilities live and in which direction does information flow across the app?'* **Design Patterns (Micro-Level / Tactical Solutions)**.
Localized, reusable idioms solving specific recurring design challenges between collaborating classes. Examples: Using the Builder pattern for complex notification construction, the Adapter pattern for converting third-party analytics APIs, or the Strategy pattern for dynamic fee calculations.
Tactical decisions that can be refactored within a single package without destabilizing the broader system. Finally, answers: *'How should these specific objects collaborate to solve a localized problem?'*


## Interview answer — deep senior

A helpful mental model is urban planning: Architecture is the zoning laws, highway networks, and utility grids of a city. Design patterns are the architectural blueprints for individual houses, doorways, and interior plumbing.

Architecture dictates the constraints within which design patterns operate. For example, inside a Clean Architecture system, you might employ the **Repository pattern** to mediate data access, the **Factory pattern** to instantiate network decoders, and the **Observer pattern** (`Flow`) to project UI state. The design patterns live harmoniously within the architectural boundaries established by the system.


## How to answer in the interview

- **Why:** Pattern vocabulary helps only when it names a real local change point.
- **How:** Contrast Adapter/Strategy inside checkout with app-wide ownership and server authority.
- **Trade-off:** Avoid ceremonial classes for one stable implementation.
- **Failure case:** A named Singleton still leaks Activity or loses state on process death.
- **Production solution:** Show the boundary, tests, and expected variation before naming the pattern.

## Deep-dive talking points

Compare object collaboration with module boundaries, and identify Kotlin shorthand plus lifecycle caveats.

## Follow-up questions

- **Interviewer:** "Can a bad design pattern ruin good architecture?"
  **Answer:** "Yes. If an anti-pattern like a monolithic God-Singleton is introduced, it creates hidden shared mutable state across architectural boundaries, corrupting the Clean Architecture dependency rule."

- **Interviewer:** "Is the Repository pattern an architectural pattern or a design pattern?"
  **Answer:** "It functions at both levels: tactically as a mediator design pattern abstracting data access, and architecturally as the foundational boundary between Data and Domain layers."

## Self-check rubric

Define pattern and architecture at different scales and give one Android example of each.

## References and reviewed-on date

- [GoF Design Patterns, publisher](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — original pattern catalog and categories.
- [Android architecture guide](https://developer.android.com/topic/architecture) — app-level boundaries.

Technically reviewed against primary documentation on 2026-10-13.
