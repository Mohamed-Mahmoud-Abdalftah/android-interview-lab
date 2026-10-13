#!/usr/bin/env python3
"""Generator for DAT-08 through DAT-14 elevation data."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "dat.json"

DAT_08_14 = [
    {
        "id": "DAT-08",
        "arabic_explanation": (
            "مقارنة استراتيجيات التخزين المؤقت في Android:\nCache-First، و Network-First، و Stale-While-Revalidate، ومتى تختار كل استراتيجية؟\n\n"
            "1. Cache-First (قراءة الكاش أولاً):\n   - **كيف تعمل**: يبحث التطبيق في الكاش المحلي (Room / Disk Cache). إذا وُجدت البيانات ولم تنتهِ صلاحيتها، يتم عرضها فوراً ولا يتم الاتصال بالشبكة على الإطلاق. إذا لم تكن موجودة أو انتهت صلاحيتها، يتصل بالشبكة ويحفظ النتيجة في الكاش.\n   - **المميزات**: سرعة فائقة (0-5ms)، توفير كبير لبيانات الهاتف والبطارية، وتخفيف الحمل على السيرفر.\n   - **العيوب**: خطر عرض بيانات قديمة (Stale Data).\n   - **أفضل استخدام**: البيانات شبه الثابتة (قائمة الدول، إعدادات التطبيق، بيانات التصنيفات، الصور والـ Assets).\n\n"
            "2. Network-First (الاتصال بالشبكة أولاً والرجوع للكاش عند الفشل):\n   - **كيف تعمل**: يحاول التطبيق الاتصال بالسيرفر أولاً. إذا نجح، يعرض أحدث بيانات ويحدث الكاش. إذا انقطع الاتصال أو حدث Timeout، يرجع للكاش ويعرض آخر نسخة محفوظة مع تنبيه المستخدم.\n   - **المميزات**: حداثة البيانات دائماً (Fresh Data Guaranteed).\n   - **العيوب**: بطء العرض وظهور مؤشر التحميل (Loading Spinner) دائماً، واعتمادية كاملة على سرعة الشبكة.\n   - **أفضل استخدام**: البيانات الحساسة جداً التي لا تحتمل الخطأ (رصيد الحساب البنكي، أسعار الأسهم والعملات، حالة شحن الطلب المالي).\n\n"
            "3. Stale-While-Revalidate (عرض الكاش فوراً ثم التحديث في الخلفية):\n   - **كيف تعمل**: المعيار الذهبي في تطبيقات الموبايل الحديثة! يعرض التطبيق أحدث نسخة في الكاش فوراً في 5ms حتى يشاهد المستخدم المحتوى دون أي انتظار، وفي نفس اللحظة يطلق طلباً في الخلفية لجلب أحدث البيانات وتحديث الكاش والـ UI تلقائياً.\n   - **أفضل استخدام**: الـ Feeds الإخبارية، وسائل التواصل الاجتماعي (Twitter/Instagram feed)، وقوائم المنتجات في التجارة الإلكترونية."
        ),
        "practical_walkthrough": (
            "تنفيذ استراتيجية Stale-While-Revalidate باستخدام Kotlin Flow و Room:\n"
            "```kotlin\n"
            "class ArticleRepositoryImpl @Inject constructor(\n"
            "    private val articleDao: ArticleDao,\n"
            "    private val apiService: ArticleApiService\n"
            ") : ArticleRepository {\n"
            "\n"
            "    // Stale-While-Revalidate: ينبعث الكاش فوراً ثم يتم التحديث في الخلفية:\n"
            "    override fun getArticles(): Flow<Resource<List<Article>>> = flow {\n"
            "        // 1. بث النسخة المخزنة في الكاش فوراً (Stale Data):\n"
            "        val cachedArticles = articleDao.getAllArticles().first()\n"
            "        if (cachedArticles.isNotEmpty()) {\n"
            "            emit(Resource.Success(data = cachedArticles.map { it.toDomain() }, isStale = true))\n"
            "        } else {\n"
            "            emit(Resource.Loading)\n"
            "        }\n"
            "\n"
            "        // 2. محاولة إعادة التحقق والتحديث من الشبكة في الخلفية (Revalidate):\n"
            "        try {\n"
            "            val freshArticles = apiService.fetchArticles()\n"
            "            // حفظ البيانات الحديثة في Room:\n"
            "            articleDao.updateAllArticles(freshArticles.map { it.toEntity() })\n"
            "            // بث النسخة الحديثة بعد التحديث:\n"
            "            emit(Resource.Success(data = freshArticles.map { it.toDomain() }, isStale = false))\n"
            "        } catch (e: Exception) {\n"
            "            // لو فشلت الشبكة، يظل المستخدم يشاهد بيانات الكاش مع تنبيه خفيف:\n"
            "            if (cachedArticles.isEmpty()) {\n"
            "                emit(Resource.Error(e.message ?: \"Network error\"))\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Cache-First serves local data immediately and hits network only on misses/expiry, ideal for static data. Network-First attempts server calls first and falls back to cache on failure, ideal for financial balances. Stale-While-Revalidate displays cached data instantly while silently fetching fresh data in the background, offering the ideal UX for feeds and media.",
        "best_answer": (
            "Choosing between caching strategies depends on the latency versus freshness tolerance of the data:\n\n"
            "1. **Cache-First**: Queries local storage first. If valid, returns immediately without network access; fetches from remote only on cache miss or expiration. Optimal for static, low-churn assets (country code lists, user avatar images, feature configurations).\n\n"
            "2. **Network-First**: Prioritizes server freshness by querying the API first; falls back to local cache only when offline or during socket timeouts. Mandatory for mission-critical, volatile state where serving stale information causes real-world harm (bank account balances, stock prices, payment settlement confirmations).\n\n"
            "3. **Stale-While-Revalidate (SWR)**: The gold standard for modern mobile user experience. Emits cached data from Room in single-digit milliseconds so the user sees content immediately, while concurrently firing a background network request. Once the remote response returns, Room is updated, seamlessly animating fresh items into view. Perfect for news feeds, social timelines, and product catalogs."
        ),
        "deep_answer": (
            "When implementing Stale-While-Revalidate in production, senior engineers address the **List Jump UX Defect**.\n\n"
            "If a user is actively reading item #3 in a cached list, and the background revalidation completes 2 seconds later, prepending 5 new items to the top of the list will cause the screen to jump violently, disorienting the user.\n\n"
            "To solve this in Jetpack Compose and RecyclerView:\n"
            "- Implement **DiffUtil / stable item keys** (`key(article.id)` in Compose).\n"
            "- For dynamic feeds, buffer new background arrivals behind a subtle UI pill: '5 new posts available - Tap to refresh', giving the user control over when the UI layout recalculates."
        ),
        "follow_ups": [
            {
                "question": "How does HTTP Cache-Control header support stale-while-revalidate natively?",
                "answer": "Via the `stale-while-revalidate=<seconds>` directive in HTTP Cache-Control, supported natively by OkHttp Cache when configured with valid cache headers."
            },
            {
                "question": "What is the primary risk of Cache-First with an infinite TTL?",
                "answer": "The user may never receive updates if the app fails to invalidate or delete the cached file."
            }
        ]
    },
    {
        "id": "DAT-09",
        "arabic_explanation": (
            "كيف تنفذ معترِضات المصادقة (Authentication Interceptors) ومنطق تجديد التوكن (Refresh-Token Logic) بأمان في OkHttp؟\n\n"
            "1. تقسيم المسؤوليات في OkHttp (Interceptor vs Authenticator):\n   - **`Interceptor` (حقن التوكن في كل طلب)**:\n     * يضيف ترويسة المصادقة `Authorization: Bearer <token>` لكل طلب يخرج من التطبيق.\n     * يستثني طلبات تسجيل الدخول وتجديد التوكن العامة لتجنب إرسال توكنز قديمة.\n   - **`Authenticator` (التعامل مع انتهاء التوكن و 401 Unauthorized)**:\n     * صُمم خصيصاً في OkHttp للتعامل مع رد `401`.\n     * يستدعي خادم التجديد (Refresh Token Endpoint) بشكل متزامن لإصدار توكن جديد، وتحديث الجلسة في التخزين المشفر، وإعادة إرسال الطلب الأصلي بالتوكن الجديد تلقائياً.\n\n"
            "2. الأخطاء القاتلة وكيفية تجنبها (Deadlocks & Infinite Loops):\n   - **حلقة التكرار اللانهائية (Infinite Retry Loop)**: إذا أعاد طلب التجديد نفسه `401`، فقد يستدعي الـ Authenticator نفسه للأبد! يجب وضع شرط توقف: إذا كان الطلب الفاشل هو نفسه طلب الـ Refresh، أو إذا تكرر الفشل أكثر من 2 مرات، توقف وأعلن تسجيل الخروج (Logout).\n   - **استخدام نفس OkHttpClient لطلب الـ Refresh**: يؤدي إلى تجمد التطبيق (Deadlock). يجب استخدام OkHttpClient نقي ومستقل ومجرد من الـ Authenticator لتنفيذ طلب التجديد."
        ),
        "practical_walkthrough": (
            "التنفيذ الكامل والآمن لـ Interceptor و Authenticator في OkHttp:\n"
            "```kotlin\n"
            "// 1. Auth Interceptor: يضيف التوكن الحالي لكل طلب:\n"
            "class AuthHeaderInterceptor(private val tokenManager: TokenManager) : Interceptor {\n"
            "    override fun intercept(chain: Interceptor.Chain): Response {\n"
            "        val token = tokenManager.getAccessToken()\n"
            "        val request = if (token != null) {\n"
            "            chain.request().newBuilder()\n"
            "                .header(\"Authorization\", \"Bearer $token\")\n"
            "                .build()\n"
            "        } else {\n"
            "            chain.request()\n"
            "        }\n"
            "        return chain.proceed(request)\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. OkHttp Authenticator: يتعامل مع 401 ويعيد المحاولة بالتوكن الجديد:\n"
            "class TokenAuthenticator(\n"
            "    private val tokenManager: TokenManager,\n"
            "    private val authService: RefreshAuthService // يستخدم OkHttpClient مستقل بدون Authenticator!\n"
            ") : Authenticator {\n"
            "    override fun authenticate(route: Route?, response: Response): Request? {\n"
            "        // حماية 1: منع الحلقات اللانهائية لو فشل الطلب أكثر من مرتين:\n"
            "        if (responseCount(response) >= 2) return null\n"
            "        \n"
            "        // حماية 2: التزامن لمنع سباق الطلبات المتزامنة (Mutex / Synchronized):\n"
            "        synchronized(this) {\n"
            "            val currentToken = tokenManager.getAccessToken()\n"
            "            // لو كان هناك طلب سابق قام بالفعل بالتجديد:\n"
            "            val requestToken = response.request.header(\"Authorization\")?.removePrefix(\"Bearer \")\n"
            "            val validToken = if (currentToken != requestToken && currentToken != null) {\n"
            "                currentToken // استخدام التوكن الجديد فوراً بدون طلب refresh إضافي\n"
            "            } else {\n"
            "                // طلب تجديد حقيقي:\n"
            "                val newTokens = authService.refreshTokenBlocking(tokenManager.getRefreshToken())\n"
            "                if (newTokens != null) {\n"
            "                    tokenManager.saveTokens(newTokens.access, newTokens.refresh)\n"
            "                    newTokens.access\n"
            "                } else {\n"
            "                    tokenManager.clearSessionAndForceLogout()\n"
            "                    return null // إلغاء المحاولة وتسجيل الخروج\n"
            "                }\n"
            "            }\n"
            "            \n"
            "            // إعادة إرسال الطلب الأصلي بالتوكن المحدث:\n"
            "            return response.request.newBuilder()\n"
            "                .header(\"Authorization\", \"Bearer $validToken\")\n"
            "                .build()\n"
            "        }\n"
            "    }\n"
            "    \n"
            "    private fun responseCount(response: Response): Int {\n"
            "        var result = 1\n"
            "        var prior = response.priorResponse\n"
            "        while (prior != null) { result++; prior = prior.priorResponse }\n"
            "        return result\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Use an OkHttp Interceptor to attach access tokens to outgoing requests, and an Authenticator to handle 401 Unauthorized responses by fetching a new token and retrying the request. Protect against infinite retry loops by checking response count, synchronize refreshes to prevent race conditions, and use a dedicated clean OkHttpClient for refresh calls.",
        "best_answer": (
            "Implementing resilient JWT authentication in OkHttp requires separating proactive header injection from reactive 401 recovery:\n\n"
            "1. **Proactive Injection (`Interceptor`)**: An Application Interceptor reads the cached access token from secure storage and injects `Authorization: Bearer <token>` into outgoing requests. Public endpoints (login, register) are excluded.\n\n"
            "2. **Reactive 401 Recovery (`Authenticator`)**: When the server returns `401 Unauthorized`, OkHttp triggers `Authenticator.authenticate()`. This method executes a synchronous token refresh, updates persistent storage, and builds a new request with the updated token, which OkHttp automatically retries.\n\n"
            "3. **Guardrails against Common Failures**:\n   - **Loop Prevention**: Inspect `response.priorResponse` chain. If attempts exceed 2, return `null` to abort and prompt user re-login.\n   - **Deadlock Isolation**: The refresh network call must execute on an isolated OkHttp client that has **no Authenticator attached**; using the primary client causes recursive lock deadlocks.\n   - **Double-Check Lock**: Check whether another concurrent thread already refreshed the token while this thread was waiting on the lock."
        ),
        "deep_answer": (
            "A critical edge case is **Refresh Token Rotation (RTR)**.\n\n"
            "Modern OAuth 2.0 backends rotate the refresh token on *every* refresh request (issuing both a new access token and a new single-use refresh token, immediately invalidating the previous refresh token). "
            "If client synchronization fails and two concurrent requests make separate refresh calls using the old refresh token, the server detects token reuse, treats it as a security breach, and invalidates all user sessions globally!\n\n"
            "To solve this, the refresh operation must be strictly serialized behind a **Single-Flight Lock (or Mutex)** with token double-checking: the thread entering the lock first executes the refresh, while subsequent threads detect that `currentToken != requestToken` and immediately replay with the new token without hitting the refresh API."
        ),
        "follow_ups": [
            {
                "question": "What happens if `Authenticator.authenticate()` returns `null`?",
                "answer": "OkHttp halts retries and returns the original 401 response to the caller, allowing the UI layer to navigate to the login screen."
            },
            {
                "question": "Where should tokens be stored securely in Android?",
                "answer": "EncryptedSharedPreferences or Proto DataStore with Android Keystore encryption, never in plaintext SharedPreferences."
            }
        ]
    },
    {
        "id": "DAT-10",
        "arabic_explanation": (
            "كيف تتجنب سباق طلبات تجديد التوكن المتزامنة (Concurrent Refresh-Token Races)؟\n\n"
            "1. سيناريو الكارثة في التطبيقات متعددة الخيوط (The Race Condition):\n   - عند فتح التطبيق، يطلق الـ Dashboard ثلاثة طلبات متزامنة في نفس اللحظة: جلب الملف الشخصي، جلب الإشعارات، وجلب السلة.\n   - انتهت صلاحية الـ Access Token، فتعود الطلبات الثلاثة بـ `401 Unauthorized` في نفس الجزء من الثانية!\n   - إذا قامت كل خيط (Thread) باستدعاء سيرفر التجديد بـ Refresh Token:\n     * السيرفر يدعم أمان Refresh Token Rotation (RTR): أول طلب ينجح ويحرق الـ Refresh Token القديم.\n     * الطلب الثاني والثالث يصلان بالـ Refresh Token القديم الذي تم حرقه!\n     * يعتبر السيرفر ذلك هجوماً واختراقاً أمنياً (Token Theft)، فيقوم بحظر حساب المستخدم وحذف جميع الجلسات وإجباره على تسجيل الدخول!\n\n"
            "2. الحل المعماري الصارم (Single-Flight Lock & Double-Check Protocol):\n   - **قفل التزامن (Mutex / Synchronized)**: خيط واحد فقط يُسمح له بطلب التجديد في أي لحظة.\n   - **فحص التوكن المزدوج (Double-Check)**: عند دخول الخيط الثاني بعد انتهاء الخيط الأول، يقارن التوكن الفاشل بالتوكن الحالي في الذاكرة. إذا وجده قد تغير، لا يتصل بالسيرفر! بل يعيد الطلب الأصلي بالتوكن الجديد فوراً.\n   - **Single-Flight Deferred**: أو تعليق الطلبات الأخرى على `Deferred` ينتظر اكتمال الطلب الأول ويستخدم نتيجته."
        ),
        "practical_walkthrough": (
            "تنفيذ بروتوكول Single-Flight مع فحص التوكن المزدوج لمنع سباق التجديد:\n"
            "```kotlin\n"
            "class SafeTokenManager @Inject constructor(\n"
            "    private val tokenStorage: SecureTokenStorage,\n"
            "    private val refreshApi: RefreshApi\n"
            ") {\n"
            "    private val refreshMutex = Mutex()\n"
            "\n"
            "    suspend fun getOrRefreshValidToken(failedToken: String?): Result<String> {\n"
            "        // قفل متزامن يمنع أي خيط آخر من بدء طلب تجديد جديد:\n"
            "        refreshMutex.withLock {\n"
            "            val currentToken = tokenStorage.getAccessToken()\n"
            "            \n"
            "            // الفحص المزدوج الحاسم (Double-Check):\n"
            "            // لو خيط آخر قام بالتجديد أثناء انتظار هذا الخيط في الطابور:\n"
            "            if (currentToken != null && currentToken != failedToken) {\n"
            "                // التوكن تم تجديده بالفعل! نرجع التوكن الجديد فوراً بدون لمس السيرفر:\n"
            "                return Result.success(currentToken)\n"
            "            }\n"
            "\n"
            "            // إذا كنا نحن الخيط الأول: ننفذ طلب تجديد واحد فقط (Single-Flight):\n"
            "            val refreshToken = tokenStorage.getRefreshToken() ?: return Result.failure(SessionExpiredException)\n"
            "            \n"
            "            return try {\n"
            "                val response = refreshApi.refreshToken(refreshToken)\n"
            "                tokenStorage.saveTokens(response.accessToken, response.newRefreshToken)\n"
            "                Result.success(response.accessToken)\n"
            "            } catch (e: Exception) {\n"
            "                tokenStorage.clearSession()\n"
            "                Result.failure(e)\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Avoid concurrent refresh-token races using a synchronized single-flight lock with a double-check protocol. When multiple concurrent requests hit 401 simultaneously, serialize them behind a Mutex. The first thread refreshes tokens; subsequent threads detect that the active token already changed and replay immediately without calling the refresh API.",
        "best_answer": (
            "When an app launches, multiple parallel network calls (profile, notifications, feed) often receive `401 Unauthorized` simultaneously. If each thread independently issues a refresh call under Refresh Token Rotation (RTR), the server treats subsequent calls using the old single-use token as credential theft, forcibly revoking the user's session.\n\n"
            "The industry-standard solution is the **Single-Flight Lock with Double-Check Protocol**:\n\n"
            "1. **Synchronized Lock**: All 401 handling is funneled through a shared lock (`Mutex` in coroutines, or `synchronized` in OkHttp Authenticator).\n\n"
            "2. **Double-Check Verification**: When a thread acquires the lock, it compares the token that triggered its 401 against the current in-memory token. If another thread already completed a refresh while this thread was waiting, `currentToken != failedToken`. The thread immediately skips the refresh API call and retries with the new token.\n\n"
            "3. **Atomic Session Update**: The winning thread executes exactly one refresh call, atomically saving both the new access token and the new refresh token to secure storage before releasing the lock."
        ),
        "deep_answer": (
            "In modern asynchronous architectures using Kotlin Coroutines, senior teams often implement this using **`CompletableDeferred` or `SharedFlow` single-flight coordination**.\n\n"
            "Instead of blocking JVM threads with `synchronized`, the token manager maintains an atomic reference to an active refresh job: `private val activeRefresh = AtomicReference<Deferred<String>?>()`. "
            "When a coroutine hits 401, it inspects the atomic reference. If an active job exists, it simply awaits the existing `Deferred`. "
            "If no job exists, it creates a new `async` job, atomically swaps it into the reference, and notifies all awaiting coroutines upon completion, clearing the reference in a `finally` block. This yields 100% non-blocking coroutine safety."
        ),
        "follow_ups": [
            {
                "question": "Why shouldn't you fire refresh-token requests in an OkHttp Interceptor instead of Authenticator?",
                "answer": "Interceptors do not naturally serialize 401 retries; Authenticator was designed specifically by OkHttp to manage retries and handle concurrent 401 responses cleanly."
            },
            {
                "question": "What happens if the single refresh call fails with network timeout?",
                "answer": "Release the lock and let callers retry transiently, but do NOT clear user session credentials on transient network timeouts—only on explicit 400/401 refresh responses."
            }
        ]
    },
    {
        "id": "DAT-11",
        "arabic_explanation": (
            "كيف تصمم ترحيل قاعدة بيانات Room (Database Migration) يحافظ على بيانات المستخدم بنسبة 100% دون فقدان أي بيانات؟\n\n"
            "1. خطورة ترقية الـ Database في الإنتاج:\n   - عندما تعدل أي `@Entity` (إضافة عمود، حذف عمود، تغيير نوع بيانات)، يجب زيادة رقم `version` في `@Database`.\n   - إذا قمت بزيادة الرقم دون كتابة `Migration`، سينهار التطبيق فوراً عند فتحه لدى المستخدم مع خطأ: `IllegalStateException: Room cannot verify the data integrity!`.\n   - **الكارثة الكبرى**: استخدام `fallbackToDestructiveMigration()`! هذا الإعداد يحذف قاعدة البيانات بالكامل ويعيد بناءها فارغة، مما يمسح مسودات المستخدم وعملياته غير المتصلة بالإنترنت!\n\n"
            "2. خطوات تصميم ترحيل آمن واحترافي:\n   - **تفعيل Schema Export في Gradle**: إعداد `room.schemaLocation` لحفظ ملفات الـ JSON لكل إصدار في Git.\n   - **كتابة كود الـ Migration الصريح**: استخدام أوامر SQLite القياسية (`ALTER TABLE ... ADD COLUMN ...`).\n   - **التعامل مع تعديل الأعمدة المعقد**: SQLite لا يدعم تعديل نوع عمود مباشرة. الخطوات القياسية: إنشاء جدول مؤقت بالهيكل الجديد، نسخ البيانات من الجدول القديم، حذف الجدول القديم، وإعادة تسمية الجدول المؤقت.\n   - **كتابة MigrationTest آلي**: اختبار الـ Migration باستخدام `MigrationTestHelper` قبل إطلاق التطبيق."
        ),
        "practical_walkthrough": (
            "كتابة كود Migration دقيق مع اختبار آلي للتأكد من سلامة البيانات:\n"
            "```kotlin\n"
            "// 1. تعريف مسار الترحيل من الإصدار 1 إلى الإصدار 2:\n"
            "val MIGRATION_1_2 = object : Migration(1, 2) {\n"
            "    override fun migrate(db: SupportSQLiteDatabase) {\n"
            "        // إضافة عمود جديد مع قيمة افتراضية لتفادي NULL في الأعمدة الإلزامية:\n"
            "        db.execSQL(\"ALTER TABLE orders ADD COLUMN tracking_number TEXT DEFAULT NULL\")\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. ترحيل معقد: تغيير عمود أو حذف عمود (تتطلب إنشاء جدول جديد):\n"
            "val MIGRATION_2_3 = object : Migration(2, 3) {\n"
            "    override fun migrate(db: SupportSQLiteDatabase) {\n"
            "        // أ. إنشاء جدول جديد بالهيكل المطلوب:\n"
            "        db.execSQL(\"\"\"\n"
            "            CREATE TABLE orders_new (\n"
            "                id TEXT PRIMARY KEY NOT NULL,\n"
            "                amount_cents INTEGER NOT NULL,\n"
            "                tracking_number TEXT\n"
            "            )\n"
            "        \"\"\".trimIndent())\n"
            "        // ب. نسخ البيانات من القديم للجديد:\n"
            "        db.execSQL(\"INSERT INTO orders_new (id, amount_cents, tracking_number) SELECT id, amount_cents, tracking_number FROM orders\")\n"
            "        // ج. حذف القديم وإعادة التسمية:\n"
            "        db.execSQL(\"DROP TABLE orders\")\n"
            "        db.execSQL(\"ALTER TABLE orders_new RENAME TO orders\")\n"
            "    }\n"
            "}\n"
            "\n"
            "// 3. اختبار الترحيل الآلي عبر MigrationTestHelper:\n"
            "@Test\n"
            "fun testMigration1To2PreservesData() {\n"
            "    // إنشاء DB بالإصدار 1 وكتابة بيانات حقيقية:\n"
            "    helper.createDatabase(TEST_DB, 1).apply {\n"
            "        execSQL(\"INSERT INTO orders (id, amount_cents) VALUES ('ord_1', 5000)\")\n"
            "        close()\n"
            "    }\n"
            "    // تشغيل الترحيل للإصدار 2 والتحقق من بقاء البيانات:\n"
            "    val db = helper.runMigrationsAndValidate(TEST_DB, 2, true, MIGRATION_1_2)\n"
            "    val cursor = db.query(\"SELECT * FROM orders WHERE id = 'ord_1'\")\n"
            "    assertTrue(cursor.moveToFirst())\n"
            "    assertEquals(5000L, cursor.getLong(cursor.getColumnIndexOrThrow(\"amount_cents\")))\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design data-preserving Room migrations by enabling exported schemas, writing explicit SQL migrations (ALTER TABLE or temp-table copy patterns), never defaulting to destructive fallback in production, and verifying migration paths from older versions using Room's MigrationTestHelper.",
        "best_answer": (
            "Preserving user data during Room schema evolution requires treating database migrations with the same rigor as backend database upgrades:\n\n"
            "1. **Export Schemas via Gradle**: Configure `room.schemaLocation` in `build.gradle.kts` and commit generated schema JSON files to Git. This provides Room with the baseline schema for every released version.\n\n"
            "2. **Explicit Migration Scripts**: Avoid `fallbackToDestructiveMigration()` in production offline-first apps, which completely drops tables and purges pending user drafts. Write explicit `Migration(from, to)` objects containing valid SQLite DDL.\n\n"
            "3. **Handling Complex Schema Changes**: Because SQLite historically has limited `ALTER TABLE` support (e.g. dropping columns or altering constraints), use the **Table Recreation Pattern**: create the new table with desired schema, copy data over (`INSERT INTO new SELECT ... FROM old`), drop the old table, and rename the new table.\n\n"
            "4. **Automated Migration Testing**: Use `MigrationTestHelper` in instrumented or Robolectric tests. The test spins up version $N$, inserts test records, executes the migration to $N+1$, and asserts that rows exist and columns match expected types."
        ),
        "deep_answer": (
            "A critical production hazard is **Sparse Version Upgrades**.\n\n"
            "Users rarely update apps sequentially. A user might jump directly from app version 1.0 (Database version 1) to app version 4.0 (Database version 5). "
            "Room allows defining discrete incremental migrations (`1->2`, `2->3`, `3->4`, `4->5`) and chains them automatically at startup. "
            "However, if any link in the chain is missing, Room crashes with an `IllegalStateException`.\n\n"
            "To bulletproof release rollouts:\n"
            "- Implement continuous CI tests verifying every supported upgrade path (e.g. test `1->5`, `2->5`, `3->5`).\n"
            "- If table recreation involves millions of rows, run migrations within a transaction and monitor disk space, as SQLite requires temporary storage equal to the table size during table copy operations."
        ),
        "follow_ups": [
            {
                "question": "What is `AutoMigration` in Room?",
                "answer": "Introduced in Room 2.4, `@AutoMigration` generates simple migrations (adding columns, creating tables) automatically using exported schema JSON diffs."
            },
            {
                "question": "What happens if a NOT NULL column is added without a DEFAULT value during migration?",
                "answer": "SQLite throws an error during migration because existing rows would have NULL in a NOT NULL column; always supply a default value."
            }
        ]
    },
    {
        "id": "DAT-12",
        "arabic_explanation": (
            "كيف تستخدم معاملات Room (@Transaction / withTransaction) لتنفيذ عمليات كتابة ذرية كلية أو لا شيء (All-or-Nothing Writes)؟\n\n"
            "1. ما هي المعاملة الذرية (Atomic Transaction)؟\n   - هي ضمان خاصية الـ Atomicity من مبادئ ACID في قواعد البيانات.\n   - إذا كانت العملية تتطلب كتابة في جدولين معاً (مثل جدول الطلب الرئيسي `Order` وجدول عناصر الطلب `OrderItem`)، أو حذف بيانات قديمة وكتابة بيانات جديدة:\n   - تضمن المعاملة أن تُنفذ جميع الخطوات بنجاح ككتلة واحدة (`COMMIT`)، أو تُلغى جميع التعديلات ويعود كل شيء كما كان إذا حدث أي خطأ أو استثناء (`ROLLBACK`).\n\n"
            "2. طريقتان للتنفيذ في Room:\n   - **تعليمة `@Transaction` على دوال الـ DAO**: مثالية عندما تكون العمليات محصورة داخل DAO واحد (مثل استبدال عناصر السلة).\n   - **دالة `roomDatabase.withTransaction { }` في الكوروتين**: المعيار الأفضل في طبقة الـ Repository لتنسيق عمليات ذرية تمتد عبر عدة DAOs مختلفة (مثل تحديث `OrderDao` وتحديث `InventoryDao` معاً).\n\n"
            "3. حدود الضمان المعماري:\n   - الـ Transaction تضمن الذرية محلياً فقط على مستوى SQLite على الهاتف؛ **لا تشمل ولا تضمن عمليات الشبكة (Network Calls)**! لا تضع استدعاءات API داخل `withTransaction` أبداً."
        ),
        "practical_walkthrough": (
            "المقارنة بين @Transaction داخل DAO و withTransaction عبر عدة DAOs في الـ Repository:\n"
            "```kotlin\n"
            "// 1. @Transaction داخل DAO: لعملية ذرية محلية في جدول واحد:\n"
            "@Dao\n"
            "interface FeedDao {\n"
            "    @Query(\"DELETE FROM feed_posts\")\n"
            "    suspend fun clearFeed()\n"
            "\n"
            "    @Insert(onConflict = OnConflictStrategy.REPLACE)\n"
            "    suspend fun insertPosts(posts: List<PostEntity>)\n"
            "\n"
            "    @Transaction\n"
            "    suspend fun clearAndInsert(posts: List<PostEntity>) {\n"
            "        clearFeed()\n"
            "        insertPosts(posts) // لو حدث OOM أو Crash، لا يتم مسح الكاش القديم!\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. withTransaction في الـ Repository: لعملية ذرية تمتد عبر DAOs متعددة:\n"
            "class CheckoutRepositoryImpl @Inject constructor(\n"
            "    private val appDatabase: AppDatabase,\n"
            "    private val orderDao: OrderDao,\n"
            "    private val cartDao: CartDao,\n"
            "    private val analyticsDao: LocalAnalyticsDao\n"
            ") : CheckoutRepository {\n"
            "\n"
            "    override suspend fun finalizeOrderLocally(order: OrderEntity, items: List<OrderItemEntity>) {\n"
            "        // فتح معاملة ذرية على مستوى قاعدة البيانات بالكامل:\n"
            "        appDatabase.withTransaction {\n"
            "            orderDao.insertOrder(order)\n"
            "            orderDao.insertOrderItems(items)\n"
            "            cartDao.clearActiveCart()\n"
            "            analyticsDao.recordEvent(\"order_created_locally\", order.id)\n"
            "            // لو فشل أي سطر هنا، يتم Rollback للجميع ولن تفقد السلة بدون حفظ الطلب!\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Use Room's @Transaction on DAO methods or database.withTransaction { } in repositories to guarantee ACID atomicity across multi-table writes. If an exception occurs, changes roll back completely, preventing partial database states. Never execute network calls inside database transactions to avoid blocking SQLite threads.",
        "best_answer": (
            "Room transactions provide ACID atomicity, guaranteeing that multi-step database writes either completely succeed or completely roll back:\n\n"
            "1. **DAO-Level Transactions (`@Transaction`)**: Used when combining multiple queries within a single DAO (e.g. deleting old cached posts and inserting fresh posts). If the app crashes or throws an exception during insertion, the delete operation rolls back automatically, preventing an empty UI state.\n\n"
            "2. **Repository-Level Transactions (`roomDatabase.withTransaction { }`)**: The preferred coroutine construct for multi-DAO atomic operations. For example, saving an order in `OrderDao`, recording line items in `OrderItemDao`, and clearing the shopping cart in `CartDao` must occur atomically. `withTransaction` wraps the block in SQLite `BEGIN TRANSACTION ... COMMIT`.\n\n"
            "3. **Consistency for Observers**: Observers watching Room `Flow` queries only receive an updated dataset *after* the entire transaction commits. They never observe intermediate, half-written states."
        ),
        "deep_answer": (
            "A critical concurrency trap is **Executing Network Calls inside `withTransaction`**:\n\n"
            "```kotlin\n"
            "// ❌ ANTI-PATTERN:\n"
            "database.withTransaction {\n"
            "    orderDao.savePendingOrder(order)\n"
            "    val response = networkApi.submit(order) // BLOCKS SQLITE CONNECTION POOL FOR 5 SECONDS!\n"
            "    orderDao.markConfirmed(response.id)\n"
            "}\n"
            "```\n"
            "SQLite has a limited connection pool (often 1 write connection in WAL mode). Holding an open database transaction while awaiting a remote HTTP call locks the database for seconds, starving all other read and write threads and causing widespread `SQLiteDatabaseLockedException` and UI ANRs.\n\n"
            "**Rule**: Network operations must happen outside database transactions. First write the pending state in a fast 2ms transaction, make the network call, and update status in a second fast transaction."
        ),
        "follow_ups": [
            {
                "question": "Does Room's `@Transaction` work with `@Query` methods returning Relations?",
                "answer": "Yes! When querying `@Relation` objects (which executes multiple SELECT queries under the hood), `@Transaction` is mandatory to avoid race conditions between parent and child queries."
            },
            {
                "question": "What is the threading model of `database.withTransaction`?",
                "answer": "It runs on an internal Room transaction dispatcher, acquiring a dedicated SQLite thread from Room's internal executor."
            }
        ]
    },
    {
        "id": "DAT-13",
        "arabic_explanation": (
            "كيف تنفذ مكتبة Paging 3 مع RemoteMediator لدعم التصفح بالصفحات في تطبيق Offline-First؟\n\n"
            "1. المفهوم المعماري لـ Paging 3 مع الـ Offline-First:\n   - **المصدر الوحيد للحقيقة هو Room (Single Source of Truth)**: لا تعرض الـ UI صفحات الشبكة مباشرة!\n   - الـ `Pager` يقدم البيانات للـ UI حصرياً من `PagingSource` الخاص بقاعدة بيانات Room.\n   - **دور الـ `RemoteMediator`**: يعمل كمراقب في الخلفية. عندما يقترب المستخدم من نهاية القائمة المعروضة في الشاشة وتنفد البيانات من Room، يتدخل `RemoteMediator` تلقائياً ليطلب الصفحة التالية من الـ Network API ويكتبها في Room.\n   - بمجرد كتابة البيانات في Room، يقوم Room تلقائياً بتحديث `PagingData` المعروضة في الشاشة بسلاسة.\n\n"
            "2. مكونات دورة حياة RemoteMediator:\n   - **`LoadType.REFRESH`**: عندما يقوم المستخدم بالسحب للتحديث (Pull-to-Refresh)، أو عند التشغيل لأول مرة.\n   - **`LoadType.APPEND`**: عندما يصل المستخدم لنهاية القائمة لجلب الصفحة التالية.\n   - **`LoadType.PREPEND`**: عند التمرير لأعلى (نادراً ما يحتاج لجلب بيانات إذا كنا نبدأ من البداية).\n   - **`RemoteKeys` Table**: جدول في Room يخزن أرقام الصفحات السابقة والتالية (`prevKey`, `nextKey`) لكل عنصر لضمان معرفة الصفحة التالية بدقة."
        ),
        "practical_walkthrough": (
            "هيكل تنفيذ RemoteMediator الكامل في Paging 3 مع Room:\n"
            "```kotlin\n"
            "@OptIn(ExperimentalPagingApi::class)\n"
            "class ArticleRemoteMediator(\n"
            "    private val api: ArticleApiService,\n"
            "    private val database: AppDatabase\n"
            ") : RemoteMediator<Int, ArticleEntity>() {\n"
            "\n"
            "    override suspend fun load(loadType: LoadType, state: PagingState<Int, ArticleEntity>): MediatorResult {\n"
            "        return try {\n"
            "            // 1. تحديد رقم الصفحة المطلوبة بناءً على LoadType:\n"
            "            val page = when (loadType) {\n"
            "                LoadType.REFRESH -> 1\n"
            "                LoadType.PREPEND -> return MediatorResult.Success(endOfPaginationReached = true)\n"
            "                LoadType.APPEND -> {\n"
            "                    val remoteKey = getRemoteKeyForLastItem(state)\n"
            "                    val nextKey = remoteKey?.nextPage ?: return MediatorResult.Success(endOfPaginationReached = remoteKey != null)\n"
            "                    nextKey\n"
            "                }\n"
            "            }\n"
            "\n"
            "            // 2. جلب البيانات من السيرفر:\n"
            "            val response = api.fetchArticles(page = page, pageSize = state.config.pageSize)\n"
            "            val endOfPagination = response.items.isEmpty()\n"
            "\n"
            "            // 3. كتابة البيانات ومفاتيح الصفحات في Room داخل Transaction واحدة:\n"
            "            database.withTransaction {\n"
            "                if (loadType == LoadType.REFRESH) {\n"
            "                    database.remoteKeysDao().clearAllKeys()\n"
            "                    database.articleDao().clearAllArticles()\n"
            "                }\n"
            "                val nextKey = if (endOfPagination) null else page + 1\n"
            "                val keys = response.items.map { ArticleRemoteKey(it.id, prevPage = page - 1, nextPage = nextKey) }\n"
            "                database.remoteKeysDao().insertAll(keys)\n"
            "                database.articleDao().insertAll(response.items.map { it.toEntity() })\n"
            "            }\n"
            "\n"
            "            MediatorResult.Success(endOfPaginationReached = endOfPagination)\n"
            "        } catch (e: Exception) {\n"
            "            MediatorResult.Error(e) // Paging 3 يعرض حالة الخطأ في الـ UI مع زر Retry تلقائياً\n"
            "        }\n"
            "    }\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Paging 3 with RemoteMediator uses Room as the single source of truth for the UI while fetching pages from the network on demand. The Pager streams data from Room's PagingSource, and RemoteMediator intercepts pagination boundaries (REFRESH, APPEND) to load network pages and save them alongside pagination keys in a Room transaction.",
        "best_answer": (
            "Implementing Paging 3 with `RemoteMediator` provides production-grade offline-first pagination:\n\n"
            "1. **Architecture Separation**:\n   - The presentation layer collects `Flow<PagingData<T>>` served exclusively by Room's generated `PagingSource`.\n   - `RemoteMediator` acts as the network pump. It does not return items to the UI; it fetches remote payloads and writes them into Room. Room's invalidation tracker then emits updated paging slices to the UI.\n\n"
            "2. **LoadTypes & Lifecycle**:\n   - **`REFRESH`**: Triggered on initial load or swipe-to-refresh. If online, clears existing database tables and inserts page 1.\n   - **`APPEND`**: Triggered when the user scrolls near the end of the loaded viewport. Fetches the next page and appends entities to Room.\n   - **`PREPEND`**: Triggered if scrolling upwards; typically returns `endOfPaginationReached = true` if items are only added forward.\n\n"
            "3. **RemoteKeys Table**: Maintains cursor/page pointers in SQLite for each entity, ensuring accurate page math across app restarts and process recreation."
        ),
        "deep_answer": (
            "A frequent failure mode in Paging 3 is **Infinite Refresh Loops caused by Table Invalidation**.\n\n"
            "If your `RemoteMediator` writes to a secondary table that triggers invalidation of the primary observed query *before* the transaction finishes, or if `RemoteMediator` returns `MediatorResult.Success(endOfPaginationReached = false)` when the network actually returned an empty list, Paging 3 continuously triggers new `APPEND` loads in an infinite loop, draining battery and flooding the server.\n\n"
            "**Defensive Rules**:\n"
            "- Always write entities and `RemoteKeys` together inside `database.withTransaction { }`.\n"
            "- If `response.items.isEmpty()`, immediately set `endOfPaginationReached = true`.\n"
            "- Use `initialize(): InitializeAction` in `RemoteMediator`. If cached database data is fresh (e.g. less than 10 minutes old), return `InitializeAction.SKIP_INITIAL_REFRESH` to open the screen instantly without hitting the network."
        ),
        "follow_ups": [
            {
                "question": "What is the purpose of `InitializeAction.SKIP_INITIAL_REFRESH`?",
                "answer": "It instructs RemoteMediator to skip the network refresh on launch if local cached data is deemed fresh, opening the screen offline immediately."
            },
            {
                "question": "How do you display error states with Paging 3 in Compose?",
                "answer": "Inspect `lazyPagingItems.loadState.append` or `refresh` for `LoadState.Error`, rendering a retry button or error banner."
            }
        ]
    },
    {
        "id": "DAT-14",
        "arabic_explanation": (
            "كيف تصمم استراتيجية إعادة المحاولة (Retry Strategy) مع احترام مبادئ الـ Idempotency وحدود معدل الطلبات (Rate Limits)؟\n\n"
            "1. القواعد الذهبية لإعادة المحاولة (Retry Rules):\n   - **فصل القراءة عن الكتابة (Read vs. Write)**:\n     * طلبات القراءة (`GET`) آمنة ويمكن إعادة محاولتها تلقائياً.\n     * طلبات الكتابة (`POST`) غير آمنة؛ لا تعيد محاولتها إلا إذا كانت تحتوي على **Idempotency Key** فريد وثابت.\n   - **التمييز بين الأخطاء العابرة والدائمة (Transient vs. Permanent Errors)**:\n     * أخطاء عابرة (Transient): انقطاع الشبكة المؤقت، مهلة الاتصال `ConnectTimeout`, أو أخطاء السيرفر `503 Service Unavailable`, `502 Bad Gateway` -> تستحق إعادة المحاولة.\n     * أخطاء دائمة (Permanent): أخطاء التحقق `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found` -> **ممنوع إعادة المحاولة** لأنها ستفشل دائماً وتضيع بطارية الهاتف والموارد.\n\n"
            "2. خوارزمية التراجع الأسي مع التشتت العشوائي (Exponential Backoff with Full Jitter):\n   - لا تعيد المحاولة في نفس الثانية! كل محاولة فاشلة تضاعف وقت الانتظار: 1s ثم 2s ثم 4s ثم 8s.\n   - **Full Jitter**: إضافة قيمة عشوائية (Random Offset) لوقت الانتظار. إذا انقطع السيرفر عن العمل، وعادت الشبكة لـ 100 ألف هاتف في نفس اللحظة، فإن الـ Jitter يمنع كل الهواتف من إعادة الطلب في نفس الثانية بالظبط، مما يحمي السيرفر من الانهيار (Thundering Herd Problem).\n\n"
            "3. احترام ترويسة `429 Too Many Requests` و `Retry-After`:\n   - إذا أرجع السيرفر كود `429` أو `503` مع ترويسة `Retry-After: 60`، يجب أن يعلق التطبيق جميع الطلبات لنفس الـ Endpoint لمدة 60 ثانية بالكامل."
        ),
        "practical_walkthrough": (
            "تنفيذ خوارزمية Exponential Backoff with Jitter واحترام ترويسة Retry-After:\n"
            "```kotlin\n"
            "suspend fun <T> retryWithBackoff(\n"
            "    maxAttempts: Int = 3,\n"
            "    initialDelayMs: Long = 1000L,\n"
            "    maxDelayMs: Long = 16000L,\n"
            "    factor: Double = 2.0,\n"
            "    block: suspend () -> T\n"
            "): Result<T> {\n"
            "    var currentDelay = initialDelayMs\n"
            "    \n"
            "    repeat(maxAttempts - 1) { attempt ->\n"
            "        try {\n"
            "            return Result.success(block())\n"
            "        } catch (e: HttpException) {\n"
            "            // 1. فحص كود 429 أو 503 مع احترام Retry-After:\n"
            "            if (e.code() == 429 || e.code() == 503) {\n"
            "                val retryAfterSeconds = e.response()?.headers()?.get(\"Retry-After\")?.toLongOrNull()\n"
            "                if (retryAfterSeconds != null) {\n"
            "                    delay(retryAfterSeconds * 1000L)\n"
            "                    return@repeat\n"
            "                }\n"
            "            }\n"
            "            // 2. إذا كان الخطأ غير عابر (4xx): توقف فوراً ولا تعد المحاولة!\n"
            "            if (e.code() in 400..499) return Result.failure(e)\n"
            "        } catch (e: IOException) {\n"
            "            // أخطاء اتصال عابرة (SocketTimeout / Network loss) -> مؤهلة لإعادة المحاولة\n"
            "        }\n"
            "\n"
            "        // 3. حساب Exponential Backoff مع Full Jitter لمنع الـ Thundering Herd:\n"
            "        val jitter = Random.nextLong(0, currentDelay)\n"
            "        delay(jitter)\n"
            "        currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelayMs)\n"
            "    }\n"
            "    \n"
            "    return runCatching { block() } // المحاولة الأخيرة\n"
            "}\n"
            "```"
        ),
        "quick_answer": "Design retries by distinguishing transient network/server errors (503, timeouts) from permanent client errors (400, 401, 404). Use exponential backoff with full jitter to prevent thundering herd spikes on the backend, respect server Retry-After headers on 429 status codes, and mandate client-side Idempotency Keys on all retried mutations.",
        "best_answer": (
            "A production-grade retry architecture balances user resilience against backend capacity:\n\n"
            "1. **Error Classification**:\n   - **Retryable (Transient)**: `SocketTimeoutException`, `UnknownHostException`, and HTTP `502`, `503`, `504`.\n   - **Non-Retryable (Permanent)**: Client errors (`400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`). Retrying permanent errors burns battery and cellular quota without any chance of success.\n\n"
            "2. **Exponential Backoff with Full Jitter**:\n   - Simple fixed delays (e.g. retrying every 2 seconds) cause the **Thundering Herd Problem**: if an outage resolves, millions of devices retry at synchronized intervals, knocking the server offline again.\n   - Exponential backoff ($1s, 2s, 4s, 8s$) paired with randomized Jitter (`delay = Random(0, currentBackoff)`) spreads retry distribution smoothly across the timeline.\n\n"
            "3. **Rate Limit Governance (`429 Too Many Requests`)**:\n   - Always parse the `Retry-After` header. If present, pause coroutines or queue execution for the server-requested duration rather than applying client backoff.\n\n"
            "4. **Write Idempotency**: Never retry a mutating `POST` request unless backed by a persistent client-generated `Idempotency-Key`."
        ),
        "deep_answer": (
            "When designing background synchronization retries in Android, senior architects offload execution from in-memory coroutine loops to **`WorkManager`**.\n\n"
            "If an in-memory coroutine retry loop is executing with a 30-second delay, and the user swipes the app away from recents, Android kills the process and cancels the coroutine, dropping the pending retry permanently.\n\n"
            "By encapsulating offline retries inside WorkManager:\n"
            "- WorkManager persists the retry intent in its own SQLite database.\n"
            "- It supports native backoff policies: `setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)`.\n"
            "- It respects OS constraints (`NetworkType.CONNECTED`, battery not low), ensuring retries execute deterministically even after phone reboots."
        ),
        "follow_ups": [
            {
                "question": "What is the Thundering Herd Problem in mobile systems?",
                "answer": "When a major service outage recovers and thousands of mobile clients retry simultaneously, overwhelming server CPU and causing immediate cascading failures."
            },
            {
                "question": "What does 'Full Jitter' mean mathematically?",
                "answer": "`sleep = random_between(0, min(max_backoff, initial_backoff * 2^attempt))`, which maximizes randomness and flattens traffic spikes."
            }
        ]
    }
]

def main() -> None:
    if DATA_FILE.exists():
        existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in existing}
    else:
        by_id = {}

    for item in DAT_08_14:
        by_id[item["id"]] = item

    output = [by_id[k] for k in sorted(by_id.keys())]
    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {DATA_FILE} with questions DAT-08 to DAT-14. Total questions: {len(output)}")

if __name__ == "__main__":
    main()
