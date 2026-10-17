---
id: "DAT-10"
question: "How do you avoid concurrent refresh-token races?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "B"
phase: 3
priority: "P1"
order: 267
editorial_status: "reviewed"
---

# DAT-10

## Original interview question

How do you avoid concurrent refresh-token races?

## What the interviewer evaluates

Prevent concurrent refresh-token rotation races with a single-flight, double-check protocol.

## Concept and technical explanation

The concurrent refresh-token race condition (also called the Thundering Herd token issue) occurs when multiple parallel network requests fail with HTTP 401 simultaneously:
- The Failure Scenario: When an access token expires while multiple asynchronous coroutines are executing parallel API calls (e.g., loading user profile, notifications count, and dashboard feed concurrently), all requests receive HTTP 401 Unauthorized at nearly the same millisecond.
- Refresh Token Rotation Hazard: Modern OAuth2 servers implement Refresh Token Rotation, where using a refresh token invalidates it and issues a single-use replacement. If all failing requests trigger their own independent refresh calls, the first refresh succeeds and rotates the secret; the remaining four requests then hit the server with the now-invalidated token. The backend interprets this as a token replay attack and revokes the user's entire session, causing an unexpected, frustrating logout.
- The Architectural Solution (Single-Flight Double-Checked Locking):
  1. Synchronized Mutual Exclusion: Synchronize the token refresh block using a Kotlin Coroutines Mutex or ReentrantLock so only a single thread can execute the network refresh at any moment.
  2. Double-Checked Token Inspection: Before executing the refresh network call, inspect whether the access token in memory has already been updated while the current thread was waiting to acquire the lock. If the token in memory differs from the token that failed in the request, skip the network call entirely and immediately replay with the already-refreshed token.
  3. Single-Flight Execution: Only the first thread performs the network refresh; once complete, it updates shared storage and releases the lock. Waiting threads wake up, detect the fresh token via the double-check, and replay their requests without hitting the auth server.

## Practical walkthrough (English)

Thread-safe token manager implementing single-flight double-checked locking:
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
```

## Explanation in Arabic

كيف تتجنب سباق طلبات تجديد التوكن المتزامنة (Concurrent Refresh-Token Races)؟

1. سيناريو الكارثة في التطبيقات متعددة الخيوط (The Race Condition):
   - عند فتح التطبيق، يطلق الـ Dashboard ثلاثة طلبات متزامنة في نفس اللحظة: جلب الملف الشخصي، جلب الإشعارات، وجلب السلة.
   - انتهت صلاحية الـ Access Token، فتعود الطلبات الثلاثة بـ `401 Unauthorized` في نفس الجزء من الثانية!
   - إذا قامت كل خيط (Thread) باستدعاء سيرفر التجديد بـ Refresh Token:
     * السيرفر يدعم أمان Refresh Token Rotation (RTR): أول طلب ينجح ويحرق الـ Refresh Token القديم.
     * الطلب الثاني والثالث يصلان بالـ Refresh Token القديم الذي تم حرقه!
     * يعتبر السيرفر ذلك هجوماً واختراقاً أمنياً (Token Theft)، فيقوم بحظر حساب المستخدم وحذف جميع الجلسات وإجباره على تسجيل الدخول!

2. الحل المعماري الصارم (Single-Flight Lock & Double-Check Protocol):
   - **قفل التزامن (Mutex / Synchronized)**: خيط واحد فقط يُسمح له بطلب التجديد في أي لحظة.
   - **فحص التوكن المزدوج (Double-Check)**: عند دخول الخيط الثاني بعد انتهاء الخيط الأول، يقارن التوكن الفاشل بالتوكن الحالي في الذاكرة. إذا وجده قد تغير، لا يتصل بالسيرفر! بل يعيد الطلب الأصلي بالتوكن الجديد فوراً.
   - **Single-Flight Deferred**: أو تعليق الطلبات الأخرى على `Deferred` ينتظر اكتمال الطلب الأول ويستخدم نتيجته.

## Practical walkthrough

تنفيذ بروتوكول Single-Flight مع فحص التوكن المزدوج لمنع سباق التجديد:
```kotlin
class SafeTokenManager @Inject constructor(
    private val tokenStorage: SecureTokenStorage,
    private val refreshApi: RefreshApi
) {
    private val refreshMutex = Mutex()

    suspend fun getOrRefreshValidToken(failedToken: String?): Result<String> {
        // قفل متزامن يمنع أي خيط آخر من بدء طلب تجديد جديد:
        refreshMutex.withLock {
            val currentToken = tokenStorage.getAccessToken()
            
            // الفحص المزدوج الحاسم (Double-Check):
            // لو خيط آخر قام بالتجديد أثناء انتظار هذا الخيط في الطابور:
            if (currentToken != null && currentToken != failedToken) {
                // التوكن تم تجديده بالفعل! نرجع التوكن الجديد فوراً بدون لمس السيرفر:
                return Result.success(currentToken)
            }

            // إذا كنا نحن الخيط الأول: ننفذ طلب تجديد واحد فقط (Single-Flight):
            val refreshToken = tokenStorage.getRefreshToken() ?: return Result.failure(SessionExpiredException)
            
            return try {
                val response = refreshApi.refreshToken(refreshToken)
                tokenStorage.saveTokens(response.accessToken, response.newRefreshToken)
                Result.success(response.accessToken)
            } catch (e: Exception) {
                tokenStorage.clearSession()
                Result.failure(e)
            }
        }
    }
}
```

## Why it matters and how it works

Lock must be shared across calls for the same session, not recreated per request. Bound refresh attempts and handle permanent invalid refresh as session expiration. Cancellation of one waiter should not necessarily cancel a refresh owned by the session; define ownership explicitly, and reject refresh results after logout generation changes.

## Worked example

Conceptual coroutine coordinator; TokenStore and refresh API are app-owned, and the adapter to synchronous OkHttp Authenticator requires careful threading.

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class TokenRefresh(private val store: TokenStore, private val api: AuthApi) {
    private val lock = Mutex()
    suspend fun tokenAfter401(sent: String): String = lock.withLock {
        val generation = store.generation()
        val current = store.accessToken()
        if (current != sent) return@withLock current
        val pair = api.refresh(store.refreshToken())
        check(store.replaceIfGeneration(generation, pair)) { "session changed" }
        pair.access
    }
}
// TokenStore must atomically compare session generation and replace both tokens;
// a logout increments the generation. These are app-owned contracts.
```

## Trade-offs and decision criteria

Mutex simplifies correctness but holds waiters during network refresh; use a session-level Deferred/single-flight if many callers should await one refresh without holding a lock. A server refresh-token family/rotation policy matters. Do not overwrite credentials after logout.

## Failure modes

A per-request Mutex protects nothing across two requests. Refreshing without recheck duplicates rotation. A stale refresh response can resurrect a logged-out account unless session generation is checked before commit.

## Production perspective

A session repository stores tokens with generation, serializes refresh and replaces the pair in one protected step. The backend invalidates rotated credentials per its policy. Concurrency tests start two 401s simultaneously and assert one refresh and both retries use the new token.

## Interview answer — short

Concurrent refresh races occur when multiple parallel requests receive 401 simultaneously, risking session revocation under token rotation. The solution is single-flight double-checked locking: a synchronization lock ensures only one request performs the refresh, while subsequent waiting requests detect the updated token and replay without re-hitting the auth server.

## Interview answer — structured

Preventing concurrent refresh-token races is critical for preserving user sessions in applications with parallel networking.
First, when an access token expires while multiple parallel requests are in flight, all requests fail with 401 at the same time. If each request triggers its own refresh call, the server's Refresh Token Rotation mechanism treats subsequent calls as token theft and revokes the entire user session.
Second, we solve this using single-flight double-checked synchronization. When a 401 reaches the token manager, threads synchronize on a shared lock.
Third, the double-check verifies whether another thread has already refreshed the credentials while the current thread was waiting for the lock. If the current stored token differs from the failed request's token, the thread immediately uses the fresh token without network activity. Only the first thread makes the refresh API call, updating shared state for all waiters.

## Interview answer — deep senior

In enterprise mobile development, the concurrent refresh race condition is one of the most frustrating sources of phantom user logouts.
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
Once it succeeds, all queued requests proceed seamlessly with the updated token, reducing five redundant auth network calls to a single atomic roundtrip and completely eliminating session revocation bugs.

## How to answer in the interview

- **Why:** Multiple expired requests must share one logical rotation.
- **How:** Lock, recheck token inside lock, refresh once, persist pair conditionally.
- **Trade-offs:** Coordinate waiters without coupling to a cancelled screen scope.
- **Failure cases:** Double rotation, stale post-logout write, refresh deadlock.
- **Production solution:** Deterministic concurrent-401 and logout-race tests.

## Deep-dive talking points

Draw two callers racing, recheck-after-lock and logout generation safeguards.

## Follow-up questions

- **Interviewer:** "Why shouldn't you fire refresh-token requests in an OkHttp Interceptor instead of Authenticator?"
  **Answer:** "Interceptors do not naturally serialize 401 retries; Authenticator was designed specifically by OkHttp to manage retries and handle concurrent 401 responses cleanly."

- **Interviewer:** "What happens if the single refresh call fails with network timeout?"
  **Answer:** "Release the lock and let callers retry transiently, but do NOT clear user session credentials on transient network timeouts—only on explicit 400/401 refresh responses."

## Self-check rubric

Can I prove one refresh, atomic pair save, bounded retries and no logout resurrection?

## References and reviewed-on date

- [Kotlin shared mutable state](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) — Mutex coordination.
- [OkHttp calls guide](https://lysine.dev/okhttp/features/calls/) — authentication follow-up.

Technically reviewed against primary documentation on 2026-10-13.
