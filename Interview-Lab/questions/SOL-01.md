---
id: "SOL-01"
question: "What does SOLID stand for, and why does it matter?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "A"
phase: 2
priority: "P1"
order: 172
editorial_status: "reviewed"
---

# SOL-01

## Original interview question

What does SOLID stand for, and why does it matter?

## What the interviewer evaluates

Name all five principles and explain their shared goal as change control, not class-count rules.

## Concept and technical explanation

SOLID is an acronym representing five foundational object-oriented design principles formulated by Robert C. Martin: Single Responsibility Principle (SRP), Open/Closed Principle (OCP), Liskov Substitution Principle (LSP), Interface Segregation Principle (ISP), and Dependency Inversion Principle (DIP). In professional Android engineering, these principles establish maintainable architectural boundaries, prevent God Objects like monolithic Activities and ViewModels, isolate volatile framework APIs from pure business logic, enable fast JVM unit testing via dependency inversion, and safeguard large multi-module codebases against regression cascades when features evolve.

## Practical walkthrough (English)

Mapping SOLID principles to modern Android Clean Architecture:
```kotlin
// S - Single Responsibility: Class handles only validation logic
class FormInputValidator {
    fun isValidEmail(email: String): Boolean = email.contains("@") && email.contains(".")
}

// O - Open/Closed: Extensible notification strategy without modifying existing sender
interface PushRenderer { fun render(payload: Map<String, String>) }
class OrderStatusPushRenderer : PushRenderer { override fun render(payload: Map<String, String>) { /* ... */ } }

// L - Liskov Substitution: Specialized repository fulfills base contract without surprises
interface UserRepository { suspend fun fetchUser(): Result<User> }
class NetworkUserRepository(private val api: UserApi) : UserRepository {
    override suspend fun fetchUser(): Result<User> = runCatching { api.getUser() }
}

// I - Interface Segregation: Client depends only on what it actually reads
interface ProfileReader { val currentUserName: Flow<String> }
interface ProfileUpdater { suspend fun updateName(newName: String) }

// D - Dependency Inversion: ViewModel depends on abstraction, not Room/Retrofit
class ProfileViewModel @Inject constructor(
    private val profileReader: ProfileReader // Inverted dependency
) : ViewModel() {
    val name = profileReader.currentUserName
}
```

## Explanation in Arabic

ما هي مبادئ SOLID الخمسة ولماذا تُعد حجر الأساس في هندسة تطبيقات Android الاحترافية؟

1. ما الذي ترمز إليه حروف SOLID؟
   - **S - Single Responsibility Principle (SRP)**: كل كلاس يمتلك مسؤولية واحدة فقط وسبباً واحداً للتغيير.
   - **O - Open/Closed Principle (OCP)**: الكيانات البرمجية مفتوحة للتوسيع (Extension) ومغلقة للتعديل (Modification).
   - **L - Liskov Substitution Principle (LSP)**: الكلاسات الفرعية يجب أن تحل محل الكلاسات الأساسية دون كسر صحة وسلوك البرنامج.
   - **I - Interface Segregation Principle (ISP)**: تقسيم الواجهات الضخمة إلى واجهات صغيرة محددة؛ لا تُجبر كوداً على تنفيذ دوال لا يحتاجها.
   - **D - Dependency Inversion Principle (DIP)**: الوحدات العليا لا تعتمد على الوحدات الدنيا؛ كلاهما يعتمد على التجريدات (Abstractions).

2. لماذا تُعتبر حيوية في Android الحديث؟
   - بدون SOLID، يتحول المشروع إلى **كود هش (Fragile Code)**: أي تعديل في شاشة يكسر شاشة أخرى، وتتضخم الـ Activities إلى God Classes يستحيل اختبارها.
   - تطبيق SOLID يضمن: سهولة الصيانة، قابلية الاختبار بنسبة 100% على الـ JVM، وسهولة تقسيم المشروع إلى Gradle Modules مستقلة.

## Practical walkthrough

نظرة سريعة على كود ينتهك SOLID وكود يعتمد عليها في Android:
```kotlin
// ❌ انتهاك صارخ لمبادئ SOLID: God Activity تجمع كل شيء:
class MonolithicProfileActivity : AppCompatActivity() {
    // تنتهك SRP: تجمع الرسم، واستدعاء Retrofit، وحفظ SQLite، والـ Validation!
    // تنتهك OCP: إضافة نوع مستخدم جديد يتطلب تعديل if/else في 5 دوال.
    // تنتهك DIP: تعتمد على كائنات ملموسة مباشرة new Retrofit().
}

// ✅ تطبيق SOLID: تفكيك المسؤوليات إلى مكونات متماسكة ومعزولة:
class ProfileViewModel @Inject constructor(
    private val getProfile: GetProfileUseCase, // DIP & SRP
    private val analytics: AnalyticsTracker // ISP & OCP
) : ViewModel() {
    val uiState: StateFlow<ProfileUiState> = ...
}
```

## Why it matters and how it works

The principles address cohesion, extension, substitutability, client-specific contracts and dependency direction. They work together when a codebase grows, but each has a cost and context. Their practical measure is whether changes remain local and behavior remains substitutable.

## Worked example

Conceptual Android example: checkout policy depends on `PaymentGateway` rather than a specific SDK (DIP), accepts new provider adapters without editing the policy (OCP), and every adapter must honor the same result/cancellation contract (LSP). UI does not depend on unrelated gateway methods (ISP), while rendering stays separate from provider I/O (SRP).

## Trade-offs and decision criteria

Applying every principle mechanically can create needless layers and interface pairs. Start with concrete cohesive code, then introduce abstractions where change or variation is real. Duplication can be cheaper than a premature “universal” base class.

## Failure modes

A team says “we use Hilt, therefore SOLID is satisfied,” while business rules still import Retrofit DTOs and a base class forces unsupported methods. DI wiring alone does not establish proper contracts or substitution.

## Production perspective

A multi-provider payment app isolates provider SDKs behind a narrow contract and tests failure semantics; it does not claim exactly-once execution from an interface or local state. A one-screen prototype can remain simpler.

## Interview answer — short

SOLID stands for Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion. I use those ideas to make changes safer: keep a class focused, let implementations honor their contracts, and keep business rules away from concrete framework details. They are useful checks when a design is hard to change or test, not a reason to add an interface to every class.

## Interview answer — structured

SOLID is a set of five design principles: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion. In an interview I would name them, then explain the common purpose: make a change in one part of the app without surprising unrelated parts.

In Android, a large Activity that draws the screen, calls Retrofit, validates input, and writes to Room is a useful warning sign. I would move the decision logic out of the UI and give it a clear dependency on the data it needs. That makes the behavior easier to test. If I have several payment providers, I might put their differing behavior behind a narrow contract; each implementation must still honor the same failure semantics.

I would not apply the acronym mechanically. A one-off class does not need an interface just because Dependency Inversion exists, and forcing every variation into a shared base class can make things worse. I use the principles when they answer a real change or testing problem, then keep the simplest design that does that.

## Interview answer — deep senior

The interesting part is how the principles interact when requirements change. Single Responsibility is about reasons to change, not about making every class tiny. If a ViewModel owns UI state and delegates payment authorization rules, a policy change can be tested without booting an Activity. Open/Closed can help when new providers arrive, but only if the variation is real; an elaborate plugin system for one provider adds cost without benefit.

Liskov Substitution is the contract check. A provider implementation that silently treats a timeout as a decline cannot safely replace one that reports an unknown outcome. That is a correctness issue, even if both satisfy the same Kotlin interface. Interface Segregation helps keep consumers from depending on operations they cannot use, such as a read-only screen receiving a repository with mutation methods. Dependency Inversion puts important policy behind an abstraction that can be supplied by a data implementation, but using Hilt alone does not prove that the dependency direction is healthy.

I would test these boundaries with behavior-focused tests: the same contract cases for each provider, plus tests for failures and cancellation. I would also review whether the new abstraction made the code easier to change. If the change still touches ten unrelated classes, the boundary is probably in the wrong place. If a tiny feature now has five pass-through layers, I would simplify it. SOLID is most useful as a way to reason about change and substitutability, not as a scoring checklist.

## How to answer in the interview

- **Why:** Lead with the five meanings and one change request.
- **How:** show where changes propagate.
- **Trade-offs:** mention abstraction cost.
- **Failure cases:** cite contract violations or cancellation.
- **Production solutions:** finish with contract tests and server confirmation..

## Deep-dive talking points

Map each letter to one concrete Android failure and an appropriate refactor; distinguish principle from DI framework.

## Follow-up questions

- **Interviewer:** "Does using Hilt mean the app follows Dependency Inversion?"
  **Answer:** "No. Hilt wires objects. If the business rule still imports a Retrofit DTO or depends directly on an Android component, its policy is coupled to that detail. I would look at the dependency direction, not just the constructor annotation."

- **Interviewer:** "Would you create an interface for every repository and use case?"
  **Answer:** "Only where the contract gives us a useful boundary or real variation. For one simple implementation, an extra interface can hide the flow without making change easier."

- **Interviewer:** "How can an implementation satisfy an interface and still violate Liskov Substitution?"
  **Answer:** "The method signatures can match while behavior differs. If one payment provider reports a timeout as a decline, callers may retry and charge twice. The behavioral contract has to cover those outcomes."

## Self-check rubric

Expand all five letters, give an Android example for two, and explain one overengineering risk.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — separation of responsibilities and dependency boundaries.
- [Robert C. Martin on SRP](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — reasons to change.
- [Robert C. Martin on OCP](https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html) — extension and dependency direction.

Technically reviewed against primary documentation on 2026-10-13.
