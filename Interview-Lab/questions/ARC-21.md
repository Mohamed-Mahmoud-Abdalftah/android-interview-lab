---
id: "ARC-21"
question: "A ViewModel contains 1,000 lines of networking, mapping, and business logic. How do you refactor it incrementally?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "C"
phase: 2
priority: "P1"
order: 166
editorial_status: "reviewed"
---

# ARC-21

## Original interview question

A ViewModel contains 1,000 lines of networking, mapping, and business logic. How do you refactor it incrementally?

## What the interviewer evaluates

Show a safe incremental refactor with characterization tests, seam extraction and behavior preservation.

## Explanation in Arabic

كيف تقوم بإعادة هيكلة (Refactoring) كلاس ViewModel ضخم يحتوي على 1,000 سطر يجمع بين الشبكة، الـ Mapping، ومنطق البيزنس بشكل تدريجي وآمن؟

1. استراتيجية الـ Strangler Fig Pattern (التفكيك التدريجي دون إيقاف التطوير):
   - إياك أن تعيد كتابة الـ ViewModel من الصفر في فرع منفصل (Big Bang Rewrite)؛ هذا يؤدي إلى كوارث دمج ومشاكل لا تنتهي.
   - نقوم بإعادة الهيكلة بخطوات جراحية تدريجية في عدة PRs صغيرة ومختبرة.

2. خطوات إعادة الهيكلة خطوة بخطوة:
   - **الخطوة 1: كتابة Characterization Tests (شبكة أمان)**:
     * قبل كتابة سطر كود، اكتب اختبارات للـ ViewModel القديم تلتقط سلوكه الحالي بالكامل (حتى أخطائه) لضمان عدم كسر أي شيء.
   - **الخطوة 2: استخراج طبقة البيانات (Extract Data Layer)**:
     * سحب استدعاءات Retrofit و SharedPreferences والـ DTO Mappings ووضعها داخل `FeatureRepositoryImpl` خلف `Interface`.
   - **الخطوة 3: استخراج منطق العمليات المعقدة إلى Use Cases**:
     * عزل الحسابات والتحققات الضخمة داخل UseCases مخصصة (`ValidateOrderUseCase`, `CalculateShippingUseCase`).
   - **الخطوة 4: توحيد الـ UI State**:
     * دمج الـ 10 متغيرات LiveData/StateFlow المتفرقة في كائن `data class ScreenUiState` واحد.
   - **الخطوة 5: تنظيف الـ ViewModel ليصبح مجرد Coordinator نحيف (Thin ViewModel)**.

## Practical walkthrough

نموذج تحويل تدريجي لـ ViewModel ضخم:
```kotlin
// المرحلة 1: الـ ViewModel القديم (1000 سطر يجمع كل شيء):
class MonolithicCartViewModel : ViewModel() {
    // استدعاء شبكة مباشر، وحسابات أسعار، وSharedPreferences وUI State!
}

// المرحلة 2: سحب الـ Networking والـ Storage إلى Repository:
class CartRepositoryImpl(private val api: CartApi, private val prefs: CartPrefs) : CartRepository { ... }

// المرحلة 3: سحب العمليات المعقدة إلى Use Cases:
class ValidateCartUseCase(private val inventoryRepo: InventoryRepository) { ... }
class ApplyPromoCodeUseCase(private val promoRepo: PromoRepository) { ... }

// المرحلة 4: الـ ViewModel النظيف الناتج (أقل من 80 سطراً):
@HiltViewModel
class CleanCartViewModel @Inject constructor(
    private val cartRepository: CartRepository,
    private val validateCart: ValidateCartUseCase,
    private val applyPromo: ApplyPromoCodeUseCase
) : ViewModel() {
    val uiState: StateFlow<CartUiState> = cartRepository.observeCart()
        .map { CartUiState.Success(it) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), CartUiState.Loading)
}
```

## Why it matters and how it works

Incremental extraction reduces risk while establishing ownership. Tests capture observable behavior before moving code. The goal is thinner state holder and stable data/domain contracts, not merely fewer lines.

## Worked example

Refactor sequence: (1) assert `Loading -> Content/Error` for a representative API response; (2) introduce `ProfileRepository` behind existing ViewModel call; (3) move DTO-to-domain mapping; (4) move shared eligibility into use case; (5) replace direct Retrofit in ViewModel; (6) remove dead code after tests and telemetry agree. Each step is reviewable.

## Trade-offs and decision criteria

A big-bang rewrite may look clean but creates migration risk and lost edge cases. An incremental adapter can temporarily duplicate a call path; remove it after parity is established. Avoid extracting a use case for every helper before identifying real business responsibilities.

## Failure modes

Moving network code into a new repository but keeping `Response<Dto>` as the return type leaves UI coupled. Another failure is changing exception handling so a timeout becomes empty content. Test observable states, cancellation, and retry before and after.

## Production perspective

A mature retail app has a giant search ViewModel. Team extracts repository refresh and cache policy, adds domain search filters shared with catalog, and tracks crash/error metrics by phase. UI remains functional during staged rollout.

## Interview answer — short

Refactor a 1,000-line ViewModel incrementally using the Strangler Fig pattern: write baseline characterization tests, extract network and database calls into a Repository, extract heavy business rules into dedicated Use Cases, consolidate scattered state variables into a single immutable `UiState`, and verify zero behavior regression at each PR.

## Interview answer — structured

Refactoring a monolithic 1,000-line ViewModel requires a surgical, incremental migration strategy without halting feature delivery.

1. **Step 1: Characterization Testing**: Before modifying code, write baseline unit tests against the existing ViewModel. Capture its current inputs, outputs, and side-effects. This provides a safety net guaranteeing that subsequent extractions cause zero behavioral regressions.

2. **Step 2: Extract Data Access into a Repository**: Identify raw Retrofit calls, Room DAO queries, and SharedPreferences accesses. Move them into a concrete `FeatureRepositoryImpl` behind a clean interface. Inject the repository into the ViewModel. The ViewModel now consumes repository methods, shedding hundreds of lines of HTTP configuration and mapping.

3. **Step 3: Extract Domain Rules into Use Cases**: Identify dense business calculations (validation algorithms, discount computations, cross-repository logic). Extract each calculation into a dedicated, single-responsibility Use Case with pure JVM unit tests.

4. **Step 4: Consolidate State**: Migrate scattered `LiveData` variables (`isLoading`, `user`, `error`, `items`) into a single consolidated `StateFlow<ScreenUiState>`.

Ship each step as an independent, fully tested Pull Request.

## Interview answer — deep senior

The cardinal mistake in legacy refactoring is attempting a **Big Bang Rewrite** in an isolated branch for weeks. By the time the branch is ready, main branch merge conflicts are insurmountable, subtle production bugs are introduced, and business stakeholders are frustrated by halted feature velocity.

Using the **Strangler Fig pattern**, the legacy ViewModel delegates portions of its work to new clean components while continuing to serve production traffic. At any point during the multi-sprint refactoring, the application builds, tests pass, and features remain deployable.

Once all responsibilities are delegated, the legacy ViewModel collapses from 1,000 lines down to a lightweight 60-80 line coordinator whose only job is holding `uiState` and binding user gestures to Use Cases.

## How to answer in the interview

- **Why:** large VM hides multiple responsibilities.
- **How:** extract one behavior with regression test.
- **Trade-off:** incremental migration versus rewrite speed.
- **Failure case:** big bang loses edge cases.
- **Production solution:** ship slices with metrics and rollback.

## Deep-dive talking points

Describe characterization tests, an extraction sequence, parity criteria, coroutine ownership, and a rollback strategy.

## Follow-up questions

- **Interviewer:** "What is a Characterization Test?"
  **Answer:** "A test written to characterize the current behavior of legacy code as it actually exists, creating a baseline safety net so future refactoring does not alter existing functionality."

- **Interviewer:** "How do you avoid merge conflicts during a long refactoring project?"
  **Answer:** "By breaking refactorings into small, bite-sized PRs (extracting one repository or use case at a time) and merging directly to the main trunk behind feature flags if necessary."

## Self-check rubric

Propose three small PR steps, one behavior test, and one hidden coupling to remove.

## References and reviewed-on date

- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) — layer and state-holder guidance.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository role.

Technically reviewed against primary documentation on 2026-10-13.
