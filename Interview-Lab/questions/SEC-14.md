---
id: "SEC-14"
question: "Where should access and refresh tokens be stored and how are they revoked?"
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "B"
phase: 3
priority: "P1"
order: 311
editorial_status: "reviewed"
---

# SEC-14

## Original interview question

Where should access and refresh tokens be stored and how are they revoked?

## What the interviewer evaluates

- Access/refresh token scope and storage minimization.
- Server revocation, rotation races and logout across process death.

## Concept and technical explanation

Secure token storage and revocation architecture represents the core of identity management in modern mobile applications. Access tokens are short-lived bearer credentials (typically lasting 15 to 60 minutes) used in HTTP Authorization headers. Because of their ephemeral nature, access tokens can reside in volatile in-memory repositories or securely in encrypted storage. Refresh tokens are long-lived, high-privilege credentials whose sole purpose is to exchange for new access tokens; they must be persisted securely on disk using Jetpack DataStore or EncryptedSharedPreferences backed by hardware-rooted Android Keystore master keys. Token revocation operates on two planes: client-side lifecycle and server-side invalidation. A client-side logout must cancel running background network tasks, wipe in-memory token singletons, and purge persisted ciphertext from disk. However, local deletion alone does not invalidate a bearer token across distributed systems. The client must dispatch an explicit logout request to the authorization server's OAuth 2.0 Token Revocation endpoint (RFC 7009), allowing the backend to invalidate the refresh token in Redis and trigger Refresh Token Rotation (RTR).

## Practical walkthrough (English)

Implementing secure token storage and RFC 7009 compliant token revocation:
```kotlin
class AuthenticationRepository(
    private val secureStorage: EncryptedDataStore,
    private val authApi: OAuthService,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    // 1. In-memory volatile access token cache for high-throughput OkHttp interceptors
    @Volatile private var cachedAccessToken: String? = null

    suspend fun getAccessToken(): String? = cachedAccessToken ?: withContext(ioDispatcher) {
        secureStorage.readAccessToken().also { cachedAccessToken = it }
    }

    // 2. Comprehensive Logout: Server-side RFC 7009 revocation + Local purge
    suspend fun executeCompleteLogout(): Result<Unit> = withContext(ioDispatcher) {
        try {
            val currentRefreshToken = secureStorage.readRefreshToken()
            if (!currentRefreshToken.isNullOrBlank()) {
                // Inform backend authorization server to invalidate the token in Redis
                authApi.revokeToken(
                    token = currentRefreshToken,
                    tokenTypeHint = "refresh_token"
                )
            }
        } catch (e: Exception) {
            // Even if network fails, proceed to clean local state
        } finally {
            // Guarantee local credentials are eradicated
            cachedAccessToken = null
            secureStorage.clearAllTokens()
        }
        Result.success(Unit)
    }
}
```

## Explanation in Arabic

أين وكيف يجب تخزين الـ Access Tokens والـ Refresh Tokens، وكيف يتم إلغاؤها (Revocation) من جهة السيرفر والتطبيق؟

1. استراتيجية تخزين الـ Tokens على الهاتف:
   - **Access Token (قصير العمر - Short-Lived: 5 إلى 15 دقيقة)**: يُفضل الاحتفاظ به في **ذاكرة الـ RAM فقط** (داخل Singleton أو Repository في الذاكرة) أثناء تشغيل التطبيق. لا داعي لحفظه على القرص إذا كان قصير العمر، أو يُحفظ مشفراً في Keystore/DataStore إذا أردنا تجنب طلب توكن جديد عند إعادة فتح التطبيق.
   - **Refresh Token (طويل العمر - Long-Lived: أيام أو أسابيع)**: **يُمنع منعاً باتاً تخزينه كنص صريح (Plaintext)**. يجب تخزينه مشفراً باستخدام مفتاح عتادي داخل Android Keystore مدمج مع Jetpack DataStore.

2. آلية الـ Token Rotation والـ Revocation في السيرفر:
   - **Refresh Token Rotation (RTR)**: في كل مرة يستخدم فيها العميل الـ Refresh Token للحصول على Access Token جديد، يقوم السيرفر بإنشاء Refresh Token جديد وإلغاء القديم فوراً.
   - **كشف سرقة التوكن (Token Theft Detection)**: إذا حاول مهاجم استخدام Refresh Token قديم تم تدويره مسبقاً، يدرك السيرفر فوراً أن هناك سرقة حدثت، فيقوم بإلغاء عائلة التوكنز بالكامل (Family Revocation) وقطع جميع الجلسات فوراً.

3. آلية التجديد التلقائي عبر OkHttp Authenticator:
   - لا يتم فحص صلاحية التوكن يدوياً في كل Request. بل نعتمد على `okhttp3.Authenticator` الذي يتم استدعاؤه تلقائياً فقط عند رجوع استجابة `HTTP 401 Unauthorized` من السيرفر، ليقوم بتجميد الطلبات وتجديد التوكن وإعادة المحاولة بسلاسة.

## Practical walkthrough

تنفيذ تجديد التوكن بسلاسة وأمان باستخدام OkHttp Authenticator و Mutex لمنع Race Conditions:
```kotlin
class TokenAuthenticator(
    private val tokenStorage: SecureTokenStorage,
    private val authService: AuthService
) : Authenticator {
    private val refreshMutex = Mutex()

    override fun authenticate(route: Route?, response: Response): Request? {
        // 1. منع المحاولات المتكررة اللانهائية إذا فشل الـ Refresh أصلاً:
        if (responseCount(response) >= 3) return null

        val currentAccessToken = runBlocking { tokenStorage.getAccessToken() }
        
        // 2. فحص ما إذا كان طلب آخر قد قام بتجديد التوكن بالفعل أثناء انتظار هذا الطلب:
        val requestToken = response.request.header("Authorization")?.removePrefix("Bearer ")
        if (requestToken != currentAccessToken && currentAccessToken != null) {
            // تم تجديد التوكن بالفعل؛ إعادة إرسال الطلب بالتوكن الجديد فوراً:
            return response.request.newBuilder()
                .header("Authorization", "Bearer $currentAccessToken")
                .build()
        }

        // 3. تجديد التوكن بشكل متزامن وحصري عبر Mutex:
        return runBlocking {
            refreshMutex.withLock {
                val latestToken = tokenStorage.getAccessToken()
                if (latestToken != requestToken && latestToken != null) {
                    return@withLock response.request.newBuilder()
                        .header("Authorization", "Bearer $latestToken")
                        .build()
                }

                val refreshToken = tokenStorage.getRefreshToken() ?: return@withLock null
                val newTokensResult = authService.refreshTokens(refreshToken)
                
                if (newTokensResult.isSuccessful) {
                    val newTokens = newTokensResult.body()!!
                    tokenStorage.saveTokens(newTokens.accessToken, newTokens.refreshToken)
                    response.request.newBuilder()
                        .header("Authorization", "Bearer ${newTokens.accessToken}")
                        .build()
                } else {
                    // تم رفض الـ Refresh Token على السيرفر؛ إبطال الجلسة وتوجيه المستخدم لتسجيل الدخول
                    tokenStorage.clearTokens()
                    null
                }
            }
        }
    }
    private fun responseCount(response: Response): Int = generateSequence(response) { it.priorResponse }.count()
}
```

## Why it matters and how it works

Token validity is determined by the issuer, not by local encryption. A refresh endpoint should enforce rotation/reuse detection according to the server design. Concurrent 401 responses can race to refresh and invalidate one another; serialize refresh for one session and recheck the latest token before making a new request.

## Worked example

In an account app, an OkHttp authenticator delegates refresh to one session repository. That repository uses a mutex around the refresh state, persists a rotated refresh token before releasing waiting calls, and clears state after an authoritative invalid-grant response. The mutex is only process-local; server policy handles multi-device races.

## Trade-offs and decision criteria

In-memory access tokens reduce persistence exposure but require refresh after process death. Keystore-backed local storage raises extraction cost but adds key-loss behavior. Long-lived sessions improve convenience while increasing abuse window; use server revocation and device/session visibility.

## Failure modes

If logout only removes a DataStore value, a copied refresh token may still work. If `CancellationException` is swallowed in refresh logic, canceled requests may continue unexpectedly. Handle 401 storms, revoked grants and lost rotation responses without retry loops.

## Production perspective

Production logout coordinates local clearing, cancellation of pending authenticated work, backend revocation and redacted audit events. On offline logout, locally block further use and queue/retry revocation under an explicit server policy; do not claim remote revocation already succeeded.

## Interview answer — short

We store short-lived access tokens in volatile memory or encrypted storage, while long-lived refresh tokens are securely encrypted on disk using Keystore-backed DataStore. Revocation requires a dual approach: wiping in-memory singletons and encrypted disk storage on the client, and calling the server's OAuth revocation endpoint so the refresh token is immediately blacklisted in backend caches.

## Interview answer — structured

Effective mobile token management separates storage requirements by token lifetime while enforcing robust revocation protocols.
Access tokens are short-lived bearer credentials that expire in minutes, which we maintain in volatile memory or encrypted local storage to satisfy frequent network calls with low latency.
Refresh tokens represent permanent account access; they must be encrypted on disk using Jetpack DataStore or EncryptedSharedPreferences anchored to an Android Keystore master key.
Revocation requires a coordinated effort between client state and backend infrastructure.
Simply clearing local app storage upon logout is insufficient because an exfiltrated refresh token remains valid on the authorization server until its natural expiration.
A production logout workflow first sends an authenticated request to the server's OAuth 2.0 revocation endpoint, instructing the backend to blacklist the token family in its Redis cache.
The client then cancels all running coroutines, clears in-memory token singletons, and purges the encrypted disk storage.
Additionally, the backend enforces Refresh Token Rotation, issuing a new refresh token on every exchange and invalidating the entire family if an already-consumed token is replayed.

## Interview answer — deep senior

From an adversarial perspective, the security of an OAuth 2.0 mobile client rests entirely on the protection of its refresh token and the resilience of its revocation pathways.
If an attacker intercepts an access token, the exposure window is strictly bounded by its brief time-to-live.
However, a compromised refresh token allows persistent access to account resources.
Therefore, storing refresh tokens in plain SharedPreferences or unencrypted Room tables is a catastrophic vulnerability.
We persist refresh tokens exclusively in storage encrypted via AES-256-GCM using hardware-backed Keystore keys, while caching the access token in volatile memory to prevent repeated disk decryption overhead on every API call.
For revocation, we must design for both user-initiated logouts and automated threat mitigation.
In a user logout, deleting local records while offline is a dangerous half-measure; if the network is available, the client must notify the server's RFC 7009 revocation endpoint so distributed API gateways reject subsequent requests using that token.
More importantly, modern systems implement Refresh Token Rotation with Automatic Reuse Detection.
Every time the mobile app requests a new access token, the authorization server invalidates the current refresh token and issues a replacement pair.
If an attacker attempts to use a previously consumed refresh token, the server detects the token replay attack, recognizes that a breach has occurred, and immediately revokes all active tokens associated with that user session, neutralizing the threat automatically.

## How to answer in the interview

- **Why:** bearer tokens grant access wherever presented.
- **How:** minimize access-token life, protect refresh persistence, and rotate/revoke server-side.
- **Trade-off:** stronger session controls increase reauthentication and refresh traffic.
- **Failure case:** local deletion without server revocation leaves stolen credentials live.
- **Production solution:** session IDs, revocation policy, and replay monitoring.

## Deep-dive talking points

Trace login, refresh rotation, concurrent 401 handling, logout and server-side revocation; describe how a leaked refresh token is invalidated.

## Follow-up questions

- **Interviewer:** "What is the difference between an OkHttp Interceptor and an Authenticator for auth tokens?"
  **Answer:** "An Interceptor attaches the current token to outgoing requests; an Authenticator is triggered only when the server returns 401 Unauthorized, specifically designed for token refresh."

- **Interviewer:** "Why should JWTs not store sensitive PII in their payload?"
  **Answer:** "JWT payloads are Base64Url-encoded, not encrypted; anyone intercepting or inspecting the token in memory can decode and read the claims instantly."

## Self-check rubric

Can I explain token lifetime, storage, single-flight refresh, offline logout and authoritative server revocation?

## References and reviewed-on date

- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — local key protection.
- [OWASP MASVS authentication](https://mas.owasp.org/MASVS/controls/MASVS-AUTH-1/) — authentication and session controls.

Technically reviewed against primary documentation on 2026-10-13.
