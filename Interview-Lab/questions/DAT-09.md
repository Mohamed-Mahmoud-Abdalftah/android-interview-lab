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

Use an OkHttp Interceptor to attach access tokens to outgoing requests, and an Authenticator to handle 401 Unauthorized responses by fetching a new token and retrying the request. Protect against infinite retry loops by checking response count, synchronize refreshes to prevent race conditions, and use a dedicated clean OkHttpClient for refresh calls.

## Interview answer — structured

Implementing resilient JWT authentication in OkHttp requires separating proactive header injection from reactive 401 recovery:

1. **Proactive Injection (`Interceptor`)**: An Application Interceptor reads the cached access token from secure storage and injects `Authorization: Bearer <token>` into outgoing requests. Public endpoints (login, register) are excluded.

2. **Reactive 401 Recovery (`Authenticator`)**: When the server returns `401 Unauthorized`, OkHttp triggers `Authenticator.authenticate()`. This method executes a synchronous token refresh, updates persistent storage, and builds a new request with the updated token, which OkHttp automatically retries.

3. **Guardrails against Common Failures**:
   - **Loop Prevention**: Inspect `response.priorResponse` chain. If attempts exceed 2, return `null` to abort and prompt user re-login.
   - **Deadlock Isolation**: The refresh network call must execute on an isolated OkHttp client that has **no Authenticator attached**; using the primary client causes recursive lock deadlocks.
   - **Double-Check Lock**: Check whether another concurrent thread already refreshed the token while this thread was waiting on the lock.

## Interview answer — deep senior

A critical edge case is **Refresh Token Rotation (RTR)**.

Modern OAuth 2.0 backends rotate the refresh token on *every* refresh request (issuing both a new access token and a new single-use refresh token, immediately invalidating the previous refresh token). If client synchronization fails and two concurrent requests make separate refresh calls using the old refresh token, the server detects token reuse, treats it as a security breach, and invalidates all user sessions globally!

To solve this, the refresh operation must be strictly serialized behind a **Single-Flight Lock (or Mutex)** with token double-checking: the thread entering the lock first executes the refresh, while subsequent threads detect that `currentToken != requestToken` and immediately replay with the new token without hitting the refresh API.

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
