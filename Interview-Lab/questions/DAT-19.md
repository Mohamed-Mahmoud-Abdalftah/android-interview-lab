---
id: "DAT-19"
question: "Two refresh-token requests both invalidate the session. How do you serialize refresh correctly?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "C"
phase: 3
priority: "P1"
order: 276
editorial_status: "reviewed"
---

# DAT-19

## Original interview question

Two refresh-token requests both invalidate the session. How do you serialize refresh correctly?

## What the interviewer evaluates

Serialize refresh-token rotation and avoid false logout from two concurrent 401 responses.

## Concept and technical explanation

Safe serialization of refresh-token operations resolves concurrency race conditions in modern token rotation architectures:
- Token Rotation & The Concurrency Trap: Modern OAuth/OIDC backends employ Refresh Token Rotation. Each refresh token is single-use: when presented, the server issues a new pair of access and refresh tokens and invalidates the old refresh token. If two concurrent HTTP requests fail with 401 simultaneously and both attempt to use the existing refresh token, the second request arrives at the backend after the refresh token was already consumed. The server interprets this as a potential token replay attack, revokes the user's entire session family, and forces an immediate logout.
- OkHttp Authenticator Serialization: OkHttp does not synchronize Authenticator.authenticate() calls across parallel dispatcher threads. A thread-safe TokenManager must coordinate execution:
  1. Double-Checked Token Inspection: Before executing a network refresh, the Authenticator checks if the failed request's Authorization header differs from the latest access token in memory. If another concurrent thread has already completed the refresh, the Authenticator simply updates the header to the fresh token and returns the request for replay without contacting the auth server.
  2. Single-Flight Concurrency Lock: If the token is still stale, the thread acquires an exclusive lock (via Kotlin Coroutines Mutex or ReentrantLock).
  3. Request Queuing: Any other concurrent 401 threads suspend or block on the lock, waiting for the single refresh network call to complete.
  4. Atomic Storage & Release: Once the fresh tokens are stored in secure storage, the lock is released, and all queued requests replay seamlessly with the new bearer token.

## Practical walkthrough (English)

Thread-safe token manager coordinating single-flight refresh with Mutex:
```kotlin
class SafeTokenManager(
    private val authApi: AuthApiService,
    private val tokenStorage: EncryptedTokenStorage
) {
    private val mutex = Mutex()

    suspend fun getOrRefreshToken(staleHeaderToken: String?): String? = mutex.withLock {
        val currentToken = tokenStorage.getAccessToken()
        // Double-checked locking: If another thread already refreshed it, return immediately
        if (currentToken != null && "Bearer $currentToken" != staleHeaderToken) {
            return currentToken
        }

        // Execute single refresh request
        val refreshToken = tokenStorage.getRefreshToken() ?: return null
        return try {
            val response = authApi.refreshTokens(RefreshTokenRequest(refreshToken))
            tokenStorage.saveTokens(response.accessToken, response.refreshToken)
            response.accessToken
        } catch (e: Exception) {
            tokenStorage.clearSession()
            null
        }
    }
}

class SynchronizedAuthenticator(
    private val tokenManager: SafeTokenManager
) : Authenticator {
    override fun authenticate(route: Route?, response: Response): Request? {
        if (responseCount(response) >= 2) return null

        val currentAuth = response.request.header("Authorization")
        val newToken = runBlocking {
            tokenManager.getOrRefreshToken(currentAuth)
        } ?: return null

        return response.request.newBuilder()
            .header("Authorization", "Bearer $newToken")
            .build()
    }

    private fun responseCount(response: Response): Int {
        var count = 1
        var prior = response.priorResponse
        while (prior != null) { count++; prior = prior.priorResponse }
        return count
    }
}
```

## Explanation in Arabic

طلبان متزامنان لتجديد التوكن (Refresh Token) أديا معاً إلى إبطال جلسة المستخدم وتسجيل خروجه بالخطأ. كيف تضبط تسلسل التجديد وتمنع هذا الخطأ؟

1. تشريح المشكلة (Why Concurrent Requests Invalidate the Session):
   - معظم خوادم الـ OAuth 2.0 الحديثة تطبق حماية **Refresh Token Rotation (RTR)**: عند استخدام Refresh Token، يُصدر السيرفر توكن جديد ويحرق (Revoke) التوكن القديم فوراً.
   - إذا أرسل التطبيق طلبين متزامنين بـ Access Token منتهي، يستقبل الاثنان `401 Unauthorized`.
   - إذا قام كلا الطلبين باستدعاء endpoint التجديد باستخدام نفس الـ Refresh Token القديم:
     * الطلب الأول يصل السيرفر وينجح ويحرق الـ Refresh Token القديم.
     * الطلب الثاني يصل بعده بـ 10 ميلي ثانية حاملاً نفس الـ Refresh Token القديم المحروق!
     * يكتشف السيرفر محاولة استخدام توكن ملغى، ويعتبر ذلك هجوماً واختراقاً (Breach Detection)، فيقوم فوراً بإبطال جميع توكنز المستخدم وحظر الجلسة!

2. المعمارية الصحيحة لتسلسل التجديد (Serialized Single-Flight Protocol):
   - **قفل تسلسلي إجباري (Serialized Mutex)**: لا يجوز لأكثر من خيط واحد التحدث إلى endpoint التجديد في نفس الوقت.
   - **فحص التوكن المزدوج (Double-Check under Lock)**: عند حصول أي خيط على القفل، يقارن التوكن الذي سبب الـ 401 بالتوكن المخزن حالياً. إذا كان التوكن قد تم تحديثه بالفعل بواسطة خيط سابق، يتخطى طلب التجديد ويعيد المحاولة بالتوكن الجديد فوراً.
   - **جيل الجلسة (Session Generation Counter)**: عداد يمنع أي استجابة تجديد متأخرة من إعادة تنشيط جلسة تم تسجيل خروجها عمداً بواسطة المستخدم.

## Practical walkthrough

التنفيذ البرمجي المانع لسباق تجديد التوكن في OkHttp Authenticator:
```kotlin
class ThreadSafeAuthenticator @Inject constructor(
    private val sessionStore: SessionStore,
    private val refreshApi: DedicatedRefreshClient
) : Authenticator {

    private val lock = Any()

    override fun authenticate(route: Route?, response: Response): Request? {
        // 1. استخراج التوكن الذي فشل في هذا الطلب المحدد:
        val failedToken = response.request.header("Authorization")?.removePrefix("Bearer ")

        synchronized(lock) {
            val currentToken = sessionStore.getAccessToken()

            // 2. الفحص المزدوج الحاسم:
            // إذا كان التوكن الحالي يختلف عن التوكن الذي فشل، فهذا يعني أن خيطاً آخر
            // قد أكمل التجديد بنجاح أثناء انتظار هذا الخيط في الطابور!
            if (currentToken != null && currentToken != failedToken) {
                // أعد المحاولة مباشرة بالتوكن الجديد بدون استدعاء السيرفر:
                return response.request.newBuilder()
                    .header("Authorization", "Bearer $currentToken")
                    .build()
            }

            // 3. إذا كنا الخيط الأول: استدعاء التجديد مرة واحدة فقط:
            val refreshToken = sessionStore.getRefreshToken() ?: return null
            val refreshResult = refreshApi.executeRefreshToken(refreshToken)

            return if (refreshResult.isSuccessful && refreshResult.tokens != null) {
                // حفظ التوكن الجديد و Refresh Token الجديد ذرياً:
                sessionStore.updateTokens(refreshResult.tokens.access, refreshResult.tokens.refresh)
                
                response.request.newBuilder()
                    .header("Authorization", "Bearer ${refreshResult.tokens.access}")
                    .build()
            } else {
                // فشل حقيقي في التجديد -> مسح الجلسة وإلغاء المحاولات:
                sessionStore.clearSession()
                null
            }
        }
    }
}
```

## Why it matters and how it works

Bound the number of HTTP follow-ups and avoid authenticating the refresh call with the same looping authenticator. Differentiate permanent refresh rejection from transient network failure; only authoritative invalidation should clear session. The shared coordinator must outlive individual requests but be cancelled/reset on account switch.

## Worked example

Conceptual coordinator; TokenStore and AuthApi include atomic persistence and backend rotation contract.

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class SessionRefresh(private val store: TokenStore, private val api: AuthApi) {
    private val mutex = Mutex()
    suspend fun resolve401(sent: String, generation: Long): String = mutex.withLock {
        if (store.generation() != generation) error("session changed")
        val current = store.access()
        if (current != sent) return@withLock current
        val pair = api.rotate(store.refresh())
        check(store.saveIfGeneration(generation, pair)) { "session changed" }
        pair.access
    }
}
// saveIfGeneration atomically compares the session generation and stores both
// tokens; it returns false after logout or account switch.
```

## Trade-offs and decision criteria

Mutex is easy to reason about but makes waiters share refresh latency. An in-flight Deferred can reduce lock hold time but complicates cancellation ownership. The backend still determines token validity and rotation semantics.

## Failure modes

A refresh call cancelled by one screen must not necessarily cancel the session’s shared refresh for other requests. A late pair saved after logout resurrects credentials. Clearing session on a transient offline error logs users out unnecessarily.

## Production perspective

A multi-tab banking app coordinates refresh per signed-in account, rechecks token after lock, and stores new credentials only if session generation matches. Tests force simultaneous 401s, refresh 5xx, permanent invalid refresh and logout during refresh.

## Interview answer — short

Serializing refresh-token requests requires thread-safe single-flight coordination using a Mutex or ReentrantLock. The authenticator compares the failed request's token against current in-memory credentials: if already refreshed by another thread, it immediately replays with the new token; otherwise, it acquires the lock, executes a single refresh, and unblocks queued requests.

## Interview answer — structured

Preventing concurrent refresh requests from invalidating user sessions requires single-flight synchronization to honor Refresh Token Rotation policies.
First, understand the failure mode. Modern backends enforce single-use refresh tokens. When parallel network calls return 401 simultaneously, uncoordinated refresh attempts submit identical tokens; the server detects reuse, treats it as a security breach, and terminates the entire session.
Second, implement double-checked token inspection in OkHttp Authenticator. Before contacting the auth server, compare the failed request's Authorization header with the latest token in memory. If another thread already completed a refresh, immediately replay the request with the fresh token.
Third, guard actual network renewal behind a synchronization primitive such as a Mutex or ReentrantLock. Only one thread calls the refresh API while concurrent 401s suspend, resuming cleanly once fresh credentials are saved.

## Interview answer — deep senior

In large-scale Android architectures, handling token refresh without robust thread synchronization is a frequent cause of random user logouts in production.
Enterprise backends implement Refresh Token Rotation to comply with OAuth 2.1 standards: when a refresh token is exchanged, it is immediately invalidated and replaced with a new pair.
If a screen dispatches five parallel Retrofit calls and all receive HTTP 401 Unauthorized because the access token expired, each thread enters OkHttp's Authenticator concurrently.
Without coordination, all five threads attempt to invoke the refresh endpoint with the same refresh token.
The first request succeeds, but the remaining four present an already-invalidated token.
The auth server detects this as a replay attack, invalidates the entire token family, and rejects all subsequent calls, unexpectedly kicking the user out of the app.
To eliminate this race condition, we implement a single-flight TokenManager utilizing double-checked locking with a Coroutine Mutex.
When an Authenticator thread wakes up, it first checks whether the failed request's header matches the active access token in storage.
If they differ, a sibling thread has already refreshed the session, so the Authenticator returns the new request immediately without network traffic.
If they match, it enters the Mutex lock, re-verifies the token, issues a single refresh request, persists the new pair into encrypted storage, and releases the lock, allowing queued requests to replay smoothly.

## How to answer in the interview

- **Why:** Rotating tokens are invalidated by duplicate refresh calls.
- **How:** Lock by session, recheck inside lock, commit pair conditionally.
- **Trade-offs:** Separate transient network error from permanent invalid grant.
- **Failure cases:** Second rotation, recursive Authenticator, post-logout resurrection.
- **Production solution:** Barrier-based concurrent-401 test with one refresh call.

## Deep-dive talking points

Draw token observed/current comparison, session generation and refresh failure categories.

## Follow-up questions

- **Interviewer:** "What is Refresh Token Rotation (RTR)?"
  **Answer:** "An OAuth 2.0 security mechanism where the server issues a new refresh token and revokes the old one on every single refresh, preventing replay attacks."

- **Interviewer:** "Why must the refresh HTTP client be independent of the primary OkHttpClient?"
  **Answer:** "If the refresh client shares the primary client's Authenticator, an unexpected 401 on the refresh endpoint triggers recursive authentication calls, causing a deadlock."

## Self-check rubric

Can I force two 401s, show one rotation, preserve logout and distinguish offline from invalid session?

## References and reviewed-on date

- [Kotlin shared mutable state](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) — Mutex coordination.
- [OkHttp calls guide](https://lysine.dev/okhttp/features/calls/) — 401 authenticator follow-up.

Technically reviewed against primary documentation on 2026-10-13.
