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

Cache-First serves local data immediately and hits network only on misses/expiry, ideal for static data. Network-First attempts server calls first and falls back to cache on failure, ideal for financial balances. Stale-While-Revalidate displays cached data instantly while silently fetching fresh data in the background, offering the ideal UX for feeds and media.

## Interview answer — structured

Choosing between caching strategies depends on the latency versus freshness tolerance of the data.

First, with Cache-First, queries local storage first. If valid, returns immediately without network access; fetches from remote only on cache miss or expiration. Optimal for static, low-churn assets (country code lists, user avatar images, feature configurations). Next, with Network-First, prioritizes server freshness by querying the API first; falls back to local cache only when offline or during socket timeouts. Mandatory for mission-critical, volatile state where serving stale information causes real-world harm (bank account balances, stock prices, payment settlement confirmations).
Finally, a Stale-While-Revalidate (SWR) is the gold standard for modern mobile user experience. Emits cached data from Room in single-digit milliseconds so the user sees content immediately, while concurrently firing a background network request. Once the remote response returns, Room is updated, seamlessly animating fresh items into view. Perfect for news feeds, social timelines, and product catalogs.


## Interview answer — deep senior

When implementing Stale-While-Revalidate in production, senior engineers address the **List Jump UX Defect**.

If a user is actively reading item #3 in a cached list, and the background revalidation completes 2 seconds later, prepending 5 new items to the top of the list will cause the screen to jump violently, disorienting the user.

To solve this in Jetpack Compose and RecyclerView.

First, implement **DiffUtil / stable item keys** (`key(article.id)` in Compose). Finally, for dynamic feeds, buffer new background arrivals behind a subtle UI pill: '5 new posts available - Tap to refresh', giving the user control over when the UI layout recalculates.


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
