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

## Concept and technical explanation

Architectural boundary discipline dictates clear responsibility allocation among ViewModel, UseCase, and Repository to prevent God classes and maintain modular cohesion. The ViewModel (Presentation) acts as a lifecycle-aware state holder that manages UI state production, handles user interactions, triggers navigation events, survives configuration changes, and formats domain data into presentation models. It must never reference View hierarchies, hold Android Activity Context, or execute business transactions directly. The UseCase (Domain) encapsulates single-responsibility, framework-agnostic business logic, mathematical computations, input validation rules, and cross-repository orchestration. The Repository (Data) serves as the authoritative single source of truth for an aggregate entity, mediating between remote APIs, local databases, and caches while managing data synchronization, offline persistence, and entity mapping.

## Practical walkthrough (English)

Mapping clear separation of concerns in a funds transfer feature:
```kotlin
// 1. DATA LAYER: Data synchronization and remote execution
class TransferRepositoryImpl(private val api: BankingApi, private val dao: AccountDao) : TransferRepository {
    override suspend fun sendMoney(recipientId: String, amount: Double): Result<TransactionId> = runCatching {
        api.postTransfer(TransferRequest(recipientId, amount)).toDomain()
    }
}

// 2. DOMAIN LAYER: Pure business validation and orchestration
class SendMoneyUseCase(
    private val accountRepo: AccountRepository,
    private val transferRepo: TransferRepository
) {
    suspend operator fun invoke(recipientId: String, amount: Double): Result<TransactionId> {
        if (amount <= 0.0) return Result.failure(IllegalArgumentException("Amount must exceed zero"))
        val balance = accountRepo.getCurrentBalance()
        if (balance < amount) return Result.failure(IllegalStateException("Insufficient funds"))
        return transferRepo.sendMoney(recipientId, amount)
    }
}

// 3. PRESENTATION LAYER: UI state management and user action dispatch
class TransferViewModel(
    private val sendMoneyUseCase: SendMoneyUseCase
) : ViewModel() {
    private val _uiState = MutableStateFlow<TransferUiState>(TransferUiState.Idle)
    val uiState: StateFlow<TransferUiState> = _uiState.asStateFlow()

    fun onTransferConfirmed(recipientId: String, rawAmount: String) {
        val amount = rawAmount.toDoubleOrNull() ?: run {
            _uiState.value = TransferUiState.Error("Invalid amount format")
            return
        }
        viewModelScope.launch {
            _uiState.value = TransferUiState.Loading
            sendMoneyUseCase(recipientId, amount)
                .onSuccess { _uiState.value = TransferUiState.Success(it.value) }
                .onFailure { _uiState.value = TransferUiState.Error(it.localizedMessage ?: "Transfer failed") }
        }
    }
}
```

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

ViewModel holds and manages UI state, responding to user actions and surviving configuration changes. UseCase encapsulates specific business rules and multi-repository workflows. Repository manages data sources, caching policies, and data synchronization as a single source of truth.

## Interview answer — structured

Assigning responsibilities cleanly across ViewModel, UseCase, and Repository prevents monolithic classes and keeps codebases maintainable.

The ViewModel is a presentation state holder that lives in the presentation layer. It manages UI state lifecycles, observes domain streams, translates raw business data into display-ready UI models, and processes user events while surviving screen rotations.

In production, the UseCase resides in the domain layer and owns pure business logic. It handles calculations, domain validations, authorization checks, and orchestrates workflows that touch multiple repositories.
As for the Repository, it belongs to the data layer and acts as the single source of truth for an aggregate entity. It coordinates remote network calls, Room database caching, offline synchronization, and local storage, ensuring upper layers remain unaware of whether data originates from memory, disk, or the cloud.


## Interview answer — deep senior

Under the hood, drawing explicit boundaries between ViewModel, UseCase, and Repository ensures high cohesion and localized failure modes. A common architectural smell in Android applications is the Fat ViewModel, where developers place network API calls, database queries, and business calculations directly inside ViewModel coroutines. This tightly couples presentation logic with business rules, making automated testing cumbersome and causing memory leaks if Android Context is captured.
The rule of thumb for placement is clear: if a concern relates to how data is displayed, screen lifecycle, or navigation events, it belongs in the ViewModel. If a rule must execute regardless of whether the request came from a Composable, a WearOS notification, or a WorkManager background job—such as validating an account balance before a transfer—it belongs in a UseCase. If logic decides whether to read from SQLite or fetch fresh JSON over HTTP, it belongs in the Repository.
Staff engineers enforce that ViewModels never reference Android View hierarchies, Activity contexts, or database DAOs. Furthermore, Repositories never expose UI-specific models or framework errors; they catch low-level IOExceptions and SQLiteExceptions, translating them into domain-safe failure abstractions before passing them upward. This strict separation guarantees that features remain robust, testable, and adaptable to future platform changes.

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
