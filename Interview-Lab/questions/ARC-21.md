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

## Concept and technical explanation

Incrementally refactoring a 1,000-line monolithic ViewModel requires adopting the Strangler Fig pattern to surgically extract concerns into decoupled components without halting feature delivery or causing regressions. A monolithic ViewModel typically conflates network requests, persistent caching, DTO transformations, validation rules, and disparate UI state holders. Rather than undertaking a high-risk Big Bang rewrite in an isolated feature branch, senior engineers establish a baseline safety net by writing characterization unit tests against the existing ViewModel. Refactoring then proceeds through discrete, verifiable steps: extracting data transport and storage operations into concrete Repositories, isolating complex business calculations into dedicated Use Cases, consolidating fragmented state primitives into a single immutable UiState, and reducing the ViewModel to a lightweight state orchestrator.

## Practical walkthrough (English)

Incrementally decomposing a 1,000-line monolithic ViewModel:
```kotlin
// Step 1: Characterization test captures existing black-box behavior before touching code
class MonolithicCartViewModelTest {
    @Test
    fun existingCheckoutFlow_emitsExpectedStatus() = runTest {
        val vm = MonolithicCartViewModel(fakeApi, fakeDb)
        vm.checkout("user_123")
        assertEquals(true, vm.isCheckoutSuccess.value)
    }
}

// Step 2: Extract data persistence and network calls into a clean Repository
class CartRepositoryImpl(
    private val cartApi: CartApi,
    private val cartDao: CartDao
) : CartRepository {
    override suspend fun checkoutCart(userId: String): Result<OrderReceipt> = runCatching {
        val remoteOrder = cartApi.submitOrder(userId)
        cartDao.clearCart()
        remoteOrder.toDomain()
    }
}

// Step 3: Extract business rules into a dedicated UseCase
class ValidateCheckoutEligibilityUseCase(private val userRepo: UserRepository) {
    operator fun invoke(cartTotal: Double): CheckoutValidationResult {
        if (cartTotal <= 0.0) return CheckoutValidationResult.EmptyCart
        return CheckoutValidationResult.Eligible
    }
}

// Step 4: Final Refactored ViewModel becomes a thin (<80 line) coordinator
@HiltViewModel
class CleanCartViewModel @Inject constructor(
    private val cartRepository: CartRepository,
    private val validateEligibility: ValidateCheckoutEligibilityUseCase
) : ViewModel() {
    private val _uiState = MutableStateFlow<CartUiState>(CartUiState.Idle)
    val uiState: StateFlow<CartUiState> = _uiState.asStateFlow()

    fun onCheckoutClicked(total: Double) {
        when (validateEligibility(total)) {
            is CheckoutValidationResult.EmptyCart -> _uiState.value = CartUiState.Error("Cart is empty")
            is CheckoutValidationResult.Eligible -> processCheckout()
        }
    }

    private fun processCheckout() = viewModelScope.launch {
        _uiState.value = CartUiState.Loading
        cartRepository.checkoutCart("user_id")
            .onSuccess { receipt -> _uiState.value = CartUiState.Success(receipt.orderId) }
            .onFailure { error -> _uiState.value = CartUiState.Error(error.message ?: "Failed") }
    }
}
```

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

Refactor a 1,000-line ViewModel incrementally using the Strangler Fig pattern: write baseline characterization tests to capture existing behavior, extract network and database calls into a Repository, extract heavy business rules into dedicated Use Cases, consolidate scattered state variables into a single immutable UiState, and verify zero behavior regression with small, atomic pull requests.

## Interview answer — structured

Refactoring a monolithic 1,000-line ViewModel requires a disciplined, step-by-step migration to prevent regression while keeping active development unblocked.
The process begins with establishing characterization tests. Before changing a single line of production code, we write black-box unit tests asserting the ViewModel's existing inputs, outputs, and side-effects. This creates an automated safety net ensuring subsequent extractions preserve system behavior.
Next, we extract data access into a dedicated Repository. Direct Retrofit API calls, Room database transactions, and SharedPreferences operations are migrated into a concrete repository implementation behind an interface. Injecting this repository into the ViewModel immediately eliminates hundreds of lines of HTTP configuration and DTO mappings.
Following data isolation, we extract domain business logic into single-responsibility Use Cases. Validation routines, complex mathematical calculations, and multi-source workflows are isolated into pure Kotlin classes with focused unit tests.
Finally, we consolidate fragmented UI state. Scattered LiveData or StateFlow flags—such as loading booleans, error strings, and data models—are merged into a single immutable UiState data class, transforming the ViewModel into a thin coordinator of under eighty lines.

## Interview answer — deep senior

Under the hood, attempting a Big Bang rewrite of a massive legacy ViewModel represents one of the highest risks in software engineering. Over months of parallel feature development, isolated rewrite branches suffer severe merge conflicts, miss subtle production bugfixes, and halt regular release cycles.
Employing the Strangler Fig pattern avoids this trap by migrating old functionality slice by slice within the main production branch. At every commit, the application compiles, existing tests pass, and new features continue shipping to production.
During the extraction of data access, engineers must maintain strict boundary isolation. When moving Retrofit calls out of the ViewModel, raw network DTOs must not leak back into presentation code; the newly introduced Repository must map responses into clean Domain models before returning them.
When consolidating UI state, legacy ViewModels often suffer from race conditions where separate StateFlow variables update asynchronously, causing UI composables to render invalid intermediate combinations such as displaying a progress bar while showing an error banner. Merging these primitives into a single sealed hierarchy or cohesive data class guarantees atomic state transitions.
Staff engineers coordinate this refactor across four to five small Pull Requests, accompanied by code coverage metrics and production crash monitoring. By the conclusion of the refactor, the ViewModel is reduced from a messy thousand-line god object to a declarative coordinator focusing solely on UI state binding and event forwarding.

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
