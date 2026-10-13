---
id: "PAT-06"
question: "Where does Repository fit as an architectural/data-access pattern?"
topic: "Design Patterns"
code: "PAT"
group: "A"
phase: 2
priority: "P1"
order: 197
editorial_status: "reviewed"
---

# PAT-06

## Original interview question

Where does Repository fit as an architectural/data-access pattern?

## What the interviewer evaluates

Position Repository as data boundary, not a GoF catalog entry or a pure DAO alias.

## Explanation in Arabic

أين يقع نمط المستودع (Repository Pattern) كنمط معماري ونمط وصول للبيانات (Architectural / Data-Access Pattern)؟

1. موقع الـ Repository في البناء المعماري (Architectural Placement):
   - يقع الـ Repository عند **الحد الفاصل (Boundary) بين طبقة النطاق (Domain) وطبقة البيانات (Data)**.
   - في Clean Architecture:
     * **الواجهة (Interface)** تقع في قلب طبقة الـ Domain.
     * **التنفيذ الفعلي (Implementation)** يقع في طبقة الـ Data.

2. دوره كنمط وصول للبيانات (Data-Access Pattern):
   - يعمل كـ **وسيط مجرد (Mediator)** يتصرف وكأنه مجموعة كائنات محفوظة في الذاكرة (In-memory collection).
   - يخفي تفاصيل كيفية استرجاع البيانات ومصادرها (SQLite, Retrofit, Preferences, Cache).
   - يوحد منطق إدارة الكاش والـ Offline-first.

3. لماذا لا نضع الـ Repository في طبقة الـ Presentation أو ككلاس مستقل في UI؟
   - لأن وظيفته خدمة قواعد الأعمال، وليس الواجهات.
   - عزل الـ Repository يتيح إعادة استخدامه عبر شاشات متعددة، وفي Background Workers، ومع الإشعارات دون تكرار كود التخزين والشبكة.

## Practical walkthrough

تموضع الـ Repository في كود Clean Architecture عبر الطبقات:
```kotlin
// 1. في طبقة DOMAIN: العقد المجرد للبيانات:
interface UserRepository {
    fun observeUser(id: String): Flow<User>
    suspend fun refreshUser(id: String): Result<Unit>
}

// 2. في طبقة DATA: تنفيذ الـ Repository وإدارة مصادر البيانات والكاش (SSOT):
class UserRepositoryImpl @Inject constructor(
    private val localDao: UserDao,       // مصدر بيانات محلي
    private val remoteApi: UserApi       // مصدر بيانات خارجي
) : UserRepository {
    override fun observeUser(id: String): Flow<User> = localDao.getUser(id).map { it.toDomain() }
    override suspend fun refreshUser(id: String): Result<Unit> = runCatching {
        val networkDto = remoteApi.fetchUser(id)
        localDao.insert(networkDto.toEntity())
    }
}

// 3. في طبقة PRESENTATION: ViewModel يستهلك الـ Repository دون معرفة أي تفاصيل تخزين:
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() { ... }
```

## Why it matters and how it works

Repositories expose application data and centralize updates while abstracting data sources. They sit at a layer boundary and can contain data-centric business logic. Their value is consistent ownership, not merely a naming pattern.

## Worked example

Conceptual API: `observeOrders(): Flow<List<Order>>` reads Room; `refresh()` fetches and writes validated entities; `submit(requestId)` persists pending status and queries server outcome. UI observes the same local path. Room entity and Retrofit DTO stay internal.

## Trade-offs and decision criteria

A repository adds a boundary and testing seam; for tiny one-source features, a direct data-source wrapper may be enough but should still expose a stable app contract. Do not build one repository per method or hide unrelated workflows in one huge repository.

## Failure modes

One screen renders API DTOs while another reads Room entities, showing contradictory status. A repository should route both through a chosen source of truth. Another failure is treating a local `Paid` row as final server authorization.

## Production perspective

A delivery app uses a task repository to merge remote assignments into Room, preserve cached tasks offline, and expose freshness. Conflict rules and device tests cover reconnect.

## Interview answer — short

The Repository pattern sits at the boundary between Domain and Data layers. In Clean Architecture, its interface lives in Domain (defining what data the business requires) and its implementation lives in Data (coordinating Room, Retrofit, and caching). It abstracts data storage behind an in-memory collection facade.

## Interview answer — structured

The Repository pattern operates simultaneously as an architectural boundary and a specialized data-access design pattern.

1. **Architectural Placement (The Clean Boundary)**:
   - Sits squarely at the demarcation line between **Domain and Data layers**.
   - In adherence with the Dependency Inversion Principle, the **Repository Interface** resides in the Domain layer as an abstract business requirement.
   - The **Repository Implementation** (`RepositoryImpl`) resides in the Data layer, depending on the Domain interface and concrete DataSources (Room, Retrofit, Datastore).

2. **Data-Access Responsibilities (The Mediating Facade)**:
   - Mediates between the domain and multiple raw data sources, masquerading as an in-memory collection (`Flow<T>`, `save()`, `delete()`).
   - Implements the **Single Source of Truth (SSOT)**: managing offline-first persistence, cache invalidation, and background synchronization policies.
   - Maps raw technical DTOs and SQLite entities into clean Domain Entities before emitting them upward.

## Interview answer — deep senior

A frequent question is whether each database table or API endpoint requires its own Repository. The answer is no. Under Domain-Driven Design (DDD) principles, a Repository should be modeled around an **Aggregate Root**.

For example, in an e-commerce app, an `Order` aggregate root might involve `orders`, `order_items`, and `delivery_addresses` tables across SQLite, alongside two distinct REST APIs. A single `OrderRepository` orchestrates all these underlying tables and network endpoints, providing a unified `Order` entity to the domain. Creating a separate repository for each individual database table leaks database schema boundaries into business code.

## How to answer in the interview

- **Why:** Centralize data-source coordination and domain contracts.
- **How:** UI observes repository; repository maps Room/network and freshness.
- **Trade-off:** Keep a one-source repository small instead of adding forwarding layers.
- **Failure case:** ViewModel merges two sources or repository hides stale/unknown state.
- **Production solution:** Test cache updates and payment reconciliation through one boundary.

## Deep-dive talking points

Distinguish repository from DAO and UseCase; explain local SSOT versus server authority.

## Follow-up questions

- **Interviewer:** "What is an Aggregate Root in the context of Repositories?"
  **Answer:** "An entity that acts as the gateway to a cluster of associated objects (e.g. `Order` owns `OrderItem`). The Repository is created for the Aggregate Root, not for each internal child table."

- **Interviewer:** "Why shouldn't a ViewModel query a DataSource directly?"
  **Answer:** "Because DataSources represent raw individual I/O channels (one API or one DAO). The Repository provides caching, orchestration, error translation, and SSOT guarantees that DataSources lack."

## Self-check rubric

Give two responsibilities beyond DAO forwarding and explain why Repository is not a GoF entry.

## References and reviewed-on date

- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository responsibilities.
- [GoF pattern catalog](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) — original 23-pattern catalog.

Technically reviewed against primary documentation on 2026-10-13.
