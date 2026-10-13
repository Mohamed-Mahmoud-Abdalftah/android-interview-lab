---
id: "SOL-08"
question: "Compare SRP and ISP."
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "A"
phase: 2
priority: "P1"
order: 179
editorial_status: "reviewed"
---

# SOL-08

## Original interview question

Compare SRP and ISP.

## What the interviewer evaluates

Contrast module cohesion/change actors with client-specific dependency surfaces.

## Explanation in Arabic

المقارنة والفرق الجوهري بين مبدأ المسؤولية الواحدة (SRP) ومبدأ فصل الواجهات (ISP):

1. ما هو الفرق الأساسي بينهما؟
   - **مبدأ المسؤولية الواحدة (SRP - Single Responsibility Principle)**:
     * يركز على **الكلاسات والتنفيذ (Classes & Implementations)**.
     * ينظر إلى الكود من **الداخل إلى الخارج (Inside-Out)**.
     * يسأل: *"كم سبباً لدى هذا الكلاس ليتغير؟ ومن هو صاحب المصلحة (Actor) الذي يخدمه هذا الكلاس؟"*
     * الهدف: تماسك الكود (High Cohesion) ومنع الكلاسات من التضخم بمسؤوليات متعددة.
   - **مبدأ فصل الواجهات (ISP - Interface Segregation Principle)**:
     * يركز على **الواجهات والعملاء المستهلكين (Interfaces & Clients)**.
     * ينظر إلى الكود من **الخارج إلى الداخل (Outside-In)**.
     * يسأل: *"هل هذا الـ Client مجبر على معرفة أو تنفيذ دوال لا يحتاجها في هذا الـ Interface؟"*
     * الهدف: تقليل الاعتمادية غير الضرورية وفصل الصلاحيات (Decoupling).

2. كيف يتكاملان معاً في كود Android؟
   - كلاس `UserRepositoryImpl` قد يكون متوافقاً تماماً مع **SRP** (مسؤول فقط عن تنسيق بيانات المستخدم).
   - ولكنه يقدم واجهة ضخمة (Fat Interface) فيها 20 دالة.
   - هنا يأتي دور **ISP** لتقسيم تلك الواجهة إلى `UserReader` و `UserWriter` حتى لا تجبر شاشة العرض على رؤية دوال الحذف والتعديل.

## Practical walkthrough

توضيح التكامل بين SRP و ISP في كود Android:
```kotlin
// كلاس واحد محقق لمبدأ SRP (مسؤوليته الوحيدة تنسيق بيانات المستخدم في Data layer):
class UserRepositoryImpl(
    private val localDao: UserDao,
    private val remoteApi: UserApi
) : UserReader, UserWriter { // ينفذ واجهتين مفصولتين تحقيقاً لـ ISP

    override fun getUser(id: String): Flow<User> = localDao.getUser(id)
    override suspend fun updateUser(user: User) { remoteApi.update(user) }
}

// واجهات دقيقة تحقق مبدأ ISP:
interface UserReader { // موجهة للـ Widgets والشاشات التي تقرأ فقط
    fun getUser(id: String): Flow<User>
}

interface UserWriter { // موجهة لشاشات التعديل فقط
    suspend fun updateUser(user: User)
}
```

## Why it matters and how it works

SRP concerns the cohesion of a module and its reasons to change. ISP concerns the surface a client must depend on. One large service may violate both, but the diagnostic questions and boundaries differ.

## Worked example

Scenario: `AccountRepository` owns session refresh and profile storage, which may be cohesive or not depending on change. `CheckoutScreen` only needs `SessionReader`; giving it the full repository API creates ISP coupling even if repository itself is cohesive.

## Trade-offs and decision criteria

Splitting implementation for SRP may reduce unrelated changes but adds composition. Segregating interfaces for ISP can keep one implementation behind several client views. Avoid class explosion when only the public dependency surface needs narrowing.

## Failure modes

A team responds to ISP by splitting a cohesive repository into dozens of tiny classes, increasing coordination. Another responds to SRP only by adding smaller interfaces while one God Class still contains unrelated policies. Diagnose before refactoring.

## Production perspective

A wallet team separates risk policy from session refresh (SRP) but exposes one session implementation through read-only and sign-out contracts for different features (ISP). Tests reflect both responsibilities and client surfaces.

## Interview answer — short

SRP focuses on classes and actors: a class should have only one reason to change. ISP focuses on interfaces and clients: a client should not be forced to depend on methods it doesn't use. A class can satisfy SRP (single responsibility) while its interface violates ISP (exposing too many methods to distinct callers).

## Interview answer — structured

While both SRP and ISP promote modularity, they operate from opposing perspectives in the design hierarchy.

1. **SRP (Single Responsibility Principle - Inside-Out Perspective)**:
   - Governs **classes, modules, and concrete implementations**.
   - Focuses on the *producer* of behavior.
   - Criterion: A class must have only one reason to change, serving a single business actor (e.g. `PaymentValidator` serves business rules; `PaymentRepository` serves storage).
   - Goal: High cohesion within the class.

2. **ISP (Interface Segregation Principle - Outside-In Perspective)**:
   - Governs **interfaces and abstractions**.
   - Focuses on the *consumer (client)* of behavior.
   - Criterion: No client should be forced to depend on methods it does not invoke.
   - Goal: Loose coupling between clients and shared abstractions.

A concrete class can be 100% compliant with SRP (e.g. `UserRepositoryImpl` has the single cohesive responsibility of managing user data persistence), yet violate ISP if it exposes a monolithic 30-method interface to simple read-only UI clients.

## Interview answer — deep senior

Under the hood, violating ISP harms build performance and incremental compilation in Gradle multi-module projects. If an interface `FullUserApi` is shared across 10 feature modules, modifying or adding a method used by only one feature invalidates the ABI hash. Gradle is forced to recompile all 10 consuming modules!

Applying ISP prevents this ripple effect: fine-grained interfaces (`UserReader`, `UserPreferences`) isolate compilation boundaries. Updating `UserWriter` triggers recompilation strictly for the edit profile module, leaving read-only feed modules cached.

In Kotlin, using interface segregation combined with delegation allows composing rich capabilities: `class FacadeRepo(reader: UserReader, writer: UserWriter) : UserReader by reader, UserWriter by writer`.

## How to answer in the interview

- **Why:** Contrast implementation cohesion with client dependence.
- **How:** use the repository/client example.
- **Trade-offs:** warn about extra types.
- **Failure cases:** cite broad mocks.
- **Production solutions:** propose change-history and client-method evidence..

## Deep-dive talking points

Diagnose a God Class and a fat interface separately; show a shared implementation behind narrow client contracts.

## Follow-up questions

- **Interviewer:** "Can a class violate SRP while its interface satisfies ISP?"
  **Answer:** "Yes. A class might implement a clean 2-method interface like `Runnable`, but inside `run()` it executes networking, database parsing, and UI mutations, severely violating SRP."

- **Interviewer:** "How does ISP benefit unit testing?"
  **Answer:** "Clients depending on segregated interfaces require tiny, focused test doubles (Fakes) implementing 1-2 methods rather than massive mock objects stubbing 20 irrelevant methods."

## Self-check rubric

Give one SRP-only smell and one ISP-only smell, then choose the right repair for each.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — separation of concerns in application modules.
- [Robert C. Martin on SRP](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — cohesion/change actors.
- [Robert C. Martin, A Little Architecture](https://blog.cleancoder.com/uncle-bob/2016/01/04/ALittleArchitecture.html) — interface segregation.

Technically reviewed against primary documentation on 2026-10-13.
