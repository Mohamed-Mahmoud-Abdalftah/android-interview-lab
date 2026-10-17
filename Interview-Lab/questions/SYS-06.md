---
id: "SYS-06"
question: "Design caching, pagination, and remote synchronization."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 335
editorial_status: "reviewed"
---

# SYS-06

## Original interview question

Design caching, pagination, and remote synchronization.

## What the interviewer evaluates

Combine cache, Paging 3 and remote sync with stable keys and freshness.

## Concept and technical explanation

Designing mobile caching, pagination, and remote data synchronization requires balancing network bandwidth, memory pressure, and UI frame rate stability. A modern Android pagination architecture pairs Jetpack Paging 3 with Room local database caching via a RemoteMediator. RemoteMediator bridges remote REST/GraphQL APIs with the local SQLite persistence layer, requesting subsequent network pages only when the user scrolls near the boundary of cached data. Fetched items are persisted directly into Room within an atomic transaction alongside a dedicated RemoteKeys table tracking page tokens or timestamps. The Compose UI observes a continuous Flow of PagingData sourced directly from Room's PagingSource, guaranteeing 60/120 FPS jank-free scrolling, zero-latency offline access, and automatic memory windowing.

## Practical walkthrough (English)

Implementing robust caching, pagination, and sync with Jetpack Paging 3 and RemoteMediator:
```kotlin
// 1. Entities for Content and Pagination Remote Keys
@Entity(tableName = "articles")
data class ArticleEntity(
    @PrimaryKey val id: String,
    val title: String,
    val summary: String,
    val publishedAtMs: Long
)

@Entity(tableName = "article_remote_keys")
data class ArticleRemoteKeys(
    @PrimaryKey val articleId: String,
    val prevKey: Int?,
    val nextKey: Int?
)

// 2. RemoteMediator coordinating network page fetches with Room caching
@OptIn(ExperimentalPagingApi::class)
class ArticleRemoteMediator(
    private val database: AppDatabase,
    private val apiService: ArticleApiService
) : RemoteMediator<Int, ArticleEntity>() {

    override suspend fun load(
        loadType: LoadType,
        state: PagingState<Int, ArticleEntity>
    ): MediatorResult {
        val page = when (loadType) {
            LoadType.REFRESH -> {
                val remoteKeys = getRemoteKeyClosestToPosition(state)
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

        return try {
            val response = apiService.getArticles(page = page, pageSize = state.config.pageSize)
            val articles = response.items
            val endOfPaginationReached = articles.isEmpty()

            database.withTransaction {
                if (loadType == LoadType.REFRESH) {
                    database.articleRemoteKeysDao().clearRemoteKeys()
                    database.articleDao().clearArticles()
                }

                val prevKey = if (page == 1) null else page - 1
                val nextKey = if (endOfPaginationReached) null else page + 1
                val keys = articles.map { ArticleRemoteKeys(it.id, prevKey, nextKey) }

                database.articleRemoteKeysDao().insertAll(keys)
                database.articleDao().insertAll(articles.map { it.toEntity() })
            }

            MediatorResult.Success(endOfPaginationReached = endOfPaginationReached)
        } catch (e: Exception) {
            MediatorResult.Error(e)
        }
    }

    private suspend fun getRemoteKeyForLastItem(state: PagingState<Int, ArticleEntity>): ArticleRemoteKeys? {
        return state.pages.lastOrNull { it.data.isNotEmpty() }?.data?.lastOrNull()?.let { article ->
            database.articleRemoteKeysDao().getRemoteKeyByArticleId(article.id)
        }
    }

    private suspend fun getRemoteKeyClosestToPosition(state: PagingState<Int, ArticleEntity>): ArticleRemoteKeys? {
        return state.anchorPosition?.let { position ->
            state.closestItemToPosition(position)?.id?.let { articleId ->
                database.articleRemoteKeysDao().getRemoteKeyByArticleId(articleId)
            }
        }
    }
}
```

## Explanation in Arabic

كيف تصمم نظام تخزين مؤقت (Caching)، تقسيم صفحات (Pagination)، ومزامنة البيانات عن بُعد (Remote Synchronization)؟

1. استراتيجيات التخزين المؤقت (Multi-Tier Caching Architecture):
   - **L1 In-Memory Cache (RAM)**: سريع جداً (ميكروثانية) ومناسب للصور والأشياء النشطة في الـ UI، ولكنه يموت بموت التطبيق. نستخدم `LruCache` بحجم محدد.
   - **L2 Persistent Storage (Disk - Room SQLite)**: يحتفظ بالبيانات عبر جلسات التطبيق والـ Process Death. يعمل كـ Single Source of Truth.
   - **HTTP Cache Headers (OkHttp Cache)**: احترام هيدرز السيرفر (`ETag`, `Cache-Control: max-age`, `If-None-Match: 304 Not Modified`) لمنع إعادة تحميل بيانات لم تتغير.

2. تقسيم الصفحات الحديث (Pagination via Jetpack Paging 3):
   - **Keyset / Cursor-Based Pagination**: أفضل بكثير من Offset/Limit التقليدي لأن الـ Offset يعاني من مشاكل تكرار العناصر أو تفويتها عند إضافة عناصر جديدة في أول القائمة أثناء تصفح المستخدم.
   - **RemoteMediator**: الجسر الهندسي في Paging 3 الذي يراقب نهاية القائمة في الـ Room DB ويقوم بطلب الصفحة التالية من الـ Network، ثم حفظها في Room، فتقوم Room بتحديث الـ UI تلقائياً بسلاسة وبدون أي فجوات.

3. سياسة تفريغ الذاكرة المؤقتة (Cache Invalidation & Eviction):
   - مسح العناصر القديمة بعد فترة زمنية (Time-To-Live - TTL).
   - وضع سقف أعلى لحجم الكاش على القرص (مثلاً 200MB)، وحذف أقدم العناصر عند الوصول للحد الأقصى (Least Recently Used - LRU).

## Practical walkthrough

تنفيذ Paging 3 مع RemoteMediator ومصدر حقيقة محلي في Room ومزامنة شبكة ذكية:
```kotlin
@OptIn(ExperimentalPagingApi::class)
class ArticleRemoteMediator(
    private val database: AppDatabase,
    private val apiService: ArticleApiService
) : RemoteMediator<Int, ArticleEntity>() {
    private val articleDao = database.articleDao()
    private val remoteKeyDao = database.remoteKeyDao()

    override suspend fun load(
        loadType: LoadType,
        state: PagingState<Int, ArticleEntity>
    ): MediatorResult {
        return try {
            // 1. تحديد رقم الصفحة المطلوبة بناءً على نوع الـ LoadType والـ Keys المحفوظة:
            val page = when (loadType) {
                LoadType.REFRESH -> 1
                LoadType.PREPEND -> return MediatorResult.Success(endOfPaginationReached = true)
                LoadType.APPEND -> {
                    val remoteKey = getRemoteKeyForLastItem(state)
                    val nextKey = remoteKey?.nextPage ?: return MediatorResult.Success(endOfPaginationReached = remoteKey != null)
                    nextKey
                }
            }

            // 2. جلب البيانات من الشبكة:
            val response = apiService.getArticles(page = page, pageSize = state.config.pageSize)
            val endOfPaginationReached = response.articles.isEmpty()

            // 3. كتابة البيانات ومفاتيح الصفحات في Room ضمن Transaction ذرية:
            database.withTransaction {
                if (loadType == LoadType.REFRESH) {
                    remoteKeyDao.clearRemoteKeys()
                    articleDao.clearAll()
                }
                val nextKey = if (endOfPaginationReached) null else page + 1
                remoteKeyDao.insertAll(response.articles.map { ArticleRemoteKey(it.id, nextKey) })
                articleDao.insertAll(response.articles.map { it.toEntity() })
            }

            MediatorResult.Success(endOfPaginationReached = endOfPaginationReached)
        } catch (e: Exception) {
            MediatorResult.Error(e)
        }
    }

    private suspend fun getRemoteKeyForLastItem(state: PagingState<Int, ArticleEntity>): ArticleRemoteKey? {
        return state.pages.lastOrNull { it.data.isNotEmpty() }?.data?.lastOrNull()?.let {
            remoteKeyDao.getRemoteKeyByArticleId(it.id)
        }
    }
}
```

## Why it matters and how it works

PagingData is a UI window over local rows, not a substitute for sync correctness. RemoteMediator handles REFRESH/APPEND and invalidates Room source via committed changes. Version checks reject out-of-order refresh. WorkManager can prefetch, while UI on-demand loads remain responsive.

## Worked example

Conceptual Kotlin graph; types are app-owned except Paging APIs.

```kotlin
// Backend cursor pages -> RemoteMediator
// RemoteMediator -> Room transaction(items + remoteKeys)
// Room PagingSource -> Pager.flow -> ViewModel.cachedIn(viewModelScope)
// UI renders cached rows and load/freshness state.
```

## Trade-offs and decision criteria

Local-first paging gives instant offline scrolling but adds key schema and migration complexity. Network-only PagingSource is simpler if offline is unnecessary. Prefetch uses battery/data and should respect constraints. Cache invalidation must preserve pending user edits.

## Failure modes

Clearing rows before successful refresh produces blank UI. Storing remote keys after rows in a separate transaction can repeat pages after crash. A late stale response can overwrite newer content. Treating load error as a reason to delete cache harms offline UX.

## Production perspective

A news/social feed opens from Room, refreshes pages by opaque cursor, marks stale age and uses stable article IDs. Sync writes server versions; WorkManager prefetches only under acceptable network constraints. Tests cover reordering, cursor expiry, offline restart and duplicate page.

## Interview answer — short

We combine Jetpack Paging 3 with Room database caching using a RemoteMediator. The UI observes a reactive PagingData stream directly from Room, guaranteeing instant offline rendering and smooth scrolling. As the user approaches the scroll boundary, RemoteMediator fetches the next page from the network, stores it in Room alongside boundary keys in a single transaction, and automatically updates the UI.

## Interview answer — structured

A scalable pagination and caching architecture utilizes Room persistence as the backing store for Jetpack Paging 3, orchestrated by RemoteMediator.
Instead of loading network payloads directly into memory-backed lists that are lost on process death, all paginated data flows from the network into Room tables.
The UI observes a continuous Flow of PagingData sourced from a Room PagingSource, ensuring that list items remain available offline and survive orientation changes without re-fetching.
When the user scrolls near the list boundary, Paging 3 signals RemoteMediator to fetch additional items.
RemoteMediator looks up the corresponding page token from a dedicated RemoteKeys table, executes the HTTP request, and saves both the new items and updated keys within a single atomic database transaction.
If the network request fails, Paging 3 surfaces the error state directly to the UI's load state adapter, allowing users to retry with a single tap while continuing to view previously cached content.
This decouples network latency from UI rendering and optimizes memory consumption.

## Interview answer — deep senior

Under the hood, the combination of Paging 3 and Room eliminates common production pitfalls like duplicate items, scroll jumps, and memory bloat.
In memory-only pagination, rapid user scrolling accumulates thousands of heavy object allocations in the heap, eventually triggering garbage collection pauses and OutOfMemory errors.
By backing the PagingSource with SQLite, Room and Paging 3 utilize windowed cursor queries, holding only the active viewport items and a small prefetch buffer in memory while paging data in and out of disk seamlessly.
The critical design challenge in RemoteMediator is managing cache invalidation and prepend or append boundary keys.
We maintain a separate RemoteKeys table storing next and previous page identifiers keyed by item ID.
During a user pull-to-refresh action, RemoteMediator triggers a REFRESH load type, clearing stale entities and resetting remote keys in an atomic transaction before writing fresh items.
Furthermore, we decouple item identity using stable keys in LazyColumn, which prevents Compose recomposition flicker during item updates.
For freshness, we store a sync timestamp; if the cached dataset exceeds our time-to-live threshold, RemoteMediator initiates a background refresh while immediately displaying the cached data, achieving instantaneous startup performance.
Additionally, to avoid exceeding Android's two-megabyte SQLite CursorWindow threshold on media-heavy datasets, our Room queries select only the minimal columns needed for list rendering, preventing CursorWindowAllocationException under high scroll velocity.

## How to answer in the interview

- **Why:** paging must preserve a stable user-visible dataset.
- **How:** use Room PagingSource as display source and RemoteMediator for transactional fetch.
- **Trade-off:** stale cache improves speed but needs freshness signaling.
- **Failure case:** unstable offset paging duplicates or skips rows.
- **Production solution:** negotiate cursor/version contract and test refresh, append, deletion, and offline paths.

## Deep-dive talking points

Trace page key lifecycle and distinguish UI windowing from sync correctness.

## Follow-up questions

- **Interviewer:** "Why is .cachedIn(viewModelScope) essential in Paging 3?"
  **Answer:** "It caches the active PagingData stream across configuration changes so that ViewModels do not trigger a fresh collection or recreate pages on screen rotation."

- **Interviewer:** "What is the difference between PagingSource and RemoteMediator?"
  **Answer:** "PagingSource loads data from a single data source (either memory or DB); RemoteMediator coordinates loading from network into a local database source of truth."

## Self-check rubric

Can I preserve cache on error, store keys atomically and handle changing server order?

## References and reviewed-on date

- [Android Paging network/database](https://developer.android.com/topic/libraries/architecture/paging/v3-network-db) — mediator architecture.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — local source of truth.

Technically reviewed against primary documentation on 2026-10-13.
