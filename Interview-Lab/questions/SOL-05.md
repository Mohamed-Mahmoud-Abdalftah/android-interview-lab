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

Interface Segregation Principle states that clients should not be forced to depend on methods they do not use. In Android, rather than creating a bloated 20-method repository interface or implementing the cumbersome 3-method `TextWatcher`, we split contracts into fine-grained single-purpose interfaces like `UserProfileReader` and `UserProfileWriter`.

## Interview answer — structured

The Interface Segregation Principle (ISP) states that **no client should be forced to depend on methods it does not use**.

When an interface becomes a 'fat interface' (accumulating dozens of methods across multiple feature areas), any change to an unrelated method forces recompilation and re-testing across all consumers. Furthermore, mock implementations in unit tests become bloated with empty stub methods.

Classic Android examples of ISP violations include:
- **`TextWatcher`**: Forces implementers to override `beforeTextChanged()`, `onTextChanged()`, and `afterTextChanged()` even if they only care about text changes. (Modern Android resolved this with `core-ktx` extension `doAfterTextChanged { ... }`).
- **`Animator.AnimatorListener`**: Forces four method implementations (`onAnimationStart`, `End`, `Cancel`, `Repeat`) for a simple end callback.

In modern architecture, we segregate data contracts based on consumer roles: splitting a monolithic `UserRepository` into `UserReader` and `UserWriter`. A read-only home widget injects only `UserReader`, ensuring it has zero visibility or coupling to sensitive account deletion or password change operations.

## Interview answer — deep senior

Kotlin provides exceptional language support for ISP via **Functional (SAM) Interfaces** (`fun interface`). A functional interface contains exactly one abstract method and can be implemented via a concise lambda: `val reader = UserProfileReader { flowOf(currentUser) }`. This makes mocking in unit tests practically instantaneous without heavy mocking libraries.

ISP also protects security and modularization. In enterprise fintech applications, the payment SDK might implement `PaymentAuditor`, `PaymentExecutor`, and `PaymentConfigurator`. The standard checkout UI module is injected only with `PaymentExecutor`, while administrative modules receive `PaymentConfigurator`. This compiler-level segregation prevents feature developers from accidentally exposing administrative configurations.

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
