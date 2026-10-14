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

Paging 3 with RemoteMediator uses Room as the single source of truth for the UI while fetching pages from the network on demand. The Pager streams data from Room's PagingSource, and RemoteMediator intercepts pagination boundaries (REFRESH, APPEND) to load network pages and save them alongside pagination keys in a Room transaction.

## Interview answer — structured

Implementing Paging 3 with `RemoteMediator` provides production-grade offline-first pagination.

First, **Architecture Separation**. Next, the presentation layer collects `Flow<PagingData<T>>` served exclusively by Room's generated `PagingSource`.
`RemoteMediator` acts as the network pump. It does not return items to the UI; it fetches remote payloads and writes them into Room. Room's invalidation tracker then emits updated paging slices to the UI. **LoadTypes & Lifecycle**.
REFRESH is triggered on initial load or swipe-to-refresh. If online, clears existing database tables and inserts page 1. APPEND is triggered when the user scrolls near the end of the loaded viewport. Fetches the next page and appends entities to Room.
PREPEND is triggered if scrolling upwards; typically returns `endOfPaginationReached = true` if items are only added forward. Finally, a RemoteKeys Table maintains cursor/page pointers in SQLite for each entity, ensuring accurate page math across app restarts and process recreation.


## Interview answer — deep senior

A frequent failure mode in Paging 3 is **Infinite Refresh Loops caused by Table Invalidation**.

If your `RemoteMediator` writes to a secondary table that triggers invalidation of the primary observed query *before* the transaction finishes, or if `RemoteMediator` returns `MediatorResult.Success(endOfPaginationReached = false)` when the network actually returned an empty list, Paging 3 continuously triggers new `APPEND` loads in an infinite loop, draining battery and flooding the server.

**Defensive Rules**.

First, always write entities and `RemoteKeys` together inside `database.withTransaction { }`. Next, if `response.items.isEmpty()`, immediately set `endOfPaginationReached = true`.
Finally, use `initialize(): InitializeAction` in `RemoteMediator`. If cached database data is fresh (e.g. Less than 10 minutes old), return `InitializeAction.SKIP_INITIAL_REFRESH` to open the screen instantly without hitting the network.


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
