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

SOLID stands for Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion. In Android, these principles prevent monolithic God Activities, isolate business rules from framework churn, enable pure JVM unit testing, and maintain high code cohesion in multi-module codebases.

## Interview answer — structured

SOLID represents five foundational object-oriented design principles aimed at creating maintainable, testable, and scalable software systems.

First, a Single Responsibility (SRP) is a class should have one, and only one, reason to change. Next, with Open/Closed (OCP), software entities should be open for extension (adding new features via polymorphism or composition) but closed for modification (not editing existing tested code).
Additionally, with Liskov Substitution (LSP), subtypes must be substitutable for their base types without altering program correctness or throwing unexpected exceptions. With Interface Segregation (ISP), clients should not be forced to depend on interfaces they do not use; prefer many fine-grained interfaces over one fat interface.
Finally, with Dependency Inversion (DIP), high-level business policies should not depend on low-level infrastructure details; both should depend on abstractions.

In Android, violating SOLID leads to fragile 'God Activities', tight coupling to SDK lifecycles, and impossible unit testing. Adhering to SOLID keeps domain logic decoupled from framework churn.


## Interview answer — deep senior

Under the hood, SOLID principles are not dogmatic laws—they are tools to manage **coupling and cohesion**. High cohesion means code that changes together stays together; loose coupling means changes in one module do not ripple into others.

In modern Android architectures (Clean Architecture + Jetpack Compose + Kotlin Coroutines), SOLID principles manifest concretely.

First, sRP drives the separation between ViewModels, Use Cases, Repositories, and DataSources. Next, oCP enables feature extensions via Strategy patterns and polymorphic sealed classes.
LSP eliminates rigid, deeply nested inheritance hierarchies like bloated `BaseActivity` classes in favor of composable delegates. ISP creates focused repository interfaces (`UserReader`, `UserWriter`) rather than monolithic CRUD interfaces.
Finally, dIP powers inversion of control where the Domain layer defines repository contracts implemented by the Data layer.

We balance SOLID against the YAGNI principle to prevent speculative overengineering in early-stage features.


## How to answer in the interview

- **Why:** Lead with the five meanings and one change request.
- **How:** show where changes propagate.
- **Trade-offs:** mention abstraction cost.
- **Failure cases:** cite contract violations or cancellation.
- **Production solutions:** finish with contract tests and server confirmation..

## Deep-dive talking points

Map each letter to one concrete Android failure and an appropriate refactor; distinguish principle from DI framework.

## Follow-up questions

- **Interviewer:** "Which SOLID principle is most commonly violated in legacy Android codebases?"
  **Answer:** "The Single Responsibility Principle (SRP), typically resulting in massive 'God Activities' or 'God Fragments' managing UI inflation, network calls, SQLite transactions, and business calculations in a single file."

- **Interviewer:** "How does Kotlin's language design support SOLID out of the box?"
  **Answer:** "Kotlin promotes SOLID via first-class composition (delegation via `by`), pure functions, interface default implementations, immutability by default (`val`), and sealed hierarchies for type-safe extension."

## Self-check rubric

Expand all five letters, give an Android example for two, and explain one overengineering risk.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — separation of responsibilities and dependency boundaries.
- [Robert C. Martin on SRP](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — reasons to change.
- [Robert C. Martin on OCP](https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html) — extension and dependency direction.

Technically reviewed against primary documentation on 2026-10-13.
