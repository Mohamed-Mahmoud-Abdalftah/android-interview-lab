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

Design secure authentication using short-lived access tokens and Keystore-encrypted refresh tokens. Intercept 401 responses via OkHttp's Authenticator, coordinate concurrent refresh requests using a mutex to prevent thundering-herd issues, support refresh token rotation, and clear session state deterministically when refresh fails.

## Interview answer — structured

A production-grade mobile authentication system must handle transient concurrency, key security, and automatic recovery.

First, **Tiered Token Architecture**. Next, with Access Token (Short-lived, ~5-15 min), passed in standard HTTP `Authorization: Bearer` headers. Kept primarily in volatile memory or encrypted DataStore.
Additionally, a Refresh Token (Long-lived, ~14-30 days) is stored encrypted using Android Keystore AES-GCM in private storage. **Transparent Refresh via OkHttp Authenticator**.
Attach an `Authenticator` implementation to the primary `OkHttpClient`. When any endpoint returns `401 Unauthorized`, OkHttp automatically triggers this handler. **Concurrency & Thundering-Herd Synchronization**.
When multiple parallel requests fail simultaneously with 401, they hit `authenticate()` concurrently. A synchronized `Mutex` serializes execution. The first thread completes the refresh; subsequent threads observe that the current token has already updated and immediately replay with the new token without issuing duplicate refresh calls. **Terminal Failure Handling**.
Finally, if the refresh token has expired, been revoked, or fails with 401/403, the authenticator returns `null`, wipes local credentials from Keystore and DataStore, and emits an unauthenticated session event to navigate to Login.


## Interview answer — deep senior

From an enterprise platform design perspective, session management extends beyond simple HTTP headers.

First, with Refresh Token Rotation (RTR) & Compromise Detection, each refresh cycle issues both a new access token and a new refresh token, immediately invalidating the old refresh token on the server. If an attacker intercepts and attempts to use an already-rotated refresh token, the backend detects replay fraud and terminates all sessions across all devices for that user account. Next, with Cryptographic Token Binding (DPoP), in high-security banking architectures, access tokens are cryptographically bound to a device-generated asymmetric EC keypair in Android Keystore. The client signs an HTTP header containing the target URL and a server nonce, ensuring intercepted tokens cannot be replayed from other clients.
Finally, with Multi-Process & Global Session State Broadcast, if an app utilizes multiple processes (e.g. Background sync or media playback services), session invalidation must propagate across IPC boundaries using an encrypted ContentProvider or reactive DataStore flows to prevent orphaned background tasks from flooding servers with stale credentials.


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
