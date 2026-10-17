---
id: "DAT-17"
question: "How do you manage caching expiration and invalidation?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "B"
phase: 3
priority: "P1"
order: 274
editorial_status: "reviewed"
---

# DAT-17

## Original interview question

How do you manage caching expiration and invalidation?

## What the interviewer evaluates

Set cache expiry and invalidation by data semantics, server validators and session changes.

## Concept and technical explanation

Managing caching expiration and invalidation ensures data freshness while preserving the low-latency and offline benefits of local storage:
- Time-To-Live (TTL) & Expiration Windows: Caches attach ingestion timestamps to persisted records. When accessed, the repository compares the record's age against predefined freshness bounds. Expired data either forces a synchronous network refresh or triggers a background fetch while returning stale data temporarily.
- Conditional HTTP Validation: Leverages HTTP headers (ETag, Last-Modified, and Cache-Control) via OkHttp Cache. When a cached resource becomes stale, OkHttp dispatches an If-None-Match or If-Modified-Since validation request. If the backend resource is unchanged, the server responds with HTTP 304 Not Modified without a response payload, refreshing the local TTL without network data overhead.
- Event-Driven Remote Invalidation: Uses server-pushed events (Firebase Cloud Messaging silent data notifications or WebSockets) to explicitly evict or refresh stale client records immediately upon server-side mutations.
- Mutation-Triggered Invalidation: Local write operations (POST, PUT, DELETE) immediately invalidate corresponding cached query results or update local Room entities directly.
- Cache Eviction Policies: Enforces size-bounded storage eviction (such as Least Recently Used - LRU) and schedules periodic Room cleanup jobs via WorkManager to purge historical records and prevent database bloat.

## Practical walkthrough (English)

Cache manager coordinating TTL validation and ETag HTTP caching:
```kotlin
@Entity(tableName = "products")
data class ProductEntity(
    @PrimaryKey val id: String,
    val name: String,
    val price: Double,
    val cachedAt: Long = System.currentTimeMillis()
)

class ProductRepository(
    private val dao: ProductDao,
    private val api: ProductApi,
    private val maxAgeMillis: Long = 10 * 60 * 1000L // 10 minutes TTL
) {
    fun getProduct(id: String): Flow<Product> = flow {
        val cached = dao.getById(id)
        val isExpired = cached == null || (System.currentTimeMillis() - cached.cachedAt) > maxAgeMillis

        if (cached != null) {
            emit(cached.toDomain())
        }

        if (isExpired) {
            runCatching {
                val fresh = api.fetchProduct(id)
                dao.insert(fresh.toEntity(cachedAt = System.currentTimeMillis()))
            }
        }
    }

    // Invalidation on mutation
    suspend fun updateProduct(product: Product) {
        api.updateProduct(product)
        dao.insert(product.toEntity(cachedAt = System.currentTimeMillis()))
    }
}
```

## Explanation in Arabic

كيف تدير انتهاء صلاحية الكاش (Caching Expiration) وإبطاله (Invalidation) في تطبيقات Android؟

1. الفرق بين انتهاء الصلاحية والإبطال (Expiration vs. Invalidation):
   - **Expiration (انتهاء الصلاحية الزمني - Time-based TTL)**: تحديد مدة بقاء البيانات صالحة في الكاش (Time-To-Live). بعد مرور 10 دقائق مثلاً، تعتبر البيانات Stale وتتطلب إعادة طلبها من السيرفر.
   - **Invalidation (الإبطال الفوري المبني على الأحداث - Event-driven Invalidation)**: مسح أو تفريغ الكاش فوراً نتيجة لحدث معين (مثل قيام المستخدم بتسجيل الخروج Logout، أو تعديل الملف الشخصي، أو استلام Push Notification من السيرفر تفيد بتغير البيانات).

2. استراتيجيات إدارة الصلاحية حسب طبيعة البيانات:
   - **بيانات ثابتة (Static Assets / Lookup tables)**: TTL طويل جداً (أيام أو أسابيع).
   - **بيانات متغيرة متوسطة (News / Products Feed)**: TTL يتراوح بين 5 إلى 15 دقيقة مع دعم Stale-While-Revalidate.
   - **بيانات مالية وحساسة (Account Balance / Rights Entitlements)**: TTL صفر (No-Cache)، تتطلب دائماً فحص السيرفر أو استخدام ETag `If-None-Match`.

3. آليات الإبطال الصارمة (Strict Invalidation Rules):
   - **عند تسجيل الخروج (Logout / Account Switch)**: يجب إفراغ جميع جداول الـ Room والـ DataStore المرتبطة بالمستخدم لمنع تسريب بياناته للمستخدم التالي.
   - **عند العمليات المحلية (Local Mutations)**: إذا قام المستخدم بحذف عنصر من السلة، يتم إبطال وحذف العنصر من Room فوراً دون انتظار استجابة السيرفر.

## Practical walkthrough

إدارة انتهاء صلاحية الكاش عبر TTL زمني وترويسات ETag في الـ Repository:
```kotlin
class CachedFeedRepository @Inject constructor(
    private val feedDao: FeedDao,
    private val feedApi: FeedApiService,
    private val metaStore: CacheMetadataStore
) {
    private val CACHE_TTL_MS = TimeUnit.MINUTES.toMillis(15) // صلاحية 15 دقيقة

    fun observeFeed(): Flow<List<FeedItem>> = feedDao.observePosts()

    suspend fun refreshFeedIfExpired(forceRefresh: Boolean = false) {
        val lastFetchTime = metaStore.getLastFetchTime()
        val isExpired = System.currentTimeMillis() - lastFetchTime > CACHE_TTL_MS

        if (isExpired || forceRefresh) {
            val savedETag = metaStore.getFeedETag()
            // إرسال ETag للتحقق مما إذا كان السيرفر قد غير البيانات:
            val response = feedApi.fetchFeed(ifNoneMatch = savedETag)
            
            if (response.code() == 304) {
                // 304 Not Modified: البيانات لم تتغير على السيرفر! نجدد الـ TTL فقط ونوفر الباندويث:
                metaStore.saveLastFetchTime(System.currentTimeMillis())
            } else if (response.isSuccessful && response.body() != null) {
                // 200 OK: بيانات جديدة، نحفظها في Room ونحدث الـ ETag:
                feedDao.replaceFeed(response.body()!!.items)
                metaStore.saveFeedETag(response.headers()["ETag"])
                metaStore.saveLastFetchTime(System.currentTimeMillis())
            }
        }
    }
}
```

## Why it matters and how it works

Use monotonic elapsed time for in-process scheduling and persisted server timestamps/validators carefully across reboot and clock changes. HTTP cache headers can govern transport cache, while Room application cache needs its own invalidation policy. Generation/version checks prevent late old refresh from overwriting a newer row.

## Worked example

Conceptual cache metadata; version is a server token, not a client clock.

```kotlin
data class CachedRow<T>(
    val value: T,
    val serverVersion: String,
    val fetchedAtEpochMs: Long,
)
fun isExpired(row: CachedRow<*>, nowEpochMs: Long, ttlMs: Long): Boolean =
    nowEpochMs - row.fetchedAtEpochMs >= ttlMs
// Also invalidate on mutation/session switch and revalidate with server version.
```

## Trade-offs and decision criteria

TTL is simple and available offline but can be wrong after device clock changes. Server validators reduce payload but need endpoint support. Push invalidation is timely but unreliable during disconnect, so periodic/reconnect revalidation remains necessary.

## Failure modes

A cache keyed only by URL can leak prior user data after account switch. A late response for old version can overwrite new state. Relying on push notifications alone misses updates while offline. Treat unknown freshness as stale rather than silently fresh.

## Production perspective

A catalog caches pages with server versions and fetchedAt, revalidates on app foreground/reconnect, and invalidates edited items immediately. Checkout asks the server for a fresh quote with expiry before payment. Metrics track cache hit rate and stale age.

## Interview answer — short

Managing cache expiration and invalidation requires pairing client-side Time-To-Live policies with server-driven conditional headers and event triggers. Room entities record ingestion timestamps for expiration checks, OkHttp utilizes ETags and 304 responses to eliminate redundant payloads, and Firebase Cloud Messaging pushes trigger targeted eviction of stale local records.

## Interview answer — structured

Managing cache freshness and invalidation effectively balances immediate offline responsiveness against data staleness across several complementary mechanisms.
First, client-side Time-To-Live policies store expiration timestamps alongside Room entities, allowing repositories to determine whether cached data can be served directly or requires a network refresh.
Second, HTTP conditional validation utilizes ETags and Last-Modified headers in OkHttp. When the client issues a request with If-None-Match, a 304 Not Modified response validates that the local cache remains pristine without redownloading JSON bodies.
Third, event-driven invalidation leverages silent push notifications via Firebase Cloud Messaging or WebSockets to instantly purge stale resources upon backend changes.
Fourth, automated eviction policies employ periodic WorkManager background tasks to prune expired, non-favorited records from SQLite, preventing unconstrained disk bloat.

## Interview answer — deep senior

A robust caching architecture requires a unified strategy spanning the HTTP transport layer, local SQLite persistence, and real-time backend synchronization.
At the HTTP layer, we configure OkHttp's disk cache with strict size limits and integrate conditional requests using ETags and Cache-Control directives.
When a repository requests data, OkHttp evaluates Cache-Control headers; if stale, it transmits an If-None-Match header, allowing the server to emit an empty 304 Not Modified status that preserves battery and bandwidth.
At the persistence layer, Room models incorporate a cachedAt timestamp.
When reading from the repository, our business logic checks this timestamp against screen-specific Time-To-Live thresholds: five minutes for live commerce inventory versus twenty-four hours for static category taxonomies.
However, relying purely on polling or passive TTL is insufficient for enterprise applications where remote mutations must reflect immediately.
To achieve real-time accuracy, we implement event-driven cache invalidation: when a product price or user permission updates on the backend, a high-priority silent push notification dispatches through Firebase Cloud Messaging.
The background receiver catches the notification, extracts the affected entity IDs, and executes an atomic Room deletion or background sync.
Finally, to prevent storage leaks on budget devices, a daily WorkManager job evicts unreferenced cache rows older than thirty days.

## How to answer in the interview

- **Why:** Freshness is domain-specific and account-specific.
- **How:** Distinguish HTTP validators from Room metadata and invalidation.
- **Trade-offs:** Show stale low-risk content, revalidate sensitive actions.
- **Failure cases:** Clock-skew TTL, old response overwrite, cross-account cache leak.
- **Production solution:** Version checks, account partitioning and explicit stale UI.

## Deep-dive talking points

Define per-domain max age, account partitioning, validators and race-safe refresh.

## Follow-up questions

- **Interviewer:** "What is the advantage of HTTP 304 Not Modified?"
  **Answer:** "It informs the client that the cached data is still valid without re-transmitting the HTTP response payload, saving battery and cellular data."

- **Interviewer:** "Why shouldn't you delete cached data immediately when a TTL expires?"
  **Answer:** "Keep the stale data to support offline viewing; mark it as stale and attempt a revalidation, falling back to stale content if the network fails."

## Self-check rubric

Can I set freshness by domain, invalidate session data and handle out-of-order updates?

## References and reviewed-on date

- [HTTP Semantics RFC 9110](https://httpwg.org/specs/rfc9110.html) — conditional requests.
- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — cache freshness.

Technically reviewed against primary documentation on 2026-10-13.
