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

Manage cache expiration using domain-specific TTLs paired with HTTP conditional validation (ETags / If-None-Match returning 304 Not Modified). Invalidate caches proactively upon user mutations, FCM push invalidations, and enforce immediate database purges on logout or user switching.

## Interview answer — structured

A comprehensive caching strategy separates time-based expiration from event-driven invalidation:

1. **Time-To-Live (TTL) Expiration**:
   - Different domains demand different freshness thresholds: user avatars (7 days), catalog feed (15 minutes), account balances (0 seconds / always revalidate).
   - Leverage **HTTP Conditional Requests**: Store server `ETag` or `Last-Modified` headers. When the TTL expires, issue a lightweight `If-None-Match` request. If unchanged, the server returns **`304 Not Modified`** with an empty body, saving mobile bandwidth while refreshing the TTL.

2. **Event-Driven Invalidation**:
   - **Local Write Invalidation**: When a user updates their profile, the repository immediately mutates Room, ensuring UI screens observe fresh state without waiting for a TTL cycle.
   - **Remote Server Invalidation**: Use high-priority FCM Silent Push notifications to instruct clients to invalidate specific cache keys when backend data updates.
   - **Session Purges**: On `Logout` or account switching, execute an atomic SQLite wipe (`database.clearAllTables()`) to prevent data leaking between users.

## Interview answer — deep senior

A subtle pitfall in Android caching is **Clock Skew with Device Time**.

If a developer calculates expiration using `System.currentTimeMillis()` (`now - lastFetched > TTL`), and the user manually alters device time or travels across time zones, the cache may appear permanently expired or permanently fresh.

To prevent clock skew bugs:
- Use **`SystemClock.elapsedRealtime()`** for in-session relative cache calculations (which counts milliseconds since device boot, immune to user time adjustments).
- For persistent multi-day caches, rely on the server's HTTP `Date` header to calculate relative age rather than trusting the Android hardware clock.

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
