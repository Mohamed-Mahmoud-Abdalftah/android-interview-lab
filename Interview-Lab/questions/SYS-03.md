---
id: "SYS-03"
question: "Design login, session management, and secure token refresh."
topic: "Android System Design & Architecture Decisions"
code: "SYS"
group: "A"
phase: 4
priority: "P1"
order: 332
editorial_status: "reviewed"
---

# SYS-03

## Original interview question

Design login, session management, and secure token refresh.

## What the interviewer evaluates

Design secure login/session lifecycle and race-safe token refresh.

## Concept and technical explanation

Designing enterprise mobile authentication requires defense-in-depth security coupled with race-safe concurrency controls. Access tokens are short-lived JSON Web Tokens (JWTs) stored securely in hardware-backed storage (EncryptedSharedPreferences backed by Android Keystore), while refresh tokens are longer-lived credentials used exclusively to issue new access tokens. The primary architectural challenge is handling concurrent HTTP requests encountering HTTP 401 Unauthorized errors simultaneously. Without synchronization, multiple threads trigger redundant token refresh network calls, which invalidates the refresh token if the backend implements refresh token rotation. The production solution employs an OkHttp Authenticator combined with a coroutine Mutex to serialize refresh requests, updating the shared session state atomically and retrying queued requests seamlessly with the newly issued token.

## Practical walkthrough (English)

Implementing race-safe token refresh with OkHttp Authenticator, Mutex, and Keystore storage:
```kotlin
// 1. Thread-safe Session Manager backed by Android Keystore
class SessionManager @Inject constructor(
    private val encryptedPrefs: SharedPreferences
) {
    private val mutex = Mutex()
    private val _authState = MutableStateFlow<AuthStatus>(AuthStatus.Initial)
    val authState: StateFlow<AuthStatus> = _authState.asStateFlow()

    fun getAccessToken(): String? = encryptedPrefs.getString("KEY_ACCESS_TOKEN", null)
    fun getRefreshToken(): String? = encryptedPrefs.getString("KEY_REFRESH_TOKEN", null)

    suspend fun updateTokens(accessToken: String, refreshToken: String) {
        mutex.withLock {
            encryptedPrefs.edit()
                .putString("KEY_ACCESS_TOKEN", accessToken)
                .putString("KEY_REFRESH_TOKEN", refreshToken)
                .apply()
            _authState.value = AuthStatus.Authenticated(accessToken)
        }
    }

    suspend fun clearSession() {
        mutex.withLock {
            encryptedPrefs.edit().clear().apply()
            _authState.value = AuthStatus.Unauthenticated
        }
    }
}

// 2. OkHttp Authenticator serializing concurrent 401 recovery
class TokenAuthenticator @Inject constructor(
    private val sessionManager: SessionManager,
    private val authApiProvider: Provider<AuthApiService>
) : Authenticator {
    private val refreshMutex = Mutex()

    override fun authenticate(route: Route?, response: Response): Request? {
        val currentToken = sessionManager.getAccessToken() ?: return null
        
        // Fast-path: check if another thread already refreshed the token
        val requestToken = response.request.header("Authorization")?.removePrefix("Bearer ")
        if (requestToken != currentToken) {
            return response.request.newBuilder()
                .header("Authorization", "Bearer $currentToken")
                .build()
        }

        return runBlocking {
            refreshMutex.withLock {
                val latestToken = sessionManager.getAccessToken()
                if (latestToken != currentToken && latestToken != null) {
                    return@withLock response.request.newBuilder()
                        .header("Authorization", "Bearer $latestToken")
                        .build()
                }

                val refreshToken = sessionManager.getRefreshToken() ?: return@withLock null
                val refreshResult = authApiProvider.get().refreshToken(RefreshTokenRequest(refreshToken))

                if (refreshResult.isSuccessful && refreshResult.body() != null) {
                    val tokens = refreshResult.body()!!
                    sessionManager.updateTokens(tokens.accessToken, tokens.refreshToken)
                    response.request.newBuilder()
                        .header("Authorization", "Bearer ${tokens.accessToken}")
                        .build()
                } else {
                    sessionManager.clearSession()
                    null // Abort retries and trigger login navigation
                }
            }
        }
    }
}
```

## Explanation in Arabic

كيف تصمم نظام مصادقة وإدارة جلسات وتجديد آمن للتوكنز (Login, Session Management, and Secure Token Refresh) بمستوى إنتاج ضخم؟

1. دورة حياة الجلسة الآمنة (Session Lifecycle Architecture):
   - **Login**: يرسل المستخدم بيانات الاعتماد (أو عبر OAuth2/OIDC/Biometric) إلى السيرفر المشفر، ويعود الـ Backend بزوج توكنز:
     * **Access Token (قصير العمر - 5 إلى 15 دقيقة)**: يستخدم في ترويسة الطلبات `Authorization: Bearer <token>`.
     * **Refresh Token (طويل العمر - 14 إلى 30 يوماً)**: يستخدم حصرياً لتجديد الـ Access Token.
   - **التخزين**: Access Token يُحفظ في الذاكرة (RAM) لتقليل التعرض، و Refresh Token يُشفر عبر Android Keystore AES-GCM ويُخزن في DataStore.

2. التجديد التلقائي الشفاف (Transparent Token Refresh):
   - يجب ألا يشعر المستخدم بأي انقطاع عند انتهاء صلاحية الـ Access Token.
   - نستخدم `okhttp3.Authenticator` الذي يتم استدعاؤه فقط عند تلقي استجابة `HTTP 401 Unauthorized`.

3. التحديات القاتلة في بيئات الإنتاج وكيفية حلها:
   - **مشكلة الـ Thundering Herd (عشرات الطلبات المتزامنة)**: عندما تنتهي صلاحية التوكن، قد تعود 5 طلبات متزامنة بـ 401 في نفس اللحظة! إذا حاولت كلها تجديد التوكن، ستحدث فوضى ويفشل الـ Refresh Token Rotation. **الحل**: مزامنة التجديد باستخدام Coroutines `Mutex` لضمان تشغيل طلب تجديد واحد فقط، وإعادة استخدام النتيجة لباقي الطلبات.
   - **حلقات الـ 401 اللانهائية (Infinite 401 Loop)**: إذا انتهت صلاحية الـ Refresh Token أيضاً، يجب التوقف فوراً ومسح الجلسة وتوجيه المستخدم لواجهة تسجيل الدخول.

## Practical walkthrough

تنفيذ OkHttp Authenticator احترافي مع Mutex متزامن ومعالجة Race Conditions وإعادة المحاولة:
```kotlin
class ProductionTokenAuthenticator(
    private val sessionRepository: SessionRepository,
    private val authApi: AuthApiService
) : Authenticator {
    private val refreshMutex = Mutex()

    override fun authenticate(route: Route?, response: Response): Request? {
        // 1. منع الحلقات اللانهائية إذا تكرر الفشل أكثر من مرتين:
        if (responseCount(response) >= 2) return null

        val staleToken = response.request.header("Authorization")?.removePrefix("Bearer ")

        return runBlocking {
            refreshMutex.withLock {
                val currentToken = sessionRepository.getAccessToken()
                
                // 2. إذا كان هناك طلب آخر قد جدد التوكن بالفعل أثناء انتظار هذا الطلب في الـ Mutex:
                if (currentToken != null && currentToken != staleToken) {
                    return@withLock response.request.newBuilder()
                        .header("Authorization", "Bearer $currentToken")
                        .build()
                }

                // 3. طلب تجديد التوكن باستخدام الـ Refresh Token المشفر:
                val refreshToken = sessionRepository.getRefreshToken() ?: run {
                    sessionRepository.forceLogout()
                    return@withLock null
                }

                val refreshResponse = authApi.refreshToken(RefreshTokenRequest(refreshToken))
                if (refreshResponse.isSuccessful && refreshResponse.body() != null) {
                    val newSession = refreshResponse.body()!!
                    sessionRepository.saveTokens(newSession.accessToken, newSession.refreshToken)
                    
                    response.request.newBuilder()
                        .header("Authorization", "Bearer ${newSession.accessToken}")
                        .build()
                } else {
                    // فشل الـ Refresh (مثلاً تم إلغاؤه من السيرفر) -> طرد المستخدم فوراً
                    sessionRepository.forceLogout()
                    null
                }
            }
        }
    }

    private fun responseCount(response: Response): Int = generateSequence(response) { it.priorResponse }.count()
}
```

## Why it matters and how it works

Session state is a state machine: signed out, authenticating, active, refreshing, expired. Token refresh is per session and must handle concurrent 401s, network failure, permanent rejection and logout race. UI derives destination from session state. Sensitive endpoints need TLS; do not log credentials.

## Worked example

Conceptual Kotlin state model; real credential storage and backend revocation are product-specific.

```kotlin
sealed interface SessionState {
    data object SignedOut : SessionState
    data class Active(val generation: Long) : SessionState
    data class Refreshing(val generation: Long) : SessionState
    data object Expired : SessionState
}
// A refresh result commits only if generation is still current.
```

## Trade-offs and decision criteria

Bearer tokens simplify API calls but theft gives access until expiry/revocation; short lifetimes increase refresh pressure. A session-scoped coordinator adds complexity but prevents rotation races. Biometric unlock protects local UX but is not backend authentication by itself.

## Failure modes

Two concurrent refreshes can invalidate each other. A late refresh after logout can restore old credentials. Saving refresh token in backup without key policy can leak or become unreadable. An embedded client secret is extractable from APK.

## Production perspective

A finance app uses backend-bound session IDs, TLS, short-lived access token, controlled refresh, generation-aware logout and server revocation. Tests force simultaneous 401s and process restart; telemetry excludes secrets and monitors refresh failures.

## Interview answer — short

We design session management using short-lived access tokens and longer-lived refresh tokens stored in EncryptedSharedPreferences backed by Android Keystore. For race-safe token refresh, we use an OkHttp Authenticator with a Mutex to serialize concurrent 401 responses. Only the first request triggers the refresh API call; queued requests wait for the new access token and retry seamlessly without duplicate authentication calls or user interruption.

## Interview answer — structured

A production-grade mobile authentication system must guarantee cryptographic credential security, seamless user experience, and race-safe token refreshing.
We store sensitive JWT access and refresh tokens in EncryptedSharedPreferences, where encryption keys are managed by the hardware-backed Android Keystore.
Our networking layer utilizes OkHttp interceptors and an Authenticator.
When an API call returns HTTP 401 Unauthorized, OkHttp delegates recovery to the Authenticator.
Because multiple parallel network calls can fail simultaneously, we guard the refresh routine with a coroutine Mutex or synchronized lock.
The first failing request acquires the lock, verifies whether another thread already refreshed the token, and if not, dispatches a refresh request using the refresh token.
Once a new token pair arrives, we persist it atomically and release the lock.
The pending requests resume, updating their Authorization headers with the new token and executing without failure.
If the refresh token itself is expired or revoked, the Authenticator triggers an unauthenticated session event, clearing local credentials and navigating the user securely to the login screen.

## Interview answer — deep senior

Under the hood, token refresh architectures must anticipate refresh token rotation, process termination, and background synchronization failures.
When backends implement refresh token rotation for enhanced security, issuing a refresh request immediately invalidates the previous refresh token.
If two concurrent mobile network requests trigger duplicate refresh calls with the old refresh token, the second call will be rejected by the backend as a replay attack, causing an unintended session termination.
To prevent this, our Authenticator checks if the request's Authorization header already contains an outdated token compared to the current in-memory token.
If another thread already completed a refresh, the Authenticator retries immediately with the existing fresh token without making another network call.
If a refresh is required, the Mutex ensures strictly one in-flight refresh request.
Furthermore, we decouple the authentication state machine into a reactive SessionManager exposing a StateFlow of AuthStatus to the presentation layer.
When a refresh permanently fails with HTTP 400 or 403, SessionManager wipes cached user data from Room and Keystore, cancels in-flight background sync jobs in WorkManager, and emits an unauthenticated state that routes the UI to authentication.
For high-assurance banking features, we wrap the access token decryption inside a BiometricPrompt CryptoObject, ensuring that credentials cannot be retrieved from hardware Keystore without physical fingerprint or facial authorization.
This guarantees total data isolation between user sessions on shared devices.

## How to answer in the interview

- **Why:** token refresh has concurrency and revocation races.
- **How:** model session states, serialize refresh, and compare generation before committing credentials.
- **Trade-off:** persistent sessions add storage and recovery complexity.
- **Failure case:** simultaneous 401s race or a late refresh revives logout.
- **Production solution:** server revocation, one refresh coordinator, and race-focused tests.

## Deep-dive talking points

Trace simultaneous 401s, transient failure, permanent revocation and logout race.

## Follow-up questions

- **Interviewer:** "Why should you use an OkHttp Authenticator instead of an Interceptor for refreshing tokens?"
  **Answer:** "An Interceptor executes on every single request and must inspect response codes manually; an Authenticator is invoked specifically by OkHttp only on 401 responses and natively handles retry loops."

- **Interviewer:** "What happens if runBlocking in Authenticator blocks an IO thread?"
  **Answer:** "It blocks one OkHttp background thread during the refresh; because OkHttp thread pools manage network I/O, the UI remains responsive, provided UI operations never block waiting for network responses synchronously."

## Self-check rubric

Can I protect credentials, define backend authority and test refresh/logout races?

## References and reviewed-on date

- [Android security configuration](https://developer.android.com/privacy-and-security/security-config) — TLS trust.
- [Android architecture guide](https://developer.android.com/topic/architecture) — SSOT/state ownership.

Technically reviewed against primary documentation on 2026-10-13.
