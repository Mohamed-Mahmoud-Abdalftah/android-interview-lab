---
id: "SOL-02"
question: "Explain Single Responsibility Principle with an Android example."
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "A"
phase: 2
priority: "P1"
order: 173
editorial_status: "reviewed"
---

# SOL-02

## Original interview question

Explain Single Responsibility Principle with an Android example.

## What the interviewer evaluates

Use “one reason to change” correctly rather than one method or one task per class.

## Explanation in Arabic

شرح مبدأ المسؤولية الواحدة (Single Responsibility Principle - SRP) مع مثال عملي واقعي في Android:

1. تعريف مبدأ المسؤولية الواحدة (SRP):
   - ينص المبدأ على: **"يجب أن يمتلك الكلاس سبباً واحداً فقط للتغيير (Single Reason to Change)"**.
   - أو بتعبير روبرت مارتن الأعمق: **"يجب أن يكون الكلاس مسؤولاً أمام مستخدم أو جهة مصلحة واحدة فقط (Single Actor)"**.

2. ما الذي ينتهك SRP في Android؟
   - كلاس `UserRegistrationActivity` يقوم بالتحقق من صحة الإيميل (Business Rule)، وطلب السيرفر بـ Retrofit (Networking)، وعرض ProgressDialog (UI)، وحفظ الـ Token في SharedPreferences (Storage).
   - أسباب التغيير متعددة: إذا تغير تصميم الشاشة، أو تغيرت قواعد الإيميل، أو تغيرت الـ API، أو تغير التخزين إلى DataStore—كل هذه الأسباب المختلفة تجبرك على تعديل نفس الكلاس!

3. كيف نطبق SRP بشكل سليم؟
   - **EmailValidator**: مسؤول عن قواعد التحقق فقط (سبب التغيير: قرار قسم الـ Product).
   - **AuthRepository**: مسؤول عن الشبكة والتخزين (سبب التغيير: قرار قسم الـ Backend أو الـ Infrastructure).
   - **RegisterViewModel**: ينسق بين الواجهة والبيزنس.
   - **RegisterScreen**: مسؤول عن الرسم والتفاعل فقط (سبب التغيير: قرار مصمم الـ UI/UX).

## Practical walkthrough

تطبيق مبدأ SRP بفصل المسؤوليات المعزولة في شاشة التسجيل:
```kotlin
// ❌ انتهاك صارخ لـ SRP: كلاس واحد يقوم بالتحقق، والشبكة، والتخزين، وتحديث الواجهة:
class BadRegistrationActivity : AppCompatActivity() {
    fun onRegisterClicked(email: String, pass: String) {
        if (!email.contains("@")) return // منطق بيزنس!
        api.register(email, pass) { response -> // اتصال شبكة!
            prefs.edit().putString("token", response.token).apply() // تخزين محلي!
            showSuccessDialog() // رسم واجهة!
        }
    }
}

// ✅ تطبيق SRP السليم: كل كائن له مسؤولية وحيدة وسبب واحد للتعديل:
class EmailValidator { // سبب التغيير: تعديل قواعد الإيميل من الـ Business
    fun isValid(email: String): Boolean = email.isNotBlank() && Patterns.EMAIL_ADDRESS.matcher(email).matches()
}

class RegisterUserUseCase(private val authRepo: AuthRepository, private val validator: EmailValidator) {
    suspend operator fun invoke(email: String, pass: String): Result<UserSession> {
        if (!validator.isValid(email)) return Result.failure(InvalidEmailException())
        return authRepo.register(email, pass)
    }
}

// الـ ViewModel مسؤول حصرياً عن إدارة الـ UI State وإطلاق الـ UseCase:
@HiltViewModel
class RegisterViewModel @Inject constructor(private val registerUser: RegisterUserUseCase) : ViewModel() { ... }
```

## Why it matters and how it works

Cohesion around one reason to change keeps unrelated changes from breaking each other. In Android, UI rendering, network schema and business policy commonly evolve on different timelines. SRP is about responsibility to a change actor, not a fixed line count.

## Worked example

Scenario: `ProfileViewModel` both converts JSON and produces `ProfileUiState`. When server renames `avatar_url`, the ViewModel must change even though the screen contract did not. Move DTO mapping to repository/data; keep `ProfileUiState` logic in ViewModel. Test both boundaries separately.

## Trade-offs and decision criteria

Extract only independently changing concerns. A small class may legitimately contain several methods supporting one responsibility. Too many microscopic classes can obscure the use case and increase DI/build overhead.

## Failure modes

A “God ViewModel” changes for API schema, tax policy and UI copy in one release, causing regression outside the requested area. Characterization tests and incremental extraction reduce risk. Naming a class `UseCase` without moving policy does not fix cohesion.

## Production perspective

An ecommerce team separates checkout price policy from localized UI strings and provider transport. Product managers can change discounts without touching screen lifecycle code; UI redesign does not rewrite server mapping.

## Interview answer — short

Single Responsibility Principle dictates that a class should have only one reason to change (one business actor). In Android, instead of letting an Activity handle validation, network calls, storage, and UI rendering, we divide responsibilities into a Validator, a UseCase, a Repository, and a ViewModel.

## Interview answer — structured

The Single Responsibility Principle (SRP) states that a software component should have one, and only one, reason to change.

A 'reason to change' aligns directly with the business actor who requests the modification. If a single class caters to requests from the UI designer, the security officer, and the database administrator simultaneously, it severely violates SRP.

In Android, a textbook SRP violation is a monolithic Activity or ViewModel that performs.

First, input validation (e.g. Password complexity rules). Next, network API invocation and HTTP header management.
SQLite / SharedPreferences token persistence. Finally, UI layout manipulation and dialog animations.

To resolve this, we break responsibilities into cohesive units.

First, `PasswordValidator`: Pure validation rules (responds to security policy changes). Next, `AuthRepository`: Encapsulates network communication and token persistence (responds to backend API/storage changes).
`RegisterUserUseCase`: Orchestrates the registration business flow. Finally, `RegisterViewModel`: Projects results into `RegisterUiState` (responds to UI workflow changes).


## Interview answer — deep senior

A subtle pitfall when applying SRP is **over-fragmentation** (creating a new class for every single function). SRP is about **cohesion around a single actor**, not making classes microscopic. If five utility functions all serve the exact same business responsibility and change together, keeping them in one cohesive class respects SRP.

In unit testing, SRP delivers immediate gains. Testing `PasswordValidator` requires a 10-line JVM unit test verifying strings. If password rules were buried inside `RegistrationActivity`, testing them would require booting an Android Activity, finding view IDs, and dealing with Robolectric or espresso overhead.


## How to answer in the interview

- **Why:** Define reason to change.
- **How:** walk through the DTO/ViewModel split.
- **Trade-offs:** avoid class-count dogma.
- **Failure cases:** mention schema-coupled UI tests.
- **Production solutions:** end with narrow tests per boundary..

## Deep-dive talking points

Use change history to identify independent actors; compare line-count refactoring with actual cohesion.

## Follow-up questions

- **Interviewer:** "What is the relationship between SRP and Cohesion?"
  **Answer:** "Cohesion measures how closely related the functions within a class are. SRP maximizes cohesion by ensuring all methods in a class serve a single unified purpose."

- **Interviewer:** "How do you detect an SRP violation during code review?"
  **Answer:** "Look at the class imports: if a ViewModel imports SQLite, OkHttp, and Android View classes, or if the class description requires using the word 'AND' ('This class fetches data AND validates AND formats UI'), it violates SRP."

## Self-check rubric

Identify three reasons to change in one ViewModel, propose owners, and explain why one-method classes are unnecessary.

## References and reviewed-on date

- [Robert C. Martin, Single Responsibility Principle](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — change actors and cohesion.
- [Android UI layer](https://developer.android.com/topic/architecture/ui-layer) — ViewModel role.

Technically reviewed against primary documentation on 2026-10-13.
