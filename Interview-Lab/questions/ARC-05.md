---
id: "ARC-05"
question: "What belongs in ViewModel versus UseCase versus Repository?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 150
editorial_status: "reviewed"
---

# ARC-05

## Original interview question

What belongs in ViewModel versus UseCase versus Repository?

## What the interviewer evaluates

Place UI state/lifecycle, reusable policy, and data-source coordination with the right owner.

## Explanation in Arabic

ما الذي ينتمي إلى الـ ViewModel مقابل الـ UseCase مقابل الـ Repository؟ وكيف نقسم المسؤوليات بينهم؟

1. ما ينتمي إلى الـ ViewModel:
   - **إدارة دورة حياة الواجهة (UI Lifecycle Management)**: الصمود أثناء تدوير الشاشة (Configuration Changes).
   - **تجهيز وإدارة الـ UI State**: استقبال البيانات وتحويلها إلى `StateFlow<UiState>` يسهل على Compose عرضه مباشرة.
   - **معالجة مدخلات المستخدم (User Interactions)**: استقبال نقرات الأزرار، تبديل التبويبات، والتحقق من صحة الفورم البصرية (Form validation).
   - **لا يحتوي أبداً على**: استدعاءات Retrofit مباشرة، منطق حسابات البزنس المعقدة، أو مراجع لـ Android Views و Context!

2. ما ينتمي إلى الـ UseCase:
   - **قواعد وسياسات العمل (Business Policies)**: حساب الضرائب، التأكد من شروط ترقية العضوية، فحص الصلاحيات.
   - **التنسيق بين مستودعات متعددة (Cross-Repository Coordination)**: سحب بيانات من `UserRepository` والدفع عبر `PaymentRepository` وتحديث `AnalyticsRepository`.
   - **إعادة استخدام المنطق عبر شاشات متعددة (Shared Business Logic)**.

3. ما ينتمي إلى الـ Repository:
   - **استراتيجية التخزين والكاش (Caching Strategy)**: متى نقرأ من الـ Database ومتى نسحب من الـ Network.
   - **مزامنة البيانات (Offline Sync)**: حفظ البيانات محلياً وإرسالها عند توفر الإنترنت.
   - **Mapping**: تحويل DTOs و SQLite Rows إلى Domain Models.

## Practical walkthrough

مثال عملي يوضح الحدود الصارمة للمسؤوليات:
```kotlin
// 1. REPOSITORY: إدارة البيانات والكاش والشبكة فقط:
class OrderRepositoryImpl(private val api: OrderApi, private val dao: OrderDao) : OrderRepository {
    override suspend fun submitOrder(order: Order): Result<OrderConfirmation> = runCatching {
        val response = api.postOrder(order.toDto())
        dao.insertOrder(response.toEntity())
        response.toDomain()
    }
}

// 2. USE CASE: قواعد البيزنس والتحقق والتنسيق بين مستودعين:
class PlaceOrderUseCase @Inject constructor(
    private val orderRepo: OrderRepository,
    private val inventoryRepo: InventoryRepository
) {
    suspend operator fun invoke(order: Order): OrderResult {
        if (order.items.isEmpty()) return OrderResult.Error("Cart is empty")
        val inStock = inventoryRepo.checkStock(order.items)
        if (!inStock) return OrderResult.Error("Items out of stock")
        return orderRepo.submitOrder(order).fold(
            onSuccess = { OrderResult.Success(it) },
            onFailure = { OrderResult.Error(it.message ?: "Submission failed") }
        )
    }
}

// 3. VIEWMODEL: إدارة حالة الواجهة والتفاعل فقط:
@HiltViewModel
class CheckoutViewModel @Inject constructor(
    private val placeOrder: PlaceOrderUseCase
) : ViewModel() {
    private val _uiState = MutableStateFlow<CheckoutUiState>(CheckoutUiState.Idle)
    val uiState: StateFlow<CheckoutUiState> = _uiState.asStateFlow()

    fun onPlaceOrderClicked(order: Order) {
        viewModelScope.launch {
            _uiState.value = CheckoutUiState.Loading
            when (val result = placeOrder(order)) {
                is OrderResult.Success -> _uiState.value = CheckoutUiState.Success(result.confirmation)
                is OrderResult.Error -> _uiState.value = CheckoutUiState.Error(result.message)
            }
        }
    }
}
```

## Why it matters and how it works

Screen state holder owns state production and event handling. Domain use cases encapsulate reusable business operations. Repositories expose data and coordinate sources. Keeping owners distinct makes lifecycle, testing, and change impact clearer.

## Worked example

Conceptual flow: `TransferViewModel.onSubmit` disables duplicate UI submit and calls `SubmitTransferUseCase`; the use case enforces amount rules and invokes `TransfersRepository`; repository sends with an idempotency key and persists pending status; ViewModel maps result to `TransferUiState`. Server still validates the transfer.

## Trade-offs and decision criteria

A small screen can call a repository directly. Do not move every `map` into a use case: formatting or selection purely for a screen can live in Presentation. Conversely, a rule needed by multiple screens should not be copied across ViewModels.

## Failure modes

A 1,000-line ViewModel that parses JSON and retries network requests becomes hard to test and lifecycle-sensitive. A repository that emits Snackbar string resources leaks UI concerns. A use case that holds Activity context is not presentation-independent.

## Production perspective

A checkout feature tests ViewModel state transitions with a fake use case, transfer policy with fake repositories, and repository sync with fake service/DAO. Production logs distinguish user action, policy rejection, and transport uncertainty.

## Interview answer — short

ViewModel manages UI lifecycle and exposes `StateFlow<UiState>` to the presentation layer. UseCase encapsulates business operations, validating policies and coordinating multiple repositories. Repository mediates between network, local database, and in-memory caches, abstracting storage mechanisms.

## Interview answer — structured

Clear boundary division among ViewModel, UseCase, and Repository prevents monolithic architectural bloat.

First, **ViewModel (Presentation Layer)**. Next, owns UI state and survives configuration changes.
Converts domain outputs into immutable `StateFlow<UiState>` tailored for rendering. Translates raw user actions into business commands.
Never performs I/O directly, never references Android `Context`, and contains zero business calculations. **UseCase (Domain Layer)**.
Encapsulates discrete, reusable business rules (e.g. Eligibility criteria, tax calculations). Coordinates multiple repositories (e.g. Querying user balance from `AccountRepository` and deducting inventory from `ProductRepository`).
Operates strictly on pure Kotlin domain models without UI or database dependencies. **Repository (Data Layer)**.
Single source of truth for a specific data aggregate. Decides whether to query local database, fetch from network, or return cached memory.
Finally, maps external schemas (DTOs, Room entities) to clean domain models.


## Interview answer — deep senior

A frequent anti-pattern is **Fat ViewModel Syndrome**, where ViewModels perform data mapping, HTTP header configuration, and multiple repository joins directly. This makes ViewModels massive (1,000+ lines) and untestable without heavy mocking.

Conversely, pushing business rules down into Repositories is an equal architectural mistake. A Repository should never know business policy (e.g. 'a gold member gets 15% discount'); the Repository simply stores and retrieves orders and user profiles. Calculating the discount is the strict domain responsibility of a Use Case.

By strictly adhering to these boundaries, each component remains easily testable in isolation: Repositories are verified via Fake DataSources, UseCases are verified via Fake Repositories, and ViewModels are verified by asserting `uiState` emissions.


## How to answer in the interview

- **Why:** one owner per kind of decision.
- **How:** route event through VM, policy and data.
- **Trade-off:** smaller classes versus navigation overhead.
- **Failure case:** VM becomes network and ledger god object.
- **Production solution:** refactor slice with regression test.

## Deep-dive talking points

Walk a transfer submit from tap to server confirmation. Separate UI duplicate-tap handling, policy validation, data retry, and server authority.

## Follow-up questions

- **Interviewer:** "Can a UseCase call another UseCase?"
  **Answer:** "Yes, when one complex business operation depends on a foundational business policy (e.g. `CheckoutCartUseCase` calling `ValidateCouponUseCase`). However, deep nesting should be avoided to prevent call stack confusion."

- **Interviewer:** "Why shouldn't a Repository expose a `UiState`?"
  **Answer:** "A Repository serves the domain, not the UI. Coupling a Repository to `UiState` makes it impossible to reuse across different screens or background workers with different presentation requirements."

## Self-check rubric

Place four lines of transfer code with ViewModel, UseCase, or Repository; explain why an uncertain result cannot be treated as success.

## References and reviewed-on date

- [Android UI layer](https://developer.android.com/topic/architecture/ui-layer) — ViewModel state-holder role.
- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — use-case scope.

Technically reviewed against primary documentation on 2026-10-13.
