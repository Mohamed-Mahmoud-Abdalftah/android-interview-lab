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

## Concept and technical explanation

The Single Responsibility Principle (SRP) states that a class, module, or function should have one, and only one, reason to change, meaning it must be responsible to only a single business actor, stakeholder, or operational role. In Android development, SRP serves as the primary antidote against God Activities, God Fragments, and bloated ViewModels. A component that simultaneously coordinates UI rendering, inflates menus, validates user input, constructs HTTP requests, reads SQLite tables, and logs analytics events has half a dozen reasons to change. Violating SRP couples unrelated business concerns, creating severe regression risks whenever any individual responsibility is modified.

## Practical walkthrough (English)

Refactoring a God ViewModel violating SRP into cohesive, single-purpose components:
```kotlin
// BAD ANTI-PATTERN: Violates SRP (Too many reasons to change: validation, network, DB, UI state)
class BadRegistrationViewModel(private val api: Api, private val db: AppDb) : ViewModel() {
    fun register(email: String, pass: String) {
        if (!email.contains("@")) return // Reason 1: Validation policy changes
        val response = api.registerUser(email, pass) // Reason 2: API endpoints or auth headers change
        db.userDao().insert(response.toEntity()) // Reason 3: Database schema or caching rules change
        // Reason 4: UI presentation formatting changes
    }
}

// ARCHITECTURAL BEST PRACTICE: Single Responsibility per component
class EmailValidator @Inject constructor() { // One reason: Email format policies
    fun isValid(email: String): Boolean = email.isNotBlank() && email.matches(Regex("^[A-Za-z0-9+_.-]+@(.+)\$"))
}

class RegisterUserUseCase @Inject constructor( // One reason: Registration business orchestration
    private val validator: EmailValidator,
    private val userRepository: UserRepository
) {
    suspend operator fun invoke(email: String, pass: String): Result<User> {
        if (!validator.isValid(email)) return Result.failure(InvalidEmailException())
        return userRepository.register(email, pass)
    }
}

class RegistrationViewModel @Inject constructor( // One reason: Managing Registration UI State
    private val registerUser: RegisterUserUseCase
) : ViewModel() {
    private val _uiState = MutableStateFlow<RegUiState>(RegUiState.Idle)
    val uiState: StateFlow<RegUiState> = _uiState.asStateFlow()
    fun onRegisterClicked(email: String, pass: String) { /* Updates UI state only */ }
}
```

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

The Single Responsibility Principle dictates that a class should have only one reason to change, meaning it serves a single actor or concern. In Android, violating SRP creates God Activities that validate inputs, call network APIs, manage database caching, and format UI layouts. Applying SRP separates these responsibilities into distinct components: a Validator for input rules, a UseCase for business logic, a Repository for data persistence, and a ViewModel strictly for managing UI state.

## Interview answer — structured

The Single Responsibility Principle ensures that software components remain focused, maintainable, and isolated from unrelated feature churn.
In Android development, the most frequent violation of SRP is the God Class anti-pattern. Developers frequently cram entire user journeys into a single Activity or ViewModel. When a single class parses JSON, formats currency strings, interacts with GPS location managers, queries Room databases, and binds views, any change requested by product managers, design teams, or backend architects forces edits to the exact same file. This creates high cognitive friction, frequent merge conflicts, and high regression risks.
To adhere to SRP, responsibilities must be decomposed along natural actor boundaries.
The UI layer (Activity, Fragment, or Compose function) is responsible exclusively for rendering pixels and capturing user gestures. The ViewModel is responsible strictly for holding and exposing UI state machines.
Business rules and multi-repository coordination are encapsulated inside isolated UseCase classes, such as RegisterUserUseCase. Validation logic is moved into pure utility classes like EmailValidator, and data storage policies live inside Repositories.
Each class now has exactly one reason to change, making the codebase intuitive to navigate and trivially easy to unit test in isolation.

## Interview answer — deep senior

Under the hood, Robert C. Martin refined the definition of SRP to state: 'A module should be responsible to one, and only one, actor.' Understanding this actor-based framing is what separates junior pattern matching from senior architectural design.
An actor represents a cohesive group of users, stakeholders, or system departments requiring changes. For example, marketing defines analytics formatting, the security team defines password hashing constraints, the DBA defines offline caching schemas, and the design team defines UI loading indicators.
If all four concerns live in a single UserProfileViewModel, changes demanded by marketing can inadvertently break authentication hashing or introduce database deadlocks across background threads.
Furthermore, enforcing SRP directly impacts compilation speed and memory utilization. In modern multi-module Gradle setups, dividing responsibilities creates distinct modules: :core:validation, :domain:auth, and :feature:auth. When validation logic changes, Gradle re-compiles only the tiny validation module without recompiling domain logic or presentation bytecode.
At the runtime level, single-responsibility classes adhere closely to the High Cohesion / Low Coupling principle. Their method dispatch tables remain small, optimizing ART inline caching, and their localized memory references ensure high CPU cache locality during execution, avoiding the creation of bloated objects that linger in generation-zero heap memory and trigger unnecessary garbage collection pauses.

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
