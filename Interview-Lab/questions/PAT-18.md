---
id: "PAT-18"
question: "How can patterns turn into unnecessary indirection? Give an example."
topic: "Design Patterns"
code: "PAT"
group: "C"
phase: 2
priority: "P1"
order: 209
editorial_status: "reviewed"
---

# PAT-18

## Original interview question

How can patterns turn into unnecessary indirection? Give an example.

## What the interviewer evaluates

Recognize accidental indirection and choose a simpler design with a concrete example.

## Explanation in Arabic

كيف تتحول أنماط التصميم إلى تعقيد زائد وتشتت غير ضروري (Unnecessary Indirection)؟ مع مثال عملي:

1. فخ الإفراط في تطبيق الأنماط (Over-Engineering & Pattern Abuse):
   - يحدث التعقيد غير المبرر عندما يطبق المطور أنماط التصميم لمجرد تطبيقها، دون وجود مشكلة حقيقية تتطلب ذلك (المرونة الخيالية للمستقبل - Speculative Generality).
   - النتيجة: شاشة بسيطة جداً تعرض قائمة عناصر ثابتة، تمر بـ 6 طبقات فارغة لا تفعل أي شيء سوى استدعاء الطبقة التي تليها:
     `Screen -> ViewModel -> GetItemsUseCase -> ItemsFacade -> ItemsRepository -> ItemsAdapter -> ItemsDao`
   - هذه الطبقات الفارغة تُعرف بـ **Pass-Through Indirection** أو **Middleman Code**.

2. أضرار الـ Unnecessary Indirection في مشاريع Android:
   - **صعوبة تتبع الكود واستكشاف الأخطاء (Cognitive Load & Debugging Hell)**: للانتقال من الضغط على الزر إلى قراءة قاعدة البيانات، تضطر للقفز بين 7 ملفات مختلفة لا تحتوي أي منها على منطق برمجي حقيقي.
   - **بطء التطوير وتضخم الـ Boilerplate**: لإضافة حقل واحد، تضطر لتعديل 6 كلاسات و 6 اختبارات و 6 DTOs مختلفة.
   - **تضخم الـ DI Graph**: استهلاك وقت تجميع أطول (Build Time) واستهلاك ذاكرة إضافي للكائنات غير الضرورية.

3. المعيار الواقعي لمهندس البرمجيات الأول (Senior Rule of Thumb):
   - أضف طبقة تجريد (Indirection) فقط عندما يكون هناك: **تعدد في التطبيقات (Multiple Implementations)**، أو **منطق عمل معقد قابل لإعادة الاستخدام (Reusable Domain Logic)**، أو **حدود استقرار لعزل تبعية خارجية متقلبة (Volatile Boundary)**. إذا كان الـ Use Case يكتفي بسطر واحد `repository.getData()` بدون أي شروط أو دمج، فاحذفه واستدعِ الـ Repository مباشرة من الـ ViewModel.

## Practical walkthrough

المقارنة بين التعقيد الزائد المتكلف وبين التصميم العملي المباشر:
```kotlin
// ❌ تعقيد غير ضروري (Unnecessary Indirection): 4 طبقات وسيطة لا تفعل شيئاً سوى التمرير!
class GetAppThemeUseCase @Inject constructor(private val repo: ThemeRepository) {
    suspend operator fun invoke(): Theme = repo.getTheme() // مجرد وسيط فارغ!
}
class ThemeRepositoryImpl @Inject constructor(private val facade: ThemeFacade) : ThemeRepository {
    override suspend fun getTheme(): Theme = facade.fetch() // وسيط آخر!
}
class ThemeFacade @Inject constructor(private val adapter: ThemeAdapter) {
    suspend fun fetch(): Theme = adapter.get() // وسيط ثالث!
}

// ✅ تصميم مباشر وعملي (Pragmatic & Clean): ViewModel يتحدث مباشرة إلى Repository:
interface ThemePreferences {
    val isDarkMode: Flow<Boolean>
    suspend fun setDarkMode(enabled: Boolean)
}

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val themePreferences: ThemePreferences
) : ViewModel() {
    val isDarkMode = themePreferences.isDarkMode.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = false
    )
    
    fun toggleDarkMode(enabled: Boolean) {
        viewModelScope.launch { themePreferences.setDarkMode(enabled) }
    }
}
// وفرنا 4 كلاسات فارغة، كود مقروء في 10 ثوانٍ، وتكلفة صيانة صفرية!
```

## Why it matters and how it works

Patterns encode trade-offs; without the forces they solve, they add navigation and maintenance cost. A simpler direct collaboration can be more testable and readable. Keep correctness boundaries even when removing ceremony.

## Worked example

Concrete simplification: replace a one-line `GetThemeUseCase` and `ThemeFacade` with `SettingsViewModel(settingsRepository)` if they add no policy. Repository still owns DataStore access and main-safety; ViewModel produces UI state. This removes indirection without sending I/O into Compose.

## Trade-offs and decision criteria

Too little structure can leak DTOs or duplicate business rules. Too much structure makes local changes touch many wrappers. Choose a seam when independent change, substitution or reuse is demonstrated. Keep a path to extract later.

## Failure modes

A new setting requires editing six forwarding interfaces and generated bindings but no new behavior. Refactor to direct repository use. Conversely, removing the repository and calling DataStore from UI would lose ownership; simplify only ceremonial layers.

## Production perspective

A small settings feature ships with two clear classes and behavior tests. When profile and checkout later share a policy, team extracts one focused use case; they do not prebuild a generic pattern framework.

## Interview answer — short

Design patterns turn into unnecessary indirection when abstractions are introduced without multiple implementations, complex domain logic, or volatile boundaries. A classic example is a 1-line 'pass-through' UseCase wrapping a Repository that wraps a Facade for simple read operations, dramatically increasing cognitive load, boilerplate, and build times without providing any architectural benefit.

## Interview answer — structured

Design patterns exist to manage variation and isolate volatile change. When applied dogmatically without actual variation, they create unnecessary indirection—often called 'speculative generality' or 'architecture astronautics'.

A prime Android example is dogmatic Clean Architecture where every single screen must have a Use Case, even for trivial reads: `ViewModel -> GetUserProfileUseCase -> ProfileRepository -> ProfileDataSource -> Dao`. If `GetUserProfileUseCase` contains literally one line: `repository.getProfile()`, it adds zero value. It provides no validation, no composition, and no caching. Instead, it doubles the file count, bloats the Dagger dependency graph, increases build times, and forces developers to jump through five files just to understand a simple database query.

A senior engineer practices pragmatic architecture: consume the `ProfileRepository` directly from the `ViewModel` for straightforward CRUD operations. Extract a Use Case only when you have business logic that orchestrates multiple repositories, applies complex calculation rules, or is reused across multiple ViewModels.

## Interview answer — deep senior

The cost of indirection is measured in **Cognitive Complexity, Build Overhead, and Refactoring Friction**.

1. **The 'Tax' of an Abstraction**: Every layer requires: an interface, an implementation, DTO mapping functions, Dagger `@Provides` / `@Binds` bindings, and mock setup in unit tests. If the abstraction does not encapsulate volatility, you pay this architectural tax on every sprint without ever reaping the benefits.

2. **Symptoms of Accidental Complexity in Codebases**:
   - **Shotgun Surgery**: Adding a single boolean flag to an entity forces edits across 7 distinct files (DTO, Mapper, Domain Model, UseCase, Repository, ViewModel, UI State).
   - **Pass-through Methods**: Methods whose sole implementation is `return collaborator.execute(args)` without mutation or validation.
   - **Factories with Single Products**: Writing abstract factories for classes that will only ever have one concrete implementation on Android.

3. **Pragmatic Heuristics (YAGNI & Rule of Three)**: Never introduce an abstraction for an anticipated future requirement. Wait until you have at least two distinct concrete implementations or concrete business rules before introducing a UseCase or Strategy. Simplicity is an active design decision, not a lack of design.

## How to answer in the interview

- **Why:** Indirection costs reading, debugging and API churn.
- **How:** Walk a theme call graph and remove pass-through layers.
- **Trade-off:** Keep a layer when it owns reuse, policy, validation or boundary.
- **Failure case:** Pattern names hide no-op forwarding and obscure errors.
- **Production solution:** Simplify call sites, preserve data boundary and verify tests.

## Deep-dive talking points

Trace a six-wrapper chain, identify pass-through layers, retain useful repository ownership and extraction trigger.

## Follow-up questions

- **Interviewer:** "When IS a Use Case genuinely necessary in Android?"
  **Answer:** "When it coordinates multiple repositories (e.g., checkout requiring PaymentRepo, CartRepo, and InventoryRepo), applies complex domain validation rules, or is reused across multiple feature ViewModels."

- **Interviewer:** "What is the difference between essential complexity and accidental complexity?"
  **Answer:** "Essential complexity is inherent to the business domain problem itself. Accidental complexity is introduced by the developer's choice of excessive layers, unnecessary patterns, and boilerplate."

## Self-check rubric

Remove two ceremonial wrappers from a sample chain while preserving data/UI correctness boundaries.

## References and reviewed-on date

- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — optional use cases.
- [GoF pattern catalog](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — original pattern context.

Technically reviewed against primary documentation on 2026-10-13.
