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

UI calling Retrofit or Room directly tightly couples the presentation layer to network/database implementation details, destroys JVM unit testability, eliminates offline caching strategies, and duplicates error-handling logic across screens. A Repository must mediate to enforce SSOT.

## Interview answer — structured

Bypassing the data/domain layer to call Retrofit or Room DAOs directly from the UI layer is a critical architectural violation.

1. **Tight Coupling to Infrastructure Details**: The UI layer's sole concern is rendering state and capturing user intent. Calling Retrofit couples the UI to HTTP verbs, status codes, query parameters, and JSON parsing. Calling Room couples it to SQL tables, migrations, and database cursors. Any backend schema or database change directly breaks presentation code.

2. **Destruction of Unit Testability**: If a ViewModel interacts directly with Retrofit or Room, testing its presentation logic requires complex mock servers (MockWebServer) or SQLite fixtures. With a Repository abstraction, the ViewModel is tested via a lightweight Fake Repository in sub-second JVM tests.

3. **Loss of Caching and Offline Resilience**: A direct API call in the UI provides zero offline capability. The Repository pattern is where caching policies, SQLite write-through caching, and network retries live, presenting a cohesive Single Source of Truth to the UI.

## Interview answer — deep senior

Under the hood, direct data source calls also lead to **threading and main-safety violations**. While Room and Retrofit support suspend functions, direct invocation often leads developers to execute database transactions or large JSON deserializations directly in UI scopes without appropriate dispatcher switches.

Furthermore, direct calls create **duplicate business logic**. If Screen A and Screen B both query `UserApi.getProfile()`, both ViewModels must independently handle token refresh logic, HTTP 401 handling, DTO mapping, and error messages. Centralizing this within `UserRepository` guarantees that network resilience logic is written and tested once.

In enterprise codebases, we enforce this boundary via Gradle modularization and static analysis: the `:ui` module does not have a dependency on Retrofit, OkHttp, or Room libraries, making direct invocation impossible at compile time.

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
