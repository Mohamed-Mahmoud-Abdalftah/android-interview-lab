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

## Concept and technical explanation

The Single Responsibility Principle (SRP) and the Interface Segregation Principle (ISP) are complementary SOLID principles addressing cohesion and coupling at different structural granularities. SRP governs implementation cohesion at the class, module, and actor level, mandating that a component must have only one reason to change. ISP governs contract coupling at the interface and consumer level, asserting that no client should be forced to depend on methods it does not invoke. A class can completely satisfy SRP by maintaining a single, highly cohesive responsibility (such as user account management) while simultaneously violating ISP if it exposes a fat, monolithic interface combining administrative, billing, and profile methods to disparate callers.

## Practical walkthrough (English)

Demonstrating a class satisfying SRP while violating ISP, and its refactoring:
```kotlin
// A class that has a single business responsibility (satisfies SRP: User Account Management)
// But its single interface violates ISP because distinct clients need only a fraction of its methods!
interface MonolithicAccountContract { // VIOLATES ISP: Combines disparate client needs
    fun getDisplayName(): String
    fun getAvatarUrl(): String
    fun changePassword(oldPass: String, newPass: String)
    fun processSubscriptionRenewal()
}

// REFACTORED TO SATISFY BOTH SRP AND ISP:
// Segregated Client-Specific Interfaces (ISP Satisfied)
interface UserProfileHeaderViewContract {
    fun getDisplayName(): String
    fun getAvatarUrl(): String
}

interface AccountSecurityContract {
    fun changePassword(oldPass: String, newPass: String)
}

interface SubscriptionBillingContract {
    fun processSubscriptionRenewal()
}

// Cohesive implementation satisfies SRP and multiple role-specific ISP interfaces
class UserAccountService @Inject constructor(
    private val api: AccountApi
) : UserProfileHeaderViewContract, AccountSecurityContract, SubscriptionBillingContract {
    // Single cohesive responsibility: manages account logic, but exposes fine-grained seams to callers!
    override fun getDisplayName() = "Alice"
    override fun getAvatarUrl() = "https://cdn.io/avatar.png"
    override fun changePassword(oldPass: String, newPass: String) { /* ... */ }
    override fun processSubscriptionRenewal() { /* ... */ }
}
```

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

SRP focuses on classes and actors, dictating that a class should have only one reason to change. ISP focuses on interfaces and clients, dictating that a client should not depend on methods it does not use. A class can satisfy SRP by having a single cohesive responsibility, yet violate ISP if its interface forces callers to depend on unused methods. SRP promotes high internal cohesion, while ISP minimizes external caller coupling.

## Interview answer — structured

Comparing SRP and ISP clarifies how cohesion and coupling operate together across class implementations and interface contracts.
The Single Responsibility Principle evaluates an entity from the inside out and from the perspective of the actors who request changes. It asks: does this class do only one job, and does it serve a single stakeholder? If a class handles validation, networking, and UI rendering, it violates SRP because changes in business rules, backend APIs, or visual designs all force modifications to that single file.
The Interface Segregation Principle evaluates an entity from the outside in and from the perspective of the clients who consume it. It asks: does this caller need every method exposed by this interface? If an interface combines read operations, write operations, and administrative functions, a caller that only reads data is forced to depend on the full contract, violating ISP.
The key insight is that a class can perfectly satisfy SRP while violating ISP. A UserManager class might focus purely on user account domain mechanics, satisfying SRP. However, if it exposes a single 15-method interface to both a lightweight UI header widget and a security settings screen, it violates ISP.
Applying ISP splits the contract into role interfaces, ensuring clients remain decoupled while the underlying implementation maintains its single responsibility.

## Interview answer — deep senior

Under the hood, SRP and ISP operate at different phases of software development, compilation, and automated verification.
SRP directly impacts codebase maintainability, change velocity, and merge conflict frequency. When classes violate SRP, multiple developers working on different features constantly edit the same source file, leading to high friction in Git branch workflows.
ISP, on the other hand, directly impacts compilation avoidance in Gradle, binary compatibility across SDK boundaries, and mocking overhead in test harnesses.
When a client module depends on a fat interface violating ISP, any addition or modification to an unused method signature changes the interface's public ABI. The Gradle build cache is invalidated, and the client module must be recompiled despite having zero functional interest in the change.
Furthermore, in unit testing, ISP violations lead to fragile test doubles. If a ViewModel depends on a fat 20-method repository interface, tests must supply mock configurations or throwaway stubs for methods that the ViewModel never executes.
When ISP is enforced, testing seams become razor-thin. A test passes a clean fake satisfying a 2-method SAM interface, keeping test setup code concise, deterministic, and resilient against unrelated interface churn across the enterprise codebase, ensuring smooth and rapid continuous delivery. This isolation ensures that client modules remain unaffected when other consumers request contract extensions.

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
