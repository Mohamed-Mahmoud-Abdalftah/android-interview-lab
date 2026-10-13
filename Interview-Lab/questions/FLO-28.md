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

The local database (Room) is the Single Source of Truth (SSOT). The UI exclusively observes the Flow emitted by Room. Remote network calls write fresh data into Room, and Room automatically emits the updated data to the UI, guaranteeing seamless offline-first operation.

## Interview answer — structured

In an offline-first Android architecture, the local database (Room) is strictly the **Single Source of Truth (SSOT)**.

The architecture follows a unidirectional reactive pipeline:

1. **UI Observes Room:** The UI layer never observes raw network responses directly; it exclusively collects a Flow emitted by Room DAO (`articleDao.observeArticles()`). This guarantees that cached data is rendered instantly upon launch with zero network latency.

2. **Network Updates Room:** When a refresh is triggered, the repository makes a network call to the remote API. Upon receiving the payload, the repository persists it directly into the local Room database (`articleDao.upsert(data)`).

3. **Automatic Reactive UI Emission:** Because Room's SQLite database observer tracks table modifications, inserting new data automatically triggers Room to re-query and emit the fresh list through its cold Flow. The UI receives the update automatically without any manual coordination.

## Interview answer — deep senior

Under the hood, Room achieves this via SQLite transaction hooks and `InvalidationTracker`. When you return `Flow<List<T>>` from a DAO method, Room registers a table observer. Whenever any DAO write transaction commits against that table, `InvalidationTracker` dispatches an invalidation event on Room's query executor, prompting the Flow to re-query SQLite and emit the fresh snapshot.

In enterprise codebases, we guard against stale deletions and conflicts using **Database Synchronization Strategies**: Instead of naive `insertAll()`, we either use `@Upsert` (introduced in Room 2.5) or execute a clean transaction: `withTransaction { dao.deleteStale(); dao.insertAll(fresh) }`. This ensures that items deleted on the backend are removed from local storage without breaking the continuous Flow observation.

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
