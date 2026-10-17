---
id: "SOL-05"
question: "Explain Interface Segregation Principle with an Android example."
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "A"
phase: 2
priority: "P1"
order: 176
editorial_status: "reviewed"
---

# SOL-05

## Original interview question

Explain Interface Segregation Principle with an Android example.

## What the interviewer evaluates

Explain client-specific interfaces rather than merely “small interfaces” or SRP.

## Concept and technical explanation

The Interface Segregation Principle (ISP) dictates that clients should never be forced to depend upon interfaces or methods that they do not use. Instead of authoring monolithic, 'fat' interfaces containing dozens of heterogeneous operational methods, software architects must decompose contracts into small, highly cohesive, client-specific role interfaces. In Android development, fat interfaces create cognitive bloat, force implementing classes to provide meaningless empty-body stubs for irrelevant callbacks, and couple unrelated feature modules together, causing re-compilation ripple effects across the entire dependency graph whenever any single signature in the bloated interface is modified.

## Practical walkthrough (English)

Refactoring a bloated Android listener into segregated, role-specific interfaces:
```kotlin
// BAD ANTI-PATTERN: Fat interface forces implementers to write empty stubs (like legacy TextWatcher)
interface MassiveUserProfileContract {
    fun loadBasicInfo()
    fun updateAvatar(url: String)
    fun processSubscriptionPayment(amount: Long) // Irrelevant to a simple profile view!
    fun exportGdprData() // Irrelevant to normal app sessions!
}

// ARCHITECTURAL BEST PRACTICE: Segregated, role-specific interfaces
interface ProfileReader {
    val userProfile: Flow<UserProfile>
}

interface AvatarUploader {
    suspend fun uploadAvatar(imageBytes: ByteArray): Result<String>
}

interface SubscriptionBilling {
    suspend fun paySubscription(amount: Long): Result<Receipt>
}

// Profile Header component depends ONLY on what it actually needs
class ProfileHeaderPresenter @Inject constructor(
    private val profileReader: ProfileReader // Dependent strictly on read capabilities!
) {
    fun bind(view: ProfileHeaderView) { /* Consumes profileReader exclusively */ }
}
```

## Explanation in Arabic

شرح مبدأ فصل الواجهات (Interface Segregation Principle - ISP) مع مثال عملي واقعي في Android:

1. تعريف مبدأ فصل الواجهات (ISP):
   - ينص المبدأ على: **"لا ينبغي إجبار أي كود أو عميل (Client) على الاعتماد على واجهات (Interfaces) تحتوي على دوال لا يستخدمها"**.
   - الأفضل دائماً إنشاء عدة واجهات صغيرة متخصصة (Fine-grained interfaces) بدلاً من واجهة واحدة ضخمة تجمع كل شيء (Fat Interface).

2. ما الذي ينتهك ISP في Android الكلاسيكي؟
   - كلاس `TextWatcher` الشهير في Java Android! إذا أردت مراقبة النص فقط بعد تغييره، فأنت مجبر على تنفيذ 3 دوال: `beforeTextChanged`, `onTextChanged`, و `afterTextChanged`، وتترك أول دالتين فارغتين بلا فائدة!
   - مستودع ضخم `interface FullUserRepository` يحتوي على 20 دالة (قراءة البروفايل، تحديث الصورة، حذف الحساب، دفع الفاتورة، تسجيل الدخول)؛ في حين أن شاشة العرض البسيطة تحتاج فقط لدالة قراءة الاسم!

3. كيف نطبق ISP في Android الحديث؟
   - تقسيم الواجهات الكبيرة إلى واجهات دقيقة حسب الاستخدام:
     * `interface UserReader { fun getUser(): Flow<User> }`
     * `interface UserWriter { suspend fun updateUser(user: User) }`
   - في Kotlin، استخدام الـ Lambdas المباشرة (مثل `doAfterTextChanged { ... }`) أو واجهات أحادية الدالة (Functional Interfaces - `fun interface`).

## Practical walkthrough

المقارنة بين واجهة ضخمة تنتهك ISP وواجهات مجزأة دقيقة:
```kotlin
// ❌ انتهاك صارخ لـ ISP: واجهة ضخمة تجبر الكلاسات على تنفيذ دوال لا تحتاجها:
interface UserManagementService {
    fun readProfile(): User
    fun updateProfile(user: User)
    fun deleteAccount()
    fun processSubscriptionPayment(amount: Long)
}

// شاشة العرض البسيطة تضطر للتعامل مع دوال الحذف والدفع الحساسة بلا داعٍ!
class ReadOnlyProfileWidget(private val service: UserManagementService) { ... }

// ✅ تطبيق ISP السليم: واجهات دقيقة مقسمة حسب الصلاحيات والاحتياج:
fun interface UserProfileReader {
    fun readProfile(): Flow<User>
}

interface UserProfileWriter {
    suspend fun updateProfile(user: User)
}

interface AccountTerminator {
    suspend fun deleteAccount()
}

// يمكن لكلاس الـ Repository في طبقة Data تنفيذ الواجهات الثلاث معاً، ولكن الـ Widget يستهلك Reader فقط:
class ReadOnlyProfileWidget(private val reader: UserProfileReader) {
    // آمن تماماً، ولا يعرف أي شيء عن الحذف أو الدفع!
}
```

## Why it matters and how it works

A wide interface couples clients to unrelated changes and forces implementations to provide irrelevant behavior. Segregated contracts let each consumer depend on exactly the capabilities it needs, improving substitution and test fakes.

## Worked example

Conceptual Kotlin:
```kotlin
interface SessionReader { fun currentUserId(): String? }
interface SignOut { suspend fun signOut() }
class AccountMenu(private val signOut: SignOut)
```
A read-only widget does not need to depend on sign-out or payment methods. Shared implementation may implement both interfaces.

## Trade-offs and decision criteria

Over-splitting creates interface clutter and wiring. Group operations that change together for one client. A cohesive repository API can have several methods without violating ISP; size alone is not the criterion.

## Failure modes

A fake for a settings screen implements 20 unrelated payment methods as `error("unused")`; tests become brittle and production substitutes may throw. Split contracts around consuming features and run contract tests.

## Production perspective

A wallet app exposes a narrow session reader to UI, a token refresher to networking, and sign-out capability to account settings. The implementation can share state while feature dependencies stay focused.

## Interview answer — short

The Interface Segregation Principle states that clients should never be forced to depend on methods they do not use. In Android, the classic violation is the legacy Java TextWatcher, where developers wanting only afterTextChanged were forced to implement beforeTextChanged and onTextChanged with empty bodies. Applying ISP breaks fat interfaces into focused, role-specific contracts, such as separating a monolithic repository into ProfileReader and ProfileUpdater interfaces.

## Interview answer — structured

The Interface Segregation Principle ensures that contracts between components remain minimal, purposeful, and decoupled from extraneous functionality.
When an interface accumulates too many responsibilities, it becomes a 'fat interface'. Consumers that require only a fraction of those capabilities are forced to depend on the entire definition. In Android, this creates two major problems: boilerplate clutter and undesirable architectural coupling.
A famous Android framework example is the legacy android.text.TextWatcher interface. It declared three distinct callback methods: beforeTextChanged, onTextChanged, and afterTextChanged. In ninety percent of use cases, developers only care about reacting to the final text in afterTextChanged. Yet, every implementation was forced to declare empty boilerplate overrides for the other two methods. Android Jetpack eventually corrected this with the core-ktx doAfterTextChanged extension lambda.
In application architecture, ISP is vital when designing repositories and data sources. If a single UserRepository interface contains methods for fetching public user info, updating admin permissions, and billing subscriptions, a simple UI header component depends unnecessarily on sensitive billing and admin methods.
By segregating the interface into ProfileReader, RoleManager, and BillingService, consumers depend strictly on the capabilities they actually consume.

## Interview answer — deep senior

Under the hood, the Interface Segregation Principle directly optimizes binary interface contracts (ABI), incremental compilation graphs, and mock footprint in unit test suites.
In multi-module Android codebases, if Module A depends on a fat interface defined in Module B, any change to an unused method signature in that interface changes Module B's public ABI. This invalidates Gradle's incremental compilation cache, forcing the compiler to re-analyze and recompile Module A and all downstream dependencies, even though Module A never called the modified method.
By segregating fat interfaces into granular role interfaces (often single-abstract-method SAM interfaces in Kotlin), Gradle's compilation avoidance mechanics successfully skip recompiling unaffected consumer modules, drastically accelerating build speeds in enterprise teams.
From a testability standpoint, ISP eliminates mocking friction. When writing unit tests for a ViewModel that consumes a 20-method repository, developers often struggle with verbose mocking configurations where every uncalled method must be stubbed or ignored. With fine-grained role interfaces, writing a lightweight in-memory fake takes less than ten lines of pure Kotlin code.
Furthermore, Kotlin's language features natively reinforce ISP through first-class functional types ((String) -> Unit) and interface delegation (by), allowing classes to compose multiple segregated interfaces cleanly without manual forwarding boilerplate, keeping the runtime footprint exceptionally lightweight.

## How to answer in the interview

- **Why:** Describe the client's unused methods.
- **How:** draw client-method matrix.
- **Trade-offs:** note interface proliferation.
- **Failure cases:** cite giant mocks as a symptom.
- **Production solutions:** propose role interfaces and focused fakes..

## Deep-dive talking points

Compare one giant account API to client-facing capabilities; discuss fake tests and module rebuild coupling.

## Follow-up questions

- **Interviewer:** "How did Android KTX resolve ISP violations in legacy Android listeners?"
  **Answer:** "KTX introduced extension functions accepting single lambdas with default no-op parameters (e.g. `view.doAfterTextChanged { }`, `animator.doOnEnd { }`), freeing developers from overriding unused methods."

- **Interviewer:** "Can a single concrete class implement multiple segregated interfaces?"
  **Answer:** "Yes. A single `UserRepositoryImpl` can implement both `UserReader` and `UserWriter`, while clients inject only the specific interface abstraction they require."

## Self-check rubric

Identify two clients using different method subsets, propose capability interfaces, and avoid one-method-interface dogma.

## References and reviewed-on date

- [Robert C. Martin, A Little Architecture](https://blog.cleancoder.com/uncle-bob/2016/01/04/ALittleArchitecture.html) — interface segregation and dependency direction.
- [Android modularization guide](https://developer.android.com/topic/modularization) — module boundaries.

Technically reviewed against primary documentation on 2026-10-13.
