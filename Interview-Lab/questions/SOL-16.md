---
id: "SOL-16"
question: "How do you identify cohesive responsibilities within a God Class?"
topic: "SOLID & Object-Oriented Design"
code: "SOL"
group: "B"
phase: 2
priority: "P1"
order: 187
editorial_status: "reviewed"
---

# SOL-16

## Original interview question

How do you identify cohesive responsibilities within a God Class?

## What the interviewer evaluates

Diagnose God Class responsibilities using change history, clients, data flow and safe extraction.

## Concept and technical explanation

Identifying cohesive responsibilities within a God Class involves analyzing cohesion metrics, state usage clusters, and distinct business stakeholders (actors) to deconstruct monolithic classes into single-responsibility components. In software architecture, a God Class typically exhibits a high Lack of Cohesion of Methods (LCOM), where disjoint subsets of methods operate on mutually exclusive member variables. By auditing field access graphs, identifying competing reasons to change, and grouping operations by their business domains (such as caching, network synchronization, UI presentation, and input validation), senior engineers isolate natural responsibility boundaries for extraction into dedicated UseCases and Repositories.

## Practical walkthrough (English)

Analyzing field clustering to decompose a God Class into cohesive components:
```kotlin
// BAD ANTI-PATTERN: God Class with high Lack of Cohesion of Methods (LCOM)
class GodUserProfileController {
    // Cluster 1 fields: Validation & Formatting
    private val emailRegex = Regex("^[A-Za-z0-9+_.-]+@(.+)\$")
    fun validateEmail(email: String) = email.matches(emailRegex)

    // Cluster 2 fields: Database Caching
    private val userDao: UserDao = getDatabase().userDao()
    suspend fun cacheUser(user: UserEntity) = userDao.insert(user)

    // Cluster 3 fields: HTTP Remote Networking
    private val api: UserApi = getRetrofit().create(UserApi::class.java)
    suspend fun fetchRemoteUser(id: String) = api.getUser(id)

    // Cluster 4 fields: UI Presentation State
    private val _uiState = MutableStateFlow<ProfileUiState>(ProfileUiState.Loading)
    val uiState = _uiState.asStateFlow()
}

// ARCHITECTURAL BEST PRACTICE: Cohesive, single-responsibility components
class UserInputValidator @Inject constructor() {
    fun isValidEmail(email: String): Boolean = email.isNotBlank() && email.contains("@")
}

class UserRepository @Inject constructor(
    private val api: UserApi,
    private val dao: UserDao
) {
    suspend fun getUser(id: String): Result<User> = runCatching {
        dao.getUser(id)?.toDomain() ?: api.getUser(id).toDomain().also { dao.insert(it.toEntity()) }
    }
}

class ProfileViewModel @Inject constructor(
    private val repository: UserRepository,
    private val validator: UserInputValidator
) : ViewModel() {
    // Pure UI presentation state machine
}
```

## Explanation in Arabic

كيف تحدد وتكتشف المسؤوليات المتماسكة (Cohesive Responsibilities) داخل كلاس متضخم (God Class)؟

1. ما هو الـ God Class في Android؟
   - كلاس ضخم (1,500 إلى 3,000 سطر) يسيطر على كل شيء؛ يقرأ الحساسات، ويطلب الشبكة، ويعدل قاعدة البيانات، وينسق الرسوم، ويتعامل مع الأذونات (مثل كلاس `OrderManager` أو `MainActivity`).

2. المنهجية العلمية لتحديد المسؤوليات المتماسكة داخل الكلاس:
   - **فحص استخدام المتغيرات المشتركة (LCOM - Lack of Cohesion of Methods)**:
     * انظر إلى خصائص الكلاس (Fields): ستجد مجموعة دوال (A, B, C) تستخدم فقط `LocationManager` و `gpsCoordinates`.
     * ومجموعة أخرى (D, E, F) تستخدم فقط `RetrofitOrderApi` و `authToken`.
     * ومجموعة ثالثة تستخدم فقط `Dialog` و `Toast`.
     * هذه المجموعات المنفصلة هي كلاسات جديدة تنادي عليك لاستخراجها فوراً!
   - **فحص أصحاب المصلحة (Stakeholders / Business Actors)**:
     * اسأل نفسك: من يطلب تعديل هذا الجزء؟ هل هو فريق الـ UI؟ أم فريق الـ Backend؟ أم فريق الأمان؟
   - **فحص التسميات (Naming Smells)**: الدوال التي تبدأ بـ `calculate...`, `validate...`, `format...` غالباً ما تكون وظائف Domain يجب فصلها عن وظائف التخزين `save...` و `fetch...`.

## Practical walkthrough

تحليل وتفكيك God Class إلى مكونات متماسكة:
```kotlin
// ❌ God Class يجمع حقولاً غير متجانسة إطلاقاً:
class MonolithicCartManager {
    // Cluster 1: موقع جغرافي لحساب التوصيل
    var userLat: Double = 0.0
    var userLng: Double = 0.0
    fun updateGpsLocation() { ... }

    // Cluster 2: حسابات الضرائب والخصومات (Domain Rules)
    fun applyDiscountCoupon(code: String) { ... }
    fun calculateVatTax(subtotal: Long): Long { ... }

    // Cluster 3: التخزين وقاعدة البيانات (Data Storage)
    fun persistCartToDatabase() { ... }
    fun syncWithBackendApi() { ... }
}

// ✅ التفكيك إلى كلاسات عالية التماسك (High Cohesion):
// 1. DeliveryLocationProvider (مسؤول عن الموقع فقط)
class DeliveryLocationProvider { ... }

// 2. CartPricingEngine (مسؤول عن حسابات الضرائب والخصومات في Domain)
class CartPricingEngine { ... }

// 3. CartRepository (مسؤول عن حفظ البيانات ومزامنة السيرفر في Data)
class CartRepository { ... }
```

## Why it matters and how it works

Cohesion is about related change pressure and invariants. A large class can be coherent; a small class can still mix unrelated reasons. Safe extraction requires understanding state, side effects and caller contracts.

## Worked example

Refactor plan for `CheckoutManager`: (1) test submit/timeout/duplicate tap; (2) move provider SDK mapping to adapter; (3) move eligibility into a policy component; (4) keep UI state transition in ViewModel; (5) move durable request tracking to repository. Measure changed-file locality afterward.

## Trade-offs and decision criteria

Incremental extraction temporarily leaves adapters and duplicate paths but lowers risk. A big-bang rewrite may be faster on paper yet miss hidden behavior. Avoid microscopic classes that split one invariant across too many owners.

## Failure modes

A team moves `calculateFee()` to `FeeUseCase` but leaves mutable cart state in God Class, so the new method still reaches back into shared fields. Pass explicit inputs and define ownership. Test concurrent/timeout behavior before changing flow.

## Production perspective

A commerce team uses production incident history to prioritize extracting payment SDK code from a 1,200-line coordinator. They monitor decline/timeout metrics during rollout and keep rollback available.

## Interview answer — short

We identify cohesive responsibilities within a God Class by analyzing its field-method access graph and identifying distinct business actors. A God Class reveals itself when disjoint groups of methods access only specific subsets of member variables without cross-interaction, exhibiting high Lack of Cohesion of Methods (LCOM). By clustering methods around their shared state—separating network APIs, database DAOs, input validation, and UI state—we delineate clean boundaries to extract into dedicated Repositories, UseCases, and ViewModels.

## Interview answer — structured

Deconstructing a God Class requires a systematic methodology rather than arbitrary file splitting.
A God Class arises when developers continually append new requirements to an existing file, gradually combining networking, storage, validation, and presentation.
Senior engineers use three complementary techniques to identify natural responsibility seams.
First, perform field-method cluster analysis. Diagram which methods access which member variables. In a God Class, you will discover distinct, disconnected islands of state: validation regexes used only by input checkers, database DAOs used only by persistence functions, and HTTP clients used only by network calls. These isolated clusters represent textbook candidates for extraction.
Second, identify business actors and change triggers. Ask: who requests modifications to this method? Marketing changes analytics events, backend architects alter API schemas, DBAs modify caching tables, and UX designers adjust screen layouts. Methods driven by different actors belong in different classes.
Third, extract components progressively along architectural boundaries: moving validation to pure utility classes, data persistence to Repositories, and business orchestration to UseCases, leaving the host class focused strictly on its primary responsibility.

## Interview answer — deep senior

Under the hood, cohesion can be mathematically formalized using the Lack of Cohesion of Methods (LCOM) metric suite (such as LCOM4).
In graph theory, LCOM4 constructs an undirected graph where nodes represent class methods, and edges connect methods that access at least one shared instance variable or invoke each other directly. In an ideal single-responsibility class, LCOM4 equals 1, indicating a single connected component where all methods collaborate on a cohesive state. In an Android God Activity or God ViewModel, LCOM4 frequently reaches 5 or higher, proving that the class is a composite artifact artificially grouping independent subgraphs.
Extracting these subgraphs into isolated classes directly impacts memory allocation and Garbage Collection behavior in the Android ART runtime. Monolithic God Classes hold long-lived references to multiple heavyweight resources simultaneously—SQLite database connections, OkHttpClient instances, Bitmaps, and View contexts. Because these references reside in the same object graph, their memory lifetimes are tied together, preventing generational Garbage Collection from reclaiming temporary buffers and driving up memory pressure.
By decomposing the God Class into fine-grained, scoped dependencies managed by Hilt or Dagger, memory lifecycles decouple. Transient objects are collected promptly in generation-zero heap allocations, reducing GC pause frequencies and eliminating hidden memory leaks during Android screen configuration changes.

## How to answer in the interview

- **Why:** Use change history and invariants.
- **How:** describe extraction order.
- **Trade-offs:** mention temporary migration cost.
- **Failure cases:** flag cyclic cosmetic split.
- **Production solutions:** close with behavior tests and change-locality evidence..

## Deep-dive talking points

Use change history, state-field map, call graph and characterization tests to find cohesive slices.

## Follow-up questions

- **Interviewer:** "What is LCOM (Lack of Cohesion of Methods)?"
  **Answer:** "A software metric that measures the disparity between methods and fields in a class. High LCOM indicates low cohesion, proving that a class is doing too many unrelated things and should be split."

- **Interviewer:** "How do God Classes negatively affect team velocity and Git workflows?"
  **Answer:** "Multiple developers working on different features simultaneously edit the same massive file, creating frequent and painful merge conflicts, broken builds, and duplicated regression testing."

## Self-check rubric

Identify three change actors and one shared invariant in a God Class; propose a first safe extraction.

## References and reviewed-on date

- [Robert C. Martin, SRP](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — reasons to change.
- [Android architecture guide](https://developer.android.com/topic/architecture) — separation of concerns.

Technically reviewed against primary documentation on 2026-10-13.
