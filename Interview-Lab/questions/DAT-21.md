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

## Concept and technical explanation

Designing an enterprise paginated news feed with instant cold start and robust offline synchronization requires an integrated architectural system:
- Instant Cold Start & Single Source of Truth: The UI never awaits network responses on launch. ViewModels query Room directly, observing a cold Flow<PagingData<ArticleEntity>>. Room delivers cached articles from disk in under 50ms, rendering the feed immediately without blank screens or loading shimmers.
- Jetpack Paging 3 with RemoteMediator: Decouples UI rendering from network transport. As the user scrolls near the threshold of cached items, RemoteMediator detects the boundary and dispatches an asynchronous network request to fetch the subsequent page.
- Cursor & RemoteKey Persistence: A companion ArticleRemoteKeys table in Room tracks pagination tokens (prevKey and nextKey) for each entity, ensuring scroll positions and page cursors survive process death.
- Atomic Refresh & Consistency: Swipe-to-refresh actions execute inside RoomDatabase.withTransaction: clearing outdated non-bookmarked cache, resetting remote keys, and inserting fresh articles atomically to eliminate visual jumping.
- Dual-Layer Image Caching: Media loaders (such as Coil) configure disk and memory caches with 250MB bounds, prefetching article thumbnails ahead of the viewport.
- Periodic Background Synchronization: WorkManager periodically syncs the feed under unmetered network conditions, keeping the offline cache warm.

## Practical walkthrough (English)

System architecture connecting Room, RemoteMediator, and Pager:
```kotlin
@Entity(tableName = "articles")
data class ArticleEntity(
    @PrimaryKey val id: String,
    val title: String,
    val snippet: String,
    val publishedAt: Long
)

@Entity(tableName = "article_remote_keys")
data class ArticleRemoteKey(
    @PrimaryKey val articleId: String,
    val prevKey: Int?,
    val nextKey: Int?
)

class FeedRepository(
    private val db: AppDatabase,
    private val api: NewsApiService
) {
    @OptIn(ExperimentalPagingApi::class)
    fun getNewsStream(): Flow<PagingData<ArticleEntity>> {
        return Pager(
            config = PagingConfig(pageSize = 20, prefetchDistance = 5, enablePlaceholders = false),
            remoteMediator = NewsRemoteMediator(db, api),
            pagingSourceFactory = { db.articleDao().pagingSource() }
        ).flow
    }
}
```

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

Designing an instant-launch paginated feed requires Jetpack Paging 3 with RemoteMediator and Room as the single source of truth. The UI streams cached articles immediately via Flow, RemoteMediator fetches subsequent pages at scroll boundaries, companion RemoteKey tables preserve cursors, and WorkManager keeps content warm in the background.

## Interview answer — structured

Architecting an instant-opening paginated news feed requires separating immediate local presentation from background network synchronization.
First, make Room the single source of truth. The UI observes a Flow of PagingData queried directly from SQLite, rendering cached articles in under fifty milliseconds and eliminating launch loading spinners.
Second, integrate Jetpack Paging 3 with RemoteMediator. As users scroll near the list boundary, RemoteMediator triggers network requests to fetch the next page, persisting incoming articles directly into Room.
Third, manage pagination tokens using a dedicated RemoteKeys table in Room. Storing nextKey and prevKey cursors alongside entities ensures pagination resumes correctly across application restarts.
Fourth, execute swipe-to-refresh resets inside atomic Room transactions, clearing stale items and updating keys simultaneously to avoid list flickering, paired with Coil for bounded thumbnail caching.

## Interview answer — deep senior

Architecting a paginated news feed capable of sub-100ms cold start while supporting seamless offline reading requires an offline-first reactive architecture centered around Room and Paging 3.
The primary design violation in mobile feeds is initiating network requests on screen launch before rendering content.
To achieve zero-latency startup, the UI layer connects exclusively to Room via Flow<PagingData<Article>>, allowing SQLite to stream existing cached articles to Compose or RecyclerView within milliseconds.
To coordinate pagination with backend APIs, we deploy Paging 3 with a custom RemoteMediator.
The RemoteMediator acts as a bridge: when the user scrolls near the end of the viewport, Paging 3 signals RemoteMediator to request the next page from Retrofit.
To maintain cursor integrity across app process deaths and device restarts, we persist nextKey and prevKey tokens in an ArticleRemoteKeys table in Room.
When a refresh event triggers, we wrap the database operations in db.withTransaction: clearing old unbookmarked articles, resetting remote keys, and inserting the first page atomically.
Because the UI observes Room reactively, the list updates smoothly without layout jumps or white flashes.
Furthermore, we integrate Coil with a 250MB disk cache and memory prefetching for thumbnails, and register a periodic WorkManager constraint worker to fetch fresh headlines during night charges.

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
