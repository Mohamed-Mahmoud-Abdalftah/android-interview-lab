---
id: "ARC-09"
question: "How does UI state differ from business/domain state?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 154
editorial_status: "reviewed"
---

# ARC-09

## Original interview question

How does UI state differ from business/domain state?

## What the interviewer evaluates

Separate durable business facts from screen-specific rendering and interaction state.

## Concept and technical explanation

Differentiating UI state from business/domain state is a foundational architectural boundary that prevents transient presentation mechanics from contaminating core enterprise data models. Domain state represents the persistent, authoritative business truth of an application—such as an authenticated user profile, bank account balance, or items in a shopping cart. It is governed by enterprise invariants, maintained in repositories, persisted in databases or remote backends, and survives screen transitions. UI state represents the transient, presentation-specific configuration of what is currently rendered on screen—such as loading progress indicators, accordion expand/collapse toggles, text field focus, selected tabs, or localized validation error banners. UI state is derived from domain streams, owned by ViewModels, scoped strictly to screen lifecycles, and discarded upon screen completion.

## Practical walkthrough (English)

Contrasting persistent domain state with transient UI state in a banking dashboard:
```kotlin
// 1. DOMAIN STATE: Persistent, authoritative, business truth
data class AccountBalance(
    val accountId: String,
    val availableBalance: BigDecimal,
    val currency: Currency,
    val isFrozen: Boolean
)

// 2. UI STATE: Transient, display-specific projection
data class AccountDashboardUiState(
    val isLoading: Boolean = false,
    val formattedBalance: String = "",       // e.g. "$12,450.00"
    val isBalanceVisible: Boolean = true,     // Toggle eye icon (UI only)
    val isTransferButtonEnabled: Boolean = false,
    val userErrorMessage: String? = null
)

// 3. ViewModel derives UI state by combining domain stream with UI toggle flow
class AccountDashboardViewModel(
    private val accountRepository: AccountRepository
) : ViewModel() {
    private val isBalanceVisibleFlow = MutableStateFlow(true)

    val uiState: StateFlow<AccountDashboardUiState> = combine(
        accountRepository.observeBalance(),
        isBalanceVisibleFlow
    ) { balance, isVisible ->
        AccountDashboardUiState(
            isLoading = false,
            formattedBalance = if (isVisible) "$${balance.availableBalance}" else "••••••",
            isBalanceVisible = isVisible,
            isTransferButtonEnabled = !balance.isFrozen && balance.availableBalance > BigDecimal.ZERO,
            userErrorMessage = if (balance.isFrozen) "Account is temporarily locked" else null
        )
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), AccountDashboardUiState(isLoading = true))

    fun toggleBalanceVisibility() {
        isBalanceVisibleFlow.update { !it } // Modifies transient UI state only!
    }
}
```

## Explanation in Arabic

كيف تختلف حالة الواجهة (UI State) عن حالة الأعمال/النطاق (Business / Domain State)؟

1. ما هي حالة الأعمال (Business / Domain State)؟
   - تمثل الحقيقة الأساسية للبيانات والمنتج (Source of Truth) بصرف النظر عن كيفية أو مكان عرضها.
   - أمثلة: رصيد الحساب البنكي، عناصر سلة التسوق الفعلية في قاعدة البيانات، وحالة اشتراك المستخدم (Active / Expired).
   - تتميز بأنها: طويلة الأجل (Long-lived)، مستقلة عن أجهزة العرض وشاشات الهواتف، ولا تتغير بمجرد تفاعل بصري.

2. ما هي حالة الواجهة (UI State)؟
   - تمثل ما يراه المستخدم ويتفاعل معه على الشاشة في اللحظة الراهنة.
   - أمثلة: هل مؤشر التحميل (Spinner) ظاهر؟ ما هو نص رسالة الخطأ المترجمة المعروضة؟ أي تبويب محدد حالياً؟ هل القائمة منسدلة (Expanded)؟ وما هو النص المكتوب في حقل البحث؟
   - تتميز بأنها: مؤقتة (Ephemeral)، تعيش مع الشاشة، وتتأثر بالحجم والدوران ونوع الجهاز.

3. لماذا يُعتبر الخلط بينهما خطأ معمارياً فادحاً؟
   - إذا قمت بحفظ متغير مثل `isDropdownExpanded: Boolean` داخل الـ Domain Entity، فإنك لوثت بيانات البزنس بتفاصيل واجهة مستخدم مؤقتة لا معنى لها في قاعدة البيانات أو على السيرفر!

## Practical walkthrough

توضيح الفرق العملي بين Domain State و UI State وكيف يحول الـ ViewModel بينهما:
```kotlin
// 1. DOMAIN STATE (حالة البزنس النقية - تعيش في Domain/Database):
data class BankAccount(
    val accountNumber: String,
    val balanceCents: Long,
    val currency: String,
    val isOverdrawn: Boolean
)

// 2. UI STATE (حالة العرض المخصصة للشاشة - تعيش في Presentation):
@Immutable
data class AccountDetailsUiState(
    val isLoading: Boolean = false,
    val formattedBalance: String = "", // مجهزة للعرض المباشر: "-$150.00"
    val balanceColor: Color = Color.Black, // أحمر إذا كان مكشوفاً
    val isDepositButtonEnabled: Boolean = true,
    val errorMessage: String? = null
)

// 3. التحويل في الـ ViewModel:
fun BankAccount.toUiState(): AccountDetailsUiState {
    return AccountDetailsUiState(
        isLoading = false,
        formattedBalance = CurrencyFormatter.format(balanceCents, currency),
        balanceColor = if (isOverdrawn) Color.Red else Color.Green,
        isDepositButtonEnabled = !isOverdrawn
    )
}
```

## Why it matters and how it works

UI state describes what to display now, while domain state describes application facts and rules. A ViewModel transforms domain/data streams into screen state; the repository remains responsible for the underlying source of truth.

## Worked example

Conceptual mapping: `Order(status = Pending, totalMinor = 1299)` is domain data; `CheckoutUiState(showSpinner = true, totalText = "EGP 12.99", canRetry = false)` is presentation. On server confirmation, repository updates order status; ViewModel emits a new UI state. The label is not persisted as canonical money.

## Trade-offs and decision criteria

A separate UI model costs mapping but prevents display details from contaminating domain. Very small screens may render a domain model directly if no distinct presentation contract exists. Do not persist every transient UI flag as though it were business truth.

## Failure modes

A ViewModel sets `isPaid = true` after an HTTP timeout because it saw a local click. The client has no confirmed outcome; render pending verification and reconcile. Another failure is storing locale-formatted amount in database and later parsing it for payment logic.

## Production perspective

An order details screen observes Room-backed order status and composes locale-specific text. After process death, it reloads business status from repository; selected accordion state may restore from saved UI state if worthwhile.

## Interview answer — short

Business or domain state represents persistent, core enterprise truth independent of screens, such as account balances or user roles. UI state is transient and screen-specific, defining what is visually rendered at any moment, including loading spinners, input validation errors, and selected tabs.

## Interview answer — structured

Distinguishing UI state from domain state prevents presentation concerns from corrupting enterprise business models.

Domain state represents the persistent, authoritative truth of the application. It includes user credentials, shopping cart contents, and transaction histories managed by repositories and databases, existing independently of whether any screen is actively visible.

In production, UI state is a transient, presentation-focused projection of that domain data combined with screen-specific UI conditions. It models what the user sees at a particular moment, encompassing loading indicators, accordion expansion states, selected tabs, and localized input error messages.
As for lifecycle and derivation, domain state survives navigation and process death, whereas UI state is owned by a ViewModel and scoped to a specific user journey, continuously derived from underlying domain streams and discarded when the screen finishes.


## Interview answer — deep senior

Under the hood, conflating UI state with domain state introduces major architectural bugs, memory leaks, and synchronization failures. Domain state is governed by business rules and backend invariants; it changes only when explicit business transactions occur, such as finalizing a purchase or receiving a WebSocket price update. It is typically modeled as immutable domain entities stored in local databases like Room or encrypted secure storage.
UI state, conversely, is ephemeral and dynamic. In Jetpack Compose, UI state must be modeled as a single, immutable data class or sealed hierarchy exposed via StateFlow. It contains presentation-only properties that have zero meaning to the enterprise domain—such as isSwipeRefreshing, searchQueryInputText, scaffoldSnackbarMessage, or isBiometricPromptVisible.
When designing reactive pipelines, senior engineers treat UI state as a derived projection. The ViewModel combines multiple domain repository flows alongside local UI event flows using operators like combine or map, producing a unified screen state. If the user navigates away, the UI state vanishes from memory, while the underlying domain state remains intact in the data layer.
Staff engineers maintain strict architectural hygiene: domain entities must never hold UI-specific primitives like Android string resource IDs or format strings, while UI state classes should flatten complex domain graphs into simple, primitive-backed display models that guarantee fast Compose recomposition without unnecessary object allocations. This separation ensures rock-solid state management across process recreation and deep-link navigation.

## How to answer in the interview

- **Why:** UI rendering and business authority differ.
- **How:** derive UiState from durable domain state.
- **Trade-off:** responsive UI versus extra mapping.
- **Failure case:** saveable success badge outlives truth.
- **Production solution:** reconcile backend and render current state.

## Deep-dive talking points

Contrast durable order status with a screen spinner, selected tab, and localized total. Discuss process death and server authority for payments.

## Follow-up questions

- **Interviewer:** "Can UI state exist without domain state?"
  **Answer:** "Yes. Purely transient UI states—like an accordion expansion toggle, a dialog visibility flag, or animation progress—are UI states that have zero backing domain state."

- **Interviewer:** "Where should the formatting of a date timestamp (Long to String) occur?"
  **Answer:** "In the Presentation layer (ViewModel or Presentation Mapper). Formatting depends on device locale and UI display rules, which have no place in the pure domain layer."

## Self-check rubric

Give two domain facts and two UI-only fields, then explain how a ViewModel derives UI state after recreation.

## References and reviewed-on date

- [Android state holders](https://developer.android.com/topic/architecture/ui-layer/stateholders) — screen UI state versus data.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — application data ownership.

Technically reviewed against primary documentation on 2026-10-13.
