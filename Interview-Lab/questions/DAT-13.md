---
id: "DAT-13"
question: "How would you implement Paging 3 and RemoteMediator?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "B"
phase: 3
priority: "P1"
order: 270
editorial_status: "reviewed"
---

# DAT-13

## Original interview question

How would you implement Paging 3 and RemoteMediator?

## What the interviewer evaluates

Design Paging 3 with Room source, RemoteMediator keys and refresh transaction.

## Concept and technical explanation

Jetpack Paging 3 combined with RemoteMediator provides an enterprise-grade architecture for large-dataset pagination backed by local database caching:
- Paging 3 Architecture Layers:
  * Local Source of Truth: Room provides the PagingSource via standard SQL queries (SELECT * FROM items ORDER BY index). The UI layer consumes an immutable Flow<PagingData<Item>> pipeline directly from the database, eliminating network flickering and providing instant offline rendering.
  * Pager Component: Connects the PagingConfig (defining pageSize, prefetchDistance, and enablePlaceholders) with Room's PagingSource and the optional RemoteMediator.
- RemoteMediator Role & Mechanics:
  * Boundary Detection: Unlike an in-memory PagingSource that fetches network directly, RemoteMediator acts as a signal listener. When the user scrolls near the end of the cached local list, Paging 3 invokes RemoteMediator.load(loadType, state).
  * LoadType Taxonomy: REFRESH (initial load or swipe-to-refresh), APPEND (scrolling towards the end of dataset), PREPEND (scrolling towards the start of dataset).
- RemoteKey Entity & Atomic Refresh:
  * To track pagination cursors or next/prev page tokens across process death, a companion RemoteKeyEntity table is maintained in Room.
  * When loadType == REFRESH, Room executes an atomic transaction that clears existing RemoteKeys, clears stale feed items, and inserts the initial batch of network items alongside their updated cursors, ensuring seamless, non-jumping UI rendering.

## Practical walkthrough (English)

Complete Paging 3 and RemoteMediator implementation:
```kotlin
@OptIn(ExperimentalPagingApi::class)
class FeedRemoteMediator(
    private val db: AppDatabase,
    private val api: FeedApiService
) : RemoteMediator<Int, FeedItemEntity>() {

    override suspend fun load(
        loadType: LoadType,
        state: PagingState<Int, FeedItemEntity>
    ): MediatorResult {
        val page = when (loadType) {
            LoadType.REFRESH -> {
                val remoteKeys = getRemoteKeyClosestToCurrentPosition(state)
                remoteKeys?.nextKey?.minus(1) ?: 1
            }
            LoadType.PREPEND -> return MediatorResult.Success(endOfPaginationReached = true)
            LoadType.APPEND -> {
                val remoteKeys = getRemoteKeyForLastItem(state)
                val nextKey = remoteKeys?.nextKey
                    ?: return MediatorResult.Success(endOfPaginationReached = remoteKeys != null)
                nextKey
            }
        }

        try {
            val response = api.fetchFeed(page = page, pageSize = state.config.pageSize)
            val items = response.items.map { it.toEntity() }
            val endOfPagination = items.isEmpty()

            db.withTransaction {
                if (loadType == LoadType.REFRESH) {
                    db.remoteKeyDao().clearRemoteKeys()
                    db.feedDao().clearFeed()
                }
                val prevKey = if (page == 1) null else page - 1
                val nextKey = if (endOfPagination) null else page + 1
                val keys = items.map { FeedRemoteKey(it.id, prevKey, nextKey) }

                db.remoteKeyDao().insertAll(keys)
                db.feedDao().insertAll(items)
            }
            return MediatorResult.Success(endOfPaginationReached = endOfPagination)
        } catch (e: Exception) {
            return MediatorResult.Error(e)
        }
    }
}
```

## Explanation in Arabic

كيف تنفذ مكتبة Paging 3 مع RemoteMediator لدعم التصفح بالصفحات في تطبيق Offline-First؟

1. المفهوم المعماري لـ Paging 3 مع الـ Offline-First:
   - **المصدر الوحيد للحقيقة هو Room (Single Source of Truth)**: لا تعرض الـ UI صفحات الشبكة مباشرة!
   - الـ `Pager` يقدم البيانات للـ UI حصرياً من `PagingSource` الخاص بقاعدة بيانات Room.
   - **دور الـ `RemoteMediator`**: يعمل كمراقب في الخلفية. عندما يقترب المستخدم من نهاية القائمة المعروضة في الشاشة وتنفد البيانات من Room، يتدخل `RemoteMediator` تلقائياً ليطلب الصفحة التالية من الـ Network API ويكتبها في Room.
   - بمجرد كتابة البيانات في Room، يقوم Room تلقائياً بتحديث `PagingData` المعروضة في الشاشة بسلاسة.

2. مكونات دورة حياة RemoteMediator:
   - **`LoadType.REFRESH`**: عندما يقوم المستخدم بالسحب للتحديث (Pull-to-Refresh)، أو عند التشغيل لأول مرة.
   - **`LoadType.APPEND`**: عندما يصل المستخدم لنهاية القائمة لجلب الصفحة التالية.
   - **`LoadType.PREPEND`**: عند التمرير لأعلى (نادراً ما يحتاج لجلب بيانات إذا كنا نبدأ من البداية).
   - **`RemoteKeys` Table**: جدول في Room يخزن أرقام الصفحات السابقة والتالية (`prevKey`, `nextKey`) لكل عنصر لضمان معرفة الصفحة التالية بدقة.

## Practical walkthrough

هيكل تنفيذ RemoteMediator الكامل في Paging 3 مع Room:
```kotlin
@OptIn(ExperimentalPagingApi::class)
class ArticleRemoteMediator(
    private val api: ArticleApiService,
    private val database: AppDatabase
) : RemoteMediator<Int, ArticleEntity>() {

    override suspend fun load(loadType: LoadType, state: PagingState<Int, ArticleEntity>): MediatorResult {
        return try {
            // 1. تحديد رقم الصفحة المطلوبة بناءً على LoadType:
            val page = when (loadType) {
                LoadType.REFRESH -> 1
                LoadType.PREPEND -> return MediatorResult.Success(endOfPaginationReached = true)
                LoadType.APPEND -> {
                    val remoteKey = getRemoteKeyForLastItem(state)
                    val nextKey = remoteKey?.nextPage ?: return MediatorResult.Success(endOfPaginationReached = remoteKey != null)
                    nextKey
                }
            }

            // 2. جلب البيانات من السيرفر:
            val response = api.fetchArticles(page = page, pageSize = state.config.pageSize)
            val endOfPagination = response.items.isEmpty()

            // 3. كتابة البيانات ومفاتيح الصفحات في Room داخل Transaction واحدة:
            database.withTransaction {
                if (loadType == LoadType.REFRESH) {
                    database.remoteKeysDao().clearAllKeys()
                    database.articleDao().clearAllArticles()
                }
                val nextKey = if (endOfPagination) null else page + 1
                val keys = response.items.map { ArticleRemoteKey(it.id, prevPage = page - 1, nextPage = nextKey) }
                database.remoteKeysDao().insertAll(keys)
                database.articleDao().insertAll(response.items.map { it.toEntity() })
            }

            MediatorResult.Success(endOfPaginationReached = endOfPagination)
        } catch (e: Exception) {
            MediatorResult.Error(e) // Paging 3 يعرض حالة الخطأ في الـ UI مع زر Retry تلقائياً
        }
    }
}
```

## Why it matters and how it works

RemoteMediator coordinates remote load with local database; stable item IDs and remote keys/cursors prevent duplicate or missing pages. On REFRESH decide whether to clear/replace within a transaction while preserving user-owned pending edits. `cachedIn(viewModelScope)` shares PagingData across configuration changes within ViewModel lifetime.

## Worked example

Conceptual Android Paging repository; FeedDao and FeedMediator are app types, and page size is illustrative.

```kotlin
import androidx.paging.Pager
import androidx.paging.PagingConfig
import androidx.paging.PagingData
import kotlinx.coroutines.flow.Flow

fun feed(dao: FeedDao, mediator: FeedMediator): Flow<PagingData<FeedItem>> =
    Pager(
        config = PagingConfig(pageSize = 30),
        remoteMediator = mediator,
        pagingSourceFactory = { dao.pagingSource() },
    ).flow
```

## Trade-offs and decision criteria

Paging controls memory/network demand but adds remote-key and invalidation complexity. A network-only PagingSource may be simpler for ephemeral data; Room plus mediator is preferable when offline startup and a single local truth matter.

## Failure modes

Using offset keys on a changing server list can duplicate/skip items; cursor/version contracts are safer. Clearing tables outside a transaction can flash empty UI. An error load state must offer retry without wiping cached rows.

## Production perspective

A news app opens cached Room articles instantly, appends pages via server cursor, and commits rows plus keys together. Refresh labels stale data until successful; tests cover offline startup, repeated APPEND and reordered server items.

## Interview answer — short

Paging 3 with RemoteMediator uses Room as the single source of truth for UI streams while fetching incremental network pages at scroll boundaries. Companion RemoteKey tables persist pagination tokens across app restarts, and atomic Room transactions coordinate clearing and inserting records during refreshes without UI flickering.

## Interview answer — structured

Implementing Paging 3 with RemoteMediator establishes an offline-first pagination pipeline for large datasets.
First, Room serves as the absolute single source of truth. The DAO exposes a PagingSource queried by the Pager, streaming immutable PagingData directly to Compose or RecyclerView lists.
Second, RemoteMediator acts as a bridge between the local database and the remote network API. When the user scrolls near the end of the cached list, Paging 3 triggers RemoteMediator.load with an APPEND or REFRESH load type.
Third, we persist pagination tokens or cursors in a separate RemoteKeys table in Room.
During a REFRESH event, we execute an atomic transaction that resets remote keys, purges stale items, and inserts the fresh page, eliminating list jumping and supporting seamless offline paging.

## Interview answer — deep senior

Architecting paginated feeds using Jetpack Paging 3 and RemoteMediator requires shifting from naive network-bound pagination to local-first database mediation.
A common anti-pattern is creating a custom PagingSource that calls Retrofit directly.
While straightforward, this approach breaks offline support, discards cached scroll positions on process death, and causes layout jumps during network re-fetches.
RemoteMediator solves this by fully decoupling UI pagination from network latency.
The UI layer observes a cold Flow<PagingData<Item>> queried strictly from Room.
When the user scrolls past the prefetchDistance threshold, Paging 3 evaluates the viewport and dispatches an APPEND event to RemoteMediator.
To maintain cursor integrity across app process death and system restarts, we maintain a companion FeedRemoteKeys table in Room storing nextKey and prevKey tokens.
During a swipe-to-refresh action (LoadType.REFRESH), executing the reset atomically inside db.withTransaction is mandatory.
We delete outdated remote keys, purge cached feed entities, and insert the new page along with its successor cursors within a single SQLite transaction.
Because Room is observed via Flow, the UI transitions gracefully to the fresh dataset without visual blinking or scroll glitches, providing a high-performance 120Hz scrolling experience that remains completely functional even when the user enters offline areas.
Additionally, we configure backpressure handling and prefetch buffers within PagingConfig, ensuring background network fetching completes well ahead of user scroll thresholds for an uninterrupted reading experience.

## How to answer in the interview

- **Why:** Large feeds need bounded loading with consistent cached pages.
- **How:** Room PagingSource reads; RemoteMediator fetches and transacts rows/keys.
- **Trade-offs:** Choose cursor/snapshot semantics for changing lists when available.
- **Failure cases:** Erasing cache on failed refresh or duplicate/shifted pages.
- **Production solution:** Test load states, restart, empty pages and offline scroll.

## Deep-dive talking points

Trace REFRESH/APPEND, key storage, cursor stability and cached failure behavior.

## Follow-up questions

- **Interviewer:** "What is the purpose of `InitializeAction.SKIP_INITIAL_REFRESH`?"
  **Answer:** "It instructs RemoteMediator to skip the network refresh on launch if local cached data is deemed fresh, opening the screen offline immediately."

- **Interviewer:** "How do you display error states with Paging 3 in Compose?"
  **Answer:** "Inspect `lazyPagingItems.loadState.append` or `refresh` for `LoadState.Error`, rendering a retry button or error banner."

## Self-check rubric

Can I identify source of truth, persist keys atomically and test changing server order?

## References and reviewed-on date

- [Android Paging network/database guide](https://developer.android.com/topic/libraries/architecture/paging/v3-network-db) — RemoteMediator pattern.

Technically reviewed against primary documentation on 2026-10-13.
