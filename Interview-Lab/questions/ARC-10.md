---
id: "ARC-10"
question: "What is Single Source of Truth (SSOT)?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 155
editorial_status: "reviewed"
---

# ARC-10

## Original interview question

What is Single Source of Truth (SSOT)?

## What the interviewer evaluates

Define one authoritative owner per data type and distinguish local cache from server authority.

## Concept and technical explanation

Single Source of Truth (SSOT) is an architectural pattern dictating that a specific piece of application data has exactly one authoritative owner responsible for its storage, mutation, and distribution. In Android, the Data layer—specifically local persistent storage such as a Room database or an authoritative in-memory StateFlow repository—acts as the SSOT. When remote network payloads arrive from Retrofit or WebSocket streams, they are written directly to local storage rather than dispatched to the UI. The UI observes database tables reactively via Flow. This guarantees consistent offline-first data, prevents conflicting states between concurrent screens, and simplifies application recovery after process death.

## Practical walkthrough (English)

Implementing an offline-first Single Source of Truth with Room and Retrofit:
```kotlin
class OfflineFirstUserRepository(
    private val userDao: UserDao,
    private val userApi: UserApi,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) : UserRepository {
    // 1. SSOT: Room database is the sole data stream exposed to the application
    override fun observeUserProfile(userId: String): Flow<UserProfile> =
        userDao.observeUser(userId).map { it.toDomain() }

    // 2. Network mutations write directly into SSOT, never bypassing it
    override suspend fun refreshUserProfile(userId: String): Result<Unit> = withContext(ioDispatcher) {
        runCatching {
            val remoteUserDto = userApi.fetchUser(userId)
            userDao.upsertUser(remoteUserDto.toEntity()) // DB update automatically emits to downstream Flow
        }
    }
}
```

## Explanation in Arabic

ما هو مبدأ المصدر الوحيد للحقيقة (Single Source of Truth - SSOT) وكيف نطبقه في أندرويد؟

1. تعريف مبدأ الـ SSOT:
   - ينص المبدأ على أن **كل معلومة أو بيان في التطبيق يجب أن يمتلك مالكاً ومصدراً وحيداً مسؤولاً عن حفظه وتعديله ونشره**.
   - لا يجوز أبداً الاحتفاظ بنسخ متعددة قابلة للتعديل من نفس البيانات في أماكن متفرقة (مثل وجود نسخة في ViewModel ونسخة في Activity ونسخة في قاعدة البيانات).

2. كيف نطبقه عملياً في Android (Offline-First Pattern)؟
   - **قاعدة البيانات المحلية (Room) هي الـ SSOT لبيانات التطبيق**:
   - الـ UI يراقب فقط قاعدة البيانات المحلية عبر `Flow<List<Item>>`.
   - عندما يطلب التطبيق بيانات من السيرفر عبر Network API:
     * لا يتم إرسال استجابة الشبكة مباشرة إلى الشاشة!
     * يتم حفظ استجابة الشبكة داخل قاعدة بيانات Room أولاً.
     * تقوم Room تلقائياً بإطلاق انبعاث (Emit) جديد للبيانات المحدثة إلى الشاشة.

3. الفوائد الحقيقية للـ SSOT:
   - **منع تضارب البيانات (No Inconsistencies)**: مستحيل أن تظهر الشاشة بيانات تختلف عن البيانات المحفوظة.
   - **دعم Offline كامل تلقائياً**: التطبيق يعرض البيانات فوراً من الـ DB حتى لو انقطع الإنترنت، ثم يحدثها بصمت عند عودته.

## Practical walkthrough

تطبيق نمط Offline-First بجعل Room هي المصدر الوحيد للحقيقة (SSOT):
```kotlin
class UserRepositoryImpl(
    private val userDao: UserDao,
    private val userApi: UserApi
) : UserRepository {

    // 1. القراءة تتدفق دائماً وحصرياً من الـ SSOT (قاعدة بيانات Room):
    override fun observeUserProfile(userId: String): Flow<User> {
        return userDao.observeUser(userId)
            .map { it.toDomain() }
    }

    // 2. طلب الشبكة يحدث الـ SSOT فقط، والـ SSOT هي التي تخطر الواجهة تلقائياً:
    override suspend fun refreshUserProfile(userId: String): Result<Unit> = runCatching {
        val remoteDto = userApi.fetchUser(userId)
        // كتابة البيانات في Room هي الخطوة الوحيدة؛ انبعاث الـ Flow سيحدث تلقائياً:
        userDao.insertUser(remoteDto.toEntity())
    }
}
```

## Why it matters and how it works

A single source of truth prevents conflicting copies and creates a predictable update path. Android offline-first guidance often uses a local data source as the observable app source, with network synchronization feeding it. Server-authoritative business facts still require reconciliation.

## Worked example

Conceptual flow: `Room.observeOrders()` feeds the repository Flow and UI; `refreshOrders()` fetches remote records and writes them transactionally to Room; UI never renders the raw Retrofit response directly. For an uncertain payment, repository requests server status before promoting local `Pending` to `Paid`.

## Trade-offs and decision criteria

A local SSOT improves offline UX and consistent observation but adds synchronization and stale-data policy. Direct network rendering is simpler for a tiny online-only screen but makes cache and recreation behavior less coherent. Choose per data type.

## Failure modes

A screen renders fresh network data while another observes an older Room row, so users see contradictory order status. Route successful refresh through the same source and version/conflict rules. Never treat a local cache as authority for authorization.

## Production perspective

An offline news app uses Room as SSOT for articles and tracks `lastSyncedAt`; a wallet app may use Room as display cache but always confirms transfers on the server. Telemetry distinguishes stale data from refresh errors.

## Interview answer — short

Single Source of Truth establishes that a single, authoritative component owns and mutates a piece of state. In Android, local storage like Room acts as the SSOT. Network responses update the database, and the UI reacts purely to database flows, ensuring offline consistency and preventing data discrepancies.

## Interview answer — structured

Single Source of Truth guarantees data consistency across multi-screen Android applications by establishing one authoritative owner for each data entity.

The local database—typically Room—functions as the SSOT within the data layer. Instead of the UI observing both network responses and cached models, all read operations observe continuous Flow streams emitted by the database.

In production, write operations follow an offline-first pipeline. When user actions trigger mutations or background workers fetch remote data from Retrofit, the repository inserts the new records directly into Room. The database then automatically notifies active UI collectors through reactive queries.
As for system reliability, SSOT eliminates race conditions where two screens display conflicting account balances, ensures full offline functionality without special UI branching, and simplifies testing by reducing state validation to inspecting the persistent database store.


## Interview answer — deep senior

Under the hood, Single Source of Truth transforms the data layer from an imperative request-response bridge into an authoritative reactive store. In flawed architectures, ViewModels often maintain their own in-memory caches or combine network payloads with database records inside presentation coroutines. When a user updates their profile name on one screen, sibling screens or background sync tasks continue displaying stale information because each component references disparate copies of the data.
Enforcing SSOT centralizes data ownership inside a repository backed by a persistent relational database like Room or an authoritative StateFlow in memory. The repository exposes read-only reactive streams using Flow. Upstream consumers, whether ViewModels or background workers, cannot mutate the data directly; they dispatch write requests to the repository, which validates the payload, performs optimistic or pessimistic database writes, and handles backend synchronization.
Because Room's query pipeline observes SQLite table updates via InvalidationTracker, writing to the database triggers automatic recalculation and emission across every active collector in the application simultaneously.
Staff engineers ensure that SSOT is not violated by caching network DTOs in transient ViewModel variables. They also design conflict resolution strategies: when offline modifications conflict with remote server states, the repository reconciles timestamps and operational transforms before committing to the SSOT, guaranteeing enterprise-grade data integrity across device restarts.

## How to answer in the interview

- **Why:** conflicting copies create stale UI.
- **How:** name authority and derive projections.
- **Trade-off:** offline responsiveness versus reconciliation.
- **Failure case:** two mutable caches disagree.
- **Production solution:** single observable path with conflict policy.

## Deep-dive talking points

Draw Room-backed observation plus network refresh. Specify stale data, conflict, atomic writes, and server-authoritative payment reconciliation.

## Follow-up questions

- **Interviewer:** "Can an in-memory cache serve as an SSOT?"
  **Answer:** "Yes, for volatile session data that must not persist across app process death (like an active in-memory shopping cart or socket stream), a thread-safe in-memory cache (like `MutableStateFlow`) acts as the SSOT."

- **Interviewer:** "How does Room notify observers when data changes in the table?"
  **Answer:** "Room installs an internal SQLite `InvalidationTracker` that hooks into database table updates. When a write occurs on an observed table, it triggers a query re-evaluation and emits the updated result on the Flow."

## Self-check rubric

Identify a source of truth for an offline feed and for payment confirmation; describe one conflicting-copy failure and recovery path.

## References and reviewed-on date

- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository and source-of-truth responsibilities.
- [Android offline-first guide](https://developer.android.com/topic/architecture/data-layer/offline-first) — local source of truth.

Technically reviewed against primary documentation on 2026-10-13.
