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

## Concept and technical explanation

Explaining SOLID trade-offs to an overengineering team requires pragmatic technical leadership that balances long-term architectural hygiene with immediate product delivery velocity. SOLID principles are not dogmatic laws that must be implemented universally; they are risk-mitigation strategies designed to manage complexity in evolving, enterprise software. When junior or mid-level engineers introduce dozens of speculative interfaces, multi-layer UseCases, and abstract factories for simple CRUD screens, they incur high cognitive tax and maintenance overhead without deriving any architectural benefits. Senior leaders guide teams toward evolutionary architecture, teaching them to apply KISS and YAGNI first, scaling to full SOLID patterns only as feature volatility and domain complexity legitimately demand it.

## Practical walkthrough (English)

Simplifying an overengineered feature into a pragmatic, maintainable design:
```kotlin
// BAD OVERENGINEERED PATTERN: Excessive abstraction for a simple static FAQ screen
interface FaqAnalyticsTracker { fun track() }
interface FaqFormatter { fun format(raw: String): String }
interface FaqRepository { suspend fun getFaqs(): List<Faq> }
class GetFaqsUseCase @Inject constructor(private val repo: FaqRepository) { suspend operator fun invoke() = repo.getFaqs() }
class FaqViewModel @Inject constructor(
    private val useCase: GetFaqsUseCase,
    private val tracker: FaqAnalyticsTracker,
    private val formatter: FaqFormatter
) : ViewModel()

// ARCHITECTURAL BEST PRACTICE: Pragmatic, clean architecture scaled to feature complexity
// Single cohesive ViewModel fetching static FAQ data directly: 1 file instead of 8!
class FaqViewModel @Inject constructor(
    private val faqApi: FaqApi // Direct dependency appropriate for low-complexity, static read-only screen
) : ViewModel() {
    private val _faqs = MutableStateFlow<List<FaqItem>>(emptyList())
    val faqs: StateFlow<List<FaqItem>> = _faqs.asStateFlow()

    fun loadFaqs() {
        viewModelScope.launch {
            _faqs.value = runCatching { faqApi.fetchFaqs().map { it.toUiModel() } }.getOrDefault(emptyList())
        }
    }
}
```

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

I explain SOLID trade-offs by framing them as tools for managing complexity, not moral requirements. Every abstraction introduces cognitive tax, extra files, and navigation overhead. For a simple or stable feature, overengineering with speculative interfaces and redundant UseCases wastes engineering time and slows down builds without adding value. I encourage the team to follow YAGNI and KISS first, building clean concrete code and applying advanced SOLID patterns progressively as feature complexity and business volatility genuinely demand it.

## Interview answer — structured

Guiding a team away from overengineering requires empathy, architectural pragmatism, and clear economic reasoning.
When enthusiastic engineers overengineer small features, they believe they are following 'best practices' by creating interfaces for every class, writing single-line UseCases, and engineering elaborate factories for static screens.
I address this through a structured mentorship conversation.
First, reframe the purpose of SOLID. Explain that SOLID principles are risk-mitigation mechanisms designed to counter the cost of change in volatile systems. If a screen has low business volatility (such as an About Us or static FAQ screen), the risk of change is nearly zero, making complex abstractions an unnecessary expense.
Second, highlight the real costs of over-abstraction. Show the team that every redundant interface doubles the file count, impairs IDE navigation, complicates debugging, and inflates Gradle compilation times.
Third, introduce the concept of Evolutionary Architecture and the Rule of Three. Encourage the team to start with the simplest workable design that satisfies clean coding standards (KISS and YAGNI).
As requirements evolve and true business variation emerges, the team can refactor toward full SOLID abstractions incrementally with full test coverage, ensuring engineering time delivers tangible business value.

## Interview answer — deep senior

Under the hood, overengineering directly penalizes engineering velocity, developer onboarding time, and CI/CD build economics in production Android teams.
When a simple feature with 200 lines of functional logic is fragmented across 12 files (interfaces, implementations, mappers, delegates, and UseCases), the cognitive load required to understand the control flow skyrockets. New engineers spending hours tracing call graphs through single-implementation abstractions experience high onboarding friction.
At the build system level, unnecessary class definitions inflate the Gradle task graph. Every additional interface and Dagger component adds annotations that the Kotlin Symbol Processing (KSP) tool must inspect. In massive multi-module projects, speculative abstraction bloat noticeably degrades incremental compilation performance and dev-loop turnaround times.
Furthermore, premature abstraction impairs runtime performance. In the Android ART runtime, deeply nested layers of UseCases and delegates create chains of method forwarding, increasing stack frame depth and allocating temporary wrapper objects that add pressure to the garbage collector.
Staff engineers establish pragmatic architectural guidelines: simple CRUD screens connect ViewModels directly to Repositories, omitting intermediate UseCases unless cross-repository orchestration or complex business logic is genuinely present.
Architecture is a spectrum, and true seniority is knowing how much architecture a specific problem actually warrants. This balanced technical mindset protects teams from burning velocity on low-value architectural ceremony.

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
