---
id: "DAT-21"
question: "Design a paginated news feed that opens instantly and syncs when online."
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "C"
phase: 3
priority: "P1"
order: 278
editorial_status: "reviewed"
---

# DAT-21

## Original interview question

Design a paginated news feed that opens instantly and syncs when online.

## What the interviewer evaluates

Design instant paginated news with Room-backed Paging and online sync.

## Explanation in Arabic

تصميم نظام تغذية إخبارية مقسمة لصفحات (Paginated News Feed) تفتح فوراً في 5ms دون اتصال وتتزامن عند الاتصال بالإنترنت:

1. المخطط المعماري الكامل (Architecture Blueprint):
   - **قاعدة البيانات المحلية (Room) هي المصدر الوحيد للحقيقة (Single Source of Truth)**.
   - **UI Layer (Jetpack Compose / LazyColumn)**: تجمع `Flow<PagingData<Article>>` من الـ ViewModel باستخدام `collectAsLazyPagingItems()`.
   - **Presentation Model**: تعرض البيانات المخزنة فوراً من الـ SQLite Cache دون أي مؤشر انتظار أولي (Zero Initial Loading Spinner).
   - **Data Layer (Paging 3 + RemoteMediator)**: يتولى `RemoteMediator` جلب الصفحات من السيرفر في الخلفية وكتابتها في Room.
   - **مفاتيح التصفح (RemoteKeys Table)**: جدول في Room يخزن الصفحة التالية والسابقة لكل مقال لضمان عدم تكرار المقالات.

2. تجربة المستخدم في وضع عدم الاتصال (Offline UX):
   - عندما يفتح المستخدم التطبيق بدون إنترنت، تعرض الشاشة المقالات المخزنة فوراً، مع شريط علوي خفيف يفيد بأن التطبيق في وضع عدم الاتصال.
   - عند عودة الإنترنت، يقوم `RemoteMediator` بجلب أحدث المقالات ودمجها بسلاسة دون التسبب في قفز الشاشة (No Scroll Jumping).

## Practical walkthrough

التطبيق البرمجي لنظام الأخبار الفوري باستخدام Room و Paging 3 و RemoteMediator:
```kotlin
// 1. إعداد الـ Repository لربط Room مع RemoteMediator:
class NewsRepositoryImpl @Inject constructor(
    private val database: AppDatabase,
    private val newsApi: NewsApiService
) : NewsRepository {

    @OptIn(ExperimentalPagingApi::class)
    override fun getNewsFeedStream(): Flow<PagingData<ArticleEntity>> {
        return Pager(
            config = PagingConfig(
                pageSize = 20,
                enablePlaceholders = false,
                initialLoadSize = 20 // تحميل 20 عنصراً فقط لسرعة فائقة
            ),
            remoteMediator = NewsRemoteMediator(newsApi, database),
            // القراءة تتم حصرياً من Room PagingSource:
            pagingSourceFactory = { database.newsDao().observePagedArticles() }
        ).flow
    }
}

// 2. الـ ViewModel يعرض التدفق مباشرة مع التخزين المؤقت في viewModelScope:
@HiltViewModel
class NewsFeedViewModel @Inject constructor(
    repository: NewsRepository
) : ViewModel() {
    val feedPagingData = repository.getNewsFeedStream().cachedIn(viewModelScope)
}

// 3. في Compose: فتح فوري في 5 ميلي ثانية من الكاش المحلي:
@Composable
fun NewsFeedScreen(viewModel: NewsFeedViewModel = hiltViewModel()) {
    val articles = viewModel.feedPagingData.collectAsLazyPagingItems()

    LazyColumn {
        items(
            count = articles.itemCount,
            key = articles.itemKey { it.id } // مفاتيح ثابتة لمنع قفز الشاشة عند التحديث!
        ) { index ->
            articles[index]?.let { article -> ArticleCard(article) }
        }
    }
}
```

## Why it matters and how it works

Pager produces PagingData from Room; mediator loads remote pages and commits keys with rows. A refresh policy determines when cached data is stale. WorkManager can prefetch under constraints, while UI collection can trigger on-demand loads. Backend cursor stability matters when stories are inserted or reordered.

## Worked example

Conceptual Paging 3 repository; DAO, mediator and model types are application-specific.

```kotlin
import androidx.paging.Pager
import androidx.paging.PagingConfig
import androidx.paging.PagingData
import kotlinx.coroutines.flow.Flow

fun news(dao: NewsDao, mediator: NewsMediator): Flow<PagingData<Article>> =
    Pager(PagingConfig(pageSize = 30), remoteMediator = mediator) {
        dao.pagingSource()
    }.flow
```

## Trade-offs and decision criteria

Room-backed paging gives instant offline content but adds storage and key migration work. Network-only paging is simpler but opens empty offline. Prefetch improves startup at battery/network cost; respect user data policies.

## Failure modes

An offset API on a changing feed can skip/duplicate stories when new items arrive. Clearing cache before successful refresh flashes empty UI. Failing to persist keys with rows can make APPEND repeat pages after process death.

## Production perspective

A news app shows cached headlines immediately, starts conditional refresh when online, stores pages and cursors in one transaction, and labels stale content. Tests cover offline launch, new articles inserted at top, repeated pages and crash during refresh.

## Interview answer — short

Design an instant offline-first paginated feed by configuring Paging 3 with Room as the local source of truth via pagingSourceFactory and RemoteMediator as the network coordinator. UI renders local Room data instantly in 5ms, while RemoteMediator fetches remote pages in the background, updating Room transactionally without scroll jumps using stable item keys.

## Interview answer — structured

Designing an instant-opening, paginated feed that works seamlessly offline requires four integrated architectural pillars.

First, a Room as the Single Source of Truth is the UI collects `Flow<PagingData<T>>` served exclusively by Room's generated `PagingSource`. When the app launches, local SQLite records render onto the screen in under 5ms without displaying full-screen loading spinners. Next, with Background Pagination Coordination (`RemoteMediator`), `RemoteMediator` intercepts scroll boundaries. When the user nears the bottom, it requests the next page from the API and writes the items and page cursors (`RemoteKeys`) into SQLite within a single `roomDatabase.withTransaction { }`.
Additionally, with Zero Scroll-Jumping UX, in Jetpack Compose, pass stable item keys (`key = articles.itemKey { it.id }`). When fresh items are inserted into SQLite, Compose calculates precise diffs, maintaining the user's scroll position rather than snapping to the top. Finally, with Graceful Offline Degradation, network errors during background fetches are routed to `LoadState.Error`. The existing cached list remains fully interactive, and a subtle inline snackbar offers a 'Retry' action without blanking the screen.


## Interview answer — deep senior

To achieve true enterprise-grade performance with large feeds.

First, with InitializeAction.SKIP_INITIAL_REFRESH, in `RemoteMediator.initialize()`, inspect the timestamp of the last successful sync. If local data is less than 15 minutes old, return `SKIP_INITIAL_REFRESH`. This eliminates redundant API calls on frequent app launches, saving battery and server costs. Finally, with Cache Pruning and Database Compaction, if an infinite feed appends hundreds of articles daily, the SQLite database will bloat over time. Implement an automated cleanup task in `RemoteMediator` on `REFRESH`: retain the most recent 200 articles and delete older items (`DELETE FROM articles WHERE id NOT IN (SELECT id FROM articles ORDER BY publishedAt DESC LIMIT 200)`).


## How to answer in the interview

- **Why:** Instant launch and offline reading need local paging.
- **How:** Room PagingSource renders; mediator refreshes rows and keys transactionally.
- **Trade-offs:** Cursor/snapshot contract versus simpler but shifting offsets.
- **Failure cases:** Blank feed on failed refresh or duplicate page rows.
- **Production solution:** Stale indicator, retry load state and offline/article tests.

## Deep-dive talking points

Draw Page API → mediator → Room → UI and describe cursor/invalidation behavior.

## Follow-up questions

- **Interviewer:** "Why is `cachedIn(viewModelScope)` mandatory in Paging 3?"
  **Answer:** "It caches the PagingData stream across configuration changes (screen rotations), preventing the entire paging flow from resetting and reloading from scratch."

- **Interviewer:** "What is the role of `enablePlaceholders = false` in PagingConfig?"
  **Answer:** "It prevents Room from projecting thousands of null placeholder items in the list before they are actually loaded from SQLite."

## Self-check rubric

Can I show instant local page, atomic keys, stable cursor and offline error UX?

## References and reviewed-on date

- [Android Paging network/database guide](https://developer.android.com/topic/libraries/architecture/paging/v3-network-db) — RemoteMediator.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — local source of truth.

Technically reviewed against primary documentation on 2026-10-13.
