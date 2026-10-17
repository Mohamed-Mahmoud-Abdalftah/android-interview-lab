---
id: "DAT-08"
question: "What are cache-first, network-first, and stale-while-revalidate strategies?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "A"
phase: 3
priority: "P1"
order: 265
editorial_status: "reviewed"
---

# DAT-08

## Original interview question

What are cache-first, network-first, and stale-while-revalidate strategies?

## What the interviewer evaluates

Compare cache-first, network-first and stale-while-revalidate from freshness and latency constraints.

## Concept and technical explanation

Data caching strategies govern the trade-off between latency, freshness, and network bandwidth in mobile architectures:
- Cache-First (Cache-Only with Fallback): Queries local storage first. If valid data exists, it returns immediately without issuing a network request. The network is contacted exclusively when cache is missing or expired. Ideal for static reference data like country codes, app feature flags, and localized product categories. Minimizes network requests and maximizes battery efficiency, but risks presenting stale data if Time-To-Live (TTL) is misconfigured.
- Network-First (Network with Cache Fallback): Issues an HTTP request to the remote backend first. Upon receiving a successful response, it updates the local cache and emits the fresh data. If the network request fails due to offline connectivity, timeouts, or 5xx server errors, it falls back to local cached data. Ideal for real-time mission-critical information like bank account balances, live stock prices, and ticket inventory. Guarantees absolute freshness when online, but incurs network latency on every screen opening and degrades perceived speed on poor cellular connections.
- Stale-While-Revalidate (SWR): Returns cached data immediately to provide instantaneous zero-latency UI rendering, while concurrently triggering an asynchronous background network request. Once the fresh network payload arrives, it persists to the local database, which automatically emits the updated snapshot to the UI via reactive Flow streams. Ideal for social feeds, news streams, and product catalogs, balancing instant perceived responsiveness with eventual consistency.

## Practical walkthrough (English)

Implementing Cache-First, Network-First, and Stale-While-Revalidate repository patterns:
```kotlin
class ProductRepository(
    private val productDao: ProductDao,
    private val api: ProductApiService
) {
    // 1. Cache-First: Emits cache if fresh, otherwise fetches network
    fun getProductCacheFirst(id: String, maxAgeMillis: Long): Flow<Product> = flow {
        val cached = productDao.getProductById(id)
        if (cached != null && (System.currentTimeMillis() - cached.updatedAt) < maxAgeMillis) {
            emit(cached.toDomain())
        } else {
            val network = api.fetchProduct(id).toEntity()
            productDao.insert(network)
            emit(network.toDomain())
        }
    }

    // 2. Stale-While-Revalidate: Emits cached data instantly, revalidates via network in background
    fun getFeedSWR(): Flow<List<FeedItem>> = flow {
        // Emit stale cache immediately for instant UI render
        val cached = productDao.getFeed().firstOrNull() ?: emptyList()
        if (cached.isNotEmpty()) emit(cached.map { it.toDomain() })

        // Asynchronously fetch fresh data and update Room
        try {
            val fresh = api.fetchFeed().map { it.toEntity() }
            productDao.replaceFeed(fresh)
            // Room Flow will automatically dispatch fresh items to observers
        } catch (e: Exception) {
            // If offline, user already sees cached data; log or show subtle offline banner
        }
    }
}
```

## Explanation in Arabic

مقارنة استراتيجيات التخزين المؤقت في Android:
Cache-First، و Network-First، و Stale-While-Revalidate، ومتى تختار كل استراتيجية؟

1. Cache-First (قراءة الكاش أولاً):
   - **كيف تعمل**: يبحث التطبيق في الكاش المحلي (Room / Disk Cache). إذا وُجدت البيانات ولم تنتهِ صلاحيتها، يتم عرضها فوراً ولا يتم الاتصال بالشبكة على الإطلاق. إذا لم تكن موجودة أو انتهت صلاحيتها، يتصل بالشبكة ويحفظ النتيجة في الكاش.
   - **المميزات**: سرعة فائقة (0-5ms)، توفير كبير لبيانات الهاتف والبطارية، وتخفيف الحمل على السيرفر.
   - **العيوب**: خطر عرض بيانات قديمة (Stale Data).
   - **أفضل استخدام**: البيانات شبه الثابتة (قائمة الدول، إعدادات التطبيق، بيانات التصنيفات، الصور والـ Assets).

2. Network-First (الاتصال بالشبكة أولاً والرجوع للكاش عند الفشل):
   - **كيف تعمل**: يحاول التطبيق الاتصال بالسيرفر أولاً. إذا نجح، يعرض أحدث بيانات ويحدث الكاش. إذا انقطع الاتصال أو حدث Timeout، يرجع للكاش ويعرض آخر نسخة محفوظة مع تنبيه المستخدم.
   - **المميزات**: حداثة البيانات دائماً (Fresh Data Guaranteed).
   - **العيوب**: بطء العرض وظهور مؤشر التحميل (Loading Spinner) دائماً، واعتمادية كاملة على سرعة الشبكة.
   - **أفضل استخدام**: البيانات الحساسة جداً التي لا تحتمل الخطأ (رصيد الحساب البنكي، أسعار الأسهم والعملات، حالة شحن الطلب المالي).

3. Stale-While-Revalidate (عرض الكاش فوراً ثم التحديث في الخلفية):
   - **كيف تعمل**: المعيار الذهبي في تطبيقات الموبايل الحديثة! يعرض التطبيق أحدث نسخة في الكاش فوراً في 5ms حتى يشاهد المستخدم المحتوى دون أي انتظار، وفي نفس اللحظة يطلق طلباً في الخلفية لجلب أحدث البيانات وتحديث الكاش والـ UI تلقائياً.
   - **أفضل استخدام**: الـ Feeds الإخبارية، وسائل التواصل الاجتماعي (Twitter/Instagram feed)، وقوائم المنتجات في التجارة الإلكترونية.

## Practical walkthrough

تنفيذ استراتيجية Stale-While-Revalidate باستخدام Kotlin Flow و Room:
```kotlin
class ArticleRepositoryImpl @Inject constructor(
    private val articleDao: ArticleDao,
    private val apiService: ArticleApiService
) : ArticleRepository {

    // Stale-While-Revalidate: ينبعث الكاش فوراً ثم يتم التحديث في الخلفية:
    override fun getArticles(): Flow<Resource<List<Article>>> = flow {
        // 1. بث النسخة المخزنة في الكاش فوراً (Stale Data):
        val cachedArticles = articleDao.getAllArticles().first()
        if (cachedArticles.isNotEmpty()) {
            emit(Resource.Success(data = cachedArticles.map { it.toDomain() }, isStale = true))
        } else {
            emit(Resource.Loading)
        }

        // 2. محاولة إعادة التحقق والتحديث من الشبكة في الخلفية (Revalidate):
        try {
            val freshArticles = apiService.fetchArticles()
            // حفظ البيانات الحديثة في Room:
            articleDao.updateAllArticles(freshArticles.map { it.toEntity() })
            // بث النسخة الحديثة بعد التحديث:
            emit(Resource.Success(data = freshArticles.map { it.toDomain() }, isStale = false))
        } catch (e: Exception) {
            // لو فشلت الشبكة، يظل المستخدم يشاهد بيانات الكاش مع تنبيه خفيف:
            if (cachedArticles.isEmpty()) {
                emit(Resource.Error(e.message ?: "Network error"))
            }
        }
    }
}
```

## Why it matters and how it works

Cache validity depends on TTL, server validators such as ETag, invalidation events and per-record versioning. Network-first needs a bounded deadline and offline fallback. Stale-while-revalidate needs one local source of truth so remote result does not race a separate UI channel.

## Worked example

Conceptual repository contract; caller observes Room and asks for refresh separately.

```kotlin
import kotlinx.coroutines.flow.Flow

interface FeedCache {
    fun observe(): Flow<CachedFeed> // includes fetchedAt and stale flag
    suspend fun refreshIfNeeded(force: Boolean = false)
}
// Remote refresh writes Room transactionally; UI does not merge two lists.
```

## Trade-offs and decision criteria

Cache-first is fast and economical; network-first favors freshness at latency cost; stale-while-revalidate improves perceived speed but can briefly show outdated data. For security-critical or financial status, verify current server authority before committing an action.

## Failure modes

A timestamp-only TTL can be wrong after clock changes; use server validators/versions where possible. Showing old stock or price as current can mislead users. Concurrent refreshes can arrive out of order and overwrite newer cache without version checks.

## Production perspective

A news feed displays cached stories immediately with an updated-at label and refreshes in background. Checkout price instead requests a fresh server quote with expiry and cannot transact on stale cached price.

## Interview answer — short

Cache-First returns local storage data first and hits the network only on cache misses, maximizing speed and battery life. Network-First attempts remote fetching first for guaranteed freshness, falling back to cache when offline. Stale-While-Revalidate serves local cache immediately for instantaneous rendering while asynchronously updating the database from the network.

## Interview answer — structured

Selecting between caching strategies depends on the latency tolerances and data volatility of each feature.
First, Cache-First checks local storage before the network. If cached data is present within its validity window, the request completes without radio activity. It is ideal for static dictionaries and application configurations where speed and offline availability take precedence over real-time accuracy.
Second, Network-First attempts remote API communication first to guarantee absolute data freshness. If the request encounters a socket timeout or cellular failure, it falls back to cached records. This pattern is indispensable for volatile financial balances and checkout steps.
Third, Stale-While-Revalidate delivers the optimal mobile user experience. It emits cached records instantly so the user sees populated layouts immediately, then fetches fresh data in the background and updates the local database, streaming the refreshed state to the UI without blocking spinners.

## Interview answer — deep senior

In high-scale Android engineering, choosing a caching strategy directly dictates user-perceived performance, server load, and battery consumption.
Network-First creates a poor experience on volatile 4G and 5G connections. When an app blocks UI rendering awaiting an HTTP response, high packet loss induces multi-second spinners even when ninety percent of the data has not changed since the last launch.
Conversely, Stale-While-Revalidate eliminates perceived latency entirely. By observing Room via Kotlin Flow, the presentation layer renders locally cached entities within five milliseconds of process start.
Under the hood, the repository launches an asynchronous network revalidation task.
To prevent redundant backend traffic, we combine SWR with HTTP conditional requests using ETags and If-None-Match headers.
When the background worker contacts the server, receiving a 304 Not Modified status confirms the local cache remains valid without transmitting duplicate JSON payloads.
For financial applications, we enforce hybrid strategies: the transaction history list uses Stale-While-Revalidate for smooth scrolling, whereas the available balance endpoint enforces Network-First with strict 5-second timeouts, ensuring money is never spent against stale ledger states.
Additionally, we enforce Time-To-Live expiration policies in Room, purging entries older than thirty days via background WorkManager cleanups to prevent unbounded database bloat.
Finally, we coordinate the UI state with network monitors, displaying subtle offline banners when SWR serves cached data without connectivity, giving users full operational transparency.

## How to answer in the interview

- **Why:** Cache policy is a product correctness choice, not only call order.
- **How:** Contrast first render and refresh behavior of all three strategies.
- **Trade-offs:** Set tolerated age per feature and bound network-first wait.
- **Failure cases:** Hidden stale balance or older response overwriting newer rows.
- **Production solution:** Use freshness/version metadata and retain last-good data on failure.

## Deep-dive talking points

Define TTL/ETag/version, out-of-order refresh and stale-action safety.

## Follow-up questions

- **Interviewer:** "How does HTTP Cache-Control header support stale-while-revalidate natively?"
  **Answer:** "Via the `stale-while-revalidate=<seconds>` directive in HTTP Cache-Control, supported natively by OkHttp Cache when configured with valid cache headers."

- **Interviewer:** "What is the primary risk of Cache-First with an infinite TTL?"
  **Answer:** "The user may never receive updates if the app fails to invalidate or delete the cached file."

## Self-check rubric

Can I choose all three by domain, label stale data and prevent old refresh overwrite?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — cached local reads and refresh.
- [HTTP Semantics RFC 9110](https://httpwg.org/specs/rfc9110.html) — conditional request semantics.

Technically reviewed against primary documentation on 2026-10-13.
