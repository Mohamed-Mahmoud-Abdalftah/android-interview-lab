---
id: "SOL-20"
question: "How would you explain SOLID trade-offs to a team overengineering a small feature?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "C"
phase: 2
priority: "P1"
order: 191
editorial_status: "reviewed"
---

# SOL-20

## Original interview question

How would you explain SOLID trade-offs to a team overengineering a small feature?

## What the interviewer evaluates

Communicate practical trade-offs to a team and propose a small, evidence-based design.

## Explanation in Arabic

كيف تشرح توازنات ومقايضات SOLID (SOLID Trade-offs) لفريق يقوم بهندسة مفرطة (Overengineering) لميزة صغيرة وبسيطة؟

1. الفهم السليم لمبادئ SOLID (Principles, not Dogma):
   - مبادئ SOLID هي **أدوات إرشادية لحل مشاكل التعقيد والاقتران**، وليست قوانين دينية مقدسة يجب تطبيقها بحذافيرها على كل سطر كود!
   - التجريد (Abstraction) له تكلفة حقيقية: زيادة عدد الملفات، تعقيد التصفح، زيادة وقت الـ Build، وبطء وتيرة الإنجاز (Velocity Loss).

2. خطة الحوار والإقناع في الفريق (Engineering Coaching):
   - **البدء بالقيمة التجارية (Business Value & Time-to-Market)**: تذكير الفريق أن الهدف الأساسي هو تقديم قيمة للمستخدم وليس إرضاء الـ Design Patterns. تطبيق 5 طبقات لميزة قراءة نص بسيط يؤخر طرح الميزة أسبوعين بلا أي مبرر!
   - **التذكير بمبدأ YAGNI و KISS**:
     * **YAGNI (You Aren't Gonna Need It)**: لا تبنِ نظام استراتيجيات معقد لاحتمال نظري قد يحدث بعد سنتين.
     * **KISS (Keep It Simple, Stupid)**: أبسط كود يعمل ويفي بالشروط هو الكود الأفضل.
   - **إيضاح سهولة التعديل المستقبلي (Evolutionary Architecture)**:
     * الكود البسيط سهل القراءة يمكن إعادة هيكلته (Refactored) في ساعتين عندما يظهر التعقيد الحقيقي، بينما الكود المفرط في التجريد (Over-abstracted) يستحيل فك تشابكه!

3. وضع معيار عملي متفق عليه (Team Rule):
   - ابدأ بـ Simple MVVM مباشرة: ViewModel + Repository.
   - استخرج UseCase أو Interface فقط عندما يتكرر الكود في مكانين مختلفين، أو تظهر قواعد بيزنس معقدة تتطلب اختبارات خاصة.

## Practical walkthrough

توجيه الفريق لتبسيط ميزة بسيطة تم الإفراط في هندستها:
```kotlin
// ❌ ما كتبه الفريق (Overengineered): 6 ملفات لعرض جملة ترحيبية:
// GreetingDto -> GreetingEntity -> GreetingDomain -> GreetingUiModel
// interface IGreetingRepository -> GreetingRepositoryImpl
// interface IFetchGreetingUseCase -> FetchGreetingUseCaseImpl
// GreetingViewModel -> GreetingScreen

// ✅ ما يجب التوجيه إليه (Pragmatic & Clean): ملفان يؤديان الغرض بامتياز:
class GreetingRepository(private val api: GreetingApi) {
    suspend fun getGreeting(): String = api.fetch().message
}

@HiltViewModel
class GreetingViewModel @Inject constructor(
    private val repository: GreetingRepository
) : ViewModel() {
    val greeting = flow { emit(repository.getGreeting()) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), "Hello!")
}
```

## Why it matters and how it works

Principles help when they lower change and defect cost. Overengineering spends complexity before variation exists. A team can choose simple concrete code while preserving safe data/UI boundaries and a clear path to extract later.

## Worked example

Team discussion: show two diagrams for a small settings screen. Option A has `SettingsViewModel -> SettingsRepository` with a concrete formatter; option B adds one use case and interface per getter. Ask which independent change B protects. Keep A if no answer, and add a test for save/error behavior.

## Trade-offs and decision criteria

A lean design can defer useful abstraction until a second implementation or duplicated rule appears. Excessive simplicity can become direct SDK calls in UI, so keep core lifecycle, data and error ownership even in small work.

## Failure modes

A feature takes longer to wire than implement, and a tiny API rename forces changes across three model layers with no semantic difference. Reduce ceremonial types. Conversely, if a new payment provider touches every screen, add a real strategy boundary.

## Production perspective

A team agrees on a review checklist and revisits architecture after two iterations. They measure changed files, build time and test pain, while preserving server-side payment authority and Android lifecycle correctness.

## Interview answer — short

Coach the team that SOLID principles are heuristics to manage complexity, not dogma. Every abstraction carries real costs: cognitive overhead, build time, and delayed delivery. Reframe architecture around YAGNI, KISS, and economic trade-offs: start with simple pragmatic code, because clean simple code is easy to refactor when genuine complexity emerges.

## Interview answer — structured

Coaching an engineering team suffering from premature abstraction requires reframing architecture as an economic balance between maintainability and delivery velocity.

1. **Principles are Heuristics, Not Dogma**:
   - SOLID principles exist to solve concrete software pain points (high coupling, fragile changes, untestable code). Applying heavy solutions when those pain points do not exist is architectural waste.
   - Every abstraction introduces real overhead: doubled file counts, IDE navigation friction, Dagger binding ceremony, and longer Gradle build times.

2. **Anchor on Pragmatic Engineering Principles (YAGNI & KISS)**:
   - **YAGNI (You Aren't Gonna Need It)**: Speculative extensibility (e.g. building a strategy engine because 'marketing might want 4 alternative providers next year') wastes sprint capacity on hypothetical futures that rarely materialize.
   - **KISS (Keep It Simple, Stupid)**: The simplest code that fulfills current requirements, handles errors, and passes unit tests is the superior engineering choice.

3. **Evolutionary Architecture Assurance**:
   - Assure the team that simple code is not low-quality code. Plain, decoupled Kotlin code without gratuitous interfaces can be refactored into Use Cases and Strategies in under two hours when requirements genuinely expand.
   - Conversely, untangling a premature, multi-layered generic abstraction is notoriously painful.

## Interview answer — deep senior

In engineering leadership, a senior architect guides the team to establish **Complexity Thresholds**:
- *Tier 1 (Display / Simple CRUD)*: Direct ViewModel-to-Repository communication. Zero interfaces, zero Use Cases. Priority: Time to market.
- *Tier 2 (Interactive Features with Logic)*: ViewModel consumes Use Cases for reusable business operations. Repositories manage offline caching.
- *Tier 3 (Core Domain / Multi-Entry / Fintech)*: Full Clean Architecture with strict DIP interfaces, Strategy routers, and FSM state machines.

This empowers teams to modulate architectural ceremony proportionally to feature risk, eliminating overengineering while maintaining excellence in mission-critical domains.

## How to answer in the interview

- **Why:** Lead with change cost.
- **How:** compare simple settings flow.
- **Trade-offs:** admit later refactor cost.
- **Failure cases:** flag needless layer navigation.
- **Production solutions:** propose trigger and behavior tests..

## Deep-dive talking points

Present a concrete two-option design review, count protected change axes and identify a future extraction trigger.

## Follow-up questions

- **Interviewer:** "What is the difference between junior, mid-level, and senior engineering perspectives on SOLID?"
  **Answer:** "Junior engineers write spaghetti code unaware of SOLID. Mid-level engineers apply SOLID dogmatically to every class regardless of context. Senior engineers understand the economic trade-offs of abstractions and apply SOLID pragmatically where complexity demands it."

- **Interviewer:** "How do you challenge an overengineered PR without demotivating a developer?"
  **Answer:** "Praise their architectural understanding, explain the maintenance and compilation costs of the abstractions, highlight YAGNI, and collaborate on simplifying the PR while agreeing on future refactoring triggers."

## Self-check rubric

Explain a minimal settings design, one risk of overengineering, one risk of underengineering, and a revisit trigger.

## References and reviewed-on date

- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) — adaptable guidance.
- [Robert C. Martin, SRP](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — change ownership.

Technically reviewed against primary documentation on 2026-10-13.
