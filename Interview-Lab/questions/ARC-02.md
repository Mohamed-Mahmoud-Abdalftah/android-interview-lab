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

## Concept and technical explanation

Google's recommended Android app architecture divides applications into three primary functional layers: Presentation, Domain, and Data. The Presentation layer contains UI elements (Composables, Activities, Fragments) and state holders (ViewModels) that render data and translate user input into unidirectional events. The Domain layer is an optional mediator encapsulating complex, reusable business logic and coordinating multi-repository interactions through single-purpose Use Cases; it operates purely on Kotlin primitives without Android SDK imports. The Data layer encapsulates business data access and caching policies, serving as the single source of truth for the application. It consists of repository interfaces and data source implementations (network clients, local databases, data stores) that expose reactive data streams and domain entities to higher architectural layers.

## Practical walkthrough (English)

Orchestrating the three architectural layers in a modern Android news feed:
```kotlin
// 1. Data Layer: Repository coordinates Room and Retrofit, exposes Domain models
class NewsRepositoryImpl(
    private val api: NewsApi,
    private val dao: NewsDao
) : NewsRepository {
    override fun getArticles(): Flow<List<Article>> =
        dao.observeArticles().map { entities -> entities.map { it.toDomain() } }

    override suspend fun syncArticles() {
        val remoteArticles = api.fetchTopHeadlines()
        dao.upsertArticles(remoteArticles.map { it.toEntity() })
    }
}

// 2. Domain Layer: Encapsulates filtering business rule
class GetBookmarkedArticlesUseCase(private val repository: NewsRepository) {
    operator fun invoke(): Flow<List<Article>> =
        repository.getArticles().map { list -> list.filter { it.isBookmarked } }
}

// 3. Presentation Layer: State holder binds domain streams to UI State
class BookmarksViewModel(
    private val getBookmarkedArticles: GetBookmarkedArticlesUseCase
) : ViewModel() {
    val uiState: StateFlow<BookmarksUiState> = getBookmarkedArticles()
        .map { articles -> BookmarksUiState.Success(articles.map { it.toUiModel() }) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = BookmarksUiState.Loading
        )
}
```

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

Presentation renders UI and translates user intents into state via ViewModels and Compose. Domain encapsulates isolated, reusable business logic through pure Kotlin UseCases. Data serves as the single source of truth, managing local databases, remote network clients, and caching policies behind clean repository interfaces.

## Interview answer — structured

Modern Android architecture partitions responsibilities into Presentation, Domain, and Data layers to ensure scalability and strict boundary isolation.

The Presentation layer consumes state and dispatches user actions. It contains Composables or Fragments observing immutable UI State exposed by ViewModels, ensuring the UI remains passive and declarative without business decision logic.

In production, the Domain layer is an optional mediator containing single-purpose UseCases. It operates entirely without Android framework imports, encapsulating enterprise business rules, mathematical validations, and multi-repository coordination that multiple ViewModels can share.
As for the Data layer, it acts as the application's single source of truth. Repositories coordinate remote REST or GraphQL APIs with local Room databases, resolving synchronization conflicts, offline caching, and data mapping. This ensures that upstream consumers interact strictly with stable domain entities rather than volatile network payloads or database entities.


## Interview answer — deep senior

Under the hood, dividing an Android codebase into Presentation, Domain, and Data creates clear boundaries for reactive data flow and compilation modularity. In Google's recommended architecture, data flows unidirectionally: user actions originate in Composables, travel up through ViewModel events to UseCases and Repositories, while updated state streams downward from the Data layer through Domain flows into UI State holders.
The Data layer hides storage mechanics. Whether data originates from in-memory caches, encrypted Room databases, or remote microservices, the repository exposes a unified stream of domain entities. It handles offline-first policies, optimistic writes, and network retry backoffs so upper layers remain oblivious to transport details.
The Domain layer exists specifically to prevent logic duplication. When business algorithms—such as calculating tax rebates or enforcing credit card fraud rules—are needed across both a mobile checkout screen and a background sync worker, extracting that logic into a UseCase guarantees consistency and instant JVM testing.
Staff engineers avoid dogmatic application of all three layers across every screen. The Android team explicitly considers the Domain layer optional; when a feature merely reads and renders data without transformations, routing through a pass-through UseCase that just delegates to a repository method introduces pointless boilerplate and navigation fatigue. In mature codebases, teams enforce modular Gradle boundaries where core domain has zero dependencies on database or network modules, preserving structural integrity while allowing pragmatic direct repository access for simple screens.

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
