---
id: "FLO-28"
question: "A flow combines cached Room data with remote refresh. Who is source of truth?"
topic: "Flow, StateFlow, SharedFlow & Channels"
code: "FLO"
group: "C"
phase: 1
priority: "P1"
order: 141
editorial_status: "reviewed"
---

# FLO-28

## Original interview question

A flow combines cached Room data with remote refresh. Who is source of truth?

## What the interviewer evaluates

Design offline-first cache plus remote refresh with one local source of truth.

## Concept and technical explanation

In modern Android architecture and offline-first system design, the local database (such as Room) must serve as the absolute Single Source of Truth (SSOT), while the remote network API acts solely as a data upstream source that mutates the SSOT.
Under this architectural contract, the UI layer never observes network responses directly. Instead, the UI layer exclusively observes reactive Flow streams emitted by Room DAOs. When the application requests fresh data from a remote REST or GraphQL endpoint, the repository fetches the remote payload, maps network DTOs to local database entities, and writes them into Room.
Because Room SQLite queries are observable via Kotlin Flow, any database insertion, update, or deletion automatically triggers a fresh query evaluation, emitting the updated dataset downstream to the UI. This architectural decoupling guarantees offline resilience, eliminates data synchronization inconsistencies, and ensures the UI always renders a consistent, verified state even during transient network drops or server timeouts.

## Practical walkthrough (English)

Architecting an offline-first data stream with Room as the Single Source of Truth:
```kotlin
class NewsRepository(
    private val newsDao: NewsDao,
    private val newsApi: NewsApiService
) {
    // 1. UI observes Room database as the Single Source of Truth:
    fun observeArticles(): Flow<List<Article>> = newsDao.getArticlesFlow()

    // 2. Network refresh writes strictly to the database, never directly to UI:
    suspend fun refreshArticles(): Result<Unit> = runCatching {
        val remoteDtos = newsApi.fetchTopHeadlines()
        val entities = remoteDtos.map { it.toEntity() }
        newsDao.upsertArticles(entities) // Room automatically notifies observeArticles()!
    }
}

// In ViewModel:
class NewsViewModel(private val repository: NewsRepository) : ViewModel() {
    val articles: StateFlow<List<Article>> = repository.observeArticles()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun refresh() {
        viewModelScope.launch {
            repository.refreshArticles().onFailure { error ->
                _errorEvents.emit(error.message ?: "Sync failed")
            }
        }
    }
}
```

## Explanation in Arabic

دمج بيانات Room المحلية المخبأة مع التحديث من السيرفر البعيد وسؤال 'من هو المصدر الوحيد للحقيقة (Single Source of Truth)' هو جوهر الـ **Offline-First Architecture**:

1. من هو المصدر الوحيد للحقيقة (Single Source of Truth - SSOT)؟
   - **قاعدة البيانات المحلية (Room Database) هي المصدر الوحيد للحقيقة دائماً! (Local DB is the SSOT).**
   - واجهة المستخدم (UI) **لا تستمع إلى الـ Network إطلاقاً**؛ الـ UI يستمع حصرياً إلى الـ Flow القادم من قاعدة بيانات Room!

2. كيف تتدفق البيانات بنظافة (The Reactive Data Flow)؟
   - 1. الـ UI يطلب البيانات من الـ Repository ويستمع لـ `roomDao.observeItems()`.
   - 2. الـ UI يعرض فوراً البيانات المخزنة محلياً في Room بدون أي تأخير (Instant Offline Loading).
   - 3. في نفس الوقت، الـ Repository يطلق طلباً في الخلفية لجلب أحدث البيانات من السيرفر (`api.fetchItems()`).
   - 4. عندما ينجح طلب السيرفر، الـ Repository يقوم بحفظ وتحديث البيانات في **Room Database** (`roomDao.insertAll(newItems)`).
   - 5. بمجرد تحديث Room، تقوم الـ Database تلقائياً بإصدار (emit) القائمة الجديدة للـ UI عبر الـ Flow!

3. الفوائد الهائلة:
   - دعم كامل للـ Offline Mode بنسبة 100%.
   - تجنب أي تعارض في البيانات أو تذبذب في واجهة المستخدم.

## Practical walkthrough

تنفيذ النمط في الـ Repository:
```kotlin
class ArticleRepository(
    private val articleDao: ArticleDao,
    private val articleApi: ArticleApi,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    // 1. الواجهة تستمع حصرياً لـ Room DB:
    fun observeArticles(): Flow<List<Article>> =
        articleDao.getArticles().map { entities -> entities.map { it.toDomain() } }

    // 2. دالة التحديث تحدث Room ولا ترجع بيانات مباشرة للـ UI:
    suspend fun refreshArticles() = withContext(ioDispatcher) {
        try {
            val remoteArticles = articleApi.fetchArticles()
            articleDao.insertAll(remoteArticles.map { it.toEntity() }) // Room تحدث الـ Flow تلقائياً!
        } catch (e: Exception) {
            // لو الشبكة مقطوعة، لا نفشل؛ البيانات المحلية تظل معروضة بسلاسة
            if (e is CancellationException) throw e
            Log.e("Repo", "Failed to refresh remote articles", e)
        }
    }
}
```

## Why it matters and how it works

Expose `Flow<List<Entity>>` from DAO and a separate suspend refresh/sync operation. The network response is validated and committed transactionally before UI observes it. Offline writes need queued operations and conflict resolution. Stale state should carry freshness metadata, not silently masquerade as current.

## Worked example

Conceptual Android repository; DAO and API are app-owned types. Room transaction is required around related table updates.

```kotlin
import kotlinx.coroutines.flow.Flow

class FeedRepository(private val dao: FeedDao, private val api: FeedApi) {
    val items: Flow<List<FeedItem>> = dao.observeItems()
    suspend fun refresh() {
        val remote = api.fetchItems()
        dao.replaceAllTransactionally(remote)
    }
}
```

## Trade-offs and decision criteria

Local source gives immediate offline rendering and a single UI path, but may be stale. Remote-only rendering can show fresh data sooner but complicates consistency/offline behavior. Define TTL, invalidation, conflicts and errors; never overwrite pending local edits blindly.

## Failure modes

Combining cached and remote lists without a merge rule can duplicate or revert items. A network timeout after a server write leaves uncertain status. If refresh replaces Room in multiple non-transactional steps, UI can observe an inconsistent partial snapshot.

## Production perspective

A messaging inbox observes Room and runs a worker to fetch updates. Rows have server IDs and versions; transaction applies a consistent batch. UI marks stale/offline state, while queued outgoing messages have stable operation IDs and reconciliation.

## Interview answer — short

The local database (Room) is the absolute Single Source of Truth. The UI observes database Flow queries exclusively; the network layer simply fetches remote data and writes it to Room, which automatically emits updated snapshots to the UI while ensuring full offline functionality.

## Interview answer — structured

Offline-first applications mandate a strict Single Source of Truth to prevent synchronization conflicts.

Room is the sole source of truth. Exposing direct network streams to the UI creates fragmented state where offline access is broken and network failures wipe out previously rendered data.

In production, the repository orchestrates this boundary cleanly. The UI subscribes to a reactive Flow emitted by the Room DAO. When a network sync executes, the repository parses the network response, converts DTOs to entities, and persists them into the database using upsert operations.
As for reactive synchronization, Room invalidation trackers detect SQLite table mutations and automatically re-evaluate the query, pushing the updated list downstream through the Flow. If the network call fails, the UI continues displaying cached database records uninterrupted, handling errors via non-intrusive notification events.


## Interview answer — deep senior

Under the hood, Room generates an observable Flow by registering an InvalidationTracker on the queried SQLite tables. When repository write operations invoke insert, update, or upsert, SQLite triggers notify Room's tracker. The tracker flags table modifications and notifies the active FlowCollector, re-querying SQLite on background database threads and emitting fresh entity snapshots downstream.
This architecture establishes clean separation of concerns. The network layer is completely decoupled from UI rendering cycles. Network latency, retries, and schema mappings happen strictly in background execution pipelines that terminate at the SQLite database boundary.
A critical senior consideration is transactional consistency and data pagination. When refreshing lists with relationships or nested items, repository writes must execute within a database transaction (@Transaction). This ensures that intermediate or partial updates never leak into the observable Flow, preventing UI rendering flickering or invalid relationship states.
Furthermore, if network pagination is required, pairing Room with the Jetpack Paging 3 RemoteMediator enforces this exact pattern: RemoteMediator fetches pages from the network and saves them directly to Room, while PagingSource streams cached records from SQLite to the UI.
Staff engineers enforce this offline-first contract across all enterprise apps: the UI observes local database storage exclusively, treating network endpoints as asynchronous background synchronizers.

## How to answer in the interview

- **Why:** two read paths create inconsistent UI.
- **How:** refresh remote into Room, then observe Room Flow.
- **Trade-off:** stale cache needs freshness and conflict policy.
- **Failure case:** direct remote emission fights cached state.
- **Production solution:** offline/reconnect and transaction tests.

## Deep-dive talking points

Draw network-to-Room-to-UI flow; distinguish local display truth from server authority and pending writes.

## Follow-up questions

- **Interviewer:** "How does the UI know if the network refresh failed?"
  **Answer:** "Expose a separate UI state or status stream for the refresh operation (e.g., `isRefreshing: Boolean` and `refreshError: String?`) in the ViewModel, keeping data state and sync status decoupled."

- **Interviewer:** "What if the remote response has 50,000 items? Does Room re-emit the whole list?"
  **Answer:** "For massive datasets, pair Room with the Paging 3 library (`PagingSource`). Paging 3 queries Room incrementally in chunks (e.g., 20 items per page), keeping memory and UI rendering fast."

- **Interviewer:** "Why shouldn't the network call emit directly to a `combine` operator with Room?"
  **Answer:** "Emitting directly from both network and Room creates two competing sources of truth, causing UI state jitter, duplicate items, and race conditions where a fast network call is overwritten by a slower disk read."

## Self-check rubric

Can I name one UI source, transact updates, expose staleness and resolve conflicts?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — local source of truth and sync.
- [Android Flow guide](https://developer.android.com/kotlin/flow) — DAO stream use.

Technically reviewed against primary documentation on 2026-10-13.
