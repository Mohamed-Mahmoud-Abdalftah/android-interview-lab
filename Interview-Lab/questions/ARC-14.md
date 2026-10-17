---
id: "ARC-14"
question: "Why should UI not call Retrofit or Room DAOs directly?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 159
editorial_status: "reviewed"
---

# ARC-14

## Original interview question

Why should UI not call Retrofit or Room DAOs directly?

## What the interviewer evaluates

Explain why direct UI-to-data-source coupling hurts consistency, lifecycle and testability.

## Concept and technical explanation

Allowing UI components (Composables, Activities, Fragments, or ViewModels) to directly invoke Retrofit network interfaces or Room DAOs violates the Single Responsibility Principle, breaks Separation of Concerns, and destroys architectural boundaries. Direct calls couple the presentation layer tightly to transport protocols (HTTP status codes, REST paths, DTO annotations) and local database schemas (SQLite tables, column names, foreign keys). Any backend API contract change or Room database migration shatters UI code across the application. Furthermore, bypassing the Repository layer eliminates centralized caching policies, prevents single-source-of-truth coordination, scatters background thread dispatching, and renders automated unit testing impossible without heavy network mocks and SQLite instances.

## Practical walkthrough (English)

Contrasting direct DAO/API calls with clean repository mediation:
```kotlin
// ❌ ANTI-PATTERN: ViewModel directly coupled to Retrofit and Room DAO
class BadProductViewModel(
    private val api: ProductRetrofitApi,
    private val dao: ProductRoomDao
) : ViewModel() {
    fun loadProducts() {
        viewModelScope.launch {
            val response = api.fetchProducts() // Couples UI to HTTP response wrappers!
            if (response.isSuccessful) {
                dao.insertAll(response.body()!!.map { it.toEntity() }) // UI manages DB cache manually!
            }
        }
    }
}

// ✅ CLEAN ARCHITECTURE: Repository mediates sources, UI observes pure domain models
class CleanProductViewModel(
    private val repository: ProductRepository
) : ViewModel() {
    val products: StateFlow<List<Product>> = repository.observeProducts()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    fun refresh() {
        viewModelScope.launch { repository.refreshProducts() }
    }
}
```

## Explanation in Arabic

لماذا يجب ألا تتصل طبقة واجهة المستخدم (UI Layer) بمكتبات Retrofit أو Room DAOs مباشرة؟

1. مخاطر الارتباط المباشر (Tight Coupling):
   - إذا كان الـ ViewModel أو الـ Composable يستدعي Retrofit أو Room مباشرة، فإنه يصبح مرتبطاً بشكل وثيق (Coupled) بتفاصيل الـ Networking وقواعد البيانات المحلية.
   - أي تعديل في الـ Backend API (مثل تغيير مسار Endpoint، أو إضافة Headers، أو تعديل شكل الـ JSON) يجبرك على تعديل كود الـ UI والـ ViewModel مباشرة، مما يكسر مبدأ Single Responsibility.

2. انهيار قابلية الاختبار (Destruction of Testability):
   - لا يمكنك كتابة Unit Test نظيف وسريع للـ ViewModel على الـ JVM دون استحضار أدوات Mocking معقدة للـ HTTP Client (مثل MockWebServer) أو SQLite In-Memory Database، مما يجعل الاختبارات بطيئة وهشة.

3. غياب استراتيجية الكاش والمصدر الوحيد للحقيقة (No Caching / Offline Support):
   - استدعاء الشبكة مباشرة يحرم التطبيق من وجود وسيط ينظم حفظ البيانات محلياً؛ فلن يعمل التطبيق دون اتصال بالإنترنت (No Offline-first).
   - الـ Repository هو الذي يوحد إدارة الـ Caching والـ Retries والـ Error Mapping بعيداً عن أعين الـ UI.

## Practical walkthrough

مقارنة بين استدعاء مباشر كارثي واستخدام الـ Repository Pattern:
```kotlin
// ❌ استدعاء مباشر كارثي: ViewModel يتصل بـ Retrofit مباشرة ويعالج تفاصيل HTTP:
class BadUserViewModel(private val api: RetrofitUserApi) : ViewModel() {
    fun loadUser() {
        viewModelScope.launch {
            val response = api.getUserProfile() // تسريب تفاصيل الشبكة إلى الـ UI!
            if (response.isSuccessful) {
                _uiState.value = response.body()!!.toUi()
            }
        }
    }
}

// ✅ كود سليم ومعزول: ViewModel يتصل بـ Repository وسيط يوفر بيانات نظيفة:
class GoodUserViewModel @Inject constructor(
    private val userRepository: UserRepository // عقد وسيط مجرد
) : ViewModel() {
    val uiState: StateFlow<UserUiState> = userRepository.observeUser()
        .map { UserUiState.Success(it) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), UserUiState.Loading)
}
```

## Why it matters and how it works

A repository provides a consistent app-data API and coordinates sources. UI state holders should consume data/domain APIs and map to UI state, not own transport or persistence mechanics. This reduces change propagation and contradictory data.

## Worked example

Conceptual comparison: bad `ProfileViewModel` calls `api.getUser()` and `dao.insert()` itself; better `ProfileRepository.observeProfile(id)` emits local truth and `refresh(id)` updates that source. ViewModel sets loading/refresh UI state and handles cancellation.

## Trade-offs and decision criteria

Direct access may be acceptable in a throwaway prototype but creates coupling once caching, retries or multiple screens appear. A repository is an abstraction with behavior; avoid a wrapper that simply renames DAO methods without policy or stable contract.

## Failure modes

A UI directly renders a fresh Retrofit response while another screen observes older Room data, violating SSOT. A screen-owned `viewModelScope` refresh also gets cancelled on navigation when a durable sync was required. Put consistency and durable scheduling in appropriate data/work layers.

## Production perspective

A profile feature uses a Room-backed repository with network refresh and clear error categories. UI can be rebuilt from local data after process death, and network transport changes do not alter Compose.

## Interview answer — short

Calling Retrofit or Room directly from the UI couples presentation logic to network protocols and SQLite schemas. It bypasses offline caching, prevents single-source-of-truth synchronization, and makes UI testing impossible without complex network mocks. Repositories abstract these details, exposing clean domain streams and handling caching transparently.

## Interview answer — structured

Allowing the UI layer to communicate directly with Retrofit or Room DAOs creates fatal architectural coupling.

The UI layer is designed to be a passive consumer focused purely on rendering state and dispatching user interactions. When a Composable or ViewModel calls network endpoints or database queries directly, it assumes responsibility for transport mechanics, HTTP headers, SQL queries, and table joins.

In production, this bypasses the single source of truth. The UI is forced to manually coordinate caching—deciding whether to write to the database or read from the network—leading to fragmented data states and duplicate network traffic across different screens.
As for maintainability and testing, direct coupling makes unit testing presentation logic nearly impossible without mocking network sockets and SQLite cursors, while any minor backend API modification shatters UI controllers across the entire app.


## Interview answer — deep senior

Under the hood, exposing network clients and database DAOs to the presentation layer destroys architectural boundaries and causes catastrophic lifecycle bugs. Retrofit calls return raw HTTP response wrappers and transport DTOs containing nullable attributes and server metadata. If an Activity or ViewModel directly parses these objects, network parsing exceptions occur directly on the main thread, while business validation logic becomes scattered across dozens of individual UI files.
Similarly, directly invoking Room DAOs from ViewModels couples presentation logic to the local database schema. When a database migration alters column names or normalizes relational tables, UI code breaks. Furthermore, if two independent ViewModels write to the DAO directly without a centralized repository mediator, optimistic concurrency conflicts and write-skew anomalies arise because there is no unified coordination of caching policies or transaction boundaries.
The Repository pattern provides a necessary abstraction layer. It encapsulates the coordination of remote network calls with local database writes, executes background thread dispatching on Dispatchers.IO, handles token re-authentication, and exposes clean, immutable domain models through Flow.
Staff engineers enforce this separation through strict dependency injection rules and modular Gradle boundaries. Feature modules implementing UI and ViewModels are given dependencies only on repository interfaces, completely lacking compile-time visibility of Retrofit interfaces or Room DAO annotations. This guarantees that infrastructure changes never impact the presentation layer.

## How to answer in the interview

- **Why:** rendering can repeat and data policy must be shared.
- **How:** route effects through owner and repository.
- **Trade-off:** separation versus call-chain overhead.
- **Failure case:** network call in composable body repeats.
- **Production solution:** observable state and adapter tests.

## Deep-dive talking points

Trace one profile refresh through UI and data; compare direct DTO rendering to Room-backed repository observation.

## Follow-up questions

- **Interviewer:** "Can a ViewModel call a Room DAO directly if the app has no network layer?"
  **Answer:** "Even in an offline-only app, a Repository is still recommended. It abstracts SQLite details, handles mapping from database entities to UI/Domain models, and manages transactions cleanly."

- **Interviewer:** "How do you enforce that the UI layer cannot import Retrofit?"
  **Answer:** "By splitting Gradle modules: `:feature:home` depends on `:core:domain` or `:core:data-api`, but has no dependency on `:core:network` or `com.squareup.retrofit2`."

## Self-check rubric

Explain two coupling risks, one SSOT failure, and a repository contract that fixes them.

## References and reviewed-on date

- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repositories and data sources.
- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) — UI/data boundaries.

Technically reviewed against primary documentation on 2026-10-13.
