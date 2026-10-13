---
id: "ARC-02"
question: "Explain Presentation, Domain, and Data layers."
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 147
editorial_status: "reviewed"
---

# ARC-02

## Original interview question

Explain Presentation, Domain, and Data layers.

## What the interviewer evaluates

Assign responsibilities to UI, optional domain, and data without confusing policy with rendering.

## Explanation in Arabic

شرح طبقات Clean Architecture الثلاث: العرض (Presentation)، النطاق (Domain)، والبيانات (Data):

1. طبقة النطاق (Domain Layer - The Core):
   - هي قلب التطبيق والطبقة الأكثر استقراراً؛ مكتوبة بلغة **Kotlin نقية 100%** بدون أي اعتمادية على Android SDK أو Retrofit أو Room.
   - تحتوي على: **Entities** (كائنات الأعمال الحقيقية)، **UseCases / Interactors** (منطق العمليات والقرارات الحسابية وقواعد التحقق)، و **Repository Interfaces** (العقود المجردة لجلب وحفظ البيانات دون معرفة كيفية التنفيذ).

2. طبقة البيانات (Data Layer):
   - مسؤولة عن إدارة وتنسيق مصادر البيانات المتعددة (Network, Local Database, Datastore/Preferences, In-Memory Caches).
   - تحتوي على: **DataSources** (Retrofit API Service, Room DAO)، **DTOs & Entities** (كائنات السيرفر وقاعدة البيانات)، و **Repository Implementations** التي تنفذ الواجهات المعرفة في طبقة النطاق وتقوم بـ Mapping للبيانات إلى Domain Entities.

3. طبقة العرض (Presentation / UI Layer):
   - مسؤولة عن كيفية تقديم البيانات للمستخدم والتقاط تفاعلاته.
   - تحتوي على: **UI Composables / Activities / Fragments**، و **ViewModels** التي تستدعي الـ UseCases أو Repositories وتحول النتائج إلى تدفق حالة موحد `StateFlow<UiState>`، وتلتقط الأحداث (`UiEvent`).

## Practical walkthrough

توزيع كود شاشة سلة المشتريات عبر الطبقات الثلاث:
```kotlin
// 1. DOMAIN LAYER (Pure Kotlin - No Frameworks):
data class CartItem(val productId: String, val quantity: Int, val unitPrice: Long)
interface CartRepository {
    fun observeCart(): Flow<List<CartItem>>
    suspend fun updateQuantity(productId: String, quantity: Int)
}
class CalculateCartTotalUseCase {
    operator fun invoke(items: List<CartItem>): Long = items.sumOf { it.quantity * it.unitPrice }
}

// 2. DATA LAYER (Implements Domain contracts, manages SQLite & Network):
class CartRepositoryImpl(
    private val cartDao: CartDao,
    private val api: CartApi
) : CartRepository {
    override fun observeCart(): Flow<List<CartItem>> = cartDao.getCartEntities().map { it.toDomain() }
    override suspend fun updateQuantity(productId: String, quantity: Int) {
        cartDao.update(productId, quantity)
        api.syncCart(productId, quantity)
    }
}

// 3. PRESENTATION LAYER (Translates domain state into observable UI):
@HiltViewModel
class CartViewModel @Inject constructor(
    private val repository: CartRepository,
    private val calculateTotal: CalculateCartTotalUseCase
) : ViewModel() {
    val uiState: StateFlow<CartUiState> = repository.observeCart().map {
        CartUiState.Success(items = it, total = calculateTotal(it))
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), CartUiState.Loading)
}
```

## Why it matters and how it works

Android guidance recommends a UI layer and data layer, with a domain layer when reuse or complexity calls for it. UI state holders produce screen state and delegate business operations. Data repositories coordinate data sources, own consistency decisions, and expose app data. Domain use cases can combine or transform repository outputs without adopting UI/framework types.

## Worked example

Conceptual flow: `LoginScreen` emits `Submit(credentials)` to `LoginViewModel`; ViewModel invokes `SignInUseCase` if the workflow is shared; use case calls `AuthRepository`; repository maps Retrofit response into a domain session and persists it. ViewModel maps domain outcome to `LoginUiState`. No layer promises server trust by itself.

## Trade-offs and decision criteria

A separate domain layer adds types, mapping, and navigation overhead. Keep a simple one-screen feature in UI/data if no reusable policy exists. Put rules at the lowest layer that owns them; avoid “use case” wrappers that merely delegate one method with no value.

## Failure modes

If Presentation receives a raw `HttpException`, it may branch on transport status and become coupled to Retrofit. If Domain imports `android.app.Activity`, its tests and reuse suffer. Map at boundaries and keep lifecycle-specific work in UI.

## Production perspective

An offline account screen observes repository data backed by Room; domain computes account eligibility reused by checkout and settings; ViewModels render different states. Network failure is reported without replacing valid cached data with a false empty screen.

## Interview answer — short

Presentation displays UI and translates user gestures into state streams via ViewModels. Domain contains pure business rules, entities, use cases, and repository interfaces without Android framework dependencies. Data implements domain repository interfaces, coordinating network APIs and local databases via mappers.

## Interview answer — structured

Modern Android Clean Architecture partitions responsibilities into three distinct architectural layers:

1. **Domain Layer (The Business Core)**: Represents the innermost layer and contains pure business logic. It has zero dependencies on Android frameworks, network libraries, or databases. It contains:
   - **Entities**: Business models encapsulating core data structures and invariant validation.
   - **Use Cases (Interactors)**: Single-purpose orchestrators executing specific business scenarios (e.g. `CalculateCartTotalUseCase`).
   - **Repository Interfaces**: Abstract contracts specifying what data operations the business requires, completely divorced from storage mechanisms.

2. **Data Layer (The Source Coordinators)**: Implements domain repository interfaces. It manages raw data sources (Retrofit REST APIs, Room SQLite DAOs, SharedPreferences/DataStore), handles caching strategies, and maps external DTOs into domain entities.

3. **Presentation Layer (The UI)**: Consists of ViewModels and Composable screens. The ViewModel calls Use Cases, reacts to state updates, and projects data into immutable `StateFlow<UiState>` streams, while capturing user UI events.

## Interview answer — deep senior

A critical design aspect of this division is the **Inversion of Control (IoC)** achieved through the Dependency Inversion Principle. Because the Domain layer defines the `Repository` interface and the Data layer implements it, compile-time source code dependencies point inward (`Data -> Domain` and `UI -> Domain`), while runtime execution flows outward.

This division maximizes testability. Because the Domain layer is pure Kotlin without Android dependencies, its entire test suite runs as lightning-fast JVM unit tests executing in milliseconds without Robolectric or emulator bootstrapping.

In enterprise Android modularization, these layers are often represented as separate Gradle modules: `:feature:cart:ui`, `:feature:cart:domain`, and `:feature:cart:data`, enforcing boundary discipline at the compiler level.

## How to answer in the interview

- **Why:** layers assign decision ownership.
- **How:** trace event through UI, policy and adapters.
- **Trade-off:** isolation versus mapping cost.
- **Failure case:** DTO leaks directly into screen.
- **Production solution:** contract tests per boundary.

## Deep-dive talking points

Compare a screen event, reusable rule, and repository refresh. Identify where locale formatting, HTTP mapping, conflict resolution, and lifecycle state belong; test each boundary separately.

## Follow-up questions

- **Interviewer:** "Can the Presentation layer bypass Domain and call Data directly?"
  **Answer:** "In simpler feature screens with no complex business rules (like simple CRUD lists), Google allows ViewModels to consume Repositories directly. However, in core business flows, bypassing Domain couples the UI to data concerns and bypasses business validations."

- **Interviewer:** "Why shouldn't the Domain layer import Android `Context`?"
  **Answer:** "Importing `Context` couples pure business rules to Android framework lifecycles and platform APIs, destroying JVM testability and making cross-platform migration (e.g. Kotlin Multiplatform) impossible."

## Self-check rubric

Can you assign a ViewModel, use case, repository, DTO, and Room entity without mixing responsibilities? Explain one business rule and one rendering rule.

## References and reviewed-on date

- [Android architecture guide](https://developer.android.com/topic/architecture) — layer responsibilities.
- [Android domain layer](https://developer.android.com/topic/architecture/domain-layer) — optional domain use cases.

Technically reviewed against primary documentation on 2026-10-13.
