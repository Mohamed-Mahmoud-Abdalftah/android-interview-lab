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

Single Source of Truth (SSOT) means every piece of data has a single owner that acts as the authoritative source. In Android, the local database (Room) is typically the SSOT: network responses write directly to Room, and the UI exclusively observes Room flows, preventing data inconsistency and providing offline support.

## Interview answer — structured

Single Source of Truth (SSOT) is an architectural discipline ensuring that every piece of state has exactly one authoritative owner responsible for its storage, mutation, and distribution.

In modern Android architectures, we implement SSOT via the **Offline-First Reactive Repository pattern**.

First, an Authoritative Storage is the local database (Room) serves as the definitive SSOT for app data. Next, an Unidirectional Observation is the UI layer and ViewModels observe data strictly through reactive streams (`Flow<T>`) emitted by the local database DAO. The UI never queries the network directly.
Finally, with Write-Through Ingestion, when network requests complete, the repository does not return network models to the UI. Instead, it writes the payload directly into Room inside a database transaction. Room's internal invalidation tracker automatically triggers a new emission on the active Flow, notifying all listening ViewModels.

This eliminates state desynchronization: if five different screens or background workers observe the same user profile, modifying that profile in one place instantly updates all five screens automatically.


## Interview answer — deep senior

Contrast this with the flawed **Dual-Source Anti-Pattern**: a screen fetches data from Retrofit, displays it, and separately writes a copy to SharedPreferences or Room. If the network request succeeds but database persistence fails, or if an in-memory cache differs from disk, the user encounters jarring contradictions—such as navigating back and seeing an outdated item count.

SSOT applies to the Presentation layer as well. Inside the ViewModel, a single `MutableStateFlow<ScreenUiState>` acts as the SSOT for the entire screen. Mutating UI state requires calling `_uiState.update { ... }`, preventing multiple independent LiveData streams from racing each other.

In testing, SSOT drastically simplifies verification: repository tests simply verify that executing a network sync populates the local Fake DAO, and UI tests verify reactions to simulated DAO emissions.


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
