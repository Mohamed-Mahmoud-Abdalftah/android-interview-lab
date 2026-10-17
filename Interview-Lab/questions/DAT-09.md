---
id: "DAT-09"
question: "How do you implement authentication interceptors and refresh-token logic safely?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "B"
phase: 3
priority: "P1"
order: 266
editorial_status: "reviewed"
---

# DAT-09

## Original interview question

How do you implement authentication interceptors and refresh-token logic safely?

## What the interviewer evaluates

Design token attachment and refresh handling without loops, leakage or racing requests.

## Concept and technical explanation

Safe implementation of authentication and token refresh in OkHttp requires separating token injection from 401 error recovery:
- Application Auth Interceptor: Intercepts outgoing requests to attach the current access token to the HTTP Authorization header (e.g., Bearer <token>). It identifies public, unauthenticated endpoints (such as login or registration) via custom OkHttp Request Tags and permits them to proceed without authorization headers.
- OkHttp Authenticator Interface: Specifically designed to handle HTTP 401 Unauthorized responses. Unlike a standard interceptor, Authenticator is invoked exclusively upon authentication failure. It handles token renewal synchronously or delegates to a thread-safe token manager, rebuilds the original request with the fresh credential, and returns it to OkHttp for automatic transparent replay.
- Infinite 401 Loop Prevention: If credentials are fundamentally invalid or the refresh token is revoked, a poorly designed Authenticator can recursively loop forever. Robust implementations inspect the response chain (responseCount(response) >= 2) or verify whether the failed request already carried the newest token. If so, it returns null to abort the call, clears local session storage, and broadcasts a global logout event to navigate the user to the login screen.

## Practical walkthrough (English)

Production-grade token refresh implementation using OkHttp Authenticator:
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
```

## Explanation in Arabic

كيف تنفذ معترِضات المصادقة (Authentication Interceptors) ومنطق تجديد التوكن (Refresh-Token Logic) بأمان في OkHttp؟

1. تقسيم المسؤوليات في OkHttp (Interceptor vs Authenticator):
   - **`Interceptor` (حقن التوكن في كل طلب)**:
     * يضيف ترويسة المصادقة `Authorization: Bearer <token>` لكل طلب يخرج من التطبيق.
     * يستثني طلبات تسجيل الدخول وتجديد التوكن العامة لتجنب إرسال توكنز قديمة.
   - **`Authenticator` (التعامل مع انتهاء التوكن و 401 Unauthorized)**:
     * صُمم خصيصاً في OkHttp للتعامل مع رد `401`.
     * يستدعي خادم التجديد (Refresh Token Endpoint) بشكل متزامن لإصدار توكن جديد، وتحديث الجلسة في التخزين المشفر، وإعادة إرسال الطلب الأصلي بالتوكن الجديد تلقائياً.

2. الأخطاء القاتلة وكيفية تجنبها (Deadlocks & Infinite Loops):
   - **حلقة التكرار اللانهائية (Infinite Retry Loop)**: إذا أعاد طلب التجديد نفسه `401`، فقد يستدعي الـ Authenticator نفسه للأبد! يجب وضع شرط توقف: إذا كان الطلب الفاشل هو نفسه طلب الـ Refresh، أو إذا تكرر الفشل أكثر من 2 مرات، توقف وأعلن تسجيل الخروج (Logout).
   - **استخدام نفس OkHttpClient لطلب الـ Refresh**: يؤدي إلى تجمد التطبيق (Deadlock). يجب استخدام OkHttpClient نقي ومستقل ومجرد من الـ Authenticator لتنفيذ طلب التجديد.

## Practical walkthrough

التنفيذ الكامل والآمن لـ Interceptor و Authenticator في OkHttp:
```kotlin
// 1. Auth Interceptor: يضيف التوكن الحالي لكل طلب:
class AuthHeaderInterceptor(private val tokenManager: TokenManager) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val token = tokenManager.getAccessToken()
        val request = if (token != null) {
            chain.request().newBuilder()
                .header("Authorization", "Bearer $token")
                .build()
        } else {
            chain.request()
        }
        return chain.proceed(request)
    }
}

// 2. OkHttp Authenticator: يتعامل مع 401 ويعيد المحاولة بالتوكن الجديد:
class TokenAuthenticator(
    private val tokenManager: TokenManager,
    private val authService: RefreshAuthService // يستخدم OkHttpClient مستقل بدون Authenticator!
) : Authenticator {
    override fun authenticate(route: Route?, response: Response): Request? {
        // حماية 1: منع الحلقات اللانهائية لو فشل الطلب أكثر من مرتين:
        if (responseCount(response) >= 2) return null
        
        // حماية 2: التزامن لمنع سباق الطلبات المتزامنة (Mutex / Synchronized):
        synchronized(this) {
            val currentToken = tokenManager.getAccessToken()
            // لو كان هناك طلب سابق قام بالفعل بالتجديد:
            val requestToken = response.request.header("Authorization")?.removePrefix("Bearer ")
            val validToken = if (currentToken != requestToken && currentToken != null) {
                currentToken // استخدام التوكن الجديد فوراً بدون طلب refresh إضافي
            } else {
                // طلب تجديد حقيقي:
                val newTokens = authService.refreshTokenBlocking(tokenManager.getRefreshToken())
                if (newTokens != null) {
                    tokenManager.saveTokens(newTokens.access, newTokens.refresh)
                    newTokens.access
                } else {
                    tokenManager.clearSessionAndForceLogout()
                    return null // إلغاء المحاولة وتسجيل الخروج
                }
            }
            
            // إعادة إرسال الطلب الأصلي بالتوكن المحدث:
            return response.request.newBuilder()
                .header("Authorization", "Bearer $validToken")
                .build()
        }
    }
    
    private fun responseCount(response: Response): Int {
        var result = 1
        var prior = response.priorResponse
        while (prior != null) { result++; prior = prior.priorResponse }
        return result
    }
}
```

## Why it matters and how it works

Authenticate against server authority. Compare the token used in failed request with current token; if another caller already refreshed, retry with current. Otherwise serialize refresh and persist new credentials atomically. Bound follow-up attempts and clear session safely on invalid refresh. Keep credentials out of logs and backups according to threat model.

## Worked example

Conceptual Kotlin coordinator; real OkHttp Authenticator is synchronous, so integration must use a safe blocking boundary/independent refresh client and avoid main-thread work.

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class RefreshCoordinator(private val refresh: suspend () -> Token) {
    private val mutex = Mutex()
    suspend fun newToken(observed: Token, current: suspend () -> Token): Token =
        mutex.withLock {
            val now = current()
            if (now != observed) now else refresh()
        }
}
// refresh() must persist the new token pair before returning; Token, persistence,
// session-generation checks and the OkHttp Authenticator adapter are app-specific.
```

## Trade-offs and decision criteria

Authenticator is a natural 401 challenge point but runs under OkHttp’s synchronous API; avoid blocking the same exhausted dispatcher or recursive client. An application interceptor can attach a snapshot token, but proactive expiry checks still need race handling. Server session invalidation must be authoritative.

## Failure modes

Two concurrent 401s can both rotate refresh tokens, invalidating one another. An infinite 401 retry loops and drains battery. Logging Authorization headers leaks credentials. Calling the refresh endpoint through the same auth path can recurse.

## Production perspective

A banking app has a session repository with atomic token replacement and one refresh coordinator. Logout increments a session generation and cancels old calls; late refresh cannot resurrect a logged-out session. Tests force simultaneous 401s, refresh failure and logout race.

## Interview answer — short

Authentication is implemented by combining an application interceptor that injects access tokens into outgoing requests with an OkHttp Authenticator that intercepts 401 responses to refresh tokens. Loop counters prevent infinite retries, and thread-safe managers serialize refresh calls while broadcasting logout events upon revocation.

## Interview answer — structured

Implementing token authentication and refresh logic safely requires separating token attachment from 401 failure handling.
First, an application-level Interceptor inspects outgoing requests and attaches the active JWT access token in the Authorization header. It bypasses public endpoints that do not require credentials.
Second, token renewal is delegated to OkHttp's Authenticator interface rather than a generic interceptor. The Authenticator triggers only when the server responds with HTTP 401 Unauthorized, automatically executing token renewal and returning a new request to be replayed transparently.
Third, we guard against infinite retry loops by checking response.priorResponse. If a request has already failed authentication twice, or if the refresh token itself has expired, the authenticator returns null to cancel the request, purges local session storage, and dispatches a navigation event to the login screen.

## Interview answer — deep senior

Designing enterprise authentication pipelines requires understanding OkHttp's internal execution architecture and handling edge-case failure modes.
Developers frequently attempt to handle token refresh inside a standard Interceptor.
This is an anti-pattern: interceptors execute for every request and require manual recursive chain calls, complicating error recovery and risking thread starvation.
In contrast, OkHttp's Authenticator interface was specifically engineered for reactive credential challenges.
When a 401 Unauthorized occurs, OkHttp routes execution to Authenticator.authenticate().
Our implementation first checks responseCount(): if prior responses exist and the Authorization header already matches the newly refreshed token, we know the account was revoked or lacked permissions, so we immediately return null to halt the loop.
Under the hood, our TokenManager encapsulates a ReentrantLock to serialize concurrent refresh calls across threads.
When refresh succeeds, we persist the new access and refresh tokens into EncryptedSharedPreferences backed by Android Keystore.
If the auth server rejects the refresh token with a 400 or 401, we treat the session as permanently compromised: we clear local Room user tables, wipe secure storage, and post a SessionExpiredEvent to our UI navigation coordinator to redirect the user to authentication.
Furthermore, we implement an in-flight request buffer to queue concurrent network calls while the refresh transaction executes, preventing duplicate 401 storms and ensuring all paused requests replay seamlessly with the new bearer token.

## How to answer in the interview

- **Why:** Concurrent 401s can rotate credentials more than once.
- **How:** Separate token interceptor from bounded challenge/refresh coordinator.
- **Trade-offs:** A synchronous Authenticator needs a safe independent refresh path.
- **Failure cases:** Recursive refresh loop, deadlock, late token after logout.
- **Production solution:** Single-flight refresh, atomic token pair, generation checks and tests.

## Deep-dive talking points

Trace two 401s, token rotation, logout generation and synchronous Authenticator constraints.

## Follow-up questions

- **Interviewer:** "What happens if `Authenticator.authenticate()` returns `null`?"
  **Answer:** "OkHttp halts retries and returns the original 401 response to the caller, allowing the UI layer to navigate to the login screen."

- **Interviewer:** "Where should tokens be stored securely in Android?"
  **Answer:** "EncryptedSharedPreferences or Proto DataStore with Android Keystore encryption, never in plaintext SharedPreferences."

## Self-check rubric

Can I prevent recursion and duplicate refresh, bound retries and protect logout state?

## References and reviewed-on date

- [OkHttp calls guide](https://lysine.dev/okhttp/features/calls/) — Authenticator follow-up requests.
- [Android security configuration](https://developer.android.com/privacy-and-security/security-config) — transport security.

Technically reviewed against primary documentation on 2026-10-13.
