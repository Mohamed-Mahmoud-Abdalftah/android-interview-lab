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

Design caching and pagination using a multi-tiered architecture: L1 in-memory LruCache, L2 persistent Room database as the single source of truth, and HTTP ETag caching. Implement pagination using Jetpack Paging 3 with RemoteMediator and cursor keys to seamlessly stream network pages directly into the local database.

## Interview answer — structured

Designing scalable pagination and caching balances UI responsiveness, memory limits, and data freshness:

1. **Multi-Tiered Cache Architecture**:
   - **L1 Memory (LruCache)**: Fast access for decoded bitmaps and active view models; bounded by a strict memory cap (e.g. 25% of available heap).
   - **L2 Disk (Room Database)**: Persistent single source of truth surviving process death.
   - **L3 HTTP Layer**: Leverage OkHttp's disk cache with `ETag` and `If-None-Match` to avoid re-downloading unmodified server payloads (`304 Not Modified`).

2. **Cursor-Based Pagination with Jetpack Paging 3**:
   - Avoid traditional `offset/limit` pagination because inserting new items at the head of a live feed causes duplicate items or skipped records during scrolling. Use cursor keys (timestamps or opaque server tokens).
   - Use `RemoteMediator` to coordinate between network requests and the database. The mediator triggers network loads only when the user approaches the end of cached content, persisting pages directly to Room in an atomic transaction.

3. **Cache Eviction Strategy**:
   - Enforce an LRU eviction policy with a 200MB ceiling or TTL expiration. When refreshing lists, keep the top N items and evict stale records beyond page 5 to conserve device storage.

## Interview answer — deep senior

From an advanced performance and memory perspective, pagination architectures must prevent memory leaks and UI stutter:

1. **Paging 3 Flow Lifecycle & Invalidation**: Expose paged streams as `Flow<PagingData<Item>>` cached in `viewModelScope` using `.cachedIn(viewModelScope)`. This ensures that screen rotations or configuration changes do not re-fetch or re-paginate data from scratch, retaining the exact scroll position in Compose `LazyColumn`.

2. **Boundary Conditions & Placeholders**: Enable placeholders in `PagingConfig` when list items have fixed heights. This allows `LazyColumn` to allocate scrollbar travel accurately without jumping or layout thrashing when new pages append.

3. **Network Resilience & Partial Failures**: If a page fails to load, `RemoteMediator` returns `MediatorResult.Error(e)`. The UI catches this in `CombinedLoadStates.append` and renders a retry button at the bottom of the list without wiping the already-loaded items from the screen.

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
