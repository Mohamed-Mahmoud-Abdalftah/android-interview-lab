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

Store short-lived access tokens in memory or encrypted storage, and long-lived refresh tokens strictly in Keystore-backed encrypted DataStore. Revocation must occur server-side by blacklisting session IDs in Redis. Use OkHttp's Authenticator with a Mutex to seamlessly refresh tokens upon 401 responses and handle token rotation.

## Interview answer — structured

Token architecture follows a tiered security approach balancing user experience against attack windows.

First, **Storage Topology**. Next, with Access Token, short validity (5–15 minutes). Can reside in an in-memory repository during active process lifecycle, supplemented with Keystore-backed encrypted persistence to survive process death without forced re-logins.
Additionally, with Refresh Token, longer validity (7–30 days). Must never be stored in plain SharedPreferences. It must be encrypted using Android Keystore AES-GCM and stored in Jetpack DataStore. **Server-Side Revocation**.
Mobile logout must invoke a backend `/logout` or `/revoke` endpoint. The server marks the session/refresh token family revoked in a distributed cache (e.g. Redis). Client-side token deletion alone is insufficient because a compromised token remains valid on the server until expiry.
**Refresh Token Rotation (RTR)**. Finally, every refresh request invalidates the previous refresh token and issues a new pair. If an invalidated refresh token is ever reused, the server detects token compromise and immediately revokes all tokens issued to that user session.


## Interview answer — deep senior

In high-traffic distributed mobile apps, token refreshing introduces significant concurrency and failure handling challenges.

First, with Handling Thundering Herds on 401, when multiple parallel API calls fail simultaneously with `401 Unauthorized`, an uncoordinated authenticator triggers parallel refresh calls. The first call succeeds and rotates the refresh token; the subsequent calls submit an already-invalidated refresh token, causing the backend to falsely assume token theft and revoke the session! We prevent this by serializing refresh execution using a Coroutines `Mutex` inside `okhttp3.Authenticator`. Next, with Re-entrant 401 Loop Protection, `Authenticator.authenticate()` must track `response.priorResponse` count. If the refresh request itself fails or if three consecutive retries return 401, return `null` to terminate the loop, wipe stored tokens, and dispatch an unauthenticated session event to navigate to the Login screen.
Finally, with Token Binding & Attestation, in high-assurance fintech apps, refresh tokens are cryptographically bound to a client-generated Keystore EC keypair (DPoP - Demonstrating Proof-of-Possession). Even if an attacker intercepts the refresh token via TLS proxy, they cannot replay it without signing the request using the device's non-exportable private key.


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
