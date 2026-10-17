---
id: "SEC-03"
question: "Compare cryptographic keys, access tokens, refresh tokens, API keys, and passwords."
topic: "Android Security, Crypto & Fintech Threat Modeling"
code: "SEC"
group: "A"
phase: 3
priority: "P1"
order: 300
editorial_status: "reviewed"
---

# SEC-03

## Original interview question

Compare cryptographic keys, access tokens, refresh tokens, API keys, and passwords.

## What the interviewer evaluates

- Purpose, lifetime, exposure and rotation of five credential types.
- Why a bearer token is not a cryptographic key and an APK API key is not a secret.

## Concept and technical explanation

Secure Android application architecture requires categorizing sensitive data into distinct credential classes, each with unique lifetimes, cryptographic properties, exposure risks, and storage requirements. Cryptographic keys (such as AES symmetric keys or ECDSA asymmetric key pairs) provide mathematical confidentiality and digital signatures; they must reside inside the hardware-backed Android Keystore. Access tokens are short-lived bearer credentials (typically OAuth 2.0 JWTs valid for 15 to 60 minutes) used in HTTP headers to authorize client API requests; they are kept in secure volatile memory or encrypted storage and rotated frequently. Refresh tokens are high-value, long-lived credentials (valid for weeks or months) whose sole purpose is to authenticate with the identity provider to obtain new access tokens; they require maximum protection in EncryptedSharedPreferences backed by Keystore master keys, combined with refresh token rotation (RTR). API keys are public client identifiers used by platforms like Google Maps to track usage and quota; they are not secrets and must be restricted by package name and SHA-1 signing certificates in cloud consoles. Passwords are user-held master authentication secrets that should never be permanently persisted on mobile devices, manipulated only as ephemeral char arrays to avoid immutable JVM heap String intern pooling.

## Practical walkthrough (English)

Production token storage and secure password memory handling in Android:
```kotlin
// 1. Secure token storage using Jetpack Security EncryptedSharedPreferences
class SecureSessionManager(context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val encryptedPrefs = EncryptedSharedPreferences.create(
        context,
        "secure_session_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun saveTokens(accessToken: String, refreshToken: String) {
        encryptedPrefs.edit()
            .putString("access_token", accessToken)
            .putString("refresh_token", refreshToken)
            .apply()
    }
}

// 2. Safe user password handling: zeroing out character arrays immediately
fun authenticateWithZeroablePassword(passwordChars: CharArray, onComplete: () -> Unit) {
    try {
        // Send password over TLS to exchange for OAuth token pair
        transmitCredentialsOverTls(passwordChars)
    } finally {
        // Overwrite memory buffer immediately to prevent heap dump exposure
        passwordChars.fill('0')
    }
    onComplete()
}
```

## Explanation in Arabic

مقارنة شاملة بين 5 أنواع من بيانات الاعتماد الحساسة في Android:
المفاتيح التشفيرية، و Access Tokens، و Refresh Tokens، و API Keys، وكلمات المرور:

1. Cryptographic Keys (المفاتيح التشفيرية - مثل AES / RSA / ECC):
   - **طبيعتها**: أرقام باينري عشوائية تُستخدم للعمليات الرياضية (تشفير، فك تشفير، توقيع رقمي HMAC أو RSA).
   - **مكان حفظها**: حصرياً داخل `AndroidKeyStore` المدعوم عتادياً.
   - **فترة البقاء**: طويلة جداً (أشهر أو سنوات) حتى إعادة تثبيت التطبيق أو إبطالها.

2. Access Tokens (توكنز الوصول المؤقتة - مثل JWT Bearer Tokens):
   - **طبيعتها**: تصريح دخول قصير المدى يحمله العميل في كل طلب شبكة (`Authorization: Bearer <token>`).
   - **مكان حفظها**: في الذاكرة (RAM) أو في تخزين مشفر بمفتاح Keystore (Encrypted DataStore).
   - **فترة البقاء**: قصيرة جداً (15 دقيقة إلى ساعة واحدة) لتقليل ضرر التسريب.

3. Refresh Tokens (توكنز التجديد طويلة المدى):
   - **طبيعتها**: بيانات اعتماد سرية تُستخدم فقط لاستدعاء سيرفر المصادقة لإصدار Access Token جديد.
   - **مكان حفظها**: مخزن مشفر عالي الحماية (Android Keystore + Encrypted Storage).
   - **فترة البقاء**: طويلة (أيام أو أسابيع)، ويتم تجديدها مع كل استخدام (Refresh Token Rotation).

4. API Keys (مفاتيح واجهات الطرف الثالث - مثل Google Maps API Key):
   - **طبيعتها**: معرفات عامة للمشروع (Public Identifiers) لتتبع الاستهلاك وإصدار الفواتير لدى Google أو Firebase.
   - **تحذير خطير**: **ليست أسراراً (Not Secrets)**! أي مفتاح مدمج في ملف الـ APK يمكن استخراجه في 3 ثوانٍ بواسطة `apktool`! يجب تقييدها عبر لوحة تحكم Google Cloud بقيود الحزمة وبصمة التوقيع (Package Name + SHA-1 Restriction).

5. Passwords / PINs (كلمات المرور والرموز السرية للمستخدم):
   - **طبيعتها**: بيانات اعتماد يدخلها المستخدم لإثبات هويته.
   - **قاعدة ذهبية**: لا تحفظ كلمات المرور كـ Plaintext في التخزين المحلي أبداً! استبدلها بـ Session Tokens فور تسجيل الدخول، ومسح الـ CharArray من الذاكرة فوراً.

## Practical walkthrough

جدول المقارنة المعمارية بين أنواع بيانات الاعتماد الخمسة في Android:
```text
┌────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬─────────────────────────┐
│ نوع الاعتماد       │ الغرض المعماري       │ فترة الحياة (TTL)    │ مكان التخزين الآمن   │ الإجراء عند التسريب     │
├────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤
│ Cryptographic Key  │ تشفير وتوقيع رقمي    │ دائمة (حتى الإلغاء)  │ Android Keystore (HW)│ إبطال وإعادة توليد محلي │
│ Access Token       │ مصادقة طلبات الشبكة  │ قصيرة (15-60 دقيقة)  │ Encrypted DataStore  │ انتهاء الصلاحية التلقائي│
│ Refresh Token      │ تجديد Access Token   │ متوسطة (14-30 يوماً) │ Encrypted DataStore  │ إبطال الجلسة في السيرفر │
│ API Key (APK)      │ تتبع الاستهلاك والفوترة│ دائمة                │ BuildConfig/Manifest │ قيود SHA-1 + PackageName│
│ Password / PIN     │ إثبات هوية المستخدم  │ عابرة في الذاكرة     │ لا تُخزن أبداً محلياً│ تغيير كلمة المرور فوراً │
└────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴─────────────────────────┘
```

## Why it matters and how it works

Each credential has a distinct issuer, verifier, scope and revocation path. Passwords are verified server-side with an appropriate salted password-hashing scheme. Access/refresh tokens are issued and checked by the identity backend. Cryptographic keys may be generated in Android Keystore. A public mobile API key can identify a project but needs server restrictions and quotas.

## Worked example

In a checkout app, the backend authenticates the user and issues scoped access/refresh credentials. The app stores only what it needs; the refresh token is replaceable through sign-in and never enters logs. The payment-provider private key remains on the server. A bundled map-service identifier is restricted by provider controls, not treated as confidential.

## Trade-offs and decision criteria

Short access-token lifetimes limit exposure but increase refresh traffic. Refresh-token rotation improves revocation visibility but requires race handling. Keystore protects a local encryption key; it does not turn a bearer token into proof of device integrity.

## Failure modes

Putting a provider secret in BuildConfig ships it in the APK. Recording Authorization headers leaks bearer tokens. Reusing one symmetric key for unrelated purposes complicates rotation. Keep private provider operations behind a backend and use per-credential lifecycle rules.

## Production perspective

Document a credential inventory: owner, storage location, scope, lifetime, rotation, incident response. Build a redaction policy and server revocation endpoint. Test expired tokens, refresh races and logout across devices.

## Interview answer — short

We categorize mobile credentials into five distinct security classes: cryptographic keys stored in Keystore for mathematical operations, short-lived access tokens for daily API calls, long-lived refresh tokens securely persisted to rotate access tokens, public API keys restricted in cloud consoles for service quotas, and raw user passwords that are never persisted and zeroed from memory immediately after exchange.

## Interview answer — structured

A resilient mobile security posture treats credentials differently according to their specific blast radius, lifetime, and storage requirements.
Cryptographic keys are mathematical instruments used for encryption and digital signing, requiring non-exportable hardware protection inside Android Keystore.
Access tokens are ephemeral bearer credentials with short lifespans between fifteen and sixty minutes, used in HTTP Authorization headers to authenticate API calls without requiring persistent storage.
Refresh tokens are high-privilege credentials used exclusively with authorization servers to fetch fresh access tokens; they must be encrypted on disk using EncryptedSharedPreferences and rotated on every exchange.
API keys identify the client application for third-party platforms like Google Maps or Firebase; because they are packaged inside the APK, they are public identifiers rather than secrets and must be restricted in developer consoles using application package names and SHA-1 signing fingerprints.
User passwords represent user identity secrets that should never be written to local storage, handled in memory exclusively as ephemeral char arrays that are wiped with zeroes immediately after exchanging them over TLS for authentication tokens.

## Interview answer — deep senior

When evaluating credential management at a staff level, the most common architectural failure is conflating client identification with client authorization.
Developers frequently embed third-party API keys in BuildConfig and treat them as secrets.
In reality, any string bundled into an APK is a public identifier easily extracted with static analysis tools.
For vendor API keys, security relies entirely on platform-level restrictions such as pinning the key to the release SHA-256 signing fingerprint and package name, combined with API quotas.
For user session management, OAuth 2.0 with Proof Key for Code Exchange (PKCE) is the industry standard.
Access tokens must have strict, short time-to-live envelopes to minimize exposure if intercepted over compromised networks.
Conversely, refresh tokens represent the real crown jewels of client authentication.
If a refresh token leaks, an attacker maintains persistent access to the user account.
Therefore, we persist refresh tokens in EncryptedSharedPreferences backed by hardware-rooted Keystore master keys, while enforcing Refresh Token Rotation on the backend.
Under this rotation pattern, using a refresh token invalidates it and issues a replacement; if an authorization server observes an already-consumed refresh token, it assumes token theft and immediately terminates the entire user session.
Finally, raw passwords must never touch disk persistence or SQLite databases.
In memory, we avoid Java Strings because they are immutable and cached in the internal string pool where garbage collection cannot guarantee timely erasure; instead, we handle passwords as mutable CharArrays and explicitly overwrite them with zeroes immediately following network transmission.

## How to answer in the interview

- **Why:** calling everything a secret hides its authority.
- **How:** classify each by issuer, storage, scope, expiry, rotation, and revocation.
- **Trade-off:** shorter sessions improve exposure limits but add refresh traffic.
- **Failure case:** shipping a privileged provider key in an APK.
- **Production solution:** server-own private keys and rotate/revoke sessions explicitly.

## Deep-dive talking points

Classify each credential by issuer, holder, scope, revocation and lifetime; explain why an APK API key is not equivalent to a backend private key.

## Follow-up questions

- **Interviewer:** "Why is an APK API key like Google Maps safe to ship in an APK?"
  **Answer:** "Because Google Maps verifies requests by checking the client's HTTP Referer or Android Package Name and SHA-1 certificate fingerprint against the Google Cloud Console allowlist."

- **Interviewer:** "What is the difference between an Access Token and an API Key?"
  **Answer:** "An API key identifies the client application or project; an Access token identifies a specific authenticated user session with specific scopes."

## Self-check rubric

Can I name issuer, verifier, lifetime, storage, and revocation for each of the five credential types?

## References and reviewed-on date

- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore) — key operations.
- [OWASP MASVS authentication](https://mas.owasp.org/MASVS/controls/MASVS-AUTH-1/) — authentication controls.

Technically reviewed against primary documentation on 2026-10-13.
