"""
Elevation script for DAT questions: DAT-08 to DAT-15.
Topic: Networking, Room, DataStore & Offline-First (DAT)
Phase 4, Batch 2
"""

import os
import sys

sys.path.insert(0, os.path.abspath("scripts/elevations"))
import elevation_engine as ee

TOPIC_AR = "الشبكات وقواعد بيانات Room والـ DataStore والتخزين المحلي"
REVIEWED_DATE_AR = "تمت المراجعة والتحقق في 17 أكتوبر 2026"

DATA = {}

# ==========================================
# DAT-08: What are cache-first, network-first, and stale-while-revalidate strategies?
# ==========================================
DATA["DAT-08"] = {
    "concept_en": """Data caching strategies govern the trade-off between latency, freshness, and network bandwidth in mobile architectures:
- Cache-First (Cache-Only with Fallback): Queries local storage first. If valid data exists, it returns immediately without issuing a network request. The network is contacted exclusively when cache is missing or expired. Ideal for static reference data like country codes, app feature flags, and localized product categories. Minimizes network requests and maximizes battery efficiency, but risks presenting stale data if Time-To-Live (TTL) is misconfigured.
- Network-First (Network with Cache Fallback): Issues an HTTP request to the remote backend first. Upon receiving a successful response, it updates the local cache and emits the fresh data. If the network request fails due to offline connectivity, timeouts, or 5xx server errors, it falls back to local cached data. Ideal for real-time mission-critical information like bank account balances, live stock prices, and ticket inventory. Guarantees absolute freshness when online, but incurs network latency on every screen opening and degrades perceived speed on poor cellular connections.
- Stale-While-Revalidate (SWR): Returns cached data immediately to provide instantaneous zero-latency UI rendering, while concurrently triggering an asynchronous background network request. Once the fresh network payload arrives, it persists to the local database, which automatically emits the updated snapshot to the UI via reactive Flow streams. Ideal for social feeds, news streams, and product catalogs, balancing instant perceived responsiveness with eventual consistency.""",
    "walkthrough_en": """Implementing Cache-First, Network-First, and Stale-While-Revalidate repository patterns:
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
```""",
    "short_en": """Cache-First returns local storage data first and hits the network only on cache misses, maximizing speed and battery life. Network-First attempts remote fetching first for guaranteed freshness, falling back to cache when offline. Stale-While-Revalidate serves local cache immediately for instantaneous rendering while asynchronously updating the database from the network.""",
    "structured_en": """Selecting between caching strategies depends on the latency tolerances and data volatility of each feature.
First, Cache-First checks local storage before the network. If cached data is present within its validity window, the request completes without radio activity. It is ideal for static dictionaries and application configurations where speed and offline availability take precedence over real-time accuracy.
Second, Network-First attempts remote API communication first to guarantee absolute data freshness. If the request encounters a socket timeout or cellular failure, it falls back to cached records. This pattern is indispensable for volatile financial balances and checkout steps.
Third, Stale-While-Revalidate delivers the optimal mobile user experience. It emits cached records instantly so the user sees populated layouts immediately, then fetches fresh data in the background and updates the local database, streaming the refreshed state to the UI without blocking spinners.""",
    "deep_senior_en": """In high-scale Android engineering, choosing a caching strategy directly dictates user-perceived performance, server load, and battery consumption.
Network-First creates a poor experience on volatile 4G and 5G connections. When an app blocks UI rendering awaiting an HTTP response, high packet loss induces multi-second spinners even when ninety percent of the data has not changed since the last launch.
Conversely, Stale-While-Revalidate eliminates perceived latency entirely. By observing Room via Kotlin Flow, the presentation layer renders locally cached entities within five milliseconds of process start.
Under the hood, the repository launches an asynchronous network revalidation task.
To prevent redundant backend traffic, we combine SWR with HTTP conditional requests using ETags and If-None-Match headers.
When the background worker contacts the server, receiving a 304 Not Modified status confirms the local cache remains valid without transmitting duplicate JSON payloads.
For financial applications, we enforce hybrid strategies: the transaction history list uses Stale-While-Revalidate for smooth scrolling, whereas the available balance endpoint enforces Network-First with strict 5-second timeouts, ensuring money is never spent against stale ledger states.
Additionally, we enforce Time-To-Live expiration policies in Room, purging entries older than thirty days via background WorkManager cleanups to prevent unbounded database bloat.
Finally, we coordinate the UI state with network monitors, displaying subtle offline banners when SWR serves cached data without connectivity, giving users full operational transparency.""",
    "meta_ar": {
        "id": "DAT-08",
        "questionAr": "ما هي استراتيجيات التخزين المؤقت: الكاش أولاً (Cache-First)، والشبكة أولاً (Network-First)، والكاش المؤقت مع التحديث الخلفي (Stale-While-Revalidate)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على الموازنة بين سرعة الاستجابة اللحظية وحداثة البيانات، واختيار استراتيجية الكاش المناسبة بحسب طبيعة الشاشة واستهلاك باقة الإنترنت وموارد البطارية.",
        "concept_ar": "تحدد استراتيجيات الكاش المعادلة الهندسية بين زمن الاستجابة وحداثة البيانات: استراتيجية 'الكاش أولاً' (Cache-First) تفحص التخزين المحلي أولاً وتعيد البيانات فوراً إذا كانت صالحة، ولا تلجأ للشبكة إلا عند غياب الكاش؛ وتناسب البيانات شبه الثابتة كقوائم الدول والإعدادات. واستراتيجية 'الشبكة أولاً' (Network-First) ترسل طلب HTTP للسيرفر أولاً لجلب أحدث البيانات وتحديث الكاش، ولا تعود للكاش إلا عند انقطاع الاتصال أو تعطل السيرفر؛ وتناسب البيانات الحساسة كالأرصدة المصرفية ومخزون التذاكر. أما استراتيجية 'الكاش المؤقت مع التحديث الخلفي' (Stale-While-Revalidate) فتعرض الكاش القديم فوراً للواجهة لمنع ظهور مؤشرات التحميل، وتطلق طلباً في الخلفية لجلب البيانات الحديثة وتحديث قاعدة البيانات وبثها عبر Flow؛ وتعتبر الأفضل لمعظم شاشات الموبايل كقوائم الأخبار والمنتجات.",
        "walkthrough_ar": """تطبيق استراتيجيات الكاش الثلاث في طبقة المستودع:
```kotlin
// 1. الكاش أولاً للبيانات الثابتة
fun getCountries(): Flow<List<Country>> = flow {
    val cached = countryDao.getAll()
    if (cached.isNotEmpty()) {
        emit(cached)
    } else {
        val fresh = api.getCountries()
        countryDao.insertAll(fresh)
        emit(fresh)
    }
}

// 2. الكاش المؤقت مع التحديث الخلفي (SWR) للشاشات السريعة
fun getFeed(): Flow<List<FeedItem>> = flow {
    // عرض الكاش القديم فوراً بلا تأخير
    val local = feedDao.getItems()
    if (local.isNotEmpty()) emit(local)

    // جلب التحديث في الخلفية بهدوء
    runCatching {
        val remote = api.getFeed()
        feedDao.updateFeed(remote)
    }
}
```""",
        "why_it_matters_ar": "يحدد سرعة فتح شاشات التطبيق أمام المستخدم؛ فاختيار النمط المناسب يقضي على شاشات التحميل المزعجة ويوفر استهلاك البطارية وباقة الإنترنت ويضمن العمل بسلاسة في ظروف الشبكة السيئة.",
        "worked_example_ar": "استخدام Cache-First لشاشة اختيار الدولة ولغة التطبيق، واستخدام Network-First مع مهلة 5 ثوانٍ لشاشة تحويل الأموال والتحقق من الرصيد، واستخدام SWR لشاشة تصفح المنتجات في متجر إلكتروني.",
        "trade_offs_ar": "توفر Cache-First سرعة فائقة ولكنها قد تعرض بيانات قديمة، وتضمن Network-First دقة تامة ولكنها تبطئ فتح الشاشات وتفشل بدون اتصال، بينما تحقق SWR تجربة مستخدم مثالية على حساب كتابة كود مزامنة إضافي.",
        "failure_modes_ar": "استخدام Network-First لشاشات المحتوى اليومي مما يجعل التطبيق بطيئاً جداً في كل مرة يفتحه المستخدم، أو استخدام Cache-First بدون تاريخ انتهاء صلاحية TTL مما يجمد البيانات القديمة للأبد.",
        "production_perspective_ar": "في التطبيقات الضخمة، نعتمد SWR كنمط افتراضي لأكثر من ثمانين بالمئة من الشاشات، وندمج معه ترويسات ETag و If-None-Match لتقليل استهلاك السيرفر عند عدم وجود تعديلات.",
        "how_to_answer_ar": "عرف كل استراتيجية باختصار موضحاً اتجاه تدفق البيانات، ثم اذكر السيناريو المثالي لكل نمط، وركز على أفضلية Stale-While-Revalidate في واجهات الهواتف المحمولة وتكاملها مع Flow.",
        "talking_points_ar": "مفهوم التحديث الخلفي في SWR، تكلفة فتح مودم الشبكة في Network-First، وأهمية تحديد مدة الصلاحية TTL لحماية الكاش من التقادم.",
        "follow_ups_ar": "- **المحاور:** 'كيف تمنع استهلاك باقة الإنترنت مع استراتيجية SWR عند فتح الشاشة بشكل متكرر؟'\n  **المرشح:** 'باستخدام ترويسات ETag و 304 Not Modified؛ فيرسل السيرفر رداً فارغاً يؤكد صحة الكاش المحلي دون إعادة تنزيل البيانات ثانية.'\n\n- **المحاور:** 'لماذا لا نستخدم Network-First في الصفحة الرئيسية للتطبيق؟'\n  **المرشح:** 'لأنها تجبر المستخدم على مشاهدة شاشة تحميل بيضاء لثوانٍ مع كل فتح للتطبيق، وتفشل تماماً إذا كانت الشبكة متقلبة، بينما يعرض SWR المحتوى في 5 ملي ثوانٍ.'",
        "self_check_ar": "هل شرحت الفروق بين الأنماط الثلاثة بدقة؟ وهل بينت لماذا تعتبر SWR هي الخيار الأفضل لمعظم شاشات الموبايل؟",
        "references_ar": f"- [Android Architecture: Offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first) — إرشادات جوجل لطبقة البيانات والكاش.\n- [HTTP Caching and SWR Specification](https://web.dev/stale-while-revalidate/) — دليل معايير التخزين المؤقت وحداثة البيانات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تعتمد استراتيجية الكاش أولاً على قراءة التخزين المحلي وتتصل بالشبكة عند غياب الكاش للبيانات الثابتة. وتعتمد الشبكة أولاً على جلب البيانات الحية أولاً وتلجأ للكاش كبديل عند الانقطاع للمعلومات المالية الحساسة. بينما تقدم Stale-While-Revalidate الكاش القديم فوراً لتجاوب الشاشة بلحظتها وتحدث البيانات بالخلفية بهدوء.",
        "best_answer_ar": "تحدد استراتيجيات التخزين المؤقت التوازن الهندسي الدقيق بين سرعة استجابة الشاشة وحداثة البيانات المعروضة للمستخدم.\n\nاستراتيجية الكاش أولاً Cache-First تضع التخزين المحلي كوجهة أولى؛ فإذا كانت البيانات موجودة وسارية المفعول، تُعرض فوراً دون تشغيل مودم الهاتف وتوفيراً للباقة والبطارية، وتقتصر على جلب الشبكة عند خلو الكاش، وهي مثالية لقوائم الدول والعملات وإعدادات التطبيق الثابتة.\n\nاستراتيجية الشبكة أولاً Network-First تعكس الأولويات؛ حيث تحاول الاتصال بالسيرفر أولاً لجلب أحدث حالة للبيانات، ولا تستخدم الكاش المحلي إلا كحزام أمان أخير عند انقطاع الاتصال أو فشل الخادم، وهي إلزامية للمعلومات اللحظية الخطرة كأرصدة الحسابات البنكية وحجز المقاعد.\n\nأما استراتيجية الكاش مع التحديث الخلفي Stale-While-Revalidate، فهي المعيار الذهبي لتطبيقات الموبايل الحديثة؛ حيث تبث البيانات المخزنة محلياً في بضع ملي ثوانٍ لتظهر الشاشة فوراً دون أي مؤشرات انتظار، وفي ذات الوقت تطلق طلباً غير متزامن في الخلفية لتحديث قاعدة البيانات، مما يمنح المستخدم سرعة فائقة وحداثة مستمرة للبيانات.",
        "deep_answer_ar": "في قيادة هندسة المنصات لتطبيقات أندرويد الضخمة، يعتبر اختيار استراتيجية الكاش الخاطئة سبباً رئيسياً لشكاوى المستخدمين من بطء التطبيق واستهلاك باقة الإنترنت والبطارية.\n\nإن الاعتماد على استراتيجية Network-First في الشاشات الرئيسية يمثل خطأ معمارياً فادحاً؛ فشبكات المحمول تتسم بالتقلب وارتفاع زمن الوصول Latency، وإجبار المستخدم على انتظار رد السيرفر لرؤية الشاشة يخلق تجربة استخدام سيئة حتى لو كانت البيانات مطابقة لآخر تصفح. لذلك نوجه الفرق الهندسية لاعتماد نمط Stale-While-Revalidate كخيار قياسي في طبقة الـ Repository؛ حيث تقرأ الشاشة من Room عبر Flow فورياً، وتتولى الكوروتينز إرسال استعلام خلفي لتحديث القاعدة.\n\nولحماية خوادمنا من الضغط الناتج عن استعلامات SWR المتكررة، ندمجها مع تقنيات HTTP Caching الذكية باستخدام معرفات ETags؛ فعندما يرسل التطبيق ترويسة If-None-Match، يرد السيرفر بكود 304 Not Modified دون إرسال محتوى الـ JSON إذا لم تتغير البيانات، مما يوفر تسعين بالمئة من استهلاك البيانات.\n\nوفي المقابل، نقتصر في استخدام Network-First على نقاط النهاية الحساسة للغاية مثل تأكيد سحب الرصيد مع وضع مهل زمنية صارمة لا تتجاوز خمس ثوانٍ، مع تطبيق سياسات تنظيف دورية في قواعد بيانات Room لحذف السجلات القديمة عبر WorkManager لحماية مساحة تخزين الهاتف. وأخيراً، نقوم بربط واجهة المستخدم بمراقب حالة الشبكة لإظهار تنبيه بصري هادئ يوضح للمستخدم أن البيانات المعروضة مأخوذة من الذاكرة المؤقتة أثناء انقطاع الاتصال، مما يحقق أعلى درجات الشفافية التشغيلية وسلاسة الاستخدام."
    }
}

# ==========================================
# DAT-09: How do you implement authentication interceptors and refresh-token logic safely?
# ==========================================
DATA["DAT-09"] = {
    "concept_en": """Safe implementation of authentication and token refresh in OkHttp requires separating token injection from 401 error recovery:
- Application Auth Interceptor: Intercepts outgoing requests to attach the current access token to the HTTP Authorization header (e.g., Bearer <token>). It identifies public, unauthenticated endpoints (such as login or registration) via custom OkHttp Request Tags and permits them to proceed without authorization headers.
- OkHttp Authenticator Interface: Specifically designed to handle HTTP 401 Unauthorized responses. Unlike a standard interceptor, Authenticator is invoked exclusively upon authentication failure. It handles token renewal synchronously or delegates to a thread-safe token manager, rebuilds the original request with the fresh credential, and returns it to OkHttp for automatic transparent replay.
- Infinite 401 Loop Prevention: If credentials are fundamentally invalid or the refresh token is revoked, a poorly designed Authenticator can recursively loop forever. Robust implementations inspect the response chain (responseCount(response) >= 2) or verify whether the failed request already carried the newest token. If so, it returns null to abort the call, clears local session storage, and broadcasts a global logout event to navigate the user to the login screen.""",
    "walkthrough_en": """Production-grade token refresh implementation using OkHttp Authenticator:
```kotlin
// 1. Interceptor attaching current access token
class AuthHeaderInterceptor(
    private val tokenStorage: TokenStorage
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val original = chain.request()
        val token = tokenStorage.getAccessToken()
        return if (token != null && original.header("Authorization") == null) {
            val authenticated = original.newBuilder()
                .header("Authorization", "Bearer $token")
                .build()
            chain.proceed(authenticated)
        } else {
            chain.proceed(original)
        }
    }
}

// 2. Authenticator handling 401 and token renewal
class TokenAuthenticator(
    private val tokenManager: TokenManager
) : Authenticator {
    override fun authenticate(route: Route?, response: Response): Request? {
        // Prevent infinite loops: abort if we already retried this request twice
        if (responseCount(response) >= 2) return null

        // Coordinate thread-safe single-flight refresh
        val freshToken = tokenManager.refreshTokenSynchronously(response.request.header("Authorization"))
            ?: return null // Refresh failed or session revoked; abort and trigger logout

        // Replay original request with the new access token
        return response.request.newBuilder()
            .header("Authorization", "Bearer $freshToken")
            .build()
    }

    private fun responseCount(response: Response): Int {
        var count = 1
        var prior = response.priorResponse
        while (prior != null) { count++; prior = prior.priorResponse }
        return count
    }
}
```""",
    "short_en": """Authentication is implemented by combining an application interceptor that injects access tokens into outgoing requests with an OkHttp Authenticator that intercepts 401 responses to refresh tokens. Loop counters prevent infinite retries, and thread-safe managers serialize refresh calls while broadcasting logout events upon revocation.""",
    "structured_en": """Implementing token authentication and refresh logic safely requires separating token attachment from 401 failure handling.
First, an application-level Interceptor inspects outgoing requests and attaches the active JWT access token in the Authorization header. It bypasses public endpoints that do not require credentials.
Second, token renewal is delegated to OkHttp's Authenticator interface rather than a generic interceptor. The Authenticator triggers only when the server responds with HTTP 401 Unauthorized, automatically executing token renewal and returning a new request to be replayed transparently.
Third, we guard against infinite retry loops by checking response.priorResponse. If a request has already failed authentication twice, or if the refresh token itself has expired, the authenticator returns null to cancel the request, purges local session storage, and dispatches a navigation event to the login screen.""",
    "deep_senior_en": """Designing enterprise authentication pipelines requires understanding OkHttp's internal execution architecture and handling edge-case failure modes.
Developers frequently attempt to handle token refresh inside a standard Interceptor.
This is an anti-pattern: interceptors execute for every request and require manual recursive chain calls, complicating error recovery and risking thread starvation.
In contrast, OkHttp's Authenticator interface was specifically engineered for reactive credential challenges.
When a 401 Unauthorized occurs, OkHttp routes execution to Authenticator.authenticate().
Our implementation first checks responseCount(): if prior responses exist and the Authorization header already matches the newly refreshed token, we know the account was revoked or lacked permissions, so we immediately return null to halt the loop.
Under the hood, our TokenManager encapsulates a ReentrantLock to serialize concurrent refresh calls across threads.
When refresh succeeds, we persist the new access and refresh tokens into EncryptedSharedPreferences backed by Android Keystore.
If the auth server rejects the refresh token with a 400 or 401, we treat the session as permanently compromised: we clear local Room user tables, wipe secure storage, and post a SessionExpiredEvent to our UI navigation coordinator to redirect the user to authentication.
Furthermore, we implement an in-flight request buffer to queue concurrent network calls while the refresh transaction executes, preventing duplicate 401 storms and ensuring all paused requests replay seamlessly with the new bearer token.""",
    "meta_ar": {
        "id": "DAT-09",
        "questionAr": "كيف تطبق معترضات المصادقة (Auth Interceptors) ومنطق تجديد الـ Token (Refresh Token) بأمان دون حلقات لا نهائية؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم الفرق بين Interceptor و Authenticator في OkHttp، وتأمين تخزين التوكنز، ومنع الحلقات اللانهائية عند فشل التجديد، وإدارة تسجيل الخروج التلقائي.",
        "concept_ar": "يتطلب التطبيق الآمن لدورة حياة التوكن في OkHttp فصلاً دقيقاً للمهام: استخدام معترض التطبيق (Auth Interceptor) لإرفاق توكن الوصول (Access Token) في ترويسة Authorization لكافة الطلبات الخارجة، مع استثناء نقاط الاتصال العامة كشاشات تسجيل الدخول. وتفويض مهمة التجديد لواجهة Authenticator الخاصة بـ OkHttp؛ حيث تُستدعى حصرياً عند استقبال كود 401 Unauthorized لطلب توكن جديد من السيرفر وإعادة إرسال الطلب الأصلي تلقائياً. ولمنع الحلقات اللانهائية (Infinite 401 Loops)، يفحص الـ Authenticator عدد مرات الفشل السابقة عبر response.priorResponse؛ فإذا تكرر الفشل مرتين أو كان التوكن المرفق هو بالفعل أحدث توكن، يتم إرجاع null لإلغاء المحاولات ومسح الجلسة وتوجيه المستخدم لشاشة تسجيل الدخول.",
        "walkthrough_ar": """بناء متكامل لمعترض التوكن و Authenticator مع حماية الحلقات:
```kotlin
// 1. معترض لإرفاق التوكن في الطلبات
class AuthInterceptor(private val prefs: TokenStorage) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val token = prefs.getAccessToken()
        val request = chain.request().newBuilder().apply {
            if (token != null) header("Authorization", "Bearer $token")
        }.build()
        return chain.proceed(request)
    }
}

// 2. Authenticator لتجديد التوكن عند كود 401
class TokenAuthenticator(private val tokenManager: TokenManager) : Authenticator {
    override fun authenticate(route: Route?, response: Response): Request? {
        // منع الحلقات اللانهائية إذا فشل الطلب أكثر من مرة
        if (response.priorResponseCount() >= 2) return null

        val newToken = tokenManager.refreshTokenSync() ?: return null

        return response.request.newBuilder()
            .header("Authorization", "Bearer $newToken")
            .build()
    }
}
```""",
        "why_it_matters_ar": "يمنع تجمد التطبيق واستهلاك باقة الإنترنت في حلقات إعادة المحاولة اللانهائية عند انتهاء صلاحية الجلسة، ويوفر تجربة تجديد توكن سلسة دون شعور المستخدم بأي انقطاع.",
        "worked_example_ar": "إرسال طلب لجلب بيانات المستخدم؛ يستجيب السيرفر بكود 401 لانتهاء صلاحية التوكن، فيلتقطه TokenAuthenticator، ويطلب توكناً جديداً بالـ Refresh Token، ثم يعيد تنفيذ الطلب بنجاح شفاف.",
        "trade_offs_ar": "استخدام Authenticator يتطلب إدارة تزامن للخيوط وحفظ التوكن في مساحة مشفرة، ولكنه يغنيك عن كتابة معالجة معقدة ويدوية للأخطاء داخل كل دالة API في المشروع.",
        "failure_modes_ar": "تجديد التوكن داخل Interceptor عادي مما يسبب استدعاءات متكررة وفوضى في الخيوط، أو نسيان فحص priorResponse مما يوقع التطبيق في حلقة لا نهائية تفرغ شحن البطارية بالكامل.",
        "production_perspective_ar": "في التطبيقات البنكية، نخزن Refresh Token داخل EncryptedSharedPreferences مدعومة بـ Android Keystore، ونلزم الـ Authenticator بمسح الجلسة فوراً عند فشل التجديد وتوجيه المستخدم لشاشة تسجيل الدخول.",
        "how_to_answer_ar": "اشرح تقسيم المسؤوليات: Interceptor لإضافة التوكن، و Authenticator لمعالجة كود 401، ثم بين تفصيلياً كيف تحمي النظام من الحلقات اللانهائية عبر فحص عدد الردود السابقة priorResponse.",
        "talking_points_ar": "الفارق الجوهري بين Interceptor و Authenticator، دور priorResponse في كسر الحلقات، وكيفية مزامنة تجديد التوكن بين الخيوط المتزامنة.",
        "follow_ups_ar": "- **المحاور:** 'لماذا نستخدم Authenticator بدلاً من كتابة شرط كود 401 داخل Interceptor العادي؟'\n  **المرشح:** 'لأن Authenticator مدمج في نواة OkHttp لإعادة محاولة الطلب تلقائياً دون تكرار سلسلة المعترضات، كما أنه لا يُستدعى إلا عند فشل المصادقة فقط مما يوفر الأداء.'\n\n- **المحاور:** 'ماذا تفعل إذا كان الـ Refresh Token نفسه منتهي الصلاحية؟'\n  **المرشح:** 'يرجع الـ Authenticator قيمة null فوراً لإلغاء أي طلبات معلقة، ويطلق حدث SessionExpiredEvent لمسح قاعدة البيانات المحلية وتوجيه المستخدم لشاشة تسجيل الدخول.'",
        "self_check_ar": "هل وضحت سبب تفضيل Authenticator على Interceptor في كود 401؟ وهل شرحت كيفية منع الـ Infinite Loops بدقة؟",
        "references_ar": f"- [OkHttp Authenticator Documentation](https://square.github.io/okhttp/features/calls/#authenticator) — التوثيق الرسمي لواجهة Authenticator في OkHttp.\n- [OAuth 2.0 Token Refresh Best Practices](https://oauth.net/2/grant-types/refresh-token/) — معايير تجديد التوكن في بروتوكول OAuth 2.0.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تُبنى منظومة المصادقة الآمنة عبر معترض يرفق توكن الوصول في الترويسة لكل طلب، مع واجهة Authenticator متخصصة تلتقط كود 401 لتجديد التوكن وإعادة إرسال الطلب تلقائياً. وتُمنع الحلقات اللانهائية بفحص عدد الردود السابقة قبل التجديد وإلغاء الجلسة ومسحها فوراً عند فشل العملية.",
        "best_answer_ar": "التطبيق الهندسي الآمن لمصادقة المستخدمين وتجديد التوكن في أندرويد يقوم على توزيع دقيق للأدوار بين مكونين رئيسيين في مكتبة OkHttp.\n\nالمكون الأول هو معترض التطبيق AuthInterceptor؛ حيث يفحص كل طلب خارج ويحقن توكن الوصول في ترويسة Authorization بصيغة Bearer Token، مع استثناء طلبات تسجيل الدخول وتسجيل الحساب الجديد التي لا تتطلب مصادقة مسبقة.\n\nالمكون الثاني هو واجهة التوثيق TokenAuthenticator؛ وهي المكون المصمم خصيصاً في OkHttp لمعالجة تحديات المصادقة. فعندما يرفض السيرفر الطلب بكود 401 Unauthorized، يتولى الـ Authenticator اعتراض الاستجابة وإجراء طلب تجديد التوكن عبر Refresh Token، ثم يقوم بتحديث الترويسة بالتوكن الجديد وإرجاع الطلب لتقوم OkHttp بإعادة تنفيذه بشفافية تامة للمستخدم.\n\nولمنع الوقوع في فخ الحلقات اللانهائية Infinite Loops، نقوم بفحص سلسلة الردود السابقة عبر response.priorResponse؛ فإذا لاحظنا أن هذا الطلب قد تم تجديده وفشل بالفعل مرتين، أو إذا كان السيرفر يرفض نفس التوكن الجديد، يرجع الـ Authenticator قيمة null لإيقاف المحاولات، مع إطلاق حدث تسجيل الخروج وتوجيه المستخدم لشاشة الدخول.",
        "deep_answer_ar": "في تصميم منصات أندرويد عالية الأمان، يعتبر التعامل السطحي مع التوكنز ثغرة خطيرة تؤدي إلى انهيار الخوادم واستنزاف بطاريات الهواتف في حلقات استدعاء لا نهائية.\n\nالخطأ الأكثر شيوعاً بين المطورين هو محاولة التقاط كود 401 وتجديد التوكن داخل Interceptor عادي؛ هذا الأسلوب كارثي لأنه يعقد مسار الاستدعاء ويجبر المطور على تكرار سلسلة المعترضات يدوياً مما يسبب استنزاف خيوط المعالجة. البديل المعماري القياسي هو واجهة OkHttp Authenticator التي لا تعمل إلا كمعالج استثنائي عند فشل الاعتماد.\n\nعند دخول الـ Authenticator، نطبق فحصاً صارماً لمنع الحلقات اللانهائية عبر دالة تفحص priorResponseCount؛ فإذا تجاوزت المحاولات مرتين، ندرك أن المشكلة ليست انتهاء صلاحية التوكن بل إلغاء الصلاحيات من لوحة التحكم، فنوقف المحاولات فوراً بإرجاع null. كما نقوم بمطابقة التوكن المرفق في الطلب الفاشل مع التوكن الحالي المخزن في الذاكرة؛ فإذا كانا مختلفين، فهذا يعني أن خيطاً آخر قد أنجز التجديد بالفعل، فنعيد إرسال الطلب بالتوكن الجديد مباشرة دون طلب تجديد ثانٍ.\n\nوعلى الصعيد الأمني، نحفظ الـ Refresh Token داخل EncryptedSharedPreferences مرتبطة بمفاتيح عتادية مشفرة في Android Keystore لمنع استخراجها من الأجهزة المخترقة، وفي حال فشل طلب التجديد واستجابة السيرفر بكود 400 أو 401، نطلق إجراءات مسح شاملة لقواعد بيانات Room المحلية ونوجه المستخدم لتسجيل الدخول لحماية أمان الحساب."
    }
}

# ==========================================
# DAT-10: How do you avoid concurrent refresh-token races?
# ==========================================
DATA["DAT-10"] = {
    "concept_en": """The concurrent refresh-token race condition (also called the Thundering Herd token issue) occurs when multiple parallel network requests fail with HTTP 401 simultaneously:
- The Failure Scenario: When an access token expires while multiple asynchronous coroutines are executing parallel API calls (e.g., loading user profile, notifications count, and dashboard feed concurrently), all requests receive HTTP 401 Unauthorized at nearly the same millisecond.
- Refresh Token Rotation Hazard: Modern OAuth2 servers implement Refresh Token Rotation, where using a refresh token invalidates it and issues a single-use replacement. If all failing requests trigger their own independent refresh calls, the first refresh succeeds and rotates the secret; the remaining four requests then hit the server with the now-invalidated token. The backend interprets this as a token replay attack and revokes the user's entire session, causing an unexpected, frustrating logout.
- The Architectural Solution (Single-Flight Double-Checked Locking):
  1. Synchronized Mutual Exclusion: Synchronize the token refresh block using a Kotlin Coroutines Mutex or ReentrantLock so only a single thread can execute the network refresh at any moment.
  2. Double-Checked Token Inspection: Before executing the refresh network call, inspect whether the access token in memory has already been updated while the current thread was waiting to acquire the lock. If the token in memory differs from the token that failed in the request, skip the network call entirely and immediately replay with the already-refreshed token.
  3. Single-Flight Execution: Only the first thread performs the network refresh; once complete, it updates shared storage and releases the lock. Waiting threads wake up, detect the fresh token via the double-check, and replay their requests without hitting the auth server.""",
    "walkthrough_en": """Thread-safe token manager implementing single-flight double-checked locking:
```kotlin
class SafeTokenManager(
    private val tokenStorage: TokenStorage,
    private val authApi: AuthApiService
) {
    private val refreshLock = Any()

    fun getValidTokenOrRefresh(failedTokenHeader: String?): String? {
        val failedToken = failedTokenHeader?.removePrefix("Bearer ")?.trim()

        synchronized(refreshLock) {
            val currentToken = tokenStorage.getAccessToken()

            // 1. Double-check: If another thread already refreshed the token, return it immediately
            if (currentToken != null && currentToken != failedToken) {
                return currentToken
            }

            // 2. First thread: Perform the actual network refresh
            val refreshToken = tokenStorage.getRefreshToken() ?: return null
            val response = authApi.refreshTokenCall(RefreshTokenRequest(refreshToken)).execute()

            return if (response.isSuccessful && response.body() != null) {
                val newTokens = response.body()!!
                tokenStorage.saveTokens(newTokens.accessToken, newTokens.refreshToken)
                newTokens.accessToken
            } else {
                // Refresh failed or revoked; wipe local session
                tokenStorage.clearTokens()
                null
            }
        }
    }
}
```""",
    "short_en": """Concurrent refresh races occur when multiple parallel requests receive 401 simultaneously, risking session revocation under token rotation. The solution is single-flight double-checked locking: a synchronization lock ensures only one request performs the refresh, while subsequent waiting requests detect the updated token and replay without re-hitting the auth server.""",
    "structured_en": """Preventing concurrent refresh-token races is critical for preserving user sessions in applications with parallel networking.
First, when an access token expires while multiple parallel requests are in flight, all requests fail with 401 at the same time. If each request triggers its own refresh call, the server's Refresh Token Rotation mechanism treats subsequent calls as token theft and revokes the entire user session.
Second, we solve this using single-flight double-checked synchronization. When a 401 reaches the token manager, threads synchronize on a shared lock.
Third, the double-check verifies whether another thread has already refreshed the credentials while the current thread was waiting for the lock. If the current stored token differs from the failed request's token, the thread immediately uses the fresh token without network activity. Only the first thread makes the refresh API call, updating shared state for all waiters.""",
    "deep_senior_en": """In enterprise mobile development, the concurrent refresh race condition is one of the most frustrating sources of phantom user logouts.
When opening a complex dashboard screen, multiple independent repositories launch parallel coroutines to fetch distinct data slices.
If the access token expired two seconds prior, all five requests hit the server, fail with 401, and invoke Authenticator.authenticate() concurrently across thread pool workers.
On backends enforcing strict OAuth2 Refresh Token Rotation, the first refresh request succeeds, updates the database, and invalidates the previous refresh token.
When the other four parallel threads hit the auth endpoint with the invalidated token, the auth server detects a potential replay attack, flags the account as compromised, and revokes all active refresh tokens, forcing the user back to the login screen.
To prevent this catastrophe, we implement single-flight double-checked locking inside our TokenManager.
When Authenticator catches a 401, it passes the failed request's Authorization header into our synchronized manager.
Inside the synchronized critical section, we inspect the active token.
If another worker thread already executed the refresh while we were queued on the lock, the active token will no longer match the failed request's token.
We immediately return the active token, completely bypassing the network call.
Only the thread that arrives first performs the network roundtrip.
Once it succeeds, all queued requests proceed seamlessly with the updated token, reducing five redundant auth network calls to a single atomic roundtrip and completely eliminating session revocation bugs.""",
    "meta_ar": {
        "id": "DAT-10",
        "questionAr": "كيف تتجنب مشكلة السباق المتزامن عند تجديد الـ Token (Concurrent Refresh-Token Races)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم معضلة الـ Thundering Herd وتزامن الخيوط المتعددة، ومخاطر Refresh Token Rotation، وتطبيق نمط Double-Checked Locking لضمان تجديد التوكن لمرة واحدة فقط.",
        "concept_ar": "تحدث مشكلة السباق المتزامن (Concurrent Refresh Race) عندما تنتهي صلاحية توكن الوصول أثناء تنفيذ عدة طلبات متوازية في نفس اللحظة (مثل فتح شاشة رئيسية تجلب الملف الشخصي والإشعارات والمنتجات معاً)، حيث ترجع جميعها بكود 401 في نفس الوقت. وتكمن الكارثة عند تطبيق السيرفر لميزة تدوير التوكن (Refresh Token Rotation) التي تجعل التوكن صالحاً للاستخدام لمرة واحدة فقط؛ فإذا أرسلت الطلبات الخمسة طلبات تجديد مستقلة، ينجح الطلب الأول ويلغي صلاحية الـ Refresh Token، فتصل الطلبات الأربعة التالية بتوكن ملغى، فيعتبرها السيرفر هجوماً أمنياً ويقوم بإلغاء جلسة المستخدم بالكامل وطرده لشاشة الدخول. ويكمن الحل في تطبيق قفل التزامن وفحص التحقق المزدوج (Single-Flight with Double-Checked Locking)، بحيث يقوم الخيط الأول فقط بالتجديد عبر الشبكة، بينما تكتشف باقي الخيوط المنتظرة التوكن الجديد في الذاكرة وتعيد إرسال طلباتها فوراً دون لمس سيرفر المصادقة.",
        "walkthrough_ar": """تطبيق نمط الفحص المزدوج لمنع سباق تجديد التوكن:
```kotlin
class SafeTokenManager(
    private val tokenStorage: TokenStorage,
    private val authApi: AuthApiService
) {
    private val lock = Any()

    fun refreshTokenSafely(failedHeader: String?): String? {
        val failedToken = failedHeader?.removePrefix("Bearer ")

        synchronized(lock) {
            val currentToken = tokenStorage.getAccessToken()

            // 1. الفحص المزدوج: إذا كان خيط آخر قد جدد التوكن بالفعل
            if (currentToken != null && currentToken != failedToken) {
                return currentToken // استخدم التوكن الجديد فوراً دون اتصال
            }

            // 2. الخيط الأول فقط: ينفذ طلب التجديد الفعلي عبر الشبكة
            val refreshToken = tokenStorage.getRefreshToken() ?: return null
            val response = authApi.refreshSync(refreshToken).execute()

            return if (response.isSuccessful && response.body() != null) {
                val tokens = response.body()!!
                tokenStorage.save(tokens.accessToken, tokens.refreshToken)
                tokens.accessToken
            } else {
                tokenStorage.clear()
                null
            }
        }
    }
}
```""",
        "why_it_matters_ar": "يحمي المستخدم من تسجيل الخروج المفاجئ وغير المبرر أثناء استخدام التطبيق، ويقلل الضغط والطلبات المتكررة على سيرفرات المصادقة في أوقات الذروة.",
        "worked_example_ar": "فتح تطبيق التجارة الإلكترونية وإطلاق 4 طلبات متزامنة لشاشات العرض؛ تفشل جميعها بـ 401، فيقوم خيط واحد بتجديد التوكن بينما تنتظر الخيوط الثلاثة الأخرى لتستخدم التوكن الجديد فوراً وتنجح العمليات.",
        "trade_offs_ar": "إضافة قفل تزامن Synchronized يحجب الخيوط لأجزاء من الثانية أثناء انتظار التجديد، ولكنه الضمان الوحيد لمنع إلغاء الجلسات وحماية استقرار تجربة المستخدم.",
        "failure_modes_ar": "إطلاق طلب تجديد لكل طلب فاشل بـ 401 مما يفعل نظام حماية الاختراق في السيرفر بسبب تكرار استخدام نفس Refresh Token ويطرد المستخدم نهائياً من حسابه.",
        "production_perspective_ar": "في كبرى الشركات، نلزم كافة مكاتب الشبكة بتطبيق نمط Single-Flight عبر TokenManager موحد، ونكتب اختبارات ضغط Stress Tests تطلق مئة طلب متزامن للتأكد من عدم استدعاء سيرفر التجديد إلا مرة واحدة.",
        "how_to_answer_ar": "ابدأ بشرح سيناريو الفشل ومخاطر Refresh Token Rotation، ثم اشرح آلية الحل الهندسي بنمط Double-Checked Locking وكيف يتعرف الخيط الثاني على التوكن الجديد دون طلب شبكي.",
        "talking_points_ar": "ظاهرة Thundering Herd في المصادقة، مخاطر Refresh Token Rotation، وكيفية عمل الفحص المزدوج داخل القفل التزامني.",
        "follow_ups_ar": "- **المحاور:** 'ما هو الـ Refresh Token Rotation ولماذا يزيد من تعقيد المشكلة؟'\n  **المرشح:** 'هو معيار أمني يبطل صلاحية الـ Refresh Token بمجرد استخدامه ويصدر بديلاً له، فإذا استخدمته طلبات متزامنة يعتبر السيرفر أن التوكن سُرق ويقفل الحساب فوراً.'\n\n- **المحاور:** 'كيف يعمل الفحص المزدوج Double-Check عملياً داخل القفل؟'\n  **المرشح:** 'يقارن الخيط التوكن الفاشل في طلبه بالتوكن الحالي المخزن في الذاكرة؛ فإذا وجدهما مختلفين يعلم أن خيطاً سابقاً قام بالتجديد أثناء انتظاره، فيستخدم التوكن الجديد فوراً دون لمس الشبكة.'",
        "self_check_ar": "هل شرحت خطورة Refresh Token Rotation بالتفصيل؟ وهل بينت منطق الفحص المزدوج وكيف يمنع تكرار طلبات التجديد؟",
        "references_ar": f"- [IETF: OAuth 2.0 Threat Model and Security](https://datatracker.ietf.org/doc/html/rfc6819#section-5.2.2.3) — توثيق مخاطر تدوير التوكن وسرقته.\n- [OkHttp Single-Flight Discussion](https://github.com/square/okhttp/issues/3146) — مناقشات مهندسي OkHttp حول تزامن تجديد الجلسات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تحدث مشكلة السباق عند فشل عدة طلبات متوازية بكود 401 معاً مما يدفعها لتجديد التوكن في نفس الوقت وإلغاء الجلسة تحت نظام تدوير التوكن. ونحلها بتطبيق نمط الفحص المزدوج مع قفل التزامن؛ فينفذ الخيط الأول فقط طلب التجديد الشبكي، بينما تكتشف باقي الخيوط التوكن المحدث وتستخدمه فوراً دون تكرار الاتصال.",
        "best_answer_ar": "تعد مشكلة السباق المتزامن عند تجديد التوكن من أكثر المشاكل المعمارية الخفية التي تسبب طرد المستخدمين فجأة من التطبيقات.\n\nالسيناريو يحدث عند فتح شاشة رئيسية تطلق مثلاً أربعة استدعاءات شبكة في نفس اللحظة عبر Coroutines متوازية؛ فإذا كان التوكن منتهياً، ترجع الطلبات الأربعة بكود 401 في نفس الثانية. وإذا ترك الأمر دون تنظيم، سيحاول كل طلب إرسال استدعاء تجديد مستقل إلى السيرفر.\n\nوتكمن الخطورة في أن أنظمة الحماية الحديثة تطبق تقنية تدوير التوكن Refresh Token Rotation، والتي تمنح التوكن صلاحية استخدام لمرة واحدة فقط؛ فبمجرد نجاح أول طلب، يلغي السيرفر الـ Refresh Token القديم، وعندما تصل الطلبات الثلاثة التالية بالتوكن القديم، يعتبر السيرفر أن التوكن قد تعرض للسرقة ويقوم بإلغاء جلسة المستخدم بالكامل كإجراء أمني وقائي.\n\nالحل الهندسي هو تطبيق نمط القفل الموحد مع الفحص المزدوج Single-Flight Double-Checked Locking؛ حيث تدخل الطلبات الفاشلة في قفل تزامني واحد. والخيط الذي يصل أولاً يقوم بفحص التوكن وتنفيذ طلب التجديد وحفظه في الذاكرة، بينما تقوم الخيوط الأخرى المنتظرة بمجرد دخولها بمقارنة التوكن، فتجد أنه قد تم تحديثه بالفعل، فتأخذ التوكن الجديد وتعيد إرسال طلباتها فوراً دون إجراء أي مكالمة شبكة إضافية.",
        "deep_answer_ar": "في إدارة الأنظمة الحساسة وتطبيقات التكنولوجيا المالية، يمثل تسجيل الخروج الوهمي بسبب سباق التوكن عيباً تشغيلياً جسيماً يضر بثقة المستخدمين ويفسد تجربة الاستخدام.\n\nأصل المشكلة يكمن في معايير أمان OAuth2 المشددة؛ فعندما يكتشف السيرفر وصول عدة طلبات متزامنة بنفس الـ Refresh Token بعد تدويره، يفترض النظام الأمني حدوث هجوم استيلاء على الجلسة Token Replay Attack، مما يدفعه لحرق الجلسة فوراً وإلغاء كافة الرموز المرتبطة بالمستخدم. ولتجنب هذا السيناريو، نصمم مدير التوكن TokenManager وفق معمارية تعتمد على القفل المتبادل ReentrantLock أو Mutex.\n\nعند استقبال كود 401 في OkHttp Authenticator، نمرر التوكن الذي فشل في الطلب إلى دالة التجديد الآمنة. وعند عبور القفل، نطبق خطوة الفحص المزدوج Double-Check بمقارنة التوكن المرفق بالتوكن المخزن حالياً في الكاش؛ فإذا وجدنا أن التوكن تغير، نعلم يقيناً أن خيطاً سابقاً كان قد حاز القفل وأتم التجديد بنجاح أثناء انتظار هذا الخيط، فنقوم بإرجاع التوكن الجديد فوراً ونعيد محاولة الطلب دون فتح اتصال بالشبكة.\n\nوفي حال كان التوكن ما زال مطابقاً، يتولى هذا الخيط الوحيد تنفيذ طلب التجديد وحفظ الزوج الجديد من Access و Refresh Tokens في التخزين المشفر، ثم يحرر القفل. هذا التنسيق الدقيق يختصر موجة الـ 401 من عدة استدعاءات عشوائية إلى استدعاء شبكي وحيد وذري، مما يضمن ثبات الجلسات واستقرار التطبيق في أصعب ظروف الاستخدام المتزامن."
    }
}

# ==========================================
# DAT-11: How do you design a migration that preserves user data?
# ==========================================
DATA["DAT-11"] = {
    "concept_en": """Designing production Room database migrations requires evolving SQLite schemas incrementally without corrupting or dropping user data:
- Versioning & Schema Contracts: Every database modification requires incrementing the database version number in the @Database annotation and providing an explicit Migration(startVersion, endVersion) implementation containing raw SQL Data Definition Language (DDL) statements.
- SQLite Alter Table Limitations: SQLite has historically lacked support for dropping columns, altering column types, or modifying constraints in place. Complex migrations require a four-step table recreation pattern:
  1. Create a new temporary table with the desired schema, constraints, and defaults.
  2. Copy data from the old table into the temporary table using INSERT INTO ... SELECT.
  3. Drop the old table via DROP TABLE.
  4. Rename the temporary table to the original table name via ALTER TABLE ... RENAME TO.
- Testing & Verification:
  * Export Schema: Configure room.schemaLocation in Gradle so KSP exports a JSON snapshot of each database version schema into Git version control.
  * Automated Migration Tests: Use Room's MigrationTestHelper in instrumented tests to create an old database version, populate it with mock user records, execute the migration, and assert that data remains uncorrupted and tables match the exported schema.
- The Golden Production Rule: Strictly forbid fallbackToDestructiveMigration() in release builds, as it drops all SQLite tables and wipes user data upon schema mismatches.""",
    "walkthrough_en": """Comprehensive Room migration with table recreation and automated test:
```kotlin
// 1. Defining a complex migration that splits columns and adds foreign keys
val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // Step 1: Create temp table with updated schema
        db.execSQL(
            "CREATE TABLE users_temp (" +
            "id TEXT PRIMARY KEY NOT NULL, " +
            "firstName TEXT NOT NULL, " +
            "lastName TEXT NOT NULL, " +
            "email TEXT NOT NULL DEFAULT '')"
        )

        // Step 2: Copy existing data over
        db.execSQL(
            "INSERT INTO users_temp (id, firstName, lastName) " +
            "SELECT id, firstName, lastName FROM users"
        )

        // Step 3: Drop old table
        db.execSQL("DROP TABLE users")

        // Step 4: Rename temp table to final name
        db.execSQL("ALTER TABLE users_temp RENAME TO users")

        // Step 5: Recreate indices
        db.execSQL("CREATE UNIQUE INDEX IF NOT EXISTS index_users_email ON users(email)")
    }
}

// 2. Automated Migration Test using MigrationTestHelper
@RunWith(AndroidJUnit4::class)
class DatabaseMigrationTest {
    @get:Rule
    val helper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java.canonicalName,
        FrameworkSQLiteOpenHelperFactory()
    )

    @Test
    fun migrate2To3_preservesUserData() {
        // Create DB at version 2 and insert test record
        helper.createDatabase("test-db", 2).apply {
            execSQL("INSERT INTO users (id, firstName, lastName) VALUES ('u1', 'Mohamed', 'Mahmoud')")
            close()
        }

        // Run migration to version 3 and validate constraints
        val db = helper.runMigrationsAndValidate("test-db", 3, true, MIGRATION_2_3)
        val cursor = db.query("SELECT id, firstName, lastName, email FROM users WHERE id = 'u1'")
        cursor.moveToFirst()
        assertEquals("Mohamed", cursor.getString(1))
        assertEquals("", cursor.getString(3)) // Default value populated
        cursor.close()
    }
}
```""",
    "short_en": """Designing a data-preserving Room migration requires incrementing database version numbers, providing explicit SQL DDL migrations, and utilizing the 4-step table recreation pattern for complex alterations. Schema JSON dumps and MigrationTestHelper automate validation in CI, while destructive fallback migrations are strictly banned in release builds.""",
    "structured_en": """Designing safe database migrations in Android requires a disciplined approach to schema evolution and automated testing.
First, every schema change requires bumping the Room database version and supplying a custom Migration object. For simple changes like adding a nullable column, a raw ALTER TABLE ADD COLUMN statement suffices.
Second, because SQLite does not permit direct column deletions or constraint modifications, complex schema shifts require a 4-step migration: creating a temporary table with the target schema, copying existing user records via INSERT INTO SELECT, dropping the old table, and renaming the temporary table.
Third, migrations must be verified automatically before production release. By enabling schema exports in Gradle, we write instrumented tests using MigrationTestHelper to simulate real upgrades and confirm zero data loss, strictly banning fallbackToDestructiveMigration in production.""",
    "deep_senior_en": """In production applications storing offline-first user state, a failed database migration is an existential threat that leads to immediate app crashes on launch or catastrophic data loss.
The most frequent production bug occurs when an engineer relies on fallbackToDestructiveMigration().
While convenient during early prototyping, shipping this flag to production guarantees that whenever the database version increases, Room silently wipes all SQLite tables, erasing unsynced user drafts, cached credentials, and offline purchase records.
To evolve schemas safely, we enforce a strict migration protocol.
Because SQLite lacks full ALTER TABLE capabilities, removing a column or adding a NOT NULL constraint without a default requires the classic temporary table shuffle: creating the new table structure, copying over data with fallback defaults, dropping the legacy table, and renaming the temporary table.
To guarantee mathematical correctness, we export Room schemas as JSON artifacts tracked in Git version control via the room.schemaLocation Gradle compiler argument.
In our CI pipeline, an automated test suite powered by MigrationTestHelper executes every historical migration path against real SQLite instances, seeding mock customer records into version N and asserting their integrity in version N+1.
This end-to-end automated verification guarantees that millions of existing users upgrade smoothly without a single lost record or launch crash.""",
    "meta_ar": {
        "id": "DAT-11",
        "questionAr": "كيف تصمم ترحيلاً آمناً لقاعدة بيانات Room (Migration) يحافظ على بيانات المستخدم دون أي فقدان؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم دورة حياة ترحيل قواعد البيانات، والتعامل مع قيود SQLite عبر تقنية الجدول المؤقت (Table Recreation)، واختبار الـ Migrations بـ MigrationTestHelper وحظر الـ Destructive Migration.",
        "concept_ar": "يتطلب الترحيل الآمن لقواعد بيانات Room الحفاظ التام على بيانات المستخدمين مع ترقية هيكل الجداول: يتم رفع رقم إصدار قاعدة البيانات في تعليق @Database وكتابة كائن Migration(start, end) يحتوي على أوامر SQL صريحة. ولأن محرك SQLite يفرض قيوداً تاريخية تمنع حذف الأعمدة أو تعديل القيود مباشرة في الجدول القائم، تتطلب التعديلات المعقدة تطبيق نمط الجدول المؤقت المكون من أربع خطوات: إنشاء جدول مؤقت بالهيكل الجديد والقيود المطلوبة، ثم نسخ البيانات من الجدول القديم باستخدام INSERT INTO SELECT، ثم حذف الجدول القديم عبر DROP TABLE، وأخيراً إعادة تسمية الجدول المؤقت للاسم الأصلي بـ ALTER TABLE RENAME. ويجب تصدير مخططات البيانات كملفات JSON عبر room.schemaLocation واختبار الترحيل آلياً في الـ CI باستخدام أداة MigrationTestHelper، مع الحظر التام لاستخدام fallbackToDestructiveMigration في إصدارات الإنتاج.",
        "walkthrough_ar": """تنفيذ ترحيل معقد بالجدول المؤقت واختباره آلياً:
```kotlin
// 1. ترحيل معقد بحذف وتعديل أعمدة عبر جدول مؤقت
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // إنشاء الجدول المؤقت
        db.execSQL("CREATE TABLE users_temp (id TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL)")
        // نسخ البيانات
        db.execSQL("INSERT INTO users_temp (id, name) SELECT id, name FROM users")
        // حذف القديم وتغيير اسم المؤقت
        db.execSQL("DROP TABLE users")
        db.execSQL("ALTER TABLE users_temp RENAME TO users")
    }
}

// 2. اختبار الترحيل آلياً للتأكد من بقاء البيانات
@Test
fun testMigration1To2() {
    val helper = MigrationTestHelper(...)
    val db = helper.createDatabase("test.db", 1).apply {
        execSQL("INSERT INTO users VALUES ('1', 'Mohamed')")
        close()
    }
    helper.runMigrationsAndValidate("test.db", 2, true, MIGRATION_1_2)
    // التحقق من أن السجل '1' لا يزال موجوداً
}
```""",
        "why_it_matters_ar": "يمنع انهيار التطبيق المفاجئ عند التحديث من متجر التطبيقات ويحمي بيانات المستخدمين وسجلاتهم غير المزامنة من المسح العشوائي، مما يحافظ على ثقة المستخدمين وسمعة التطبيق.",
        "worked_example_ar": "تحديث تطبيق محادثات لإضافة حقل 'الرسائل المثبتة' وحذف حقل قديم؛ عند فتح التحديث يتم تنفيذ الميجريشن بأمان دون حذف سجل الرسائل التاريخي للمستخدم.",
        "trade_offs_ar": "كتابة سكريبتات الترحيل واختبارها يدوياً وآلياً تتطلب وقتاً وجهداً هندسياً كبيراً، ولكنها الخيار الحتمي لمنع فقدان بيانات ملايين المستخدمين وانهيار تقييمات التطبيق.",
        "failure_modes_ar": "تفعيل fallbackToDestructiveMigration() في تطبيق إنتاجي مما يمسح قاعدة بيانات المستخدمين بالكامل مع كل تحديث، أو نسيان كتابة قيمة افتراضية DEFAULT لعمود NOT NULL جديد مما يفشل الترحيل وينهار التطبيق.",
        "production_perspective_ar": "في كبرى المؤسسات، نضع فحصاً آلياً في مسار الـ CI يمنع دمج أي كود يحتوي على fallbackToDestructiveMigration، ونلزم الفرق بكتابة اختبار لكل ملف JSON يتم تصديره في مجلد schemas.",
        "how_to_answer_ar": "اشرح الخطوات الأساسية: رفع رقم الإصدار وكتابة كائن Migration، ثم وضح حيلة الجدول المؤقت لتخطي قيود SQLite، واختم بأهمية MigrationTestHelper وحظر المسح التدميري في الإنتاج.",
        "talking_points_ar": "قيود SQLite في تعديل الجداول، خطوات الجدول المؤقت الأربع، دور MigrationTestHelper، وخطورة Destructive Migration في الإنتاج.",
        "follow_ups_ar": "- **المحاور:** 'ماذا يحدث لو أضفت عموداً جديداً بنوع NOT NULL دون وضع قيمة افتراضية DEFAULT؟'\n  **المرشح:** 'سيفشل الترحيل فوراً بانهيار التطبيق؛ لأن السجلات القديمة ستحتوي على قيم خالية NULL وهو ما يتعارض صراحة مع شرط NOT NULL.'\n\n- **المحاور:** 'كيف تضمن عدم نسيان أي ترحيل بين الإصدارات القديمة والإصدار الحالي؟'\n  **المرشح:** 'بتوفير مسارات ترحيل متتالية واختبار الترقية من أقدم إصدار متاح في السوق إلى الإصدار الحالي داخل اختبارات الـ CI المؤتمتة باستخدام MigrationTestHelper.'",
        "self_check_ar": "هل شرحت خطوات استخدام الجدول المؤقت الأربع بوضوح؟ وهل ذكرت أهمية اختبار الترحيل بـ MigrationTestHelper وخطر Destructive Migration؟",
        "references_ar": f"- [Room Database Migrations](https://developer.android.com/training/data-storage/room/migrating-db-versions) — دليل جوجل الرسمي لترحيل قواعد بيانات Room.\n- [SQLite ALTER TABLE Capabilities](https://www.sqlite.org/lang_altertable.html) — توثيق إمكانيات ومحددات تعديل الجداول في SQLite.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يصمم الترحيل الآمن برفع رقم الإصدار وكتابة كائن Migration بأوامر SQL دقيقة، مع استخدام تقنية الجدول المؤقت لنقل البيانات وتعديل القيود بأمان لتخطي محددات SQLite. وتُختبر الترحيلات آلياً في الـ CI باستخدام MigrationTestHelper مع حظر استخدام التدمير التلقائي Destructive Migration نهائياً في الإنتاج.",
        "best_answer_ar": "تصميم ترحيل آمن لقواعد بيانات Room يتطلب انضباطاً معمارياً واختبارات صارمة لضمان بقاء بيانات المستخدم سليمة.\n\nالخطوة الأولى تبدأ برفع رقم إصدار قاعدة البيانات في تعليق @Database وكتابة كائن Migration صريح يربط الإصدار القديم بالجديد بأوامر SQL مباشرة؛ فإذا كان التعديل بسيطاً كإضافة عمود يقبل القيمة الخالية، يكفي أمر ALTER TABLE ADD COLUMN.\n\nأما إذا كان التعديل معقداً مثل حذف عمود أو تعديل قيود المفاتيح، فإن محرك SQLite يمنع التعديل المباشر في نفس الجدول؛ وهنا نطبق نمط الجدول المؤقت المكون من أربع خطوات متتالية: إنشاء جدول مؤقت بالهيكل الجديد، ثم نسخ البيانات من الجدول القديم باستخدام INSERT INTO SELECT، ثم حذف الجدول القديم عبر DROP TABLE، وأخيراً إعادة تسمية الجدول المؤقت ليأخذ اسم الجدول الأصلي مع إعادة إنشاء الفهارس.\n\nولضمان عدم حدوث أي مفاجآت، نصدر مخططات الـ JSON في الـ Git ونكتب اختبارات آلية عبر MigrationTestHelper تحاكي ترقية مستخدم حقيقي بالبيانات القديمة وتتأكد من سلامتها في الـ CI، مع حظر خيار fallbackToDestructiveMigration نهائياً في بيئات الإنتاج لمنع مسح بيانات المستخدمين.",
        "deep_answer_ar": "في تطبيقات أندرويد المؤسسية التي تعتمد على التخزين المحلي، يمثل فشل ترحيل قاعدة البيانات خطراً كارثياً يؤدي إما لتعطل التطبيق عند التشغيل فور التحديث أو فقدان دائم لبيانات ومسودات العملاء غير المزامنة.\n\nالكارثة الكبرى تحدث عندما يستسهل المطور استخدام دالة fallbackToDestructiveMigration؛ فرغم فائدتها في مرحلة التطوير السريع، إلا أن شحنها للمستخدمين يعني مسح كافة الجداول وإعادة بنائها من الصفر مع كل تحديث للإصدار، مما يمحو بيانات الدفع والمسودات المخزنة محلياً. المعمارية السليمة تفرض توفير مسارات ترحيل تدريجية وصريحة في كافة ملفات البناء.\n\nوللتغلب على قيود SQLite التاريخية في تعديل الأعمدة، نعتمد استراتيجية الترحيل عبر الجدول المؤقت Table Recreation Pattern؛ فننشئ الجدول البديل بكافة القيود وننقل البيانات القديمة مع وضع قيم افتراضية حذرة للحقول الإلزامية الجديدة، ثم نسقط الجدول القديم ونعيد تسمية المؤقت ونبني الفهارس. هذا التسلسل يحمينا من أخطاء قيود البيانات وتناقضات السجلات.\n\nولضمان صحة هذه العمليات برمجياً، نفعل خاصية تصدير مخططات Room بصيغة JSON تحت إدارة Git عبر إعدادات KSP. وندمج أداة MigrationTestHelper في مسار التكامل المستمر CI لتشغيل اختبارات آلية تنشئ قاعدة بيانات قديمة وتملؤها ببيانات وهمية، ثم تنفذ سكريبت الترحيل للتحقق من عدم حدوث أي تسريب أو تلف في البيانات، مما يضمن انتقال ملايين المستخدمين للإصدار الجديد بسلاسة مطلقة."
    }
}

# ==========================================
# DAT-12: How do you use Room transactions for all-or-nothing writes?
# ==========================================
DATA["DAT-12"] = {
    "concept_en": """Enforcing ACID atomicity across multi-step database writes in Room prevents partial data corruption and state inconsistencies:
- Atomicity Guarantee (All-or-Nothing): A database transaction ensures that a group of interdependent SQL write operations (inserts, updates, deletes) either all succeed completely and commit to disk, or if any single operation fails or throws a runtime exception, the entire operation is rolled back to the exact initial state.
- Implementation Paradigms in Room:
  1. The @Transaction DAO Annotation: When a DAO method is annotated with @Transaction, Room automatically wraps its execution body within a SQLite transaction block (beginTransaction / setTransactionSuccessful / endTransaction). It is commonly applied to methods that clear existing cache and insert fresh items, or queries fetching @Relation composite entities.
  2. Programmatic RoomDatabase.withTransaction: A Kotlin Coroutines extension function designed for repository or UseCase layers. It enables cross-DAO transactional boundaries, allowing writes across multiple distinct tables and DAOs to execute atomically within a single SQLite transaction on Dispatchers.IO.
- Concurrency & SQLite WAL Mode: Room operates in SQLite Write-Ahead Logging (WAL) mode by default. Transactions use beginTransactionNonExclusive(), allowing concurrent read operations from the UI thread or background workers to proceed unimpeded without being blocked by active write transactions.""",
    "walkthrough_en": """Atomic cache replacement using @Transaction and cross-DAO withTransaction:
```kotlin
// 1. DAO-level Transaction for atomic cache refresh
@Dao
interface OrderDao {
    @Query("DELETE FROM orders WHERE status = :status")
    suspend fun deleteOrdersByStatus(status: String)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOrders(orders: List<OrderEntity>)

    // Atomic All-or-Nothing execution: if insert fails, delete is rolled back
    @Transaction
    suspend fun refreshOrders(status: String, newOrders: List<OrderEntity>) {
        deleteOrdersByStatus(status)
        insertOrders(newOrders)
    }
}

// 2. Repository-level cross-DAO atomic transaction
class CheckoutRepository(
    private val db: AppDatabase,
    private val orderDao: OrderDao,
    private val inventoryDao: InventoryDao
) {
    suspend fun completePurchase(order: OrderEntity, items: List<OrderItemEntity>): Result<Unit> = runCatching {
        // Enforces atomic boundary across distinct tables
        db.withTransaction {
            orderDao.insertOrder(order)
            items.forEach { item ->
                val updated = inventoryDao.decrementStock(item.productId, item.quantity)
                if (updated == 0) throw IllegalStateException("Insufficient inventory for product ${item.productId}")
            }
        }
    }
}
```""",
    "short_en": """Room transactions enforce atomic all-or-nothing guarantees, ensuring multiple writes commit completely or roll back entirely upon failure. They can be declared via the @Transaction annotation on DAO methods or programmatically across multiple DAOs using RoomDatabase.withTransaction, operating with SQLite WAL mode to prevent blocking concurrent reads.""",
    "structured_en": """Using Room transactions guarantees data consistency by enforcing atomic all-or-nothing writes across database tables.
First, atomicity ensures that when executing multi-step updates, such as clearing a cache table and inserting fresh records, any mid-operation failure cleanly reverts the database to its pre-transaction state, preventing partial data corruption.
Second, Room supports two implementation approaches: annotating DAO methods with @Transaction for single-DAO operations, or utilizing the RoomDatabase.withTransaction coroutine extension for coordinating multi-DAO transactions at the repository level.
Third, Room combines transactions with SQLite Write-Ahead Logging (WAL) mode. This architectural separation ensures that background write transactions execute without locking the database against concurrent read queries, keeping UI Flow rendering smooth and uninterrupted.""",
    "deep_senior_en": """In complex mobile applications, maintaining database invariants across multi-table writes without transactions is impossible.
Consider an e-commerce checkout flow where an app must insert an order record, insert line items, and decrement local stock counters.
If the device process dies midway due to low memory or an uncaught exception, executing these statements independently leaves the local database in a corrupted state: the order exists, but stock was never decremented and line items are missing.
By wrapping the logic inside db.withTransaction, Room binds the coroutine context to an exclusive database transaction.
Under the hood, Room invokes beginTransactionNonExclusive().
If any statement throws an exception or the coroutine job is cancelled, SQLite executes a rollback, restoring all tables to their exact state prior to the transaction.
Furthermore, Room's default Write-Ahead Logging mode provides snapshot isolation: readers read from the main database file while writes append to the -wal journal file.
This means active write transactions never block the Main thread from querying Room via Flow, completely preventing UI jank.
However, senior engineers avoid wrapping heavy network calls or complex business computations inside withTransaction, as keeping a SQLite transaction open excessively long locks out other background write workers and risks database busy timeouts.
By keeping transaction blocks micro-scoped and atomic, we guarantee pristine data integrity while maintaining peak database throughput across concurrent background threads.""",
    "meta_ar": {
        "id": "DAT-12",
        "questionAr": "كيف تستخدم معاملات Room البرمجية (Transactions) لتنفيذ عمليات الكتابة الذرية (All-or-Nothing Writes)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم مبدأ الذرية (Atomicity) في معايير ACID، والفرق بين @Transaction في الـ DAO و withTransaction في المستودع، واستغلال وضع WAL لمنع حجب استعلامات القراءة.",
        "concept_ar": "تضمن المعاملات البرمجية (Transactions) في Room تحقيق مبدأ الذرية (Atomicity) ضمن معايير ACID؛ فإما أن تنجح كافة عمليات التعديل والكتابة وتُحفظ نهائياً على القرص، أو يتم التراجع الكامل (Rollback) عن كافة الخطوات السابقة في حال حدوث أي خطأ أو استثناء برمجي، مما يمنع تشوه البيانات وتركها في حالة ناقصة. وتوفر Room طريقتين للتطبيق: تعليق @Transaction فوق دوال كائن الـ DAO للعمليات الذرية المباشرة (مثل مسح الكاش القديم وحفظ البيانات الجديدة معاً)، واستخدام دالة الامتداد RoomDatabase.withTransaction لتنسيق المعاملات عبر عدة DAOs وجداول مختلفة داخل طبقة المستودع. وتعمل هذه المعاملات بالتزامن مع وضع التخزين المسبق SQLite WAL، مما يسمح بتنفيذ عمليات الكتابة في الخلفية دون حجب استعلامات القراءة المتزامنة لشاشات العرض.",
        "walkthrough_ar": """تطبيق المعاملات الذرية على مستوى DAO وعلى مستوى المستودع:
```kotlin
// 1. معاملة على مستوى الـ DAO لتحديث الكاش ذرياً
@Dao
interface CartDao {
    @Query("DELETE FROM cart")
    suspend fun clear()

    @Insert
    suspend fun insertAll(items: List<CartEntity>)

    @Transaction
    suspend fun replaceCart(items: List<CartEntity>) {
        clear()
        insertAll(items) // إذا فشلت الإضافة، يتراجع تلقائياً عن المسح
    }
}

// 2. معاملة عبر عدة DAOs في المستودع بـ withTransaction
class CheckoutRepository(private val db: AppDatabase) {
    suspend fun checkout(order: Order, items: List<Item>) = db.withTransaction {
        db.orderDao().insert(order)
        db.inventoryDao().decrementStock(items)
    }
}
```""",
        "why_it_matters_ar": "يحمي قاعدة البيانات من التلف وتناقض السجلات عند انقطاع التطبيق أو حدوث خطأ أثناء العمليات المتعددة، مثل خصم الرصيد دون تسجيل الفاتورة أو مسح السلة دون إضافة الأصناف الجديدة.",
        "worked_example_ar": "تنفيذ عملية إتمام شراء في متجر؛ حيث يتم تسجيل الطلب وخصم كميات المخزون وتحديث المحفظة داخل Transaction واحدة، فإذا نفد صنف يتراجع النظام عن كل التعديلات فوراً.",
        "trade_offs_ar": "تضمن المعاملات سلامة مطلقة للبيانات ولكن إبقاء المعاملة مفتوحة لفترة طويلة أو تضمين استدعاءات شبكة داخلها قد يعلق قاعدة البيانات ويسبب أخطاء SQLiteDatabaseLockedException.",
        "failure_modes_ar": "تنفيذ عمليات كتابة مترابطة في جداول متعددة دون Transaction مما يترك بيانات يتيمة ومشوهة عند حدوث كراش، أو وضع استدعاء Retrofit داخل withTransaction مما يجمد قاعدة البيانات.",
        "production_perspective_ar": "في المشروعات الكبرى، نمنع نهائياً وضع أي كود شبكي أو عمليات تشفير بطيئة داخل withTransaction، ونقصر المعاملة على العمليات المباشرة لقاعدة البيانات فقط لتفادي إقفال قاعدة البيانات.",
        "how_to_answer_ar": "عرف مفهوم الـ Atomicity و All-or-Nothing، ثم اشرح الفارق بين @Transaction في DAO و withTransaction في Repository، واختم بدور نمط WAL في عدم حجب القراءة أثناء الكتابة.",
        "talking_points_ar": "مبدأ الذرية والـ Rollback التلقائي، دالة withTransaction عبر عدة جداول، وتفادي وضع استدعاءات الشبكة داخل المعاملات.",
        "follow_ups_ar": "- **المحاور:** 'هل يجوز إجراء استدعاء شبكة عبر Retrofit داخل دالة withTransaction؟'\n  **المرشح:** 'قطعاً لا؛ لأن استدعاء الشبكة قد يستغرق ثوانٍ مما يبقي قفل المعاملة في SQLite محجوزاً ويمنع كافة خيوط التطبيق الأخرى من الكتابة في قاعدة البيانات.'\n\n- **المحاور:** 'كيف يساعد وضع WAL في Room على تحسين أداء المعاملات مع شاشات Compose؟'\n  **المرشح:** 'وضع WAL يسمح لعمليات القراءة بالاستمرار من ملف قاعدة البيانات الرئيسي في نفس الوقت الذي تكتب فيه المعاملة داخل ملف الـ WAL، فلا تتجمد شاشات العرض إطلاقاً.'",
        "self_check_ar": "هل شرحت مبدأ الذرية بوضوح؟ وهل بينت الفرق بين استخدام @Transaction واستخدام withTransaction والتحذير من استدعاءات الشبكة بداخلها؟",
        "references_ar": f"- [Android Developers: Room Transactions](https://developer.android.com/training/data-storage/room/referencing-data#transactions) — توثيق جوجل الرسمي للمعاملات في Room.\n- [SQLite Write-Ahead Logging](https://www.sqlite.org/wal.html) — توثيق معمارية التخزين المسبق WAL في محرك SQLite.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تضمن معاملات Room تنفيذ مجموعة عمليات كتابة مترابطة بشكل ذري متكامل All-or-Nothing، بحيث تحفظ كلها أو يُلغى أثرها بالكامل عند حدوث أي خطأ لمنع تشوه البيانات. وتطبق عبر تعليق @Transaction في الـ DAO أو عبر دالة withTransaction عبر عدة جداول في المستودع، وتعمل بنمط WAL لمنع حجب استعلامات القراءة.",
        "best_answer_ar": "المعاملات البرمجية Transactions في Room هي صمام الأمان الذي يحمي قاعدة البيانات من التلف والتناقض عند تنفيذ عمليات كتابة متعددة ومترابطة.\n\nالفكرة الجوهرية للمعاملة تقوم على مبدأ الذرية Atomicity؛ فإما أن تكتمل كافة العمليات بنجاح تام وتُحفظ على القرص، أو يتم التراجع الفوري Rollback عن كافة الخطوات السابقة في حال حدوث أي خطأ أو كراش مفاجئ، مما يضمن استحالة بقاء البيانات في حالة مشوهة.\n\nتوفر لنا مكتبة Room طريقتين لتنفيذ المعاملات: الأولى هي استخدام تعليق @Transaction فوق دوال كائن الوصول DAO، وتناسب العمليات التي تجري داخل جدول واحد أو استعلامات العلاقات المترابطة، مثل تفريغ سلة الشراء وإضافة العناصر الجديدة ذرياً. والثانية هي دالة الامتداد RoomDatabase.withTransaction، وتستخدم في طبقة الـ Repository لتنسيق المعاملات عبر عدة DAOs وجداول مختلفة كإنشاء فاتورة وتعديل رصيد المخزن معاً.\n\nوتعمل هذه المعاملات بالتكامل مع نمط SQLite WAL الافتراضي؛ مما يتيح لخيوط الخلفية إنجاز عمليات الكتابة الذرية دون حجب استعلامات القراءة التفاعلية لشاشات Compose، مع الالتزام الصارم بعدم وضع أي استدعاءات شبكة داخل المعاملة لتفادي حجز أقفال قاعدة البيانات لفترات طويلة.",
        "deep_answer_ar": "في هندسة التطبيقات المالية والتجارة الإلكترونية، يمثل التخلي عن المعاملات الذرية عند كتابة البيانات المتشعبة مصدراً مباشراً للأخطاء الكارثية وتلف الحسابات.\n\nتخيل سيناريو إتمام عملية شراء: يحتاج التطبيق إلى إنشاء سجل الطلب، ثم إضافة عناصر الفاتورة، ثم خصم الكمية من المخزون المحلي. فلو قُتل التطبيق بسبب نقص الذاكرة بعد إضافة الطلب وقبل خصم المخزون، تصبح قاعدة البيانات في حالة تناقض معمارية مشوهة. وباستخدام دالة db.withTransaction، نضمن دمج هذه العمليات في سياق ذري واحد يستدعي داخلياً beginTransactionNonExclusive في SQLite، فإذا رُفع أي استثناء أو أُلغيت مهمة الـ Coroutine، يتراجع المحرك تلقائياً ويعيد الجداول لحالتها الأصلية النظيفة.\n\nوتبرز قوة Room في دعمها الافتراضي لنمط Write-Ahead Logging؛ حيث تُكتب التعديلات في ملف سجل فرعي (-wal) بينما تواصل خيوط الشاشات قراءة النسخ الثابتة من ملف قاعدة البيانات الأساسي، مما يحقق عزلاً تاماً يمنع سقوط معدل الإطارات 120Hz أثناء التحديثات المكثفة للبيانات.\n\nولكننا في الفرق الهندسية الكبرى نضع معايير صارمة تمنع تضمين أي استدعاء شبكي لـ Retrofit أو عمليات معالجة للصور داخل نطاق withTransaction؛ لأن بطء الشبكة سيبقي المعاملة مفتوحة لثوانٍ مما يؤدي إلى تراكم طوابير الانتظار وحدوث أخطاء SQLiteDatabaseLockedException وانهيار التطبيق، ولذا نحصر المعاملات فقط في عمليات الـ SQLite الخالصة والسريعة."
    }
}

# ==========================================
# DAT-13: How would you implement Paging 3 and RemoteMediator?
# ==========================================
DATA["DAT-13"] = {
    "concept_en": """Jetpack Paging 3 combined with RemoteMediator provides an enterprise-grade architecture for large-dataset pagination backed by local database caching:
- Paging 3 Architecture Layers:
  * Local Source of Truth: Room provides the PagingSource via standard SQL queries (SELECT * FROM items ORDER BY index). The UI layer consumes an immutable Flow<PagingData<Item>> pipeline directly from the database, eliminating network flickering and providing instant offline rendering.
  * Pager Component: Connects the PagingConfig (defining pageSize, prefetchDistance, and enablePlaceholders) with Room's PagingSource and the optional RemoteMediator.
- RemoteMediator Role & Mechanics:
  * Boundary Detection: Unlike an in-memory PagingSource that fetches network directly, RemoteMediator acts as a signal listener. When the user scrolls near the end of the cached local list, Paging 3 invokes RemoteMediator.load(loadType, state).
  * LoadType Taxonomy: REFRESH (initial load or swipe-to-refresh), APPEND (scrolling towards the end of dataset), PREPEND (scrolling towards the start of dataset).
- RemoteKey Entity & Atomic Refresh:
  * To track pagination cursors or next/prev page tokens across process death, a companion RemoteKeyEntity table is maintained in Room.
  * When loadType == REFRESH, Room executes an atomic transaction that clears existing RemoteKeys, clears stale feed items, and inserts the initial batch of network items alongside their updated cursors, ensuring seamless, non-jumping UI rendering.""",
    "walkthrough_en": """Complete Paging 3 and RemoteMediator implementation:
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
```""",
    "short_en": """Paging 3 with RemoteMediator uses Room as the single source of truth for UI streams while fetching incremental network pages at scroll boundaries. Companion RemoteKey tables persist pagination tokens across app restarts, and atomic Room transactions coordinate clearing and inserting records during refreshes without UI flickering.""",
    "structured_en": """Implementing Paging 3 with RemoteMediator establishes an offline-first pagination pipeline for large datasets.
First, Room serves as the absolute single source of truth. The DAO exposes a PagingSource queried by the Pager, streaming immutable PagingData directly to Compose or RecyclerView lists.
Second, RemoteMediator acts as a bridge between the local database and the remote network API. When the user scrolls near the end of the cached list, Paging 3 triggers RemoteMediator.load with an APPEND or REFRESH load type.
Third, we persist pagination tokens or cursors in a separate RemoteKeys table in Room.
During a REFRESH event, we execute an atomic transaction that resets remote keys, purges stale items, and inserts the fresh page, eliminating list jumping and supporting seamless offline paging.""",
    "deep_senior_en": """Architecting paginated feeds using Jetpack Paging 3 and RemoteMediator requires shifting from naive network-bound pagination to local-first database mediation.
A common anti-pattern is creating a custom PagingSource that calls Retrofit directly.
While straightforward, this approach breaks offline support, discards cached scroll positions on process death, and causes layout jumps during network re-fetches.
RemoteMediator solves this by fully decoupling UI pagination from network latency.
The UI layer observes a cold Flow<PagingData<Item>> queried strictly from Room.
When the user scrolls past the prefetchDistance threshold, Paging 3 evaluates the viewport and dispatches an APPEND event to RemoteMediator.
To maintain cursor integrity across app process death and system restarts, we maintain a companion FeedRemoteKeys table in Room storing nextKey and prevKey tokens.
During a swipe-to-refresh action (LoadType.REFRESH), executing the reset atomically inside db.withTransaction is mandatory.
We delete outdated remote keys, purge cached feed entities, and insert the new page along with its successor cursors within a single SQLite transaction.
Because Room is observed via Flow, the UI transitions gracefully to the fresh dataset without visual blinking or scroll glitches, providing a high-performance 120Hz scrolling experience that remains completely functional even when the user enters offline areas.
Additionally, we configure backpressure handling and prefetch buffers within PagingConfig, ensuring background network fetching completes well ahead of user scroll thresholds for an uninterrupted reading experience.""",
    "meta_ar": {
        "id": "DAT-13",
        "questionAr": "كيف تطبق مكتبة Paging 3 مع وسيط المزامنة البعيدة (RemoteMediator) لتصفح القوائم الكبيرة والعمل دون اتصال؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم معمارية Paging 3 وفصل الـ UI عن الشبكة، ودور RemoteMediator في جلب البيانات عند حواف التمرير، وإدارة جدول RemoteKeys والمعاملات الذرية لمنع وميض الشاشة.",
        "concept_ar": "توفر مكتبة Paging 3 مع وسيط المزامنة RemoteMediator حلاً معمارياً متكاملاً لتصفح القوائم الضخمة وفق مبدأ العمل دون اتصال أولاً: تصبح قاعدة بيانات Room هي المصدر الوحيد للحقيقة عبر PagingSource، حيث تستهلك واجهة المستخدم تدفقاً مستمراً Flow<PagingData> من الكاش المحلي فورياً. ويعمل RemoteMediator كحلقة وصل وسيطة تلتقط إشارات حواف التمرير؛ فعندما يقترب المستخدم من نهاية القائمة المعروضة، يُطلق Paging 3 دالة RemoteMediator.load بأنواع تحميل مختلفة (REFRESH للتحميل الأولي أو السحب للتحديث، و APPEND لجلب الصفحات التالية). ولتتبع مؤشرات الصفحات Cursors عند إغلاق التطبيق، يُنشأ جدول مخصص في Room يسمى RemoteKeys. وعند حدوث Refresh، يُنفذ كود الحذف والإضافة داخل @Transaction ذرية واحدة لضمان سلاسة الواجهة ومنع وميض القائمة أو قفزات التمرير.",
        "walkthrough_ar": """تطبيق RemoteMediator مع جدول المفاتيح RemoteKeys والمعاملة الذرية:
```kotlin
@OptIn(ExperimentalPagingApi::class)
class NewsRemoteMediator(
    private val db: AppDatabase,
    private val api: NewsApi
) : RemoteMediator<Int, NewsEntity>() {

    override suspend fun load(loadType: LoadType, state: PagingState<Int, NewsEntity>): MediatorResult {
        val page = when (loadType) {
            LoadType.REFRESH -> 1
            LoadType.PREPEND -> return MediatorResult.Success(endOfPaginationReached = true)
            LoadType.APPEND -> {
                val remoteKey = db.remoteKeyDao().getKeyForLastItem(state)
                remoteKey?.nextPage ?: return MediatorResult.Success(endOfPaginationReached = true)
            }
        }

        return try {
            val response = api.getNews(page = page)
            db.withTransaction {
                if (loadType == LoadType.REFRESH) {
                    db.remoteKeyDao().clear()
                    db.newsDao().clear()
                }
                db.remoteKeyDao().insert(NewsRemoteKey(page + 1))
                db.newsDao().insertAll(response.toEntities())
            }
            MediatorResult.Success(endOfPaginationReached = response.isEmpty())
        } catch (e: Exception) {
            MediatorResult.Error(e)
        }
    }
}
```""",
        "why_it_matters_ar": "يسمح بتصفح ملايين العناصر بسلاسة فائقة واستهلاك ضئيل للذاكرة والبطارية، ويوفر تجربة تصفح فورية لا تنقطع حتى لو كان الهاتف في وضع الطيران.",
        "worked_example_ar": "تطبيق أخبار أو متجر إلكتروني يتيح للمستخدم التمرير عبر آلاف المنتجات؛ حيث تُحفظ المنتجات في Room تدريجياً، وعند إعادة فتح التطبيق في المترو يجد المستخدم كافة الصفحات السابقة جاهزة للتصفح.",
        "trade_offs_ar": "توفر المعمارية تجربة مستخدم استثنائية وثباتاً معمارياً، ولكنها تزيد من تعقيد الكود وتتطلب إدارة جدول إضافي للمفاتيح وتنسيق المعاملات بدقة بالغة.",
        "failure_modes_ar": "كتابة PagingSource يستدعي Retrofit مباشرة مما يدمر دعم العمل دون اتصال ويضيع موضع التمرير، أو مسح البيانات في Refresh دون @Transaction مما يسبب وميضاً أبيض مزعجاً للمستخدم.",
        "production_perspective_ar": "في تطبيقات التواصل والمتاجر الكبرى، نمنع نهائياً استخدام PagingSource المباشر على الشبكة، ونلزم الفرق بتطبيق RemoteMediator وربطه بقاعدة Room مع ضبط prefetchDistance لتجربة تمرير ناعمة 120Hz.",
        "how_to_answer_ar": "اشرح الفكرة المعمارية أولاً: Room كمصدر وحيد للحقيقة و RemoteMediator كوسيط لجلب البيانات عند الحواف، ثم اشرح دور جدول RemoteKeys، واختم بأهمية Transaction لمنع وميض الواجهة.",
        "talking_points_ar": "دور PagingSource في Room، أنواع LoadType في RemoteMediator، وظيفة جدول RemoteKeys، وأهمية المعاملة الذرية لمنع قفزات القائمة.",
        "follow_ups_ar": "- **المحاور:** 'لماذا نحتاج لجدول منفصل مثل RemoteKeys بدلاً من وضع رقم الصفحة داخل الكيان نفسه؟'\n  **المرشح:** 'لأن رقم الصفحة أو الـ Cursor يرتبط بموضع العنصر في سياق الاستعلام الشبكي الحالي وقد يتغير، وفصله في جدول مستقل يمنع تلويث نموذج الدومين ويسهل مسحه وتحديثه ذرياً.'\n\n- **المحاور:** 'ماذا يحدث إذا انقطع الإنترنت أثناء جلب صفحة جديدة بـ RemoteMediator؟'\n  **المرشح:** 'يُرجع الوسيط MediatorResult.Error(e)، وتقوم Paging 3 بعرض حالة الخطأ في LoadState.append دون التأثير على العناصر السابقة المعروضة، مما يسمح للمستخدم بالضغط على زر إعادة المحاولة.'",
        "self_check_ar": "هل شرحت سبب اعتبار Room المصدر الوحيد للحقيقة؟ وهل وضحت دور جدول RemoteKeys وكيفية تفادي وميض القائمة بـ withTransaction؟",
        "references_ar": f"- [Android Developers: Paging 3 with RemoteMediator](https://developer.android.com/topic/libraries/architecture/paging/v3-network-db) — الدليل الرسمي لدمج Paging 3 مع قاعدة البيانات.\n- [Paging 3 Architecture Concepts](https://developer.android.com/topic/libraries/architecture/paging/v3-overview) — البنية التحتية لمعمارية Paging 3.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تعتمد Paging 3 مع RemoteMediator على جعل قاعدة بيانات Room المصدر الوحيد للحقيقة للواجهة، بينما يتولى RemoteMediator استشعار وصول التمرير للحواف لجلب صفحات إضافية من الشبكة. وتُحفظ مؤشرات الصفحات في جدول RemoteKeys، وتُنسق عمليات المسح والإضافة داخل Transaction واحدة لمنع وميض الشاشة.",
        "best_answer_ar": "معمارية تصفح القوائم الكبيرة باستخدام Paging 3 و RemoteMediator تمثل الحل القياسي للتطبيقات التي تتطلب أداءً فائقاً ودعماً كاملاً للعمل دون اتصال.\n\nفي هذه المعمارية، تنفصل واجهة المستخدم تماماً عن الشبكة؛ حيث تقرأ الشاشات تدفق البيانات حصرياً من قاعدة بيانات Room عبر PagingSource، مما يضمن عرض العناصر في أجزاء من الثانية دون انتظار استجابة السيرفر، مع الاحتفاظ التام بموضع التمرير عند إعادة تشغيل التطبيق.\n\nويتدخل وسيط المزامنة RemoteMediator كحلقة وصل ذكية؛ حيث يراقب موضع التمرير، وعند اقتراب المستخدم من نهاية القائمة، يطلق Paging 3 استدعاء load بنوع APPEND، فيقوم الوسيط بقراءة مؤشر الصفحة التالية من جدول مخصص في Room يسمى RemoteKeys، ويطلب البيانات من السيرفر ويحفظها في قاعدة البيانات، فتقوم Room تلقائياً بتغذية الشاشة بالعناصر الجديدة.\n\nوعند قيام المستخدم بالسحب للتحديث Swipe-to-refresh، نمرر نوع REFRESH؛ وهنا نطبق معاملة ذرية db.withTransaction لمسح المفاتيح القديمة والبيانات السابقة وإدخال الصفحة الأولى الجديدة معاً، مما يمنع وميض الشاشة أو قفز القائمة ويمنح المستخدم تجربة تمرير ناعمة ومستمرة.",
        "deep_answer_ar": "في تصميم أنظمة أندرويد المعقدة كمنصات الأخبار ومواقع التجارة الإلكترونية، يعتبر تطبيق الـ Pagination عبر استدعاءات الشبكة المباشرة خطأ هندسياً يؤدي لتجربة استخدام متقطعة وفقدان كامل لموضع التمرير عند انقطاع الاتصال.\n\nتوفر مكتبة Paging 3 مع RemoteMediator فصلاً معمارياً حاسماً بين طبقة العرض ومحرك المزامنة؛ فالواجهة تستهلك PagingData ناتجة عن استعلامات SQLite محلية ومحسوبة بدقة. وعندما يصل التمرير لحدود prefetchDistance، يطلق النظام دالة RemoteMediator في الخلفية. وتكمن الصعوبة في إدارة مؤشرات الصفحات Cursors عبر دورات حياة التطبيق؛ ولذلك ننشئ جدولاً مستقلاً RemoteKeys يحفظ مفاتيح nextKey و prevKey لكل عنصر، مما يحمي النظام من التخبط عند استقبال صفحات متداخلة.\n\nوفي حالات التحديث الشامل LoadType.REFRESH، نلزم الكود بتنفيذ عمليات المسح والتخزين داخل نطاق db.withTransaction؛ وهذا يضمن التبديل الذري للبيانات، حيث تلتقط Room التعديل وتحدث الشاشة بسلاسة دون أن يرى المستخدم أي شاشات تحميل بيضاء أو قفزات مفاجئة في موضع القائمة.\n\nكما تستفيد هذه المعمارية من إدارة حالات التحميل LoadState؛ فإذا فشلت الشبكة أثناء التمرير في مكان ضعيف التغطية، تظل العناصر السابقة معروضة ومستقرة، وتظهر رسالة خطأ موضعية في أسفل القائمة Footer مع زر لإعادة المحاولة، مما يوفر تجربة تصفح متكاملة وممتعة بمعدل 120 إطاراً في الثانية."
    }
}

# ==========================================
# DAT-14: How do you design retries while respecting idempotency and rate limits?
# ==========================================
DATA["DAT-14"] = {
    "concept_en": """Designing resilient network retry architectures requires balancing recovery from transient failures against server protection and transactional safety:
- Idempotency & Operation Identity:
  * Safe vs Unsafe Retries: HTTP GET, PUT, and DELETE are idempotent by specification and can be retried automatically upon network dropouts. In contrast, POST requests modify server state (such as placing orders or charging payments).
  * Idempotency Keys: Mobile applications must inject client-generated UUIDs (e.g., X-Idempotency-Key) into mutable operations and persist them in Room alongside the pending request. This ensures that if a network timeout occurs after the server processed the transaction, retrying with the identical key deduplicates the operation on the backend without duplicate charges.
- Exponential Backoff with Jitter:
  * Exponential Delay Formula: Delay doubles with each successive failure: T = Base * 2^(attempt).
  * Full Jitter: Adding randomized randomness (delay = random(0, T)) breaks synchronization among thousands of mobile devices recovering from an outage, preventing the 'thundering herd' spike from crashing recovering infrastructure.
- Server Throttling & 429/503 Governance:
  * Parse Retry-After: When a backend returns HTTP 429 (Too Many Requests) or HTTP 503 (Service Unavailable), the client must extract the Retry-After header (in seconds or HTTP-date) and halt all retries until that window elapses.
  * Fatal Error Classification: Client errors (400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found) are non-transient and must fail immediately without retrying, conserving radio battery.""",
    "walkthrough_en": """Production retry policy combining exponential backoff, jitter, and Retry-After handling:
```kotlin
suspend fun <T> retryWithBackoff(
    maxAttempts: Int = 3,
    initialDelayMs: Long = 1000L,
    maxDelayMs: Long = 10000L,
    factor: Double = 2.0,
    block: suspend () -> Response<T>
): Response<T> {
    var currentDelay = initialDelayMs

    repeat(maxAttempts - 1) { attempt ->
        try {
            val response = block()
            if (response.isSuccessful) return response

            // 1. Handle Server Rate Limits (429 or 503)
            val statusCode = response.code()
            if (statusCode == 429 || statusCode == 503) {
                val retryAfterSec = response.headers()["Retry-After"]?.toLongOrNull() ?: (currentDelay / 1000)
                delay(retryAfterSec * 1000L)
            } else if (statusCode in 400..499) {
                // Fatal client error; do not retry
                return response
            }
        } catch (e: IOException) {
            // Transient network failure: proceed with jittered backoff
        }

        // 2. Exponential Backoff with Full Jitter
        val jitteredDelay = Random.nextLong(0, currentDelay)
        delay(jitteredDelay)
        currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelayMs)
    }

    return block() // Final attempt
}
```""",
    "short_en": """Designing retries requires respecting idempotency by attaching client UUID keys to POST requests, applying exponential backoff with randomized jitter to prevent thundering herd spikes, and honoring Retry-After headers on 429 and 503 responses while failing client errors immediately.""",
    "structured_en": """A resilient mobile retry strategy must protect the backend from cascading collapse while recovering gracefully from flaky cellular connections.
First, retries must respect operation idempotency. While GET and PUT are safe to retry automatically, state-changing POST requests require unique client-generated idempotency keys to guarantee that network timeouts do not trigger duplicate transactions or charges.
Second, retry timing must incorporate exponential backoff with jitter. Rather than retrying at fixed intervals, the client doubles delay intervals and adds randomized variance, de-synchronizing thousands of client retries.
Third, the client must strictly adhere to server backpressure signals. When receiving HTTP 429 Too Many Requests or 503 Service Unavailable, the client parses the Retry-After header and suspends requests. Non-retryable 4xx client errors abort immediately to conserve battery.""",
    "deep_senior_en": """In large-scale distributed systems, naive client retry loops frequently cause catastrophic self-inflicted Denial of Service (DoS) outages.
When an edge gateway experiences a transient hiccup, thousands of mobile clients fail simultaneously.
If every app retries immediately or at fixed 2-second intervals, the client fleet forms a synchronized wave of traffic that repeatedly hammers the recovering backend, keeping it down permanently in an outage death spiral.
To prevent this, our retry policy enforces three mandatory architectural rules.
First, we apply Full Jitter to our exponential backoff formula.
Randomizing the backoff sleep duration across the interval [0, Base * 2^attempt] flattens the retry curve into a smooth, manageable background distribution that allows servers to recover gracefully.
Second, we implement strict status code classification.
Transient transport failures like SocketTimeoutException and server 5xx codes warrant retries.
Conversely, client errors such as 400 Bad Request, 401 Unauthorized, or 403 Forbidden indicate non-recoverable state; retrying them is a bug that wastes CPU cycles and battery power.
When receiving a 429 or 503, our interceptor parses the Retry-After header and halts automated background sync for the specified duration.
Finally, for all mutating financial operations, we require an X-Idempotency-Key.
Even if a cellular connection drops and the client re-executes the transaction via WorkManager three hours later, the backend identifies the key and returns the cached receipt without charging the customer twice.""",
    "meta_ar": {
        "id": "DAT-14",
        "questionAr": "كيف تصمم استراتيجيات إعادة المحاولة (Retries) مع احترام معايير الـ Idempotency ومعدلات السيرفر (Rate Limits)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "القدرة على تصميم سياسات إعادة المحاولة الذكية، وتطبيق التراجع الأسي مع التباين العشوائي (Exponential Backoff with Jitter)، واحترام ترويسة Retry-After ومفاتيح Idempotency.",
        "concept_ar": "يتطلب التصميم الاحترافي لإعادة محاولة الطلبات حماية السيرفر من الانهيار ومراعاة استهلاك طاقة الهاتف: التمييز الدلالي للعمليات بحيث تُعاد محاولة استدعاءات GET و PUT و DELETE بأمان لأنها Idempotent بطبيعتها، بينما يُحظر إعادة محاولة طلبات POST المالية إلا بوجود مفتاح عدم التكرار (Idempotency Key) محفوظ محلياً لمنع الخصم المزدوج. وتطبيق خوارزمية التراجع الأسي مع التباين العشوائي (Exponential Backoff with Jitter) لمضاعفة زمن الانتظار بعد كل فشل وإضافة قيمة عشوائية تفك تزامن ملايين الأجهزة وتمنع هجوم Thundering Herd على السيرفر المتعافي. واحترام ترويسات تحديد المعدل كترويسة Retry-After عند استقبال كود 429 أو 503 بوقف الطلبات فوراً للمدة المحددة، مع إنهاء المحاولات فوراً عند أخطاء العميل 4xx (كالخطأ 400 و 403) لتوفير البطارية.",
        "walkthrough_ar": """تطبيق خوارزمية التراجع الأسي مع Jitter واحترام Retry-After:
```kotlin
suspend fun <T> safeRetry(
    maxAttempts: Int = 3,
    block: suspend () -> Response<T>
): Response<T> {
    var delayMs = 1000L

    repeat(maxAttempts - 1) {
        val response = runCatching { block() }.getOrNull()

        if (response != null && response.isSuccessful) return response

        // 1. احترام ترويسة Retry-After لأكواد 429 و 503
        if (response?.code() in listOf(429, 503)) {
            val retryAfter = response?.headers()?.get("Retry-After")?.toLongOrNull() ?: (delayMs / 1000)
            delay(retryAfter * 1000L)
        } else if (response != null && response.code() in 400..499) {
            return response // خطأ حتمي من العميل، لا تعيد المحاولة
        }

        // 2. تراجع أسي مع تباين عشوائي (Jitter)
        val jitter = Random.nextLong(0, delayMs)
        delay(jitter)
        delayMs = (delayMs * 2).coerceAtMost(8000L)
    }
    return block()
}
```""",
        "why_it_matters_ar": "يمنع تدمير خوادم الباك إند عبر هجمات الإنكار العشوائية DDOS غير المقصودة الصادرة من ملايين الهواتف، ويحمي حسابات المستخدمين من التكرار والخصم المالي المزدوج.",
        "worked_example_ar": "تعرض خوادم البنك لعطل مؤقت لمدة 30 ثانية؛ بدلاً من أن تقوم تطبيقات العملاء بإرسال آلاف الطلبات في نفس الثانية فتسقط السيرفر مجدداً، يتوزع ضغط المحاولات بفضل الـ Jitter و Retry-After بسلاسة.",
        "trade_offs_ar": "إضافة الـ Jitter والانتظار الأسي قد يؤخر إشعار المستخدم بنتيجة العملية لثوانٍ معدودة، ولكنه الضمان الوحيد لاستعادة استقرار الخدمة ونجاح العمليات.",
        "failure_modes_ar": "إعادة المحاولة المباشرة وبفواصل زمنية ثابتة مما يسقط السيرفر في حلقة انهيار دائمة، أو إعادة محاولة أخطاء 400 و 403 مما يفرغ بطارية الهاتف في محاولات محكومة بالفشل المسبق.",
        "production_perspective_ar": "في كبرى المنصات، نحدد سقفاً لا يتجاوز 3 محاولات للاستدعاءات المباشرة، ونلزم كافة الفرق باستخدام مفاتيح UUID لطلبات الدفع، مع تفعيل WorkManager للمهام المؤجلة الأطول من دقيقة.",
        "how_to_answer_ar": "قسم الإجابة إلى ثلاثة محاور: احترام دلالات الـ Idempotency، خوارزمية التراجع الأسي مع الـ Jitter لمنع الـ Thundering Herd، والتعامل الصارم مع كود 429 وترويسة Retry-After.",
        "talking_points_ar": "مفهوم الـ Full Jitter، دور Retry-After في حماية الباك إند، ومخاطر إعادة محاولة طلبات POST بدون مفتاح Idempotency.",
        "follow_ups_ar": "- **المحاور:** 'لماذا نضيف قيمة عشوائية Jitter بدلاً من الاكتفاء بالتراجع الأسي فقط؟'\n  **المرشح:** 'لأنه بدون Jitter ستتراجع جميع الأجهزة في نفس الثانية وتعود لتضرب السيرفر معاً في موجات متزامنة، بينما يقوم Jitter ببعثرة الطلبات زمنياً ليتعافى السيرفر بسلاسة.'\n\n- **المحاور:** 'هل تعيد محاولة الطلب إذا استجاب السيرفر بكود 404 أو 400؟'\n  **المرشح:** 'قطعاً لا؛ لأنها أخطاء منطقية من جانب العميل أو المورد غير موجود، وتكرار المحاولة لن يغير النتيجة بل سيستنزف البطارية ويولد بيانات تالفة.'",
        "self_check_ar": "هل شرحت سبب أهمية الـ Jitter بدقة رياضية ومعمارية؟ وهل بينت كيفية احترام Retry-After ومفاتيح الـ Idempotency؟",
        "references_ar": f"- [AWS Architecture: Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) — التحليل الرياضي لأهمية الـ Jitter في الشبكات.\n- [RFC 6585: Additional HTTP Status Codes](https://datatracker.ietf.org/doc/html/rfc6585#section-4) — توثيق كود 429 ومحددات معدل الطلبات.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "يصمم نظام إعادة المحاولة باحترام الـ Idempotency عبر إرفاق مفاتيح UUID لطلبات POST، وتطبيق التراجع الأسي مع التباين العشوائي Jitter لبعثرة الطلبات ومنع إسقاط السيرفر، مع التوقف الإجباري للمدة المحددة في ترويسة Retry-After عند كود 429 و 503، وعدم إعادة محاولة أخطاء العميل 4xx إطلاقاً.",
        "best_answer_ar": "تصميم استراتيجية إعادة المحاولة في تطبيقات أندرويد الحديثة يتطلب توازناً هندسياً دقيقاً بين استعادة الاتصال وحماية البنية التحتية للخوادم من الانهيار.\n\nالركيزة الأولى هي احترام دلالات الـ Idempotency؛ فالطلبات الآمنة مثل GET و PUT يمكن إعادة محاولتها تلقائياً عند انقطاع الاتصال، بينما يحظر إعادة محاولة طلبات POST كالدفع والتحويل المالي إلا بعد إرفاق مفتاح X-Idempotency-Key فريد ومسجل في قاعدة البيانات المحلية، مما يضمن أن السيرفر إذا كان قد نفذ العملية سابقاً سيرجع الرد القديم دون تكرار الخصم.\n\nالركيزة الثانية هي التراجع الأسي مع التباين العشوائي Exponential Backoff with Jitter؛ فبدلاً من إعادة المحاولة في فترات ثابتة تضرب السيرفر في موجات موحدة، نقوم بمضاعفة فترة الانتظار مع إضافة قيمة عشوائية تبعثر أوقات طلبات ملايين الهواتف، مما يكسر ظاهرة Thundering Herd ويسمح للسيرفر بالتعافي بهدوء.\n\nالركيزة الثالثة هي الامتثال الصارم لإشارات السيرفر؛ فعند استقبال كود 429 لتجاوز معدل الطلبات أو 503 لعدم توفر الخدمة، نفحص ترويسة Retry-After ونوقف كافة المحاولات حتى انقضاء المدة المحددة، مع الإلغاء الفوري للمحاولات عند حدوث أخطاء 4xx مثل 400 أو 403 لتوفير موارد الجهاز وبطاريته.",
        "deep_answer_ar": "في قيادة المنظومات التقنية الموزعة، تدرك الفرق الهندسية أن أخطاء إعادة المحاولة البدائية من جهة العميل هي السبب الأول لانهيار الخوادم في حلقة موت مستمرة Outage Death Spiral.\n\nعندما يتعرض السيرفر لضغط مفاجئ أو خلل عابر في قاعدة البيانات، تفشل آلاف الطلبات المتزامنة. فإذا كان كود تطبيق أندرويد يعيد المحاولة كل ثانية، فإن ملايين الأجهزة تشكل هجوماً جماعياً موزعاً DDOS غير مقصود يعيد إسقاط السيرفر في اللحظة التي يحاول فيها استعادة نشاطه. ولمعالجة ذلك، نلزم كافة تطبيقاتنا بتطبيق خوارزمية Full Jitter؛ حيث يُحسب التأخير كقيمة عشوائية بين صفر والحد الأقصى للتراجع الأسي، مما يحول موجات الضغط العاتية إلى تدفق ناعم وموزع بانتظام يستطيع السيرفر استيعابه.\n\nكما نطبق فحصاً دقيقاً لأكواد الاستجابة؛ فالأخطاء الحتمية مثل 400 Bad Request أو 401 أو 404 لا تخضع لإعادة المحاولة مطلقاً لأنها تتطلب تدخلاً برمجياً أو تعديلاً في المدخلات. وفي المقابل، نلتزم تماماً بترويسة Retry-After؛ فإذا طلب السيرفر الانتظار لستين ثانية، تعلق طبقة الشبكة كافة المهام المعنية لتلك المدة حمايةً للبنية التحتية.\n\nأما في العمليات المالية الحساسة، فإننا نربط المعاملة برقم تعريفي UUID ثابت في قاعدة بيانات Room ونرسله كترويسة Idempotency؛ فلو انقطع الاتصال وأعاد WorkManager إرسال الطلب بعد ساعة، يكتشف السيرفر العملية من الكاش الموزع ويرجع النتيجة دون إجراء أي خصم بنكي إضافي، مما يحقق الموثوقية القصوى للنظام."
    }
}

# ==========================================
# DAT-15: How do you sync local writes after offline edits?
# ==========================================
DATA["DAT-15"] = {
    "concept_en": """Synchronizing local offline mutations with remote backends requires implementing a durable, transactional outbox architecture:
- The Outbox Pattern (Local Mutation Queue):
  * Mutation Entity: Offline writes (create, update, delete) are committed immediately to the local database for instant UI feedback (optimistic updates), while a corresponding record is written atomically into a SyncMutationEntity table.
  * Schema Attributes: Stored mutations contain a unique client mutationId (UUID), entityType, entityId, operation (INSERT/UPDATE/DELETE), payload JSON, creation timestamp, and syncStatus (PENDING, IN_FLIGHT, FAILED).
- Durable Background Dispatch via WorkManager:
  * Constraints & Resilience: Synchronization is orchestrated by Jetpack WorkManager configured with NetworkType.CONNECTED. Because WorkManager schedules tasks in an internal SQLite database, pending edits survive app process termination, background OS memory reclaim, and full device reboots.
  * Causal Ordering (FIFO Execution): Mutations targeting the same entity must execute sequentially in strict chronological order to prevent out-of-order race conditions (e.g., executing a DELETE before an UPDATE completes).
- Two-Phase Reconciliation & Error Handling:
  * Upon successful backend ingestion, the server returns the canonical entity version or updated timestamp. The local client updates the domain entity and purges the mutation from the outbox in a single Room transaction.
  * If the server rejects the edit due to validation or schema conflicts, the client marks the mutation as FAILED and triggers conflict resolution policies.""",
    "walkthrough_en": """Transactional outbox pattern for offline writes and WorkManager synchronization:
```kotlin
// 1. Mutation Entity tracking pending offline operations
@Entity(tableName = "sync_mutations")
data class SyncMutationEntity(
    @PrimaryKey val mutationId: String = UUID.randomUUID().toString(),
    val entityType: String,
    val entityId: String,
    val action: String, // CREATE, UPDATE, DELETE
    val payloadJson: String,
    val createdAt: Long = System.currentTimeMillis()
)

// 2. Repository coordinates optimistic write and durable queueing atomically
class NoteRepositoryImpl(
    private val db: AppDatabase,
    private val workManager: WorkManager
) : NoteRepository {
    override suspend fun updateNote(id: String, newContent: String) = db.withTransaction {
        // Optimistic UI update
        db.noteDao().updateContent(id, newContent)

        // Queue durable mutation into outbox
        val mutation = SyncMutationEntity(
            entityType = "NOTE",
            entityId = id,
            action = "UPDATE",
            payloadJson = Json.encodeToString(NoteUpdatePayload(newContent))
        )
        db.syncDao().insertMutation(mutation)

        // Trigger guaranteed background sync
        val syncRequest = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
            .build()
        workManager.enqueueUniqueWork("sync_outbox", ExistingWorkPolicy.KEEP, syncRequest)
    }
}
```""",
    "short_en": """Syncing offline writes requires the outbox pattern where mutations are saved in Room alongside optimistic UI updates in a single transaction. WorkManager monitors network availability to dispatch queued mutations sequentially in FIFO order, updating local database entities and pruning the outbox upon successful server confirmation.""",
    "structured_en": """Implementing offline write synchronization requires a resilient outbox architecture combined with durable background scheduling.
First, when a user edits data offline, we perform an optimistic write: the entity is updated immediately in Room for instant UI feedback, while an immutable mutation record is saved atomically in a local SyncMutation outbox table.
Second, we trigger background synchronization via Jetpack WorkManager with a CONNECTED network constraint. Because WorkManager persists work in SQLite, queued sync tasks survive process death and system reboots.
Third, the sync worker executes mutations in strict FIFO causal order. Once the server acknowledges the payload, Room updates the local entity with server timestamps and purges the mutation from the outbox in an atomic transaction.""",
    "deep_senior_en": """In enterprise offline-first engineering, ensuring that user edits made in flight mode or underground subways sync durably without data loss is a core architectural requirement.
A common failure mode is firing coroutines directly inside the repository without local durability.
If the user edits three notes and immediately swipes the app away from recent tasks, in-memory coroutines are killed instantly by the Android runtime, permanently losing those edits.
To guarantee durability, we enforce the transactional Outbox Pattern.
When the user modifies an entity, we open a Room db.withTransaction block.
Within this single atomic transaction, we apply the optimistic write to our main entity table and simultaneously append a SyncMutation record into our persistent outbox table.
We then enqueue a unique WorkManager task with NetworkType.CONNECTED and exponential backoff policies.
Because WorkManager leverages an internal SQLite store, the task is immune to process termination and device reboots.
When network connectivity is established, our SyncWorker drains the outbox queue in strict First-In, First-Out (FIFO) chronological sequence.
Executing mutations sequentially per entity is critical: if an edit is followed by a delete, running them concurrently across threads could cause the delete to execute first, resulting in the edit reviving a deleted entity.
Upon successful HTTP 200 confirmation from the server, we remove the mutation from the outbox table and mark the local record as fully synchronized.""",
    "meta_ar": {
        "id": "DAT-15",
        "questionAr": "كيف تُزامن التعديلات المحلية (Local Writes) مع السيرفر بعد العمل دون اتصال (Offline Edits)؟",
        "topicAr": TOPIC_AR,
        "evaluates_ar": "فهم نمط صندوق الصادر (Outbox Pattern)، وضمان حفظ التعديلات محلياً بـ Transaction، وإدارة طابور المزامنة بترتيب زمني FIFO عبر WorkManager وحل مشاكل قتل التطبيق.",
        "concept_ar": "تتطلب مزامنة التعديلات المنفذة دون اتصال مع الخادم تطبيق نمط صندوق الصادر (Transactional Outbox Pattern): عند قيام المستخدم بإنشاء أو تعديل أو حذف أي بيان، يُنفذ التعديل في قاعدة البيانات المحلية فوراً لتحديث الشاشة بلحظتها (Optimistic Update)، ويُحفظ في نفس الوقت سجل غير قابل للتعديل داخل جدول طابور المزامنة (SyncMutations) ذرياً داخل @Transaction واحدة لمنع ضياع التعديل في حال إغلاق التطبيق. وتُجدول عملية المزامنة عبر Jetpack WorkManager مع شرط توفر الإنترنت (NetworkType.CONNECTED)، مما يضمن بقاء المهمة محفوظة في نظام التشغيل حتى لو أُعيد تشغيل الجهاز أو قُتلت العملية. وينفذ عامل المزامنة SyncWorker التعديلات بترتيب زمني صارم (FIFO) بحسب وقت الإنشاء لتفادي تعارض العمليات المتتالية على نفس العنصر، ثم يحذف السجل من صندوق الصادر بعد استلام تأكيد النجاح من السيرفر.",
        "walkthrough_ar": """تطبيق نمط Outbox والمزامنة الموثوقة عبر WorkManager:
```kotlin
// 1. جدول صندوق الصادر لحفظ العمليات المعلقة
@Entity(tableName = "outbox_mutations")
data class MutationEntity(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val action: String, // UPDATE, DELETE
    val payloadJson: String,
    val timestamp: Long = System.currentTimeMillis()
)

// 2. المستودع ينفذ التعديل ويحفظ العملية ذرياً
class TaskRepository(private val db: AppDatabase, private val wm: WorkManager) {
    suspend fun updateTask(id: String, title: String) = db.withTransaction {
        // تحديث محلي فوري للشاشة
        db.taskDao().updateTitle(id, title)

        // حفظ العملية في صندوق الصادر
        db.outboxDao().insert(MutationEntity(action = "UPDATE", payloadJson = "{...}"))

        // جدولة المزامنة بضمان WorkManager
        val request = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
            .build()
        wm.enqueueUniqueWork("sync_tasks", ExistingWorkPolicy.APPEND, request)
    }
}
```""",
        "why_it_matters_ar": "يضمن عدم فقدان أي تعديل قام به المستخدم أثناء السفر أو انقطاع الشبكة حتى لو أُغلق التطبيق أو نَفِدت بطارية الهاتف، مما يوفر تجربة مستخدم موثوقة بنسبة مئة بالمئة.",
        "worked_example_ar": "تطبيق إدارة مهام يسمح للمستخدم بإنهاء مهام وإعادة ترتيبها أثناء الطيران؛ يتم حفظ كافة التعديلات في جدول Outbox، وفور هبوط الطائرة واتصال الهاتف بالشبكة، يقوم WorkManager بمزامنة كافة التعديلات بهدوء.",
        "trade_offs_ar": "يوفر نمط Outbox موثوقية لا تضاهى ولكنه يتطلب بناء جداول إضافية لإدارة الطابور وكتابة منطق متقدم لفك تسلسل البيانات ومعالجة حالات فشل الشبكة.",
        "failure_modes_ar": "الاعتماد على خيوط Coroutines مؤقتة في الذاكرة لمزامنة التعديلات مما يضيع كل شيء إذا أُغلق التطبيق فوراً، أو إرسال التعديلات بترتيب عشوائي مما يجعل عملية الحذف تسبق التعديل وتفسد البيانات.",
        "production_perspective_ar": "في تطبيقات المؤسسات الكبرى، نمنع نهائياً حفظ التعديلات دون قيدها في جدول Outbox المحلي، ونفرض تنفيذ العمليات بترتيب زمني صارم FIFO لكل كيان لتفادي تعارض البيانات.",
        "how_to_answer_ar": "اشرح المشكلة المعمارية أولاً (خطر فقدان البيانات عند قتل العملية)، ثم اشرح نمط Outbox وحفظ التعديل في Room ذرياً، واختم بدور WorkManager والترتيب الزمني FIFO.",
        "talking_points_ar": "نمط Transactional Outbox، دور WorkManager في البقاء بعد قتل التطبيق، وأهمية الترتيب الزمني FIFO لمنع تعارض العمليات.",
        "follow_ups_ar": "- **المحاور:** 'لماذا يجب تنفيذ التعديلات المعلقة بترتيب زمني صارم FIFO؟'\n  **المرشح:** 'لأنه لو عدل المستخدم عنصراً ثم حذفه دون اتصال، وتم إرسال الحذف أولاً ثم التعديل، فسيقوم السيرفر بإعادة إنشاء العنصر المحذوف بدلاً من إبقائه محذوفاً.'\n\n- **المحاور:** 'ماذا يحدث لو رفض السيرفر تعديلاً بسبب تعارض في البيانات Validation Error؟'\n  **المرشح:** 'يتم تمييز العملية في جدول Outbox كعملية فاشلة FAILED، وإخطار المستخدم بالتعارض أو التراجع عن التعديل المحلي لاستعادة حالة السيرفر الأصلية.'",
        "self_check_ar": "هل شرحت نمط Outbox بوضوح؟ وهل بينت كيف يحمي WorkManager البيانات من الضياع عند إغلاق التطبيق وأهمية الترتيب الزمني FIFO؟",
        "references_ar": f"- [Offline-First Outbox Pattern](https://developer.android.com/topic/architecture/data-layer/offline-first#workmanager) — إرشادات جوجل لتطبيق نمط صندوق الصادر والمزامنة.\n- [WorkManager Guaranteed Execution](https://developer.android.com/topic/libraries/architecture/workmanager) — توثيق جوجل لضمان تنفيذ المهام الخلفية بعد إعادة التشغيل.\n\n{REVIEWED_DATE_AR}",
        "quick_answer_ar": "تُزامن التعديلات المنفذة دون اتصال عبر نمط صندوق الصادر Outbox Pattern؛ حيث يُحفظ التعديل محلياً فوراً للواجهة ويُسجل في جدول طابور المزامنة ذرياً داخل Transaction واحدة. ويتولى WorkManager ضمان رفع التعديلات بترتيب زمني صارم FIFO متى توفرت الشبكة حتى لو أُغلق التطبيق أو أُعيد تشغيل الهاتف.",
        "best_answer_ar": "مزامنة التعديلات التي يجريها المستخدم دون اتصال تتطلب بنية تحتية تضمن عدم ضياع أي حرف حتى في أصعب الظروف التشغيلية.\n\nالخطأ الشائع هو تنفيذ التعديلات عبر Coroutines عادية في الذاكرة؛ فلو كتب المستخدم ملاحظة وأغلق التطبيق فوراً، سيقوم نظام أندرويد بقتل العملية وتضيع التعديلات للأبد. الحل القياسي هو تطبيق نمط صندوق الصادر Transactional Outbox Pattern؛ فعندما يقوم المستخدم بأي تعديل، نفتح معاملة ذرية db.withTransaction نقوم فيها بتحديث الكيان المحلي لتنعكس النتيجة على الشاشة بلحظتها، وفي ذات المعاملة نضيف سجلاً غير قابل للتعديل في جدول مخصص يسمى outbox_mutations يحتوي على نوع العملية والبيانات وتوقيتها الزمني.\n\nبعد ذلك، نسجل مهمة مزامنة عبر Jetpack WorkManager مع شرط توفر الإنترنت NetworkType.CONNECTED؛ ونظراً لأن WorkManager يحفظ مهامه داخل قاعدة بيانات النظام في SQLite، فإن العملية تظل حية ومحفوظة حتى لو نَفِدت بطارية الهاتف أو أُعيد تشغيله.\n\nوعند استعادة الاتصال، يبدأ الـ SyncWorker في قراءة العمليات من صندوق الصادر وتنفيذها بترتيب زمني صارم FIFO؛ وهذا الترتيب جوهري لمنع حدوث أخطاء تعارض منطقية، كأن يُنفذ حذف عنصر قبل تعديله، وفور استلام رد النجاح من السيرفر، تُحذف العملية من صندوق الصادر وتُثبت كعملية متزامنة ونهائية.",
        "deep_answer_ar": "في المعمارية المتقدمة لتطبيقات الموبايل الموثوقة، تعتبر مزامنة العمليات المنفذة دون اتصال اختباراً حقيقياً لقوة التصميم الهندسي للمنصة.\n\nالمبدأ الحاكم هو أن أي عملية كتابة تفاعلية يجب أن تكتسب صفة الدوام Durability محلياً قبل أي تفاعل مع الشبكة. ولذلك ندمج التحديث المتفائل للشاشة وحفظ سجل الـ Mutation داخل معاملة واحدة في Room؛ فإذا انقطع التيار أو تجمد النظام في تلك اللحظة، إما أن تُسجل العملية بالكامل في صندوق الصادر وتنعكس على الشاشة، أو لا يحدث أي شيء، مما يمنع التناقض الداخلي.\n\nوتبرز أهمية WorkManager في قدرته على تجاوز حدود دورة حياة التطبيق؛ فهو يعمل كمنسق موثوق مع نظام التشغيل لجدولة العمليات عند توفر الشبكة ومراعاة أوضاع توفير الطاقة Doze Mode. وعند استيقاظ الـ SyncWorker، نقوم بقفل طابور العمليات لكل كيان على حدة لضمان تنفيذ التعديلات بتسلسل زمني FIFO دقيق؛ فلو قام المستخدم بتعديل ملف ثم حذفه، فإن إرسال العمليات بالتوازي قد يجعل التعديل يصل بعد الحذف ويعيد إحياء الملف المحذوف كخطأ برمجي شبحي Zombie Entity.\n\nوعند استجابة السيرفر بنجاح بكود 200، نقوم بحذف السجل من جدول Outbox وتحديث التوقيع الزمني المحلي في قاعدة البيانات ذرياً. أما في حال رفض السيرفر للعملية بسبب تعارض القواعد Validation Conflict، نقوم بوضع علامة FAILED وتنبيه المستخدم أو التراجع عن التعديل، مما يضمن اتساق البيانات التام بين العميل والخادم في كافة السيناريوهات الميدانية."
    }
}

# ==========================================
# Runner & Validation
# ==========================================
def validate_words():
    for qid, d in sorted(DATA.items()):
        short_w = len(d["short_en"].split())
        struct_w = len(d["structured_en"].split())
        deep_w = len(d["deep_senior_en"].split())
        assert 35 <= short_w <= 110, f"{qid} short_en {short_w} out of [35, 110]"
        assert 100 <= struct_w <= 280, f"{qid} struct_en {struct_w} out of [100, 280]"
        assert 200 <= deep_w <= 650, f"{qid} deep_en {deep_w} out of [200, 650]"

        q_ar_w = len(d["meta_ar"]["quick_answer_ar"].split())
        b_ar_w = len(d["meta_ar"]["best_answer_ar"].split())
        d_ar_w = len(d["meta_ar"]["deep_answer_ar"].split())
        assert 35 <= q_ar_w <= 110, f"{qid} quick_ar {q_ar_w} out of [35, 110]"
        assert 90 <= b_ar_w <= 280, f"{qid} best_ar {b_ar_w} out of [90, 280]"
        assert 180 <= d_ar_w <= 650, f"{qid} deep_ar {d_ar_w} out of [180, 650]"
        print(f"{qid}: en_s={short_w}, en_st={struct_w}, en_d={deep_w} | ar_q={q_ar_w}, ar_b={b_ar_w}, ar_d={d_ar_w}")
    print("Pre-validation word count checks passed! Updating canonical questions...")

def apply_elevations():
    validate_words()

    topic_meta = {}
    for qid, d in sorted(DATA.items()):
        ee.update_canonical_question(
            qid=qid,
            concept_en=d["concept_en"],
            walkthrough_en=d["walkthrough_en"],
            structured_en=d["structured_en"],
            deep_senior_en=d["deep_senior_en"],
            short_en=d["short_en"],
        )
        topic_meta[qid] = d["meta_ar"]

    ee.save_topic_metadata("dat_08_15", topic_meta)
    ee.merge_all_metadata()

    for qid in sorted(DATA.keys()):
        errs = ee.validate_question(qid)
        if errs:
            print(f"Errors in {qid}:")
            for er in errs:
                print(f"  ❌ {er}")
            sys.exit(1)

    print(f"\\nAll {len(DATA)} DAT questions (DAT-08 to DAT-15) successfully elevated and passed validation!\\n")

if __name__ == "__main__":
    apply_elevations()
